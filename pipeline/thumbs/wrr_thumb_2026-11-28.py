import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
COLS = [(255, 210, 80), (225, 150, 90), (170, 225, 255), (255, 110, 90), (120, 225, 240)]
def stadium(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); yy /= h; xx /= w
    c = np.array((14, 20, 40), np.float32) * (1 - yy[..., None]) + np.array((3, 4, 10), np.float32) * yy[..., None]
    for lx in (0.55, 0.75, 0.95):
        g = np.exp(-(((xx - lx) / 0.08) ** 2 + ((yy - 0.0) / 0.10) ** 2)); c += g[..., None] * np.array((120, 130, 150))
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)).convert('RGBA')
def streaks(im, x0, x1, ys, lens, wid=26):
    for (y, L, col) in zip(ys, lens, COLS):
        l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
        for k in range(16):
            a = int(230 * (k + 1) / 16); xa = x1 - L + L * k / 16; d.rounded_rectangle((xa, y - wid / 2, x1, y + wid / 2), wid // 2, fill=col + (a // 6,))
        d.rounded_rectangle((x1 - L * 0.35, y - wid / 2, x1, y + wid / 2), wid // 2, fill=col + (255,))
        im.alpha_composite(l.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(l.filter(ImageFilter.GaussianBlur(2)))
        glow(im, x1, y, wid * 2.2, col, 200); glow(im, x1, y, wid * 0.7, (255, 255, 255), 255)
def stopwatch(im, cx, cy, R0):
    glow(im, cx, cy, R0 * 1.4, (255, 200, 80), 90)
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l); C = (255, 225, 150, 255)
    d.ellipse((cx - R0, cy - R0, cx + R0, cy + R0), fill=(10, 12, 20, 230), outline=C, width=int(R0 * 0.08))
    d.rounded_rectangle((cx - R0 * 0.15, cy - R0 * 1.28, cx + R0 * 0.15, cy - R0 * 1.06), 10, fill=C)
    for i in range(60):
        a = math.radians(i * 6 - 90); r1 = R0 * (0.78 if i % 5 == 0 else 0.85)
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + R0 * 0.92 * math.cos(a), cy + R0 * 0.92 * math.sin(a)), fill=C, width=6 if i % 5 == 0 else 2)
    g = l.filter(ImageFilter.GaussianBlur(14)); im.alpha_composite(g); im.alpha_composite(l)
    d = ImageDraw.Draw(im); d.text((cx, cy + R0 * 0.05), '1位?', font=MIN(int(R0 * 0.55)), fill=(255, 255, 255), anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0))
im = stadium(1920, 1080)
# 奥のトラックの線
L = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
for i in range(6): y = 600 + i * 92; d.line((700, y, 1920, y), fill=(255, 255, 255, 45), width=3)
im.alpha_composite(L); streaks(im, 700, 1860, [646, 738, 830, 922, 1014], [1100, 900, 760, 560, 240], wid=40)
stopwatch(im, 1430, 300, 220)
im = left_shade(im, 0.9, 0.6); im = vignette(im, 0.5)
d = ImageDraw.Draw(im); spaced(d, (70, 95), '実データでシミュレーション', SANS(40), GOLD, 5)
impact_lines(im, [[('世界記録', 250, 'r'), ('が', 120, 'w')], [('全員で', 190, 'w')], [('100m競争', 200, 'w')]], x=60, y0=130, gap=14, max_w=1000)
spaced(ImageDraw.Draw(im), (70, 1030), 'IF ALL WORLD RECORD HOLDERS RACED 100M', SANS(32), (235, 232, 225), 4)
save(im, '/home/claude/wrr/wrr_thumb.jpg')
# 縦カバー
v = stadium(1080, 1920); L = Image.new('RGBA', v.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
for i in range(6): y = 900 + i * 110; d.line((0, y, 1080, y), fill=(255, 255, 255, 45), width=3)
v.alpha_composite(L)
streaks(v, 0, 980, [955, 1065, 1175, 1285, 1395], [950, 800, 650, 480, 200], wid=44)
stopwatch(v, 540, 620, 200)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.22 - yy) / 0.22, 0, 1) + np.clip((yy - 0.76) / 0.24, 0, 1)) * 0.85
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 150), '実データでシミュレーション', font=SANS(46), fill=GOLD, anchor='mm')
for t, y, s, c in [('世界記録の選手が', 300, 104, WHITE), ('全員で100m競争', 1600, 104, WHITE), ('1位は誰？', 1760, 140, GOLD)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1870), 'IF ALL WORLD RECORD HOLDERS RACED 100M', font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save('/home/claude/wrr/wrr_short_cover.jpg', quality=92)
