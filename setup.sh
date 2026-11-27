#!/usr/bin/env bash
# Prepara una sesión nueva para armar reels. Uso: bash setup.sh
set -euo pipefail
pip install -q numpy pillow sherpa-onnx 2>/dev/null || pip install -q --break-system-packages numpy pillow sherpa-onnx
M="${ASR_MODEL:-/home/claude/work/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8}"
if [ ! -f "$M/tokens.txt" ]; then
  mkdir -p "$(dirname "$M")"
  curl -sL --retry 3 -o /tmp/asr.tar.bz2 \
    https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2
  tar -xjf /tmp/asr.tar.bz2 -C "$(dirname "$M")"
  rm -f /tmp/asr.tar.bz2
fi
command -v ffmpeg >/dev/null || echo "falta ffmpeg: apt-get install -y ffmpeg"
python3 -c "import sherpa_onnx, numpy, PIL; print('kit listo')"
