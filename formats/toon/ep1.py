"""FROMAGISTAN · Épisode 1 — « Président par erreur ».
    python3 formats/toon/ep1.py ASSETS OUT [--preview t1,t2,...]
ASSETS : voice.mp3, words.json, theme.mp3 et les bruitages. Sert de modèle aux épisodes suivants."""
import math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import rig, engine, fx
from rig import W, H, SS, Pen, font, banner, gauge
from engine import pop, ease, card

LINES = [('L1', "Je suis devenu président... par erreur."), ('L2', "Je venais juste renouveler mon permis de baguette magique."), ('L3', "J'ai signé le mauvais formulaire."),
         ('L4', "Résultat : me voilà président du Fromagistan !"), ('L5', "Le pays ? Zéro citoyen. Zéro écu. Et un palais sans toit."), ('L6', "Heureusement, ici, c'est toi qui gouvernes."),
         ('L7', "Un abonné, c'est un citoyen."), ('L8', "Un like, deux écus dans la caisse."), ('L9', "Un partage, et ma popularité remonte."), ('L10', "Un enregistrement, et je gagne de la magie."),
         ('L11', "Premier chantier : rallumer la lumière du palais."), ('L12', "Premier sort : j'ai allumé le pigeon."), ('L13', "Deuxième sort : j'ai allumé ma barbe."), ('L14', "Troisième sort : une bougie. Ça marche !"),
         ('L15', "Et maintenant, on fait quoi ?"), ('L16', "Un : réparer le toit."), ('L17', "Deux : ouvrir un marché aux fromages."), ('L18', "Trois : inviter la reine du pays voisin."),
         ('L19', "Vote en commentaire."), ('L20', "Et le commentaire le plus liké deviendra une loi."), ('L21', "Abonne-toi pour devenir citoyen."), ('L22', "Ah, et dans la cave du palais... il y a une porte fermée à clé.")]
SFX = [('win-fanfare.mp3', 'L4', 1.2, -10, 2.0), ('fail-horn.mp3', 'L5', 3.2, -15, 2.0), ('pop.wav', 'L7', .1, -8, .2), ('pop.wav', 'L8', .1, -8, .2), ('coins.mp3', 'L8', .7, -9, 1.2), ('pop.wav', 'L9', .1, -8, .2),
       ('pop.wav', 'L10', .1, -8, .2), ('spell-fail.mp3', 'L12', .75, -9, .48), ('pigeon.mp3', 'L12', 1.25, -12, 1.3), ('spell-fail.mp3', 'L13', .9, -9, .48), ('spell-ok.mp3', 'L14', .9, -4, 2.0),
       ('pop.wav', 'L16', .1, -8, .2), ('pop.wav', 'L17', .1, -8, .2), ('pop.wav', 'L18', .1, -8, .2), ('coins.mp3', 'L21', .8, -9, 1.2)]
Y, V, DARK = (255, 205, 60), (125, 80, 200), (40, 30, 70)
# Plans : réplique -> (zoom, x, y du sujet, scène). Gros plans sur les visages, plan large pour poser le décor.
SHOTS = {'L1': (1.9, 300, 1270, 'mairie'), 'L2': (1.3, 560, 1180, 'mairie'), 'L3': (1.8, 800, 1140, 'mairie'), 'L4': (1.5, 320, 1250, 'mairie'),
         'L5': (1.05, 540, 1000, 'palais'), 'L6': (1.75, 330, 1290, 'palais'), 'L7': (1.0, 540, 820, 'regles'), 'L9': (1.06, 540, 820, 'regles'),
         'L11': (1.3, 540, 1280, 'nuit'), 'L12': (1.8, 800, 1320, 'nuit'), 'L13': (1.9, 300, 1340, 'nuit'), 'L14': (1.45, 470, 1320, 'nuit'),
         'L15': (1.0, 540, 820, 'vote'), 'L19': (1.05, 540, 820, 'vote'), 'L21': (1.4, 560, 1270, 'abo'), 'L22': (1.0, 540, 1000, 'cave')}


def paste(img, bg): img.paste(bg, (0, 0))


def mairie(p, t):
    p.rect(0, 0, W, H, (255, 236, 205)); p.rect(0, 1450, W, H, (214, 170, 120)); p.rect(0, 1435, W, 1462, (190, 145, 100))
    for k in range(6): p.rect(k * 200 - 20, 0, k * 200 + 60, 1435, (252, 226, 190))
    p.rect(640, 470, 1000, 790, (150, 205, 245), r=14); p.rect(812, 470, 828, 790, (255, 250, 240)); p.rect(640, 622, 1000, 638, (255, 250, 240))
    banner(p, 300, 560, 'MAIRIE', font(96), (70, 120, 200)); banner(p, 300, 690, 'GUICHET 3 · PERMIS DE BAGUETTE', font(34), (255, 250, 240), (60, 50, 90))


def desk(p):
    p.rect(560, 1330, W + 40, 1900, (170, 115, 70), r=24); p.rect(540, 1300, W + 40, 1360, (200, 140, 90), r=18)


def night_room(p):
    """Salon du palais la nuit : murs, boiseries, fenêtre à la lune, tapis, cadre au mur. Les couleurs restent celles du jour : c'est fx.darken et la lumière des flammes qui font la nuit."""
    p.rect(0, 0, W, H, (196, 150, 120)); p.rect(0, 1100, W, 1560, (170, 120, 92)); p.rect(0, 1090, W, 1112, (150, 104, 78))
    for k in range(6): p.rect(30 + k * 180, 1140, 170 + k * 180, 1520, (184, 134, 104), r=10)
    p.rect(640, 380, 980, 800, (150, 180, 230), r=170); p.rect(650, 390, 970, 790, (120, 150, 210), r=160); p.circ(860, 520, 54, (255, 250, 225)); p.circ(884, 506, 46, (120, 150, 210))
    p.rect(800, 380, 820, 800, (150, 104, 78)); p.rect(640, 580, 980, 598, (150, 104, 78))
    p.rect(150, 420, 430, 760, (150, 104, 78), r=8); p.rect(170, 440, 410, 740, (120, 150, 120), r=4); p.circ(290, 560, 70, (230, 200, 120))
    p.rect(0, 1560, W, H, (120, 82, 62)); p.ell(540, 1720, 520, 120, (150, 50, 60)); p.ell(540, 1720, 440, 90, (176, 70, 72))


def halo(p, x, y, r, col, n=5):
    for k in range(n, 0, -1): p.circ(x, y, r * k / n, tuple(int(c * (1 - .12 * k) + 20 * k) for c in col))


def cellar(p, t, img):
    p.rect(0, 0, W, H, (92, 86, 120))
    for r in range(9):
        for c in range(5): p.rect(c * 240 - (120 if r % 2 else 0) + 6, r * 200 + 6, c * 240 - (120 if r % 2 else 0) + 234, r * 200 + 194, (112, 106, 142), r=14)
    p.rect(0, 1560, W, H, (70, 64, 90)); p.rect(300, 690, 780, 1560, (88, 78, 100), r=230)
    p.rect(330, 720, 750, 1560, (110, 72, 44), r=200); p.rect(360, 760, 720, 1560, (135, 90, 56), r=180)
    for k in range(3): p.rect(330, 900 + k * 230, 750, 930 + k * 230, (70, 70, 84))
    p.circ(540, 1150, 46, (60, 45, 30)); p.ell(540, 1150, 16, 18, (255, 236, 150)); p.poly([(532, 1156), (548, 1156), (556, 1196), (524, 1196)], (255, 236, 150))
    fx.darken(img, .82); g = .8 + .2 * math.sin(t * 5)
    fx.glow(img, 540, 1170, 140, (255, 200, 80), .9 * g, falloff=1.3); fx.glow(img, 540, 1565, 420, (190, 140, 50), .7 * g, ry=50); fx.glow(img, 540, 1300, 720, (90, 70, 30), .5 * g)
    for i in range(10):                                                  # poussière dorée dans la lumière
        life = (t * .25 + i * .37) % 1; fx.glow(img, 440 + (i * 53) % 220 + 30 * math.sin(t + i), 1560 - life * 600, 10, (255, 220, 140), .9 * math.sin(life * math.pi))


def candle(img, p, x, y, t, a): fx.candle(img, p, x, y, t, a)


def top(u):
    banner(u, 540, 150, 'FROMAGISTAN · ÉPISODE 1', font(44), Y, (60, 40, 20))


def frame(t, T, p, img, caps, bgs, u):
    L = lambda k: T[k]; cy = 1490
    if t < L('L5'):                                                      # la mairie
        mairie(p, t); desk(p); rig.citizen(p, 860, 1410, .85, t, (70, 150, 230), 'talk' if t < L('L3') else 'cheer', off=.4)
        desk(p); k = pop(t, L('L3') + .2)
        if k: p.rect(700 - 130 * k, 1220 - 80 * k, 700 + 130 * k, 1300, (255, 255, 255), r=8); p.text(700, 1255, 'FORMULAIRE 12-B', font(int(32 * k)), DARK)
        act = 'wave' if t < L('L2') else ('talk' if t < L('L4') else 'cheer'); rig.barbichu(p, 300, 1650, 1.1, t, act, talk=t < L('L4') + 2.5); cy = 900
        if t >= L('L4') + 1.1:
            for i in range(26):
                cx = (i * 97) % W; cy = ((t - L('L4') - 1.1) * (500 + (i * 53) % 300) + i * 61) % 1300; p.rect(cx, cy, cx + 18, cy + 30, [(255, 90, 120), Y, (90, 200, 250), (120, 230, 140)][i % 4], r=4)
            card(u, 540, 330, 760, 150, 'PRÉSIDENT !', (230, 70, 90), size=96, k=pop(t, L('L4') + 1.1))
    elif t < L('L7'):                                                    # le pays
        paste(img, bgs['palais']); rig.pigeon(p, 860, 1620, .8, t, 'idle'); rig.barbichu(p, 330, 1650, 1.05, t, 'talk' if t < L('L6') else 'wave', talk=True); cy = 1100
        if t < L('L6'):
            for i, (lab, d) in enumerate((('CITOYENS : 0', .8), ('BUDGET : 0 ÉCU', 2.0), ('TOIT : 0 %', 2.9))): card(u, 540, 330 + i * 150, 620, 120, lab, DARK, size=62, k=pop(t, L('L5') + d))
        else: card(u, 540, 380, 900, 170, "C'EST TOI QUI GOUVERNES", (230, 70, 90), size=78, k=pop(t, L('L6') + .9))
    elif t < L('L11'):                                                   # les règles du jeu
        p.rect(0, 0, W, H, (92, 62, 170))
        for i in range(14): p.star((i * 173) % W, (i * 291 + 40 * math.sin(t + i)) % 1300 + 60, 14 + (i % 3) * 6, (120, 88, 200))
        banner(u, 540, 300, 'LES RÈGLES DU JEU', font(84), Y, (60, 40, 20))
        rules = (('L7', '1 ABONNÉ', '= 1 CITOYEN', (70, 190, 120)), ('L8', '1 LIKE', '= +2 ÉCUS', (235, 80, 100)), ('L9', '1 PARTAGE', '= +3 POPULARITÉ', (60, 140, 235)), ('L10', '1 ENREGISTREMENT', '= +1 MAGIE', (240, 160, 40)))
        for i, (lid, a, b, col) in enumerate(rules): card(u, 540, 520 + i * 215, 900, 180, a, col, size=76, k=pop(t, L(lid) + .1), sub=b)
    elif t < L('L15'):                                                   # premier chantier : la lumière
        t_cast = [L('L12') + .45, L('L13') + .55, L('L14') + .55]; lit = ease((t - L('L14') - .9) / .6)
        night_room(p); pg = (810, 1620); on_pigeon = L('L12') + .8 <= t < L('L14')
        fx.darken(img, .78 - .38 * lit)                                     # nuit, puis la bougie réchauffe la pièce
        fx.glow(img, 810, 590, 520, (40, 60, 110), .45)                      # clair de lune par la fenêtre
        if on_pigeon:
            k = ease((t - L('L12') - .8) / .3) * (.9 + .1 * math.sin(t * 17)); fx.glow(img, pg[0], pg[1] - 200, 760, (150, 120, 40), .55 * k, falloff=1.4); fx.glow(img, pg[0], pg[1] + 10, 260, (120, 90, 30), .5 * k, ry=60)
        b = rig.barbichu(p, 300, 1650, 1.05, t, 'wave' if t < L('L14') + .9 else 'cheer', talk=True); hx, hy, r = b['head']
        rig.pigeon(p, pg[0], pg[1], .9, t, 'idle', talk=on_pigeon)
        if on_pigeon:
            k = ease((t - L('L12') - .8) / .3); fx.glow(img, pg[0], pg[1] - 170, 230, (200, 170, 70), .75 * k, falloff=1.2)   # le pigeon brille de l'intérieur
            fx.sparkles(img, pg[0], pg[1] - 200, (t - L('L12') - .8) % 1.0 + L('L12') + .8, L('L12') + .8, r=200, n=10, dur=1.0)
        candle_x, candle_y = 560, 1440
        tgt = [(pg[0], pg[1] - 170), (hx, hy + r * 1.1), (candle_x, candle_y - 20)]
        for tc, tg in zip(t_cast, tgt): fx.bolt(img, b['staff'], tg, t, tc - .35); fx.sparkles(img, *tg, t, tc, r=170, seed=tc)
        for tc in t_cast: fx.flash(img, t, tc, col=(255, 220, 170), a=.18)
        if t >= L('L13') + 1.0:                                              # barbe roussie jusqu'à la fin de la scène
            c = min(1, (t - L('L13') - 1.0) / 1.2); dk = tuple(int(255 - (255 - v) * c) for v in (70, 60, 62))
            p.poly([(hx - r * .34, hy + r * 1.36), (hx + r * .34, hy + r * 1.36), (hx + r * .12, hy + r * 1.9), (hx, hy + r * 2.3), (hx - r * .14, hy + r * 1.85)], dk)
            for j, (dx, dy) in enumerate(((-.5, 1.2), (.4, 1.25), (-.15, 1.4), (.2, 1.5))): p.circ(hx + dx * r, hy + dy * r, r * .12, tuple(int(255 - (255 - v) * c) for v in (110, 100, 104)))
            if t < L('L14') + 2.5: fx.glow(img, hx + r * .1, hy + r * 1.6, 26, (255, 120, 40), .7 * (.6 + .4 * math.sin(t * 9)))   # une braise qui reste
        bx, by = b['beard']; burn = L('L13') + .55 <= t < L('L14') + .9
        if burn:
            k = min(1, (t - L('L13') - .55) / .3) * (1 if t < L('L14') + .6 else max(0, (L('L14') + .9 - t) / .3))
            fx.fire(img, bx, by + r * 1.05, r * 1.1, r * 1.45, t, k, seed=2, n=6, smoke=False)
            fx.glow(img, hx, hy + r * .2, r * 1.3, (120, 60, 20), .35 * k, falloff=1.4)            # la flamme éclaire le visage
        if lit > 0 or t >= L('L14') + .55: candle(img, p, candle_x, candle_y, t, max(.05, lit))
        if L('L14') + .9 <= t < L('L14') + 1.6:                             # une fumée s'échappe de la barbe éteinte
            q = (t - L('L14') - .9) / .7; fx.glow(img, bx, by + r * .6 - 120 * q, 120 + 80 * q, (60, 60, 64), .5 * (1 - q))
        if t < L('L12'): card(u, 540, 330, 880, 150, 'CHANTIER 1 : LA LUMIÈRE', Y, (60, 40, 20), size=70, k=pop(t, L('L11') + .2))
        for lid, d, lab, col in (('L12', .8, 'PIGEON : ALLUMÉ', (230, 70, 90)), ('L13', .9, 'BARBE : ALLUMÉE', (230, 70, 90)), ('L14', .9, 'LUMIÈRE : 1 BOUGIE', (70, 190, 120))):
            nxt = {'L12': 'L13', 'L13': 'L14', 'L14': 'L15'}[lid]
            if L(lid) + d <= t < L(nxt): card(u, 540, 330, 820, 150, lab, col, size=74, k=pop(t, L(lid) + d))
    elif t < L('L21'):                                                   # le vote
        p.rect(0, 0, W, H, (60, 130, 220))
        for i in range(10): p.circ((i * 211) % W, (i * 331) % 1300 + 80, 60 + (i % 3) * 30, (72, 142, 230))
        banner(u, 540, 300, 'ON FAIT QUOI ?', font(96), Y, (60, 40, 20))
        ch = (('L16', '1 · RÉPARER LE TOIT', '400 ÉCUS', (230, 80, 90)), ('L17', '2 · MARCHÉ AUX FROMAGES', '150 ÉCUS', (240, 160, 40)), ('L18', '3 · INVITER LA REINE', '0 ÉCU', (130, 90, 210)))
        for i, (lid, a, b, col) in enumerate(ch): card(u, 540, 520 + i * 230, 940, 195, a, col, size=66, k=pop(t, L(lid) + .1), sub=b)
        if t >= L('L19'): card(u, 540, 1220, 940, 130, 'VOTE EN COMMENTAIRE : 1, 2 OU 3' if t < L('L20') else 'COMMENTAIRE LE PLUS LIKÉ = UNE LOI', DARK, size=52, k=pop(t, L('L19') if t < L('L20') else L('L20')))
        rig.barbichu(p, 170, 1900, .62, t, 'talk', talk=True); rig.pigeon(p, 930, 1880, .55, t, 'idle')
    elif t < L('L22'):                                                   # abonne-toi
        paste(img, bgs['palais']); done = t >= L('L21') + .8; cy = 1100
        card(u, 540, 430, 720, 190, 'CITOYEN +1' if done else "S'ABONNER", (70, 190, 120) if done else (230, 60, 70), size=96, k=pop(t, L('L21') + .05) if not done else pop(t, L('L21') + .8))
        rig.barbichu(p, 330, 1650, 1.05, t, 'cheer' if done else 'talk', talk=True)
        if done: rig.citizen(p, 800, 1650, .9 * pop(t, L('L21') + .8), t, (230, 80, 80), 'cheer')
    else:                                                                # le mystère de la cave
        cellar(p, t, img); k = pop(t, L('L22') + 1.9, .4)
        if k: u.text(540, 520, '?', font(int(380 * k)), Y)
        card(u, 540, 1700, 820, 130, 'ÉPISODE 2 : LA PORTE DE LA CAVE', DARK, size=50, k=pop(t, L('L22') + 2.4))
    top(u); engine.draw_caption(u, caps, t, 1500)


def cover(bgs, out):
    img = Image.new('RGBA', (W * SS, H * SS)); paste(img, bgs['palais']); p = Pen(img); rig.pigeon(p, 850, 1700, .85, 1.0); rig.barbichu(p, 400, 1760, 1.3, .4, 'cheer')
    p.rect(60, 250, 1020, 760, DARK, r=40); p.text(540, 370, 'FROMAGISTAN', font(150), Y); p.text(540, 520, 'ÉPISODE 1', font(96), (255, 255, 255)); p.text(540, 660, 'PRÉSIDENT PAR ERREUR', font(78), (255, 120, 150))
    img.resize((W, H), Image.LANCZOS).convert('RGB').save(out, quality=92)


if __name__ == '__main__':
    A, O = sys.argv[1], sys.argv[2]; os.makedirs(O, exist_ok=True); T = engine.align(LINES, os.path.join(A, 'words.json')); caps = engine.captions(LINES, T); total = T['end'] + 1.6
    print({k: round(v, 2) for k, v in T.items()}, 'total', round(total, 2))
    bgs = {'palais': rig.background(0.0)}
    def fr(t, p, img, u): frame(min(t, total - .01), T, p, img, caps, bgs, u)
    cam = engine.shot_cam(SHOTS, T, [l for l, _ in LINES])
    if '--preview' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--preview') + 1].split(',')]; sheet = Image.new('RGB', (360 * len(ts), 640))
        for i, t in enumerate(ts): sheet.paste(engine.compose(fr, t, cam).resize((360, 640), Image.LANCZOS), (360 * i, 0))
        sheet.save(os.path.join(O, 'preview.jpg'), quality=88); sys.exit()
    if not os.path.exists(os.path.join(A, 'pop.wav')):                   # petit « pop » synthétique (le bruitage généré était muet)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=f=720:d=0.09', '-af', 'afade=t=out:st=0.02:d=0.07,asetrate=44100*1.3,aresample=44100', os.path.join(A, 'pop.wav')], check=True)
    mixf = os.path.join(O, 'mix.wav'); engine.mix(os.path.join(A, 'voice.mp3'), os.path.join(A, 'theme.mp3'), [(os.path.join(A, f), T[l] + d, db, dur) for f, l, d, db, dur in SFX], total, mixf)
    cover(bgs, os.path.join(O, 'cover.jpg')); engine.render(fr, total, O, mixf, cam)
