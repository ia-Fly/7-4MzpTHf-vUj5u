"""FROMAGISTAN — personnages dessinés en code (aplats de couleur, sans contour, grosses têtes rondes) et animés : respiration, clignement, bras, marche, bouche.
    python3 formats/toon/rig.py OUT_DIR   -> maquette.png (planche) et test.mp4 (6 s d'animation)
Tout est vectoriel (PIL, rendu ×2 puis réduit) : 0 crédit, personnages identiques d'un épisode à l'autre."""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, SS, FPS = 1080, 1920, 2, 30
HERE = os.path.dirname(os.path.abspath(__file__)); FONTS = os.path.join(HERE, '..', '..', 'assets', 'fonts')
SKIN, SKIN2 = (250, 205, 170), (238, 180, 150)
SHADOW = (98, 86, 92)                                  # ombre au sol : couleur pleine (PIL n'additionne pas la transparence)


def font(size, name='Anton-Regular.ttf'): return ImageFont.truetype(os.path.join(FONTS, name), size * SS)


class Pen:
    """Petites formes à plat, coordonnées en pixels finaux (multipliées par SS au tracé)."""
    def __init__(self, img): self.d = ImageDraw.Draw(img)
    def circ(self, x, y, r, c): self.ell(x, y, r, r, c)
    def ell(self, x, y, rx, ry, c): self.d.ellipse([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], fill=c)
    def rect(self, x0, y0, x1, y1, c, r=0): self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=c)
    def poly(self, pts, c): self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=c)
    def limb(self, p0, p1, w, c):
        self.d.line([(p0[0] * SS, p0[1] * SS), (p1[0] * SS, p1[1] * SS)], fill=c, width=int(w * SS)); self.circ(*p0, w / 2, c); self.circ(*p1, w / 2, c)
    def arc(self, x, y, rx, ry, a0, a1, c, w): self.d.arc([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], a0, a1, fill=c, width=int(w * SS))
    def text(self, x, y, s, f, c, anchor='mm'): self.d.text((x * SS, y * SS), s, font=f, fill=c, anchor=anchor)
    def star(self, x, y, r, c):
        self.poly([(x + (r if i % 2 == 0 else r * .45) * math.sin(i * math.pi / 5), y - (r if i % 2 == 0 else r * .45) * math.cos(i * math.pi / 5)) for i in range(10)], c)


def at(p, ang, L): return (p[0] + L * math.sin(ang), p[1] + L * math.cos(ang))           # angle 0 = vers le bas, positif = vers la droite


def face(p, x, y, r, t, talk=False, mood='happy', glasses=None, brow=None, blink_off=0.0):
    """Yeux (clignent toutes les 3 s environ), sourcils, bouche (s'ouvre quand le personnage parle)."""
    blink = ((t + blink_off) % 3.1) < .12; ex, ey = r * .36, -r * .02
    for s in (-1, 1):
        cx = x + s * ex
        if mood == 'happy' or blink: p.arc(cx, y + ey + r * .06, r * .15, r * .13, 200, 340, (60, 40, 40), r * .055)
        elif mood == 'bored': p.circ(cx, y + ey, r * .1, (50, 40, 40)); p.rect(cx - r * .16, y + ey - r * .16, cx + r * .16, y + ey - r * .01, SKIN if brow is None else brow)
        else: p.circ(cx, y + ey, r * .095, (50, 40, 40))
        if glasses: p.arc(cx, y + ey, r * .27, r * .27, 0, 360, glasses, r * .06)
    if glasses: p.limb((x - ex + r * .27, y + ey), (x + ex - r * .27, y + ey), r * .05, glasses)
    my = y + r * .42
    if talk and math.sin(t * 22) > -.2: p.ell(x, my, r * .15, r * (.07 + .09 * abs(math.sin(t * 13))), (120, 40, 50))
    elif mood == 'smug': p.arc(x + r * .08, my - r * .14, r * .2, r * .16, 20, 120, (150, 50, 60), r * .06)
    else: p.arc(x, my - r * .16, r * .22, r * .18, 20, 160, (190, 50, 70), r * .07)


def arm(p, sh, ang, L, w, col, hand=SKIN, bend=0.0):
    el = at(sh, ang, L * .5); ha = at(el, ang + bend, L * .5); p.limb(sh, el, w, col); p.limb(el, ha, w, col); p.circ(*ha, w * .62, hand); return ha


def acts(t, action):
    """Angles des bras, rebond et pas, selon l'action."""
    bob = 5 * math.sin(t * 3.2); la, ra, lb, rb, step = -.25, .25, 0, 0, 0
    if action == 'wave': ra, rb = 2.35 + .35 * math.sin(t * 9), .5
    elif action == 'cheer': la, ra, lb, rb = -2.5 + .2 * math.sin(t * 8), 2.5 - .2 * math.sin(t * 8), -.3, .3; bob = 14 * abs(math.sin(t * 6))
    elif action == 'talk': ra, rb = 1.1 + .25 * math.sin(t * 5), 1.0; la = -.35 + .08 * math.sin(t * 4)
    elif action == 'walk': step = math.sin(t * 8); la, ra = -.25 + .5 * step, .25 + .5 * step; bob = 6 * abs(math.cos(t * 8))
    return bob, la, ra, lb, rb, step


def human(p, x, g, s, t, action='idle', body=(60, 130, 220), legs=(40, 50, 90), hair=None, head_extra=None, mood='happy', talk=False, tall=1.0, prop=None, glasses=None, off=0.0):
    """Personnage standard : grosse tête ronde, corps en capuche, bras et jambes ronds. g = hauteur du sol."""
    bob, la, ra, lb, rb, step = acts(t + off, action); r = 105 * s; bh, bw = 190 * s * tall, 150 * s; leg = 130 * s * tall
    hip = g - leg; top = hip - bh + bob * s; hy = top - r * .78
    p.ell(x, g + 8 * s, 150 * s, 20 * s, SHADOW)
    for sgn in (-1, 1):
        fx = x + sgn * 38 * s + (sgn * step * 26 * s if action == 'walk' else 0); fy = g - (max(0, sgn * step) * 16 * s if action == 'walk' else 0)
        p.limb((x + sgn * 36 * s, hip - 10 * s), (fx, fy - 14 * s), 44 * s, legs); p.ell(fx + 8 * s, fy - 6 * s, 40 * s, 18 * s, (245, 245, 250))
    p.rect(x - bw / 2, top, x + bw / 2, hip + 12 * s, body, r=46 * s)
    p.poly([(x - bw * .3, hip - 60 * s), (x + bw * .3, hip - 60 * s), (x + bw * .3, hip - 14 * s), (x - bw * .3, hip - 14 * s)], tuple(max(0, c - 22) for c in body))   # poche
    for sgn in (-1, 1): p.limb((x + sgn * 16 * s, top + 34 * s), (x + sgn * 16 * s, top + 78 * s), 6 * s, (255, 255, 255))                                     # cordons
    lh = arm(p, (x - bw / 2 + 14 * s, top + 40 * s), la, 150 * s * tall, 46 * s, body, bend=lb); rh = arm(p, (x + bw / 2 - 14 * s, top + 40 * s), ra, 150 * s * tall, 46 * s, body, bend=rb)
    for sgn in (-1, 1): p.circ(x + sgn * r * .97, hy + r * .1, r * .2, SKIN2)
    if hair: hair(p, x, hy, r, 'back')
    p.circ(x, hy, r, SKIN)
    if hair: hair(p, x, hy, r, 'front')
    face(p, x, hy, r, t, talk, mood, glasses, blink_off=off)
    if head_extra: head_extra(p, x, hy, r)
    if prop: prop(p, lh, rh, s)
    return dict(head=(x, hy, r), lh=lh, rh=rh)


# ---- les quatre personnages ----
def barbichu(p, x, g, s, t, action='idle', talk=False):
    """Président Barbichu : mage petit et rond, robe violette étoilée, barbe tressée, lunettes rondes, bonnet à pompon, écharpe jaune, bâton à coq."""
    bob, la, ra, lb, rb, step = acts(t, action); r = 112 * s; V, V2, Y = (125, 80, 200), (100, 60, 170), (255, 205, 60)
    top = g - 250 * s + bob * s; hy = top - r * .62; sway = (step * 10 * s) if action == 'walk' else 0
    p.ell(x, g + 8 * s, 170 * s, 22 * s, SHADOW)
    for sgn in (-1, 1): p.ell(x + sgn * 55 * s + sgn * sway, g - 8 * s, 44 * s, 20 * s, (90, 60, 40))
    p.poly([(x - 95 * s, top + 30 * s), (x + 95 * s, top + 30 * s), (x + 150 * s, g - 14 * s), (x - 150 * s, g - 14 * s)], V); p.ell(x, g - 14 * s, 150 * s, 22 * s, V); p.circ(x, top + 60 * s, 96 * s, V)
    for sx, sy, sr in ((-70, 120, 13), (60, 150, 11), (-20, 190, 9), (95, 215, 12), (-105, 215, 10), (20, 110, 8)): p.star(x + sx * s, top + sy * s, sr * s, Y)
    p.poly([(x - 100 * s, top + 40 * s), (x - 70 * s, top + 22 * s), (x + 125 * s, g - 70 * s), (x + 110 * s, g - 30 * s)], Y)                                    # écharpe
    staff_top = (x - 190 * s, top - 150 * s + bob * s)
    lh = arm(p, (x - 86 * s, top + 60 * s), -.9, 120 * s, 50 * s, V); p.limb(staff_top, (lh[0] - 6 * s, g - 6 * s), 16 * s, (140, 90, 50))
    p.ell(staff_top[0], staff_top[1] - 30 * s, 30 * s, 26 * s, Y); p.circ(staff_top[0] + 22 * s, staff_top[1] - 52 * s, 16 * s, Y); p.poly([(staff_top[0] + 36 * s, staff_top[1] - 54 * s), (staff_top[0] + 54 * s, staff_top[1] - 48 * s), (staff_top[0] + 36 * s, staff_top[1] - 42 * s)], (240, 140, 40))
    for k in range(3): p.circ(staff_top[0] + (14 + k * 8) * s, staff_top[1] - 70 * s, 7 * s, (230, 60, 60))                                                        # crête du coq
    p.circ(lh[0], lh[1], 30 * s, SKIN)
    rh = arm(p, (x + 86 * s, top + 60 * s), ra if action != 'idle' else .5, 130 * s, 50 * s, V, bend=rb)
    for sgn in (-1, 1): p.circ(x + sgn * r * .97, hy + r * .1, r * .2, SKIN2)
    p.circ(x, hy, r, SKIN)
    p.ell(x, hy + r * .78, r * .86, r * .7, (255, 255, 255)); p.poly([(x - r * .3, hy + r * 1.3), (x + r * .3, hy + r * 1.3), (x, hy + r * 2.15)], (255, 255, 255))   # barbe
    for k in range(3): p.limb((x - r * .2, hy + r * (1.42 + k * .2)), (x + r * .2, hy + r * (1.5 + k * .2)), 5 * s, (215, 220, 235))                             # tresse
    p.circ(x, hy + r * 2.12, r * .1, Y)
    p.ell(x, hy + r * .4, r * .4, r * .16, (255, 255, 255)); p.circ(x, hy + r * .22, r * .13, (245, 150, 140))                                                   # moustache, nez
    face(p, x, hy - r * .05, r, t, talk, 'happy', glasses=(70, 50, 60)); p.ell(x, hy + r * .4, r * .4, r * .15, (255, 255, 255))
    if talk and math.sin(t * 22) > -.2: p.ell(x, hy + r * .58, r * .13, r * (.05 + .07 * abs(math.sin(t * 13))), (120, 40, 50))
    tip = (x + r * 1.15 + 14 * s * math.sin(t * 3), hy - r * 1.25)
    p.poly([(x - r * 1.02, hy - r * .42), (x + r * 1.02, hy - r * .42), (x + r * .5, hy - r * 1.5), tip]) if False else p.poly([(x - r * 1.02, hy - r * .42), (x + r * 1.02, hy - r * .42), tip, (x + r * .2, hy - r * 1.75)], V)
    p.rect(x - r * 1.08, hy - r * .6, x + r * 1.08, hy - r * .32, V2, r=r * .14); p.circ(*tip, r * .2, (255, 255, 255))
    for sx, sy in ((-.45, -.85), (.25, -1.2), (.55, -.75)): p.star(x + sx * r, hy + sy * r, r * .1, Y)
    return dict(head=(x, hy, r), rh=rh)


def pigeon(p, x, g, s, t, action='idle', talk=False):
    """Le pigeon conseiller : gris, blasé, cravate rouge, bloc-notes."""
    bob, la, ra, lb, rb, step = acts(t + 1.3, action); G, G2 = (150, 155, 170), (120, 125, 142); by = g - 170 * s + bob * s; hy = by - 175 * s
    p.ell(x, g + 6 * s, 130 * s, 18 * s, SHADOW)
    for sgn in (-1, 1):
        p.limb((x + sgn * 36 * s, g - 60 * s), (x + sgn * 36 * s, g - 12 * s), 12 * s, (240, 140, 50)); p.ell(x + sgn * 44 * s, g - 8 * s, 30 * s, 10 * s, (240, 140, 50))
    p.ell(x, by, 120 * s, 150 * s, G); p.ell(x, by + 30 * s, 84 * s, 104 * s, (225, 228, 236))
    p.poly([(x - 16 * s, by - 96 * s), (x + 16 * s, by - 96 * s), (x + 22 * s, by - 20 * s), (x, by + 6 * s), (x - 22 * s, by - 20 * s)], (225, 55, 60)); p.circ(x, by - 100 * s, 18 * s, (200, 45, 50))
    p.poly([(x - 112 * s, by - 60 * s), (x - 150 * s - 20 * s * math.sin(t * 3), by + 70 * s), (x - 92 * s, by + 60 * s)], G2)                                     # aile gauche
    wa = ra if action != 'idle' else .9; w1 = at((x + 104 * s, by - 50 * s), wa, 120 * s); p.limb((x + 104 * s, by - 50 * s), w1, 50 * s, G2)
    p.rect(w1[0] - 46 * s, w1[1] - 70 * s, w1[0] + 46 * s, w1[1] + 46 * s, (175, 120, 70), r=8 * s); p.rect(w1[0] - 36 * s, w1[1] - 52 * s, w1[0] + 36 * s, w1[1] + 38 * s, (255, 255, 255), r=4 * s)
    for k in range(3): p.rect(w1[0] - 26 * s, w1[1] - (36 - k * 24) * s, w1[0] + 26 * s, w1[1] - (30 - k * 24) * s, (190, 195, 205))
    p.circ(x, hy, 86 * s, G); p.poly([(x - 14 * s, hy - 80 * s), (x + 14 * s, hy - 80 * s), (x, hy - 112 * s)], G)
    p.poly([(x - 20 * s, hy + 12 * s), (x + 20 * s, hy + 12 * s), (x, hy + (48 + (10 * abs(math.sin(t * 13)) if talk else 0)) * s)], (245, 150, 50))
    blink = ((t + .7) % 3.4) < .12
    for sgn in (-1, 1):
        p.circ(x + sgn * 34 * s, hy - 10 * s, 20 * s, (255, 255, 255)); p.circ(x + sgn * 34 * s, hy - 6 * s, 9 * s, (40, 40, 50))
        p.rect(x + sgn * 34 * s - 22 * s, hy - 32 * s, x + sgn * 34 * s + 22 * s, hy - (12 if not blink else -10) * s, G2, r=6 * s)                            # paupières lourdes
    return dict(head=(x, hy, 86 * s))


def rival(p, x, g, s, t, action='idle', talk=False):
    """Le rival : grand, maigre, manteau gris, cheveux vert sombre plaqués, monocle."""
    def hair(p, x, y, r, layer):
        if layer == 'front': p.poly([(x - r * 1.0, y - r * .25), (x - r * .75, y - r * .98), (x + r * .55, y - r * 1.12), (x + r * 1.0, y - r * .3), (x + r * .45, y - r * .62), (x - r * .55, y - r * .5)], (30, 85, 65))
    def extra(p, x, y, r):
        p.arc(x + r * .36, y - r * .02, r * .3, r * .3, 0, 360, (230, 190, 70), r * .07); p.limb((x + r * .6, y + r * .2), (x + r * .75, y + r * .95), r * .03, (230, 190, 70))
    return human(p, x, g, s * .88, t, action, body=(130, 135, 150), legs=(55, 60, 75), hair=hair, head_extra=extra, mood='smug', talk=talk, tall=1.5, off=2.1)


def reporter(p, x, g, s, t, action='talk', talk=True):
    """La reporter de Fromagistan Info : cheveux roux bouclés, veste bleue, micro géant."""
    def hair(p, x, y, r, layer):
        pts = [(-1.0, -.1), (-.95, -.6), (-.6, -.98), (-.15, -1.15), (.35, -1.1), (.75, -.85), (1.0, -.4), (1.02, .1)] if layer == 'back' else [(-.7, -.72), (-.3, -.9), (.15, -.92), (.55, -.78)]
        for hx, hyy in pts: p.circ(x + hx * r, y + hyy * r, r * (.42 if layer == 'back' else .3), (245, 120, 40))
    def mic(p, lh, rh, s):
        p.limb(rh, (rh[0] + 10 * s, rh[1] - 90 * s), 22 * s, (70, 70, 80)); p.ell(rh[0] + 12 * s, rh[1] - 140 * s, 50 * s, 60 * s, (60, 60, 70)); p.ell(rh[0] + 12 * s, rh[1] - 150 * s, 36 * s, 40 * s, (95, 95, 108)); p.circ(*rh, 28 * s, SKIN)
    return human(p, x, g, s * .95, t, action, body=(50, 120, 230), legs=(40, 45, 80), hair=hair, mood='happy', talk=talk, prop=mic, off=.9)


def citizen(p, x, g, s, t, col, action='cheer', off=0.0):
    def hair(p, x, y, r, layer):
        if layer == 'front': p.poly([(x - r * .98, y - r * .3), (x - r * .7, y - r * .95), (x - r * .1, y - r * 1.2), (x + r * .2, y - r * .95), (x + r * .6, y - r * 1.05), (x + r * .98, y - r * .3), (x + r * .3, y - r * .6), (x - r * .5, y - r * .55)], (50, 60, 120))
    return human(p, x, g, s, t, action, body=col, legs=(40, 45, 90), hair=hair, off=off)


# ---- décor et interface ----
def background(t):
    img = Image.new('RGBA', (W * SS, H * SS)); p = Pen(img); d = p.d
    for y in range(0, H * SS, 4):
        k = y / (H * SS); d.rectangle([0, y, W * SS, y + 4], fill=(int(120 + 110 * k), int(190 + 40 * k), int(250 - 20 * k)))
    p.circ(860, 330, 150, (190, 222, 250)); p.circ(860, 330, 110, (255, 245, 200))
    for cx, cy, sc in ((220 + 30 * math.sin(t * .3), 420, 1.0), (640 + 40 * math.sin(t * .25 + 1), 250, .7)):
        for dx, dy, rr in ((0, 0, 60), (70, 10, 48), (-70, 14, 44), (20, -30, 46)): p.circ(cx + dx * sc, cy + dy * sc, rr * sc, (255, 255, 255))
    p.ell(200, 1420, 620, 300, (130, 200, 120)); p.ell(900, 1440, 560, 260, (110, 185, 110)); p.rect(0, 1380, W, H, (150, 210, 130))
    # palais en ruine : colonnes, fronton, demi-toit
    C, C2 = (250, 238, 210), (228, 212, 180)
    p.rect(170, 800, 910, 1400, C, r=10); p.rect(140, 1380, 940, 1420, C2, r=8)
    for k in range(5): p.rect(215 + k * 140, 880, 265 + k * 140, 1380, C2, r=10)
    p.poly([(140, 800), (540, 600), (940, 800)], (205, 90, 80)); p.poly([(540, 600), (940, 800), (700, 800), (600, 700), (660, 640)], (120, 190, 240))    # toit à moitié parti
    p.rect(470, 1140, 610, 1380, (140, 95, 60), r=60); p.circ(585, 1270, 9, (240, 200, 80))
    p.limb((540, 600), (540, 500), 8, (120, 90, 60)); p.poly([(544, 500), (650 + 10 * math.sin(t * 4), 520), (544, 548)], (255, 205, 60))                    # drapeau jaune fromage
    p.rect(0, 1560, W, H, (120, 105, 110)); p.rect(0, 1540, W, 1570, (140, 125, 130))
    return img


def gauge(p, x, y, label, val, col, w=300):
    p.rect(x, y, x + w, y + 46, (40, 40, 60), r=23); p.rect(x + 5, y + 5, x + 5 + (w - 10) * max(.06, min(1, val)), y + 41, col, r=18)
    p.text(x + w / 2, y + 80, label, font(34), (255, 255, 255)); p.d.text(((x + w / 2) * SS, (y + 80) * SS), label, font=font(34), fill=(255, 255, 255), anchor='mm', stroke_width=5 * SS, stroke_fill=(30, 30, 50))


def banner(p, x, y, s, f, bg, fg=(255, 255, 255), rot=0):
    l, t0, r, b = p.d.textbbox((0, 0), s, font=f); w = (r - l) / SS + 50; h = (b - t0) / SS + 34
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, bg, r=6); p.text(x, y, s, f, fg)


def frame(t):
    img = background(t); p = Pen(img); g = 1700
    cols = [(230, 80, 80), (70, 150, 230), (250, 200, 60), (90, 190, 110)]
    for k, cx in enumerate((90, 990)): citizen(p, cx, g + 150, .62, t, cols[k], 'cheer', off=k * 1.7)
    rival(p, 960, g - 150, .7, t, 'idle'); pigeon(p, 190, g - 20, .8, t, 'talk' if 2 < t < 4 else 'idle', talk=2 < t < 4)
    reporter(p, 770, g + 70, .8, t, 'talk', talk=t >= 4)
    act = 'walk' if t < 1 else ('wave' if t < 2 else ('talk' if t < 4 else 'cheer'))
    barbichu(p, 300 + 170 * min(1, t), g + 40, 1.0, t, act, talk=1 <= t < 2)
    banner(p, 540, 190, 'RÉPUBLIQUE DU FROMAGISTAN', font(58), (245, 190, 40), (60, 40, 20))
    gauge(p, 60, 290, 'CITOYENS 27', .27, (110, 230, 140)); gauge(p, 390, 290, 'BUDGET 671', .55, (255, 205, 60)); gauge(p, 720, 290, 'POPULARITÉ', .7 + .05 * math.sin(t), (255, 120, 150))
    return img.resize((W, H), Image.LANCZOS).convert('RGB')


def sheet():
    global SHADOW; SHADOW = (235, 224, 200); img = Image.new('RGBA', (1920 * SS, 1080 * SS), (255, 247, 230)); p = Pen(img); g = 880
    barbichu(p, 300, g, 1.0, .5); pigeon(p, 700, g, 1.0, .5); rival(p, 1080, g, 1.0, .5); reporter(p, 1430, g, 1.0, .5); citizen(p, 1740, g, .8, .5, (230, 80, 80), 'idle')
    for x, s in ((300, 'PRÉSIDENT BARBICHU'), (700, 'LE PIGEON'), (1080, 'LE RIVAL'), (1430, 'LA REPORTER'), (1740, 'CITOYEN')): banner(p, x, 985, s, font(40), (60, 50, 90))
    return img.resize((1920, 1080), Image.LANCZOS).convert('RGB')


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); sheet().save(os.path.join(out, 'maquette.png')); SHADOW = (98, 86, 92)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', os.path.join(out, 'test.mp4')], stdin=subprocess.PIPE)
    for i in range(6 * FPS): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); frame(3.0).save(os.path.join(out, 'image.jpg'), quality=90)
