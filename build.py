#!/usr/bin/env python3
"""Arma el reel vertical (1080x1920) a partir de las tomas, fotos, música y gráfica de marca.

Uso: python3 -I build.py reels/NN_tema/cfg.json
Las rutas relativas del cfg se resuelven contra la carpeta del kit (donde está este archivo).
El resultado queda en out/ y los intermedios en tmp/, junto al cfg.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 24
COL = {
    "ahumado": (0x22, 0x1C, 0x19),
    "caoba": (0x7A, 0x23, 0x16),
    "ambar": (0xC9, 0x8B, 0x2E),
    "hilo": (0xF6, 0xF1, 0xE8),
    "hilo2": (0xC9, 0xC2, 0xB6),
}

cfg = json.load(open(sys.argv[1]))
KIT = os.path.dirname(os.path.abspath(__file__))       # carpeta del kit: tipografía, fotos, música, marca
HERE = os.path.dirname(os.path.abspath(sys.argv[1]))   # carpeta del reel: ahí quedan tmp/ y out/
FONT = os.path.join(KIT, "fonts", "Archivo-VF.ttf")


def R(p):
    """Las rutas relativas del cfg se resuelven contra la carpeta del kit."""
    return p if os.path.isabs(p) else os.path.join(KIT, p)


# textos de la gráfica (se pueden cambiar por reel desde el cfg)
SERIE = cfg.get("serie", "UN DATO POR SEMANA")
TAG_PROD = cfg.get("tag_prod", "TRIPA FIBROSA E.I.")
END_TITLE = cfg.get("endcard_title", "TRIPA FIBROSA E.I.")
END_SUB = cfg.get("endcard_sub", "Embutido Inmediato: se embute sin remojar.")
WEB = cfg.get("web", "destefanosrl.com")
TMP = os.path.join(HERE, "tmp")
OUT = os.path.join(HERE, "out")
os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)


def font(size, wght=700, wdth=110):
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


def tracked(draw, xy, text, f, fill, track=0):
    """Dibuja texto con interletrado manual. Devuelve el ancho total."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + track
    return x - xy[0] - track


def tracked_width(draw, text, f, track=0):
    return sum(draw.textlength(ch, font=f) + track for ch in text) - track


def pill(text, size=30, pad=(24, 12), bg=COL["caoba"], fg=COL["hilo"], track=3, wght=700, wdth=114):
    f = font(size, wght, wdth)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = int(tracked_width(d0, text, f, track))
    asc, desc = f.getmetrics()
    w, h = tw + pad[0] * 2, asc + desc + pad[1] * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg + (255,))
    tracked(d, (pad[0], pad[1]), text, f, fg + (255,), track)
    return im


def logo_badge():
    logo = Image.open(R(cfg["logo"])).convert("RGBA")
    lw = 300
    lh = round(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    pad = (26, 22)
    w, h = lw + pad[0] * 2, lh + pad[1] * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=22, fill=COL["ahumado"] + (225,))
    im.alpha_composite(logo, pad)
    return im


def caption(parts, size=62, maxw=860):
    """parts: lista de [texto, resaltado(0/1)]. Tarjeta oscura con texto crema y resaltado caoba."""
    f = font(size, 700, 108)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    space = d0.textlength(" ", font=f)
    words = []
    for text, hl in parts:
        for w_ in text.split(" "):
            if w_:
                words.append((w_, bool(hl), d0.textlength(w_, font=f)))
    total_w = sum(w_[2] for w_ in words) + space * (len(words) - 1)
    if total_w <= maxw or len(words) < 2:
        lines = [words]
    else:
        # dos renglones lo más parejos posible
        best, best_diff = None, 1e9
        for k in range(1, len(words)):
            w1 = sum(w_[2] for w_ in words[:k]) + space * (k - 1)
            w2 = sum(w_[2] for w_ in words[k:]) + space * (len(words) - k - 1)
            if w1 <= maxw and w2 <= maxw and abs(w1 - w2) < best_diff:
                best, best_diff = k, abs(w1 - w2)
        if best is None:
            best = len(words) // 2
        lines = [words[:best], words[best:]]
    asc, desc = f.getmetrics()
    lh = asc + desc + 14
    widths = [sum(w_[2] for w_ in ln) + space * (len(ln) - 1) for ln in lines]
    padx, pady = 40, 26
    cw, ch = int(max(widths)) + padx * 2, lh * len(lines) + pady * 2 - 14
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=28, fill=COL["ahumado"] + (215,))
    for i, ln in enumerate(lines):
        x = (cw - widths[i]) / 2
        y = pady + i * lh
        # resaltados contiguos
        j = 0
        xx = x
        pos = []
        for w_ in ln:
            pos.append(xx)
            xx += w_[2] + space
        while j < len(ln):
            if ln[j][1]:
                k = j
                while k + 1 < len(ln) and ln[k + 1][1]:
                    k += 1
                x0 = pos[j] - 14
                x1 = pos[k] + ln[k][2] + 14
                d.rounded_rectangle((x0, y - 4, x1, y + asc + desc + 6), radius=16, fill=COL["caoba"] + (255,))
                j = k + 1
            else:
                j += 1
        for w_, p in zip(ln, pos):
            d.text((p, y), w_[0], font=f, fill=COL["hilo"] + (255,))
    return im


def end_card():
    im = Image.new("RGBA", (W, H), COL["ahumado"] + (255,))
    d = ImageDraw.Draw(im)
    tag = pill(SERIE, size=30)
    im.alpha_composite(tag, ((W - tag.width) // 2, 470))
    logo = Image.open(R(cfg["logo"])).convert("RGBA")
    lw = 700
    lh = round(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    im.alpha_composite(logo, ((W - lw) // 2, 600))
    y = 600 + lh + 70
    d.rectangle(((W - 120) // 2, y, (W + 120) // 2, y + 5), fill=COL["caoba"] + (255,))
    y += 60
    t = END_TITLE
    s1 = 62
    f1 = font(s1, 800, 118)
    while tracked_width(d, t, f1, 3) > W - 120 and s1 > 36:   # títulos largos: achicar hasta que entren
        s1 -= 2
        f1 = font(s1, 800, 118)
    tw = tracked_width(d, t, f1, 3)
    tracked(d, ((W - tw) / 2, y), t, f1, COL["hilo"] + (255,), 3)
    y += 96
    t = END_SUB
    s2 = 40
    f2 = font(s2, 500, 104)
    while d.textlength(t, font=f2) > W - 120 and s2 > 26:
        s2 -= 2
        f2 = font(s2, 500, 104)
    d.text(((W - d.textlength(t, font=f2)) / 2, y), t, font=f2, fill=COL["hilo2"] + (255,))
    y += 150
    f3 = font(28, 700, 114)
    t = "WHATSAPP"
    tw = tracked_width(d, t, f3, 5)
    tracked(d, ((W - tw) / 2, y), t, f3, COL["ambar"] + (255,), 5)
    y += 50
    f4 = font(60, 700, 110)
    t = cfg.get("whatsapp", "+54 221 642-2421")
    d.text(((W - d.textlength(t, font=f4)) / 2, y), t, font=f4, fill=COL["hilo"] + (255,))
    y += 100
    f5 = font(38, 500, 106)
    t = WEB
    d.text(((W - d.textlength(t, font=f5)) / 2, y), t, font=f5, fill=COL["hilo2"] + (255,))
    return im


def photo_canvas(path, out):
    """Deja la foto en 2160x3840 (para el zoom lento). Las apaisadas van como tarjeta sobre fondo desenfocado."""
    im = Image.open(path).convert("RGB")
    TW, TH = W * 2, H * 2
    if im.height / im.width >= 1.6:
        s = max(TW / im.width, TH / im.height)
        r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (r.width - TW) // 2, (r.height - TH) // 2
        r.crop((x, y, x + TW, y + TH)).save(out, quality=95)
        return
    s = max(TW / im.width, TH / im.height)
    bg = im.resize((round(im.width * s), round(im.height * s)), Image.BICUBIC)
    x, y = (bg.width - TW) // 2, (bg.height - TH) // 2
    bg = bg.crop((x, y, x + TW, y + TH)).filter(ImageFilter.GaussianBlur(60))
    bg = Image.blend(bg, Image.new("RGB", (TW, TH), COL["ahumado"]), 0.55)
    fw = TW
    fh = round(im.height * fw / im.width)
    fg = im.resize((fw, fh), Image.LANCZOS)
    bg.paste(fg, (0, (TH - fh) // 2 - 120))
    bg.save(out, quality=95)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit("fallo: " + " ".join(cmd[:6]))
    return r


def lufs(path, start=None, dur=None, af="anull"):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", path, "-af", af + ",ebur128=framelog=quiet", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    val = None
    for line in r.stderr.splitlines():
        if line.strip().startswith("I:") and "LUFS" in line:
            val = float(line.split("I:")[1].split("LUFS")[0])
    return val


# ---------- línea de tiempo (EDL explícito) ----------
TAKES = {k: R(v) for k, v in cfg["takes"].items()}
AUD = cfg["audio"]            # [[toma, in, out], ...] en orden: define el reloj del reel
acc, AMAP = 0.0, []
for tk, i0, i1 in AUD:
    AMAP.append((tk, i0, i1, acc))
    acc += i1 - i0
voice_len = acc


def T(tk, t):
    """reloj de una toma -> reloj del reel"""
    for k, i0, i1, st in AMAP:
        if k == tk and i0 - 1e-6 <= t <= i1 + 1e-6:
            return st + (t - i0)
    raise SystemExit(f"tiempo fuera del audio: {tk} {t}")


t_endcard = T(*cfg["endcard_at"])
FADE = 0.35
end_hold = cfg.get("endcard_seconds", 3.0)
total = t_endcard + end_hold
VID = cfg["video"]
starts = [T(*v["at"]) for v in VID]
ends = starts[1:] + [t_endcard + FADE]
spans = list(zip(starts, ends))
for v, (a, b) in zip(VID, spans):
    print(f"  {a:6.2f}-{b:6.2f}  {'toma ' + v['take'] if 'take' in v else 'foto ' + os.path.basename(v['photo'])}")
print(f"  {t_endcard:6.2f}-{total:6.2f}  placa final")

caps = []
for c in cfg["captions"]:
    caps.append((T(c["take"], c["t0"]), T(c["take"], c["t1"]), caption(c["parts"])))
caps.sort(key=lambda c: c[0])
for i in range(len(caps) - 1):
    if caps[i][1] > caps[i + 1][0]:
        caps[i] = (caps[i][0], caps[i + 1][0], caps[i][2])

# ---------- capas gráficas ----------
badge = logo_badge()
tag_serie = pill(SERIE, size=28)
tag_prod = pill(TAG_PROD, size=28)
card = end_card()
BY = 236
BX = W - 56 - badge.width
CAP_Y = 1380
prod_spans = [sp for v, sp in zip(VID, spans) if v.get("tag") == "prod"]


def frame_state(t):
    ci = -1
    for i, (t0, t1, _) in enumerate(caps):
        if t0 <= t < t1:
            ci = i
    tag = 0
    if t < 2.6:
        tag = 1
    elif any(a <= t < b for a, b in prod_spans):
        tag = 2
    a = 0.0
    if t >= t_endcard:
        a = min(1.0, (t - t_endcard) / FADE)
    return (ci, tag, round(a, 2))


cache = {}


def frame_bytes(state):
    if state in cache:
        return cache[state]
    ci, tag, a = state
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if a < 1.0:
        im.alpha_composite(badge, (BX, BY))
        if tag == 1:
            im.alpha_composite(tag_serie, (W - 56 - tag_serie.width, BY + badge.height + 14))
        elif tag == 2:
            im.alpha_composite(tag_prod, (W - 56 - tag_prod.width, BY + badge.height + 14))
        if ci >= 0:
            c = caps[ci][2]
            im.alpha_composite(c, ((W - c.width) // 2, CAP_Y - c.height // 2))
    if a > 0:
        if a >= 1.0:
            im = card.copy()
        else:
            ov = card.copy()
            ov.putalpha(int(255 * a))
            im.alpha_composite(ov)
    b = im.tobytes()
    if len(cache) < 48:
        cache[state] = b
    return b


# ---------- audio ----------
tk_names = list(TAKES.keys())
parts, labels = [], []
for n, (tk, i0, i1) in enumerate(AUD):
    d = i1 - i0
    parts.append(f"[{tk_names.index(tk)}:a]atrim={i0}:{i1},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:st=0:d=0.025,afade=t=out:st={d - 0.035:.3f}:d=0.035[s{n}]")
    labels.append(f"[s{n}]")
voice_af = ";".join(parts) + ";" + "".join(labels) + \
    f"concat=n={len(AUD)}:v=0:a=1,highpass=f=70,aresample=48000,apad=whole_dur={total:.3f}[voice]"
voice_wav = os.path.join(TMP, "voice.wav")
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
for tk in tk_names:
    cmd += ["-i", TAKES[tk]]
run(cmd + ["-filter_complex", voice_af, "-map", "[voice]", "-ac", "2", "-t", f"{total:.3f}", voice_wav])
music_file = R(cfg["music"]["file"])
music_dur = cfg["music"].get("duration")
if not music_dur:
    music_dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                           music_file]).stdout.strip())
music_off = max(0.0, music_dur - total)   # se usa el final de la pista, para que termine junto con el reel
music_wav = os.path.join(TMP, "music.wav")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{music_off:.3f}", "-i", music_file,
     "-t", f"{total:.3f}", "-ar", "48000", "-ac", "2", music_wav])
Lv = lufs(voice_wav, 0, voice_len) or -20.0
Lm = lufs(music_wav) or -16.0
VOICE_T, BED_T, LIFT_T = -15.0, cfg.get("bed_lufs", -33.0), -17.5
gv, gb = VOICE_T - Lv, BED_T - Lm
lift = 10 ** ((LIFT_T - BED_T) / 20)
t_lift = t_endcard - cfg.get("lift_lead", 0.6)   # cuándo empieza a subir la música antes de la placa
print(f"voz {Lv:.1f} LUFS -> {gv:+.1f} dB | música {Lm:.1f} LUFS -> {gb:+.1f} dB, sube x{lift:.1f} en {t_lift:.2f}s")

# ---------- render ----------
inputs, fc, vlabels = [], [], []
for tk in tk_names:
    inputs += ["-i", TAKES[tk]]
look = f"fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.35:5:5:0.0,setsar=1,format=yuv420p"
nin = len(tk_names)
for n, (v, (a, b)) in enumerate(zip(VID, spans)):
    d = b - a
    if "take" in v:
        i0 = v["at"][1]
        # "zoom": acercamiento opcional de la toma (1.0 = sin cambio); "zoom_y": 0 arriba, 1 abajo
        z = float(v.get("zoom", 1.0))
        crop = ""
        if z > 1.001:
            fy = float(v.get("zoom_y", 0.3))
            crop = f"crop=iw/{z:.4f}:ih/{z:.4f}:(iw-ow)/2:(ih-oh)*{fy:.3f},"
        # tpad: si el tramo pide más de lo que dura la toma, se sostiene el último cuadro (no salta a negro)
        fc.append(f"[{tk_names.index(v['take'])}:v]tpad=stop_mode=clone:stop_duration=1,"
                  f"trim=start={i0:.3f}:end={i0 + d:.3f},setpts=PTS-STARTPTS,{crop}{look}[v{n}]")
    else:
        out = os.path.join(TMP, f"photo{n}.jpg")
        photo_canvas(R(v["photo"]), out)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d + 0.5:.3f}", "-i", out]
        frames = max(1, round(d * FPS))
        zoom = "1+0.0009*on" if n % 2 == 0 else "1.07-0.0009*on"
        fc.append(f"[{nin}:v]zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
                  f"trim=end_frame={frames},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[v{n}]")
        nin += 1
    vlabels.append(f"[v{n}]")
dur_tail = total - ends[-1]
fc.append(f"color=c=0x221C19:s={W}x{H}:r={FPS}:d={dur_tail + 0.3:.3f},format=yuv420p[tail]")
vlabels.append("[tail]")
i_voice, i_music, i_ov = nin, nin + 1, nin + 2
inputs += ["-i", voice_wav, "-i", music_wav,
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0"]
fc.append("".join(vlabels) + f"concat=n={len(vlabels)}:v=1:a=0,noise=alls=3:allf=t[base]")
fc.append(f"[base][{i_ov}:v]overlay=0:0:format=auto,format=yuv420p[vout]")
fc.append(f"[{i_voice}:a]volume={gv:.2f}dB[vo]")
fc.append(f"[{i_music}:a]volume={gb:.2f}dB,afade=t=in:st=0:d=0.5,"
          f"volume=eval=frame:volume='if(lt(t,{t_lift:.3f}),1,min({lift:.3f},1+(t-{t_lift:.3f})/0.8*({lift:.3f}-1)))',"
          f"afade=t=out:st={total - 0.4:.3f}:d=0.4[mu]")
fc.append("[vo][mu]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false[aout]")
out_file = os.path.join(OUT, cfg.get("out", "reel1.mp4"))
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs + [
    "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
    "-t", f"{total:.3f}", "-r", str(FPS),
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "7M", "-bufsize", "14M",
    "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-movflags", "+faststart", out_file]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
nframes = round(total * FPS)
try:
    for n in range(nframes):
        p.stdin.write(frame_bytes(frame_state(n / FPS)))
    p.stdin.close()
except BrokenPipeError:
    pass
err = p.stderr.read().decode()[-3000:]
if p.wait() != 0:
    sys.stderr.write(err)
    raise SystemExit("fallo el render")
final = lufs(out_file)
print(f"listo: {out_file} | {os.path.getsize(out_file) / 1e6:.1f} MB | {total:.2f} s | {final} LUFS")
json.dump({"spans": spans, "t_endcard": t_endcard, "total": total,
           "captions": [[round(c[0], 2), round(c[1], 2)] for c in caps]},
          open(os.path.join(TMP, "timeline.json"), "w"))
