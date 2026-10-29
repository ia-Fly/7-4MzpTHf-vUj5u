"""Format « FUSION » (international, sans paroles) : des objets tombent dans un cercle ; deux identiques fusionnent
en l'objet suivant ; le dernier niveau reste caché « ? » jusqu'au final. Inspiré du principe des simulations de fusion
(type @cool_games_heel), avec des objets 100 % dessinés maison.

Le metteur en scène règle le débit de chute pour que le dernier niveau apparaisse vers 88 % de la vidéo,
et la recherche de graine garde la partie la plus tendue (cercle presque plein, mais pas de débordement).

usage :
  python3 fusion.py --theme planets --dur 48 --search 24 --out OUTDIR      # cherche la meilleure graine puis rend tout
  python3 fusion.py --theme fruits --seed 5 --out OUTDIR --preview 2,20,44  # quelques images seulement
Sorties dans OUTDIR : video.mp4 (avec son), cover.jpg, meta.json (+ preview_*.png en mode aperçu)."""
import argparse, json, math, os, random, subprocess, sys, time
from multiprocessing import Pool
import numpy as np, pymunk, skia, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from themes import THEMES, radii, sprite, C, P, radial, TF

W, H, FPS = 1080, 1920, 30
CX, CY, R = 540, 1010, 420          # le cercle
GAP = 162                            # largeur de la goulotte (> diamètre du plus gros objet lâché + parois)
SUB = 4                              # sous-pas physiques par image
PRE = 4.0                            # secondes simulées avant la première image (le cercle est déjà animé à 0 s)
TARGET = 0.88                        # moment visé pour le dernier niveau (fraction de la vidéo)
SPAWN_DT = 0.15                      # intervalle visé entre deux chutes (petit = plus d'objets, plus de fusions)
TH = math.asin((GAP / 2) / R)
TOP_IN = CY - R                      # haut intérieur du cercle


# =============================================================== PHYSIQUE
class Obj:
    __slots__ = ('id', 'tier', 'body', 'shape', 'born', 'r', 'merging', 'above', 'kind')


def simulate(theme, seed, dur, record=False):
    N = len(THEMES[theme]['tiers']); RS = radii(N); rng = random.Random(seed)
    sp = pymunk.Space(); sp.gravity = (0, 1600); sp.iterations = 30; sp.damping = 0.75
    a0, a1 = -math.pi / 2 + TH, 3 * math.pi / 2 - TH; nseg = 180
    pt = lambda a: (CX + R * math.cos(a), CY + R * math.sin(a))
    for i in range(nseg):
        s = pymunk.Segment(sp.static_body, pt(a0 + (a1 - a0) * i / nseg), pt(a0 + (a1 - a0) * (i + 1) / nseg), 7)
        s.elasticity, s.friction = 0.1, 0.6; sp.add(s)
    yjoin = CY - R * math.cos(TH); ytop = TOP_IN - 230
    for x in (CX - GAP / 2, CX + GAP / 2):
        s = pymunk.Segment(sp.static_body, (x, ytop), (x, yjoin), 6); s.elasticity, s.friction = 0.1, 0.3; sp.add(s)

    objs, pending, ev = {}, [], {'merge': [], 'spawn': [], 'record': []}
    nid = [0]
    def add(tier, pos, vel, t, kind):
        r = RS[tier]; m = (r / 24) ** 2; b = pymunk.Body(m, pymunk.moment_for_circle(m, 0, r))
        b.position, b.velocity = pos, vel
        sh = pymunk.Circle(b, r * (0.7 if kind == 'merge' else 1.0)); sh.elasticity, sh.friction = 0.12, 0.5
        sh.collision_type = tier + 1; sp.add(b, sh)
        o = Obj(); o.id, o.tier, o.body, o.shape, o.born, o.r, o.merging, o.above, o.kind = nid[0], tier, b, sh, t, r, False, 0.0, kind
        sh.obj = o; objs[o.id] = o; nid[0] += 1; return o
    def remove(o):
        sp.remove(o.body, o.shape); objs.pop(o.id, None)
    def begin(arb, space, data):
        a, b = arb.shapes; oa, ob = getattr(a, 'obj', None), getattr(b, 'obj', None)
        if oa and ob and not oa.merging and not ob.merging and oa.tier == ob.tier and oa.tier < N - 1:
            oa.merging = ob.merging = True; pending.append((oa, ob))
    for k in range(N - 1): sp.on_collision(k + 1, k + 1, begin=begin)

    dt = 1 / (FPS * SUB); total = int(round((PRE + dur) * FPS)) * SUB
    t_goal = PRE + TARGET * dur; U_goal = 2 ** (N - 1)
    next_spawn, score, best, final_t, over_t, danger_max = 0.0, 0, 0, None, None, 0.0
    frames = []
    kmax = min(4, N - 5)
    WTS = [6, 5, 4, 3, 2]
    AVG = [sum(WTS[i] * 2 ** i for i in range(k + 1)) / sum(WTS[:k + 1]) for k in range(kmax + 1)]
    for step in range(total):
        t = step * dt
        # ---- metteur en scène : débit et taille des chutes
        if t >= next_spawn:
            U = sum(2 ** o.tier for o in objs.values() if o.tier < N - 1)
            free = all((o.body.position - (CX, TOP_IN - 150)).length > o.r + RS[kmax] + 4 for o in objs.values())
            if not free: next_spawn = t + 0.08
            else:
                if final_t is None:
                    # débit nécessaire (unités/s) pour réunir assez de matière avant le moment visé
                    r_req = max(0.0, U_goal * 1.3 - U) / max(0.8, t_goal - t)
                    u_want = r_req * SPAWN_DT
                    hi = next((k for k in range(kmax + 1) if AVG[k] >= u_want), kmax)
                    interval = max(0.085, min(0.6, AVG[hi] / max(r_req, 1e-3)))
                else:
                    interval, hi = 0.42, 2
                counts = [0] * (kmax + 1)
                for o in objs.values():
                    if o.tier <= kmax: counts[o.tier] += 1
                odd = [k for k in range(hi + 1) if counts[k] % 2 == 1]
                if odd and rng.random() < 0.6: tier = odd[0]
                else: tier = rng.choices(range(hi + 1), weights=WTS[:hi + 1])[0]
                add(tier, (CX + rng.uniform(-14, 14), TOP_IN - 150), (rng.uniform(-40, 40), 420), t, 'spawn')
                if t >= PRE: ev['spawn'].append((round(t - PRE, 4), tier))
                next_spawn = t + interval * rng.uniform(0.85, 1.15)
        # ---- aimant léger entre objets identiques (les fusions s'enchaînent)
        if step % 2 == 0:
            groups = {}
            for o in objs.values():
                if o.tier < N - 1 and not o.merging: groups.setdefault(o.tier, []).append(o)
            for k, g in groups.items():
                if len(g) < 2: continue
                pos = np.array([[o.body.position.x, o.body.position.y] for o in g]); d = pos[:, None, :] - pos[None, :, :]
                dist = np.sqrt((d ** 2).sum(-1)) + 1e-6; np.fill_diagonal(dist, 1e9); j = dist.argmin(1)
                lim = 2 * RS[k] * 3.2 if k < 4 else 1e9
                acc = (700 + 150 * k) * dt * 2
                for i, o in enumerate(g):
                    if dist[i, j[i]] < lim:
                        u = -d[i, j[i]] / dist[i, j[i]]; o.body.velocity += (u[0] * acc, u[1] * acc)
        sp.step(dt)
        # ---- fusions
        for oa, ob in pending:
            if oa.id not in objs or ob.id not in objs: continue
            ma, mb = oa.body.mass, ob.body.mass
            pos = (oa.body.position * ma + ob.body.position * mb) / (ma + mb); vel = (oa.body.velocity + ob.body.velocity) * 0.5
            tier = oa.tier + 1; remove(oa); remove(ob)
            add(tier, pos, (vel.x, vel.y - 140), t, 'merge'); score += 10 * 2 ** tier
            if t >= PRE: ev['merge'].append((round(t - PRE, 4), tier, round(pos.x, 1), round(pos.y, 1)))
            if tier > best:
                best = tier
                if t >= PRE: ev['record'].append((round(t - PRE, 4), tier))
            if tier == N - 1 and final_t is None: final_t = t
        pending.clear()
        # ---- croissance des nouveaux objets, vitesses plafonnées, débordement
        mtop = 1e9
        for o in objs.values():
            age = t - o.born
            if o.kind == 'merge' and age < 0.16: o.shape.unsafe_set_radius(o.r * (0.7 + 0.3 * age / 0.16))
            elif o.kind == 'merge' and o.shape.radius != o.r: o.shape.unsafe_set_radius(o.r)
            v = o.body.velocity
            if v.length > 2200: o.body.velocity = v * (2200 / v.length)
            if age > 1.2 and o.body.velocity.length < 260:
                topy = o.body.position.y - o.r; mtop = min(mtop, topy)
                if topy < TOP_IN - 6: o.above += dt
                else: o.above = 0.0
                if o.above > 1.3 and over_t is None: over_t = t
        danger = max(0.0, min(1.0, ((TOP_IN + 190) - mtop) / 190)) if mtop < 1e9 else 0.0
        if final_t is None: danger_max = max(danger_max, danger)
        if not record and (over_t is not None or (final_t is not None and t > final_t + 0.5)): break
        if record and step % SUB == SUB - 1 and t >= PRE - 1e-9:
            frames.append(dict(o=[(o.id, o.tier, round(o.body.position.x, 2), round(o.body.position.y, 2),
                                   round(math.degrees(o.body.angle), 2), round(t - o.born, 3), o.kind) for o in objs.values()],
                               score=score, best=best, danger=round(danger, 3)))
    fv = None if final_t is None else round(final_t - PRE, 3); ov = None if over_t is None else round(over_t - PRE, 3)
    ok = fv is not None and (ov is None or ov > fv + 0.5) and (TARGET - 0.05) * dur <= fv <= (TARGET + 0.04) * dur
    quality = (-abs(fv / dur - TARGET) * 4 + min(danger_max, 0.92)) if ok else -9
    return dict(seed=seed, final=fv, overflow=ov, danger_max=round(danger_max, 3), ok=ok, quality=round(quality, 4),
                score=score, merges=len(ev['merge']), frames=frames, ev=ev, N=N)


def _search_one(args):
    theme, seed, dur = args; r = simulate(theme, seed, dur, record=False); r.pop('frames'); r.pop('ev'); return r


# =============================================================== IMAGE
def font(name, size): return skia.Font(TF[name], size)


def text_c(cv, s, x, y, f, paint, shadow=True, spacing=0):
    w = f.measureText(s) + spacing * max(0, len(s) - 1)
    if spacing:
        xx = x - w / 2
        for ch in s:
            if shadow: cv.drawString(ch, xx + 4, y + 6, f, P(C('#000000', 150)))
            cv.drawString(ch, xx, y, f, paint); xx += f.measureText(ch) + spacing
        return w
    if shadow:
        cv.drawString(s, x - w / 2 + 4, y + 6, f, P(C('#000000', 150)))
    cv.drawString(s, x - w / 2, y, f, paint); return w


def spring(x):
    return 0 if x <= 0 else 1 if x >= 1 else 1 - math.exp(-6 * x) * math.cos(10 * x)


class Renderer:
    def __init__(self, theme, sim, dur):
        self.th = THEMES[theme]; self.theme = theme; self.sim = sim; self.dur = dur; self.N = sim['N']; self.RS = radii(self.N)
        self.spr = [sprite(theme, i, self.RS[i]) for i in range(self.N)]
        self.icon = [sprite(theme, i, 25) for i in range(self.N)]
        self.final = sim['final']; self.merges = sim['ev']['merge']; self.records = sim['ev']['record']
        self.final_xy = next(((x, y) for (tm, tier, x, y) in self.merges if tier == self.N - 1), (CX, CY))
        self.samp = skia.SamplingOptions(skia.FilterMode.kLinear)
        self.bg = self.make_bg()
        self.rng = random.Random(3)

    def make_bg(self):
        s = skia.Surface(W, H); cv = s.getCanvas(); top, bot = self.th['bg']
        cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C(top), C(bot)])))
        if self.th.get('stars'):
            r = random.Random(11)
            for _ in range(260):
                x, y = r.uniform(0, W), r.uniform(0, H); cv.drawCircle(x, y, r.uniform(0.6, 2.2), P(C('#FFFFFF', int(r.uniform(40, 170)))))
        cv.drawCircle(CX, CY, R + 60, P(C(self.th['accent'], 34), blur=60))
        cv.drawCircle(CX, CY, R, P(shader=radial(CX, CY - 120, R * 1.1, [C('#1B2140', 235), C('#0A0C18', 245)])))
        return s.makeImageSnapshot()

    def frame(self, cv, i, cover=False):
        t = i / FPS; fr = self.sim['frames'][min(i, len(self.sim['frames']) - 1)]
        cv.drawImage(self.bg, 0, 0)
        # tremblement sur les grosses fusions
        sx = sy = 0.0
        for (tm, tier, x, y) in self.merges:
            if 0 <= t - tm < 0.35 and tier >= self.N - 4:
                k = math.exp(-(t - tm) * 10) * (6 + 5 * (tier - (self.N - 4)))
                sx += k * math.sin((t - tm) * 77); sy += k * math.cos((t - tm) * 61)
        cv.save(); cv.translate(sx, sy)
        # anneau arc-en-ciel qui tourne
        rot = skia.Matrix.RotateDeg(t * 40, skia.Point(CX, CY))
        cols = [C(c) for c in ('#FF3D6E', '#FF9F1C', '#FFE14D', '#4DFF88', '#2EC9FF', '#7A5CFF', '#FF3DD8', '#FF3D6E')]
        shader = skia.GradientShader.MakeSweep(CX, CY, cols, None, skia.TileMode.kClamp, 0, 360, 0, rot)
        oval = skia.Rect.MakeLTRB(CX - R - 8, CY - R - 8, CX + R + 8, CY + R + 8)
        start = -90 + math.degrees(TH) + 1.5; sweep = 360 - 2 * math.degrees(TH) - 3
        cv.drawArc(oval, start, sweep, False, P(shader=shader, stroke=26, blur=14, alpha=0.75))
        cv.drawArc(oval, start, sweep, False, P(shader=shader, stroke=15))
        yj = CY - R * math.cos(TH); ytop = TOP_IN - 230
        for x in (CX - GAP / 2 - 4, CX + GAP / 2 + 4):
            cv.drawLine(x, ytop, x, yj - 4, P(C('#FFFFFF', 70), stroke=20, blur=8)); cv.drawLine(x, ytop, x, yj - 4, P(C('#F4F1FF'), stroke=9))
        # ligne de danger
        dg = fr['danger']
        if dg > 0.5 and (self.final is None or t < self.final):
            a = (dg - 0.5) / 0.5 * (0.55 + 0.45 * abs(math.sin(t * 9)))
            yl = TOP_IN + 70; half = math.sqrt(max(0, R ** 2 - (yl - CY) ** 2)) - 14
            p = P(C('#FF2E4D'), stroke=6, alpha=min(1, a)); p.setPathEffect(skia.DashPathEffect.Make([26, 18], (t * 80) % 44))
            cv.drawLine(CX - half, yl, CX + half, yl, p)
        # objets
        for (oid, tier, x, y, ang, age, kind) in sorted(fr['o'], key=lambda o: o[1]):
            img = self.spr[tier]; vis = 0.6 + 0.4 * spring(age / 0.3) if kind == 'merge' else 1.0
            cv.save(); cv.translate(x, y); cv.rotate(ang)
            if vis != 1.0: cv.scale(vis, vis)
            cv.drawImage(img, -img.width() / 2, -img.height() / 2, self.samp); cv.restore()
        # effets de fusion : onde + étincelles
        for (tm, tier, x, y) in self.merges:
            d = t - tm
            if 0 <= d < 0.55:
                col = C(self.th['tiers'][tier][2]); r0 = self.RS[tier]
                cv.drawCircle(x, y, r0 * (0.9 + 0.9 * d / 0.55), P(col, stroke=max(3, r0 * 0.12 * (1 - d / 0.55)), alpha=1 - d / 0.55))
                rr = random.Random(int(tm * 1000) + tier)
                for k in range(10 + 2 * tier):
                    a = rr.uniform(0, 2 * math.pi); sp_ = rr.uniform(0.8, 1.6) * r0 * 1.4
                    dd = r0 * 0.6 + sp_ * (1 - math.exp(-d * 6))
                    cv.drawCircle(x + dd * math.cos(a), y + dd * math.sin(a), max(1.5, r0 * 0.07 * (1 - d / 0.55)), P(col, alpha=1 - d / 0.55))
        cv.restore()
        # flash du final
        if self.final is not None and 0 <= t - self.final < 0.6:
            d = (t - self.final) / 0.6; fx, fy = self.final_xy
            cv.drawCircle(fx, fy, 260 + 520 * d, P(C('#FFFFFF'), blur=90, alpha=0.5 * (1 - d)))
            if d < 0.3: cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#FFFFFF'), alpha=0.16 * (1 - d / 0.3)))
        self.hud(cv, t, fr, cover)

    def hud(self, cv, t, fr, cover):
        th = self.th; N = self.N; acc = C(th['accent']); white = C('#F6F3EA')
        fin = self.final is not None and t >= self.final
        y1, y2, f1, f2 = (330, 478, 82, 150) if cover else (205, 338, 70, 128)
        if fin and t - self.final > 2.6 and not cover:
            text_c(cv, 'WHICH THEME NEXT?', W / 2, y1, font('barlow', f1), P(white))
            text_c(cv, 'COMMENT IT', W / 2, y2, font('anton', f2), P(C('#4DFF88')))
        else:
            text_c(cv, th['title1'], W / 2, y1, font('barlow', f1), P(white))
            f = font('anton', f2)
            while f.measureText(th['title2']) > W - 110: f = font('anton', f.getSize() - 4)
            text_c(cv, th['title2'], W / 2, y2, f, P(acc))
        if cover:
            return
        best = fr['best']; name = th['tiers'][best][0] if best < N - 1 or fin else th['tiers'][best][0]
        fm = font('mono', 30); fm.setEmbolden(True)
        # niveau (à gauche de la goulotte) / record (à droite)
        lv = f'LEVEL {best + 1}/{N}'
        cv.drawCircle(98, 418, 9, P(C('#4DFF88'))); cv.drawString(lv, 118, 429, fm, P(white))
        follow = any(a <= t < a + 3.2 for a in (0.38 * self.dur, 0.70 * self.dur))
        lab = '+ FOLLOW FOR MORE' if follow else f'BEST: {name}'
        w = fm.measureText(lab); col = C('#4DFF88') if follow else acc
        pop = 1.0
        for (tm, tier) in self.records:
            if 0 <= t - tm < 0.4: pop = 1 + 0.25 * (1 - spring((t - tm) / 0.4))
        cv.save(); cv.translate(W - 82 - w / 2, 418); cv.scale(pop, pop); cv.drawString(lab, -w / 2, 11, fm, P(col)); cv.restore()
        # score
        sc = f'SCORE: {fr["score"]:,}'
        text_c(cv, sc, W / 2, 1522, font('anton', 76), P(white))
        # échelle des niveaux, dernier caché « ? »
        n = N; gap = min(64, (W - 140) / n); x0 = W / 2 - gap * (n - 1) / 2; yb = 1606
        for k in range(n):
            x = x0 + k * gap; img = self.icon[k]
            reached = k <= fr['best']
            if k == n - 1 and not reached:
                cv.drawCircle(x, yb, 25, P(C('#1A1D2E'))); cv.drawCircle(x, yb, 25, P(acc, stroke=3))
                fq = font('anton', 34); cv.drawString('?', x - fq.measureText('?') / 2, yb + 12, fq, P(acc)); continue
            p = skia.Paint(AntiAlias=True); p.setAlphaf(1.0 if reached else 0.22)
            sc_ = 1.0
            if k == n - 1 and fin: sc_ = 1 + 0.6 * (1 - spring((t - self.final) / 0.6))
            cv.save(); cv.translate(x, yb); cv.scale(sc_ * 0.95, sc_ * 0.95)
            cv.drawImage(img, -img.width() / 2, -img.height() / 2, self.samp, p); cv.restore()
            if k == fr['best']: cv.drawCircle(x, yb, 31, P(acc, stroke=3))
        # bandeau du final
        if fin and t - self.final < 2.6:
            d = t - self.final; s = 0.5 + 0.5 * spring(d / 0.5); f = font('anton', 132)
            cv.save(); cv.translate(W / 2, 760); cv.scale(s, s)
            lab = th['tiers'][N - 1][0] + '!'
            while f.measureText(lab) > W - 120: f = font('anton', f.getSize() - 6)
            text_c(cv, lab, 0, 0, f, P(acc), shadow=True)
            cv.restore()


def render(theme, sim, dur, out_dir, preview=None):
    rd = Renderer(theme, sim, dur); surf = skia.Surface(W, H); cv = surf.getCanvas()
    nfr = int(round(dur * FPS))
    if preview:
        for ts in preview:
            i = min(nfr - 1, int(round(ts * FPS))); rd.frame(cv, i)
            surf.makeImageSnapshot().save(os.path.join(out_dir, f'preview_{ts:05.1f}.png'), skia.kPNG)
        return
    raw = os.path.join(out_dir, 'video_noaudio.mp4')
    ff = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', raw],
                          stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(nfr):
        rd.frame(cv, i)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        if i % 300 == 0: print('frame', i, '/', nfr, round(time.time() - t0, 1), 's', flush=True)
    ff.stdin.close(); ff.wait()
    # couverture : moment chargé, titre dans la zone visible de la grille (3:4)
    ci = int(min(nfr - 1, max(0, ((sim['final'] or dur * 0.8) - 5.0) * FPS)))
    rd.frame(cv, ci, cover=True)
    img = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    from PIL import Image
    Image.fromarray(img[:, :, :3]).save(os.path.join(out_dir, 'cover.jpg'), quality=92)
    return raw


# =============================================================== SON (100 % synthétisé, aucune musique protégée)
def audio(sim, dur, out_wav, theme):
    SR = 48000; n = int(SR * (dur + 0.5)); L = np.zeros(n); Rr = np.zeros(n); N = sim['N']
    rng = np.random.default_rng(7)
    def place(sig, t, g, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        sig = sig[: n - i]; gl, gr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        L[i:i + len(sig)] += sig * g * gl * 1.41; Rr[i:i + len(sig)] += sig * g * gr * 1.41
    def tt(d): return np.arange(int(d * SR)) / SR
    def pluck(f, d=0.7, br=1.0):
        x = tt(d); env = np.exp(-x * (5 + f / 400)) * np.clip(x / 0.003, 0, 1)
        return (np.sin(2 * np.pi * f * x) * 0.62 + np.sin(4 * np.pi * f * x) * 0.22 * np.exp(-x * 9) * br
                + np.sin(6 * np.pi * f * x) * 0.1 * np.exp(-x * 14) * br) * env
    def noise_tick(d=0.035):
        x = tt(d); s = rng.normal(0, 1, len(x)) * np.exp(-x * 140)
        return np.convolve(s, np.ones(6) / 6, 'same')
    def boom(d=1.8):
        x = tt(d); f = 72 * np.exp(-x * 2.4) + 34
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.2)
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    scale = [96, 93, 91, 88, 86, 84, 81, 79, 76, 74, 72, 69]       # do majeur pentatonique, aigu -> grave
    last = {}
    for (tm, tier, x, y) in sim['ev']['merge']:
        if tm - last.get(tier, -1) < 0.045: continue
        last[tier] = tm; f = midi(scale[min(len(scale) - 1, tier - 1)] - (12 if tier >= N - 3 else 0))
        g = 0.16 + 0.05 * tier; place(pluck(f, 0.5 + 0.12 * tier), tm, g, (x - CX) / R * 0.6)
        if tier >= N - 4: place(boom(1.2), tm, 0.25 + 0.08 * (tier - (N - 4)))
    for (tm, tier) in sim['ev']['spawn']: place(noise_tick(), tm, 0.05, 0.0)
    # accroche sonore dès la première image : impact + arpège montant
    place(boom(1.4), 0.0, 0.45)
    for j, m in enumerate((72, 76, 79, 84)): place(pluck(midi(m), 0.6), 0.02 + 0.07 * j, 0.22)
    for (tm, tier) in sim['ev']['record']:
        if tier >= 3: place(pluck(midi(84 + 2 * (tier % 5)), 0.9) * 0.6 + pluck(midi(91 + 2 * (tier % 5)), 0.9) * 0.4, tm + 0.05, 0.22)
    # pulsation + nappe (do / sol / la mineur / fa), intensité qui monte jusqu'au final
    t = np.arange(n) / SR; fin = sim['final'] or dur
    inten = np.interp(t, [0, fin * 0.5, fin - 0.2, fin, fin + 0.6, dur], [0.55, 0.75, 1.0, 1.0, 0.8, 0.7])
    beat = 60 / 120; k = 0.0; kick = np.zeros(n)
    while k < dur:
        x = tt(0.3); f = 52 * (1 + 1.4 * np.exp(-x * 32)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 8)
        i = int(k * SR); kick[i:i + len(s)] += s[: n - i]; k += beat
    chords = [[48, 55, 64], [43, 50, 59], [45, 52, 60], [41, 48, 57]]
    pad = np.zeros(n)
    for ci in range(int(dur / (beat * 8)) + 1):
        a = int(ci * beat * 8 * SR); b = min(n, int((ci + 1) * beat * 8 * SR)); seg_t = np.arange(b - a) / SR
        env = np.clip(seg_t / 0.4, 0, 1) * np.clip((len(seg_t) / SR - seg_t) / 0.4, 0, 1)
        for m in chords[ci % 4]:
            f = midi(m); pad[a:b] += (np.sin(2 * np.pi * f * seg_t) + 0.3 * np.sin(2 * np.pi * 2 * f * seg_t + 0.5)) * env * 0.33
    bed = kick * 0.38 + pad * 0.11
    L += bed * inten; Rr += bed * inten
    # montée avant le final, puis accord final
    if sim['final'] is not None:
        d = 2.2; x = tt(d); sw = np.sin(2 * np.pi * np.cumsum(220 * (4 ** (x / d))) / SR) * (x / d) ** 2
        place(sw * 0.25 + rng.normal(0, 1, len(x)) * (x / d) ** 3 * 0.06, fin - d, 1.0)
        for m in (60, 64, 67, 72, 76): place(pluck(midi(m), 3.0, 0.6), fin, 0.3)
        place(boom(2.4), fin, 0.7)
    # alarme douce quand le cercle est presque plein
    fr = sim['frames']
    for i in range(0, len(fr), 15):
        if fr[i]['danger'] > 0.8 and (sim['final'] is None or i / FPS < sim['final']):
            x = tt(0.12); place(np.sin(2 * np.pi * 1320 * x) * np.exp(-x * 30), i / FPS, 0.1, 0.3)
    mix = np.stack([L, Rr], 1)
    import pyloudnorm as pyln
    m = pyln.Meter(SR); mix = pyln.normalize.loudness(mix, m.integrated_loudness(mix), -14.0)
    a = np.abs(mix); k_, c_ = 0.7, 0.89
    mix = np.where(a > k_, np.sign(mix) * (k_ + (c_ - k_) * np.tanh((a - k_) / (c_ - k_))), mix)
    sf.write(out_wav, mix[: int(SR * dur)].astype(np.float32), SR, subtype='FLOAT')
    return round(m.integrated_loudness(mix), 2)


# =============================================================== MAIN
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--theme', default='planets', choices=list(THEMES)); ap.add_argument('--dur', type=float, default=48)
    ap.add_argument('--seed', type=int); ap.add_argument('--search', type=int, default=0); ap.add_argument('--base', type=int, default=0)
    ap.add_argument('--out', required=True); ap.add_argument('--preview', default='')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    seed = a.seed
    if seed is None:
        t0 = time.time()
        with Pool(max(1, (os.cpu_count() or 2))) as pool:
            res = pool.map(_search_one, [(a.theme, s, a.dur) for s in range(a.base, a.base + max(1, a.search))])
        res.sort(key=lambda r: -r['quality'])
        for r in res[:6]: print('seed', r['seed'], 'ok', r['ok'], 'final', r['final'], 'over', r['overflow'], 'danger', r['danger_max'], 'q', r['quality'])
        print('recherche', round(time.time() - t0, 1), 's ;', sum(r['ok'] for r in res), '/', len(res), 'graines valides', flush=True)
        if not res[0]['ok']: sys.exit('aucune graine valide : relancer avec --base différent ou --search plus grand')
        seed = res[0]['seed']
    sim = simulate(a.theme, seed, a.dur, record=True)
    print('graine', seed, 'final', sim['final'], 'débordement', sim['overflow'], 'fusions', sim['merges'], 'score', sim['score'], flush=True)
    if a.preview:
        render(a.theme, sim, a.dur, a.out, [float(x) for x in a.preview.split(',')]); return
    raw = render(a.theme, sim, a.dur, a.out)
    lufs = audio(sim, a.dur, os.path.join(a.out, 'audio.wav'), a.theme)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', raw, '-i', os.path.join(a.out, 'audio.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(a.out, 'video.mp4')], check=True)
    th = THEMES[a.theme]
    meta = dict(format='fusion', theme=a.theme, seed=seed, dur=a.dur, final_s=sim['final'], overflow_s=sim['overflow'],
                danger_max=sim['danger_max'], merges=sim['merges'], score=sim['score'], lufs=lufs,
                goal=th['tiers'][-1][0], hook=f"{th['title1']} {th['title2']}", next_tease=th['next_tease'])
    json.dump(meta, open(os.path.join(a.out, 'meta.json'), 'w'), indent=1)
    print(json.dumps(meta))


if __name__ == '__main__':
    main()
