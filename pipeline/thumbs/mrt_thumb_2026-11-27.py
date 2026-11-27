import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
AQ = (140, 230, 245)
def diver(im, cx, cy, s):
    """光る小さな人影（落ちていく）"""
    glow(im, cx, cy, s * 1.6, (120, 210, 255), 150); l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l); c = (230, 250, 255, 255)
    d.ellipse((cx - s * 0.16, cy - s * 0.62, cx + s * 0.16, cy - s * 0.3), fill=c); d.rounded_rectangle((cx - s * 0.17, cy - s * 0.28, cx + s * 0.17, cy + s * 0.2), 10, fill=c)
    for a, b in (((-0.15, -0.22), (-0.55, -0.62)), ((0.15, -0.22), (0.55, -0.62)), ((-0.1, 0.18), (-0.3, 0.7)), ((0.1, 0.18), (0.3, 0.7))):
        d.line((cx + a[0] * s, cy + a[1] * s, cx + b[0] * s, cy + b[1] * s), fill=c, width=int(s * 0.1))
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(6))); im.alpha_composite(l)
photo = Image.open('/home/claude/mrt/dl/PIA11019.jpg').transpose(Image.FLIP_LEFT_RIGHT)
im = grade(cover(photo, cx=0.42, cy=0.62, zoom=1.25), 1.25, 1.15, 1.0)
# 深い穴の中心へ落ちていく光の筋と人影
sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((1050, 560, 1900, 1250), fill=(0, 0, 12, 170)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(80)))
for wdt, al in ((260, 50), (120, 80), (40, 120)):
    ray = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ray).polygon([(1440 - wdt, 0), (1440 + wdt, 0), (1440 + wdt * 0.15, 860), (1440 - wdt * 0.15, 860)], fill=(170, 230, 255, al)); im.alpha_composite(ray.filter(ImageFilter.GaussianBlur(25)))
glow(im, 1440, 860, 140, (90, 190, 255), 160); glow(im, 1440, 860, 34, (230, 250, 255), 255)
im = left_shade(im, 0.95, 0.66); im = vignette(im, 0.55)
headline(im, 'マリアナ海溝の底', '落ちたらどうなる？', s1=130, s2=140, max_w=1000, english='What if you fell to the bottom of the Mariana Trench?')
save(im, '/home/claude/mrt/mrt_thumb.jpg')
# 縦カバー
v = cover(photo, 1080, 1920, cx=0.55, cy=0.7, zoom=1.0); v = grade(v, 1.25, 1.15, 1.0)
ray = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(ray).polygon([(400, 0), (680, 0), (560, 1200), (520, 1200)], fill=(170, 230, 255, 80)); v.alpha_composite(ray.filter(ImageFilter.GaussianBlur(30)))
glow(v, 540, 1200, 160, (90, 190, 255), 170); glow(v, 540, 1200, 40, (230, 250, 255), 255)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.33 - yy) / 0.33, 0, 1) + np.clip((yy - 0.66) / 0.34, 0, 1)) * 0.85
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 170), '実データでシミュレーション', font=SANS(46), fill=GOLD, anchor='mm')
for t, y, s, c in [('マリアナ海溝の底に', 380, 104, WHITE), ('落ちたら', 1560, 120, WHITE), ('どうなる？', 1730, 140, GOLD)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1860), 'WHAT IF YOU FELL TO THE BOTTOM OF THE TRENCH?', font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save('/home/claude/mrt/mrt_short_cover.jpg', quality=92)
