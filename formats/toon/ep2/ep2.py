"""FROMAGISTAN · Épisode 2 — montage du nouveau format (images et plans ElevenLabs + interface et bulles de nom en code).
    python3 ep2.py ASSETS OUT [--preview t1,t2,...]"""
import json, math, os, subprocess, sys
import numpy as np, cv2, soundfile as sf, pyloudnorm as pyln
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 48000
A = sys.argv[1]; O = sys.argv[2]; os.makedirs(O, exist_ok=True)
FONTS = '/home/claude/studio/assets/fonts/'
GOLD, GOLD2, VIO, RED, BORD = (255, 196, 0), (255, 224, 102), (122, 63, 209), (255, 42, 42), (110, 10, 20)


def font(sz, f='Montserrat-Black.ttf'): return ImageFont.truetype(FONTS + f, sz)


def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)


def pop(t, t0, d=.28):
    x = (t - t0) / d
    return 0 if x < 0 else (1 + .16 * math.sin(min(1, x) * math.pi) if x < 1 else 1)


# ---------------------------------------------------------------- son
TEMPO = 1.0                                        # rythme naturel (retour de Matis : la v1 était trop rapide)


def load(name):
    p = os.path.join(A, name); sp = name.startswith('voice_'); w = p.rsplit('.', 1)[0] + ('.48k.t%.2f.wav' % TEMPO if sp else '.48k.wav')
    if not os.path.exists(w): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p] + (['-af', f'atempo={TEMPO}'] if sp else []) + ['-ar', str(SR), '-ac', '1', w], check=True)
    x, _ = sf.read(w); return x.astype(np.float32)


def trim(x, thr_db=-38):
    hop = 480; e = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)]); on = np.where(e > e.max() * 10 ** (thr_db / 20))[0]
    a, b = max(0, on[0] * hop - 1200), min(len(x), (on[-1] + 1) * hop + 2400); return x[a:b], a / SR


words = json.load(open(os.path.join(A, 'words_b.json'))); words = words.get('words', words) if isinstance(words, dict) else words
segs, cur = [], []
for w in words:
    if w['text'] == '[pause]': segs.append(cur); cur = []; continue
    if w['text'].startswith('['): continue
    cur.append(dict(w, start=w['start'] / TEMPO, end=w['end'] / TEMPO))
segs.append(cur)
vb = load('voice_b.mp3'); vr = load('voice_r.mp3'); vd = load('voice_d.mp3')
bounds = [0.0] + [(segs[i][-1]['end'] + segs[i + 1][0]['start']) / 2 for i in range(len(segs) - 1)] + [len(vb) / SR]
BIDS = ['B%d' % (i + 1) for i in range(15)]
clips = {}
for i, bid in enumerate(BIDS):
    a, b = int(bounds[i] * SR), int(bounds[i + 1] * SR); x, off = trim(vb[a:b]); ws = [(w['text'], w['start'] - bounds[i] - off, w['end'] - bounds[i] - off) for w in segs[i]]
    clips[bid] = (x, ws)
rw = json.load(open(os.path.join(A, 'words_r.json'))) if os.path.exists(os.path.join(A, 'words_r.json')) else None
RW = [('Président.', .08, .92), ('Je', 1.12, 1.28), ('signe', 1.36, 1.6), ('votre', 1.68, 1.84), ('accord,', 1.92, 2.48), ('beurre', 2.64, 2.88), ('contre', 3.0, 3.12), ('fromage...', 3.2, 3.96),
      ('à', 4.16, 4.32), ('une', 4.4, 4.56), ('condition.', 4.84, 5.2), ('Que', 6.32, 6.4), ('vos', 6.48, 6.56), ('citoyens', 6.68, 7.12), ('likent', 7.28, 7.6), ('et', 7.64, 7.68), ('republient', 7.76, 8.24),
      ('cette', 8.29, 8.4), ('vidéo.', 8.52, 9.2), ('Sinon,', 9.32, 9.84), ('je', 9.92, 10.0), ('repars.', 10.12, 10.72)]
DW = [('Fromagistan', .37, 1.04), ('!', 1.36, 1.4), ('Je', 1.44, 1.52), ('vais', 1.64, 1.76), ('saboter', 1.8, 2.24), ('ton', 2.32, 2.4), ('Grand', 2.48, 2.56), ('Prix...', 2.64, 3.04), ('et', 3.2, 3.28),
      ('te', 3.36, 3.52), ('voler', 3.6, 3.84), ('ta', 3.92, 4.08), ('reine', 4.16, 4.48), ('!', 4.72, 4.79), ('MOUAHAHA…', 5.84, 6.88), ('…HA.', 7.76, 8.24)]
RW = [(a, s / TEMPO, e / TEMPO) for a, s, e in RW]; DW = [(a, s / TEMPO, e / TEMPO) for a, s, e in DW]; C5 = 5.6 / TEMPO; cut = int(C5 * SR); x1, o1 = trim(vr[:cut]); x2, o2 = trim(vr[cut:])
clips['R1'] = (x1, [(a, s - o1, e - o1) for a, s, e in RW if s < C5]); clips['R2'] = (x2, [(a, s - C5 - o2, e - C5 - o2) for a, s, e in RW if s >= C5])
xd, od = trim(vd); clips['D'] = (xd, [(a, s - od, e - od) for a, s, e in DW])


def split_clip(fname, a, b, text):
    """réplique tirée d'une prise (de a à b s), mots répartis au prorata des lettres"""
    x = load(fname); seg = x[int(a * SR): int(b * SR) if b else len(x)]; y, off = trim(seg); ws = text.split(); Lc = len(y) / SR
    g = [max(2, len(w)) for w in ws]; tot = sum(g); t0 = .05; out = []
    for w, k in zip(ws, g): d = (Lc - .1) * k / tot; out.append((w, t0, t0 + d)); t0 += d
    return (y, out)


clips['P1a'] = split_clip('voice_p.mp3', 0, 5.4, "Je vous présente Esteban, notre comptable royal ! Il nous l'a demandé en commentaire.")
clips['P1b'] = split_clip('voice_p.mp3', 5.4, None, "Son travail : garder les écus que vous gagnez avec vos likes, et compter chaque pièce... deux fois.")
clips['C1'] = split_clip('voice_c.mp3', 0, 2.6, "Trente pour cent. J'ai compté deux fois.")
clips['C2'] = split_clip('voice_c.mp3', 2.6, None, "Président... il manque trois meules dans la réserve royale.")
clips['K1'] = split_clip('voice_k.mp3', 0, None, "Un fromage sans origine, c'est un fromage suspect !")
clips['DOC'] = split_clip('voice_doc.mp3', 0, None, "Le cabinet est ouvert ! Premier patient... le président, et sa barbe brûlée.")
clips['CAP'] = split_clip('voice_cap.mp3', 0, None, "Garde montée, en position ! Personne n'entre au château sans mon accord.")
clips['N1'] = split_clip('voice_n.mp3', 0, 5.5, "Mais pendant la fête, personne n'a remarqué... ce qui se cachait sous le carrosse.")
clips['N2'] = split_clip('voice_n.mp3', 5.5, 11.3, "Et ce soir, dans la cave du palais... la porte fermée à clé a frappé trois coups.")
clips['N3'] = split_clip('voice_n.mp3', 11.3, None, "Qui vole nos meules ? Qui frappe dans la cave ? Réponse... au prochain épisode.")
clips['D2'] = split_clip('voice_d2.mp3', 0, None, "Et mon espion... est déjà dans ton château. Hé hé.")
clips['SA'] = split_clip('voice_s.mp3', 0, 1.7, "Le bilan du royaume !")
clips['SB'] = split_clip('voice_s.mp3', 1.7, 5.0, "Cent cinquante-cinq likes : trois cent dix écus dans la caisse !")
clips['SC'] = split_clip('voice_s.mp3', 5.0, 9.0, "Vingt et un commentaires, cinq partages, six enregistrements...")
clips['SD'] = split_clip('voice_s.mp3', 9.0, None, "et quarante-trois nouveaux citoyens ! Nous sommes cinquante-deux !")
clips['ES'] = split_clip('voice_s2.mp3', 0, None, "Trois cent dix écus. Rangés dans le coffre. Comptés deux fois.")
_x, _w = clips['B5']; _cut = [w for w in _w if w[0] == 'Vous'][0][1] - .06       # « Vous êtes vingt et un » retiré (le bilan donne le vrai chiffre)
_y = _x[:int(_cut * SR)].copy(); _y[-2400:] *= np.linspace(1, 0, 2400); clips['B5'] = (_y, [w for w in _w if w[1] < _cut])
STATS = dict(likes=155, ecus=310, comments=21, shares=5, pop=15, saves=6, magie=6, new=43, citizens=52)   # vrais chiffres ép. 1 (Instagram + TikTok, 15/11)
SPEAKER = dict(ES='LE COMPTABLE', R1='LA REINE', R2='LA REINE', D='DOUDOU DICTADOR', D2='DOUDOU DICTADOR', C1='LE COMPTABLE', C2='LE COMPTABLE', K1='KXPL', DOC='LE DOCTEUR', CAP='LE CAPITAINE')
ORDER = ['B1', 'P1a', 'SA', 'SB', 'SC', 'SD', 'ES', 'B3',   # v4 (Matis 15/11) : présentation éclair -> bilan -> toit ; P1b, B2, C1 retirés
         'B4', 'B5', 'B6', 'K1', 'B7', 'DOC', 'B8', 'CAP', 'B9', 'B10', 'B11', 'R1', 'R2', 'N1', 'B12', 'B13', 'D', 'D2', 'C2', 'N2', 'B14', 'B15', 'N3']
GAP = dict(SA=.25, SB=.4, SC=.4, SD=.5, ES=.45, B1=.3, P1a=.3, P1b=.5, B2=.4, C1=.7, B3=.7, B4=1.0, B5=1.4, B6=.4, K1=.7, B7=.4, DOC=.7, B8=.5, CAP=.9, B9=.8, B10=.9, B11=.7, R1=.45, R2=.9, N1=1.3,
           B12=.6, B13=.4, D=.4, D2=.9, C2=.9, N2=1.8, B14=.6, B15=.7, N3=2.2)
LEAD = .25
T = {}; t = LEAD
for k in ORDER: T[k] = t; t += len(clips[k][0]) / SR + GAP[k]
TOTAL = t
END = {k: T[k] + len(clips[k][0]) / SR for k in ORDER}


def wt(seg, word, n=1, which=0):
    """temps (timeline) du n-ième mot commençant par `word` dans la réplique seg"""
    c = 0
    for a, s, e in clips[seg][1]:
        if a.lower().strip('.,!:…').startswith(word.lower()):
            c += 1
            if c == n: return T[seg] + (s if which == 0 else e)
    raise KeyError(seg + ' ' + word)


# sous-titres : groupes de 3 mots au plus, K X P L -> KXPL
CAPS = []
for k in ORDER:
    ws = []; src = clips[k][1]; i = 0
    while i < len(src):
        a, s, e = src[i]
        if [x[0].rstrip(',') for x in src[i:i + 4]] == ['K', 'X', 'P', 'L']:
            ws.append(('KXPL' + (',' if src[i + 3][0].endswith(',') else ''), s, src[i + 3][2])); i += 4; continue
        if a in (':', '!', '?'):
            if ws: ws[-1] = (ws[-1][0] + ' ' + a, ws[-1][1], e)
            i += 1; continue
        ws.append((a, s, e)); i += 1
    grp = []
    for a, s, e in ws:
        grp.append((a, s, e))
        if len(grp) == 3 or a[-1] in '.!?:…,':
            CAPS.append((T[k] + grp[0][1] - .05, T[k] + grp[-1][2] + .05, ' '.join(g[0] for g in grp), k)); grp = []
    if grp: CAPS.append((T[k] + grp[0][1] - .05, T[k] + grp[-1][2] + .05, ' '.join(g[0] for g in grp), k))
for i in range(len(CAPS) - 1):                    # pas de trou entre deux groupes d'une même réplique
    if CAPS[i][3] == CAPS[i + 1][3]: CAPS[i] = (CAPS[i][0], CAPS[i + 1][0], CAPS[i][2], CAPS[i][3])


def mixdown(out):
    n = int(TOTAL * SR); voice = np.zeros(n, np.float32); mus = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
    for k in ORDER:
        x = clips[k][0]; a = int(T[k] * SR); voice[a:a + len(x)] += x[:n - a] * (1.15 if k in ('R1', 'R2') else 1.0)
    def put(buf, name, at, db, dur=None, fade=.35):
        x = load(name)
        if dur: x = x[:int(dur * SR)]
        f = int(fade * SR); x = x.copy(); x[-f:] *= np.linspace(1, 0, f)
        a = int(at * SR); m = min(len(x), n - a); buf[a:a + m] += x[:m] * 10 ** (db / 20)
    th = load('theme.mp3'); amb = np.concatenate([load('amb1.mp3'), load('amb2.mp3')]); sc = load('score.mp3')
    SECT = ((0, T['N1'] - .3, th, -17), (T['N1'] - .3, T['B12'] - .3, sc, -15), (T['B12'] - .3, T['C2'] - .3, amb, -14), (T['C2'] - .3, T['B14'] - .2, sc, -14),
            (T['B14'] - .2, T['N3'] - .2, th, -17), (T['N3'] - .2, TOTAL, sc, -14))
    for a0, a1, src, db in SECT:                        # sections qui se recouvrent de 0,8 s : fondu enchaîné, pas de trou
        a0 = max(0, a0 - .4); a1 = min(TOTAL, a1 + .4)
        i0, i1 = int(a0 * SR), int(a1 * SR); L = i1 - i0; loop = np.tile(src, L // len(src) + 1)[:L].copy(); f = int(.8 * SR)
        loop[:f] *= np.linspace(0, 1, f); loop[-f:] *= np.linspace(1, 0, f); mus[i0:i1] += loop * 10 ** (db / 20)
    S = [('coins.mp3', wt('B1', 'comptable'), -12, 1.5), ('spell-ok.mp3', wt('B3', 'On') + .2, -8, 1.8),
         ('spell-fail.mp3', wt('B4', 'Premier') + .7, -5, None), ('fail-horn.mp3', wt('B4', 'le') + .5, -14, 1.2), ('spell-fail.mp3', wt('B4', 'Deuxième') + .6, -5, None),
         ('fail-horn.mp3', wt('B4', 'pleut'), -14, 1.2), ('spell-ok.mp3', wt('B4', 'tient') - .1, -4, 2.0), ('cheer.mp3', T['B5'] + .2, -9, None), ('cheer.mp3', END['B5'] + .1, -9, None),
         ('coins.mp3', T['B6'] + 1.0, -12, 1.2), ('cheer.mp3', T['B7'] + 1.0, -11, None), ('horse.mp3', T['B8'] + .9, -7, 3.0), ('spell-ok.mp3', T['B9'] + .2, -12, 1.5),
         ('car.mp3', wt('B10', 'grille') - .2, -12, 3.5), ('fanfare.mp3', T['B11'] - .1, -9, 2.0), ('fanfare.mp3', END['B11'] - .2, -8, 2.0), ('coins.mp3', wt('R2', 'likent'), -12, 1.2),
         ('sting1.mp3', T['B12'] - .25, -4, None), ('fail-horn.mp3', wt('B13', 'Refusé') + .05, -12, 1.0), ('goat1.mp3', wt('B13', 'chèvre') + .45, -8, 1.6), ('sting2.mp3', T['D'] - .2, -6, None),
         ('spell-ok.mp3', T['B14'] + .1, -12, 1.5), ('coins.mp3', END['B15'] + .1, -10, 1.5),
         ('riser.mp3', T['N1'] - .3, -12, 4.0), ('boom.mp3', END['N1'] + .1, -9, 3.0),
         ('riser.mp3', T['C2'] - .2, -13, 3.5), ('boom.mp3', END['C2'] + .1, -10, 2.5), ('knock.mp3', END['N2'] + .15, -4, 2.2), ('boom.mp3', T['N3'] - .1, -10, 3.0),
         ('boom.mp3', END['N3'] + .3, -7, 3.0), ('coins.mp3', T['SB'] + .2, -11, 1.5), ('cheer.mp3', T['SD'] + .3, -10, None), ('coins.mp3', T['ES'] + .1, -12, 1.2)]
    # Matis 15/11 : « attention quand les bruitages se superposent, ça coupe certains moments »
    # -> un seul bruitage à la fois : s'il chevauche le précédent, on le décale (≤ 0,6 s) ou on l'abandonne ; les coups de la cave restent prioritaires
    S = sorted(S, key=lambda e: e[1]); keep = []; busy = -1.0
    for name, at, db, dur in S:
        ln = dur if dur else len(load(name)) / SR
        if name == 'knock.mp3': ln = KNOCKS[-1] + .25
        if at < busy - .05 and name != 'knock.mp3':
            if busy - at <= .6: at = busy + .05
            else: continue
        keep.append((name, at, db, dur)); busy = max(busy, at + ln)
    S = keep
    for name, at, db, dur in S:
        if name == 'knock.mp3':                       # 3 coups nets : un seul coup du fichier (1,60 à 1,80 s) répété sur KNOCKS
            kn = load('knock.mp3')[int(1.60 * SR):int(1.82 * SR)].copy(); kn[-480:] *= np.linspace(1, 0, 480)
            for kt in KNOCKS:
                i0 = int((at + kt) * SR); fx[i0:i0 + len(kn)] += kn * 10 ** (db / 20)
            continue
        put(fx, name, at, db, dur)
    env = np.abs(voice); k = int(.02 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); env = np.convolve((env > .02).astype(np.float32), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
    duck = 1 - .55 * np.clip(env, 0, 1); mix = voice + mus * duck + fx * (1 - .6 * np.clip(env, 0, 1))      # bruitages baissés sous la voix
    meter = pyln.Meter(SR)
    for _ in range(3):                                # loudness -14 LUFS puis limiteur doux (crête < -1 dBFS)
        mix = pyln.normalize.loudness(mix, meter.integrated_loudness(mix), -14.0); mix = np.tanh(mix * 1.1) / 1.1 * .89
    sf.write(out, np.stack([mix, mix], 1), SR)


# ---------------------------------------------------------------- images
IMG = {}


def img(name):
    if name not in IMG:
        x = cv2.imread(os.path.join(A, name + '.png'), cv2.IMREAD_COLOR).astype(np.float32) / 255
        h, w = x.shape[:2]; s = max(W / w, H / h); bg = cv2.resize(x, (int(w * s) + 1, int(h * s) + 1)); y0, x0 = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
        bg = cv2.GaussianBlur(bg[y0:y0 + H, x0:x0 + W], (0, 0), 28) * .45
        a = np.ones((h, w), np.float32); f = int(min(h, w) * .06); ramp = np.linspace(0, 1, f)
        a[:f] *= ramp[:, None]; a[-f:] *= ramp[::-1, None]; a[:, :f] *= ramp[None]; a[:, -f:] *= ramp[None, ::-1]
        IMG[name] = (x, a, bg)
    return IMG[name]


def view(name, sc, cx, cy, sx, sy):
    """image `name` mise à l'échelle sc (px écran par px source), le point source (cx, cy) normalisé posé en (sx, sy) écran ; flou de la même image autour."""
    x, a, bg = img(name); h, w = x.shape[:2]
    M = np.float32([[sc, 0, sx - cx * w * sc], [0, sc, sy - cy * h * sc]])
    fg = cv2.warpAffine(x, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT); al = cv2.warpAffine(a, M, (W, H), borderValue=0)[..., None]
    return fg * al + bg * (1 - al), (lambda ax, ay: (sx + (ax - cx) * w * sc, sy + (ay - cy) * h * sc))


VID = {}


def vid(name, u, speed=1.0):
    if name not in VID:
        cap = cv2.VideoCapture(os.path.join(A, name)); fr = []
        while True:
            ok, f = cap.read()
            if not ok: break
            fr.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC))   # uint8 : 4× moins de mémoire
        VID[name] = (fr, cap.get(cv2.CAP_PROP_FPS) or 24)
    fr, fps = VID[name]; i = int(u * speed * fps); return fr[min(max(i, 0), len(fr) - 1)].astype(np.float32) / 255


VIG = None


def vignette():
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2); VIG = np.clip(1.08 - .55 * d ** 2, .35, 1)[..., None].astype(np.float32)
    return VIG


# ---------------------------------------------------------------- interface (calque RGBA)
SPR = {}


def glow_sprite(r, col, core=(255, 250, 225)):
    key = ('g', r, col)
    if key not in SPR:
        s = int(r * 6); im = Image.new('RGBA', (s, s)); d = ImageDraw.Draw(im); c = s // 2
        d.ellipse([c - r * 1.6, c - r * 1.6, c + r * 1.6, c + r * 1.6], fill=col + (150,)); im = im.filter(ImageFilter.GaussianBlur(r * .9))
        d = ImageDraw.Draw(im); d.ellipse([c - r, c - r, c + r, c + r], fill=col + (255,)); d.ellipse([c - r * .62, c - r * .62, c + r * .62, c + r * .62], fill=core + (255,))
        d.ellipse([c - r * .55, c - r * .7, c - r * .1, c - r * .3], fill=(255, 255, 255, 230)); SPR[key] = im
    return SPR[key]


def spark_sprite(r, col):
    key = ('s', r, col)
    if key not in SPR:
        s = int(r * 8); im = Image.new('RGBA', (s, s)); d = ImageDraw.Draw(im); c = s / 2
        d.ellipse([c - r * 1.5, c - r * 1.5, c + r * 1.5, c + r * 1.5], fill=col + (120,)); im = im.filter(ImageFilter.GaussianBlur(r)); d = ImageDraw.Draw(im)
        d.polygon([(c, c - r * 3), (c + r * .35, c - r * .35), (c + r * 3, c), (c + r * .35, c + r * .35), (c, c + r * 3), (c - r * .35, c + r * .35), (c - r * 3, c), (c - r * .35, c - r * .35)], fill=(255, 250, 220, 255))
        SPR[key] = im
    return SPR[key]


def pill_sprite(text, camp):
    key = ('p', text, camp)
    if key not in SPR:
        f = font(34, 'Montserrat-ExtraBold.ttf'); bb = f.getbbox(text); tw, th = bb[2] - bb[0], bb[3] - bb[1]; pw, ph = tw + 44, 58
        edge, fill = (GOLD, (8, 6, 14, 175)) if camp == 'gold' else (RED, (80, 6, 14, 190))
        im = Image.new('RGBA', (pw + 40, ph + 40)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([20, 20, 20 + pw, 20 + ph], radius=ph // 2, outline=edge + (160,), width=8); im = im.filter(ImageFilter.GaussianBlur(5)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([20, 20, 20 + pw, 20 + ph], radius=ph // 2, fill=fill, outline=edge + (255,), width=3)
        d.text((20 + pw / 2, 20 + ph / 2 + 1), text, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=2, stroke_fill=edge if camp == 'gold' else (200, 20, 30))
        SPR[key] = im
    return SPR[key]


def paste(L, sp, x, y, k=1.0, alpha=1.0):
    if k <= 0.01 or alpha <= 0: return
    if k != 1: sp = sp.resize((max(1, int(sp.width * k)), max(1, int(sp.height * k))), Image.BILINEAR)
    if alpha < 1: sp = sp.copy(); sp.putalpha(sp.getchannel('A').point(lambda v: int(v * alpha)))
    L.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))


def bubble(L, t, t0, hx, hy, name, camp='gold', t1=None):
    """Bulle de nom : petite boule lumineuse + étincelles en orbite + pastille « @pseudo », posée au-dessus de la tête (hx, hy = haut de la tête)."""
    if t < t0 or (t1 is not None and t > t1): return
    k = pop(t, t0, .35); fl = 5 * math.sin((t - t0) * 2.6); pulse = 1 + .06 * math.sin((t - t0) * 5.0)
    col = GOLD if camp == 'gold' else RED
    sp = pill_sprite(name, camp); px = min(max(hx, sp.width / 2 + 10), 940 - sp.width / 2); oy = max(hy - 120, 230)
    py = oy + fl; paste(L, sp, px, py + 52, k)
    paste(L, glow_sprite(20, col, (255, 250, 225) if camp == 'gold' else (255, 200, 200)), px, py, k * pulse)
    for j in range(4):
        a = (t - t0) * 2.2 + j * math.pi / 2; paste(L, spark_sprite(3, col), px + 34 * math.cos(a), py + 14 * math.sin(a), k * (.7 + .3 * math.sin(a * 2)))
    if t - t0 < .5:                                   # « pop » d'étincelles à l'apparition
        q = (t - t0) / .5
        for j in range(8):
            a = j * math.pi / 4; paste(L, spark_sprite(4, col), px + 70 * q * math.cos(a), py + 70 * q * math.sin(a), 1, 1 - q)


def card(L, t, t0, x, y, text, camp='gold', size=58, sub=None, t1=None, w=None, subk=.58):
    if t < t0 or (t1 is not None and t > t1 + .2): return
    k = pop(t, t0); a = 1 if t1 is None or t <= t1 else max(0, 1 - (t - t1) / .2)
    key = ('c', text, camp, size, sub, w, subk)
    if key not in SPR:
        f = font(size); fs = font(int(size * subk), 'Montserrat-Black.ttf' if subk > 1 else 'Montserrat-ExtraBold.ttf'); bb = f.getbbox(text); tw = bb[2] - bb[0]
        sw = (fs.getbbox(sub)[2] - fs.getbbox(sub)[0]) if sub else 0; cw = w or max(tw, sw) + 90; ch = int(size * (1.75 if not sub else 1.9 + 1.1 * subk))
        edge = GOLD if camp == 'gold' else (RED if camp == 'red' else (110, 230, 140)); im = Image.new('RGBA', (cw + 60, ch + 60)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([30, 30, 30 + cw, 30 + ch], radius=30, outline=edge + (170,), width=12); im = im.filter(ImageFilter.GaussianBlur(9)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([30, 30, 30 + cw, 30 + ch], radius=30, fill=(10, 8, 18, 205) if camp != 'red' else (30, 4, 8, 215), outline=edge + (255,), width=4)
        ty = 30 + ch / 2 - (size * (.2 + .38 * subk) if sub else 0)
        d.text((30 + cw / 2, ty), text, font=f, fill=GOLD2 if camp == 'gold' else ((255, 120, 120) if camp == 'red' else (180, 255, 190)), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0))
        if sub: d.text((30 + cw / 2, 30 + ch / 2 + size * (.25 + .62 * subk)), sub, font=fs, fill=(255, 255, 255) if subk <= 1 else GOLD2, anchor='mm', stroke_width=2 if subk > 1 else 0, stroke_fill=(0, 0, 0))
        SPR[key] = im
    paste(L, SPR[key], x, y, k, a)


def wish(L, t, t0, who, t1=None, title='VOTRE SOUHAIT A ÉTÉ EXAUCÉ'):
    if t < t0 or (t1 is not None and t > t1): return
    card(L, t, t0, 540, 340, title, 'gold', 40, sub=who, t1=t1, subk=1.35)
    for j in range(6):
        a = (t - t0) * 1.4 + j; paste(L, spark_sprite(4, GOLD), 540 + 420 * math.cos(a), 330 + 100 * math.sin(a * 1.3), 1, .8 * min(1, (t - t0) * 3))


def bar(L, t, t0, y, label, pct, col, detail):
    if t < t0: return
    d = ImageDraw.Draw(L); k = ease((t - t0) / .9); x0, x1 = 120, 960
    d.text((x0, y - 58), label, font=font(48), fill=GOLD2 if col == GOLD else (230, 210, 255), anchor='ls', stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((x1, y - 58), f'{int(round(pct * k))} %', font=font(56), fill=(255, 255, 255), anchor='rs', stroke_width=2, stroke_fill=(0, 0, 0))
    d.rounded_rectangle([x0, y - 34, x1, y + 34], radius=34, fill=(10, 8, 18, 210), outline=col + (255,), width=3)
    if k > 0: d.rounded_rectangle([x0 + 6, y - 28, x0 + 6 + (x1 - x0 - 12) * pct / 100 * k, y + 28], radius=28, fill=col + (255,))
    d.text((x0, y + 82), detail, font=font(32, 'Montserrat-ExtraBold.ttf'), fill=(255, 255, 255), anchor='ls', stroke_width=2, stroke_fill=(0, 0, 0))


def gauge(L, t, t0, y, label, val, camp):
    if t < t0: return
    col = GOLD if camp == 'gold' else RED; k = pop(t, t0); d = ImageDraw.Draw(L); x0, x1 = 160, 920
    d.rounded_rectangle([x0 - 30, y - 80, x1 + 30, y + 46], radius=26, fill=(10, 8, 18, 200) if camp == 'gold' else (30, 4, 8, 215), outline=col + (255,), width=3)
    d.text((540, y - 44), label, font=font(38), fill=GOLD2 if camp == 'gold' else (255, 130, 130), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0))
    d.rounded_rectangle([x0, y - 10, x1 - 150, y + 22], radius=16, fill=(40, 30, 50, 255)); v = ease((t - t0) / .8) * val
    d.rounded_rectangle([x0, y - 10, x0 + max(32, (x1 - 150 - x0) * v / 100), y + 22], radius=16, fill=col + (255,))
    d.text((x1, y + 6), f'{int(v)}/100', font=font(38), fill=(255, 255, 255), anchor='rm')


def statrow(L, t, t0, y, n, label, gain, plus=False):
    """ligne du bilan : compteur qui monte de 0 à n, libellé, puis le gain du jeu en or"""
    if t < t0: return
    k = pop(t, t0); q = ease((t - t0) / 1.0); d = ImageDraw.Draw(L); x0, x1 = 90, 990
    d.rounded_rectangle([x0, y - 62, x1, y + 62], radius=28, fill=(10, 8, 18, 215), outline=GOLD + (255,), width=3)
    num = ('+' if plus else '') + str(int(round(n * q)))
    d.text((x0 + 36, y), num, font=font(int(68 * min(k, 1.1))), fill=(255, 255, 255), anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
    nw = font(68).getbbox(num)[2]
    d.text((x0 + 52 + nw, y), label, font=font(34, 'Montserrat-ExtraBold.ttf'), fill=(230, 220, 255), anchor='lm')
    if t >= t0 + .8: d.text((x1 - 30, y), gain, font=font(int(40 * pop(t, t0 + .8))), fill=GOLD2, anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))


def stars3(L, x, y, k):
    d = ImageDraw.Draw(L)
    for j in (-1, 0, 1):
        cx = x + j * 64; r = 26 * k
        pts = [(cx + (r if i % 2 == 0 else r * .45) * math.cos(-math.pi / 2 + i * math.pi / 5), y + (r if i % 2 == 0 else r * .45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
        d.polygon(pts, fill=GOLD + (255,), outline=(255, 250, 220, 255))


def caption(L, t, red=False):
    for a, b, g, k in CAPS:
        if a <= t < b:
            q = min(1, (t - a) / .08); g = g.upper().replace('...', '…'); sz = 76
            while font(sz).getbbox(g)[2] > 940: sz -= 4
            f = font(int(sz * (.92 + .08 * q))); d = ImageDraw.Draw(L)
            d.text((540, 1340), g, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=8, stroke_fill=(70, 8, 16) if red else (36, 16, 70))
            if k in SPEAKER: paste(L, pill_sprite(SPEAKER[k], 'red' if k in ('D', 'D2') else 'gold'), 540, 1262)
            return


def dust(L, t, red=False):
    col = RED if red else GOLD
    for i in range(14):
        life = (t * .12 + i * .137) % 1; x = (i * 211 + 40 * math.sin(t * .7 + i)) % W; y = H * (1 - life)
        paste(L, spark_sprite(2 + i % 3, col), x, y, 1, .55 * math.sin(life * math.pi))


# ---------------------------------------------------------------- plans
def kb(t, k, a, b):
    """interpolation lissée de a vers b sur la durée de la réplique k (+ son silence)"""
    t0 = T[k]; t1 = T[k] + len(clips[k][0]) / SR + GAP[k]; q = ease((t - t0) / (t1 - t0)); return [x + (y - x) * q for x, y in zip(a, b)]


def seg_at(t):
    cur = ORDER[0]
    for k in ORDER:
        if t >= T[k] - (.0 if k == 'B1' else .0): cur = k
    return cur


KNOCKS = [0.0, 0.55, 1.1]                         # coups de knock.mp3 (s), recalés sur le fichier
NEW = ['pancakemiam450', 'nat_gbz', 'matska_prv', 'naelmomo8', 'esteban_gi19', 'justnaxt', 'elo_zht']
CIT = [(.198, '@pancakemiam450'), (.286, '@nat_gbz'), (.373, '@matska_prv'), (.455, '@naelmomo8'), (.536, '@esteban_gi19'), (.625, '@justnaxt'), (.713, '@elo_zht'), (.80, 'Kets4eki'), (.894, 'E_kling')]


def i1(t, k):
    """bureau : plans sur le comptable (I1) et sa bulle @esteban_gi19"""
    keys = {'B1': ((.8, .58, .5, 540, 980), (.9, .62, .48, 540, 960)), 'P1a': ((.9, .62, .48, 540, 960), (1.3, .68, .42, 540, 980)),
            'P1b': ((1.3, .68, .42, 540, 980), (1.38, .68, .41, 540, 980)), 'B2': ((1.38, .68, .41, 540, 980), (1.3, .66, .43, 540, 990)),
            'C1': ((1.3, .66, .43, 540, 990), (1.45, .68, .4, 540, 980)), 'ES': ((1.25, .68, .42, 540, 980), (1.45, .7, .42, 540, 1000))}
    sc, cx, cy, sx, sy = kb(t, k, *keys[k]); fr, P = view('I1', sc, cx, cy, sx, sy); return fr, P


def frame(t):
    k = seg_at(t); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); red = k in ('B12', 'B13', 'D', 'D2'); shake = (0, 0)
    if k in ('SA', 'SB', 'SC', 'SD'):
        fr, P = view('I1', 1.0 + .03 * (t - T['SA']), .55, .45, 540, 960); fr = fr * .28
        card(L, t, T['SA'], 540, 300, 'BILAN DE L\'ÉPISODE 1', 'gold', 56, sub='INSTAGRAM + TIKTOK')
        statrow(L, t, T['SB'] + .1, 520, STATS['likes'], 'LIKES', '+%d ÉCUS' % STATS['ecus'])
        statrow(L, t, wt('SC', 'commentaires') - .5, 700, STATS['comments'], 'COMMENTAIRES', '= VOS VOTES')
        statrow(L, t, wt('SC', 'partages') - .3, 860, STATS['shares'], 'PARTAGES', '+%d POPULARITÉ' % STATS['pop'])
        statrow(L, t, wt('SC', 'enregistrements') - .3, 1020, STATS['saves'], 'ENREGISTREMENTS', '+%d MAGIE' % STATS['magie'])
        statrow(L, t, T['SD'] + .2, 1180, STATS['new'], 'ABONNÉS', 'CITOYENS : %d' % STATS['citizens'], plus=True)
    elif k in ('B1', 'P1a', 'P1b', 'B2', 'C1', 'ES'):
        fr, P = i1(t, k); hx, hy = P(.674, .14); bubble(L, t, LEAD + .15, hx, hy, '@esteban_gi19')   # règle H : bulle dès la 1re apparition du comptable (il est à l'écran dès 0 s)
        if k == 'B1':
            card(L, t, LEAD, 540, 300, 'FROMAGISTAN · ÉPISODE 2', 'gold', 54)
            card(L, t, wt('B1', 'Vous') - .1, 540, 1150, 'RÉSULTAT DU VOTE', 'gold', 60)
        elif k == 'P1a': card(L, t, T['P1a'] + .2, 540, 1150, 'ESTEBAN · COMPTABLE ROYAL', 'gold', 50, sub="IL L'A DEMANDÉ EN COMMENTAIRE")
        elif k == 'P1b': card(L, t, T['P1b'] + .2, 540, 1150, 'IL GARDE LES ÉCUS DU ROYAUME', 'gold', 48, sub='1 LIKE = 2 ÉCUS DANS SON BOULIER')
        elif k == 'B2': card(L, t, wt('B2', 'vote') - .1, 540, 1150, 'SON VOTE = 30 %', 'gold', 60, sub="QUAND ON PARLE D'ARGENT")
        elif k == 'ES': card(L, t, T['ES'] + .1, 540, 1150, 'COFFRE : +%d ÉCUS' % STATS['ecus'], 'gold', 58, sub='1 LIKE = 2 ÉCUS · COMPTÉS DEUX FOIS')
        else: card(L, t, T['C1'] + .1, 540, 1150, '30 % · COMPTÉ DEUX FOIS', 'gold', 54)
    elif k == 'B3':
        fr, P = view('I1', 1.45, .68, .4, 540, 980); fr = fr * .35
        card(L, t, T['B3'], 540, 330, "VOTE D'ARGENT", 'gold', 60)
        bar(L, t, T['B3'] + .1, 620, '1 · LE TOIT', 65, GOLD, 'Comptable 30 % + Kets4eki 35 %')
        bar(L, t, wt('B3', 'Marché') - .1, 900, '2 · LE MARCHÉ', 35, VIO, 'justnaxt 35 %')
        card(L, t, wt('B3', 'On'), 540, 1130, 'LE TOIT GAGNE !', 'green', 66)
    elif k == 'B4':
        sc, cx, cy, sx, sy = kb(t, 'B4', (1.05, .62, .4, 540, 860), (1.2, .7, .38, 540, 860)); fr, P = view('I2', sc, cx, cy, sx, sy)
        e1, e2, e3 = wt('B4', 'Premier') + .6, wt('B4', 'Deuxième') + .5, wt('B4', 'tient') - .1
        for e in (e1, e2):
            if e <= t < e + .35: q = 1 - (t - e) / .35; shake = (28 * q * math.sin(t * 90), 18 * q * math.cos(t * 77))
        card(L, t, e1, 540, 330, "SORT 1 : LE TOIT S'ENVOLE", 'red', 48, t1=e2 - .05)
        card(L, t, e2, 540, 330, 'SORT 2 : IL PLEUT DEDANS', 'red', 48, t1=e3 - .05)
        card(L, t, e3, 540, 330, 'SORT 3 : IL TIENT !', 'green', 56)
        if e3 <= t < e3 + .4: fr = fr + (1 - (t - e3) / .4) * .35
    elif k == 'B5':
        t0, t1 = T['B5'], END['B5'] + GAP['B5']; q = ease((t - t0 - .2) / (t1 - t0 - .4)); cx = .19 + .69 * q
        fr, P = view('I3', 1.25, cx, .69, 540, 1080)
        card(L, t, T['B5'] + .1, 540, 300, 'BIENVENUE AUX NOUVEAUX CITOYENS', 'gold', 42)
        card(L, t, wt('B5', 'citoyens'), 540, 470, 'CITOYENS : %d' % STATS['citizens'], 'gold', 60)
        for j, (ax, nm) in enumerate(CIT):
            hx, hy = P(ax, .655)
            if -60 < hx < W + 60: bubble(L, t, T['B5'] + (ax - .19) / .69 * (t1 - t0 - .4) * .9, hx, hy + 30 - (90 if j % 2 else 0), nm)
    elif k in ('B6', 'K1'):
        sc, cx, cy, sx, sy = kb(t, 'B6', (1.0, .5, .25, 540, 760), (1.15, .5, .22, 540, 700)) if k == 'B6' else kb(t, 'K1', (1.15, .5, .22, 540, 700), (1.3, .5, .2, 540, 680))
        fr, P = view('I4', sc, cx, cy, sx, sy); hx, hy = P(.49, .1); bubble(L, t, T['B6'] + .2, hx, hy, '@justnaxt')
        card(L, t, wt('B6', 'marchand') - .2, 540, 1150, 'KXPL · MARCHAND OFFICIEL', 'gold', 52, sub='DU ROYAUME', t1=wt('B6', 'Sa') - .1)
        card(L, t, wt('B6', 'Sa'), 540, 1150, 'LOI DE KXPL', 'gold', 56, sub="SAVOIR D'OÙ VIENT CHAQUE ALIMENT")
    elif k in ('B7', 'DOC'):
        sc, cx, cy, sx, sy = kb(t, 'B7', (1.05, .47, .45, 540, 900), (1.2, .47, .42, 540, 880)) if k == 'B7' else kb(t, 'DOC', (1.2, .47, .42, 540, 880), (1.35, .47, .4, 540, 860))
        fr, P = view('I5', sc, cx, cy, sx, sy); hx, hy = P(.47, .34); bubble(L, t, T['B7'] + .3, hx, hy, '@nat_gbz')
        wish(L, t, T['B7'] + .2, '@nat_gbz', t1=END['B7'] + .3); card(L, t, wt('B7', 'cabinet') - .2, 540, 1150, '1ER CABINET MÉDICAL', 'gold', 56)
    elif k == 'B8':
        u = t - T['B8']; fr = vid('V_capitaine.mp4', u, .7)
        vu = min(u * .7, 2.4); tr = [(0, .47), (.8, .46), (1.2, .5), (1.6, .5), (2.0, .46), (2.4, .46)]; ax = np.interp(vu, [a for a, _ in tr], [b for _, b in tr]); bubble(L, t, T['B8'] + .5, ax * W, .30 * H, '@elo_zht')
        wish(L, t, T['B8'] + .2, '@elo_zht')
    elif k == 'CAP':
        sc, cx, cy, sx, sy = kb(t, 'CAP', (.8, .48, .45, 540, 900), (1.0, .46, .42, 540, 880)); fr, P = view('I6', sc, cx, cy, sx, sy)
        hx, hy = P(.45, .32); bubble(L, t, T['CAP'] - .2, hx, hy, '@elo_zht')
        card(L, t, T['CAP'] + .2, 540, 1150, 'CAPITAINE DE LA GARDE MONTÉE', 'gold', 46, sub=' ')
        if t >= T['CAP'] + .4: stars3(L, 540, 1192, pop(t, T['CAP'] + .4))
    elif k == 'B9':
        sc, cx, cy, sx, sy = kb(t, 'B9', (.75, .5, .5, 540, 960), (.86, .5, .52, 540, 960)); fr, P = view('I7', sc, cx, cy, sx, sy)
        wish(L, t, T['B9'] + .1, '@matska_prv'); card(L, t, wt('B9', 'bar') - .1, 540, 1150, 'BAR À COCKTAILS', 'gold', 58, sub='SANS ALCOOL · AVEC MODÉRATION')
    elif k == 'B10':
        sc, cx, cy, sx, sy = kb(t, 'B10', (.75, .5, .5, 540, 960), (1.0, .45, .56, 540, 1000)); fr, P = view('I8', sc, cx, cy, sx, sy)
        wish(L, t, T['B10'] + .1, '@naelmomo8', t1=wt('B10', 'Mais') - .1)
        card(L, t, wt('B10', 'Grand') - .1, 540, 1150, 'GRAND PRIX DE FORMULE 1', 'gold', 52, sub='CHAQUE WEEK-END', t1=wt('B10', 'Mais') - .1)
        card(L, t, wt('B10', 'Mais'), 540, 330, 'GRILLE DE DÉPART : VIDE', 'red', 50)
        card(L, t, wt('B10', 'inscris') - .1, 540, 1150, 'INSCRIS TON ÉCURIE', 'gold', 56, sub='EN COMMENTAIRE : UN NOM + UNE COULEUR')
    elif k == 'B11':
        sc, cx, cy, sx, sy = kb(t, 'B11', (.75, .5, .5, 540, 960), (.85, .48, .55, 540, 980)); fr, P = view('I9', sc, cx, cy, sx, sy)
        wish(L, t, T['B11'] + .1, '@pancakemiam450', title='LOI CITOYENNE VOTÉE'); card(L, t, wt('B11', 'reine') - .1, 540, 1150, 'VISITE OFFICIELLE', 'gold', 56, sub='LA REINE DE BEURRÉLIE')
    elif k in ('R1', 'R2'):
        a = (.85, .48, .55, 540, 980); b = (1.25, .47, .5, 540, 900)
        sc, cx, cy, sx, sy = kb(t, 'R1', a, b) if k == 'R1' else kb(t, 'R2', b, (1.4, .47, .5, 540, 880)); fr, P = view('I9', sc, cx, cy, sx, sy)
        if k == 'R1': card(L, t, wt('R1', 'condition') - .1, 540, 330, 'À UNE CONDITION…', 'gold', 60)
        else:
            card(L, t, wt('R2', 'likent') - .1, 300, 1130, 'LIKE', 'gold', 60, sub='= DES ÉCUS', w=420); card(L, t, wt('R2', 'republient') - .1, 780, 1130, 'REPUBLIE', 'gold', 60, sub="= SON AMITIÉ", w=420)
            gauge(L, t, T['R2'] + .1, 360, 'RELATION BEURRÉLIE', 50, 'gold'); card(L, t, wt('R2', 'Sinon'), 540, 560, 'SINON, ELLE REPART', 'red', 46)
    elif k == 'N1':
        sc, cx, cy, sx, sy = kb(t, 'N1', (.78, .5, .5, 540, 960), (1.15, .42, .52, 540, 1000)); fr, P = view('I13', sc, cx, cy, sx, sy)
        fr = fr * (.75 + .25 * ease((t - T['N1']) / 1.5))
        card(L, t, wt('N1', 'carrosse') + .2, 540, 330, 'QUI SE CACHE SOUS LE CARROSSE ?', 'red', 42)
    elif k in ('B12', 'B13'):
        if k == 'B12': sc, cx, cy, sx, sy = kb(t, 'B12', (.75, .5, .55, 540, 1000), (.8, .5, .5, 540, 960))
        else: sc, cx, cy, sx, sy = kb(t, 'B13', (.8, .5, .5, 540, 960), (.95, .5, .4, 540, 900))
        fr, P = view('I10', sc, cx, cy, sx, sy)
        if k == 'B12':
            q = ease((t - T['B12']) / .5); fr = fr * (.25 + .75 * q)
            card(L, t, T['B12'] + .3, 540, 1150, "DE L'AUTRE CÔTÉ DE LA RIVIÈRE…", 'red', 44)
        else:
            hx, hy = P(.52, .14); bubble(L, t, T['B13'] + .1, hx + 250, hy + 120, 'doudou dictador', 'red')
            card(L, t, wt('B13', 'Refusé') - .05, 540, 1150, 'PRÉSIDENT ? REFUSÉ.', 'red', 56, t1=wt('B13', 'Alors') + .4)
            card(L, t, wt('B13', 'Guimauvie') - .1, 540, 1150, 'ROYAUME DE GUIMAUVIE', 'red', 54, sub='3 HABITANTS + 1 CHÈVRE')
    elif k == 'D':
        u = t - T['D']; fr = vid('V_doudou.mp4', u, .55)
        bubble(L, t, T['D'], 300, 350, 'doudou dictador', 'red')
        gauge(L, t, T['D'] + 2.5, 1150, 'RIVALITÉ GUIMAUVIE', 10, 'red')
        if 4.6 <= u < 4.95: q = 1 - (u - 4.6) / .35; shake = (20 * q * math.sin(t * 80), 12 * q)
    elif k == 'D2':
        sc, cx, cy, sx, sy = kb(t, 'D2', (1.0, .5, .3, 540, 860), (1.25, .5, .22, 540, 820)); fr, P = view('I10', sc, cx, cy, sx, sy)
        hx, hy = P(.52, .12); bubble(L, t, T['D2'], hx + 260, hy + 140, 'doudou dictador', 'red')
        card(L, t, wt('D2', 'espion') - .1, 540, 1150, 'UN ESPION AU CHÂTEAU ?', 'red', 56)
    elif k == 'C2':
        sc, cx, cy, sx, sy = kb(t, 'C2', (.78, .5, .5, 540, 960), (.95, .55, .45, 540, 940)); fr, P = view('I14', sc, cx, cy, sx, sy)
        hx, hy = P(.65, .41); bubble(L, t, T['C2'], hx, hy, '@esteban_gi19')
        card(L, t, wt('C2', 'trois'), 540, 330, 'MYSTÈRE : 3 MEULES VOLÉES', 'red', 50)
        card(L, t, END['C2'] + .1, 540, 1150, 'INDICE', 'gold', 54, sub='UNE TOUFFE DE PELUCHE NOIRE…')
    elif k == 'N2':
        sc, cx, cy, sx, sy = kb(t, 'N2', (.78, .5, .52, 540, 960), (1.0, .55, .42, 540, 900)); fr, P = view('I12', sc, cx, cy, sx, sy)
        card(L, t, T['N2'] + .3, 540, 330, 'LA PORTE DE LA CAVE…', 'gold', 54)
        for j, kt in enumerate(KNOCKS):
            e = END['N2'] + .15 + kt
            if e <= t < e + .3: q = 1 - (t - e) / .3; shake = (22 * q * math.sin(t * 95), 14 * q); fr = fr + .18 * q
            if t >= e: card(L, t, e, 540, 1150 - 0 * j, 'TOC. ' * (j + 1), 'gold', 72, t1=(END['N2'] + .15 + KNOCKS[j + 1] - .05) if j + 1 < len(KNOCKS) else None)
    elif k in ('B14', 'B15'):
        sc, cx, cy, sx, sy = (kb(t, 'B14', (.75, .5, .55, 540, 1000), (.8, .5, .6, 540, 1040)) if k == 'B14' else kb(t, 'B15', (.8, .5, .6, 540, 1040), (.9, .5, .65, 540, 1060)))
        fr, P = view('I11', sc, cx, cy, sx, sy)
        if k == 'B14':
            card(L, t, T['B14'], 540, 260, 'PROCHAIN VOTE', 'gold', 54)
            card(L, t, wt('B14', 'Un'), 540, 430, '1 · LA LOI DE KXPL', 'gold', 48, sub='100 ÉCUS', w=900)
            card(L, t, wt('B14', 'Deux'), 540, 640, '2 · MARCHÉ AUX FROMAGES', 'gold', 48, sub='150 ÉCUS', w=900)
            card(L, t, wt('B14', 'Trois'), 540, 850, '3 · MUR ANTI-GUIMAUVE', 'gold', 48, sub='200 ÉCUS', w=900)
        else:
            card(L, t, T['B15'], 540, 330, 'VOTE EN COMMENTAIRE', 'gold', 58, sub='1, 2 OU 3')
            card(L, t, wt('B15', 'abonne'), 540, 560, "ABONNE-TOI", 'green', 60, sub='= 1 CITOYEN DE PLUS')
            card(L, t, END['B15'] + .1, 540, 1130, 'LE COMMENTAIRE LE PLUS LIKÉ', 'gold', 42, sub='DEVIENT UNE LOI')
    else:                                                               # N3 : les deux mystères, fin
        sc, cx, cy, sx, sy = kb(t, 'N3', (1.0, .55, .42, 540, 900), (1.15, .6, .4, 540, 880)); fr, P = view('I12', sc, cx, cy, sx, sy)
        fr = fr * (1 - .45 * ease((t - END['N3']) / 1.5))
        card(L, t, wt('N3', 'vole') - .2, 540, 330, 'QUI VOLE NOS MEULES ?', 'red', 50)
        card(L, t, wt('N3', 'frappe') - .2, 540, 530, 'QUI FRAPPE DANS LA CAVE ?', 'red', 50)
        card(L, t, wt('N3', 'Réponse') - .1, 540, 1150, 'SUITE AU PROCHAIN ÉPISODE', 'gold', 54, sub='ABONNE-TOI POUR SAVOIR')
    dust(L, t, red); caption(L, t, red)
    if red: fr = fr * np.float32([.55, .6, 1.08])[None, None]          # bascule de la lumière vers le rouge (BGR)
    fr = np.clip(fr * vignette(), 0, 1)
    if shake != (0, 0): fr = cv2.warpAffine(fr, np.float32([[1.04, 0, shake[0] - 21.6], [0, 1.04, shake[1] - 38.4]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    ui = np.asarray(L, dtype=np.float32) / 255; rgb = ui[..., [2, 1, 0]]; al = ui[..., 3:]
    out = fr * (1 - al) + rgb * al
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


if __name__ == '__main__':
    print('durée', round(TOTAL, 2), {k: round(v, 2) for k, v in T.items()})
    if '--preview' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--preview') + 1].split(',')]; n = len(ts); cols = min(n, 6); rows = (n + cols - 1) // cols
        sheet = np.zeros((rows * 640, cols * 360, 3), np.uint8)
        for i, tt in enumerate(ts): sheet[(i // cols) * 640:(i // cols + 1) * 640, (i % cols) * 360:(i % cols + 1) * 360] = cv2.resize(frame(tt), (360, 640), interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(O, 'preview.jpg'), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88]); sys.exit()
    if '--frame' in sys.argv:
        tt = float(sys.argv[sys.argv.index('--frame') + 1]); cv2.imwrite(os.path.join(O, f'frame_{tt}.jpg'), frame(tt)); sys.exit()
    mixf = os.path.join(O, 'mix.wav'); mixdown(mixf); silent = os.path.join(O, 'silent.mp4')
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', silent], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', mixf, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(O, 'video.mp4')], check=True); os.remove(silent)
    print('ok', os.path.join(O, 'video.mp4'))
