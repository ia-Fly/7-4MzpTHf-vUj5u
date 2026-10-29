#!/usr/bin/env bash
# Installe l'atelier dans une session neuve.
#   bash setup.sh            -> format FUSION (simulation, sans voix) : ~1 min
#   bash setup.sh --voices   -> + épisodes à voix (Omertà) : voix piper + Whisper (~400 Mo, ~3 min)
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q pymunk skia-python pyloudnorm soundfile scipy numpy pillow 2>&1 | grep -v -i "warning" || true
if [ "$1" = "--voices" ]; then
  pip install --break-system-packages -q pyworld phonemizer espeakng-loader onnxruntime onnx sherpa-onnx 2>&1 | grep -v -i "warning" || true
  export OMERTA_WORK="${OMERTA_WORK:-/home/claude/omerta-work}"
  python3 tools/fetch_models.py "$OMERTA_WORK"
fi
python3 -c "import pymunk, skia, pyloudnorm; print('atelier prêt (fusion)')"
which ffmpeg >/dev/null && echo "ffmpeg ok"
