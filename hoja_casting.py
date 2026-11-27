#!/usr/bin/env python3
"""Hoja numerada de opciones (casting, variantes de una imagen) para que se elija por número.

Uso: python3 -I hoja_casting.py salida.jpg img1 img2 ...
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Archivo-VF.ttf")
AHUMADO, CAOBA, HILO = (0x22, 0x1C, 0x19), (0x7A, 0x23, 0x16), (0xF6, 0xF1, 0xE8)


def font(size, wght=800, wdth=112):
    f = ImageFont.truetype(FONT, size)
    vals = []
    for a in f.get_variation_axes():
        n = a.get("name")
        n = n.decode() if isinstance(n, bytes) else str(n)
        if "eight" in n or n == "wght":
            vals.append(wght)
        elif "idth" in n or n == "wdth":
            vals.append(wdth)
        else:
            vals.append(a["default"])
    f.set_variation_by_axes(vals)
    return f


out, paths = sys.argv[1], sys.argv[2:]
CW, CH, GAP, PAD = 720, 1290, 28, 36
W = PAD * 2 + CW * len(paths) + GAP * (len(paths) - 1)
H = PAD * 2 + CH
sheet = Image.new("RGB", (W, H), AHUMADO)
d = ImageDraw.Draw(sheet)
f = font(92)
for i, p in enumerate(paths):
    im = Image.open(p).convert("RGB")
    s = max(CW / im.width, CH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = (im.width - CW) // 2, (im.height - CH) // 2
    im = im.crop((x0, y0, x0 + CW, y0 + CH))
    x = PAD + i * (CW + GAP)
    sheet.paste(im, (x, PAD))
    r = 70
    cx, cy = x + 28 + r, PAD + 28 + r
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CAOBA, outline=HILO, width=5)
    t = str(i + 1)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), t, font=f, fill=HILO)
sheet.save(out, quality=90)
print(out, sheet.size)
