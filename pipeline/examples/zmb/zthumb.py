import sys
sys.path.insert(0, '/home/claude/zmb')
from zbase import *
import zscenes as Z
def grad(im, side, a, start):
    w, h = im.size; g_ = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g_)
    if side == 'left':
        for x in range(w): d.line((x, 0, x, h), fill=(0, 0, 0, int(a * max(0, 1 - x / (w * start)))))
    else:
        for y in range(h): d.line((0, y, w, y), fill=(0, 0, 0, int(a * max(0, (y - h * start) / (h * (1 - start))))))
    im.alpha_composite(g_); return im
# 横サムネ
im = bg(1920, 1080, (26, 16, 24)); d = ImageDraw.Draw(im)
Z.draw_map(im, d, 22, k=3.4, ox=930, oy=30, inset=None)
x, y = lonlat_px(*SHIBUYA, 930, 30, 3.4); glow(im, x, y, 60, (255, 40, 30), 170)
im = grad(im, 'left', 230, 0.62); d = ImageDraw.Draw(im)
zombie(d, 1380, 1080, 760, phase=0.6)
d.rounded_rectangle((70, 70, 600, 140), 35, fill=(0, 0, 0, 210)); ctext(d, (335, 105), '実データでシミュレーション', Fb(38), GOLD)
ctext(d, (70, 300), '渋谷にゾンビ1人', Mi(150), PALE, 'lm', 8); ctext(d, (70, 500), '日本は何日で', Mi(150), PALE, 'lm', 8)
ctext(d, (70, 700), '全滅する？', Mi(170), GOLD, 'lm', 9)
ctext(d, (78, 860), 'ONE ZOMBIE IN SHIBUYA. HOW LONG WOULD JAPAN LAST?', Fb(40), (235, 235, 240), 'lm', 2)
im.convert('RGB').resize((1280, 720), Image.LANCZOS).save(f'{G}/zmb_thumb.jpg', quality=92)
# 縦カバー
v = bg(1080, 1920, (26, 16, 24)); d = ImageDraw.Draw(v)
Z.draw_map(v, d, 22, k=3.5, ox=60, oy=880, inset=None)
x, y = lonlat_px(*SHIBUYA, 60, 880, 3.5); glow(v, x, y, 60, (255, 40, 30), 170)
v = grad(v, 'top', 0, 0.5); d = ImageDraw.Draw(v)
zombie(d, 200, 1900, 620, phase=0.6)
ctext(d, (540, 150), '実データでシミュレーション', Fb(48), GOLD, sw=2); ctext(d, (540, 330), '渋谷にゾンビ1人', Mi(118), PALE, sw=7)
ctext(d, (540, 510), '日本は何日で', Mi(118), PALE, sw=6); ctext(d, (540, 690), '全滅する？', Mi(140), GOLD, sw=8)
ctext(d, (540, 800), 'ONE ZOMBIE IN SHIBUYA. HOW LONG WOULD JAPAN LAST?', Fb(30), (230, 230, 235), sw=2)
v.convert('RGB').save(f'{G}/zmb_short_cover.jpg', quality=92)
