"""サムネ（上品型）と縦カバー：ビーレフェルトのスパーレンブルク城の写真"""
import sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
from thumbkit import _shadow_text
G = '/home/claude/bie'; PH = '/home/claude/youtube-videos/assets/photos/bielefeld'
photo = Image.open(f'{PH}/09.jpg').convert('RGB')
bg = Image.new('RGBA', (W, H), (8, 12, 24, 255))
ph = photo.resize((int(photo.width * H / photo.height * 1.08), int(H * 1.08)), Image.LANCZOS)
m = np.clip(np.linspace(0, 1, ph.width) / 0.35, 0, 1) ** 1.5; m = Image.fromarray((np.repeat(m[None, :], ph.height, 0) * 255).astype(np.uint8))
bg.paste(ph.convert('RGBA'), (W - ph.width + 120, -60), m)
im = grade(bg, 1.15, 0.7, 0.9)
im.alpha_composite(Image.new('RGBA', im.size, (20, 35, 80, 70)))
glow(im, 1360, 300, 300, (255, 220, 150), 40)
im = left_shade(im, 0.97, 0.6); im = vignette(im, 0.5)
x, y1, y2 = 110, 470, 680
d = ImageDraw.Draw(im); ky = y1 - 150 - 40; d.line((x, ky - 12, x + 70, ky - 12), fill=GOLD, width=4)
spaced(d, (x + 92, ky), '都市伝説', SANS(40), GOLD, 8)
_shadow_text(im, (x, y1), '人口34万人の町は', MIN(126), WHITE, stroke=2)
_shadow_text(im, (x, y2), '存在しない？', MIN(170), GOLD, stroke=2, glowcol=(255, 170, 40))
spaced(ImageDraw.Draw(im), (x + 4, y2 + 90), 'BIELEFELD - THE CITY THAT DOES NOT EXIST?', SANS(28), (230, 228, 222, 210), 4)
save(im, f'{G}/bie_thumb.jpg')
# 縦カバー
v = cover(photo, 1080, 1920, cx=0.45, cy=0.5, zoom=1.0); v = grade(v, 1.15, 0.7, 0.9); v.alpha_composite(Image.new('RGBA', v.size, (20, 35, 80, 70)))
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.34 - yy) / 0.34, 0, 1) + np.clip((yy - 0.66) / 0.34, 0, 1)) * 0.9
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 12, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 170), '都市伝説', font=SANS(50), fill=GOLD, anchor='mm')
for t, y, s, c in [('人口34万人の町は', 340, 100, WHITE), ('存在しない？', 490, 130, GOLD), ('ビーレフェルト', 1650, 120, WHITE)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1790), 'BIELEFELD - THE CITY THAT DOES NOT EXIST?', font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save(f'{G}/bie_short_cover.jpg', quality=92)
print('thumb done')
