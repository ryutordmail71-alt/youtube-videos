"""サムネ（インパクト型）と縦カバー：本物の写真（ゲームセンター）＋架空の黒いゲーム機"""
import sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs'); sys.path.insert(0, '/home/claude/plb')
from thumbkit import *
import prnd as R
G = '/home/claude/plb'; PH = R.PH
photo = Image.open(f'{PH}/06.jpg')
im = grade(cover(photo, cx=0.62, cy=0.55, zoom=1.0), 1.2, 0.6, 0.62)
im.alpha_composite(Image.new('RGBA', im.size, (20, 40, 80, 60)))
rgb = im.convert('RGB'); R.cabinet(rgb, 1460, 1080, 980, 1.3, 1.0); im = rgb.convert('RGBA')
glow(im, 1460, 380, 260, (110, 230, 220), 50)
im = left_shade(im, 0.92, 0.62); im = vignette(im, 0.55)
d = ImageDraw.Draw(im); spaced(d, (70, 95), '都市伝説', SANS(44), GOLD, 8)
impact_lines(im, [[('遊ぶと', 150, 'w')], [('おかしくなる', 230, 'r')], [('ゲーム', 200, 'w'), ('が', 110, 'w'), ('あった', 160, 'w')]], x=60, y0=140, gap=20, max_w=1040)
spaced(ImageDraw.Draw(im), (70, 1030), 'POLYBIUS - THE ARCADE GAME THAT VANISHED', SANS(32), (235, 232, 225), 4)
save(im, f'{G}/plb_thumb.jpg')
# 縦カバー
v = grade(cover(photo, 1080, 1920, cx=0.66, cy=0.55, zoom=1.0), 1.2, 0.6, 0.62); v.alpha_composite(Image.new('RGBA', v.size, (20, 40, 80, 60)))
rgb = v.convert('RGB'); R.cabinet(rgb, 540, 1450, 900, 1.3, 1.0); v = rgb.convert('RGBA'); glow(v, 540, 820, 240, (110, 230, 220), 50)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.34 - yy) / 0.34, 0, 1) + np.clip((yy - 0.72) / 0.28, 0, 1)) * 0.88
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 150), '都市伝説', font=SANS(50), fill=GOLD, anchor='mm')
for t, y, s, c in [('遊ぶと', 300, 110, WHITE), ('おかしくなるゲーム', 450, 104, GOLD), ('ポリビアス', 1700, 130, WHITE)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1850), 'POLYBIUS - THE ARCADE GAME THAT VANISHED', font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save(f'{G}/plb_short_cover.jpg', quality=92)
print('thumb done')
