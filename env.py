#!/usr/bin/env python3
"""Tramos de voz por envolvente RMS. Uso: python3 -I env.py archivo [umbral_rel] [hueco_min]
Imprime los tramos con voz (inicio-fin) y las pausas entre ellos."""
import subprocess
import sys

import numpy as np

src = sys.argv[1]
rel = float(sys.argv[2]) if len(sys.argv) > 2 else 0.07
gap_min = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
SR = 16000
pcm = np.frombuffer(subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
    capture_output=True).stdout, dtype=np.float32)
# pasa-altos simple para sacar el zumbido de heladera
x = pcm - np.convolve(pcm, np.ones(160) / 160, mode="same")
win, hop = 320, 160
n = 1 + (len(x) - win) // hop
rms = np.array([np.sqrt(np.mean(x[i * hop:i * hop + win] ** 2)) for i in range(n)])
ref = np.percentile(rms, 97)
floor = np.percentile(rms, 8)
thr = max(ref * rel, floor * 2.5)
act = rms > thr
segs, start = [], None
for i, a in enumerate(act):
    t = i * hop / SR
    if a and start is None:
        start = t
    elif not a and start is not None:
        segs.append([start, t])
        start = None
if start is not None:
    segs.append([start, n * hop / SR])
merged = []
for s in segs:
    if merged and s[0] - merged[-1][1] < gap_min:
        merged[-1][1] = s[1]
    else:
        merged.append(s)
merged = [s for s in merged if s[1] - s[0] >= 0.06]
print(f"dur {len(pcm) / SR:.2f}s  piso {20 * np.log10(floor + 1e-9):.1f} dB  ref {20 * np.log10(ref + 1e-9):.1f} dB  umbral {20 * np.log10(thr + 1e-9):.1f} dB")
prev = None
for a, b in merged:
    gap = f"  (pausa {a - prev:.2f})" if prev is not None else ""
    print(f"  {a:6.2f} - {b:6.2f}  [{b - a:.2f}]{gap}")
    prev = b
