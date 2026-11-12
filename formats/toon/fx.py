"""FROMAGISTAN — effets visuels intégrés à la scène : lumière additive (la flamme éclaire le visage, le mur, le sol), feu en couches floutées
qui ondule et monte, braises, fumée, étincelles de magie, éclair d'allumage. Tout travaille directement sur l'image du monde (RGBA, échelle SS),
avant que la caméra ne la cadre : les effets bougent donc avec la scène, comme s'ils en faisaient partie."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from rig import W, H, SS


def _box(x, y, r):
    X, Y, R = x * SS, y * SS, r * SS
    return int(max(0, X - R)), int(max(0, Y - R)), int(min(W * SS, X + R)), int(min(H * SS, Y + R))


def glow(img, x, y, r, col, a=1.0, falloff=2.2, ry=None):
    """Lumière additive douce (centre (x, y), rayon r) : éclaircit ce qu'elle touche au lieu de poser un disque plein."""
    if a <= 0 or r <= 0: return
    ry = ry or r; x0, y0, x1, y1 = _box(x, y, max(r, ry))
    if x1 <= x0 or y1 <= y0: return
    reg = np.asarray(img.crop((x0, y0, x1, y1))).astype(np.float32)
    yy, xx = np.ogrid[y0:y1, x0:x1]; d = np.sqrt(((xx - x * SS) / (r * SS)) ** 2 + ((yy - y * SS) / (ry * SS)) ** 2)
    m = (np.clip(1 - d, 0, 1) ** falloff * a)[..., None]
    reg[..., :3] += m * np.array(col, np.float32); reg[..., 3:] = np.maximum(reg[..., 3:], m * 255)
    img.paste(Image.fromarray(np.clip(reg, 0, 255).astype(np.uint8), 'RGBA'), (x0, y0))


def tint(img, x, y, r, col, a=.5, falloff=1.5):
    """Teinte la lumière ambiante d'une zone (multiplie) : nuit bleutée, lumière chaude d'une flamme."""
    x0, y0, x1, y1 = _box(x, y, r)
    reg = np.asarray(img.crop((x0, y0, x1, y1))).astype(np.float32)
    yy, xx = np.ogrid[y0:y1, x0:x1]; d = np.sqrt((xx - x * SS) ** 2 + (yy - y * SS) ** 2) / (r * SS)
    m = (np.clip(1 - d, 0, 1) ** falloff * a)[..., None]; c = np.array(col, np.float32) / 255
    reg[..., :3] = reg[..., :3] * (1 - m) + reg[..., :3] * c * m
    img.paste(Image.fromarray(np.clip(reg, 0, 255).astype(np.uint8), 'RGBA'), (x0, y0))


def darken(img, k, col=(20, 18, 50)):
    """Assombrit toute l'image vers une couleur de nuit (k de 0 à 1)."""
    if k <= 0: return
    a = np.asarray(img).astype(np.float32); a[..., :3] = a[..., :3] * (1 - k) + np.array(col, np.float32) * k * (a[..., :3] / 255 * .6 + .4)
    img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def _noise(t, i, f=1.0): return math.sin(t * 7.3 * f + i * 1.9) * .5 + math.sin(t * 13.1 * f + i * 3.7) * .3 + math.sin(t * 3.1 * f + i * .7) * .2


def _tongue(d, x, y, w, h, t, i, scale, col, lean):
    """Une langue de flamme : base arrondie, pointe qui ondule de plus en plus vers le haut."""
    pts_l, pts_r = [], []; n = 14
    for k in range(n + 1):
        s = k / n; hh = h * scale; width = w * scale * (math.sin(math.pi * min(1, s * 1.15 + .02)) ** .75) * (1 - s) ** .35 * .5
        sway = (_noise(t, i) * .25 + lean) * w * s ** 1.6 + math.sin(t * 11 + i * 2 + s * 5) * w * .06 * s
        cy = y - s * hh; cx = x + sway
        pts_l.append(((cx - width) * SS, cy * SS)); pts_r.append(((cx + width) * SS, cy * SS))
    d.polygon(pts_l + pts_r[::-1], fill=col)


def fire(img, x, y, w, h, t, a=1.0, seed=0, n=6, lean=0.0, smoke=True, light=True):
    """Feu intégré : fumée floutée derrière, langues en 4 couches (rouge, orange, jaune, cœur blanc) adoucies par un flou, braises qui montent,
    et lumière orange qui éclaire tout autour. (x, y) = base du feu, w = largeur, h = hauteur, a = intensité de 0 à 1 (allumage, extinction)."""
    if a <= 0: return
    R = max(w, h) * 1.6; x0, y0, x1, y1 = _box(x, y - h * .5, R)
    if x1 <= x0 or y1 <= y0: return
    lay = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ox, oy = x0 / SS, y0 / SS
    if smoke:
        sm = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sm)
        for j in range(7):
            life = ((t * .55 + j / 7 + seed * .13) % 1.0); px = x - ox + math.sin(t * 1.3 + j) * w * .25 + (j - 3) * w * .05; py = y - oy - h * (.7 + life * 1.3); rr = w * (.18 + life * .4)
            ds.ellipse([(px - rr) * SS, (py - rr) * SS, (px + rr) * SS, (py + rr) * SS], fill=(70, 66, 72, int(90 * (1 - life) * a)))
        lay = Image.alpha_composite(lay, sm.filter(ImageFilter.GaussianBlur(10 * SS))); d = ImageDraw.Draw(lay)
    hh = h * a ** .5
    for scale, col in ((1.0, (200, 40, 24, 235)), (.8, (246, 110, 28, 245)), (.58, (255, 190, 50, 250)), (.32, (255, 246, 205, 255))):
        for i in range(n):
            u = (i - (n - 1) / 2) / max(1, n - 1); bx = x - ox + u * w * .62; ht = hh * (.55 + .45 * (1 - abs(u)) ** 1.2) * (.85 + .25 * (_noise(t, i + seed, 1.2) * .5 + .5))
            _tongue(d, bx, y - oy, w * .42, ht, t, i + seed, scale, col, lean)
    soft = lay.filter(ImageFilter.GaussianBlur(2.2 * SS)); lay = Image.alpha_composite(soft, lay.filter(ImageFilter.GaussianBlur(.8 * SS)))
    d = ImageDraw.Draw(lay)
    for j in range(14):                                                    # braises
        life = (t * .9 + j * .618 + seed * .31) % 1.0; ex = x - ox + (math.sin(j * 12.9) * .45 + math.sin(t * 3 + j) * .15 * life) * w; ey = y - oy - life * h * 1.9; rr = (3.5 - 2.5 * life) * SS
        if life < .95: d.ellipse([ex * SS - rr, ey * SS - rr, ex * SS + rr, ey * SS + rr], fill=(255, 200 - int(120 * life), 80, int(255 * (1 - life) * a)))
    img.alpha_composite(lay, (x0, y0))
    if light:
        fl = .85 + .15 * _noise(t, seed, 2.0)
        glow(img, x, y - h * .45, h * 2.4, (150, 70, 18), .55 * a * fl, falloff=1.6)          # lumière chaude sur le décor et le personnage
        glow(img, x, y - h * .35, h * .9, (120, 80, 30), .5 * a * fl, falloff=2.0)            # cœur lumineux


def candle(img, p, x, y, t, a=1.0):
    """Bougie : cire avec coulures, mèche, petite flamme vivante et halo chaud qui éclaire la pièce."""
    p.rect(x - 26, y, x + 26, y + 170, (246, 236, 210), r=10); p.rect(x + 8, y, x + 26, y + 170, (222, 208, 180), r=8)
    p.ell(x, y + 2, 26, 10, (255, 248, 228)); p.rect(x - 22, y, x - 12, y + 44, (255, 248, 228), r=5); p.rect(x + 6, y, x + 14, y + 30, (255, 248, 228), r=4)
    p.rect(x - 46, y + 160, x + 46, y + 186, (176, 132, 70), r=12); p.limb((x, y - 2), (x, y - 16), 4, (60, 50, 50))
    if a > 0:
        glow(img, x, y - 30, 760, (150, 88, 30), .62 * a * (.92 + .08 * _noise(t, 3, 2)), falloff=1.5)
        fire(img, x, y - 12, 26, 70 * (.6 + .4 * a), t, a, seed=5, n=2, smoke=False, light=False); glow(img, x, y - 40, 90, (140, 100, 40), .8 * a)


def sparkles(img, x, y, t, t0, r=160, col=(255, 230, 120), n=18, dur=.9, seed=0):
    """Gerbe d'étincelles magiques qui jaillissent puis retombent en scintillant."""
    u = (t - t0) / dur
    if not 0 <= u < 1: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(n):
        ang = i * 2.399 + seed; sp = r * (.5 + .5 * math.sin(i * 7.7 + seed) ** 2); px = x + math.cos(ang) * sp * u; py = y + math.sin(ang) * sp * u + 120 * u * u
        s = (9 - 6 * u) * (1 + .3 * math.sin(t * 30 + i)) * SS
        if s > 0: d.polygon([(px * SS, py * SS - s * 2), (px * SS + s * .5, py * SS - s * .5), (px * SS + s * 2, py * SS), (px * SS + s * .5, py * SS + s * .5), (px * SS, py * SS + s * 2), (px * SS - s * .5, py * SS + s * .5), (px * SS - s * 2, py * SS), (px * SS - s * .5, py * SS - s * .5)], fill=col + (int(255 * (1 - u)),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(.6 * SS))); glow(img, x, y, r * .9, tuple(int(c * .5) for c in col), .7 * (1 - u))


def bolt(img, p0, p1, t, t0, dur=.35, col=(190, 140, 255)):
    """Trait de magie du bâton vers la cible : traînée lumineuse floutée qui file en 0,35 s."""
    u = (t - t0) / dur
    if not 0 <= u < 1.2: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); pts = []
    for k in range(16):
        s = min(1, u) * k / 15; q = (p0[0] + (p1[0] - p0[0]) * s + math.sin(s * 9 + t * 20) * 18, p0[1] + (p1[1] - p0[1]) * s - math.sin(s * math.pi) * 140)
        pts.append((q[0] * SS, q[1] * SS))
    fade = 1 if u < 1 else (1.2 - u) / .2
    d.line(pts, fill=col + (int(220 * fade),), width=int(16 * SS), joint='curve'); d.line(pts, fill=(255, 255, 255, int(255 * fade)), width=int(5 * SS), joint='curve')
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3 * SS))); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(.8 * SS)))
    glow(img, pts[-1][0] / SS, pts[-1][1] / SS, 220, tuple(int(c * .55) for c in col), .8 * fade)


def flash(img, t, t0, col=(255, 240, 210), dur=.25, a=.55):
    """Éclair blanc bref sur toute l'image (allumage, explosion)."""
    u = (t - t0) / dur
    if 0 <= u < 1:
        k = a * (1 - u) ** 2; arr = np.asarray(img).astype(np.float32); arr[..., :3] = arr[..., :3] * (1 - k) + np.array(col, np.float32) * k
        img.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA'))
