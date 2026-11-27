import sys, os
from PIL import Image, ImageDraw
out, cols, cell = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
paths = sys.argv[4:]
rows = (len(paths) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rows * (cell + 16)), (30, 30, 30))
d = ImageDraw.Draw(sheet)
for i, p in enumerate(paths):
    try:
        im = Image.open(p).convert("RGB")
    except Exception as e:
        continue
    w, h = im.size
    im.thumbnail((cell - 4, cell - 4))
    x = (i % cols) * cell + (cell - im.size[0]) // 2
    y = (i // cols) * (cell + 16) + (cell - im.size[1]) // 2
    sheet.paste(im, (x, y))
    d.text(((i % cols) * cell + 3, (i // cols) * (cell + 16) + cell), f"{os.path.basename(p)[:26]} {w}x{h}", fill=(230, 230, 230))
sheet.save(out, quality=80)
print(out, sheet.size)
