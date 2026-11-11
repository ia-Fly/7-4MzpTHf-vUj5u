"""FROMAGISTAN — personnages dessinés en code (aplats de couleur sans contour, ombres en deux tons, détails de vêtements et de décor) et animés : respiration, clignement, bras, marche, bouche.
    python3 formats/toon/rig.py OUT_DIR   -> maquette.png (planche) et test.mp4 (6 s d'animation)
Tout est vectoriel (PIL, rendu ×2 puis réduit) : 0 crédit, personnages identiques d'un épisode à l'autre."""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, SS, FPS = 1080, 1920, 2, 30
HERE = os.path.dirname(os.path.abspath(__file__)); FONTS = os.path.join(HERE, '..', '..', 'assets', 'fonts')
SKIN, SKIN2, SKIN3 = (244, 200, 165), (226, 172, 138), (205, 150, 120)
SHADOW = (98, 86, 92)                                  # ombre au sol : couleur pleine (PIL n'additionne pas la transparence)
INK = (52, 40, 48)


def font(size, name='Anton-Regular.ttf'): return ImageFont.truetype(os.path.join(FONTS, name), max(1, int(size)) * SS)
def sh(c, k=.82): return tuple(int(v * k) for v in c[:3])
def li(c, k=.25): return tuple(int(v + (255 - v) * k) for v in c[:3])


class Pen:
    """Petites formes à plat, coordonnées en pixels finaux (multipliées par SS au tracé)."""
    def __init__(self, img): self.d = ImageDraw.Draw(img)
    def circ(self, x, y, r, c): self.ell(x, y, r, r, c)
    def ell(self, x, y, rx, ry, c):
        if rx > 0 and ry > 0: self.d.ellipse([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], fill=c)
    def rect(self, x0, y0, x1, y1, c, r=0):
        if x1 > x0 and y1 > y0: self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2)) * SS, fill=c)
    def poly(self, pts, c): self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=c)
    def limb(self, p0, p1, w, c):
        self.d.line([(p0[0] * SS, p0[1] * SS), (p1[0] * SS, p1[1] * SS)], fill=c, width=max(1, int(w * SS))); self.circ(*p0, w / 2, c); self.circ(*p1, w / 2, c)
    def arc(self, x, y, rx, ry, a0, a1, c, w): self.d.arc([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], a0, a1, fill=c, width=max(1, int(w * SS)))
    def text(self, x, y, s, f, c, anchor='mm'): self.d.text((x * SS, y * SS), s, font=f, fill=c, anchor=anchor)
    def star(self, x, y, r, c):
        self.poly([(x + (r if i % 2 == 0 else r * .45) * math.sin(i * math.pi / 5), y - (r if i % 2 == 0 else r * .45) * math.cos(i * math.pi / 5)) for i in range(10)], c)


def at(p, ang, L): return (p[0] + L * math.sin(ang), p[1] + L * math.cos(ang))           # angle 0 = vers le bas, positif = vers la droite


def face(p, x, y, r, t, talk=False, mood='neutral', glasses=None, brow=(90, 60, 50), blink_off=0.0, iris=(70, 45, 35)):
    """Visage détaillé : yeux ouverts (blanc, iris, reflet) qui clignent, sourcils, nez, bouche avec dents quand le personnage parle."""
    blink = ((t + blink_off) % 3.1) < .12; ex, ey = r * .36, -r * .04; look = r * .03 * math.sin(t * .9 + blink_off)
    p.ell(x, y + r * .22, r * .1, r * .075, SKIN2); p.ell(x + r * .03, y + r * .25, r * .06, r * .04, SKIN3)                      # nez
    for s in (-1, 1):
        cx = x + s * ex
        if blink: p.limb((cx - r * .15, y + ey), (cx + r * .15, y + ey), r * .05, INK)
        else:
            p.ell(cx, y + ey, r * .17, r * (.12 if mood in ('bored', 'smug') else .18), (255, 255, 255)); p.circ(cx + look, y + ey + (r * .03 if mood in ('bored', 'smug') else 0), r * .105, iris); p.circ(cx + look, y + ey, r * .055, INK); p.circ(cx + look + r * .04, y + ey - r * .04, r * .03, (255, 255, 255))
            p.arc(cx, y + ey + r * .02, r * .19, r * .2, 200, 340, INK, r * .045)                                                     # paupière
        up = {'neutral': 0, 'happy': -.03, 'bored': .06, 'smug': -.1 if s > 0 else .05}.get(mood, 0)
        p.limb((cx - s * r * .17, y + ey - r * (.27 + up)), (cx + s * r * .15, y + ey - r * (.31 + up + (.05 if mood == 'happy' else 0))), r * .065, brow)
        if glasses: p.arc(cx, y + ey, r * .28, r * .28, 0, 360, glasses, r * .06)
    if glasses: p.limb((x - ex + r * .28, y + ey), (x + ex - r * .28, y + ey), r * .05, glasses)
    my = y + r * .52
    if talk and math.sin(t * 22) > -.2:
        o = r * (.07 + .09 * abs(math.sin(t * 13))); p.ell(x, my, r * .17, o, (110, 35, 45)); p.rect(x - r * .11, my - o, x + r * .11, my - o * .45, (255, 255, 255), r=r * .03); p.ell(x, my + o * .55, r * .09, o * .35, (225, 110, 120))
    elif mood == 'smug': p.arc(x + r * .08, my - r * .16, r * .22, r * .16, 20, 110, (140, 55, 60), r * .06)
    elif mood == 'bored': p.limb((x - r * .13, my), (x + r * .13, my), r * .055, (140, 60, 65))
    else: p.arc(x, my - r * .2, r * .25, r * .2, 20, 160, (165, 55, 70), r * .065)


def arm(p, shd, ang, L, w, col, hand=SKIN, bend=0.0):
    el = at(shd, ang, L * .5); ha = at(el, ang + bend, L * .5); p.limb(shd, el, w, col); p.limb(el, ha, w, col); p.circ(*at(el, ang + bend, L * .42), w * .55, sh(col))   # poignet
    p.circ(*ha, w * .6, hand); p.circ(ha[0] + w * .32 * math.cos(ang), ha[1] - w * .3, w * .24, hand); return ha


def acts(t, action):
    """Angles des bras, rebond et pas, selon l'action."""
    bob = 4 * math.sin(t * 3.2); la, ra, lb, rb, step = -.22, .22, 0, 0, 0
    if action == 'wave': ra, rb = 2.35 + .35 * math.sin(t * 9), .5
    elif action == 'cheer': la, ra, lb, rb = -2.5 + .2 * math.sin(t * 8), 2.5 - .2 * math.sin(t * 8), -.3, .3; bob = 14 * abs(math.sin(t * 6))
    elif action == 'talk': ra, rb = 1.1 + .25 * math.sin(t * 5), 1.0; la = -.3 + .08 * math.sin(t * 4)
    elif action == 'walk': step = math.sin(t * 8); la, ra = -.22 + .5 * step, .22 + .5 * step; bob = 6 * abs(math.cos(t * 8))
    return bob, la, ra, lb, rb, step


def human(p, x, g, s, t, action='idle', body=(60, 130, 220), legs=(40, 50, 90), hair=None, head_extra=None, mood='neutral', talk=False, tall=1.0, prop=None, glasses=None, off=0.0, shirt=(250, 250, 250)):
    """Personnage standard : tête ronde, cou, veste ombrée en deux tons avec col, fermeture et ceinture, mains avec pouce, chaussures à semelle. g = hauteur du sol."""
    bob, la, ra, lb, rb, step = acts(t + off, action); r = 92 * s; bh, bw = 215 * s * tall, 150 * s; leg = 150 * s * tall
    hip = g - leg; top = hip - bh + bob * s; hy = top - r * .86
    p.ell(x, g + 8 * s, 150 * s, 18 * s, SHADOW)
    for sgn in (-1, 1):
        fx = x + sgn * 38 * s + (sgn * step * 26 * s if action == 'walk' else 0); fy = g - (max(0, sgn * step) * 16 * s if action == 'walk' else 0)
        p.limb((x + sgn * 34 * s, hip - 10 * s), (fx, fy - 18 * s), 46 * s, legs if sgn < 0 else sh(legs, .88)); p.ell(fx + 10 * s, fy - 10 * s, 44 * s, 20 * s, (58, 52, 62)); p.rect(fx - 34 * s, fy - 6 * s, fx + 54 * s, fy + 4 * s, (235, 235, 240), r=5 * s)
    p.rect(x - 22 * s, top - 26 * s, x + 22 * s, top + 20 * s, SKIN2)                                                                  # cou
    p.rect(x - bw / 2, top, x + bw / 2, hip + 12 * s, body, r=44 * s); p.rect(x + bw * .16, top + 6 * s, x + bw / 2, hip + 12 * s, sh(body, .86), r=40 * s)
    p.poly([(x - 30 * s, top), (x + 30 * s, top), (x, top + 62 * s)], shirt); p.poly([(x - 46 * s, top), (x - 24 * s, top), (x - 4 * s, top + 66 * s), (x - 18 * s, top + 78 * s)], li(body, .18)); p.poly([(x + 46 * s, top), (x + 24 * s, top), (x + 4 * s, top + 66 * s), (x + 18 * s, top + 78 * s)], li(body, .1))
    p.limb((x, top + 70 * s), (x, hip - 6 * s), 5 * s, sh(body, .7))
    for k in range(3): p.circ(x + 12 * s, top + (96 + k * 34) * s, 5 * s, li(body, .45))
    p.rect(x - bw / 2 + 4 * s, hip - 6 * s, x + bw / 2 - 4 * s, hip + 10 * s, sh(legs, .7), r=6 * s); p.rect(x - 12 * s, hip - 8 * s, x + 12 * s, hip + 12 * s, (225, 190, 90), r=3 * s)
    lh = arm(p, (x - bw / 2 + 14 * s, top + 40 * s), la, 160 * s * tall, 46 * s, body, bend=lb); rh = arm(p, (x + bw / 2 - 14 * s, top + 40 * s), ra, 160 * s * tall, 46 * s, sh(body, .9), bend=rb)
    for sgn in (-1, 1): p.circ(x + sgn * r * .97, hy + r * .1, r * .19, SKIN2); p.circ(x + sgn * r * .97, hy + r * .1, r * .09, SKIN3)
    if hair: hair(p, x, hy, r, 'back')
    p.circ(x, hy, r, SKIN); p.ell(x + r * .5, hy + r * .25, r * .42, r * .6, SKIN2); p.circ(x - r * .08, hy - r * .02, r * .9, SKIN)   # ombre de joue
    if hair: hair(p, x, hy, r, 'front')
    face(p, x, hy, r, t, talk, mood, glasses, blink_off=off)
    if head_extra: head_extra(p, x, hy, r)
    if prop: prop(p, lh, rh, s)
    return dict(head=(x, hy, r), lh=lh, rh=rh)


# ---- les personnages ----
def barbichu(p, x, g, s, t, action='idle', talk=False):
    """Président Barbichu : vieux mage rond, robe violette étoilée à plis, barbe tressée, sourcils blancs, lunettes rondes, bonnet à pompon, écharpe présidentielle jaune, bâton à coq."""
    bob, la, ra, lb, rb, step = acts(t, action); r = 104 * s; V, V2, Y = (112, 72, 190), (86, 52, 156), (250, 200, 60)
    top = g - 290 * s + bob * s; hy = top - r * .6; sway = (step * 10 * s) if action == 'walk' else 0
    p.ell(x, g + 8 * s, 175 * s, 22 * s, SHADOW)
    for sgn in (-1, 1): p.ell(x + sgn * 58 * s + sgn * sway, g - 8 * s, 46 * s, 20 * s, (86, 58, 40)); p.ell(x + sgn * 62 * s + sgn * sway, g - 14 * s, 30 * s, 10 * s, (116, 80, 56))
    p.poly([(x - 98 * s, top + 30 * s), (x + 98 * s, top + 30 * s), (x + 156 * s, g - 14 * s), (x - 156 * s, g - 14 * s)], V); p.ell(x, g - 14 * s, 156 * s, 22 * s, V); p.circ(x, top + 62 * s, 100 * s, V)
    p.poly([(x + 40 * s, top + 40 * s), (x + 98 * s, top + 30 * s), (x + 156 * s, g - 14 * s), (x + 70 * s, g + 2 * s)], V2)                    # côté ombré
    for fx in (-90, -30, 28): p.poly([(x + fx * s * .5, top + 150 * s), (x + (fx + 10) * s * .5, top + 150 * s), (x + (fx * 1.5 + 14) * s, g - 6 * s), (x + fx * 1.5 * s, g - 6 * s)], sh(V, .9))   # plis
    p.rect(x - 156 * s, g - 34 * s, x + 156 * s, g - 20 * s, Y, r=6 * s)                                                                         # galon du bas
    for sx, sy, sr in ((-72, 130, 13), (58, 165, 11), (-22, 215, 9), (98, 245, 12), (-108, 245, 10), (18, 120, 8)): p.star(x + sx * s, top + sy * s, sr * s, Y)
    p.poly([(x - 102 * s, top + 44 * s), (x - 70 * s, top + 22 * s), (x + 128 * s, g - 96 * s), (x + 112 * s, g - 52 * s)], Y); p.poly([(x - 86 * s, top + 33 * s), (x - 70 * s, top + 22 * s), (x + 128 * s, g - 96 * s), (x + 120 * s, g - 76 * s)], li(Y, .35))
    p.circ(x + 96 * s, g - 96 * s, 26 * s, (230, 70, 90)); p.star(x + 96 * s, g - 96 * s, 15 * s, Y)                                              # cocarde
    staff_top = (x - 196 * s, top - 150 * s + bob * s)
    lh = arm(p, (x - 88 * s, top + 62 * s), -.9, 124 * s, 52 * s, V); p.limb(staff_top, (lh[0] - 6 * s, g - 6 * s), 17 * s, (128, 84, 48)); p.limb((staff_top[0] + 3 * s, staff_top[1]), (lh[0] - 3 * s, g - 6 * s), 5 * s, (160, 112, 68))
    for k in (.25, .55, .8): p.circ(staff_top[0] + (lh[0] - 6 * s - staff_top[0]) * k, staff_top[1] + (g - staff_top[1]) * k, 11 * s, (108, 70, 40))
    cx, cy = staff_top[0], staff_top[1] - 30 * s
    p.poly([(cx - 30 * s, cy), (cx - 58 * s, cy - 30 * s), (cx - 50 * s, cy + 8 * s)], (240, 150, 50)); p.ell(cx, cy, 32 * s, 27 * s, Y); p.ell(cx - 6 * s, cy + 6 * s, 18 * s, 12 * s, (232, 170, 40)); p.circ(cx + 24 * s, cy - 24 * s, 17 * s, Y)
    p.poly([(cx + 38 * s, cy - 27 * s), (cx + 58 * s, cy - 20 * s), (cx + 38 * s, cy - 14 * s)], (240, 140, 40)); p.circ(cx + 28 * s, cy - 27 * s, 4 * s, INK); p.ell(cx + 30 * s, cy - 6 * s, 6 * s, 10 * s, (225, 55, 55))
    for k in range(3): p.circ(cx + (15 + k * 8) * s, cy - 42 * s, 7.5 * s, (225, 55, 55))                                                        # crête du coq
    p.circ(lh[0], lh[1], 31 * s, SKIN); p.circ(lh[0] + 16 * s, lh[1] - 12 * s, 12 * s, SKIN2)
    rh = arm(p, (x + 88 * s, top + 62 * s), ra if action != 'idle' else .5, 134 * s, 52 * s, V2, bend=rb)
    for sgn in (-1, 1): p.circ(x + sgn * r * .97, hy + r * .1, r * .2, SKIN2); p.circ(x + sgn * r * .97, hy + r * .1, r * .09, SKIN3)
    p.circ(x, hy, r, SKIN); p.ell(x + r * .52, hy + r * .1, r * .4, r * .7, SKIN2); p.circ(x - r * .08, hy - r * .04, r * .9, SKIN)
    p.ell(x, hy + r * .86, r * .9, r * .72, (236, 238, 246)); p.ell(x - r * .06, hy + r * .8, r * .82, r * .68, (255, 255, 255))                 # barbe en deux tons
    p.poly([(x - r * .32, hy + r * 1.36), (x + r * .32, hy + r * 1.36), (x, hy + r * 2.3)], (255, 255, 255)); p.poly([(x, hy + r * 1.36), (x + r * .32, hy + r * 1.36), (x, hy + r * 2.3)], (232, 235, 244))
    for k in range(4): p.limb((x - r * (.22 - k * .03), hy + r * (1.46 + k * .2)), (x + r * (.2 - k * .03), hy + r * (1.54 + k * .2)), 5 * s, (200, 206, 224))                        # tresse
    for k in (-.5, -.2, .15, .45): p.limb((x + k * r, hy + r * .75), (x + k * r * .9, hy + r * 1.2), 3.5 * s, (222, 226, 238))                    # mèches
    p.circ(x, hy + r * 2.28, r * .11, Y)
    face(p, x, hy - r * .06, r, t, False, 'happy' if action == 'cheer' else 'neutral', glasses=(60, 44, 52), brow=(250, 250, 252), iris=(70, 110, 160))
    p.ell(x - r * .2, hy + r * .46, r * .3, r * .15, (255, 255, 255)); p.ell(x + r * .2, hy + r * .46, r * .3, r * .15, (240, 242, 248)); p.ell(x, hy + r * .2, r * .13, r * .11, (236, 150, 135))   # moustache, nez
    if talk and math.sin(t * 22) > -.2: p.ell(x, hy + r * .66, r * .14, r * (.05 + .08 * abs(math.sin(t * 13))), (110, 35, 45))
    tip = (x + r * 1.15 + 14 * s * math.sin(t * 3), hy - r * 1.3)
    p.poly([(x - r * 1.02, hy - r * .44), (x + r * 1.02, hy - r * .44), tip, (x + r * .15, hy - r * 1.85)], V); p.poly([(x + r * .3, hy - r * .44), (x + r * 1.02, hy - r * .44), tip, (x + r * .55, hy - r * 1.5)], V2)
    p.rect(x - r * 1.1, hy - r * .62, x + r * 1.1, hy - r * .34, V2, r=r * .14); p.rect(x - r * 1.1, hy - r * .62, x + r * 1.1, hy - r * .52, sh(V2, 1.15), r=r * .1); p.rect(x - r * .16, hy - r * .64, x + r * .16, hy - r * .32, Y, r=r * .04); p.rect(x - r * .09, hy - r * .57, x + r * .09, hy - r * .39, V2, r=r * .03)
    p.circ(*tip, r * .21, (240, 242, 248)); p.circ(tip[0] - r * .05, tip[1] - r * .05, r * .15, (255, 255, 255))
    for sx, sy in ((-.45, -.9), (.2, -1.3), (-.1, -1.55)): p.star(x + sx * r, hy + sy * r, r * .1, Y)
    return dict(head=(x, hy, r), rh=rh)


def pigeon(p, x, g, s, t, action='idle', talk=False):
    """Le pigeon conseiller : gris, plumage en couches, col irisé, cravate rouge, lunettes de lecture, bloc-notes."""
    bob, la, ra, lb, rb, step = acts(t + 1.3, action); G, G2, G3 = (140, 146, 164), (108, 114, 134), (84, 90, 110); by = g - 170 * s + bob * s; hy = by - 180 * s
    p.ell(x, g + 6 * s, 130 * s, 18 * s, SHADOW)
    for sgn in (-1, 1):
        p.limb((x + sgn * 36 * s, g - 60 * s), (x + sgn * 36 * s, g - 12 * s), 11 * s, (232, 128, 60))
        for k in (-1, 0, 1): p.limb((x + sgn * 36 * s, g - 12 * s), (x + sgn * 36 * s + (k * 22 + 14) * s, g - 4 * s), 9 * s, (232, 128, 60))
    p.poly([(x - 60 * s, by + 100 * s), (x - 150 * s, by + 150 * s), (x - 40 * s, by + 140 * s)], G3)                                              # queue
    p.ell(x, by, 120 * s, 150 * s, G); p.ell(x + 46 * s, by + 10 * s, 70 * s, 132 * s, G2); p.ell(x - 4 * s, by + 34 * s, 82 * s, 104 * s, (222, 226, 236))
    for k in range(5): p.arc(x - 4 * s, by + (0 + k * 26) * s, 50 * s, 20 * s, 20, 160, (198, 204, 218), 4 * s)                                   # plumes du ventre
    p.ell(x, by - 96 * s, 74 * s, 40 * s, (96, 150, 140)); p.ell(x, by - 86 * s, 70 * s, 30 * s, (130, 110, 170))                                 # col irisé
    p.poly([(x - 16 * s, by - 96 * s), (x + 16 * s, by - 96 * s), (x + 22 * s, by - 20 * s), (x, by + 6 * s), (x - 22 * s, by - 20 * s)], (214, 50, 56)); p.poly([(x, by - 96 * s), (x + 16 * s, by - 96 * s), (x + 22 * s, by - 20 * s), (x, by + 6 * s)], (180, 38, 46)); p.circ(x, by - 100 * s, 18 * s, (196, 42, 48))
    wx = x - 150 * s - 18 * s * math.sin(t * 3); p.poly([(x - 112 * s, by - 60 * s), (wx, by + 70 * s), (x - 92 * s, by + 64 * s)], G2); p.poly([(x - 108 * s, by - 20 * s), (wx + 16 * s, by + 66 * s), (x - 96 * s, by + 62 * s)], G3)
    wa = ra if action != 'idle' else .9; w1 = at((x + 104 * s, by - 50 * s), wa, 120 * s); p.limb((x + 104 * s, by - 50 * s), w1, 50 * s, G2); p.limb((x + 108 * s, by - 40 * s), at((x + 108 * s, by - 40 * s), wa, 96 * s), 22 * s, G3)
    p.rect(w1[0] - 46 * s, w1[1] - 70 * s, w1[0] + 46 * s, w1[1] + 46 * s, (160, 108, 62), r=8 * s); p.rect(w1[0] - 36 * s, w1[1] - 52 * s, w1[0] + 36 * s, w1[1] + 38 * s, (252, 250, 244), r=4 * s); p.rect(w1[0] - 16 * s, w1[1] - 80 * s, w1[0] + 16 * s, w1[1] - 60 * s, (150, 152, 162), r=5 * s)
    for k in range(4): p.rect(w1[0] - 26 * s, w1[1] - (38 - k * 20) * s, w1[0] + (26 - (k % 2) * 14) * s, w1[1] - (33 - k * 20) * s, (176, 182, 196))
    p.circ(x, hy, 86 * s, G); p.ell(x + 34 * s, hy + 8 * s, 48 * s, 70 * s, G2); p.circ(x - 6 * s, hy - 2 * s, 76 * s, G)
    p.poly([(x - 14 * s, hy - 80 * s), (x + 14 * s, hy - 80 * s), (x + 6 * s, hy - 114 * s)], G2)
    o = (10 * abs(math.sin(t * 13)) if talk else 0) * s
    p.poly([(x - 22 * s, hy + 10 * s), (x + 22 * s, hy + 10 * s), (x, hy + 44 * s)], (240, 150, 60)); p.poly([(x - 16 * s, hy + 26 * s + o * .3), (x + 16 * s, hy + 26 * s + o * .3), (x, hy + 50 * s + o)], (214, 120, 44)); p.ell(x, hy + 12 * s, 16 * s, 8 * s, (236, 236, 242))
    blink = ((t + .7) % 3.4) < .12
    for sgn in (-1, 1):
        ex = x + sgn * 34 * s; p.circ(ex, hy - 10 * s, 21 * s, (255, 255, 255)); p.circ(ex + 2 * s, hy - 6 * s, 11 * s, (214, 120, 44)); p.circ(ex + 2 * s, hy - 6 * s, 6 * s, INK); p.circ(ex + 5 * s, hy - 9 * s, 2.5 * s, (255, 255, 255))
        p.rect(ex - 23 * s, hy - 33 * s, ex + 23 * s, hy - (13 if not blink else -12) * s, G2, r=6 * s)                                             # paupières lourdes
        p.arc(ex, hy - 4 * s, 26 * s, 24 * s, 0, 180, (60, 60, 70), 4 * s)                                                                         # demi-lunes
    p.limb((x - 8 * s, hy + 2 * s), (x + 8 * s, hy + 2 * s), 4 * s, (60, 60, 70))
    return dict(head=(x, hy, 86 * s))


def rival(p, x, g, s, t, action='idle', talk=False):
    """Le rival : grand, maigre, manteau gris, cheveux vert sombre plaqués avec raie, monocle à chaîne."""
    C = (28, 80, 62)
    def hair(p, x, y, r, layer):
        if layer == 'back': p.circ(x, y - r * .1, r * 1.03, C)
        else:
            p.poly([(x - r * 1.0, y - r * .2), (x - r * .9, y - r * .75), (x - r * .3, y - r * 1.06), (x + r * .5, y - r * 1.0), (x + r * 1.0, y - r * .35), (x + r * .6, y - r * .62), (x - r * .1, y - r * .72), (x - r * .62, y - r * .5)], C)
            p.limb((x - r * .3, y - r * 1.0), (x - r * .1, y - r * .72), r * .04, li(C, .25)); p.poly([(x - r * 1.02, y - r * .2), (x - r * .86, y - r * .25), (x - r * .9, y + r * .25)], C); p.poly([(x + r * 1.02, y - r * .3), (x + r * .86, y - r * .3), (x + r * .92, y + r * .2)], C)
    def extra(p, x, y, r):
        p.arc(x + r * .36, y - r * .04, r * .29, r * .29, 0, 360, (226, 186, 70), r * .07); p.limb((x + r * .62, y + r * .14), (x + r * .78, y + r * 1.0), r * .028, (226, 186, 70))
    return human(p, x, g, s * .9, t, action, body=(118, 124, 142), legs=(52, 56, 72), hair=hair, head_extra=extra, mood='smug', talk=talk, tall=1.45, off=2.1, shirt=(190, 60, 70))


def reporter(p, x, g, s, t, action='talk', talk=True):
    """La reporter de Fromagistan Info : cheveux roux bouclés, veste bleue, badge presse, micro à bonnette."""
    def hair(p, x, y, r, layer):
        pts = [(-1.0, -.1), (-.98, -.6), (-.62, -.98), (-.15, -1.15), (.35, -1.1), (.78, -.85), (1.02, -.4), (1.04, .15), (-1.0, .3)] if layer == 'back' else [(-.72, -.72), (-.32, -.92), (.14, -.94), (.56, -.78)]
        for k, (hx, hyy) in enumerate(pts): p.circ(x + hx * r, y + hyy * r, r * (.42 if layer == 'back' else .3), (232, 108, 36) if k % 2 else (244, 128, 48))
    def mic(p, lh, rh, s):
        p.limb(rh, (rh[0] + 10 * s, rh[1] - 90 * s), 22 * s, (64, 64, 76)); p.ell(rh[0] + 12 * s, rh[1] - 140 * s, 50 * s, 60 * s, (54, 54, 66)); p.ell(rh[0] + 4 * s, rh[1] - 150 * s, 34 * s, 42 * s, (84, 84, 98)); p.rect(rh[0] - 30 * s, rh[1] - 100 * s, rh[0] + 54 * s, rh[1] - 70 * s, (240, 190, 50), r=5 * s); p.circ(*rh, 28 * s, SKIN)
    b = human(p, x, g, s * .95, t, action, body=(46, 112, 214), legs=(40, 44, 78), hair=hair, mood='happy', talk=talk, prop=mic, off=.9)
    hx, hy, r = b['head']; p.rect(x - 62 * s, hy + r * 2.0, x - 22 * s, hy + r * 2.45, (255, 255, 255), r=4 * s); p.rect(x - 56 * s, hy + r * 2.08, x - 28 * s, hy + r * 2.2, (230, 70, 90)); return b


def citizen(p, x, g, s, t, col, action='cheer', off=0.0):
    def hair(p, x, y, r, layer):
        if layer == 'front': p.poly([(x - r * .98, y - r * .3), (x - r * .76, y - r * .92), (x - r * .1, y - r * 1.14), (x + r * .5, y - r * 1.0), (x + r * .98, y - r * .3), (x + r * .4, y - r * .62), (x - r * .5, y - r * .56)], (58, 48, 70)); p.limb((x - r * .4, y - r * .95), (x + r * .3, y - r * .98), r * .05, (86, 74, 100))
    return human(p, x, g, s, t, action, body=col, legs=(44, 48, 84), hair=hair, mood='happy' if action == 'cheer' else 'neutral', off=off)


# ---- décor et interface ----
def background(t):
    """Le palais présidentiel en ruine : colonnes à chapiteaux, fenêtres, marches, fissures, demi-toit, buissons, pavés."""
    img = Image.new('RGBA', (W * SS, H * SS)); p = Pen(img); d = p.d
    for y in range(0, H * SS, 4):
        k = y / (H * SS); d.rectangle([0, y, W * SS, y + 4], fill=(int(112 + 118 * k), int(182 + 48 * k), int(246 - 16 * k)))
    p.circ(860, 330, 150, (190, 222, 250)); p.circ(860, 330, 110, (255, 244, 196))
    for cx, cy, sc in ((220 + 30 * math.sin(t * .3), 420, 1.0), (640 + 40 * math.sin(t * .25 + 1), 250, .7)):
        for dx, dy, rr in ((0, 0, 60), (70, 10, 48), (-70, 14, 44), (20, -30, 46)): p.circ(cx + dx * sc, cy + dy * sc, rr * sc, (255, 255, 255))
        p.rect(cx - 110 * sc, cy + 22 * sc, cx + 112 * sc, cy + 58 * sc, (255, 255, 255), r=18 * sc)
    p.ell(200, 1420, 620, 300, (118, 190, 112)); p.ell(900, 1440, 560, 260, (98, 174, 104)); p.rect(0, 1380, W, H, (140, 202, 122))
    for bx in (60, 1010): p.circ(bx, 1380, 80, (70, 150, 90)); p.circ(bx + 50, 1400, 60, (86, 166, 100)); p.circ(bx - 50, 1404, 56, (60, 136, 84))
    C, C2, C3 = (246, 234, 206), (224, 208, 176), (198, 180, 148)
    p.rect(170, 800, 910, 1400, C, r=6); p.rect(730, 800, 910, 1400, li(C2, .35))
    for k in range(5):
        x0 = 215 + k * 140; p.rect(x0, 900, x0 + 50, 1380, C2, r=6); p.rect(x0 + 34, 900, x0 + 50, 1380, C3, r=4); p.rect(x0 - 12, 876, x0 + 62, 906, C2, r=6); p.rect(x0 - 12, 1362, x0 + 62, 1392, C2, r=6)
    for k in range(4):
        wx0 = 288 + k * 140
        if k not in (1, 2): p.rect(wx0, 960, wx0 + 44, 1060, (96, 132, 176), r=22); p.rect(wx0 + 20, 960, wx0 + 24, 1060, C)
    p.rect(150, 790, 930, 826, C2, r=6); p.rect(120, 1392, 960, 1424, C2, r=6); p.rect(96, 1420, 984, 1452, C3, r=6); p.rect(70, 1448, 1010, 1482, sh(C3, .92), r=6)
    p.poly([(140, 800), (540, 600), (940, 800)], (198, 84, 76)); p.poly([(210, 786), (540, 624), (870, 786)], (214, 98, 88)); p.circ(540, 716, 34, C); p.circ(540, 716, 22, (96, 132, 176))
    p.poly([(540, 600), (940, 800), (700, 800), (600, 700), (660, 640)], (126, 192, 240))                                                          # toit à moitié parti
    for a, b in (((640, 830), (668, 900)), ((668, 900), (650, 960)), ((300, 1180), (330, 1250)), ((820, 1100), (800, 1190))): p.limb(a, b, 4, C3)   # fissures
    p.rect(456, 1128, 624, 1392, C3, r=84); p.rect(470, 1140, 610, 1392, (128, 86, 54), r=70); p.rect(538, 1140, 542, 1392, (100, 66, 42)); p.circ(585, 1270, 9, (236, 196, 80)); p.circ(495, 1270, 9, (236, 196, 80))
    p.limb((540, 600), (540, 500), 8, (116, 86, 58)); f = 10 * math.sin(t * 4); p.poly([(544, 500), (650 + f, 520), (544, 548)], (250, 200, 60)); p.poly([(544, 524), (650 + f, 520), (544, 548)], (228, 172, 44))
    p.rect(0, 1560, W, H, (118, 104, 110)); p.rect(0, 1540, W, 1572, (140, 126, 132))
    for r_ in range(5):
        for c in range(8): p.rect(c * 150 - (75 if r_ % 2 else 0) + 5, 1582 + r_ * 70, c * 150 - (75 if r_ % 2 else 0) + 143, 1582 + r_ * 70 + 60, (126, 112, 118) if (c + r_) % 3 else (110, 97, 104), r=10)
    return img


def gauge(p, x, y, label, val, col, w=300):
    p.rect(x, y, x + w, y + 46, (40, 40, 60), r=23); p.rect(x + 5, y + 5, x + 5 + (w - 10) * max(.06, min(1, val)), y + 41, col, r=18)
    p.d.text(((x + w / 2) * SS, (y + 80) * SS), label, font=font(34), fill=(255, 255, 255), anchor='mm', stroke_width=5 * SS, stroke_fill=(30, 30, 50))


def banner(p, x, y, s, f, bg, fg=(255, 255, 255), rot=0):
    l, t0, r, b = p.d.textbbox((0, 0), s, font=f); w = (r - l) / SS + 50; h = (b - t0) / SS + 34
    p.rect(x - w / 2, y - h / 2 + 6, x + w / 2, y + h / 2 + 6, sh(bg, .75), r=8); p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, bg, r=8); p.text(x, y, s, f, fg)


def camera(img, z, cx, cy):
    """Cadre la scène : zoom z (1 = plan large) centré sur (cx, cy), sans sortir de l'image. Renvoie une image à la taille de rendu."""
    z = max(1.0, z); w, h = W / z, H / z; x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    return img.transform((W * SS, H * SS), Image.EXTENT, (x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS), Image.BICUBIC)


def sheet():
    global SHADOW; SHADOW = (235, 224, 200); img = Image.new('RGBA', (1920 * SS, 1080 * SS), (255, 247, 230)); p = Pen(img); g = 900
    barbichu(p, 300, g, 1.0, .5); pigeon(p, 700, g, 1.0, .5); rival(p, 1080, g, 1.0, .5); reporter(p, 1430, g, 1.0, .5); citizen(p, 1740, g, .85, .5, (214, 76, 76), 'idle')
    for x, s in ((300, 'PRÉSIDENT BARBICHU'), (700, 'LE PIGEON'), (1080, 'LE RIVAL'), (1430, 'LA REPORTER'), (1740, 'CITOYEN')): banner(p, x, 1005, s, font(40), (60, 50, 90))
    return img.resize((1920, 1080), Image.LANCZOS).convert('RGB')


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); sheet().save(os.path.join(out, 'maquette.png'))
