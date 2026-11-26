import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
def bg_grad(c1, c2, cx=0.7, cy=0.5, w=W, h=H):
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx / w - cx) * 1.6 * w / W * H / h) ** 2 + (yy / h - cy) ** 2)
    t = np.clip(r / 1.0, 0, 1)[..., None]; a = np.array(c1, float) * (1 - t) + np.array(c2, float) * t
    return Image.fromarray(a.astype(np.uint8)).convert('RGBA')
def vortex(im, cx, cy, R0, tilt=0.42, arms=9, col=(110, 205, 255)):
    """光る渦（上から斜めに見た排水の渦）"""
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    for k in range(arms):
        pts = []
        for i in range(160):
            u = i / 159; r = R0 * (1 - 0.93 * u) ** 1.2; a = k * 2 * math.pi / arms + u * 7.0
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * tilt + 60 * u ** 2))
        for j in range(len(pts) - 1):
            w = max(3, int(22 * (1 - j / len(pts)) + 3)); al = int(255 * (0.35 + 0.65 * j / len(pts)))
            d.line((pts[j], pts[j + 1]), fill=col + (al,), width=w)
    g = l.filter(ImageFilter.GaussianBlur(24)); im.alpha_composite(g); im.alpha_composite(g); im.alpha_composite(l.filter(ImageFilter.GaussianBlur(2)))
    d3 = ImageDraw.Draw(im); hr = R0 * 0.11; d3.ellipse((cx - hr, cy + 55 - hr * tilt, cx + hr, cy + 55 + hr * tilt), fill=(2, 6, 16, 255), outline=(200, 235, 255, 255), width=4)
    rim = Image.new('RGBA', im.size, (0, 0, 0, 0)); rr = R0 * 1.08; ImageDraw.Draw(rim).ellipse((cx - rr, cy - rr * tilt, cx + rr, cy + rr * tilt), outline=(235, 242, 250, 255), width=26)
    im.alpha_composite(rim.filter(ImageFilter.GaussianBlur(18))); im.alpha_composite(rim.filter(ImageFilter.GaussianBlur(3)))
    rng = np.random.default_rng(3); d2 = ImageDraw.Draw(im)
    for _ in range(90):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.3, 1.25) * R0; s = rng.uniform(2, 7)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * tilt; d2.ellipse((x - s, y - s, x + s, y + s), fill=(200, 230, 255, int(rng.uniform(80, 220))))
    return im
im = bg_grad((20, 60, 120), (2, 4, 12), 0.72, 0.5)
im = vortex(im, 1420, 560, 560)
im = left_shade(im, 0.85, 0.55); im = vignette(im, 0.55)
headline(im, '全員でトイレを流したら', '下水はあふれる？', s1=104, s2=150, max_w=1150, english='What if all of Japan flushed at once?')
save(im, '/home/claude/tlt/tlt_thumb.jpg')
# 縦カバー 1080×1920
import thumbkit as TK
v = bg_grad((20, 60, 120), (2, 4, 12), 0.5, 0.5, 1080, 1920)
v = vortex(v, 540, 1000, 470)
d = ImageDraw.Draw(v)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.33 - yy) / 0.33, 0, 1) + np.clip((yy - 0.66) / 0.34, 0, 1)) * 0.85
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 170), '実データでシミュレーション', font=SANS(46), fill=GOLD, anchor='mm')
for t, y, s, c in [('日本中で同時に', 360, 118, WHITE), ('トイレを流したら', 1560, 112, WHITE), ('下水はあふれる？', 1730, 124, GOLD)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1860), 'WHAT IF ALL OF JAPAN FLUSHED AT ONCE?', font=SANS(32), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save('/home/claude/tlt/tlt_short_cover.jpg', quality=92)
