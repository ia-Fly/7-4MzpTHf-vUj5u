"""Reconnaissance vocale anglaise (Whisper base.en, sherpa-onnx). usage: asr_en.py fichier.wav [...]  ou import asr(x, sr)"""
import sys, numpy as np, soundfile as sf, sherpa_onnx
from scipy.signal import resample_poly
S = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + '/'
md = S + 'asr_dl/sherpa-onnx-whisper-base.en/'
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=md + 'base.en-encoder.int8.onnx', decoder=md + 'base.en-decoder.int8.onnx',
                                                 tokens=md + 'base.en-tokens.txt', language='en', task='transcribe', num_threads=2)
def asr(x, sr):
    if x.ndim > 1: x = x.mean(1)
    if sr != 16000: x = resample_poly(x, 160, sr // 100)
    x = (x / np.abs(x).max() * 0.8).astype(np.float32)
    st = rec.create_stream(); st.accept_waveform(16000, np.concatenate([np.zeros(8000, np.float32), x, np.zeros(8000, np.float32)]))
    rec.decode_stream(st); return st.result.text.strip()
if __name__ == '__main__':
    for f in sys.argv[1:]:
        x, sr = sf.read(f); print(f.split('/')[-1], '|', asr(x, sr))
