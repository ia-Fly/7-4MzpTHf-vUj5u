"""FROMAGISTAN — moteur d'épisode : cale les répliques sur la voix, dessine les sous-titres, mixe le son, écrit la vidéo.
Un épisode = un fichier Python (voir ep1.py) qui donne LINES, SFX et frame(t, T, p)."""
import difflib, json, math, os, re, subprocess, unicodedata
from PIL import Image
import rig
from rig import W, H, SS, FPS, Pen, font

NUM = dict(ZERO='0', UN='1', UNE='1', DEUX='2', TROIS='3', QUATRE='4', CINQ='5', SIX='6', SEPT='7', HUIT='8', NEUF='9', DIX='10')


def norm(t):
    t = re.sub(r'[^A-Z0-9 ]', ' ', unicodedata.normalize('NFD', t.upper()).encode('ascii', 'ignore').decode())
    return [NUM.get(w, w) for w in t.split()]


def align(lines, words_json):
    """Début de chaque réplique (en s) : mots du script retrouvés dans la transcription minutée ; les trous sont interpolés."""
    w = json.load(open(words_json, encoding='utf-8')); w = w['words'] if isinstance(w, dict) else w
    heard = [(n, o['start'], o['end']) for o in w if o.get('type', 'word') == 'word' for n in norm(o['text'])]
    script = [(n, i) for i, (_, txt) in enumerate(lines) for n in norm(txt)]
    sm = difflib.SequenceMatcher(None, [a for a, _ in script], [h for h, _, _ in heard], autojunk=False)
    tok = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): tok[a + k] = heard[b + k]
    first = {}; pos = 0; starts = []
    for i, (_, txt) in enumerate(lines):
        n = len(norm(txt)); hit = [tok[k] for k in range(pos, pos + n) if k in tok][:1]; starts.append(hit[0][1] if hit and (pos in tok or pos + 1 in tok) else None); pos += n
    end = heard[-1][2]; starts[0] = starts[0] if starts[0] is not None else 0.0
    for i, s in enumerate(starts):
        if s is None:
            j = next((k for k in range(i + 1, len(starts)) if starts[k] is not None), None); a = starts[i - 1]; b = starts[j] if j else end
            starts[i] = a + (b - a) / ((j or len(starts)) - i + 1)
    T = {lid: s for (lid, _), s in zip(lines, starts)}; T['end'] = end
    return T


def captions(lines, T):
    """Sous-titres par groupes de 3 mots au plus, répartis sur la durée de la réplique selon leur longueur."""
    out = []; ids = [l for l, _ in lines]
    for i, (lid, txt) in enumerate(lines):
        t0 = T[lid]; t1 = (T[ids[i + 1]] if i + 1 < len(ids) else T['end']); ws = txt.split(); groups = []; cur = []
        for wd in ws:
            cur.append(wd)
            if len(cur) == 3 or wd[-1] in '.!?:…': groups.append(' '.join(cur)); cur = []
        if cur: groups.append(' '.join(cur))
        tot = sum(len(g) + 2 for g in groups); a = t0
        for g in groups:
            b = a + (t1 - t0) * (len(g) + 2) / tot; out.append((a, b, g)); a = b
    return out


def draw_caption(p, caps, t, y=1490):
    for a, b, g in caps:
        if a <= t < b:
            k = min(1, (t - a) / .08); f = font(int(86 * (.9 + .1 * k)), 'Anton-Regular.ttf')
            p.d.text((W / 2 * SS, y * SS), g.upper(), font=f, fill=(255, 255, 255), anchor='mm', stroke_width=9 * SS, stroke_fill=(40, 30, 70)); return


def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def pop(t, t0, d=.25):
    """Échelle d'apparition avec petit dépassement (0 avant t0)."""
    x = (t - t0) / d
    return 0 if x < 0 else (1 + .18 * math.sin(min(1, x) * math.pi) if x < 1 else 1)


def card(p, x, y, w, h, text, bg, fg=(255, 255, 255), size=58, k=1.0, sub=None):
    if k <= 0: return
    w, h = w * k, h * k; p.rect(x - w / 2, y - h / 2 + 8, x + w / 2, y + h / 2 + 8, tuple(max(0, c - 60) for c in bg), r=28 * k); p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, bg, r=28 * k)
    p.text(x, y - (h * .17 if sub else 0), text, font(int(size * k * (.9 if sub else 1))), fg)
    if sub: p.text(x, y + h * .26, sub, font(int(size * .62 * k)), fg)


def compose(frame, t, cam=None):
    """Une image finale : le monde (dessiné puis cadré par la caméra) + l'interface (cartes, bandeau, sous-titres) posée par-dessus, hors caméra."""
    world = Image.new('RGBA', (W * SS, H * SS)); ui = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); frame(t, Pen(world), world, Pen(ui))
    if cam: world = rig.camera(world, *cam(t))
    return Image.alpha_composite(world.convert('RGBA'), ui).resize((W, H), Image.LANCZOS).convert('RGB')


def shot_cam(shots, T, order, face_y=800):
    """Caméra par plans : shots = {réplique: (zoom, x, y, scène)} ; le point (x, y) est amené vers le haut-milieu de l'écran.
    Coupe franche entre deux scènes, glissé de 0,4 s dans une même scène, petit zoom d'attaque, lente avancée et léger balancement gauche-droite."""
    keys = [k for k in order if k in shots]
    def cam(t):
        i = max([n for n, k in enumerate(keys) if T[k] <= t] or [0]); z, x, y, sc = shots[keys[i]]; t0 = T[keys[i]]
        if i and shots[keys[i - 1]][3] == sc:
            pz, px, py, _ = shots[keys[i - 1]]; k = ease((t - t0) / .4); z, x, y = pz + (z - pz) * k, px + (x - px) * k, py + (y - py) * k
        u = t - t0; z = z * (1 + .05 * math.exp(-u * 5) + .012 * min(u, 4)); x += 16 * math.sin(t * 1.15) / z; y += 7 * math.sin(t * .8 + 1) / z
        return z, x, y + (H / 2 - face_y) / z
    return cam


def render(frame, total, out_dir, audio, cam=None):
    os.makedirs(out_dir, exist_ok=True); silent = os.path.join(out_dir, 'silent.mp4')
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', silent], stdin=subprocess.PIPE)
    for i in range(int(total * FPS)): ff.stdin.write(compose(frame, i / FPS, cam).tobytes())
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', audio, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(out_dir, 'video.mp4')], check=True); os.remove(silent)


def mix(voice, music, sfx, total, out, music_db=-21, lead=0.0):
    """voix + musique en boucle (baissée) + bruitages [(fichier, temps, dB, durée max)], normalisé à -14 LUFS."""
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', voice, '-stream_loop', '-1', '-i', music]; fc = [f'[0:a]adelay={int(lead * 1000)}:all=1,volume=1.0[v]', f'[1:a]volume={music_db}dB,atrim=0:{total:.3f},afade=t=out:st={total - 1.2:.3f}:d=1.2[m]']; tags = ['[v]', '[m]']
    for k, (f, t, db, dur) in enumerate(sfx):
        cmd += ['-i', f]; fc.append(f'[{k + 2}:a]atrim=0:{dur},afade=t=out:st={max(0, dur - .12):.3f}:d=0.12,volume={db}dB,adelay={int(t * 1000)}:all=1[s{k}]'); tags.append(f'[s{k}]')
    fc.append(''.join(tags) + f'amix=inputs={len(tags)}:normalize=0:duration=longest,atrim=0:{total:.3f},loudnorm=I=-13:TP=-1.5:LRA=11[o]')
    subprocess.run(cmd + ['-filter_complex', ';'.join(fc), '-map', '[o]', '-ar', '48000', '-ac', '2', out], check=True)
