import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
ICE = (140, 215, 255)
def stopwatch(im, cx, cy, R0, frac=0.25):
    glow(im, cx, cy, R0 * 1.5, (60, 140, 255), 110)
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    d.ellipse((cx - R0, cy - R0, cx + R0, cy + R0), outline=ICE + (255,), width=int(R0 * 0.07))
    d.rounded_rectangle((cx - R0 * 0.14, cy - R0 * 1.25, cx + R0 * 0.14, cy - R0 * 1.06), 10, fill=ICE + (255,))
    for i in range(60):
        a = math.radians(i * 6 - 90); r1 = R0 * (0.80 if i % 5 == 0 else 0.86)
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + R0 * 0.92 * math.cos(a), cy + R0 * 0.92 * math.sin(a)), fill=ICE + (255,), width=6 if i % 5 == 0 else 2)
    d.pieslice((cx - R0 * 0.75, cy - R0 * 0.75, cx + R0 * 0.75, cy + R0 * 0.75), -90, -90 + 360 * frac, fill=(232, 32, 42, 150))
    g = l.filter(ImageFilter.GaussianBlur(16)); im.alpha_composite(g); im.alpha_composite(l)
    d = ImageDraw.Draw(im); d.text((cx, cy + 20), '?', font=MIN(int(R0 * 0.9)), fill=(255, 255, 255), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0))
    return im
photo = Image.open('/home/claude/spc/dl/iss044e045215.jpg')
im = grade(cover(photo, cx=0.6, cy=0.72, zoom=1.25), 1.2, 1.0, 0.95)
im = stopwatch(im, 1450, 520, 300, 0.25)
im = left_shade(im, 0.92, 0.62); im = vignette(im, 0.5)
d = ImageDraw.Draw(im); spaced(d, (70, 95), '実データでシミュレーション', SANS(40), GOLD, 5)
y = impact_lines(im, [[('宇宙に', 190, 'w')], [('生身', 300, 'r'), ('で', 140, 'w')], [('何秒', 230, 'y'), ('もつ？', 170, 'w')]], x=60, y0=120, gap=10, max_w=1000)
spaced(ImageDraw.Draw(im), (70, 1030), 'HOW LONG COULD YOU LAST IN SPACE?', SANS(32), (235, 232, 225), 4)
save(im, '/home/claude/spc/spc_thumb.jpg')
# 縦カバー
v = cover(photo, 1080, 1920, cx=0.55, cy=0.5, zoom=1.0); v = grade(v, 1.2, 1.0, 0.9)
v = stopwatch(v, 540, 1040, 300, 0.25)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.33 - yy) / 0.33, 0, 1) + np.clip((yy - 0.66) / 0.34, 0, 1)) * 0.85
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 170), '実データでシミュレーション', font=SANS(46), fill=GOLD, anchor='mm')
for t, y, s, c in [('宇宙に生身で', 380, 120, WHITE), ('放り出されたら', 1560, 104, WHITE), ('何秒もつ？', 1730, 140, GOLD)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1860), 'HOW LONG COULD YOU LAST IN SPACE?', font=SANS(32), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save('/home/claude/spc/spc_short_cover.jpg', quality=92)
