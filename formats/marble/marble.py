"""Format « MARBLE RACE » (projet D, international, sans paroles) : 4 billes de couleur (RED, BLUE, GREEN, YELLOW)
descendent un parcours de picots. La caméra suit la course, un classement en direct et une barre de progression
restent visibles ; la ligne d'arrivée est placée pour que la course se termine vers 88 % de la vidéo, avec plusieurs
changements de tête et une arrivée serrée (recherche de graine). 100 % dessiné et synthétisé maison.

usage :
  python3 marble.py --dur 34 --search 60 --base 0 --out OUTDIR              # cherche la graine puis rend tout
  python3 marble.py --seed 5 --dur 34 --out OUTDIR --preview 1,12,25,31,33    # quelques images seulement
Sorties : video.mp4 (avec son), cover.jpg, meta.json (+ preview_*.png en mode aperçu)."""
import argparse, json, math, os, random, subprocess, sys
from multiprocessing import Pool
import numpy as np, skia, soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'escape'))
from escape import C, P, text_c, font, spring, limit  # noqa: E402  (outils communs déjà testés)

W, H, FPS = 1080, 1920, 30
XL, XR = 90, 990                  # murs du parcours
BR = 24                           # rayon des billes
PR = 11                           # rayon des picots
ROW = 120                         # espacement vertical des rangées de picots
COLS = 7                          # picots par rangée
TOP = 520                         # 1re rangée (monde)
LEN = 16000                       # longueur du parcours simulé (monde)
G = 1300.0; DRAG = 0.9; VMAX = 1050.0; REST = 0.55
SUB = 6
AIM = 0.88
NAMES = ['RED', 'BLUE', 'GREEN', 'YELLOW']
HUES = ['#FF3B4E', '#2E8BFF', '#2EE07A', '#FFD21A']


def course(seed):
    """Picots en quinconce avec un léger désordre ; quelques rangées « portes » (un trou) pour créer des écarts."""
    r = random.Random(seed * 7 + 1); pegs = []
    rows = int((LEN - TOP) / ROW)
    for k in range(rows):
        y = TOP + k * ROW; off = (k % 2) * 0.5; gate = r.random() < 0.12
        hole = r.randrange(COLS) if gate else -1
        for c in range(COLS):
            if c == hole: continue
            x = XL + (XR - XL) * (c + 0.5 + off) / (COLS + 0.5) + r.uniform(-14, 14)
            pegs.append((x, y + r.uniform(-10, 10)))
    return pegs, rows


def simulate(seed, dur, record=False):
    rng = random.Random(seed); dt = 1 / FPS / SUB
    pegs, rows = course(seed)
    byrow = {}
    for (x, y) in pegs: byrow.setdefault(int(round((y - TOP) / ROW)), []).append((x, y))
    xs = [540 - 120, 540 - 40, 540 + 40, 540 + 120]; rng.shuffle(xs)
    m = [dict(x=xs[i], y=300.0, vx=rng.uniform(-60, 60), vy=0.0) for i in range(4)]
    ev = dict(hit=[], clack=[]); hist = []; frames = []
    nfr = int(round(dur * FPS))
    for fi in range(nfr):
        for _ in range(SUB):
            for b in m:
                b['vy'] += G * dt
                b['vx'] *= 1 - DRAG * dt; b['vy'] *= 1 - DRAG * dt * 0.5
                s = math.hypot(b['vx'], b['vy'])
                if s > VMAX: b['vx'] *= VMAX / s; b['vy'] *= VMAX / s
                b['x'] += b['vx'] * dt; b['y'] += b['vy'] * dt
                if b['x'] < XL + BR: b['x'] = XL + BR; b['vx'] = abs(b['vx']) * REST
                if b['x'] > XR - BR: b['x'] = XR - BR; b['vx'] = -abs(b['vx']) * REST
                k0 = int(round((b['y'] - TOP) / ROW))
                for k in (k0 - 1, k0, k0 + 1):
                    for (px, py) in byrow.get(k, ()):
                        dx, dy = b['x'] - px, b['y'] - py; d = math.hypot(dx, dy)
                        if 0 < d < BR + PR:
                            nx, ny = dx / d, dy / d; vn = b['vx'] * nx + b['vy'] * ny
                            b['x'] = px + nx * (BR + PR); b['y'] = py + ny * (BR + PR)
                            if vn < 0:
                                b['vx'] -= (1 + REST) * vn * nx; b['vy'] -= (1 + REST) * vn * ny
                                b['vx'] += rng.uniform(-90, 90)
                                if -vn > 150: ev['hit'].append((fi / FPS, b['x'], m.index(b)))
            for i in range(4):                                   # chocs entre billes
                for j in range(i + 1, 4):
                    a, b = m[i], m[j]; dx, dy = b['x'] - a['x'], b['y'] - a['y']; d = math.hypot(dx, dy)
                    if 0 < d < 2 * BR:
                        nx, ny = dx / d, dy / d; ov = 2 * BR - d
                        a['x'] -= nx * ov / 2; a['y'] -= ny * ov / 2; b['x'] += nx * ov / 2; b['y'] += ny * ov / 2
                        rv = (b['vx'] - a['vx']) * nx + (b['vy'] - a['vy']) * ny
                        if rv < 0:
                            a['vx'] += rv * nx * 0.9; a['vy'] += rv * ny * 0.9; b['vx'] -= rv * nx * 0.9; b['vy'] -= rv * ny * 0.9
                            if -rv > 120: ev['clack'].append((fi / FPS, (a['x'] + b['x']) / 2))
        hist.append([b['y'] for b in m])
        if record: frames.append([(b['x'], b['y']) for b in m])
    # ligne d'arrivée : là où se trouve la tête au moment visé
    T = int(AIM * nfr) - 1; finish = max(hist[T])
    fin_t = [None] * 4
    for fi, ys in enumerate(hist):
        for i, y in enumerate(ys):
            if fin_t[i] is None and y >= finish: fin_t[i] = (fi + 1) / FPS
    order = sorted(range(4), key=lambda i: (fin_t[i] or 1e9, -hist[-1][i]))
    winner = order[0]
    leads = []; cur = None
    for fi, ys in enumerate(hist[:T + 1]):
        if fi < FPS * 2: continue                                 # on ignore le départ
        ld = max(range(4), key=lambda i: ys[i])
        if ld != cur: leads.append(((fi + 1) / FPS, ld)); cur = ld
    changes = len(leads) - 1
    spread = sum(max(ys) - min(ys) for ys in hist[:T + 1]) / (T + 1)
    gap2 = (fin_t[order[1]] - fin_t[winner]) if fin_t[order[1]] else 9.0
    last_change = leads[-1][0] if leads else 0
    res = dict(seed=seed, dur=dur, finish_y=finish, winner=winner, order=order, fin_t=fin_t, changes=changes,
               gap2=round(gap2, 2), spread=round(spread), last_change=round(last_change, 2), finish_s=fin_t[winner])
    # bonne course : >= 4 changements de tête, dernier changement dans les 5 dernières s avant l'arrivée, arrivée serrée
    res['ok'] = changes >= 4 and last_change >= fin_t[winner] - 5 and gap2 <= 0.8 and finish > 6000 and spread < 1100
    res['quality'] = changes * 0.5 + last_change / dur * 4 - gap2 * 2 - spread / 600
    if record: res['frames'] = frames; res['ev'] = ev; res['leads'] = leads; res['pegs'] = pegs; res['hist'] = hist
    return res


def _search_one(args): return simulate(*args)


class Renderer:
    def __init__(self, sim):
        self.s = sim; self.F = sim['finish_y']; self.cam = []; self.zoom = []
        cam = z = None
        for fr in sim['frames']:              # caméra : cadre tout le peloton (zoom arrière si besoin), lissée
            ys = [min(y, self.F + 150) for _, y in fr]; lo, hi = min(ys), max(ys)
            tz = max(0.42, min(1.0, (H * 0.52) / (hi - lo + 260)))
            mid = (lo + hi) / 2 + 60
            z = tz if z is None else z + (tz - z) * 0.08
            cam = mid if cam is None else cam + (mid - cam) * 0.15
            self.cam.append(cam); self.zoom.append(z)
        r = random.Random(3); self.stars = [(r.uniform(0, W), r.uniform(0, H * 3), r.uniform(0.6, 2), r.uniform(30, 120)) for _ in range(160)]

    def ranking(self, i):
        fr = self.s['frames'][i]; t = (i + 1) / FPS; ft = self.s['fin_t']
        return sorted(range(4), key=lambda k: (ft[k] if ft[k] is not None and ft[k] <= t else 1e9, -fr[k][1]))

    def frame(self, cv, i, cover=False):
        s = self.s; fr = s['frames'][i]; t = (i + 1) / FPS; z = self.zoom[i]
        cy = self.cam[i] - (H * 0.47) / z                 # haut du cadre (monde)
        vh = H / z
        cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, 0), skia.Point(0, H)], [C('#0D1030'), C('#05060F')])))
        for (x, y, rr, a) in self.stars:
            yy = (y - self.cam[i] * 0.3) % (H * 1.0); cv.drawCircle(x, yy, rr, P(C('#FFFFFF', int(a))))
        cv.save(); cv.translate(W / 2, H * 0.47); cv.scale(z, z); cv.translate(-W / 2, -self.cam[i])
        # murs
        for x in (XL - 6, XR + 6):
            cv.drawLine(x, cy - 50, x, cy + vh + 50, P(C('#7A5CFF', 120), stroke=16, blur=10))
            cv.drawLine(x, cy - 50, x, cy + vh + 50, P(C('#B9A8FF'), stroke=6))
        # picots visibles
        for (px, py) in s['pegs']:
            if cy - 40 < py < cy + vh + 40:
                cv.drawCircle(px, py, PR + 5, P(C('#8FD8FF', 60), blur=6)); cv.drawCircle(px, py, PR, P(C('#DDF3FF')))
        # ligne d'arrivée (damier maison)
        F = self.F + BR
        if cy - 100 < F < cy + vh + 100:
            sq = 30
            for k in range(int((XR - XL) / sq) + 1):
                for j in range(2):
                    col = C('#FFFFFF') if (k + j) % 2 == 0 else C('#111111')
                    cv.drawRect(skia.Rect.MakeXYWH(XL + k * sq, F + j * sq, min(sq, XR - XL - k * sq), sq), P(col))
            text_c(cv, 'FINISH', W / 2, F + 150, font('anton', 90), P(C('#FFFFFF')))
        # billes
        for k, (x, y) in enumerate(fr):
            col = HUES[k]
            if i > 0:
                for j in range(1, 6):
                    px, py = s['frames'][max(0, i - j)][k]
                    cv.drawCircle(px, py, BR * (1 - j * 0.13), P(C(col, int(70 - j * 11))))
            cv.drawCircle(x, y, BR + 9, P(C(col, 110), blur=12))
            cv.drawCircle(x, y, BR, P(shader=skia.GradientShader.MakeRadial(skia.Point(x - 7, y - 8), BR * 1.3, [C('#FFFFFF'), C(col)], [0.0, 0.5])))
        cv.restore()
        self.hud(cv, i, t, cover)

    def hud(self, cv, i, t, cover):
        s = self.s; white = C('#F7F5EE'); yel = C('#FFC21A'); w = s['winner']; wt = s['fin_t'][w]
        ended = t >= wt
        cv.drawRect(skia.Rect.MakeWH(W, 300), P(shader=skia.GradientShader.MakeLinear(
            [skia.Point(0, 0), skia.Point(0, 300)], [C('#05060F', 235), C('#05060F', 0)])))
        if ended and not cover:
            d = t - wt; sc = 0.5 + 0.5 * spring(d / 0.5)
            cv.save(); cv.translate(W / 2, 330); cv.scale(sc, sc)
            text_c(cv, f'{NAMES[w]} WINS!', 0, 0, font('anton', 150), P(C(HUES[w]))); cv.restore()
            if d > 1.2:
                text_c(cv, 'DID YOU GUESS RIGHT?', W / 2, 470, font('barlow', 72), P(white))
                text_c(cv, 'COMMENT BELOW', W / 2, 570, font('anton', 100), P(C('#4DFF88')))
        else:
            text_c(cv, 'WHICH COLOR WINS?', W / 2, 200, font('anton', 120), P(yel))
            text_c(cv, 'COMMENT BEFORE THE END', W / 2, 285, font('barlow', 64), P(white))
        # classement en direct
        rk = self.ranking(i); y0 = H - 250
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, y0 - 70, W - 120, 200), 30, 30), P(C('#05060F', 200)))
        for pos, k in enumerate(rk):
            x = 60 + (W - 120) * (pos + 0.5) / 4
            cv.drawCircle(x - 60, y0 + 6, 26, P(C(HUES[k])))
            fn = font('anton', 64 if pos == 0 else 52)
            cv.drawString(f'{pos + 1}', x - 20, y0 + 28, fn, P(yel if pos == 0 else white))
            nf = font('barlow', 40); nw = nf.measureText(NAMES[k])
            cv.drawString(NAMES[k], x - nw / 2 - 20, y0 + 95, nf, P(C(HUES[k])))
        # progression de la tête vers l'arrivée
        fr = s['frames'][i]
        bx, by, bw = 120, H - 360, W - 240
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx, by, bw, 18), 9, 9), P(C('#FFFFFF', 45)))
        for k in range(4):
            pk = min(1.0, max(0.0, (fr[k][1] - 300) / (self.F - 300)))
            cv.drawCircle(bx + bw * pk, by + 9, 15, P(C(HUES[k])))
        cv.drawString('FINISH', bx + bw - 60, by - 14, font('barlow', 30), P(white))
        fm = font('mono', 30); fm.setEmbolden(True)
        dur = s['dur']
        if not cover and (0.38 * dur < t < 0.38 * dur + 2.5 or 0.68 * dur < t < 0.68 * dur + 2.5):
            text_c(cv, '+ FOLLOW FOR MORE RACES', W / 2, H - 395, fm, P(C('#4DFF88')), shadow=False)


def render(sim, out_dir, preview=None):
    rd = Renderer(sim); surf = skia.Surface(W, H); cv = surf.getCanvas(); nfr = len(sim['frames'])
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
    ci = int(min(nfr - 1, max(0, (sim['fin_t'][sim['winner']] * 0.5) * FPS)))   # couverture : milieu de course, peloton serré
    rd.frame(cv, ci, cover=True)
    from PIL import Image
    Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3]).save(
        os.path.join(out_dir, 'cover.jpg'), quality=92)
    return raw


def audio(sim, out_wav):
    SR = 48000; dur = sim['dur']; n = int(SR * (dur + 0.5)); L = np.zeros(n); Rr = np.zeros(n)
    rng = np.random.default_rng(9); midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    def tt(d): return np.arange(int(d * SR)) / SR
    def place(sig, t, g, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        sig = sig[: n - i]; gl, gr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        L[i:i + len(sig)] += sig * g * gl * 1.41; Rr[i:i + len(sig)] += sig * g * gr * 1.41
    def pluck(f, d=0.4):
        x = tt(d); env = np.exp(-x * (9 + f / 300)) * np.clip(x / 0.002, 0, 1)
        return (np.sin(2 * np.pi * f * x) * 0.7 + np.sin(6 * np.pi * f * x) * 0.15 * np.exp(-x * 20)) * env
    def boom(d=1.6):
        x = tt(d); f = 70 * np.exp(-x * 2.4) + 34
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.2)
    wt = sim['fin_t'][sim['winner']]
    notes = [84, 86, 88, 91, 93, 96]; last = -1
    for (tm, x, k) in sim['ev']['hit']:                           # picots : petites notes (max ~14/s)
        if tm - last < 0.07 or tm > wt: continue
        last = tm; place(pluck(midi(notes[int(x) % len(notes)] - 12 * (k % 2))), tm, 0.09, (x - 540) / 540 * 0.7)
    for (tm, x) in sim['ev']['clack']:
        if tm > wt: continue
        place(rng.normal(0, 1, int(0.04 * SR)) * np.exp(-tt(0.04) * 90), tm, 0.12, (x - 540) / 540 * 0.6)
    for (tm, k) in sim['leads'][1:]:                              # changement de tête : « ding » montant
        place(pluck(midi(79), 0.6) + pluck(midi(86), 0.6) * 0.7, tm, 0.2)
    place(boom(1.3), 0.0, 0.45)
    for j, m in enumerate((67, 67, 67, 79)): place(pluck(midi(m), 0.5 if j < 3 else 1.0), 0.02 + 0.28 * j, 0.25)  # 3-2-1-GO
    t = np.arange(n) / SR
    inten = np.interp(t, [0, wt * 0.5, wt, wt + 0.6, dur + 0.5], [0.6, 0.8, 1.0, 0.8, 0.7])
    beat = 60 / 132; kick = np.zeros(n); kk = 0.0
    while kk < dur:
        x = tt(0.3); f = 52 * (1 + 1.4 * np.exp(-x * 32)); sg = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 8)
        i = int(kk * SR); kick[i:i + len(sg)] += sg[: n - i]; kk += beat
    chords = [[45, 52, 60], [41, 48, 57], [48, 55, 64], [43, 50, 59]]; pad = np.zeros(n)
    for ci in range(int(dur / (beat * 8)) + 1):
        a = int(ci * beat * 8 * SR); b = min(n, int((ci + 1) * beat * 8 * SR)); st = np.arange(b - a) / SR
        env = np.clip(st / 0.4, 0, 1) * np.clip((len(st) / SR - st) / 0.4, 0, 1)
        for m in chords[ci % 4]:
            f = midi(m); pad[a:b] += (np.sin(2 * np.pi * f * st) + 0.3 * np.sin(4 * np.pi * f * st + 0.5)) * env * 0.33
    bed = kick * 0.38 + pad * 0.11; L += bed * inten; Rr += bed * inten
    d = 2.0; x = tt(d); sw = np.sin(2 * np.pi * np.cumsum(260 * (3 ** (x / d))) / SR) * (x / d) ** 2
    place(sw * 0.2, wt - d, 1.0)
    for j, m in enumerate((72, 76, 79, 84)): place(pluck(midi(m), 2.5), wt + 0.09 * j, 0.22)   # fanfare d'arrivée
    place(boom(2.2), wt, 0.4)
    mix = np.stack([L, Rr], 1)
    import pyloudnorm as pyln
    mtr = pyln.Meter(SR); mix = pyln.normalize.loudness(mix, mtr.integrated_loudness(mix), -14.0)
    mix = limit(mix, SR)
    sf.write(out_wav, mix[: int(SR * dur)].astype(np.float32), SR, subtype='FLOAT')
    return round(mtr.integrated_loudness(mix), 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dur', type=float, default=34); ap.add_argument('--seed', type=int)
    ap.add_argument('--search', type=int, default=60); ap.add_argument('--base', type=int, default=0)
    ap.add_argument('--out', required=True); ap.add_argument('--preview', default='')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); seed = a.seed
    if seed is None:
        with Pool(max(1, os.cpu_count() or 2)) as pool:
            res = pool.map(_search_one, [(s, a.dur) for s in range(a.base, a.base + a.search)])
        res.sort(key=lambda r: (not r['ok'], -r['quality']))
        for r in res[:6]:
            print('seed', r['seed'], 'ok', r['ok'], 'win', NAMES[r['winner']], 'changes', r['changes'], 'gap2', r['gap2'], 'spread', r['spread'],
                  'last_change', r['last_change'], 'finish_s', r['finish_s'], 'finish_y', round(r['finish_y']))
        print(sum(r['ok'] for r in res), '/', len(res), 'graines valides', flush=True)
        if not res[0]['ok']: sys.exit('aucune graine valide : relancer avec --base différent ou --search plus grand')
        seed = res[0]['seed']
    sim = simulate(seed, a.dur, record=True)
    print('graine', seed, 'vainqueur', NAMES[sim['winner']], 'arrivée', sim['finish_s'], 'changements', sim['changes'], flush=True)
    if a.preview:
        render(sim, a.out, [float(x) for x in a.preview.split(',')]); return
    raw = render(sim, a.out); lufs = audio(sim, os.path.join(a.out, 'audio.wav'))
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', raw, '-i', os.path.join(a.out, 'audio.wav'),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', os.path.join(a.out, 'video.mp4')], check=True)
    meta = dict(format='marble', seed=seed, dur=a.dur, winner=NAMES[sim['winner']], order=[NAMES[k] for k in sim['order']],
                finish_s=sim['finish_s'], lead_changes=sim['changes'], gap2_s=sim['gap2'], lufs=lufs,
                hook='WHICH COLOR WINS? · COMMENT BEFORE THE END')
    json.dump(meta, open(os.path.join(a.out, 'meta.json'), 'w'), indent=1); print(json.dumps(meta))


if __name__ == '__main__':
    main()
