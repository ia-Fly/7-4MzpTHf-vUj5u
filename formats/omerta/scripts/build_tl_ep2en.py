"""Timeline épisode 2 en anglais (« You sit down ») -> planches/tl_ep2en.json"""
import json, sys
S = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + '/'
sys.path.insert(0, S + 'scripts')
from tl_common import assemble
V = S + 'ep2en/voix/'
D = json.load(open(V + 'raw/durations.json')); D.update(json.load(open(V + 'rawb/durations.json')))
WAV = {k: (V + f'proc/{k}.wav' if k.startswith('c') else V + f'procb/{k}.wav') for k in D}
# espeak soude certains petits mots (« in the », « on the », « for a ») : on les soude aussi à l'écrit pour l'alignement
for k, a, b in [('c10', 'In the', 'In‿the'), ('c13', 'on the', 'on‿the'), ('c14', 'for a', 'for‿a')]:
    assert a in D[k]['text']; D[k]['text'] = D[k]['text'].replace(a, b)
ORDER = ['c01', 'c02', 'c03', 'c04', 'c05', 'c06', 'b01', 'c07', 'c08', 'c09', 'c10', 'c11', 'c12',
         'c13', 'c14', 'c15', 'b02', 'c16', 'c17', 'c18']
GAP = {'c01': 0.06, 'c02': 0.3, 'c03': 0.1, 'c04': 0.08, 'c05': 0.08, 'c06': 0.16, 'b01': 0.18, 'c07': 0.12, 'c08': 0.08,
       'c09': 0.08, 'c10': 0.1, 'c11': 0.2, 'c12': 0.24, 'c13': 0.08, 'c14': 0.14, 'c15': 0.28, 'b02': 0.28,
       'c16': 0.14, 'c17': 0.3}
CAPS = {
 'c01': [(0, "THIS COFFEE"), (2, "IS *POISONED.*")],
 'c02': [(0, "AND *YOU'RE*"), (2, "THE ONE"), (4, "WHO MADE IT.")],
 'c03': [(0, "YOU *VOTED:*"), (2, "YOU *SIT DOWN.*")],
 'c04': [(0, "ACROSS FROM YOU:"), (3, "THE *GODFATHER.*")],
 'c05': [(0, "YOUR FATHER"), (2, "OWED HIM"), (4, "*€40,000.*")],
 'c06': [(0, "AND HE HAS"), (3, "A *PHOTO*"), (5, "OF YOU"), (7, "STARTING THE *FIRE.*")],
 'b01': [(0, "“*40,000.*”"), (2, "“BY *TOMORROW.*”")],
 'c07': [(0, "YOU DON'T HAVE"), (3, "*A CENT.*")],
 'c08': [(0, "SO YOU BUY"), (3, "*TIME:*"), (4, "YOU OFFER HIM"), (7, "A *COFFEE.*")],
 'c09': [(0, "HE *ACCEPTS.*")],
 'c10': [(0, "IN THE CUPBOARD,"), (2, "THERE'S STILL"), (4, "YOUR FATHER'S"), (6, "RAT *POISON.*")],
 'c11': [(0, "YOU *POUR*"), (2, "A SPOONFUL"), (4, "INTO HIS CUP…"), (7, "THEN *TWO.*")],
 'c12': [(0, "_FOLLOW:_"), (1, "THE NEXT CHOICE"), (4, "IS _YOURS._")],
 'c13': [(0, "YOU SET"), (2, "BOTH *CUPS*"), (4, "ON THE TABLE.")],
 'c14': [(0, "HE STARES"), (2, "AT HIS…"), (4, "FOR A *LONG TIME.*")],
 'c15': [(0, "THEN HE *SMILES…*"), (3, "AND *SWAPS*"), (5, "THE CUPS.")],
 'b02': [(0, "“*RULE NUMBER TWO:*”"), (3, "“WHOEVER SERVES…”"), (5, "“DRINKS *FIRST.*”")],
 'c16': [(0, "THE *POISON*"), (2, "IS RIGHT"), (4, "IN FRONT OF *YOU.*")],
 'c17': [(0, "DO YOU *DRINK IT…*"), (4, "OR *CONFESS*"), (6, "EVERYTHING?")],
 'c18': [(0, "THE MOST *VOTED*"), (3, "CHOICE BECOMES"), (5, "*EPISODE 3.*")],
}
seg, words, caps, END = assemble(D, WAV, ORDER, GAP, CAPS, {'b01': 'boss', 'b02': 'boss'}, start=0.12, tail=1.55)
def W(k, i): return words[k][i][1]
def We(k, i): return words[k][i][2]
def L0(k): return seg[k]
REW = L0('c03') - 0.1
shots = [
 [0.0,          778, 1098, 3.3, 778, 1100, 3.55],    # flash-forward : la tasse empoisonnée devant toi
 [L0('c02'),    742, 1040, 2.0, 746, 1036, 2.16],    # toi, assis, devant la tasse
 [REW,          520, 1040, 0.95, 528, 1036, 1.0],    # retour 5 min avant : tu t'assois
 [L0('c04'),    930, 1000, 1.9, 934, 994, 2.06],     # le parrain
 [L0('c05'),    382, 816, 2.9, 382, 812, 3.12],      # la photo de ton père : la dette
 [L0('c06'),    880, 1060, 1.55, 884, 1056, 1.62],   # la photo de l'incendie
 [L0('b01'),    930, 920, 1.95, 934, 916, 2.1],      # « 40,000. By tomorrow. »
 [L0('c07'),    712, 966, 2.4, 712, 962, 2.62],      # toi : 0 €
 [L0('c08'),    186, 806, 3.1, 186, 806, 3.35],      # l'horloge : gagner du temps
 [W('c08', 4), -150, 1010, 1.55, -140, 1006, 1.66],  # au comptoir, la cafetière
 [L0('c09'),    938, 958, 2.25, 940, 952, 2.45],     # il accepte
 [L0('c10'),   -148, 842, 2.5, -148, 838, 2.75],     # le placard : le poison
 [L0('c11'),   -112, 1098, 3.3, -112, 1096, 3.6],    # une cuillère… puis deux
 [L0('c12'),    384, 1012, 0.88, 392, 1010, 0.94],   # plan large : follow
 [L0('c13'),    830, 1102, 2.6, 830, 1100, 2.8],     # tu poses les tasses
 [L0('c14'),    930, 992, 2.9, 936, 984, 3.45],      # il regarde la sienne
 [L0('c15'),    940, 948, 3.6, 942, 946, 3.85],      # il sourit
 [W('c15', 3),  830, 1102, 2.6, 830, 1100, 2.76],    # il échange les tasses
 [L0('b02'),    800, 1030, 1.4, 806, 1026, 1.5],     # règle n°2
 [L0('c16'),    778, 1098, 3.3, 778, 1100, 3.5],     # le poison devant toi
 [L0('c17'),    748, 1030, 1.42, 752, 1028, 1.5],    # drink or confess
 [L0('c18'),    760, 1040, 1.5, 770, 1060, 1.9],     # most voted… puis retour dans la tasse (boucle)
]
ev = dict(
 END=END, rew=[REW, REW + 0.55], sit=W('c03', 3) - 0.08, vote=[L0('c03') + 0.2, L0('c04') - 0.05],
 debt=W('c05', 4), photo=[W('c06', 4) - 0.05, L0('b01') - 0.04], bubble1=[L0('b01'), L0('c07') + 0.05],
 zero=[W('c07', 3), L0('c08') - 0.04], clock=[L0('c08'), W('c08', 4)], moka=W('c08', 8), nod=W('c09', 1),
 cupboard=W('c10', 1), poison=W('c10', 7), pour1=[W('c11', 2), W('c11', 5) + 0.1], pour2=[W('c11', 8) - 0.1, We('c11', 8) + 0.35],
 cta=[L0('c12'), L0('c13') - 0.05], serve=[W('c13', 1), W('c13', 5) + 0.15], look=[L0('c14'), L0('c15')],
 smile=W('c15', 2), swap=[W('c15', 4), We('c15', 6) + 0.2], rule=[L0('b02') - 0.05, L0('c16') - 0.05],
 premier=W('b02', 6), devant=W('c16', 5), drink=W('c17', 2), avoue=W('c17', 5), comment=We('c17', 6) + 0.05,
 next=W('c18', 5), loop=[END - 0.75, END],
 clk=[[0.0, 52], [REW + 0.5, 47], [W('c08', 3), 48], [L0('c09'), 49], [W('c11', 2), 50], [L0('c13'), 51], [W('c15', 4), 52]],
 gauge=[[0.0, 5], [REW + 0.45, 2], [W('c09', 1), 1], [W('c14', 1), 2], [W('c14', 3), 3], [W('c14', 5), 4], [W('c15', 2), 5]],
)
json.dump(dict(seg=seg, words=words, caps=caps, shots=shots, ev=ev, voice={k: WAV[k] for k in ORDER}),
          open(S + 'planches/tl_ep2en.json', 'w'), ensure_ascii=False, indent=1)
print('END', END)
for k in ORDER: print(k, seg[k], [(w, a) for w, a, _ in words[k]])
