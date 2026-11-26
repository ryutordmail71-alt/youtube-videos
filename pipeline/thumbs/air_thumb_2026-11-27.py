import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
def red_eye(im, cx, cy, R0):
    glow(im, cx, cy, R0 * 1.6, (255, 40, 40), 120)
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    d.ellipse((cx - R0, cy - R0, cx + R0, cy + R0), outline=(255, 90, 90, 255), width=int(R0 * 0.05))
    for k, rr in enumerate((0.8, 0.6)):
        for s in range(6):
            a0 = s * 60 + k * 25; d.arc((cx - R0 * rr, cy - R0 * rr, cx + R0 * rr, cy + R0 * rr), a0, a0 + 36, fill=(255, 60, 60, 255), width=int(R0 * 0.07))
    rc = R0 * 0.28; d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), fill=(255, 50, 50, 255))
    rc2 = R0 * 0.1; d.ellipse((cx - rc2, cy - rc2, cx + rc2, cy + rc2), fill=(255, 235, 235, 255))
    g = l.filter(ImageFilter.GaussianBlur(18)); im.alpha_composite(g); im.alpha_composite(g); im.alpha_composite(l.filter(ImageFilter.GaussianBlur(1.5)))
    return im
photo = Image.open('/home/claude/air/dl/iss073e0824492.jpg')
im = grade(cover(photo, cx=0.62, cy=0.5, zoom=1.0), 1.25, 0.95, 0.95)
red = Image.new('RGBA', im.size, (110, 0, 10, 30)); im.alpha_composite(red)
im = red_eye(im, 1480, 330, 240)
im = left_shade(im, 0.9, 0.6); im = vignette(im, 0.55)
headline(im, 'AIが反乱したら', '人類は何日もつ？', s1=130, s2=150, max_w=1100, english='If AI rebelled, how long would we last?')
save(im, '/home/claude/air/air_thumb.jpg')
# 縦カバー
v = cover(photo, 1080, 1920, cx=0.7, cy=0.5, zoom=1.0)
v = grade(v, 1.25, 0.95, 0.9); v.alpha_composite(Image.new('RGBA', v.size, (110, 0, 10, 30)))
v = red_eye(v, 540, 980, 330)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.33 - yy) / 0.33, 0, 1) + np.clip((yy - 0.66) / 0.34, 0, 1)) * 0.85
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 170), '実データでシミュレーション', font=SANS(46), fill=GOLD, anchor='mm')
for t, y, s, c in [('AIが反乱したら', 380, 120, WHITE), ('人類は', 1560, 112, WHITE), ('何日もつ？', 1730, 140, GOLD)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1860), 'IF AI REBELLED, HOW LONG WOULD WE LAST?', font=SANS(32), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save('/home/claude/air/air_short_cover.jpg', quality=92)
