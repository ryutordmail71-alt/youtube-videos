import sys
sys.path.insert(0, '/home/claude/met')
from mbase import *
def grad(im, a, start):
    w, h = im.size; g_ = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g_)
    for x in range(w): d.line((x, 0, x, h), fill=(0, 0, 0, int(a * max(0, 1 - x / (w * start)))))
    im.alpha_composite(g_); return im
def fire(im, d, cx, cy, r):
    glow(im, cx, cy, r * 2.4, (255, 120, 40), 170); glow(im, cx, cy, r * 1.2, (255, 220, 150), 230)
    for k in range(24):
        q = k / 24; d.line((cx, cy, cx + 700 * q, cy - 560 * q), fill=(255, int(210 - 130 * q), 80, int(220 * (1 - q))), width=max(2, int(r * 0.9 * (1 - q))))
    d.ellipse((cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5), fill=(255, 250, 230))
im = bg(1920, 1080, (16, 16, 30)); im.alpha_composite(map_img(2.6, 1920, 1080, 1380, 640)); d = ImageDraw.Draw(im)
ring(im, 1380, 640, 40 * 2.6, RED, 110, 255, 6); ring(im, 1380, 640, 200 * 2.6, (255, 120, 60), 35, 200, 5)
fire(im, d, 1450, 560, 60)
im = grad(im, 235, 0.6); d = ImageDraw.Draw(im)
d.rounded_rectangle((70, 70, 600, 140), 35, fill=(0, 0, 0, 210)); ctext(d, (335, 105), '実データでシミュレーション', Fb(38), GOLD)
ctext(d, (70, 310), '東京に隕石', Mi(170), PALE, 'lm', 8); ctext(d, (70, 520), '落ちたら？', Mi(170), PALE, 'lm', 8)
ctext(d, (70, 730), '1kmで関東が…', Mi(140), GOLD, 'lm', 8)
ctext(d, (78, 880), 'WHAT IF AN ASTEROID HIT TOKYO?', Fb(42), (235, 235, 240), 'lm', 2)
im.convert('RGB').resize((1280, 720), Image.LANCZOS).save(f'{G}/met_thumb.jpg', quality=92)
v = bg(1080, 1920, (16, 16, 30)); v.alpha_composite(map_img(2.2, 1080, 1920, 540, 1350)); d = ImageDraw.Draw(v)
ring(v, 540, 1350, 40 * 2.2, RED, 110, 255, 6); ring(v, 540, 1350, 200 * 2.2, (255, 120, 60), 35, 200, 5); fire(v, d, 600, 1250, 55)
ctext(d, (540, 150), '実データでシミュレーション', Fb(48), GOLD, sw=2); ctext(d, (540, 340), '東京に隕石が', Mi(120), PALE, sw=7)
ctext(d, (540, 520), '落ちたら？', Mi(130), PALE, sw=7); ctext(d, (540, 700), '10m・100m・1km', Mi(100), GOLD, sw=7)
ctext(d, (540, 820), 'WHAT IF AN ASTEROID HIT TOKYO?', Fb(34), (230, 230, 235), sw=2)
v.convert('RGB').save(f'{G}/met_short_cover.jpg', quality=92)
print('thumbs')
