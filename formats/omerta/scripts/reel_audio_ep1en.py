"""Bande son de l'épisode 1 en anglais (version rapide, ~23 s).
Reel « omertà » 20 s, version rapide : voix + pulsation + coupes + impacts calés sur planches/timeline4.json.
usage: reel_audio_v4.py out_dir"""
import json, sys, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve

S = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + '/'
OUT = sys.argv[1]
TL = json.load(open(S + 'planches/timeline_ep1en.json')); EV, SEG, SHOTS = TL['ev'], TL['seg'], TL['shots']
SR = 48000; DUR = EV['END']; N = int(SR * DUR)
rng = np.random.default_rng(23)
def bp(x, lo, hi, order=4): return sosfilt(butter(order, [lo, min(hi, SR / 2 - 100)], btype='band', fs=SR, output='sos'), x)
def lp(x, f, order=4): return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)
def hp(x, f, order=4): return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)
def tt(d): return np.arange(int(d * SR)) / SR
def db(x): return 10 ** (x / 20)
class Bus:
    def __init__(self): self.L = np.zeros(N); self.R = np.zeros(N)
    def place(self, sig, t, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= N or i + len(sig) <= 0: return
        if i < 0: sig = sig[-i:]; i = 0
        sig = sig[: N - i]; gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.L[i:i + len(sig)] += sig * gain * gl * 1.414; self.R[i:i + len(sig)] += sig * gain * gr * 1.414
    def st(self): return np.stack([self.L, self.R], 1)
voice, mus, hit = Bus(), Bus(), Bus()

# ---------------- VOIX ----------------
def load_voice(path):
    x, sr = sf.read(path); x = x.astype(np.float64)
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = resample_poly(x, SR // 100, sr // 100)
    return hp(x, 70)
def room_ir(dur=0.4, decay=10.0, dark=5000):
    x = tt(dur); ir = rng.normal(0, 1, len(x)) * np.exp(-x * decay); ir = lp(ir, dark); ir[0] = 0
    for d, g in ((0.011, 0.5), (0.017, 0.35), (0.029, 0.25)): ir[int(d * SR)] += g
    return ir / np.sqrt(np.sum(ir ** 2))
IR, IRB = room_ir(), room_ir(0.9, 4.5, 3200)
def treat(x, wet, ir, target):
    rms = np.sqrt(np.mean(x[np.abs(x) > 0.02 * np.abs(x).max()] ** 2)); x = x / rms * db(target)
    w = fftconvolve(x, ir)[: len(x) + int(0.3 * SR)]; y = np.zeros(len(w)); y[:len(x)] += x; y += wet * w
    return np.tanh(y * 1.2) / 1.2
spans = []
for k, t0 in SEG.items():
    x = load_voice(TL['voice'][k])
    if k.startswith('b'): x = lp(x, 8000); x = x + 0.35 * bp(x, 1800, 4500); x = treat(x, 0.03, IRB, -13.0); pan = 0.1
    else: x = treat(x, 0.08, IR, -17); pan = 0.0
    voice.place(x, t0, 1.0, pan); spans.append((t0, t0 + len(x) / SR - 0.3, k.startswith('b')))
gate = np.zeros(N)
for a, b, isb in spans: gate[int(a * SR): int(b * SR)] = 1.6 if isb else 1.0
env = np.zeros(N); up, down = 1 / (0.03 * SR), 1 / (0.2 * SR); e = 0.0
for i in range(0, N, 48):
    tg = gate[i]; e = min(tg, e + up * 48) if tg > e else max(tg, e - down * 48); env[i:i + 48] = e
DUCK = np.clip(1 - (1 - db(-6)) * env, db(-11), 1)

# ---------------- ÉLÉMENTS ----------------
def click(d=0.012, f=3200):
    x = tt(d); return bp(rng.normal(0, 1, len(x)), f * 0.6, f * 1.6) * np.exp(-x * 420)
def thud(f0=58, d=0.9, drop=0.5, nz=0.3):
    x = tt(d); f = f0 * (1 + drop * np.exp(-x * 18))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 4.2) + lp(rng.normal(0, 1, len(x)), 900) * np.exp(-x * 30) * nz
def boom(d=2.0):
    x = tt(d); f = 70 * np.exp(-x * 2.2) + 30
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.0) + lp(rng.normal(0, 1, len(x)), 500) * np.exp(-x * 6) * 0.5
    return s
def whoosh(bus, d, f0, f1, gain, t0, pan=0.0):
    x = tt(d); n = rng.normal(0, 1, len(x)); lo, hi = min(f0, f1), max(f0, f1)
    a = bp(n, lo * 0.7, lo * 1.6); b = bp(n, hi * 0.6, hi * 1.5); k = x / d if f1 > f0 else 1 - x / d
    bus.place((a * (1 - k) + b * k) * np.sin(np.pi * np.clip(x / d, 0, 1)) ** 2, t0, gain, pan)
def ting(f=2210):
    x = tt(1.4)
    s = sum(a * np.sin(2 * np.pi * f * m * x + p) * np.exp(-x * dcy) for m, a, p, dcy in ((1, 0.6, 0, 3.2), (1.534, 0.45, 1, 4.5), (2.317, 0.3, 2, 6.0), (0.661, 0.35, 0.5, 2.6)))
    return s + hp(rng.normal(0, 1, len(x)), 3000) * np.exp(-x * 160) * 0.8
def scrape(d=0.5):
    x = tt(d); am = (1 + np.sign(np.sin(2 * np.pi * 38 * x)) * 0.5) * np.sin(np.pi * x / d)
    return bp(rng.normal(0, 1, len(x)), 500, 1800) * am
def paper(d=0.6):
    x = tt(d); n = rng.normal(0, 1, len(x)); env = np.sin(np.pi * x / d) ** 1.5 * (1 + 0.4 * np.sin(2 * np.pi * 23 * x))
    return (bp(n, 2500, 9000) * 0.6 + bp(n, 600, 1500) * 0.4) * env
def shutter():
    a = click(0.012, 3800) * 1.4; b = click(0.02, 1800); out = np.zeros(int(0.12 * SR)); out[:len(a)] += a; j = int(0.055 * SR); out[j:j + len(b)] += b; return out
def flint():
    x = tt(0.2); s = hp(rng.normal(0, 1, len(x)), 2500) * np.exp(-x * 25); c = click(0.01, 5000) * 1.5; s[:len(c)] += c
    y = tt(0.6); s2 = bp(rng.normal(0, 1, len(y)), 200, 1200) * np.sin(np.pi * y / 0.6) * 0.6
    out = np.zeros(len(y)); out[:len(s)] += s; out += s2; return out
def tick():
    x = tt(0.05); return bp(rng.normal(0, 1, len(x)), 2000, 6000) * np.exp(-x * 300) + np.sin(2 * np.pi * 1400 * x) * np.exp(-x * 200) * 0.4
def crackle(t0, t1, gain):
    k = t0
    while k < t1:
        x = tt(0.03); s = hp(rng.normal(0, 1, len(x)), 1800) * np.exp(-x * rng.uniform(150, 400))
        hit.place(s * rng.uniform(0.3, 1.0), k, gain, rng.uniform(-0.3, 0.4)); k += rng.exponential(0.025)
    x = np.arange(int((t1 - t0) * SR)) / SR
    hit.place(lp(rng.normal(0, 1, len(x)), 320) * np.clip(x / 0.15, 0, 1) * np.clip((t1 - t0 - x) / 0.3, 0, 1), t0, gain * 1.2)

t = np.arange(N) / SR
# ---------------- PULSATION (128 BPM) + nappe ----------------
BPM = 128; beat = 60 / BPM
pulse_env = np.zeros(N)
k = 0.0
while k < DUR:
    i = int(k * SR); x = tt(0.4); pulse_env[i:i + len(x)] = np.maximum(pulse_env[i:i + len(x)], np.exp(-x * 9)[: N - i]); k += beat
drone = np.sin(2 * np.pi * 41.2 * t) * 0.9 + np.sin(2 * np.pi * 55.0 * t + 0.7) * 0.5 + np.sin(2 * np.pi * 82.4 * t + 1.3) * 0.2
inten = np.interp(t, [0, 3.0, 3.86, 6.6, 8.2, 9.96, 11.37, 12.64, 13.45, 17.9, 19.0, SEG['n10'], EV['next'], DUR - 0.6, DUR],
                     [0.55, 0.7, 0.8, 0.85, 0.75, 0.85, 1.0, 0.25, 1.0, 0.9, 1.0, 0.75, 0.95, 0.95, 0.0])
mus.place(drone * (0.35 + 0.65 * pulse_env) * inten * db(-20), 0)
kick = np.zeros(N); k = 0.0
while k < DUR:
    x = tt(0.35); f = 55 * (1 + 1.2 * np.exp(-x * 30)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 7)
    i = int(k * SR); kick[i:i + len(s)] += s[: N - i]; k += beat
kick_gate = np.interp(t, [0, 1.4, 1.45, 12.5, 12.64, 13.4, 13.45, DUR - 0.7, DUR], [0, 0, 1, 1, 0, 0, 1, 1, 0])
mus.place(lp(kick, 200) * kick_gate * inten * db(-17), 0)
# tic-tac en croches à partir de la règle
k = EV['rule'][0]
while k < DUR - 0.6:
    if not (EV['lamp_on'] - 1.25 < k < EV['parrain']): mus.place(tick(), k, db(-29) * (1.0 if int(k / (beat / 2)) % 2 == 0 else 0.6), pan=0.25)
    k += beat / 2
# montée avant la révélation
x = tt(EV['lamp_on'] - EV['days'][1]); r = x / x[-1]
riser = bp(rng.normal(0, 1, len(x)), 400, 6000) * r ** 2 * 0.6 + np.sin(2 * np.pi * np.cumsum(200 + 900 * r ** 2) / SR) * r ** 2 * 0.3
mus.place(riser, EV['days'][1], db(-22))
mus.L *= DUCK; mus.R *= DUCK

# ---------------- COUPES ET IMPACTS ----------------
for sh in SHOTS[1:]: whoosh(hit, 0.2, 2500, 500, db(-31), sh[0] - 0.2, pan=rng.uniform(-0.4, 0.4))
hit.place(lp(boom(1.6), 250), EV['mourn'] + 0.1, db(-11))
hit.place(lp(thud(52), 300), EV['debt'] + 0.12, db(-13))
hit.place(lp(boom(1.4), 250), EV['mafia'] + 0.15, db(-11))
x = tt(0.6); f = 300 + 700 * (x / 0.6) ** 1.5
hit.place(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / 0.6) ** 2, EV['string_draw'][0], db(-27), pan=0.3)
hit.place(flint(), EV['flame'] - 0.4, db(-15), pan=0.1)
hit.place(boom(2.2), EV['fire'], db(-6)); whoosh(hit, 0.7, 150, 1200, db(-20), EV['fire'] - 0.55)
crackle(EV['fire'] + 0.05, SEG['n04'] + 0.2, db(-24))
hit.place(ting(), EV['snap'] + 0.2, db(-17), pan=0.35); hit.place(lp(thud(90, 0.4, 1.0, 0.6), 400), EV['snap'] + 0.12, db(-13))
hit.place(lp(thud(46, 1.0, 0.6), 400), EV['rule'][0], db(-12)); hit.place(lp(thud(40, 1.3, 0.7, 0.5), 400), EV['jamais'], db(-8))
d0, d1 = EV['days']
for i in range(4): whoosh(hit, 0.3, 400, 2200, db(-27), d0 + i * (d1 - d0) / 4, pan=0.2)
L0 = EV['lamp_on']
hit.place(click(0.02, 2500) * 2.0, L0, db(-11), pan=0.45); hit.place(click(0.02, 2500) * 1.3, L0 + 0.07, db(-15), pan=0.45)
x = tt(1.2); f = 85 * np.exp(-x * 1.1) + 28; hit.place(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 1.8), L0 + 0.02, db(-9))
hit.place(boom(2.0), EV['parrain'], db(-7))
hit.place(paper(0.6), EV['photo_slide'][0], db(-20), pan=0.3)
hit.place(shutter(), EV['inset'][0] + 0.25, db(-17)); hit.place(lp(thud(50, 0.9, 0.5), 300), EV['inset'][0] + 0.1, db(-12))
whoosh(hit, 0.5, 200, 1500, db(-25), EV['feu'] + 0.15)
hit.place(lp(thud(38, 1.4, 0.4, 0.4), 300), SEG['b14'] - 0.32, db(-10))
hit.place(lp(thud(70, 0.3, 0.6, 0.2), 300), EV['chair'] + 0.05, db(-16), pan=0.3); hit.place(lp(scrape(0.35), 900), SEG['n09'] - 0.2, db(-26), pan=0.3)
x = tt(EV['leash'][1] - EV['leash'][0]); f = 300 + 500 * (x / x[-1]) ** 1.7
hit.place(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / x[-1] * 0.5) ** 2, EV['leash'][0], db(-28))
hit.place(lp(thud(50, 0.8, 0.5), 300), EV['assois'] + 0.12, db(-14), pan=0.3)
hit.place(lp(thud(46, 0.9, 0.5), 300), EV['cours'] + 0.12, db(-13), pan=-0.3)
hit.place(lp(boom(1.4), 300), EV['cta'], db(-13))
hit.place(lp(thud(52, 0.7, 0.5), 300), EV['vote'] + 0.14, db(-16))
hit.place(lp(boom(1.6), 260), EV['next'], db(-10)); hit.place(ting(1760), EV['next'] + 0.05, db(-24), pan=0.2)
# cœur qui s'emballe pendant l'attente puis la révélation
k = SEG['n06']
while k < SEG['n09'] + 1.4:
    r = (k - SEG['n06']) / (SEG['n09'] + 1.4 - SEG['n06']); per = 60 / (92 + 40 * r)
    for off, g in ((0, 1.0), (0.16, 0.7)):
        x = tt(0.22); s = np.sin(2 * np.pi * 52 * x) * np.exp(-x * 22) + 0.4 * np.sin(2 * np.pi * 78 * x) * np.exp(-x * 30)
        mus.place(lp(s, 160) * g, k + off, db(-15) * (0.6 + 0.4 * r))
    k += per

hit.L *= 1 - (1 - db(-4)) * env; hit.R *= 1 - (1 - db(-4)) * env
meter = pyln.Meter(SR)
stems = {'voix': voice.st(), 'musique': mus.st(), 'impacts': hit.st()}
for k in stems: stems[k] = np.stack([hp(stems[k][:, 0], 25), hp(stems[k][:, 1], 25)], 1); sf.write(f'{OUT}/{k}.wav', stems[k].astype(np.float32), SR, subtype='FLOAT')
tg = {'voix': -15.0, 'musique': -23.5, 'impacts': -20.0}
mix = sum(pyln.normalize.loudness(stems[k], meter.integrated_loudness(stems[k]), tg[k]) for k in stems)
mix = pyln.normalize.loudness(mix, meter.integrated_loudness(mix), -13.6)
print('loudness', round(meter.integrated_loudness(mix), 2), 'peak', round(float(np.abs(mix).max()), 3))
sf.write(f'{OUT}/mix_pre.wav', mix.astype(np.float32), SR, subtype='FLOAT')
