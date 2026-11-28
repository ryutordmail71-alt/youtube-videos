"""サムネ（上品型）と縦カバー：夕方の空の写真（NASA KSC-20190302-PH_JBS01_0011）＋うわさの姿のイメージ"""
import sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs'); sys.path.insert(0, '/home/claude/sky')
from thumbkit import *
from thumbkit import _shadow_text
import sdraw as S
G = '/home/claude/sky'
photo = Image.open(f'{G}/ph/sky.jpg').convert('RGB')
im = grade(cover(photo, cx=0.5, cy=0.45, zoom=1.05), 1.15, 0.75, 0.85)
im.alpha_composite(Image.new('RGBA', im.size, (20, 35, 80, 60)))
rgb = im.convert('RGB'); S.skyfish(rgb, 1530, 330, -0.3, 680, 1.3, 1.0); S.skyfish(rgb, 1620, 760, -0.2, 300, 2.1, 0.6); im = rgb.convert('RGBA')
im = left_shade(im, 0.95, 0.6); im = vignette(im, 0.5)
x, y1, y2 = 110, 520, 730
d = ImageDraw.Draw(im); ky = y1 - 150 - 40; d.line((x, ky - 12, x + 70, ky - 12), fill=GOLD, width=4)
spaced(d, (x + 92, ky), '都市伝説', SANS(40), GOLD, 8)
_shadow_text(im, (x, y1), 'カメラにだけ写る', MIN(120), WHITE, stroke=2)
_shadow_text(im, (x, y2), '謎の生き物', MIN(180), GOLD, stroke=2, glowcol=(255, 170, 40))
spaced(ImageDraw.Draw(im), (x + 4, y2 + 95), 'SKYFISH - A CREATURE ONLY CAMERAS CAN SEE?', SANS(28), (230, 228, 222, 210), 4)
ImageDraw.Draw(im).text((1890, 1050), 'イラストはうわさの姿のイメージ', font=SANS(26), fill=(220, 220, 225), anchor='rs')
save(im, f'{G}/sky_thumb.jpg')
v = grade(cover(photo, 1080, 1920, cx=0.5, cy=0.5, zoom=1.0), 1.15, 0.75, 0.85); v.alpha_composite(Image.new('RGBA', v.size, (20, 35, 80, 60)))
vr = v.convert('RGB'); S.skyfish(vr, 560, 1000, -0.35, 760, 1.3, 1.0); v = vr.convert('RGBA')
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.34 - yy) / 0.34, 0, 1) + np.clip((yy - 0.7) / 0.3, 0, 1)) * 0.9
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 12, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 170), '都市伝説', font=SANS(50), fill=GOLD, anchor='mm')
for t, y, s, c in [('カメラにだけ写る', 340, 100, WHITE), ('謎の生き物', 500, 150, GOLD), ('スカイフィッシュ', 1650, 110, WHITE)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1790), 'SKYFISH - A CREATURE ONLY CAMERAS CAN SEE?', font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save(f'{G}/sky_short_cover.jpg', quality=92)
print('thumb done')
