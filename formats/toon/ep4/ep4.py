"""FROMAGISTAN · Épisode 4 (21/11/2026) — règles anti-décrochage du 19/11 (35-50 s, accroche qui bouge, un seul élément d'interface à la fois, bilan à la fin).
    Copié du monteur ep3 ; les plans Veo sont remplacés par des mouvements en code (tourbillon, coulure, secousses) car le compte ElevenLabs connecté le 21/11 est gratuit.
    python3 ep4.py ASSETS OUT [--preview t1,t2,...]"""
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





# ---------------------------------------------------------------- ép. 4 (21/11/2026) : format anti-décrochage (35-50 s, accroche qui bouge, bilan à la fin)
LINES = {
    'V1': ('v1.mp3', "Une guimauve géante attaque mon château… et une seule attaque a suffi !"),
    'V2': ('v2.mp3', "Ici, c'est toi qui gouvernes un pays de fromage. Tes commentaires deviennent des attaques."),
    'V3': ('v3.mp3', "Kxpl lance la Tempête des épices ! Et les épices… détruisent la guimauve !"),
    'V4': ('v4.mp3', "Elle fond ! Le Comptable taxe les oursons : ruinés, ils lâchent nos meules. Et le Docteur lance son Serment mortel !"),
    'V5': ('v5.mp3', "Ma guimauve… fondue ?! Je reviendrai… au Grand Prix !"),
    'V6': ('v6.mp3', "Mais dans la cave… un badge d'ourson. Avec la marque du carrosse de la Reine."),
    'V7': ('v7.mp3', "Écris en commentaire : un, Kxpl ministre. Deux, le marché aux fromages. Trois, un piège à espion."),
    'V8': ('v8.mp3', "Bilan : quarante-deux écus gagnés, et cinquante-cinq citoyens."),
    'V9': ('v9.mp3', "Qui a ouvert la cave à Doudou ? Abonne-toi pour devenir citoyen."),
}
clips = {k: split_clip(f, 0, None, txt) for k, (f, txt) in LINES.items()}
# vrais chiffres (lus le 21/11) : likes ép. 3 + spécial = IG 4 + 2, TikTok 10 + 5 = 21 likes = +42 écus ; abonnés IG 42 + TikTok 13 = 55
STATS = dict(ecus=42, citizens=55, coffre=84)
SPEAKER = dict(V1='BARBICHU', V2='BARBICHU', V3='BARBICHU', V4='BARBICHU', V5='DOUDOU DICTADOR', V6='BARBICHU', V7='BARBICHU', V8='BARBICHU', V9='BARBICHU')
REDLINES = {'V5'}
ORDER = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9']
GAP = dict(V1=.25, V2=.3, V3=.3, V4=.3, V5=.35, V6=.3, V7=.3, V8=.25, V9=.9)
LEAD = .08
T = {}; t = LEAD
for k in ORDER: T[k] = t; t += len(clips[k][0]) / SR + GAP[k]
TOTAL = t
END = {k: T[k] + len(clips[k][0]) / SR for k in ORDER}


def wt(seg, word, n=1, which=0):
    c = 0
    for a, s, e in clips[seg][1]:
        if a.lower().strip('.,!:…?').startswith(word.lower()):
            c += 1
            if c == n: return T[seg] + (s if which == 0 else e)
    raise KeyError(seg + ' ' + word)


CAPS = []
for k in ORDER:
    ws = []
    for a, s, e in clips[k][1]:
        if a in (':', '!', '?', '?!') and ws: ws[-1] = (ws[-1][0] + ' ' + a, ws[-1][1], e); continue
        ws.append((a, s, e))
    grp = []
    for a, s, e in ws:
        grp.append((a, s, e))
        if len(grp) == 3 or a[-1] in '.!?:…,':
            CAPS.append((T[k] + grp[0][1] - .05, T[k] + grp[-1][2] + .05, ' '.join(g[0] for g in grp), k)); grp = []
    if grp: CAPS.append((T[k] + grp[0][1] - .05, T[k] + grp[-1][2] + .05, ' '.join(g[0] for g in grp), k))
for i in range(len(CAPS) - 1):
    if CAPS[i][3] == CAPS[i + 1][3]: CAPS[i] = (CAPS[i][0], CAPS[i + 1][0], CAPS[i][2], CAPS[i][3])

# ---------------------------------------------------------------- plans (un changement toutes les 2 à 3 s)
CUTS = []  # (début, nom du plan)


def build_cuts():
    c = [(0.0, 'storm_wide'), (T['V1'] + 2.0, 'storm_hit'),
         (T['V2'], 'barbichu'), (wt('V2', 'Tes'), 'kxpl_far'),
         (T['V3'], 'kxpl'), (wt('V3', 'Et'), 'storm_wide2'),
         (T['V4'], 'melt'), (wt('V4', 'Comptable') - .15, 'esteban'), (wt('V4', 'ruinés') - .05, 'bears'), (wt('V4', 'Docteur') - .15, 'docteur'),
         (T['V5'], 'doudou'), (wt('V5', 'Je'), 'doudou_wide'),
         (T['V6'], 'badge_wide'), (wt('V6', 'Avec') - .1, 'badge_close'),
         (T['V7'], 'vote0'), (wt('V7', 'un') - .1, 'vote1'), (wt('V7', 'Deux') - .1, 'vote2'), (wt('V7', 'Trois') - .1, 'vote3'),
         (T['V8'], 'bilan'), (wt('V8', 'cinquante') - .1, 'bilan2'),
         (T['V9'], 'question'), (wt('V9', 'Abonne') - .1, 'abonne')]
    return c


CUTS = build_cuts()


def cut_at(t):
    cur, t0 = CUTS[0][1], 0.0
    for a, n in CUTS:
        if t >= a: cur, t0 = n, a
    return cur, t0


def cut_end(t0):
    for a, n in CUTS:
        if a > t0 + 1e-6: return a
    return TOTAL



def mixdown(out):
    n = int(TOTAL * SR); voice = np.zeros(n, np.float32); mus = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
    for k in ORDER:
        x = clips[k][0]; a = int(T[k] * SR); voice[a:a + len(x)] += x[:n - a]
    def put(buf, name, at, db, dur=None, fade=.25):
        x = load(name)
        if dur: x = x[:int(dur * SR)]
        f = min(int(fade * SR), len(x)); x = x.copy(); x[-f:] *= np.linspace(1, 0, f)
        a = int(at * SR); m = min(len(x), n - a); buf[a:a + m] += x[:m] * 10 ** (db / 20)
    m = load('music.mp3'); L = min(len(m), n); mus[:L] = m[:L] * 10 ** (-15 / 20)
    f = int(1.2 * SR); mus[max(0, n - f):n] *= np.linspace(1, 0, n - max(0, n - f))
    # un bruitage court à chaque changement de plan, un seul à la fois (logique du monteur ep2/ep3)
    S = [('swirl.mp3', 0.0, -13, 2.0), ('impact.mp3', T['V1'] + 1.95, -11, 1.0), ('impact.mp3', T['V3'] - .12, -11, 1.0),
         ('swirl.mp3', wt('V3', 'Et') - .05, -14, 1.6), ('goo.mp3', T['V4'] - .1, -11, 1.3), ('coins.mp3', wt('V4', 'Comptable') - .15, -13, 1.2),
         ('magic.mp3', wt('V4', 'Docteur') - .15, -12, 1.6), ('goo.mp3', T['V5'] - .15, -12, 1.0), ('mystery.mp3', T['V6'] - .1, -10, 2.4),
         ('impact.mp3', wt('V7', 'un') - .1, -16, .6), ('impact.mp3', wt('V7', 'Deux') - .1, -16, .6), ('impact.mp3', wt('V7', 'Trois') - .1, -16, .6),
         ('coins.mp3', T['V8'] - .05, -12, 1.4), ('impact.mp3', T['V9'] - .1, -13, .8)]
    S = sorted(S, key=lambda e: e[1]); busy = -1.0
    for name, at, db, dur in S:
        if not os.path.exists(os.path.join(A, name)): continue
        ln = min(dur, len(load(name)) / SR)
        if at < busy - .05:
            if busy - at <= .4: at = busy + .05
            else: continue
        put(fx, name, at, db, dur); busy = at + ln
    env = np.abs(voice); k = int(.02 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); env = np.convolve((env > .02).astype(np.float32), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
    mix = voice + mus * (1 - .6 * np.clip(env, 0, 1)) + fx * (1 - .6 * np.clip(env, 0, 1))
    meter = pyln.Meter(SR)
    for _ in range(3):
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


def bubble(L, t, t0, hx, hy, name, camp='gold', t1=None, scale=1.0):
    """Bulle de nom : petite boule lumineuse + étincelles en orbite + pastille « @pseudo », posée au-dessus de la tête (hx, hy = haut de la tête)."""
    if t < t0 or (t1 is not None and t > t1): return
    k = pop(t, t0, .35); fl = 5 * math.sin((t - t0) * 2.6); pulse = 1 + .06 * math.sin((t - t0) * 5.0)
    col = GOLD if camp == 'gold' else RED
    sp = pill_sprite(name, camp); oy = max(hy - 120, 230); px = min(max(hx, sp.width * scale / 2 + 10), (1075 if oy < 900 else 940) - sp.width * scale / 2)   # colonne de boutons : moitié basse seulement
    py = oy + fl; paste(L, sp, px, py + 52 * scale, k * scale)
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




# ---------------------------------------------------------------- effets de mouvement (remplacent les plans Veo, indisponibles sur l'offre gratuite)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def swirl(fr, cx, cy, r, ang):
    """tourbillon : rotation qui décroît avec la distance au centre (cx, cy en px écran)"""
    dx, dy = XX - cx, YY - cy; d = np.sqrt(dx * dx + dy * dy); a = ang * np.clip(1 - d / r, 0, 1) ** 2
    c, s = np.cos(a), np.sin(a); mx = cx + dx * c - dy * s; my = cy + dx * s + dy * c
    return cv2.remap(fr, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def melt(fr, y0, y1, amp, t):
    """la guimauve coule : déplacement vertical ondulé dans la bande y0-y1"""
    w = np.clip((YY - y0) / max(1, (y1 - y0)), 0, 1); w = np.sin(w * math.pi)
    off = amp * w * (0.6 + 0.4 * np.sin(XX / 37 + t * 3.1)) * (0.5 + 0.5 * np.sin(XX / 91 - t * 1.7))
    return cv2.remap(fr, XX, YY - off, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def shake_fr(fr, t, t0, amp=22, d=.35):
    if not (t0 <= t < t0 + d): return fr
    q = 1 - (t - t0) / d; sx = amp * q * math.sin(t * 97); sy = amp * .6 * q * math.cos(t * 83)
    return cv2.warpAffine(fr, np.float32([[1.04, 0, sx - 21.6], [0, 1.04, sy - 38.4]]), (W, H), borderMode=cv2.BORDER_REFLECT)


def flash(fr, t, t0, d=.2, k=.55):
    if t0 <= t < t0 + d: fr = fr + k * (1 - (t - t0) / d)
    return fr


def speed_lines(L, t, cx, cy, col=(255, 255, 255), n=34, alpha=110):
    rng = np.random.default_rng(int(t * 15)); d = ImageDraw.Draw(L)
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(560, 760); r1 = 1500; w = rng.uniform(.006, .016)
        p = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)), (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))]
        d.polygon(p, fill=col + (alpha,))


def particles(L, t, t0, cx, cy, col, n=46, speed=900, seed=3):
    rng = np.random.default_rng(seed)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); ph = rng.uniform(0, 1); sp = speed * rng.uniform(.5, 1.3)
        life = ((t - t0) * .9 + ph) % 1; r = 30 + sp * life
        paste(L, spark_sprite(int(3 + 4 * life) + i % 2, col), cx + r * math.cos(a), cy + r * math.sin(a), 1, .9 * (1 - life))


def seal(L, t, t0, cx, cy, R=330):
    """sceau de lumière du « Serment mortel » : anneaux d'or et de violet qui tournent, étoiles"""
    if t < t0: return
    k = ease((t - t0) / .45); d = ImageDraw.Draw(L)
    for j, (rr, col, w) in enumerate(((R, GOLD, 10), (R * .78, VIO, 7), (R * 1.18, GOLD2, 4))):
        r = rr * k; d.ellipse([cx - r, cy - r * .42, cx + r, cy + r * .42], outline=col + (220,), width=w)
    for j in range(8):
        a = (t - t0) * 1.6 + j * math.pi / 4; paste(L, spark_sprite(6, GOLD), cx + R * k * math.cos(a), cy + R * .42 * k * math.sin(a), 1.2)
    paste(L, glow_sprite(int(40 * k) + 1, GOLD), cx, cy, 1, .5)
    key = ('band', R)
    if key not in SPR:                                 # bande de lumière dorée (cache aussi le bord du plan réutilisé)
        im = Image.new('RGBA', (1300, 400)); d2 = ImageDraw.Draw(im); d2.ellipse([50, 140, 1250, 260], fill=GOLD + (235,)); d2.ellipse([250, 175, 1050, 225], fill=(255, 250, 225, 255))
        SPR[key] = im.filter(ImageFilter.GaussianBlur(28))
    paste(L, SPR[key], cx, cy, 1, k)


def caption(L, t):
    for a, b, g, k in CAPS:
        if a <= t < b:
            q = min(1, (t - a) / .08); g = g.upper().replace('...', '…'); sz = 84
            while font(sz).getbbox(g)[2] > 960: sz -= 4
            f = font(int(sz * (.92 + .08 * q))); d = ImageDraw.Draw(L); red = k in REDLINES
            d.text((540, 1350), g, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=9, stroke_fill=(70, 8, 16) if red else (36, 16, 70))
            if t >= 3.0: paste(L, pill_sprite(SPEAKER[k], 'red' if red else 'gold'), 540, 1262)
            return


def dust(L, t, red=False):
    col = RED if red else GOLD
    for i in range(12):
        life = (t * .12 + i * .137) % 1; x = (i * 211 + 40 * math.sin(t * .7 + i)) % W; y = H * (1 - life)
        paste(L, spark_sprite(2 + i % 3, col), x, y, 1, .5 * math.sin(life * math.pi))


def mv(t, t0, t1, a, b):
    """mouvement de caméra rapide et visible entre a et b sur le plan (t0, t1)"""
    q = ease((t - t0) / max(.01, t1 - t0)); return [x + (y - x) * q for x, y in zip(a, b)]


def frame(t):
    name, t0 = cut_at(t); t1 = cut_end(t0); u = t - t0; L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); red = False
    if name in ('storm_wide', 'storm_wide2'):                # I1 : la Tempête des épices frappe la guimauve géante (tourbillon animé)
        sc, cx, cy = mv(t, t0, t1, (.78, .5, .5), (.95, .42, .44)) if name == 'storm_wide' else mv(t, t0, t1, (.9, .55, .45), (1.05, .62, .38))
        fr, P = view('I1', sc, cx, cy, 540, 900); vx, vy = P(.21, .37)
        fr = swirl(fr, vx, vy, 300, 2.2 * math.sin(t * 1.3) + t * 2.6)
        particles(L, t, t0, vx, vy, GOLD, 40, 1100); speed_lines(L, t, vx + 200, vy, (255, 230, 170), 26, 80)
        fr = flash(fr, t, t0, .14, .35)
        if name == 'storm_wide2':
            dt = wt('V3', 'détruisent'); fr = flash(fr, t, dt, .22, .5); fr = shake_fr(fr, t, dt)
    elif name == 'storm_hit':                                 # gros plan : la guimauve est touchée
        sc, cx, cy = mv(t, t0, t1, (1.25, .7, .3), (1.45, .68, .32)); fr, P = view('I1', sc, cx, cy, 540, 820)
        hx, hy = P(.45, .4); fr = swirl(fr, hx, hy, 600, t * 3.0); fr = melt(fr, 300, 1300, 40 * u, t)
        fr = flash(fr, t, t0, .2, .6); fr = shake_fr(fr, t, t0, 28, .45); particles(L, t, t0, hx, hy, (255, 200, 120), 40, 1000, 5)
        speed_lines(L, t, 540, 820, (255, 255, 255), 30, 90)
    elif name == 'barbichu':                                  # Barbichu : contexte pour les nouveaux
        sc, cx, cy = mv(t, t0, t1, (1.65, .38, .45), (2.0, .34, .42)); fr, P = view('P_barbichu', sc, cx, cy, 540, 860); fr = flash(fr, t, t0, .12, .3)
        paste(L, glow_sprite(18, GOLD), *P(.52, .5), 1, .0)
    elif name == 'kxpl_far':                                  # Kxpl dans I1 (le public lance les attaques)
        sc, cx, cy = mv(t, t0, t1, (1.0, .3, .68), (1.2, .3, .66)); fr, P = view('I1', sc, cx, cy, 540, 860)
        vx, vy = P(.2, .45); fr = swirl(fr, vx, vy, 420, t * 2.4); particles(L, t, t0, vx, vy, GOLD, 30, 800, 7)
    elif name == 'kxpl':                                      # Kxpl (@justnaxt) en gros plan, bulle de nom
        sc, cx, cy = mv(t, t0, t1, (1.85, .42, .42), (2.15, .4, .38)); fr, P = view('P_kxpl', sc, cx, cy, 540, 760)
        speed_lines(L, t, 540, 760, (255, 236, 190), 34, 100); fr = flash(fr, t, t0, .16, .45); fr = shake_fr(fr, t, t0, 18, .3)
        bx, by = P(.53, .088); bubble(L, t, t0, bx, by - 52 * sc + 120, '@justnaxt', scale=sc)
    elif name == 'melt':                                      # « Elle fond ! » : la guimauve coule
        sc, cx, cy = mv(t, t0, t1, (.95, .5, .3), (1.1, .5, .34)); fr, P = view('I2', sc, cx, cy, 540, 760)
        fr = melt(fr, 0, 1500, 30 + 160 * u, t); fr = flash(fr, t, t0, .15, .4)
    elif name == 'esteban':                                   # le Comptable (@esteban_gi19) taxe les oursons
        sc, cx, cy = mv(t, t0, t1, (1.6, .54, .4), (1.75, .56, .36)); fr, P = view('P_esteban', sc, cx, cy, 540, 780)
        particles(L, t, t0, 540, 900, GOLD, 34, 700, 11); bx, by = P(.68, .37); bubble(L, t, t0, bx, by - 52 * sc + 120, '@esteban_gi19', scale=sc)
        fr = flash(fr, t, t0, .14, .35)
    elif name == 'bears':                                     # les oursons ruinés lâchent les meules
        sc, cx, cy = mv(t, t0, t1, (1.3, .2, .7), (1.5, .26, .72)); fr, P = view('I2', sc, cx, cy, 540, 900)
        fr = shake_fr(fr, t, t0, 14, .3); particles(L, t, t0, 400, 900, GOLD2, 20, 600, 13)
    elif name == 'docteur':                                   # le Docteur (@nat_gbz) et son Serment mortel
        sc, cx, cy = mv(t, t0, t1, (1.55, .5, .62), (1.8, .5, .66)); fr, P = view('P_docteur', sc, cx, cy, 540, 760)
        fr = fr * .85; seal(L, t, t0, 540, P(.5, 1.0)[1] - 10, 380); speed_lines(L, t, 540, 820, (255, 230, 160), 24, 70)
        bx, by = P(.525, .178); bubble(L, t, t0, bx, by - 52 * sc + 120, '@nat_gbz', scale=sc); fr = flash(fr, t, t0 + .2, .25, .5)
    elif name in ('doudou', 'question'):                      # Doudou Dictador s'enfuit (gros plan)
        red = True; sc, cx, cy = mv(t, t0, t1, (1.3, .5, .7), (1.55, .5, .7)); fr, P = view('I2', sc, cx, cy, 540, 760)
        fr = shake_fr(fr, t, t0, 16, .3); speed_lines(L, t, 540, 700, (255, 60, 60), 30, 70)
        if name == 'doudou': hx, hy = P(.5, .58); bubble(L, t, t0 + .15, hx, max(hy, 430), 'doudou dictador', 'red')
    elif name == 'doudou_wide':                               # plan large : la guimauve fondue, Doudou fuit
        red = True; sc, cx, cy = mv(t, t0, t1, (.95, .5, .5), (.78, .5, .52)); fr, P = view('I2', sc, cx, cy, 540, 960)
        fr = melt(fr, 200, 1000, 60 + 60 * u, t)
    elif name in ('badge_wide', 'badge_close'):               # indice : le badge du carrosse
        if name == 'badge_wide': sc, cx, cy = mv(t, t0, t1, (.78, .5, .45), (.95, .55, .5))
        else: sc, cx, cy = mv(t, t0, t1, (1.35, .6, .5), (1.6, .6, .5))
        fr, P = view('I5', sc, cx, cy, 540, 820); fr = fr * (.7 + .3 * ease(u / 1.0)); fr = flash(fr, t, t0, .12, .25)
        bx, by = P(.6, .5); paste(L, glow_sprite(26, GOLD), bx, by, 1, .25 + .2 * math.sin(t * 6))
    elif name.startswith('vote'):                             # le choix à commenter (seul appel à l'action)
        i = int(name[-1]); bg = {0: 'P_barbichu', 1: 'P_kxpl', 2: 'I1', 3: 'I5'}[i]
        if bg == 'I1': sc, cx, cy = mv(t, t0, t1, (1.5, .16, .16), (1.7, .2, .18)); fr, P = view(bg, sc, cx, cy, 540, 760)
        elif bg == 'I5': sc, cx, cy = mv(t, t0, t1, (.9, .55, .45), (1.05, .58, .48)); fr, P = view(bg, sc, cx, cy, 540, 900)
        else: sc, cx, cy = mv(t, t0, t1, (1.7, .45, .4), (1.95, .45, .38)); fr, P = view(bg, sc, cx, cy, 540, 860)
        fr = fr * .6
        if i == 0: card(L, t, t0, 540, 470, 'ÉCRIS 1, 2 OU 3', 'gold', 66, sub='EN COMMENTAIRE', subk=.7)
        if i == 1: card(L, t, t0, 540, 470, '1 · KXPL MINISTRE', 'gold', 58, sub='0 ÉCU · VOTE DU COMPTABLE : 30 %', w=980, subk=.6)
        if i == 2: card(L, t, t0, 540, 470, '2 · MARCHÉ AUX FROMAGES', 'gold', 54, sub='150 ÉCUS · COFFRE : %d' % STATS['coffre'], w=980, subk=.62)
        if i == 3: card(L, t, t0, 540, 470, '3 · PIÈGE À ESPION', 'gold', 58, sub='30 ÉCUS', w=980, subk=.62)
    elif name in ('bilan', 'bilan2'):                         # bilan éclair (2 chiffres)
        sc, cx, cy = mv(t, t0, t1, (1.7, .4, .42), (1.9, .38, .4)) if name == 'bilan' else mv(t, t0, t1, (2.1, .3, .38), (2.3, .3, .36))
        fr, P = view('P_barbichu', sc, cx, cy, 540, 860); fr = fr * .75
        card(L, t, T['V8'] + .15, 540, 470, '+%d ÉCUS · %d CITOYENS' % (STATS['ecus'], STATS['citizens']), 'gold', 54, sub='MERCI POUR VOS LIKES', subk=.6)
        particles(L, t, t0, 540, 470, GOLD, 26, 500, 17)
    else:                                                     # abonne-toi (2 dernières secondes)
        sc, cx, cy = mv(t, t0, t1, (1.8, .36, .42), (2.1, .34, .4)); fr, P = view('P_barbichu', sc, cx, cy, 540, 860)
        fr = fr * (1 - .35 * ease((t - END['V9']) / .8))
        card(L, t, t0 + .05, 540, 470, 'ABONNE-TOI', 'green', 70, sub='= 1 CITOYEN DE PLUS', subk=.6)
    dust(L, t, red); caption(L, t)
    fr = np.clip(fr * vignette(), 0, 1)
    ui = np.asarray(L, dtype=np.float32) / 255; rgb = ui[..., [2, 1, 0]]; al = ui[..., 3:]
    out = fr * (1 - al) + rgb * al
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


if __name__ == '__main__':
    print('durée', round(TOTAL, 2), {k: round(v, 2) for k, v in T.items()})
    print('plans', [(round(a, 2), n) for a, n in CUTS])
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
