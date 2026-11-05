#!/usr/bin/env bash
# Installe l'atelier dans une session neuve : format CINE (montage de vidéos ElevenLabs), ~1 min.
#   bash setup.sh            -> montage CINE + contrôle qualité
#   bash setup.sh --voices   -> + anciennes voix piper et Whisper (épisodes Omertà d'avant le 05/11, ~400 Mo, ~3 min)
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q opencv-python-headless pyloudnorm soundfile scipy numpy pillow 2>&1 | grep -v -i "warning" || true
if [ "$1" = "--voices" ]; then
  pip install --break-system-packages -q pymunk skia-python pyworld phonemizer espeakng-loader onnxruntime onnx sherpa-onnx 2>&1 | grep -v -i "warning" || true
  export OMERTA_WORK="${OMERTA_WORK:-/home/claude/omerta-work}"
  python3 tools/fetch_models.py "$OMERTA_WORK"
fi
python3 -c "import cv2, pyloudnorm, soundfile, scipy; print('atelier prêt (cine)')"
which ffmpeg >/dev/null && echo "ffmpeg ok"
