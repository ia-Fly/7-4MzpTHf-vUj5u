"""Habillage du format CINE : écrans de téléphone, réveil LED, sous-titres, bandeau, carte de fin.
Tout est dessiné en code : texte net à 100 %, 0 crédit. Aucune marque, aucun logo, numéros fictifs (555-01xx)."""
import os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', '..', 'assets', 'fonts')
W, H = 1080, 1920
SIGNAL = (255, 75, 43)      # rouge signal (RGB)
MINT = (94, 245, 180)       # menthe
ICE = (150, 215, 255)       # bleu glacé : la voix au téléphone
PAPER = (240, 238, 230)
_cache = {}


def font(name, size, weight=None):
    k = (name, size, weight)
    if k not in _cache:
        f = ImageFont.truetype(os.path.join(FONTS, name), size)
        if weight is not None:
            axes = f.get_variation_axes(); vals = []
            for a in axes:
                n = a['name'].decode() if isinstance(a['name'], bytes) else a['name']
                vals.append(weight if n.lower() == 'weight' else a['default'])
            f.set_variation_by_axes(vals)
        _cache[k] = f
    return _cache[k]


def inter(size, weight=500): return font('Inter-VF.ttf', size, weight)
def mono(size, weight=500): return font('JetBrainsMono-VF.ttf', size, weight)
def condensed(size): return font('BarlowCondensed-ExtraBold.ttf', size)
def anton(size): return font('Anton-Regular.ttf', size)


def to_bgra(im):
    a = np.array(im.convert('RGBA'))
    return a[:, :, [2, 1, 0, 3]]


def over(frame, rgba, x=0, y=0):
    """Colle une couche BGRA (uint8) sur une image BGR (uint8), sur place."""
    h, w = rgba.shape[:2]; x0, y0 = max(0, x), max(0, y); x1, y1 = min(frame.shape[1], x + w), min(frame.shape[0], y + h)
    if x0 >= x1 or y0 >= y1: return frame
    r = rgba[y0 - y:y1 - y, x0 - x:x1 - x]; alpha = r[:, :, 3:4].astype(np.float32) / 255.0
    roi = frame[y0:y1, x0:x1, :3].astype(np.float32)
    frame[y0:y1, x0:x1, :3] = (roi * (1 - alpha) + r[:, :, :3].astype(np.float32) * alpha).astype(np.uint8)
    return frame


def centered(d, cx, y, txt, f, fill):
    b = d.textbbox((0, 0), txt, font=f); d.text((cx - (b[2] - b[0]) / 2 - b[0], y), txt, font=f, fill=fill)


def handset(d, cx, cy, s, fill, down=False):
    """Pictogramme de combiné dessiné à la main, sans glyphe de marque."""
    S = 4; im = Image.new('L', (int(s * 2 * S), int(s * 2 * S)), 0); dd = ImageDraw.Draw(im); c = s * S
    r = s * 0.92 * S; t = s * 0.32 * S
    dd.arc([c - r, c - r * 0.55, c + r, c + r * 1.25], 200, 340, fill=255, width=int(t))
    for sx in (-1, 1):
        x = c + sx * r * 0.80; y = c + r * 0.02; w = s * 0.40 * S; h = s * 0.30 * S
        dd.rounded_rectangle([x - w, y - h * 0.5, x + w, y + h], radius=int(h * 0.5), fill=255)
    im = im.rotate(135 if down else -35, resample=Image.BICUBIC).resize((int(s * 2), int(s * 2)), Image.LANCZOS)
    d._image.paste(Image.new('RGBA', im.size, fill), (int(cx - s), int(cy - s)), im)


def avatar(size, photo=None):
    S = 3; n = size * S
    if photo is not None:
        im = Image.fromarray(photo[:, :, ::-1]).convert('RGB'); m = min(im.size)
        im = im.crop(((im.width - m) // 2, (im.height - m) // 2, (im.width + m) // 2, (im.height + m) // 2)).resize((n, n), Image.LANCZOS).convert('RGBA')
    else:
        im = Image.new('RGBA', (n, n), (58, 64, 74, 255)); d = ImageDraw.Draw(im)
        d.ellipse([n * .34, n * .20, n * .66, n * .52], fill=(150, 158, 170, 255))
        d.ellipse([n * .16, n * .58, n * .84, n * 1.25], fill=(150, 158, 170, 255))
    mask = Image.new('L', (n, n), 0); ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
    out = Image.new('RGBA', (n, n), (0, 0, 0, 0)); out.paste(im, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


def screen_incoming(sw, sh, name, number, label='Incoming call', photo=None, ring=0.0):
    im = Image.new('RGBA', (sw, sh), (9, 12, 18, 255)); d = ImageDraw.Draw(im)
    for y in range(sh):
        v = y / sh; d.line([(0, y), (sw, y)], fill=(int(10 + 10 * (1 - v)), int(14 + 14 * (1 - v)), int(22 + 22 * (1 - v)), 255))
    cx = sw // 2; a = int(sw * .34); ay = int(sh * .205)
    for k in range(3):                                      # ondes de sonnerie
        p = (ring + k / 3) % 1; r = a / 2 + p * sw * .17; o = int(70 * (1 - p))
        d.ellipse([cx - r, ay + a / 2 - r, cx + r, ay + a / 2 + r], outline=(150, 215, 255, o), width=4)
    im.alpha_composite(avatar(a, photo), (cx - a // 2, ay)); d = ImageDraw.Draw(im)
    centered(d, cx, int(sh * .135), label, inter(int(sw * .05), 500), (170, 178, 190, 255))
    centered(d, cx, int(sh * .41), name, inter(int(sw * .155), 600), (250, 250, 250, 255))
    if number: centered(d, cx, int(sh * .515), number, inter(int(sw * .052), 400), (160, 168, 180, 255))
    r = int(sw * .105); by = int(sh * .80)
    for bx, col, down, lab in ((sw * .26, (232, 62, 54, 255), True, 'Decline'), (sw * .74, (52, 199, 89, 255), False, 'Accept')):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col); handset(d, bx, by, r * .62, (255, 255, 255, 255), down)
        centered(d, bx, by + r + int(sh * .016), lab, inter(int(sw * .04), 500), (200, 205, 214, 255))
    return im


def screen_ink(sw, sh, name, label='Incoming call', number=''):
    """Écran d'appel clair à coller sur un vrai téléphone filmé : l'écran reste lumineux, seule « l'encre » est ajoutée."""
    im = Image.new('RGBA', (sw, sh), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx = sw // 2; ink = (8, 16, 28, 245)
    centered(d, cx, int(sh * .10), label, inter(int(sw * .075), 600), (20, 34, 52, 230))
    centered(d, cx, int(sh * .22), name, inter(int(sw * .27), 700), ink)
    if number: centered(d, cx, int(sh * .46), number, inter(int(sw * .07), 500), (20, 34, 52, 220))
    r = int(sw * .125); by = int(sh * .80)
    for bx, col, down in ((sw * .26, (214, 40, 36, 255), True), (sw * .74, (28, 168, 70, 255), False)):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col); handset(d, bx, by, r * .62, (255, 255, 255, 255), down)
    return to_bgra(im)


def screen_active(sw, sh, name, elapsed, env=None, ended=False):
    im = Image.new('RGBA', (sw, sh), (7, 9, 13, 255)); d = ImageDraw.Draw(im); cx = sw // 2
    centered(d, cx, int(sh * .15), name, inter(int(sw * .12), 600), (250, 250, 250, 255))
    if ended:
        centered(d, cx, int(sh * .245), 'Call ended', inter(int(sw * .058), 500), (232, 62, 54, 255))
    else:
        centered(d, cx, int(sh * .245), f'{int(elapsed) // 60:02d}:{int(elapsed) % 60:02d}', mono(int(sw * .058), 500), (170, 178, 190, 255))
    n = 34; gap = (sw * .84) / n; bw = gap * .46; x0 = sw * .08; my = sh * .50
    for i in range(n):
        v = 0.02 if env is None else float(env[i % len(env)]) if not ended else 0.0
        h = max(4, v * sh * .13); x = x0 + i * gap
        d.rounded_rectangle([x, my - h, x + bw, my + h], radius=int(bw / 2), fill=(150, 215, 255, 235) if not ended else (70, 76, 86, 255))
    return im


def phone_on(bg, screen, t=0.0, vibrate=0.0, tilt=0.0, scale=1.0, brightness=1.0):
    """Gros plan de téléphone : l'écran posé en très légère perspective sur un fond sombre flou, avec reflet de vitre."""
    frame = bg.copy(); sw, sh = screen.size; s = to_bgra(screen)
    if brightness < 1: s[:, :, :3] = (s[:, :, :3].astype(np.float32) * brightness).astype(np.uint8)
    # coins arrondis et bord de téléphone
    S = 2; pad = 22; PW, PH = sw + pad * 2, sh + pad * 2
    body = Image.new('RGBA', (PW * S, PH * S), (0, 0, 0, 0)); dr = ImageDraw.Draw(body)
    dr.rounded_rectangle([0, 0, PW * S - 1, PH * S - 1], radius=96 * S, fill=(17, 18, 22, 255), outline=(62, 66, 74, 255), width=3 * S)
    body = to_bgra(body.resize((PW, PH), Image.LANCZOS))
    mask = Image.new('L', (sw * S, sh * S), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw * S - 1, sh * S - 1], radius=74 * S, fill=255)
    mask = np.array(mask.resize((sw, sh), Image.LANCZOS)).astype(np.float32) / 255; s[:, :, 3] = (s[:, :, 3] * mask).astype(np.uint8)
    over(body, s, pad, pad)
    # reflet de vitre qui glisse
    g = np.zeros((PH, PW, 4), np.uint8); yy, xx = np.mgrid[0:PH, 0:PW]
    d = (xx * .55 + yy * .35 - ((t * 70) % (PW + PH))) / 180.0
    g[:, :, :3] = 255; g[:, :, 3] = (np.clip(np.exp(-d * d), 0, 1) * 14 * (body[:, :, 3] / 255.0)).astype(np.uint8)
    over(body, g, 0, 0)
    # perspective légère + vibration
    jx = vibrate * (math.sin(t * 190) * 3.6 + math.sin(t * 121) * 2.2); jy = vibrate * math.sin(t * 157) * 2.4
    ws = (W * .86 / PW) * scale; dw, dh = PW * ws, PH * ws; cx, cy = W / 2 + jx, H * .50 + jy
    k = tilt * dw
    src = np.float32([[0, 0], [PW, 0], [PW, PH], [0, PH]])
    dst = np.float32([[cx - dw / 2 + k, cy - dh / 2 + k * .3], [cx + dw / 2 - k, cy - dh / 2 - k * .3],
                      [cx + dw / 2 + k * .3, cy + dh / 2 + k * .2], [cx - dw / 2 - k * .3, cy + dh / 2 - k * .2]])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(body, M, (W, H), flags=cv2.INTER_AREA if ws < .8 else cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    return over(frame, warped)


def glue_on_quad(frame, screen_rgba, quad, opacity=1.0):
    """Colle un écran dessiné sur l'écran réel du téléphone dans un plan (quad = 4 coins en px de la sortie 1080×1920)."""
    sh, sw = screen_rgba.shape[:2]; src = np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]])
    M = cv2.getPerspectiveTransform(src, np.float32(quad))
    wr = cv2.warpPerspective(screen_rgba, M, (W, H), flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
    if opacity < 1: wr[:, :, 3] = (wr[:, :, 3] * opacity).astype(np.uint8)
    return over(frame, wr)


# ---------- réveil LED ----------
SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abfgcd'}


def _digit(d, x, y, w, h, t, ch, on, off):
    g = t * .18
    segs = {'a': [(x + g, y), (x + w - g, y), (x + w - t - g, y + t), (x + t + g, y + t)],
            'd': [(x + t + g, y + h - t), (x + w - t - g, y + h - t), (x + w - g, y + h), (x + g, y + h)],
            'g': [(x + t, y + h / 2 - t / 2), (x + w - t, y + h / 2 - t / 2), (x + w - g, y + h / 2), (x + w - t, y + h / 2 + t / 2), (x + t, y + h / 2 + t / 2), (x + g, y + h / 2)],
            'f': [(x, y + g), (x + t, y + t + g), (x + t, y + h / 2 - t / 2 - g), (x, y + h / 2 - g)],
            'b': [(x + w, y + g), (x + w, y + h / 2 - g), (x + w - t, y + h / 2 - t / 2 - g), (x + w - t, y + t + g)],
            'e': [(x, y + h / 2 + g), (x + t, y + h / 2 + t / 2 + g), (x + t, y + h - t - g), (x, y + h - g)],
            'c': [(x + w, y + h / 2 + g), (x + w, y + h - g), (x + w - t, y + h - t - g), (x + w - t, y + h / 2 + t / 2 + g)]}
    for k, p in segs.items(): d.polygon(p, fill=on if k in SEG[ch] else off)


def led_clock(txt, t=0.0, red=(255, 28, 18)):
    """Réveil à segments rouges avec halo : l'heure en gros, plein cadre."""
    im = Image.new('RGB', (W, H), (4, 3, 3)); d = ImageDraw.Draw(im)
    h, m = txt.split(':'); w = 210; hh = 390; th = 40; sp = 44
    total = (w if len(h) == 1 else w * 2 + sp) + 90 + w * 2 + sp; x = (W - total) / 2; y = (H - hh) / 2 - 80
    off = (22, 7, 6)
    for ch in h: _digit(d, x, y, w, hh, th, ch, red, off); x += w + sp
    x -= sp
    d.ellipse([x + 32, y + hh * .28, x + 62, y + hh * .28 + 30], fill=red); d.ellipse([x + 32, y + hh * .66, x + 62, y + hh * .66 + 30], fill=red); x += 94
    for ch in m: _digit(d, x, y, w, hh, th, ch, red, off); x += w + sp
    a = np.array(im)[:, :, ::-1].astype(np.float32)
    glow = cv2.GaussianBlur(a, (0, 0), 26) * .9 + cv2.GaussianBlur(a, (0, 0), 90) * .9
    out = np.clip(a * .92 + glow, 0, 255)
    # reflet flou sous le réveil
    ry = int(y + hh + 40); refl = cv2.GaussianBlur(a[int(y):int(y + hh), :][::-1], (0, 0), 14) * .13
    n = min(refl.shape[0], H - ry); fade = np.linspace(1, 0, n)[:, None, None]; out[ry:ry + n] = np.clip(out[ry:ry + n] + refl[:n] * fade, 0, 255)
    return out.astype(np.uint8)


# ---------- sous-titres et bandeau ----------
def caption_layer(words, active, keywords=(), accent=SIGNAL, size=98, max_w=860, dim=(255, 255, 255, 120)):
    """Groupe de 1 à 3 mots : déjà dits en blanc, mot en cours pleine lumière, mot-clé coloré, à venir atténués."""
    size_ = size
    while True:
        f = condensed(size_); sp = int(size_ * .24); ws = [f.getbbox(w)[2] - f.getbbox(w)[0] for w in words]
        if sum(ws) + sp * (len(words) - 1) <= max_w or size_ < 56: break
        size_ -= 4
    tot = sum(ws) + sp * (len(words) - 1); pad = 40; Wd, Hd = tot + pad * 2, int(size_ * 1.5) + pad
    im = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); sh = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); d = ImageDraw.Draw(im)
    x = pad; y = pad // 2
    for i, w in enumerate(words):
        ds.text((x, y + 3), w, font=f, fill=(0, 0, 0, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
        x += ws[i] + sp
    sh = sh.filter(ImageFilter.GaussianBlur(7)); im.alpha_composite(sh); im.alpha_composite(sh); d = ImageDraw.Draw(im)
    x = pad
    for i, w in enumerate(words):
        col = accent + (255,) if w.strip(".,?!…'’").upper() in keywords and i <= active else (255, 255, 255, 255) if i <= active else dim
        d.text((x, y), w, font=f, fill=col, stroke_width=2, stroke_fill=(0, 0, 0, 200)); x += ws[i] + sp
    return to_bgra(im)


def hud_layer(left, right, blink=True, line_open=False):
    """Bandeau du haut, repère visible jusqu'à la fin (zone 10-14 % de la hauteur)."""
    im = Image.new('RGBA', (W, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = mono(32, 600); y = 22; x = 78
    d.ellipse([x, y + 10, x + 18, y + 28], fill=(SIGNAL + (255,)) if blink else (120, 40, 30, 255)); x += 34
    d.text((x, y), left, font=f, fill=(255, 255, 255, 225)); b = d.textbbox((0, 0), right, font=f)
    d.text((W - 110 - (b[2] - b[0]), y), right, font=f, fill=(ICE + (235,)) if line_open else (255, 255, 255, 225))
    sh = im.filter(ImageFilter.GaussianBlur(5)); base = Image.new('RGBA', (W, 90), (0, 0, 0, 0))
    a = np.array(sh); a[:, :, :3] = 0; a[:, :, 3] = np.clip(a[:, :, 3].astype(np.int32) * 2, 0, 255); base = Image.fromarray(a, 'RGBA')
    base.alpha_composite(im); return to_bgra(base)


def wave_layer(env, label='ON THE LINE'):
    """Petite onde réactive sous laquelle s'affiche la voix au téléphone."""
    n = 26; bw = 9; gap = 8; hmax = 44; Wd = n * (bw + gap); Hd = hmax * 2 + 46
    im = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    centered(d, Wd / 2, 0, label, mono(24, 600), ICE + (235,))
    for i in range(n):
        v = float(env[i % len(env)]); h = max(3, v * hmax); x = i * (bw + gap); my = 46 + hmax
        d.rounded_rectangle([x, my - h, x + bw, my + h], radius=4, fill=ICE + (235,))
    return to_bgra(im)


def end_card(bg, a, b, question, cta1, cta2, t=0.0):
    """Le choix en 2 mots : deux boutons, l'appel au vote et l'abonnement."""
    frame = (bg.astype(np.float32) * .34).astype(np.uint8)
    p = min(1.0, t / .22); ease = 1 - (1 - p) ** 3
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    centered(d, W / 2, 468, question, condensed(92), (255, 255, 255, int(255 * ease)))
    bw, bh, by = 780, 210, 640; x = (W - bw) / 2
    for i, (lab, col) in enumerate(((a, MINT), (b, SIGNAL))):
        pulse = .5 + .5 * math.sin(t * 5.2 + i * math.pi); y = by + i * (bh + 44) + (1 - ease) * 40
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=30, fill=col + (int(40 + 40 * pulse),), outline=col + (int(255 * ease),), width=7)
        f = anton(112); bb = d.textbbox((0, 0), lab, font=f); d.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0], y + (bh - (bb[3] - bb[1])) / 2 - bb[1]), lab, font=f, fill=(255, 255, 255, int(255 * ease)))
    centered(d, W / 2, 1160, cta1, condensed(66), (255, 255, 255, int(255 * ease)))
    centered(d, W / 2, 1240, cta2, mono(32, 600), (225, 228, 232, int(235 * ease)))
    return over(frame, to_bgra(im))
