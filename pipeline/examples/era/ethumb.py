from PIL import Image, ImageDraw
import erender as R
from erender import Fo, Fb, Mi, PALE, GOLD, ctext
def grad(im, side, a, start):
    W, H = im.size; g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    if side == 'left':
        for x in range(W): d.line((x, 0, x, H), fill=(0, 0, 0, int(a * max(0, 1 - x / (W * start)))))
    else:
        for y in range(H): d.line((0, y, W, y), fill=(0, 0, 0, int(a * max(0, (y - H * start) / (H * (1 - start))))))
    im.alpha_composite(g); return im
im = R.water_bg('lake').copy(); im = grad(im, 'left', 215, 0.7)
d = ImageDraw.Draw(im, 'RGBA'); R.bubbles(d, 1.0, 900, 1920, 0, 1080, 30, 2, (5, 12)); R.swimmer(d, 1400, 820, 860, 0.6, 'gill', 0.25, 2.0, flow=0.9)
d.rounded_rectangle((70, 70, 600, 140), 35, fill=(0, 0, 0, 200)); ctext(d, (335, 105), '実データでシミュレーション', Fb(38), GOLD)
ctext(d, (70, 320), 'エラがあれば', Mi(170), PALE, 'lm', 8); ctext(d, (70, 540), '水中で暮らせる？', Mi(150), GOLD, 'lm', 8)
ctext(d, (78, 720), 'WHAT IF HUMANS HAD GILLS?', Fb(40), (235, 235, 240), 'lm', 2)
im.convert('RGB').resize((1280, 720), Image.LANCZOS).save('era_thumb.jpg', quality=92)
v = R.water_bg('lake', 1080, 1920).copy(); v = grad(v, 'bottom', 220, 0.55)
d = ImageDraw.Draw(v, 'RGBA'); R.bubbles(d, 1.0, 0, 1080, 0, 1920, 30, 2, (5, 12)); R.swimmer(d, 470, 1000, 820, 0.6, 'gill', 0.25, 2.0, flow=0.9)
ctext(d, (540, 150), '実データでシミュレーション', Fb(48), GOLD, sw=2); ctext(d, (540, 330), 'エラがあれば', Mi(140), PALE, sw=7)
ctext(d, (540, 1520), '水中で', Mi(150), PALE, sw=6); ctext(d, (540, 1690), '暮らせる？', Mi(170), GOLD, sw=8)
ctext(d, (540, 1840), 'WHAT IF HUMANS HAD GILLS?', Fb(40), (230, 230, 235), sw=2)
v.convert('RGB').save('era_short_cover.jpg', quality=92)
