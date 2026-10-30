"""Bande son de l'épisode 3 en anglais : voix + pulsation + un bruitage par événement.
usage: reel_audio_ep3en.py out_dir"""
import json, sys, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve

S = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + '/'
OUT = sys.argv[1]
TL = json.load(open(S + 'planches/tl_ep3en.json')); EV, SEG, SHOTS, WORDS = TL['ev'], TL['seg'], TL['shots'], TL['words']
SR = 48000; DUR = EV['END']; N = int(SR * DUR)
rng = np.random.default_rng(52)
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

# ---------------- SONS DE BASE ----------------
def click(d=0.012, f=3200):
    x = tt(d); return bp(rng.normal(0, 1, len(x)), f * 0.6, f * 1.6) * np.exp(-x * 420)
def thud(f0=58, d=0.9, drop=0.5, nz=0.3):
    x = tt(d); f = f0 * (1 + drop * np.exp(-x * 18))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 4.2) + lp(rng.normal(0, 1, len(x)), 900) * np.exp(-x * 30) * nz
def boom(d=2.0):
    x = tt(d); f = 70 * np.exp(-x * 2.2) + 30
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.0) + lp(rng.normal(0, 1, len(x)), 500) * np.exp(-x * 6) * 0.5
def whoosh(bus, d, f0, f1, gain, t0, pan=0.0):
    x = tt(d); n = rng.normal(0, 1, len(x)); lo, hi = min(f0, f1), max(f0, f1)
    a = bp(n, lo * 0.7, lo * 1.6); b = bp(n, hi * 0.6, hi * 1.5); k = x / d if f1 > f0 else 1 - x / d
    bus.place((a * (1 - k) + b * k) * np.sin(np.pi * np.clip(x / d, 0, 1)) ** 2, t0, gain, pan)
def ting(f=2210, d=1.2):
    x = tt(d)
    return sum(a * np.sin(2 * np.pi * f * m * x + p) * np.exp(-x * dcy) for m, a, p, dcy in ((1, 0.6, 0, 3.2), (1.534, 0.45, 1, 4.5), (2.317, 0.3, 2, 6.0), (0.661, 0.35, 0.5, 2.6))) + hp(rng.normal(0, 1, len(x)), 3000) * np.exp(-x * 160) * 0.6
def clink(): return ting(3100, 0.5) * np.exp(-tt(0.5) * 6)
def tick():
    x = tt(0.05); return bp(rng.normal(0, 1, len(x)), 2000, 6000) * np.exp(-x * 300) + np.sin(2 * np.pi * 1400 * x) * np.exp(-x * 200) * 0.4
def creak(d=0.45, f0=380):
    x = tt(d); f = f0 * (1 + 0.25 * np.sin(2 * np.pi * 3 * x)) * (1 + 0.3 * x / d)
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1; am = (1 + 0.8 * np.sign(np.sin(2 * np.pi * 26 * x))) * np.sin(np.pi * x / d)
    return bp(saw * am, 300, 2200) * 0.5
def scrape(d=0.45):
    x = tt(d); am = (1 + np.sign(np.sin(2 * np.pi * 38 * x)) * 0.5) * np.sin(np.pi * x / d)
    return lp(bp(rng.normal(0, 1, len(x)), 500, 1800) * am, 1200)
def sting(f=740):
    x = tt(1.6); s = (np.sin(2 * np.pi * f * x) + np.sin(2 * np.pi * f * 1.06 * x) + 0.5 * np.sin(2 * np.pi * f * 0.5 * x)) * np.exp(-x * 2.2) * np.clip(x / 0.03, 0, 1)
    return s * 0.4
def paper(d=0.6):
    x = tt(d); n = rng.normal(0, 1, len(x)); env = np.sin(np.pi * x / d) ** 1.5 * (1 + 0.4 * np.sin(2 * np.pi * 23 * x))
    return (bp(n, 2500, 9000) * 0.6 + bp(n, 600, 1500) * 0.4) * env
def shutter():
    a = click(0.012, 3800) * 1.4; b = click(0.02, 1800); out = np.zeros(int(0.12 * SR)); out[:len(a)] += a; j = int(0.055 * SR); out[j:j + len(b)] += b; return out
def buzz(d=0.32, f=150):
    x = tt(d); sq = np.sign(np.sin(2 * np.pi * f * x)) * 0.5 + np.sin(2 * np.pi * f * 2 * x) * 0.3
    return bp(sq, 120, 2400) * np.clip(x / 0.01, 0, 1) * np.clip((d - x) / 0.04, 0, 1)
def riser(d, f0=180, f1=900):
    x = tt(d); f = f0 * (f1 / f0) ** (x / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + bp(rng.normal(0, 1, len(x)), 800, 5000) * 0.4 * (x / d)
    return s * (x / d) ** 2
def heart(t0, t1, bpm0, bpm1, g0, g1):
    k = t0
    while k < t1:
        r = (k - t0) / max(1e-3, t1 - t0); per = 60 / (bpm0 + (bpm1 - bpm0) * r)
        for off, g in ((0, 1.0), (0.16, 0.7)):
            x = tt(0.22); s = np.sin(2 * np.pi * 52 * x) * np.exp(-x * 22) + 0.4 * np.sin(2 * np.pi * 78 * x) * np.exp(-x * 30)
            mus.place(lp(s, 160) * g, k + off, db(-15) * (g0 + (g1 - g0) * r))
        k += per

t = np.arange(N) / SR
W = lambda k, i: WORDS[k][i][1]
# ---------------- PULSATION ----------------
BPM = 128; beat = 60 / BPM
pulse_env = np.zeros(N); k = 0.0
while k < DUR:
    i = int(k * SR); x = tt(0.4); pulse_env[i:i + len(x)] = np.maximum(pulse_env[i:i + len(x)], np.exp(-x * 9)[: N - i]); k += beat
drone = np.sin(2 * np.pi * 41.2 * t) * 0.9 + np.sin(2 * np.pi * 55.0 * t + 0.7) * 0.5 + np.sin(2 * np.pi * 82.4 * t + 1.3) * 0.2
C0, C1 = EV['count']; NO = EV['nothing']
pts = [(0, 0.95), (C0, 0.9), (NO - 0.05, 1.0), (NO, 0.25), (SEG['b01'], 0.45), (EV['sugar'], 0.8), (SEG['c05'], 0.75),
       (SEG['b03'], 0.85), (EV['sealed'], 0.95), (SEG['c07'], 1.0), (DUR - 0.8, 1.0), (DUR, 0.95)]
kick_on = [(0, 1), (C0 - 0.05, 1), (C0, 0), (EV['sugar'] - 0.05, 0), (EV['sugar'], 1), (DUR, 1)]
inten = np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
mus.place(drone * (0.35 + 0.65 * pulse_env) * inten * db(-20), 0)
kick = np.zeros(N); k = 0.0
while k < DUR:
    x = tt(0.35); f = 55 * (1 + 1.2 * np.exp(-x * 30)); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 7)
    i = int(k * SR); kick[i:i + len(s)] += s[: N - i]; k += beat
kgate = np.interp(t, [p[0] for p in kick_on], [p[1] for p in kick_on])
mus.place(lp(kick, 200) * kgate * inten * db(-17), 0)
k = 0.0
while k < DUR - 0.2:
    if not (C0 - 0.05 < k < EV['sugar']): mus.place(tick(), k, db(-31) * (1.0 if int(k / (beat / 2)) % 2 == 0 else 0.6), pan=0.25)
    k += beat / 2
heart(0.2, C0, 118, 128, 0.9, 1.0)
heart(C0, NO - 0.1, 128, 168, 1.0, 1.25)          # le compte à rebours : le cœur s'emballe…
heart(NO + 0.5, SEG['b01'] + 0.6, 70, 64, 0.5, 0.3) # …puis retombe
heart(SEG['c07'], DUR - 0.2, 120, 134, 0.8, 1.0)
for sh in SHOTS[1:]: whoosh(hit, 0.2, 2500, 500, db(-31), sh[0] - 0.2, pan=rng.uniform(-0.4, 0.4))

# ---------------- BRUITAGES ----------------
d0, d1, d2 = EV['drink']
x = tt(d1 - d0); gulp = np.zeros(len(x))
for g in np.arange(0.15, d1 - d0 - 0.1, 0.42):   # gorgées
    y = tt(0.16); s = lp(rng.normal(0, 1, len(y)), 700) * np.exp(-y * 25) + np.sin(2 * np.pi * 180 * y) * np.exp(-y * 30) * 0.5
    j = int(g * SR); gulp[j:j + len(s)] += s[: len(gulp) - j]
hit.place(gulp, d0, db(-22))
hit.place(lp(thud(44, 1.2, 0.5, 0.3), 300), 0.0, db(-15)); hit.place(sting(523), W('c01', 3) + 0.05, db(-28))
hit.place(lp(thud(60, 0.4, 0.5, 0.3), 400), d2 - 0.08, db(-18)); hit.place(clink(), d2 - 0.06, db(-19), pan=0.1)
k = C0
while k < NO - 0.1: hit.place(tick(), k, db(-22), pan=0.3); k += (C1 - C0) / 10
hit.place(riser(NO - C0), C0, db(-25))
hit.place(ting(1320), NO + 0.25, db(-28), pan=0.15)
hit.place(lp(boom(1.4), 300), EV['sugar'] - 0.05, db(-13)); hit.place(ting(1760), EV['sugar'] + 0.05, db(-25), pan=-0.2)
hit.place(ting(1320), EV['cta'][0] + 0.05, db(-26), pan=0.15); whoosh(hit, 0.35, 400, 2200, db(-27), EV['cta'][0] - 0.25)
hit.place(lp(thud(46, 1.0, 0.6), 400), EV['rule'][0] + 0.05, db(-13))
hit.place(lp(thud(50, 0.6, 0.5), 300), EV['nod'] + 0.1, db(-17))
hit.place(lp(thud(46, 1.0, 0.6), 400), EV['gone'], db(-12)); hit.place(ting(2210), EV['gone'] + 0.03, db(-24), pan=0.2)
e0, e1 = EV['env']; hit.place(paper(e1 - e0), e0, db(-20), pan=0.2); hit.place(lp(scrape(e1 - e0), 1200), e0, db(-27), pan=0.2)
hit.place(lp(thud(42, 1.0, 0.5, 0.3), 300), EV['sealed'], db(-12)); hit.place(sting(466), EV['sealed'] + 0.05, db(-27))
hit.place(lp(thud(50, 0.8, 0.5), 300), EV['open'] + 0.12, db(-14), pan=-0.2)
hit.place(lp(thud(46, 0.9, 0.5), 300), EV['deliver'] + 0.12, db(-13), pan=0.2)
hit.place(lp(boom(1.4), 300), EV['comment'], db(-13))
hit.place(lp(boom(1.6), 260), EV['next'], db(-10)); hit.place(ting(1760), EV['next'] + 0.05, db(-24), pan=0.2)
whoosh(hit, EV['loop'][1] - EV['loop'][0], 300, 2600, db(-24), EV['loop'][0])

mus.L *= DUCK; mus.R *= DUCK
HD = np.clip(1 - (1 - db(-4)) * env, db(-7), 1); hit.L *= HD; hit.R *= HD
meter = pyln.Meter(SR)
stems = {'voix': voice.st(), 'musique': mus.st(), 'impacts': hit.st()}
for k in stems: stems[k] = np.stack([hp(stems[k][:, 0], 25), hp(stems[k][:, 1], 25)], 1)
tg = {'voix': -15.0, 'musique': -23.5, 'impacts': -20.0}
mix = sum(pyln.normalize.loudness(stems[k], meter.integrated_loudness(stems[k]), tg[k]) for k in stems)
mix = pyln.normalize.loudness(mix, meter.integrated_loudness(mix), -13.6)
print('loudness', round(meter.integrated_loudness(mix), 2), 'peak', round(float(np.abs(mix).max()), 3))
sf.write(f'{OUT}/mix_pre.wav', mix.astype(np.float32), SR, subtype='FLOAT')
