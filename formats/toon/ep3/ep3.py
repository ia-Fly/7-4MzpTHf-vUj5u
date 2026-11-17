"""FROMAGISTAN · Épisode 3 (format 1 min, 17/11/2026) — copié du monteur ep2 : une prise de voix par réplique, interface et bulles en code.
    python3 ep3.py ASSETS OUT [--preview t1,t2,...]"""
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

def split_clip(fname, a, b, text):
    """réplique tirée d'une prise (de a à b s), mots répartis au prorata des lettres"""
    x = load(fname); seg = x[int(a * SR): int(b * SR) if b else len(x)]; y, off = trim(seg); ws = text.split(); Lc = len(y) / SR
    g = [max(2, len(w)) for w in ws]; tot = sum(g); t0 = .05; out = []
    for w, k in zip(ws, g): d = (Lc - .1) * k / tot; out.append((w, t0, t0 + d)); t0 += d
    return (y, out)



# ---------------------------------------------------------------- ép. 3 : une réplique = une prise (fichiers v1..v9)
LINES = {
    'V1': ('v1.mp3', "Vous avez voté trois, à cent pour cent ! Le mur anti-guimauve sort de terre !"),
    'V2': ('v2.mp3', "Bilan de l'épisode deux : seize likes, trente-deux écus. Sept partages, six commentaires... et cinquante et un citoyens."),
    'V3': ('v3.mp3', "Trois cent quarante-deux écus. Moins deux cents pour le mur. Comme promis, j'avance cent écus pour la loi de Kxpl. Reste : quarante-deux."),
    'V4': ('v4.mp3', "Merci, comptable ! Et mon écurie First est la première inscrite au Grand Prix !"),
    'V5': ('v5.mp3', "Président... Seize likes, c'est maigre. Mais sept partages : j'en demandais cinq. Je signe l'accord beurre contre fromage."),
    'V6': ('v6.mp3', "Mais en creusant sous le mur, la garde a suivi une piste... de petites empreintes en peluche noire."),
    'V7': ('v7.mp3', "Elles ne viennent pas de dehors. Elles sortent de la porte fermée à clé... de notre cave."),
    'V8': ('v8.mp3', "Prochain vote ! Un : Kxpl ministre des commerces et des cultures, zéro écu. Deux : le marché aux fromages, cent cinquante écus. Trois : la garde fouille la cave, trente écus."),
    'V9': ('v9.mp3', "Et si le voleur de meules... n'était jamais sorti du château ? Abonne-toi pour devenir citoyen."),
}
clips = {k: split_clip(f, 0, None, txt) for k, (f, txt) in LINES.items()}
# vrais chiffres de l'ép. 2 (lus le 17/11 : Instagram vidIQ + TikTok profil public), additionnés
STATS = dict(likes=16, ecus=32, comments=6, shares=7, pop=21, saves=1, citizens=51, ig=41, tk=10, coffre=342, reste=42)
SPEAKER = dict(V1='BARBICHU', V2='BARBICHU', V3='LE COMPTABLE', V4='KXPL', V5='LA REINE', V6='BARBICHU', V7='BARBICHU', V8='BARBICHU', V9='BARBICHU')
ORDER = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9']
GAP = dict(V1=.45, V2=.55, V3=.5, V4=.45, V5=.6, V6=.35, V7=1.5, V8=.55, V9=1.6)    # respirations 0,3-0,6 s, plus après la révélation (V7 : 3 coups)
LEAD = .15
T = {}; t = LEAD
for k in ORDER: T[k] = t; t += len(clips[k][0]) / SR + GAP[k]
TOTAL = t
END = {k: T[k] + len(clips[k][0]) / SR for k in ORDER}
KNOCKS = [0.0, 0.42, 0.84]

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
        x = clips[k][0]; a = int(T[k] * SR); voice[a:a + len(x)] += x[:n - a] * (1.12 if k == 'V5' else 1.0)
    def put(buf, name, at, db, dur=None, fade=.35):
        x = load(name)
        if dur: x = x[:int(dur * SR)]
        f = min(int(fade * SR), len(x)); x = x.copy(); x[-f:] *= np.linspace(1, 0, f)
        a = int(at * SR); m = min(len(x), n - a); buf[a:a + m] += x[:m] * 10 ** (db / 20)
    th = load('theme.mp3'); sc = load('score.mp3')
    SECT = ((0, T['V6'] - .2, th, -17), (T['V6'] - .2, T['V8'] - .2, sc, -15), (T['V8'] - .2, T['V9'] - .2, th, -17), (T['V9'] - .2, TOTAL, sc, -14))
    for a0, a1, src, db in SECT:                        # fondu enchaîné de 0,8 s entre ambiances
        a0 = max(0, a0 - .4); a1 = min(TOTAL, a1 + .4)
        i0, i1 = int(a0 * SR), int(a1 * SR); L = i1 - i0; loop = np.tile(src, L // len(src) + 1)[:L].copy(); f = int(.8 * SR)
        loop[:f] *= np.linspace(0, 1, f); loop[-f:] *= np.linspace(1, 0, f); mus[i0:i1] += loop * 10 ** (db / 20)
    S = [('spell-ok.mp3', T['V1'] + .05, -9, 1.6), ('cheer.mp3', END['V1'] + .05, -10, None), ('coins.mp3', wt('V2', 'seize') + .2, -12, 1.3),
         ('coins.mp3', T['V3'] + .05, -12, 1.2), ('coins.mp3', wt('V3', 'Reste') - .1, -12, 1.0), ('car.mp3', T['V4'] - .1, -13, 2.5),
         ('fanfare.mp3', wt('V5', 'signe') + .3, -11, 2.0), ('riser.mp3', T['V6'] + .1, -14, 3.5), ('knock.mp3', END['V7'] + .2, -5, 1.2),
         ('boom.mp3', END['V9'] + .1, -9, 1.5)]
    # un seul bruitage à la fois (Matis, 15/11) : s'il chevauche le précédent, on le décale (≤ 0,6 s) ou on l'abandonne
    S = sorted(S, key=lambda e: e[1]); keep = []; busy = -1.0
    for name, at, db, dur in S:
        ln = dur if dur else len(load(name)) / SR
        if name == 'knock.mp3': ln = KNOCKS[-1] + .25
        if at < busy - .05 and name != 'knock.mp3':
            if busy - at <= .6: at = busy + .05
            else: continue
        keep.append((name, at, db, dur)); busy = max(busy, at + ln)
    for name, at, db, dur in keep:
        if name == 'knock.mp3':
            kn = load('knock.mp3')[int(1.60 * SR):int(1.82 * SR)].copy(); kn[-480:] *= np.linspace(1, 0, 480)
            for kt in KNOCKS:
                i0 = int((at + kt) * SR); fx[i0:i0 + len(kn)] += kn * 10 ** (db / 20)
            continue
        put(fx, name, at, db, dur)
    env = np.abs(voice); k = int(.02 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); env = np.convolve((env > .02).astype(np.float32), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
    duck = 1 - .55 * np.clip(env, 0, 1); mix = voice + mus * duck + fx * (1 - .6 * np.clip(env, 0, 1))      # musique et bruitages baissés sous la voix
    meter = pyln.Meter(SR)
    for _ in range(3):                                # -14 LUFS puis limiteur doux
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




def frame(t):
    k = seg_at(t); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); shake = (0, 0)
    if k == 'V1':                                                       # accroche : le mur se construit (plan animé), résultat du vote
        u = t - T['V1']
        if os.path.exists(os.path.join(A, 'V_mur.mp4')):            # plan animé remonté de 300 px : le visage passe au-dessus des sous-titres
            fr = cv2.warpAffine(vid('V_mur.mp4', u, .8), np.float32([[1.08, 0, -43.2], [0, 1.08, -300]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
        else: fr, P = view('J1', .81, .5, .58, 540, 860)
        card(L, t, LEAD, 540, 250, 'FROMAGISTAN · ÉPISODE 3', 'gold', 50)
        card(L, t, LEAD + .25, 540, 420, 'VOUS AVEZ VOTÉ 3 · 100 %', 'gold', 54, sub='MUR ANTI-GUIMAUVE · 200 ÉCUS')
        card(L, t, wt('V1', 'mur') - .2, 540, 610, 'VOTE DU COMPTABLE : 30 %', 'gold', 40, sub='@esteban_gi19 · @justnaxt · @alice._.glt31')
    elif k == 'V2':                                                     # bilan éclair de l'ép. 2, vrais chiffres
        fr, P = view('J1', .81 + .01 * (t - T['V2']), .5, .58, 540, 860); fr = fr * .3
        card(L, t, T['V2'], 540, 300, "BILAN DE L'ÉPISODE 2", 'gold', 56, sub='INSTAGRAM + TIKTOK')
        statrow(L, t, wt('V2', 'seize') - .2, 520, STATS['likes'], 'LIKES', '+%d ÉCUS' % STATS['ecus'])
        statrow(L, t, wt('V2', 'Sept') - .2, 690, STATS['shares'], 'PARTAGES', '+%d POPULARITÉ' % STATS['pop'])
        statrow(L, t, wt('V2', 'six') - .2, 860, STATS['comments'], 'COMMENTAIRES', '= VOS VOTES')
        statrow(L, t, wt('V2', 'cinquante') - .2, 1030, STATS['citizens'], 'CITOYENS', 'IG %d + TIKTOK %d' % (STATS['ig'], STATS['tk']))
    elif k == 'V3':                                                     # le Comptable et son boulier
        sc, cx, cy, sx, sy = kb(t, 'V3', (1.1, .64, .42, 540, 820), (1.3, .66, .4, 540, 820)); fr, P = view('E1', sc, cx, cy, sx, sy)
        hx, hy = P(.68, .15); bubble(L, t, T['V3'] + .05, hx, hy, '@esteban_gi19')
        m, a, r = wt('V3', 'Moins'), wt('V3', "j'avance"), wt('V3', 'Reste')
        card(L, t, T['V3'] + .1, 540, 1110, 'COFFRE : %d ÉCUS' % STATS['coffre'], 'gold', 58, sub='310 + 32 DES LIKES', t1=m - .05)
        card(L, t, m, 540, 1110, 'MUR : −200 ÉCUS', 'red', 58, t1=a - .05)
        card(L, t, a, 540, 1110, 'LOI DE KXPL : −100', 'gold', 56, sub='AVANCE DU COMPTABLE', t1=r - .05)
        card(L, t, r, 540, 1110, 'RESTE : %d ÉCUS' % STATS['reste'], 'green', 62)
    elif k == 'V4':                                                     # Kxpl : loi votée + écurie First
        sc, cx, cy, sx, sy = kb(t, 'V4', (.78, .46, .5, 540, 960), (.9, .44, .48, 540, 960)); fr, P = view('J2', sc, cx, cy, sx, sy)
        hx, hy = P(.43, .34); bubble(L, t, T['V4'] + .05, hx, hy, '@justnaxt')
        wish(L, t, T['V4'] + .05, '@justnaxt')
        e = wt('V4', 'écurie') - .1
        card(L, t, T['V4'] + .2, 540, 1110, 'LOI DE KXPL VOTÉE', 'gold', 52, sub="CHAQUE ALIMENT DIT D'OÙ IL VIENT", t1=e - .05)
        card(L, t, e, 540, 1110, 'ÉCURIE « FIRST »', 'gold', 58, sub='1RE ÉCURIE INSCRITE AU GRAND PRIX')
    elif k == 'V5':                                                     # condition de la Reine : vrais chiffres
        sc, cx, cy, sx, sy = kb(t, 'V5', (.78, .5, .5, 540, 960), (.9, .45, .5, 540, 960)); fr, P = view('J3', sc, cx, cy, sx, sy)
        s1, s2, s3 = wt('V5', 'Seize'), wt('V5', 'sept'), wt('V5', 'signe')
        card(L, t, T['V5'] + .1, 540, 330, 'CONDITION DE LA REINE', 'gold', 50, sub='5 PARTAGES DE L\'ÉPISODE 2', t1=s1 - .05)
        card(L, t, s1, 540, 330, '16 LIKES… C\'EST MAIGRE', 'red', 50, t1=s2 - .05)
        card(L, t, s2, 540, 330, '7 PARTAGES SUR 5 DEMANDÉS', 'green', 50, t1=s3 - .05)
        gauge(L, t, s3, 360, 'RELATION BEURRÉLIE', 60, 'gold')
        card(L, t, s3 + .2, 540, 1110, 'ACCORD SIGNÉ', 'gold', 60, sub='BEURRE CONTRE FROMAGE')
    elif k in ('V6', 'V7'):                                             # le mystère avance d'un indice
        if k == 'V6': sc, cx, cy, sx, sy = kb(t, 'V6', (.76, .5, .5, 540, 960), (.95, .5, .62, 540, 960))
        else: sc, cx, cy, sx, sy = kb(t, 'V7', (.95, .5, .62, 540, 960), (1.2, .5, .4, 540, 900))
        fr, P = view('J4', sc, cx, cy, sx, sy)
        if k == 'V6':
            fr = fr * (.55 + .45 * ease((t - T['V6']) / 1.2))
            card(L, t, wt('V6', 'empreintes') - .1, 540, 330, 'INDICE : EMPREINTES DE PELUCHE', 'red', 44)
        else:
            card(L, t, wt('V7', 'sortent') - .1, 540, 330, 'ELLES SORTENT DE LA CAVE…', 'red', 50)
            for j, kt in enumerate(KNOCKS):
                e = END['V7'] + .2 + kt
                if e <= t < e + .3: q = 1 - (t - e) / .3; shake = (20 * q * math.sin(t * 95), 12 * q); fr = fr + .15 * q
                if t >= e: card(L, t, e, 540, 1110, 'TOC. ' * (j + 1), 'gold', 72, t1=(END['V7'] + .2 + KNOCKS[j + 1] - .05) if j + 1 < len(KNOCKS) else None)
    elif k == 'V8':                                                     # 3 choix chiffrés (vote d'argent)
        sc, cx, cy, sx, sy = kb(t, 'V8', (.75, .5, .62, 540, 1060), (.8, .5, .62, 540, 1060)); fr, P = view('VOTE', sc, cx, cy, sx, sy); fr = fr * .8
        card(L, t, T['V8'], 540, 250, 'PROCHAIN VOTE', 'gold', 54, sub="VOTE D'ARGENT · COMPTABLE 30 %")
        card(L, t, wt('V8', 'Un'), 540, 430, '1 · KXPL MINISTRE', 'gold', 46, sub='DES COMMERCES ET DES CULTURES · 0 ÉCU', w=960)
        card(L, t, wt('V8', 'Deux'), 540, 610, '2 · MARCHÉ AUX FROMAGES', 'gold', 46, sub='150 ÉCUS (COFFRE : 42)', w=960)
        card(L, t, wt('V8', 'Trois'), 540, 790, '3 · LA GARDE FOUILLE LA CAVE', 'gold', 46, sub='30 ÉCUS', w=960)
    else:                                                               # V9 : cliffhanger + abonne-toi
        sc, cx, cy, sx, sy = kb(t, 'V9', (1.2, .5, .4, 540, 900), (1.35, .5, .35, 540, 880)); fr, P = view('J4', sc, cx, cy, sx, sy)
        fr = fr * (1 - .4 * ease((t - END['V9']) / 1.2))
        card(L, t, wt('V9', 'voleur') - .1, 540, 330, 'LE VOLEUR EST DANS LE CHÂTEAU ?', 'red', 44)
        card(L, t, wt('V9', 'Abonne') - .1, 540, 560, 'ABONNE-TOI', 'green', 60, sub='= 1 CITOYEN DE PLUS')
        card(L, t, END['V9'] - .3, 540, 1110, 'VOTE 1, 2 OU 3 EN COMMENTAIRE', 'gold', 42, sub='LE PLUS LIKÉ DEVIENT UNE LOI')
    dust(L, t); caption(L, t)
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
