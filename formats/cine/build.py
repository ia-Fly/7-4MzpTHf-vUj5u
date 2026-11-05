"""Monteur du format CINE : assemble un épisode à partir de fichiers générés par ElevenLabs.
    python3 formats/cine/build.py EPISODE.json ASSETS_DIR OUT_DIR [--preview 1,8,15] [--audio-only]
Sortie : OUT_DIR/video.mp4 (1080×1920, 30 i/s, -14 LUFS), cover.jpg, timeline.json.
Voir formats/cine/README.md pour le format du fichier EPISODE.json."""
import argparse, difflib, json, math, os, re, subprocess, sys
import numpy as np, cv2, soundfile as sf, pyloudnorm as pyln
from PIL import Image, ImageDraw
from scipy.ndimage import maximum_filter1d
from scipy.signal import butter, sosfilt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui

W, H, FPS, SR = ui.W, ui.H, 30, 48000


# ---------- temps ----------
def norm(w): return re.sub(r'[^a-z0-9]', '', w.lower())


def load_words(path):
    """Accepte la sortie Scribe du connecteur : [{text|word, start, end}] ou {words:[...]} ; ignore les espaces."""
    raw = json.load(open(path)); raw = raw.get('words', raw) if isinstance(raw, dict) else raw
    out = []
    for w in raw:
        txt = (w.get('text') if 'text' in w else w.get('word', '')).strip()
        if w.get('type', 'word') != 'word' or not txt or txt.startswith('[') or txt.endswith(']'): continue
        out.append(dict(w=txt, s=float(w['start']), e=float(w['end'])))
    return out


def align(lines, words):
    """Retrouve chaque réplique dans la prise : renvoie {id: (début, fin, [(mot affiché, début, fin)])}."""
    tok = []
    for ln in lines:
        for i, w in enumerate(ln['text'].split()): tok.append((ln['id'], i, w))
    a = [norm(t[2]) for t in tok]; b = [norm(w['w']) for w in words]
    m = {}
    for block in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(block.size): m[block.a + k] = block.b + k
    res = {}; pos = 0
    for ln in lines:
        n = len(ln['text'].split()); idx = list(range(pos, pos + n)); pos += n; got = [m.get(i) for i in idx]
        known = [g for g in got if g is not None]
        if not known: raise SystemExit(f"réplique introuvable dans la transcription : {ln['id']} {ln['text']!r}")
        s0, e0 = words[known[0]]['s'], words[known[-1]]['e']; items = []
        for j, g in enumerate(got):
            if g is not None: items.append([words[g]['s'], words[g]['e']])
            else: items.append(None)
        for j in range(n):                                   # mot non reconnu : temps interpolés entre ses voisins
            if items[j] is None:
                prev = next((items[k][1] for k in range(j - 1, -1, -1) if items[k]), s0)
                nxt = next((items[k][0] for k in range(j + 1, n) if items[k]), e0)
                items[j] = [prev, max(prev + .05, nxt)]
        res[ln['id']] = (s0, e0, [(w, it[0], it[1]) for w, it in zip(ln['text'].split(), items)])
    return res


def segment_lines(track, lst, found, quiet_db=-32, edge_db=-36):
    """Découpe une prise en répliques sur le vrai signal. Les temps de la transcription servent seulement de repère : sur une voix générée,
    ils sont répartis au caractère et se trompent sur les chiffres (« 3:17 »). Chaque réplique va du silence le plus long avant elle au silence le plus long après.
    Donc : séparer les répliques par une vraie pause dans le texte envoyé à la voix ([pause], « ... »)."""
    hop = int(.01 * SR); mono = np.abs(track).max(axis=1); n = len(mono) // hop
    e = np.array([mono[i * hop:(i + 1) * hop].max() for i in range(n)]); peak = float(e.max()) + 1e-9; quiet = e < peak * db(quiet_db)
    cuts = [0.0]
    for i in range(len(lst) - 1):
        h = (found[lst[i]['id']][1] + found[lst[i + 1]['id']][0]) / 2; lo, hi = max(0, int((h - .8) * 100)), min(n, int((h + .8) * 100)); best = (0, 0); run = None
        for k in range(lo, hi + 1):
            if k < hi and quiet[k]:
                run = k if run is None else run
            elif run is not None:
                if k - run > best[1]: best = (run, k - run)
                run = None
        cuts.append((best[0] + best[1] / 2) / 100 if best[1] >= 4 else h)
    cuts.append(n / 100); out = {}
    for i, ln in enumerate(lst):
        k0, k1 = int(cuts[i] * 100), int(cuts[i + 1] * 100); on = e[k0:k1] > peak * db(edge_db)
        if not on.any(): raise SystemExit(f"réplique muette dans la prise : {ln['id']}")
        s1 = (k0 + int(np.argmax(on))) / 100; e1 = (k0 + len(on) - int(np.argmax(on[::-1]))) / 100
        ws = ln['text'].split(); weights = [max(2, sum(4 if c.isdigit() else 1 for c in w if c.isalnum())) + 1 for w in ws]; tot = sum(weights); t = s1; wd = []
        for w, g in zip(ws, weights):                # temps des mots au prorata des lettres, chiffres comptés pour leur longueur parlée
            d = (e1 - s1) * g / tot; wd.append((w, t, t + d)); t += d
        out[ln['id']] = (s1, e1, wd)
    return out


class Timeline:
    def __init__(self, ep, assets):
        self.ep = ep; self.lines = {}; t = float(ep.get('lead', 0.0)); by_voice = {}
        for ln in ep['lines']: by_voice.setdefault(ln['voice'], []).append(ln)
        self.src = {}; self.tracks = {}
        for v, lst in by_voice.items():
            self.tracks[v] = decode(os.path.join(assets, ep['voices'][v]['file']))
            found = align(lst, load_words(os.path.join(assets, ep['voices'][v]['words'])))
            self.src.update(segment_lines(self.tracks[v], lst, found))
        for ln in ep['lines']:
            s0, e0, wd = self.src[ln['id']]; start = t + float(ln.get('pre', 0)); a0 = max(0.0, s0 - .015); b0 = e0 + .06
            off = start - a0; d = b0 - a0
            self.lines[ln['id']] = dict(ln, t0=start, t1=start + d, s0=a0, s1=b0, words=[(w, a + off, b + off) for w, a, b in wd])
            t = start + d + float(ln.get('gap', .12))
        self.voice_end = t; self.shots = {}; cur = 0.0
        for i, sh in enumerate(ep['shots']):
            sh['t0'] = 0.0 if i == 0 else self.T(sh['start']); self.shots[sh['id']] = sh
        self.total = max(self.T(ep['shots'][-1]['start']) + float(ep['shots'][-1].get('hold', 3.5)), self.voice_end)
        for i, sh in enumerate(ep['shots']): sh['t1'] = ep['shots'][i + 1]['t0'] if i + 1 < len(ep['shots']) else self.total

    def T(self, ref):
        """Résout une référence de temps : 12.5, "L3", "L3.end", "L3+0.4", "S2", "total"."""
        if isinstance(ref, (int, float)): return float(ref)
        m = re.fullmatch(r'([A-Za-z0-9_-]+?)(\.end)?([+-][0-9.]+)?', ref)
        if not m: raise SystemExit(f'référence de temps invalide : {ref}')
        name, end, d = m.groups(); d = float(d or 0)
        if name == 'total': return self.total + d
        if name in self.lines: return (self.lines[name]['t1'] if end else self.lines[name]['t0']) + d
        if name in self.shots: return (self.shots[name].get('t1', 0) if end else self.shots[name]['t0']) + d
        raise SystemExit(f'référence inconnue : {ref}')


# ---------- son ----------
def decode(path):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).reshape(-1, 2).copy()


def db(x): return 10 ** (x / 20)


def bandpass(x, lo=None, hi=None):
    if lo: x = sosfilt(butter(2, lo, 'hp', fs=SR, output='sos'), x, axis=0)
    if hi: x = sosfilt(butter(2, hi, 'lp', fs=SR, output='sos'), x, axis=0)
    return x


def rms(x): return float(np.sqrt(np.mean(np.square(x))) + 1e-9)


def envelope(x, att=.012, rel=.25):
    e = np.abs(x).max(axis=1); a, r = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR)); out = np.empty_like(e); c = 0.0
    for i in range(0, len(e), 64):
        v = float(e[i:i + 64].max()); k = (a if v > c else r) ** 64; c = k * c + (1 - k) * v; out[i:i + 64] = c
    return out


def limiter(x, th=.72, ceil=.89):
    env = maximum_filter1d(np.abs(x).max(1), size=int(.006 * SR))
    tgt = np.where(env > th, th + (ceil - th) * np.tanh((env - th) / (ceil - th)), env)
    g = np.where(env > 1e-9, tgt / np.maximum(env, 1e-9), 1.0); a = np.exp(-1 / (.06 * SR)); out = np.empty_like(g); cur = 1.0
    for i in range(0, len(g), 32):
        m = float(g[i:i + 32].min()); cur = m if m < cur else a ** 32 * cur + (1 - a ** 32) * m; out[i:i + 32] = cur
    return x * out[:, None]


def _loud(x, meter, target=-13.8):
    """Normalise sans passer par pyloudnorm.normalize : mêmes calculs, sans l'avertissement d'écrêtage (le limiteur suit)."""
    return x * db(target - meter.integrated_loudness(x))


def place(bus, clip, t, gain=1.0):
    i = int(t * SR)
    if i < 0: clip = clip[-i:]; i = 0
    n = min(len(clip), len(bus) - i)
    if n > 0: bus[i:i + n] += clip[:n] * gain


def fades(c, a=.005, b=.012):
    c = c.copy(); na, nb = min(int(a * SR), len(c)), min(int(b * SR), len(c))
    if na: c[:na] *= np.linspace(0, 1, na)[:, None]
    if nb: c[-nb:] *= np.linspace(1, 0, nb)[:, None]
    return c


def mix(ep, tl, assets, out_wav):
    n = int((tl.total + .05) * SR); voice = np.zeros((n, 2), np.float32); phone = np.zeros((n, 2), np.float32); beds = np.zeros((n, 2), np.float32); fx = np.zeros((n, 2), np.float32)
    tracks = tl.tracks
    target = ep.get('voice_rms_db', -19.0); phone_env = {}
    for ln in ep['lines']:
        L = tl.lines[ln['id']]; c = tracks[ln['voice']][int(L['s0'] * SR):int(L['s1'] * SR)]; c = fades(bandpass(c, lo=70).astype(np.float32))
        g = np.clip(target - 20 * math.log10(rms(c)), -6, 30) + float(ln.get('gain_db', 0)); place(voice, c, L['t0'], db(g))
        if ep['voices'][ln['voice']].get('phone'): place(phone, c, L['t0'], db(g))
    for s in ep.get('sfx', []):
        c = decode(os.path.join(assets, s['file'])); t0 = tl.T(s['at'])
        c = c * (db(-20) / rms(c)) if s.get('bed') else c * (.7 / max(float(np.abs(c).max()), 1e-6))
        if 'until' in s:
            dur = tl.T(s['until']) - t0; k = int(dur * SR); c = np.tile(c, (k // len(c) + 1, 1))[:k]
        if 'trim' in s: c = c[:int(float(s['trim']) * SR)]
        c = fades(c, float(s.get('fade_in', .004)), float(s.get('fade_out', .03)))
        if s.get('lo') or s.get('hi'): c = bandpass(c, s.get('lo'), s.get('hi')).astype(np.float32)
        place(beds if s.get('bed') else fx, c, t0, db(float(s.get('gain_db', -12))))
    if ep.get('music'):
        m = ep['music']; c = decode(os.path.join(assets, m['file'])); t0 = tl.T(m.get('at', 0)); ofs = int(float(m.get('offset', 0)) * SR); c = c[ofs:]; c = c * (db(-20) / rms(c))
        k = int((tl.total - t0) * SR)
        if len(c) < k: c = np.tile(c, (k // len(c) + 1, 1))
        c = fades(c[:k], .4, float(m.get('fade_out', 1.2))); place(beds, c, t0, db(float(m.get('gain_db', -18))))
    env = envelope(voice); env = env / max(env.max(), 1e-6); duck = db(-float(ep.get('duck_db', 7)) * np.clip(env * 3, 0, 1))
    x = voice + beds * duck[:, None] + fx
    on = envelope(voice) > .02; bal = dict(voice_db=round(20 * math.log10(rms(voice[on]) + 1e-9), 1), beds_under_voice_db=round(20 * math.log10(rms((beds * duck[:, None])[on]) + 1e-9), 1), fx_peak_db=round(20 * math.log10(float(np.abs(fx).max()) + 1e-9), 1))
    meter = pyln.Meter(SR)
    for _ in range(3):
        x = limiter(_loud(x, meter))
        if meter.integrated_loudness(x) > -14.2: break
    x = np.clip(x, -.89, .89); sf.write(out_wav, x.astype(np.float32), SR, subtype='FLOAT')
    return dict(lufs=round(meter.integrated_loudness(x), 2), peak=round(float(np.abs(x).max()), 3), **bal), phone


def line_env(voice, t, n=34):
    """Niveaux récents de la voix pour dessiner une onde réactive."""
    i = int(t * SR); span = int(.012 * SR); out = []
    for k in range(n):
        j = i - (n - k) * span; seg = voice[max(0, j):max(0, j) + span]
        out.append(rms(seg) if len(seg) else 0)
    v = np.array(out); return np.clip(v * 7, .03, 1.0)


# ---------- image ----------
def make_grade(strength=1.0):
    """Courbe filmique : noirs légèrement relevés et teintés, hautes lumières compressées, saturation retenue."""
    x = np.arange(256, dtype=np.float32) / 255
    s = x + .10 * strength * np.sin(2 * np.pi * x) * -.5                      # contraste doux
    s = np.clip(s ** 1.04, 0, 1); s = 1 - (1 - s) * (1 - .018 * strength)     # noirs jamais à zéro
    s = np.minimum(s, .90 + .10 * np.tanh((s - .90) / .10))                   # épaule des hautes lumières
    b = np.clip(s + .012 * strength * (1 - x) ** 3, 0, 1); g = np.clip(s + .004 * strength * (1 - x) ** 3, 0, 1); r = np.clip(s - .004 * strength * (1 - x) ** 3, 0, 1)
    return np.stack([b, g, r], axis=1).reshape(256, 1, 3) * 255


LUT = np.uint8(make_grade())
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d2 = ((xx - W / 2) / (W * .72)) ** 2 + ((yy - H / 2) / (H * .74)) ** 2
VIGN = np.clip(1 - .55 * np.clip(d2 - .28, 0, 1) ** 1.2, 0, 1)[:, :, None].astype(np.float32)
RNG = np.random.default_rng(7)
GRAIN = [np.int16(cv2.GaussianBlur(RNG.normal(0, 8.5, (H // 2, W // 2)).astype(np.float32), (0, 0), .6)) for _ in range(8)]
GRAIN = [cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[:, :, None] for g in GRAIN]


def finish(frame, i, grain=1.0, grade=True):
    if grade:
        frame = cv2.LUT(frame, LUT)
        lum = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)[:, :, None].astype(np.float32); frame = np.clip(lum + (frame.astype(np.float32) - lum) * .9, 0, 255) * VIGN
    else:
        frame = frame.astype(np.float32) * VIGN
    if grain > 0: frame = frame + GRAIN[(i * 5) % 8] * grain * .75
    return np.clip(frame, 0, 255).astype(np.uint8)


def handheld(t, amp=1.0):
    return (amp * (math.sin(t * 1.3) * 3.2 + math.sin(t * 2.9 + 1) * 1.6), amp * (math.sin(t * 1.1 + 2) * 3.6 + math.sin(t * 3.7) * 1.2), amp * .0009 * math.sin(t * .9 + .5))


def warp(img, zoom, cx, cy, dx=0, dy=0, rot=0):
    """Cadre 1080×1920 dans une image plus grande : zoom relatif au cadrage couvrant, centre en fraction."""
    h, w = img.shape[:2]; base = max(W / w, H / h); z = base * zoom
    a = math.cos(rot) * z; b = math.sin(rot) * z; tx = W / 2 + dx - (a * cx * w - b * cy * h); ty = H / 2 + dy - (b * cx * w + a * cy * h)
    M = np.float32([[a, -b, tx], [b, a, ty]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA if z < .7 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


MOVES = {'push_in': lambda p: (1.03 + .10 * p, .5, .5), 'pull_out': lambda p: (1.13 - .10 * p, .5, .5), 'drift_up': lambda p: (1.10, .5, .53 - .06 * p),
         'drift_down': lambda p: (1.10, .5, .47 + .06 * p), 'drift_left': lambda p: (1.12, .54 - .08 * p, .5), 'drift_right': lambda p: (1.12, .46 + .08 * p, .5), 'still': lambda p: (1.04, .5, .5)}


class Clip:
    """Plan vidéo généré : lecture en flux, temps étiré si le plan est plus long que le clip (fondu entre images voisines)."""
    def __init__(self, path, offset=0.0, slot=None, shot_speed=None):
        self.cap = cv2.VideoCapture(path); self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 24; n = self.cap.get(cv2.CAP_PROP_FRAME_COUNT); self.dur = n / self.fps
        avail = max(.1, self.dur - offset); self.speed = shot_speed or (min(1.0, avail / slot) if slot else 1.0); self.off = offset
        self.idx = -1; self.a = None; self.b = None

    def _read(self):
        ok, f = self.cap.read()
        if ok: self.b = f; self.idx += 1
        return ok

    def at(self, t):
        pos = (self.off + t * self.speed) * self.fps; i0 = int(pos); fr = pos - i0
        while self.idx < i0 + 1:
            self.a = self.b
            if not self._read(): break
        if self.a is None: self.a = self.b
        if self.a is None: raise SystemExit('clip illisible')
        return cv2.addWeighted(self.a, 1 - fr, self.b, fr, 0) if fr > .05 and self.b is not None and self.speed < .98 else self.a


def glue_screen(src, spec, t):
    """Colle l'écran d'appel sur le téléphone réel du plan, avant le recadrage. quad = coins (haut-gauche, haut-droit, bas-droit, bas-gauche) en fractions de l'image ;
    avec refine, les coins sont recalés à chaque image sur la zone lumineuse de l'écran (le téléphone peut bouger un peu)."""
    h, w = src.shape[:2]; q = (np.float32(spec['quad']) * [w, h]).astype(np.float32)
    if spec.get('refine', True):
        x0, y0 = (q.min(0) - [w * .05, h * .03]).astype(int).clip(0); x1, y1 = q.max(0) + [w * .05, h * .03]; roi = src[y0:int(y1), x0:int(x1)]
        g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY); th = cv2.morphologyEx(cv2.threshold(g, 150, 255, cv2.THRESH_BINARY)[1], cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        cs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cs:
            c = max(cs, key=cv2.contourArea); pts = c.reshape(-1, 2).astype(np.float32) + [x0, y0]
            for i in range(4):
                d = ((pts - q[i]) ** 2).sum(1); near = pts[np.argsort(d)[:max(3, len(pts) // 40)]]; cand = near.mean(0)
                if np.linalg.norm(cand - q[i]) < w * .05: q[i] = cand
    ink = spec.get('_ink')
    if ink is None:
        ink = spec['_ink'] = ui.screen_ink(600, 1240, spec['name'], spec.get('label', 'Incoming call'), spec.get('number', ''))
    sh, sw = ink.shape[:2]; M = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), q.astype(np.float32))
    wr = cv2.warpPerspective(ink, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    return ui.over(src, wr)


def caption_groups(ep, tl):
    groups = []
    for ln in ep['lines']:
        L = tl.lines[ln['id']]; ws = L['words']; keys = tuple(k.upper() for k in ln.get('keywords', [])); phone = ep['voices'][ln['voice']].get('phone', False)
        i = 0; chunks = ln.get('chunks')
        if chunks:
            sizes = chunks
        else:
            sizes = []; cur = 0
            for k, (w, a, b) in enumerate(ws):
                cur += 1; next_gap = ws[k + 1][1] - b if k + 1 < len(ws) else 0
                if cur == 3 or re.search(r'[.?!,…]$', w) or next_gap > .28 or k + 1 == len(ws): sizes.append(cur); cur = 0
        for s in sizes:
            part = ws[i:i + s]; i += s
            groups.append(dict(words=[p[0].upper() for p in part], times=[(p[1], p[2]) for p in part], t0=part[0][1], t1=part[-1][2], keys=keys, phone=phone))
    for a, b in zip(groups, groups[1:]): a['t1'] = max(a['t1'], min(b['t0'], a['t1'] + .55))
    groups[-1]['t1'] += .3
    return groups


def render(ep, tl, assets, out_mp4, voice, preview=None):
    groups = caption_groups(ep, tl); hud = ep.get('hud', {}); clocks = [(tl.T(r), v) for r, v in hud.get('clock', [])]
    nframes = int(round(tl.total * FPS)); cap_cache = {}; hud_cache = {}; shots = ep['shots']; cur = None; clip = None; img = None; bg_cache = {}
    impacts = [dict(t=tl.T(e['at']), kind=e.get('kind', 'shake'), amp=float(e.get('amp', 1))) for e in ep.get('impacts', [])]
    proc = None
    if preview is None:
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                 '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_mp4], stdin=subprocess.PIPE)
    wanted = None if preview is None else {int(p * FPS) for p in preview}; previews = []
    last_plain = np.zeros((H, W, 3), np.uint8)
    for fi in range(nframes):
        if wanted is not None and fi not in wanted and not any(s['kind'] == 'video' for s in shots): continue
        t = fi / FPS
        sh = next(s for s in reversed(shots) if s['t0'] <= t + 1e-6)
        if sh is not cur:
            cur = sh; clip = None; img = None; local0 = sh['t0']; slot = sh['t1'] - sh['t0']
            if sh['kind'] == 'video': clip = Clip(os.path.join(assets, sh['file']), float(sh.get('offset', 0)), slot, sh.get('speed'))
            if sh.get('file') and sh['kind'] in ('still', 'ui_on_still'): img = cv2.imread(os.path.join(assets, sh['file']))
        lt = t - sh['t0']; p = lt / max(1e-3, sh['t1'] - sh['t0'])
        if wanted is not None and fi not in wanted:
            if clip is not None: clip.at(lt)
            continue
        dx, dy, rot = handheld(t, float(sh.get('shake', 1)))
        punch = 0.0
        for e in impacts:
            age = t - e['t']
            if 0 <= age < .5:
                k = math.exp(-age * 9) * e['amp']
                if e['kind'] == 'shake': dx += math.sin(age * 90) * 22 * k; dy += math.cos(age * 77) * 18 * k
                if e['kind'] == 'punch': punch = max(punch, .05 * k)
        kind = sh['kind']; grade = True; grain = float(sh.get('grain', 1))
        if kind == 'video':
            src = clip.at(lt)
            if sh.get('screen'): src = glue_screen(src.copy(), sh['screen'], t)
            z0, z1 = sh.get('zoom', [1.02, 1.06]); frame = warp(src, z0 + (z1 - z0) * p + punch, *sh.get('center', [.5, .5]), dx, dy, rot)
        elif kind == 'still':
            if sh.get('screen') and not sh.get('_glued'): img = glue_screen(img, sh['screen'], t); sh['_glued'] = True
            if sh.get('zoom'): z = sh['zoom'][0] + (sh['zoom'][1] - sh['zoom'][0]) * p; cx, cy = sh.get('center', [.5, .5])
            else: z, cx, cy = MOVES[sh.get('move', 'push_in')](p)
            frame = warp(img, z + punch, cx, cy, dx, dy, rot)
        elif kind == 'ui_on_still':
            z, cx, cy = MOVES[sh.get('move', 'still')](p); frame = warp(img, z + punch, cx, cy, dx, dy, rot)
        elif kind == 'phone':
            key = sh.get('bg')
            if key not in bg_cache:
                b = cv2.imread(os.path.join(assets, key)) if key else np.zeros((H, W, 3), np.uint8)
                b = cv2.resize(b, (W, H), interpolation=cv2.INTER_AREA) if key else b; bg_cache[key] = (cv2.GaussianBlur(b, (0, 0), 28).astype(np.float32) * .35).astype(np.uint8)
            P = sh['ui']; ring = (lt * .85) % 1; sw, sh_ = 860, 1740
            if P['type'] == 'incoming':
                photo = cv2.imread(os.path.join(assets, P['photo'])) if P.get('photo') else None
                if photo is not None and 'crop' in P: x, y, w_, h_ = P['crop']; photo = photo[y:y + h_, x:x + w_]
                scr = ui.screen_incoming(sw, sh_, P['name'], P.get('number', ''), P.get('label', 'Incoming call'), photo, ring)
            else:
                env = line_env(voice, t) if P['type'] == 'active' else None
                scr = ui.screen_active(sw, sh_, P['name'], float(P.get('elapsed', 0)) + lt, env, ended=P['type'] == 'ended')
            b = 1.0 if P['type'] != 'ended' else max(.25, 1 - p * .75)
            frame = ui.phone_on(bg_cache[key], scr, t=t, vibrate=float(P.get('vibrate', 0)), tilt=.012, scale=.97 + .03 * p + punch, brightness=b)
            frame = np.roll(frame, (int(dy * .4), int(dx * .4)), axis=(0, 1)); grain = .55
        elif kind == 'led':
            seq = [(float(a), v) for a, v in sh['seq']]; txt = next(v for a, v in reversed(seq) if a <= lt + 1e-6)
            ck = 'led' + txt
            if ck not in bg_cache: bg_cache[ck] = ui.led_clock(txt)
            frame = warp(bg_cache[ck], 1.02 + .05 * p + punch, .5, .5, dx * .5, dy * .5, rot); grade = False; grain = .8
        elif kind == 'end':
            frame = ui.end_card(last_plain, sh['a'], sh['b'], sh.get('question', 'WHAT DO YOU DO?'), sh['cta1'], sh['cta2'], lt); grade = False; grain = .5
        else:
            raise SystemExit(f'type de plan inconnu : {kind}')
        if kind != 'end': last_plain = cv2.GaussianBlur(frame, (0, 0), 12)
        frame = finish(frame, fi, grain, grade)
        fade = float(sh.get('fade_in', 0))
        if fade and lt < fade: frame = (frame.astype(np.float32) * (lt / fade)).astype(np.uint8)
        for e in impacts:
            age = t - e['t']
            if e['kind'] == 'flash' and 0 <= age < .16:
                a = (1 - age / .16) * .55 * e['amp']; frame = np.clip(frame.astype(np.float32) + 255 * a, 0, 255).astype(np.uint8)
        # bandeau
        if hud and kind != 'end':
            clock = next((v for a, v in reversed(clocks) if a <= t + 1e-6), '')
            phone_now = any(g['phone'] and g['t0'] - .05 <= t <= g['t1'] for g in groups); blink = (t % 1.0) < .55
            k = (hud.get('left', ''), clock, blink, phone_now)
            if k not in hud_cache: hud_cache[k] = ui.hud_layer(hud.get('left', ''), clock, blink, phone_now)
            ui.over(frame, hud_cache[k], 0, int(H * .098))
        # sous-titres + onde de la voix au téléphone
        if kind != 'end':
            g = next((g for g in groups if g['t0'] - .03 <= t < g['t1']), None)
            if g:
                act = max(0, sum(1 for a, b in g['times'] if a <= t + .02) - 1); key = (id(g), act)
                if key not in cap_cache: cap_cache[key] = ui.caption_layer(g['words'], act, g['keys'], ui.ICE if g['phone'] else ui.SIGNAL)
                c = cap_cache[key]; age = t - g['t0']; ui.over(frame, c, (W - c.shape[1]) // 2, int(H * .635) - (c.shape[0] // 2) + int(max(0, .08 - age) * 60))
                if g['phone'] and kind != 'phone':
                    w_ = ui.wave_layer(line_env(voice, t, 26)); ui.over(frame, w_, (W - w_.shape[1]) // 2, int(H * .635) - c.shape[0] // 2 - w_.shape[0] - 8)
        if proc is not None: proc.stdin.write(frame.tobytes())
        else: previews.append((fi, frame))
    if proc is not None:
        proc.stdin.close(); proc.wait()
        if proc.returncode: raise SystemExit('ffmpeg a échoué')
    return previews


def make_cover(ep, assets, out):
    c = ep['cover']; img = cv2.imread(os.path.join(assets, c['file']))
    if img is None: img = np.zeros((H, W, 3), np.uint8)
    if c.get('screen'): img = glue_screen(img, c['screen'], 0)
    frame = warp(img, float(c.get('zoom', 1.05)), *c.get('center', [.5, .5])); frame = finish(frame, 0, .7, True)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = int(c.get('y', 1060))
    size = 190; f = ui.anton(size)
    while d.textbbox((0, 0), c['title'], font=f)[2] > W - 170 and size > 90: size -= 6; f = ui.anton(size)
    ui.centered(d, W / 2, y, c['title'], f, (255, 255, 255, 255)); y2 = y + int(size * 1.32)
    d.rectangle([W / 2 - 70, y2, W / 2 + 70, y2 + 7], fill=ui.SIGNAL + (255,))
    ui.centered(d, W / 2, y2 + 30, c['episode'], ui.condensed(84), (255, 255, 255, 255))
    if c.get('subtitle'): ui.centered(d, W / 2, y2 + 124, c['subtitle'], ui.condensed(64), ui.SIGNAL + (255,))
    ui.over(frame, ui.to_bgra(im)); cv2.imwrite(out, frame, [cv2.IMWRITE_JPEG_QUALITY, 93])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('episode'); ap.add_argument('assets'); ap.add_argument('out'); ap.add_argument('--preview'); ap.add_argument('--audio-only', action='store_true')
    a = ap.parse_args(); ep = json.load(open(a.episode)); os.makedirs(a.out, exist_ok=True); tl = Timeline(ep, a.assets)
    wav = os.path.join(a.out, 'mix.wav'); stats, voice = mix(ep, tl, a.assets, wav)
    report = dict(total=round(tl.total, 2), audio=stats, lines={k: [round(v['t0'], 2), round(v['t1'], 2)] for k, v in tl.lines.items()},
                  shots=[dict(id=s['id'], kind=s['kind'], t0=round(s['t0'], 2), t1=round(s['t1'], 2)) for s in ep['shots']])
    json.dump(report, open(os.path.join(a.out, 'timeline.json'), 'w'), indent=1); print(json.dumps(report))
    if a.audio_only: return
    if a.preview:
        pts = [float(x) for x in a.preview.split(',')]; frames = render(ep, tl, a.assets, None, voice, pts)
        sheet = np.zeros((960, 540 * len(frames), 3), np.uint8)
        for i, (_, f) in enumerate(frames): sheet[:, i * 540:(i + 1) * 540] = cv2.resize(f, (540, 960), interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(a.out, 'preview.jpg'), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88]); print('aperçu :', os.path.join(a.out, 'preview.jpg')); return
    raw = os.path.join(a.out, 'video_raw.mp4'); render(ep, tl, a.assets, raw, voice)
    out = os.path.join(a.out, 'video.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
    os.remove(raw)
    if ep.get('cover'): make_cover(ep, a.assets, os.path.join(a.out, 'cover.jpg'))
    print('vidéo :', out)


if __name__ == '__main__':
    main()
