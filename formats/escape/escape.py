"""Format « ESCAPE » (projet C, international, sans paroles) : une balle rebondit dans un anneau qui tourne et qui a
une brèche. Chaque balle qui s'échappe fait naître 2 nouvelles balles au centre (donc +1 balle dans l'anneau à chaque
sortie). Quand l'anneau contient TARGET balles, il se brise : c'est la récompense finale. 100 % dessiné et synthétisé
maison (aucune image, musique ni police protégée ; polices libres de assets/fonts).

La recherche de graine garde une partie où l'anneau casse vers 88 % de la vidéo (comme le format fusion).

usage :
  python3 escape.py --dur 34 --search 40 --base 0 --out OUTDIR             # cherche la graine puis rend tout
  python3 escape.py --seed 5 --dur 34 --out OUTDIR --preview 1,15,30,33      # quelques images seulement
Sorties : video.mp4 (avec son), cover.jpg, meta.json (+ preview_*.png en mode aperçu)."""
import argparse, json, math, os, random, subprocess, sys, time
from multiprocessing import Pool
import numpy as np, skia, soundfile as sf

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'fonts')
TF = {k: skia.Typeface.MakeFromFile(os.path.join(FONTS, f)) for k, f in
      {'anton': 'Anton-Regular.ttf', 'barlow': 'BarlowCondensed-ExtraBold.ttf', 'mono': 'JetBrainsMono-VF.ttf'}.items()}

W, H, FPS = 1080, 1920, 30
CX, CY, R = 540, 1000, 400        # l'anneau
BR = 20                           # rayon des balles
SUB = 8                           # sous-pas physiques par image
G = 1500.0                        # gravité (px/s²)
VMIN = 1150.0                     # vitesse minimale après un rebond (garde l'énergie)
GAP = 0.26                        # demi-angle de la brèche (rad)
OMEGA = 1.15                      # vitesse de rotation de l'anneau (rad/s)
TARGET = 64                       # nombre de balles qui brise l'anneau
AIM = 0.88                        # moment visé pour la casse (fraction de la vidéo)
HUES = ['#FF4D6D', '#FFB703', '#4DFF88', '#3AB0FF', '#B86BFF', '#FF7AD9', '#00E5D4', '#FFE14D']


def C(h, a=255):
    h = h.lstrip('#'); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def P(color=None, shader=None, stroke=0, blur=0):
    p = skia.Paint(AntiAlias=True)
    if color is not None: p.setColor(color)
    if shader is not None: p.setShader(shader)
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


# =============================================================== PHYSIQUE (balles sans collision entre elles)
def simulate(seed, dur, record=False):
    rng = random.Random(seed); dt = 1 / FPS / SUB
    balls = [dict(x=CX, y=CY - 120, vx=rng.uniform(-500, 500), vy=-200.0, c=0, out=False, trail=[])]
    ev = dict(bounce=[], escape=[], spawn=[]); frames = []; broke = None; ncol = 1; t = 0.0
    nfr = int(round(dur * FPS))
    for fi in range(nfr):
        for _ in range(SUB):
            t += dt; ang0 = OMEGA * t
            new = []
            for b in balls:
                b['vy'] += G * dt; b['x'] += b['vx'] * dt; b['y'] += b['vy'] * dt
                if b['out'] or broke is not None: continue
                dx, dy = b['x'] - CX, b['y'] - CY; d = math.hypot(dx, dy)
                if d > R - BR:
                    a = math.atan2(dy, dx); rel = (a - ang0 + math.pi) % (2 * math.pi) - math.pi
                    if abs(rel) < GAP - BR / R:                      # dans la brèche : elle s'échappe
                        b['out'] = True; ev['escape'].append((t, b['x'], b['y'], b['c']))
                        for k in range(2):
                            th = rng.uniform(0, 2 * math.pi); sp = rng.uniform(350, 650)
                            new.append(dict(x=CX + rng.uniform(-30, 30), y=CY + rng.uniform(-30, 30), vx=sp * math.cos(th),
                                            vy=sp * math.sin(th), c=ncol % len(HUES), out=False, trail=[]))
                            ncol += 1
                        ev['spawn'].append(t)
                    else:                                             # rebond sur l'anneau
                        nx, ny = dx / d, dy / d; vn = b['vx'] * nx + b['vy'] * ny
                        if vn > 0:
                            b['vx'] -= 2 * vn * nx; b['vy'] -= 2 * vn * ny
                            s = math.hypot(b['vx'], b['vy'])
                            if s < VMIN: b['vx'] *= VMIN / s; b['vy'] *= VMIN / s
                            # petite déviation tangentielle pour éviter les trajectoires répétitives
                            b['vx'] += -ny * rng.uniform(-60, 60); b['vy'] += nx * rng.uniform(-60, 60)
                            ev['bounce'].append((t, b['x'], b['c']))
                        b['x'] = CX + nx * (R - BR); b['y'] = CY + ny * (R - BR)
            balls += new
            balls = [b for b in balls if not (b['out'] and (b['y'] > H + 80 or b['x'] < -80 or b['x'] > W + 80))]
            inside = sum(1 for b in balls if not b['out'])
            if broke is None and inside >= TARGET:
                broke = t
                for b in balls:                                       # l'anneau casse : tout s'envole
                    if not b['out']:
                        dx, dy = b['x'] - CX, b['y'] - CY; d = max(1, math.hypot(dx, dy))
                        b['vx'] += dx / d * 900; b['vy'] += dy / d * 900 - 300; b['out'] = True
        inside = sum(1 for b in balls if not b['out'])
        for b in balls:
            b['trail'].append((b['x'], b['y'])); b['trail'] = b['trail'][-7:]
        if record:
            frames.append(dict(t=(fi + 1) / FPS, ang=OMEGA * (fi + 1) / FPS, inside=inside if broke is None else TARGET,
                               escaped=len(ev['escape']),
                               balls=[(b['x'], b['y'], b['c'], b['out'], list(b['trail'])) for b in balls]))
        if len(balls) > 400: break
    res = dict(seed=seed, dur=dur, broke=broke, escapes=len(ev['escape']), bounces=len(ev['bounce']))
    res['ok'] = broke is not None and 0.80 * dur <= broke <= 0.92 * dur
    res['quality'] = -abs((broke or 0) - AIM * dur)
    if record: res['frames'] = frames; res['ev'] = ev
    return res


def _search_one(args):
    return simulate(*args)


# =============================================================== IMAGE
def font(name, size): return skia.Font(TF[name], size)


def text_c(cv, s, x, y, f, paint, shadow=True):
    w = f.measureText(s)
    if shadow: cv.drawString(s, x - w / 2 + 4, y + 6, f, P(C('#000000', 160)))
    cv.drawString(s, x - w / 2, y, f, paint)


def spring(x):
    return 0 if x <= 0 else 1 if x >= 1 else 1 - math.exp(-6 * x) * math.cos(10 * x)


class Renderer:
    def __init__(self, sim):
        self.sim = sim; self.broke = sim['broke']; self.bg = self.make_bg()
        self.frag = []
        r = random.Random(5)
        for k in range(28):                                           # éclats de l'anneau
            a = 2 * math.pi * k / 28
            self.frag.append((a, r.uniform(500, 1100), r.uniform(-700, -100), r.uniform(-6, 6)))

    def make_bg(self):
        s = skia.Surface(W, H); cv = s.getCanvas()
        cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, 0), skia.Point(0, H)], [C('#0B0F24'), C('#04050C')])))
        r = random.Random(11)
        for _ in range(200):
            cv.drawCircle(r.uniform(0, W), r.uniform(0, H), r.uniform(0.6, 2.0), P(C('#FFFFFF', int(r.uniform(30, 140)))))
        cv.drawCircle(CX, CY, R + 70, P(C('#3AB0FF', 30), blur=70))
        cv.drawCircle(CX, CY, R, P(C('#0E1430', 230)))
        return s.makeImageSnapshot()

    def ring(self, cv, ang, t):
        sweep = skia.GradientShader.MakeSweep(CX, CY, [C(h) for h in HUES + HUES[:1]])
        if self.broke is None or t < self.broke:
            start = math.degrees(ang + GAP); span = 360 - math.degrees(2 * GAP)
            path = skia.Path(); path.addArc(skia.Rect.MakeXYWH(CX - R, CY - R, 2 * R, 2 * R), start, span)
            cv.drawPath(path, P(shader=sweep, stroke=26, blur=14))
            cv.drawPath(path, P(shader=sweep, stroke=14))
            return
        d = t - self.broke
        ang_b = OMEGA * self.broke
        for (a, sp, up, spin) in self.frag:
            seg = 2 * math.pi / 28
            mid = a + seg / 2
            rel = (mid - ang_b + math.pi) % (2 * math.pi) - math.pi
            if abs(rel) < GAP: continue
            ox = math.cos(mid) * sp * d; oy = math.sin(mid) * sp * d + up * d + 0.5 * G * d * d
            cv.save(); cv.translate(ox, oy); cv.rotate(spin * d * 30, CX + R * math.cos(mid), CY + R * math.sin(mid))
            path = skia.Path(); path.addArc(skia.Rect.MakeXYWH(CX - R, CY - R, 2 * R, 2 * R), math.degrees(a), math.degrees(seg) * 0.85)
            cv.drawPath(path, P(shader=sweep, stroke=14)); cv.restore()

    def frame(self, cv, i, cover=False):
        fr = self.sim['frames'][min(i, len(self.sim['frames']) - 1)]; t = (i + 1) / FPS
        shake = 0
        if self.broke is not None and 0 <= t - self.broke < 0.6: shake = 14 * (1 - (t - self.broke) / 0.6)
        cv.save(); cv.translate(random.uniform(-shake, shake), random.uniform(-shake, shake))
        cv.drawImage(self.bg, 0, 0)
        if self.broke is not None and 0 <= t - self.broke < 0.35:
            cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#FFFFFF', int(200 * (1 - (t - self.broke) / 0.35)))))
        self.ring(cv, fr['ang'], t)
        for (x, y, c, out, trail) in fr['balls']:
            col = HUES[c]
            for k, (tx, ty) in enumerate(trail[:-1]):
                cv.drawCircle(tx, ty, BR * (0.4 + 0.6 * k / len(trail)), P(C(col, int(25 + 60 * k / len(trail)))))
            cv.drawCircle(x, y, BR + 6, P(C(col, 90), blur=10))
            cv.drawCircle(x, y, BR, P(shader=skia.GradientShader.MakeRadial(skia.Point(x - 6, y - 7), BR * 1.3, [C('#FFFFFF'), C(col)], [0.0, 0.55])))
        cv.restore()
        self.hud(cv, t, fr, cover)

    def hud(self, cv, t, fr, cover):
        white = C('#F7F5EE'); yel = C('#FFC21A')
        ended = self.broke is not None and t >= self.broke
        if ended and t - self.broke > 1.6 and not cover:
            text_c(cv, 'HOW MANY BALLS NEXT TIME?', W / 2, 250, font('barlow', 66), P(white))
            text_c(cv, 'COMMENT YOUR GUESS', W / 2, 360, font('anton', 108), P(C('#4DFF88')))
        else:
            text_c(cv, '1 ESCAPE = 2 NEW BALLS', W / 2, 250, font('barlow', 70), P(white))
            text_c(cv, 'WILL IT BREAK?', W / 2, 375, font('anton', 132), P(yel))
        # compteur sous l'anneau
        n = fr['inside']
        text_c(cv, f'BALLS: {n} / {TARGET}', W / 2, CY + R + 140, font('anton', 84), P(white))
        bw = 560; x0 = W / 2 - bw / 2; y0 = CY + R + 175
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, bw, 22), 11, 11), P(C('#FFFFFF', 40)))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, bw * min(1, n / TARGET), 22), 11, 11), P(yel))
        fm = font('mono', 30); fm.setEmbolden(True)
        if not cover and self.broke and 0.38 * self.sim['dur'] < t < 0.38 * self.sim['dur'] + 2.5 or \
                (not cover and self.broke and 0.68 * self.sim['dur'] < t < 0.68 * self.sim['dur'] + 2.5):
            text_c(cv, '+ FOLLOW FOR MORE', W / 2, CY + R + 260, fm, P(C('#4DFF88')), shadow=False)
        if ended:
            d = t - self.broke; s = 0.5 + 0.5 * spring(d / 0.5); f = font('anton', 150)
            cv.save(); cv.translate(W / 2, CY); cv.scale(s, s)
            text_c(cv, 'IT BROKE!', 0, 50, f, P(yel)); cv.restore()


def render(sim, out_dir, preview=None):
    rd = Renderer(sim); surf = skia.Surface(W, H); cv = surf.getCanvas(); dur = sim['dur']
    nfr = len(sim['frames'])
    if preview:
        for ts in preview:
            i = min(nfr - 1, int(round(ts * FPS))); rd.frame(cv, i)
            surf.makeImageSnapshot().save(os.path.join(out_dir, f'preview_{ts:05.1f}.png'), skia.kPNG)
        return
    raw = os.path.join(out_dir, 'video_noaudio.mp4')
    ff = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', raw],
                          stdin=subprocess.PIPE)
    for i in range(nfr):
        rd.frame(cv, i); ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close(); ff.wait()
    ci = int(min(nfr - 1, max(0, (sim['broke'] - 3.0) * FPS)))       # couverture : anneau presque plein
    rd.frame(cv, ci, cover=True)
    from PIL import Image
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).save(
        os.path.join(out_dir, 'cover.jpg'), quality=92)
    return raw


# =============================================================== SON (100 % synthétisé)
def limit(x, SR, ceil=0.8, look=0.006, rel=0.08):
    """Limiteur à gain lissé (anticipation 6 ms) : pas d'écrêtage carré, donc pas de dépassement après l'encodage AAC."""
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    env = maximum_filter1d(np.abs(x).max(1), int(look * SR) * 2 + 1)
    g = np.minimum(1.0, ceil / np.maximum(env, 1e-9))
    g = uniform_filter1d(g, int(look * SR))                     # attaque douce
    out = np.empty_like(g); a = math.exp(-1 / (rel * SR)); cur = 1.0
    for i, v in enumerate(g):                                     # relâchement exponentiel
        cur = v if v < cur else v + (cur - v) * a; out[i] = cur
    y = x * out[:, None]
    return np.clip(y, -ceil, ceil)


def audio(sim, out_wav):
    SR = 48000; dur = sim['dur']; n = int(SR * (dur + 0.5)); L = np.zeros(n); Rr = np.zeros(n)
    rng = np.random.default_rng(7); midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    def tt(d): return np.arange(int(d * SR)) / SR
    def place(sig, t, g, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        sig = sig[: n - i]; gl, gr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        L[i:i + len(sig)] += sig * g * gl * 1.41; Rr[i:i + len(sig)] += sig * g * gr * 1.41
    def pluck(f, d=0.5):
        x = tt(d); env = np.exp(-x * (6 + f / 400)) * np.clip(x / 0.003, 0, 1)
        return (np.sin(2 * np.pi * f * x) * 0.65 + np.sin(4 * np.pi * f * x) * 0.2 * np.exp(-x * 10)) * env
    def boom(d=1.8):
        x = tt(d); f = 72 * np.exp(-x * 2.4) + 34
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.2)
    # rebonds : une mélodie pentatonique qui avance d'une note à chaque rebond (limité à ~10 notes/s)
    mel = [72, 74, 76, 79, 81, 84, 81, 79, 76, 74]; k = 0; last = -1
    for (tm, x, c) in sim['ev']['bounce']:
        if tm - last < 0.1: continue
        last = tm; place(pluck(midi(mel[k % len(mel)])), tm, 0.16, (x - CX) / R * 0.6); k += 1
    for (tm, x, y, c) in sim['ev']['escape']:
        if sim['broke'] and tm > sim['broke']: continue
        place(pluck(midi(91), 0.8) * 0.6 + pluck(midi(96), 0.8) * 0.4, tm, 0.2, (x - CX) / R * 0.6)
    place(boom(1.4), 0.0, 0.45)
    for j, m in enumerate((72, 76, 79, 84)): place(pluck(midi(m), 0.6), 0.02 + 0.07 * j, 0.22)
    t = np.arange(n) / SR; fin = sim['broke'] or dur
    inten = np.interp(t, [0, fin * 0.5, fin, fin + 0.6, dur + 0.5], [0.55, 0.75, 1.0, 0.8, 0.7])
    beat = 60 / 120; kick = np.zeros(n); kk = 0.0
    while kk < dur:
        x = tt(0.3); f = 52 * (1 + 1.4 * np.exp(-x * 32)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 8)
        i = int(kk * SR); kick[i:i + len(s)] += s[: n - i]; kk += beat
    chords = [[48, 55, 64], [43, 50, 59], [45, 52, 60], [41, 48, 57]]; pad = np.zeros(n)
    for ci in range(int(dur / (beat * 8)) + 1):
        a = int(ci * beat * 8 * SR); b = min(n, int((ci + 1) * beat * 8 * SR)); st = np.arange(b - a) / SR
        env = np.clip(st / 0.4, 0, 1) * np.clip((len(st) / SR - st) / 0.4, 0, 1)
        for m in chords[ci % 4]:
            f = midi(m); pad[a:b] += (np.sin(2 * np.pi * f * st) + 0.3 * np.sin(4 * np.pi * f * st + 0.5)) * env * 0.33
    bed = kick * 0.38 + pad * 0.11; L += bed * inten; Rr += bed * inten
    if sim['broke'] is not None:
        d = 2.2; x = tt(d); sw = np.sin(2 * np.pi * np.cumsum(220 * (4 ** (x / d))) / SR) * (x / d) ** 2
        place(sw * 0.25, fin - d, 1.0)
        place(rng.normal(0, 1, int(0.6 * SR)) * np.exp(-tt(0.6) * 7) * 0.18, fin, 1.0)   # verre qui casse (bruit)
        for m in (60, 64, 67, 72, 76): place(pluck(midi(m), 3.0), fin, 0.2)
        place(boom(2.4), fin, 0.42)
    mix = np.stack([L, Rr], 1)
    import pyloudnorm as pyln
    m = pyln.Meter(SR); mix = pyln.normalize.loudness(mix, m.integrated_loudness(mix), -14.0)
    mix = limit(mix, SR)
    sf.write(out_wav, mix[: int(SR * dur)].astype(np.float32), SR, subtype='FLOAT')
    return round(m.integrated_loudness(mix), 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dur', type=float, default=34); ap.add_argument('--seed', type=int)
    ap.add_argument('--search', type=int, default=40); ap.add_argument('--base', type=int, default=0)
    ap.add_argument('--out', required=True); ap.add_argument('--preview', default='')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); seed = a.seed
    if seed is None:
        with Pool(max(1, os.cpu_count() or 2)) as pool:
            res = pool.map(_search_one, [(s, a.dur) for s in range(a.base, a.base + a.search)])
        res.sort(key=lambda r: (not r['ok'], -r['quality']))
        for r in res[:6]: print('seed', r['seed'], 'ok', r['ok'], 'broke', r['broke'], 'escapes', r['escapes'])
        print(sum(r['ok'] for r in res), '/', len(res), 'graines valides', flush=True)
        if not res[0]['ok']: sys.exit('aucune graine valide : relancer avec --base différent ou --search plus grand')
        seed = res[0]['seed']
    sim = simulate(seed, a.dur, record=True)
    print('graine', seed, 'casse', sim['broke'], 'sorties', sim['escapes'], flush=True)
    if a.preview:
        render(sim, a.out, [float(x) for x in a.preview.split(',')]); return
    raw = render(sim, a.out); lufs = audio(sim, os.path.join(a.out, 'audio.wav'))
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', raw, '-i', os.path.join(a.out, 'audio.wav'),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', os.path.join(a.out, 'video.mp4')], check=True)
    meta = dict(format='escape', seed=seed, dur=a.dur, broke_s=sim['broke'], escapes=sim['escapes'], target=TARGET, lufs=lufs,
                hook='1 ESCAPE = 2 NEW BALLS · WILL IT BREAK?')
    json.dump(meta, open(os.path.join(a.out, 'meta.json'), 'w'), indent=1); print(json.dumps(meta))


if __name__ == '__main__':
    main()
