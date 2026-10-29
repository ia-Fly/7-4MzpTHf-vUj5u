import sys, glob, os, numpy as np, soundfile as sf, pyworld as pw
# usage: voice_shift.py in_dir out_dir f0_factor formant_alpha [pattern]
src, dst, k, alpha = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
pat = sys.argv[5] if len(sys.argv) > 5 else '*.wav'
allf0 = []
for f in sorted(glob.glob(os.path.join(src, pat))):
    x, sr = sf.read(f); x = x.astype(np.float64)
    f0, t = pw.harvest(x, sr, f0_floor=60, f0_ceil=400, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, sr); ap = pw.d4c(x, f0, t, sr)
    nb = sp.shape[1]; fr = np.arange(nb); srcidx = np.clip(fr / alpha, 0, nb - 1)
    if alpha != 1.0:
        sp = np.array([np.interp(srcidx, fr, r) for r in sp]); ap = np.array([np.interp(srcidx, fr, r) for r in ap])
    y = pw.synthesize(f0 * k, sp, ap, sr, 5.0)
    y = y / np.max(np.abs(y)) * 0.9
    sf.write(os.path.join(dst, os.path.basename(f)), y.astype(np.float32), sr)
    allf0.append(f0[f0 > 0] * k)
v = np.concatenate(allf0)
print('F0 après : médiane %.0f Hz, p10 %.0f, p90 %.0f' % (np.median(v), np.percentile(v, 10), np.percentile(v, 90)))
