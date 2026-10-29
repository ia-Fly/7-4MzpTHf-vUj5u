"""Timeline épisode 1 en anglais (v5 en anglais, 20 s rythmés) -> planches/timeline_ep1en.json"""
import json, sys
S = __import__('os').environ.get('OMERTA_WORK', '/home/claude/omerta-work').rstrip('/') + '/'
sys.path.insert(0, S + 'scripts')
from tl_common import assemble
V = S + 'ep1en/voix/'
D = json.load(open(V + 'raw/durations.json')); D.update(json.load(open(V + 'rawb/durations.json')))
WAV = {k: (V + f'proc/{k}.wav' if k.startswith('n') else V + f'procb/{k}.wav') for k in D}
# espeak soude certains petits mots : on les soude aussi à l'écrit pour l'alignement
for k, a, b in [('n08', 'of the', 'of‿the')]:
    if k in D and a in D[k]['text']: D[k]['text'] = D[k]['text'].replace(a, b)
ORDER = ['n01', 'n02', 'n03', 'n04', 'n05', 'n06', 'n07', 'n08', 'b14', 'n09', 'n10']
GAP = {'n01': 0.08, 'n02': 0.06, 'n03': 0.06, 'n04': 0.06, 'n05': 0.06, 'n06': 0.05, 'n07': 0.05, 'n08': 0.32, 'b14': 0.16, 'n09': 0.34, 'n10': 0.0}
CAPS = {
 'n01': [(0, "YOUR FATHER"), (2, "IS *DEAD.*")],
 'n02': [(0, "HE LEFT YOU"), (3, "A *DEBT…*"), (5, "TO THE *MAFIA.*")],
 'n03': [(0, "TO PAY IT OFF,"), (4, "YOU *BURN*"), (6, "THE BAKERY"), (8, "*ACROSS THE STREET.*")],
 'n04': [(0, "THE NEXT DAY,"), (3, "YOU *LEAVE.*")],
 'n05': [(0, "BUT YOU"), (2, "*NEVER*"), (3, "LEAVE THE"), (5, "*FAMILY.*")],
 'n06': [(0, "FOUR DAYS LATER,"), (3, "YOUR KITCHEN"), (5, "LIGHT *TURNS ON.*")],
 'n07': [(0, "THE *GODFATHER*"), (2, "IS SITTING"), (4, "AT YOUR TABLE.")],
 'n08': [(0, "HE PLACES"), (2, "A *PHOTO:*"), (4, "*YOU,*"), (5, "IN FRONT OF"), (7, "THE *FIRE.*")],
 'b14': [(0, "« *SIT DOWN.* »")],
 'n09': [(0, "YOU SIT…"), (2, "OR YOU *RUN?*")],
 'n10': [(0, "THE MOST *VOTED*"), (3, "CHOICE DECIDES"), (5, "*EPISODE 2.*")],
}
BOSS = {'b14': 'boss'}
seg, words, caps, END = assemble(D, WAV, ORDER, GAP, CAPS, BOSS, start=0.12, tail=1.45)
def W(k, i): return words[k][i][1]
def We(k, i): return words[k][i][2]
def L0(k): return seg[k]
shots = [
 [0.0,          382, 818, 2.9,  382, 812, 3.15],     # the father's photo
 [L0('n02'),    476, 1010, 1.55, 478, 1000, 1.68],   # him + the debt card
 [W('n02', 5),  640, 905, 1.04, 650, 895, 1.12],     # the string runs into the dark: the mafia
 [L0('n03'),    540, 1100, 3.1, 540, 1096, 3.4],     # the hand, the lighter
 [W('n03', 7),  630, 846, 2.6, 630, 842, 2.85],      # the bakery across the street
 [L0('n04'),    560, 965, 1.45, 556, 968, 1.55],     # the next day: him + the burnt shop
 [L0('n05'),    540, 975, 1.3, 540, 975, 1.38],      # rule #1
 [L0('n06'),    630, 846, 2.4, 630, 846, 2.55],      # four days: window, day/night
 [W('n06', 4),  520, 1000, 1.3, 532, 996, 1.38],     # night, kitchen light turns on
 [L0('n07'),    915, 992, 1.85, 925, 986, 2.02],     # the godfather
 [L0('n08'),    790, 1112, 2.8, 790, 1112, 3.0],     # the photo on the table
 [L0('b14'),    722, 1012, 1.26, 736, 1006, 1.34],   # "sit down"
 [L0('n09'),    556, 1090, 1.12, 556, 1088, 1.17],   # the chair or the door
 [L0('n10'),    560, 1040, 0.98, 560, 1036, 1.03],   # wide shot: the vote decides
]
ev = dict(
 END=END,
 mourn=W('n01', 3), debt=W('n02', 4), mafia=W('n02', 7), string_draw=[W('n02', 5) - 0.05, W('n02', 7) + 0.25],
 lighter=L0('n03'), flame=W('n03', 5), fire=W('n03', 7), snap=W('n04', 4),
 rule=[L0('n05'), L0('n06')], jamais=W('n05', 2),
 days=[W('n06', 0), W('n06', 4)], lamp_on=W('n06', 6),
 parrain=W('n07', 1), photo_slide=[W('n08', 1), W('n08', 3) + 0.2], inset=[W('n08', 4), L0('b14') - 0.02], feu=W('n08', 8),
 bubble=[L0('b14'), L0('n09') + 0.25], chair=W('b14', 1), leash=[L0('b14') + 0.1, We('b14', 1)],
 assois=W('n09', 1), cours=W('n09', 4), cta=We('n09', 4) - 0.1,
 vote=W('n10', 2), suite=W('n10', 5), next=We('n10', 6) + 0.12,
)
json.dump(dict(seg=seg, words=words, caps=caps, shots=shots, ev=ev, voice={k: WAV[k] for k in ORDER}),
          open(S + 'planches/timeline_ep1en.json', 'w'), ensure_ascii=False, indent=1)
print('END', END)
for k in ORDER: print(k, seg[k], [(w, a) for w, a, _ in words[k]])
