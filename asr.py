#!/usr/bin/env python3
"""Transcribe con marcas de tiempo por palabra. Uso: python3 asr.py archivo [inicio] [duracion]

Sirve para controlar que cada toma diga el guion completo y una sola vez, sin poder oírla.
Guarda <archivo>.asr.json. Las marcas de inicio de palabra salen entre 0,1 y 0,4 s adelantadas:
para cortes usar env.py (envolvente), no estas marcas.
El modelo se baja con setup.sh; su carpeta se puede cambiar con la variable ASR_MODEL.
"""
import json
import os
import subprocess
import sys

import numpy as np
import sherpa_onnx

M = os.environ.get("ASR_MODEL", "/home/claude/work/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")
src = sys.argv[1]
ss = sys.argv[2] if len(sys.argv) > 2 else None
dur = sys.argv[3] if len(sys.argv) > 3 else None
cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
if ss:
    cmd += ["-ss", ss]
if dur:
    cmd += ["-t", dur]
cmd += ["-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]
pcm = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, dtype=np.float32)
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx", joiner=f"{M}/joiner.int8.onnx",
    tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=2)
st = rec.create_stream()
st.accept_waveform(16000, pcm)
rec.decode_stream(st)
r = st.result
words, cur, t0 = [], "", None
for tok, ts in zip(r.tokens, r.timestamps):
    if tok.startswith(" ") or tok.startswith("▁"):
        if cur:
            words.append([cur, round(t0, 2)])
        cur, t0 = tok.strip(" ▁"), ts
    else:
        if t0 is None:
            t0 = ts
        cur += tok
if cur:
    words.append([cur, round(t0, 2)])
print(r.text.strip())
print(" ".join(f"{w}@{t}" for w, t in words))
json.dump({"text": r.text.strip(), "words": words, "dur": len(pcm) / 16000},
          open(os.path.splitext(src)[0] + ".asr.json", "w"), ensure_ascii=False)
