from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import hrender as R, hscenes as S
from hrender import Fo, Fb, Mi, PALE, GOLD, ctext
def grad(im, side, a, start):
    W, H = im.size; g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    if side == 'left':
        for x in range(W): d.line((x, 0, x, H), fill=(0, 0, 0, int(a * max(0, 1 - x / (W * start)))))
    else:
        for y in range(H): d.line((0, y, W, y), fill=(0, 0, 0, int(a * max(0, (y - H * start) / (H * (1 - start))))))
    im.alpha_composite(g); return im
im = S.track_blur(0.6); im = grad(im, 'left', 210, 0.7)
d = ImageDraw.Draw(im); c = R.runner(d, 1480, 1060, 820, 0.8, (210, 90, 60)); R.hearts_row(d, c[0], c[1] + 10, 10, 30, 0.0, 160, per=5)
d.rounded_rectangle((70, 70, 600, 140), 35, fill=(0, 0, 0, 200)); ctext(d, (335, 105), '実データでシミュレーション', Fb(38), GOLD)
ctext(d, (70, 330), '心臓が10個', Mi(190), PALE, 'lm', 8); ctext(d, (70, 560), '最強？', Mi(230), GOLD, 'lm', 9)
ctext(d, (78, 740), 'WHAT IF YOU HAD 10 HEARTS?', Fb(40), (235, 235, 240), 'lm', 2)
im.convert('RGB').resize((1280, 720), Image.LANCZOS).save('h10_thumb.jpg', quality=92)
# 縦カバー
R.W, R.H = 1080, 1920
v = S.track_blur(0.55).resize((3413, 1920)).crop((1100, 0, 2180, 1920)).convert('RGBA'); v = grad(v, 'bottom', 220, 0.55)
d = ImageDraw.Draw(v); c = R.runner(d, 560, 1330, 760, 0.8, (210, 90, 60)); R.hearts_row(d, c[0], c[1] + 10, 10, 28, 0.0, 160, per=5)
ctext(d, (540, 150), '実データでシミュレーション', Fb(48), GOLD, sw=2); ctext(d, (540, 330), '心臓が10個', Mi(150), PALE, sw=7)
ctext(d, (540, 1500), 'あったら', Mi(120), PALE, sw=6); ctext(d, (540, 1680), '最強？', Mi(200), GOLD, sw=8)
ctext(d, (540, 1840), 'WHAT IF YOU HAD 10 HEARTS?', Fb(40), (230, 230, 235), sw=2)
v.convert('RGB').save('h10_short_cover.jpg', quality=92)
