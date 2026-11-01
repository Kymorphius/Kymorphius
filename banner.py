# GitHub 主页横幅：一圆一点，由点荡开几道极淡的水波；下面一行“面壁无为 感而遂通”
# 与微信头像 L5 同形同色（素色、淡墨细线、淡晕）；出纸地、墨地两张，分别给浅色与深色模式
# 用法：python3 -I banner.py <字体文件>
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = sys.argv[1]
W, H, SS = 1600, 600, 3
TONES = {
    'paper': dict(bg=(245, 245, 242), ring=(54, 54, 52), dot=(188, 36, 42), text=(110, 110, 106), light=True),
    'ink': dict(bg=(22, 22, 22), ring=(232, 232, 229), dot=(214, 52, 56), text=(150, 150, 146), light=False),
}
R, STROKE, DOT, GAP = 0.25, 0.0085, 0.054, 0.020          # 都按横幅高度的比例
CX, CY = 0.5, 0.40                                      # 圆心：横向居中，略偏上
RIPPLE = [(0.30, 0.050, 0.045), (0.55, 0.030, 0.060), (0.85, 0.016, 0.075)]
TITLE, TITLE_Y, TITLE_SIZE, TRACK = '面壁无为　感而遂通', 0.84, 0.062, 0.32


def banner(col):
    w, h = W * SS, H * SS
    k = R * h * math.sqrt(0.5)
    dx, dy = CX * w - k, CY * h - k
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    dist = np.hypot(xx - dx, yy - dy) / h
    acc = sum(a * np.exp(-(((dist - r) / s) ** 2)) for r, a, s in RIPPLE)
    acc = np.clip(acc, 0, 1)[..., None]
    base = np.empty((h, w, 3), np.float32)
    base[:] = col['bg']
    tint = np.asarray(col['ring'], np.float32)
    base = base * (1 - acc * (1 - tint / 255)) if col['light'] else base * (1 - acc) + tint * acc
    im = Image.fromarray(np.clip(base + 0.5, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    r, s = R * h, STROKE * h
    cx, cy = CX * w, CY * h
    d.ellipse((cx - r - s / 2, cy - r - s / 2, cx + r + s / 2, cy + r + s / 2), outline=col['ring'], width=round(s))
    dr, g = DOT * h, GAP * h
    d.ellipse((dx - dr - g, dy - dr - g, dx + dr + g, dy + dr + g), fill=col['bg'])
    d.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=col['dot'])
    font = ImageFont.truetype(FONT, round(TITLE_SIZE * h))
    try:
        font.set_variation_by_axes([400])
    except Exception:
        pass
    gap = TRACK * TITLE_SIZE * h
    widths = [d.textlength(ch, font=font) for ch in TITLE]
    x = cx - (sum(widths) + gap * (len(TITLE) - 1)) / 2
    for ch, cw in zip(TITLE, widths):
        d.text((x, TITLE_Y * h), ch, font=font, fill=col['text'], anchor='lm')
        x += cw + gap
    return im.resize((W, H), Image.LANCZOS)


for name, col in TONES.items():
    banner(col).save(f'banner-{name}.png', optimize=True)
print('ok')
