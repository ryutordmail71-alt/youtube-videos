"""サムネ（インパクト型）と縦カバー：霧の夜の住宅街の写真（Spritegrape, CC BY 4.0）＋うわさの姿の影"""
import sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs'); sys.path.insert(0, '/home/claude/bek')
from thumbkit import *
import bdraw as B
G = '/home/claude/bek'
photo = Image.open(f'{G}/ph/fogstreet.jpg').convert('RGB')
im = grade(cover(photo, cx=0.45, cy=0.55, zoom=1.0), 1.2, 0.6, 0.8)
im.alpha_composite(Image.new('RGBA', im.size, (20, 40, 80, 70)))
rgb = im.convert('RGB'); B.kids(rgb, 1440, 1000, 640, 1.0, 0.0); im = rgb.convert('RGBA')
glow(im, 1440, 380, 260, (255, 235, 190), 35)
im = left_shade(im, 0.94, 0.6); im = vignette(im, 0.5)
d = ImageDraw.Draw(im); spaced(d, (70, 95), '都市伝説', SANS(44), GOLD, 8)
impact_lines(im, [[('夜、ドアをたたく', 140, 'w')], [('黒い目', 280, 'r')], [('の', 110, 'w'), ('子どもたち', 180, 'w')]], x=60, y0=140, gap=20, max_w=1040)
spaced(ImageDraw.Draw(im), (70, 1030), "BLACK-EYED KIDS - DON'T LET THEM IN", SANS(32), (235, 232, 225), 4)
ImageDraw.Draw(im).text((1890, 1050), '影はうわさの姿のイメージ', font=SANS(26), fill=(220, 220, 225), anchor='rs')
save(im, f'{G}/bek_thumb.jpg')
v = grade(cover(photo, 1080, 1920, cx=0.45, cy=0.5, zoom=1.0), 1.2, 0.6, 0.8); v.alpha_composite(Image.new('RGBA', v.size, (20, 40, 80, 70)))
vr = v.convert('RGB'); B.kids(vr, 540, 1420, 700, 1.0, 0.0); v = vr.convert('RGBA')
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.34 - yy) / 0.34, 0, 1) + np.clip((yy - 0.78) / 0.22, 0, 1)) * 0.9
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 150), '都市伝説', font=SANS(50), fill=GOLD, anchor='mm')
for t, y, s, c in [('夜、ドアをたたく', 300, 100, WHITE), ('黒い目の子どもたち', 460, 120, GOLD), ('ブラックアイド・キッズ', 1700, 80, WHITE)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1830), "BLACK-EYED KIDS - DON'T LET THEM IN", font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save(f'{G}/bek_short_cover.jpg', quality=92)
print('thumb done')
