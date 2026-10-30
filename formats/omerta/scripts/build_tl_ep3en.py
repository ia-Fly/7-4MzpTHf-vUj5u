"""Timeline épisode 3 en anglais (« You drink ») -> planches/tl_ep3en.json
Cible : 25–30 s, choix posé vers 18–20 s (l'ép. 2, 44 s, perdait la moitié des gens vers 20 s)."""
import json, sys
S = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + '/'
sys.path.insert(0, S + 'scripts')
from tl_common import assemble
V = S + 'ep3en/voix/'
D = json.load(open(V + 'raw/durations.json')); D.update(json.load(open(V + 'rawb/durations.json')))
WAV = {k: (V + f'proc/{k}.wav' if k.startswith('c') else V + f'procb/{k}.wav') for k in D}
WELD = [x.split('|') for x in sys.argv[1:]] or [['c05', 'From the', 'From‿the']]   # soudures espeak : clé|texte|texte‿soudé
for k, a, b in WELD:
    assert a in D[k]['text']; D[k]['text'] = D[k]['text'].replace(a, b)
ORDER = ['c01', 'c02', 'c03', 'c04', 'b01', 'c05', 'b02', 'b03', 'c06', 'c07', 'c08']
GAP = {'c01': 0.12, 'c02': 0.08, 'c03': 0.08, 'c04': 0.55, 'b01': 0.12, 'c05': 0.12, 'b02': 0.16, 'b03': 0.12,
       'c06': 0.1, 'c07': 0.3}
CAPS = {
 'c01': [(0, "YOU *DRANK IT.*"), (3, "EVERY *DROP.*")],
 'c02': [(0, "YOU *VOTED:*"), (2, "*DRINK.*")],
 'c03': [(0, "*TEN* SECONDS."), (2, "YOUR HEART"), (4, "IS *POUNDING.*")],
 'c04': [(0, "_NOTHING_"), (1, "_HAPPENS._")],
 'b01': [(0, "“_RELAX._”"), (1, "“I *SWAPPED*”"), (3, "“THE *POISON*”"), (5, "“THIS MORNING.”")],
 'c05': [(0, "HE *KNEW.*"), (2, "FROM THE"), (3, "VERY *START.*")],
 'b02': [(0, "“YOU'D RATHER”"), (2, "“DRINK THAN *TALK.*”"), (5, "“I *LIKE* THAT.”")],
 'b03': [(0, "“YOUR *DEBT*”"), (2, "“IS _GONE._”"), (4, "“DELIVER THIS”"), (6, "“*TONIGHT.*”")],
 'c06': [(0, "AN *ENVELOPE.*"), (2, "*SEALED SHUT.*"), (4, "NO NAME.")],
 'c07': [(0, "DO YOU"), (2, "_OPEN IT…_"), (4, "OR *DELIVER IT?*")],
 'c08': [(0, "THE MOST *VOTED*"), (3, "CHOICE BECOMES"), (5, "*EPISODE 4.*")],
}
# les indices de CAPS suivent les mots écrits ; on les décale si une soudure a fusionné deux mots
seg, words, caps, END = assemble(D, WAV, ORDER, GAP, CAPS, {'b01': 'boss', 'b02': 'boss', 'b03': 'boss'}, start=0.1, tail=2.3)
def W(k, i): return words[k][i][1]
def We(k, i): return words[k][i][2]
def L0(k): return seg[k]
shots = [
 [0.0,          738, 1000, 2.7, 742, 1004, 2.95],   # tu bois : la tasse à la bouche
 [L0('c02'),    800, 1050, 1.6, 806, 1046, 1.72],   # plan moyen : toi et le parrain
 [L0('c03'),    716, 990, 2.5, 716, 980, 3.0],      # ton visage, le cœur qui bat
 [L0('c04'),    830, 1060, 1.3, 830, 1058, 1.38],   # plan large : rien ne se passe
 [L0('b01'),    940, 966, 2.2, 942, 956, 2.4],      # le parrain : « Sugar. »
 [W('b01', 3),  786, 1100, 3.0, 786, 1098, 3.25],   # la tasse : SUGAR
 [L0('c05'),    900, 990, 1.9, 904, 984, 2.05],     # il savait
 [L0('b02'),    930, 980, 2.0, 934, 972, 2.2],      # « I like that. »
 [L0('b03'),    840, 1100, 1.8, 830, 1108, 2.0],    # la dette effacée, l'enveloppe glisse
 [L0('c06'),    812, 1112, 3.4, 812, 1112, 3.8],    # l'enveloppe scellée
 [L0('c07'),    780, 1066, 1.5, 784, 1062, 1.6],    # OPEN ou DELIVER
 [L0('c08'),    780, 1060, 1.5, 790, 1070, 1.85],   # most voted… puis retour (boucle)
]
ev = dict(
 END=END, drink=[0.0, We('c01', 4) - 0.15, L0('c02') + 0.45], vote=[L0('c02') + 0.1, L0('c03') - 0.05],
 count=[L0('c03'), W('c04', 1) + 0.1], nothing=W('c04', 1), sugar=W('b01', 2), smile=W('b01', 0),
 knew=W('c05', 1), cta=[L0('c05'), L0('b02') - 0.05], rule=[L0('b02'), L0('b03') - 0.05], like=W('b02', 6),
 nod=W('b02', 6), gone=W('b03', 3), env=[W('b03', 4), We('b03', 6) + 0.3], sealed=W('c06', 2), noname=W('c06', 4),
 open=W('c07', 2), deliver=W('c07', 5), comment=We('c07', 6) + 0.05, next=W('c08', 5), loop=[END - 0.75, END],
 clk=[[0.0, 53], [L0('c05'), 54]],
 gauge=[[0.0, 4], [W('c03', 0), 4], [W('c03', 2), 5], [W('c04', 1), 1], [L0('b02'), 2]],
)
json.dump(dict(seg=seg, words=words, caps=caps, shots=shots, ev=ev, voice={k: WAV[k] for k in ORDER}),
          open(S + 'planches/tl_ep3en.json', 'w'), ensure_ascii=False, indent=1)
print('END', END, 'choix (c07)', round(L0('c07'), 2))
for k in ORDER: print(k, seg[k], [(w, a) for w, a, _ in words[k]])
