"""サムネ（上品型）と縦カバー：NASA の月の写真"""
import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
G = '/home/claude/mon'
photo = Image.open(f'{G}/dl/iss072e618284.jpg')
im = grade(cover(photo, cx=0.392, cy=0.560, zoom=2.3), 1.2, 1.1, 1.02)
# 月のまわりに光と、近づいてくる軌跡（うすい円弧）
mx, my = 1430, 420
for r, a in ((430, 36), (300, 54), (200, 70)):
    ring = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((mx - r * 1.5, my - r, mx + r * 1.5, my + r), outline=(150, 200, 255, a), width=3)
    im.alpha_composite(ring.filter(ImageFilter.GaussianBlur(2)))
glow(im, mx, my, 380, (150, 195, 255), 55)
im = left_shade(im, 0.95, 0.62); im = vignette(im, 0.5)
headline(im, '月が半分の距離に', '潮は8倍になる', y1=430, y2=620, s1=118, s2=140, max_w=900, english='What if the Moon came twice as close?')
save(im, f'{G}/mon_thumb.jpg')
# 縦カバー
v = cover(photo, 1080, 1920, cx=0.498, cy=0.626, zoom=1.66); v = grade(v, 1.2, 1.1, 1.02)
glow(v, 540, 620, 330, (150, 195, 255), 65)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.3 - yy) / 0.3, 0, 1) + np.clip((yy - 0.62) / 0.38, 0, 1)) * 0.88
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 12, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 170), '実データでシミュレーション', font=SANS(46), fill=GOLD, anchor='mm')
for t, y, s, c in [('月が今の半分の', 340, 96, WHITE), ('距離に近づいたら', 1480, 104, WHITE), ('潮は8倍', 1660, 140, GOLD)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1810), 'WHAT IF THE MOON CAME TWICE AS CLOSE?', font=SANS(28), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save(f'{G}/mon_short_cover.jpg', quality=92)
print('thumb done')
