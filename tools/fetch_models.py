"""Prépare le dossier de travail des épisodes à voix (Omertà) : voix piper + reconnaissance Whisper, depuis les
« releases » GitHub de sherpa-onnx (domaine autorisé), et ajoute la sortie de durée des phonèmes (*.dur.onnx).
usage: python3 tools/fetch_models.py [OMERTA_WORK]   (défaut : $OMERTA_WORK ou /home/claude/omerta-work)"""
import os, sys, tarfile, urllib.request, shutil
import onnx
from onnx import helper, TensorProto

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get('OMERTA_WORK', '/home/claude/omerta-work')).rstrip('/')
REL = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/'
VOICES = ['en_US-ryan-high', 'en_US-norman-medium', 'en_US-joe-medium']   # narrateur, parrain, réserve
ASR = 'sherpa-onnx-whisper-base.en'


def fetch(url, dest_dir):
    os.makedirs(dest_dir, exist_ok=True); tmp = os.path.join(dest_dir, 'dl.tar.bz2')
    print('téléchargement', url, flush=True)
    with urllib.request.urlopen(url, timeout=600) as r, open(tmp, 'wb') as f: shutil.copyfileobj(r, f)
    with tarfile.open(tmp, 'r:bz2') as t: t.extractall(dest_dir, filter='data')
    os.remove(tmp)


def add_duration_output(src, dst):
    m = onnx.load(src)
    ceil = [n for n in m.graph.node if n.op_type == 'Ceil']
    assert ceil, 'pas de nœud Ceil (durées) dans ' + src
    out = ceil[0].output[0]
    if out not in [o.name for o in m.graph.output]:
        m.graph.output.append(helper.make_tensor_value_info(out, TensorProto.FLOAT, None))
    onnx.save(m, dst)


def main():
    os.makedirs(WORK, exist_ok=True)
    # scripts et planches du dépôt, vus depuis le dossier de travail (mêmes chemins que les scripts attendent)
    for name, src in (('scripts', 'formats/omerta/scripts'),):
        link = os.path.join(WORK, name)
        if not os.path.exists(link): os.symlink(os.path.join(REPO, src), link)
    pl = os.path.join(WORK, 'planches')
    if not os.path.exists(pl): shutil.copytree(os.path.join(REPO, 'formats/omerta/planches'), pl)
    if not os.path.exists(os.path.join(pl, 'fonts')): os.symlink(os.path.join(REPO, 'assets/fonts'), os.path.join(pl, 'fonts'))
    for v in VOICES:
        d = os.path.join(WORK, 'tts_piper', f'vits-piper-{v}.x'); inner = os.path.join(d, f'vits-piper-{v}')
        if not os.path.exists(os.path.join(inner, f'{v}.onnx')): fetch(REL + f'tts-models/vits-piper-{v}.tar.bz2', d)
        dur = os.path.join(inner, f'{v}.dur.onnx')
        if not os.path.exists(dur): add_duration_output(os.path.join(inner, f'{v}.onnx'), dur); print('durées ajoutées', dur)
    a = os.path.join(WORK, 'asr_dl')
    if not os.path.exists(os.path.join(a, ASR)): fetch(REL + f'asr-models/{ASR}.tar.bz2', a)
    print('prêt :', WORK)


if __name__ == '__main__':
    main()
