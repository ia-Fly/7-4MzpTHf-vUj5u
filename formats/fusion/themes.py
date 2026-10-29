"""Thèmes du format « fusion » : chaque thème = une échelle de niveaux (petit -> géant) dessinés en vectoriel (skia).
Tout est dessiné maison : aucun personnage, logo ou image protégée.
Chaque fonction draw_* dessine l'objet centré en (0, 0), de rayon r, sur un canvas skia."""
import math, random, os
import skia

FONTS = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'fonts')
TF = {k: skia.Typeface.MakeFromFile(os.path.join(FONTS, f)) for k, f in
      {'anton': 'Anton-Regular.ttf', 'barlow': 'BarlowCondensed-ExtraBold.ttf', 'mono': 'JetBrainsMono-VF.ttf',
       'mont': 'Montserrat-Black.ttf'}.items()}


def C(h, a=255):
    h = h.lstrip('#'); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def P(color=None, shader=None, stroke=0, blur=0, alpha=None):
    p = skia.Paint(AntiAlias=True)
    if color is not None: p.setColor(color)
    if shader is not None: p.setShader(shader)
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if alpha is not None: p.setAlphaf(alpha)
    return p


def radial(cx, cy, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [C(c) if isinstance(c, str) else c for c in cols], pos)


def linear(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [C(c) if isinstance(c, str) else c for c in cols], pos)


def ball(cv, r, c_light, c_dark):
    cv.drawCircle(0, 0, r, P(shader=radial(-0.35 * r, -0.4 * r, 1.45 * r, [c_light, c_dark])))


def clip_circle(cv, r):
    path = skia.Path(); path.addCircle(0, 0, r); cv.clipPath(path, skia.ClipOp.kIntersect, True)


def shade(cv, r, strength=1.0):
    """volume : reflet en haut à gauche + ombre en bas à droite + contour"""
    cv.drawCircle(0, 0, r, P(shader=radial(-0.38 * r, -0.42 * r, 1.25 * r,
                                          [skia.Color(255, 255, 255, int(70 * strength)), skia.Color(255, 255, 255, 0)])))
    cv.drawCircle(0, 0, r, P(shader=radial(-0.25 * r, -0.3 * r, 1.35 * r,
                                          [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, int(120 * strength))], [0, 0.55, 1])))
    cv.drawCircle(0, 0, r - max(1.0, r * 0.02), P(skia.Color(0, 0, 0, 90), stroke=max(2.0, r * 0.04)))


def blob(rng, cx, cy, rad, n=9, jit=0.35):
    path = skia.Path(); pts = []
    for i in range(n):
        a = 2 * math.pi * i / n; rr = rad * (1 + rng.uniform(-jit, jit)); pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    path.moveTo(*[(pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2])
    for i in range(n):
        p1 = pts[(i + 1) % n]; p2 = pts[(i + 2) % n]; path.quadTo(p1[0], p1[1], (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    path.close(); return path


def craters(cv, r, rng, n, col_d, col_l):
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi); d = r * math.sqrt(rng.uniform(0, 0.7)); cr = r * rng.uniform(0.07, 0.2)
        x, y = d * math.cos(a), d * math.sin(a)
        cv.drawCircle(x, y, cr, P(col_d)); cv.drawCircle(x - cr * 0.15, y - cr * 0.15, cr * 0.82, P(col_l, alpha=0.35))


# ---------------------------------------------------------------- PLANÈTES
def moon(cv, r, rng):
    ball(cv, r, '#E6E3DA', '#8C8A84'); clip_circle(cv, r); craters(cv, r, rng, 7, C('#7E7C76'), C('#C9C6BD')); shade(cv, r)

def mercury(cv, r, rng):
    ball(cv, r, '#C4B2A2', '#6F5F55'); clip_circle(cv, r); craters(cv, r, rng, 9, C('#6B5B50'), C('#B8A696')); shade(cv, r)

def mars(cv, r, rng):
    ball(cv, r, '#F08A55', '#9C3415'); clip_circle(cv, r)
    for _ in range(5): cv.drawPath(blob(rng, rng.uniform(-.5, .5) * r, rng.uniform(-.4, .6) * r, r * rng.uniform(.15, .3)), P(C('#8E2F12', 150)))
    cv.drawOval(skia.Rect.MakeLTRB(-.38 * r, -1.02 * r, .38 * r, -.72 * r), P(C('#FFF6EE', 230))); shade(cv, r)

def venus(cv, r, rng):
    ball(cv, r, '#FBE3A6', '#C48A3E'); clip_circle(cv, r)
    for i in range(6):
        y = (-0.8 + i * 0.32) * r; path = skia.Path(); path.moveTo(-r, y)
        path.cubicTo(-.4 * r, y - .18 * r, .3 * r, y + .2 * r, r, y - .05 * r)
        cv.drawPath(path, P(C('#FFF4D6', 110), stroke=r * 0.09))
    shade(cv, r)

def earth(cv, r, rng):
    ball(cv, r, '#4A9BF0', '#123A86'); clip_circle(cv, r)
    for cx, cy, s in ((-.35, -.25, .42), (.38, .1, .36), (-.1, .55, .28), (.45, -.55, .2)):
        cv.drawPath(blob(rng, cx * r, cy * r, s * r, 10, .4), P(C('#3FA45B')))
        cv.drawPath(blob(rng, cx * r + s * r * .2, cy * r + s * r * .15, s * r * .5, 8, .4), P(C('#2E7D46', 180)))
    for i in range(4):
        y = rng.uniform(-.7, .7) * r; x0 = rng.uniform(-1, .2) * r; path = skia.Path(); path.moveTo(x0, y)
        path.cubicTo(x0 + .3 * r, y - .12 * r, x0 + .6 * r, y + .1 * r, x0 + .95 * r, y - .05 * r)
        cv.drawPath(path, P(C('#FFFFFF', 170), stroke=r * 0.07))
    shade(cv, r)

def neptune(cv, r, rng):
    ball(cv, r, '#5B84FF', '#16258A'); clip_circle(cv, r)
    for i in range(4): cv.drawRect(skia.Rect.MakeLTRB(-r, (-.6 + i * .38) * r, r, (-.52 + i * .38) * r), P(C('#9DB6FF', 60)))
    cv.drawOval(skia.Rect.MakeLTRB(.05 * r, .1 * r, .45 * r, .3 * r), P(C('#0D1660', 200))); shade(cv, r)

def uranus(cv, r, rng):
    ball(cv, r, '#C8F4F6', '#4FA3B8'); clip_circle(cv, r)
    cv.drawRect(skia.Rect.MakeLTRB(-r, -.12 * r, r, .02 * r), P(C('#FFFFFF', 50))); shade(cv, r)

def saturn(cv, r, rng):
    cv.save(); cv.rotate(-18)
    oval = skia.Rect.MakeLTRB(-1.62 * r, -.42 * r, 1.62 * r, .42 * r)
    ringp = P(C('#E9D3A0', 210), stroke=r * 0.16); ringp2 = P(C('#B79A63', 200), stroke=r * 0.07)
    inner = skia.Rect.MakeLTRB(-1.3 * r, -.3 * r, 1.3 * r, .3 * r)
    cv.drawArc(oval, 180, 180, False, ringp); cv.drawArc(inner, 180, 180, False, ringp2)
    cv.restore()
    cv.save(); ball(cv, r, '#F2DDA9', '#A9844A'); clip_circle(cv, r)
    for i, c in enumerate(('#D8BC82', '#EAD3A0', '#C9A66B', '#E2C994')):
        cv.drawRect(skia.Rect.MakeLTRB(-r, (-.75 + i * .4) * r, r, (-.6 + i * .4) * r), P(C(c, 150)))
    shade(cv, r); cv.restore()
    cv.save(); cv.rotate(-18); cv.drawArc(oval, 0, 180, False, ringp); cv.drawArc(inner, 0, 180, False, ringp2); cv.restore()

def jupiter(cv, r, rng):
    ball(cv, r, '#F3DCC0', '#9E6A3E'); clip_circle(cv, r)
    cols = ['#E9D6BC', '#C98E5C', '#F1E2CC', '#B87443', '#E7CFAE', '#C78A57', '#EEDCC3']
    for i, c in enumerate(cols):
        y0 = (-1 + i * 2 / len(cols)) * r; path = skia.Path(); path.moveTo(-r, y0)
        path.cubicTo(-.3 * r, y0 - .06 * r, .3 * r, y0 + .06 * r, r, y0); path.lineTo(r, y0 + 2 * r / len(cols)); path.lineTo(-r, y0 + 2 * r / len(cols)); path.close()
        cv.drawPath(path, P(C(c, 200)))
    cv.drawOval(skia.Rect.MakeLTRB(.12 * r, .22 * r, .58 * r, .46 * r), P(C('#C2533A', 235)))
    cv.drawOval(skia.Rect.MakeLTRB(.18 * r, .27 * r, .52 * r, .41 * r), P(C('#E07A5A', 160))); shade(cv, r)

def sun(cv, r, rng):
    cv.drawCircle(0, 0, r * 1.18, P(C('#FFB300', 170), blur=r * 0.22))
    cv.drawCircle(0, 0, r, P(shader=radial(-.15 * r, -.2 * r, 1.2 * r, ['#FFFBD0', '#FFD23A', '#FF9800', '#F06A00'], [0, .35, .75, 1])))
    clip_circle(cv, r)
    for _ in range(26):
        a = rng.uniform(0, 2 * math.pi); d = r * math.sqrt(rng.uniform(0, .85))
        cv.drawCircle(d * math.cos(a), d * math.sin(a), r * rng.uniform(.03, .08), P(C('#FFF3B0', 90)))
    cv.drawCircle(0, 0, r, P(shader=radial(0, 0, r, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(200, 60, 0, 120)], [0, .7, 1])))


# ---------------------------------------------------------------- FRUITS (persos maison, visage kawaii)
def face(cv, r, dark='#2B1B17'):
    ey = -.05 * r
    for sx in (-1, 1):
        cv.drawOval(skia.Rect.MakeXYWH(sx * .3 * r - .12 * r, ey - .15 * r, .24 * r, .3 * r), P(C('#FFFFFF')))
        cv.drawCircle(sx * .3 * r + .02 * r, ey + .03 * r, .08 * r, P(C(dark)))
        cv.drawCircle(sx * .3 * r - .01 * r, ey - .03 * r, .03 * r, P(C('#FFFFFF')))
        cv.drawOval(skia.Rect.MakeXYWH(sx * .52 * r - .1 * r, .14 * r, .2 * r, .1 * r), P(C('#FF7A8A', 120)))
    path = skia.Path(); path.moveTo(-.1 * r, .2 * r); path.quadTo(0, .32 * r, .1 * r, .2 * r)
    cv.drawPath(path, P(C(dark), stroke=max(2.0, .045 * r)))

def leaf(cv, x, y, s, ang, col='#3E9B4F'):
    cv.save(); cv.translate(x, y); cv.rotate(ang); path = skia.Path(); path.moveTo(0, 0)
    path.quadTo(s * .5, -s * .45, s, 0); path.quadTo(s * .5, s * .45, 0, 0); cv.drawPath(path, P(C(col))); cv.restore()

def fruit(base_l, base_d, extra=None, stem=False, leaves=0, dark='#2B1B17'):
    def d(cv, r, rng):
        if stem: cv.drawLine(0, -.85 * r, .12 * r, -1.25 * r, P(C('#6B4226'), stroke=.09 * r))
        if leaves: leaf(cv, .05 * r, -.95 * r, .55 * r, -35)
        ball(cv, r, base_l, base_d); cv.save(); clip_circle(cv, r)
        if extra: extra(cv, r, rng)
        shade(cv, r, .8); cv.restore(); face(cv, r, dark)
    return d

def seeds(col, n=14):
    def e(cv, r, rng):
        for _ in range(n):
            a = rng.uniform(0, 2 * math.pi); dd = r * math.sqrt(rng.uniform(.1, .8))
            cv.drawOval(skia.Rect.MakeXYWH(dd * math.cos(a), dd * math.sin(a), .07 * r, .1 * r), P(C(col)))
    return e

def crown(col='#3E9B4F', n=5):
    def e(cv, r, rng):
        for i in range(n): leaf(cv, (-0.3 + .15 * i) * r, -.92 * r, .42 * r, -120 + 15 * i, col)
    return e

def stripes(col, n=7, wav=0.12):
    def e(cv, r, rng):
        for i in range(n):
            x = (-1 + (i + .5) * 2 / n) * r; path = skia.Path(); path.moveTo(x, -r)
            for k in range(1, 9): path.lineTo(x + (wav * r if k % 2 else -wav * r), -r + k * r / 4)
            cv.drawPath(path, P(C(col), stroke=.11 * r))
    return e

def lattice(col):
    def e(cv, r, rng):
        for i in range(-4, 5):
            cv.drawLine(i * .35 * r - r, -r, i * .35 * r + r, r, P(C(col, 160), stroke=.035 * r))
            cv.drawLine(i * .35 * r + r, -r, i * .35 * r - r, r, P(C(col, 160), stroke=.035 * r))
    return e

def netting(col):
    def e(cv, r, rng):
        for _ in range(16):
            x0, y0 = rng.uniform(-1, 1) * r, rng.uniform(-1, 1) * r; path = skia.Path(); path.moveTo(x0, y0)
            path.quadTo(x0 + rng.uniform(-.3, .3) * r, y0 + rng.uniform(-.3, .3) * r, x0 + rng.uniform(-.4, .4) * r, y0 + rng.uniform(-.4, .4) * r)
            cv.drawPath(path, P(C(col, 140), stroke=.03 * r))
    return e

def crease(cv, r, rng):
    path = skia.Path(); path.moveTo(0, -.95 * r); path.quadTo(.25 * r, 0, 0, .95 * r); cv.drawPath(path, P(C('#E8806A', 140), stroke=.05 * r))

def dimples(cv, r, rng):
    for _ in range(40):
        a = rng.uniform(0, 2 * math.pi); dd = r * math.sqrt(rng.uniform(0, .95)); cv.drawCircle(dd * math.cos(a), dd * math.sin(a), .025 * r, P(C('#E07A00', 110)))

def pineapple_top(cv, r, rng):
    crown('#2F8F46', 6)(cv, r, rng)


# ---------------------------------------------------------------- NOMBRES (façon 2048)
NUM_COL = ['#EEE4DA', '#EDE0C8', '#F2B179', '#F59563', '#F67C5F', '#F65E3B', '#EDCF72', '#EDCC61', '#EDC850', '#EDC53F', '#EDC22E']
def number(i):
    val = 2 ** (i + 2)
    def d(cv, r, rng):
        base = NUM_COL[i + 1]; cv.drawCircle(0, 0, r, P(C(base)))
        cv.drawCircle(0, 0, r, P(shader=radial(-.3 * r, -.35 * r, 1.3 * r, [skia.Color(255, 255, 255, 60), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 70)], [0, .6, 1])))
        cv.drawCircle(0, 0, r - r * .03, P(C('#000000', 60), stroke=r * .05))
        s = str(val); size = r * (1.15 if len(s) == 1 else .95 if len(s) == 2 else .72 if len(s) == 3 else .56)
        f = skia.Font(TF['anton'], size); w = f.measureText(s)
        cv.drawString(s, -w / 2, size * .36, f, P(C('#776E65' if i < 1 else '#FFFFFF')))
        if i == 9: cv.drawCircle(0, 0, r * 1.08, P(C('#FFE27A', 120), blur=r * .12))
    return d


THEMES = {
    'planets': dict(
        title1='CAN IT REACH', title2='THE SUN?', accent='#FFC21A', bg=('#0A0D1F', '#030409'), stars=True,
        tiers=[('MOON', moon, '#D8D5CC'), ('MERCURY', mercury, '#B9A595'), ('MARS', mars, '#E2683A'), ('VENUS', venus, '#F2CC80'),
               ('EARTH', earth, '#3D8BE0'), ('NEPTUNE', neptune, '#4C70F0'), ('URANUS', uranus, '#8FDCE6'), ('SATURN', saturn, '#E3C98E'),
               ('JUPITER', jupiter, '#D9A877'), ('SUN', sun, '#FFC21A')],
        next_tease='BLACK HOLE'),
    'fruits': dict(
        title1='CAN IT REACH', title2='THE WATERMELON?', accent='#FF5A6E', bg=('#101425', '#05060B'), stars=False,
        tiers=[('CHERRY', fruit('#FF5A6E', '#B0122C', stem=True), '#E5233F'), ('STRAWBERRY', fruit('#FF6B6B', '#C0182A', seeds('#FFE08A'), dark='#3A0D0D'), '#F0414F'),
               ('GRAPE', fruit('#B67CFF', '#5B1FA8'), '#8E4BE0'),
               ('ORANGE', fruit('#FFC066', '#F07800', dimples), '#FF9A1F'), ('APPLE', fruit('#FF6B5E', '#B81D24', stem=True, leaves=1), '#E5383B'),
               ('PEAR', fruit('#E4F28C', '#9BB536', stem=True), '#C5D86D'), ('PEACH', fruit('#FFD0B8', '#F2846A', crease), '#FFB09A'),
               ('PINEAPPLE', fruit('#FFE07A', '#D9981A', lattice('#B5761A')), '#F4C430'), ('MELON', fruit('#DDF7B4', '#86B85A', netting('#F4FFE6')), '#B5E48C'),
               ('WATERMELON', fruit('#57B96F', '#1D5E34', stripes('#174A2A')), '#2D8A4F')],
        next_tease='GOLDEN FRUIT'),
    'numbers': dict(
        title1='CAN IT REACH', title2='2048?', accent='#EDC22E', bg=('#14121C', '#060509'), stars=False,
        tiers=[(str(2 ** (i + 2)), number(i), NUM_COL[i + 1]) for i in range(10)],
        next_tease='4096'),
}


def radii(n, r0=24.0, rmax=212.0):
    q = (rmax / r0) ** (1 / (n - 1)); return [r0 * q ** i for i in range(n)]


def sprite(theme, tier, r, seed=7):
    """image skia de l'objet (rayon r), centrée, avec marge pour anneaux/halos"""
    size = int(math.ceil(r * 3.4)) + 4; surf = skia.Surface(size, size); cv = surf.getCanvas(); cv.clear(skia.Color(0, 0, 0, 0))
    cv.translate(size / 2, size / 2); THEMES[theme]['tiers'][tier][1](cv, r, random.Random(seed * 100 + tier))
    return surf.makeImageSnapshot()
