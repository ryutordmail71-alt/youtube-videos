from PIL import Image, ImageDraw
import hrender as R
from hrender import Fo, Fb, Mi, PALE, GOLD, ctext
def grad(im, side, a, start):
    W, H = im.size; g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    if side == 'left':
        for x in range(W): d.line((x, 0, x, H), fill=(0, 0, 0, int(a * max(0, 1 - x / (W * start)))))
    else:
        for y in range(H): d.line((0, y, W, y), fill=(0, 0, 0, int(a * max(0, (y - H * start) / (H * (1 - start))))))
    im.alpha_composite(g); return im
im = R.space_bg().convert('RGBA').copy(); d = R.draw_earth(im, 1420, 560, 470)
R.faller(d, 1420, 330, 44, 0.4, (255, 170, 110), glow=0.9)
im = grad(im, 'left', 200, 0.6); d = ImageDraw.Draw(im, 'RGBA')
d.rounded_rectangle((70, 70, 600, 140), 35, fill=(0, 0, 0, 200)); ctext(d, (335, 105), '実データでシミュレーション', Fb(38), GOLD)
ctext(d, (70, 300), '地球をつらぬく', Mi(130), PALE, 'lm', 8); ctext(d, (70, 470), '穴に飛びこむと', Mi(130), PALE, 'lm', 8)
ctext(d, (70, 660), '反対側まで何分？', Mi(118), GOLD, 'lm', 8)
ctext(d, (78, 830), 'WHAT IF YOU JUMPED THROUGH THE EARTH?', Fb(38), (235, 235, 240), 'lm', 2)
im.convert('RGB').resize((1280, 720), Image.LANCZOS).save('/home/claude/hole/hole_thumb.jpg', quality=92)
v = R.space_bg(1080, 1920, 7).convert('RGBA').copy(); d = R.draw_earth(v, 540, 980, 470); R.faller(d, 540, 700, 44, 0.4, (255, 170, 110), glow=0.9)
v = grad(v, 'bottom', 220, 0.6); d = ImageDraw.Draw(v, 'RGBA')
ctext(d, (540, 150), '実データでシミュレーション', Fb(48), GOLD, sw=2); ctext(d, (540, 330), '地球をつらぬく穴に', Mi(92), PALE, sw=6)
ctext(d, (540, 1540), '飛びこんだら', Mi(130), PALE, sw=6); ctext(d, (540, 1710), '何分で反対側？', Mi(116), GOLD, sw=8)
ctext(d, (540, 1850), 'WHAT IF YOU JUMPED THROUGH THE EARTH?', Fb(36), (230, 230, 235), sw=2)
v.convert('RGB').save('/home/claude/hole/hole_short_cover.jpg', quality=92)
