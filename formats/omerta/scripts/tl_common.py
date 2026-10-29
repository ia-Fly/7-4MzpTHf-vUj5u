"""Outils communs aux timelines des épisodes : mots horodatés (durées des phonèmes), assemblage des répliques."""
import json, soundfile as sf
NOT_LETTER = set(' .,:;?!-…ˈˌ')
def toks(D, k):
    """[(mot écrit, début, fin)] : le n-ième mot écrit = le n-ième mot phonétique"""
    words = D[k]['text'].split(); res, cur, anyc = [], None, None
    def close():
        if cur: res.append(cur)
        elif anyc: res.append(anyc)
    for ch, a, b in D[k]['chars']:
        if ch == ' ': close(); cur = None; anyc = None; continue
        anyc = [a, b] if anyc is None else [anyc[0], b]
        if ch in NOT_LETTER: continue
        cur = [a, b] if cur is None else [cur[0], b]
    close(); assert len(res) == len(words), (k, len(res), len(words))
    return [(w, a, b) for w, (a, b) in zip(words, res)]
def assemble(D, WAV, ORDER, GAP, CAPS, BOSS, start=0.12, tail=0.85):
    t = start; seg, words, caps = {}, {}, []
    for k in ORDER:
        seg[k] = round(t, 3); words[k] = [(w, round(t + a, 3), round(t + b, 3)) for w, a, b in toks(D, k)]
        for i, txt in CAPS[k]: caps.append(dict(t=words[k][i][1], txt=txt, boss=(k in BOSS), who=BOSS.get(k, '')))
        t += sf.info(WAV[k]).duration + GAP.get(k, 0.06)
    END = round(t + tail, 2)
    for i in range(len(caps) - 1): caps[i]['t1'] = caps[i + 1]['t']
    caps[-1]['t1'] = END + 1
    return seg, words, caps, END
