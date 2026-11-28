"""サムネ（インパクト型）と縦カバー：地下鉄のトンネルの写真"""
import sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs'); sys.path.insert(0, '/home/claude/mbe')
from thumbkit import *
G = '/home/claude/mbe'
photo = Image.open(f'{G}/ph/05.jpg').convert('RGB')
im = grade(cover(photo, cx=0.62, cy=0.5, zoom=1.0), 1.2, 0.7, 0.75)
im.alpha_composite(Image.new('RGBA', im.size, (20, 40, 80, 50)))
glow(im, 1330, 420, 200, (255, 230, 170), 45)
im = left_shade(im, 0.94, 0.6); im = vignette(im, 0.55)
d = ImageDraw.Draw(im); spaced(d, (70, 95), '都市伝説', SANS(44), GOLD, 8)
impact_lines(im, [[('東京の地下に', 150, 'w')], [('幻の駅', 260, 'r')], [('が', 110, 'w'), ('眠っている', 170, 'w')]], x=60, y0=140, gap=20, max_w=1040)
spaced(ImageDraw.Draw(im), (70, 1030), 'GHOST STATIONS UNDER TOKYO', SANS(32), (235, 232, 225), 4)
save(im, f'{G}/mbe_thumb.jpg')
v = grade(cover(photo, 1080, 1920, cx=0.6, cy=0.5, zoom=1.0), 1.2, 0.7, 0.75); v.alpha_composite(Image.new('RGBA', v.size, (20, 40, 80, 50)))
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.34 - yy) / 0.34, 0, 1) + np.clip((yy - 0.7) / 0.3, 0, 1)) * 0.9
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 150), '都市伝説', font=SANS(50), fill=GOLD, anchor='mm')
for t, y, s, c in [('東京の地下に眠る', 300, 100, WHITE), ('幻の駅', 470, 170, GOLD), ('窓に一瞬だけ見えるホーム', 1700, 70, WHITE)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1850), 'GHOST STATIONS UNDER TOKYO', font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save(f'{G}/mbe_short_cover.jpg', quality=92)
print('thumb done')
