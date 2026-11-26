from PIL import Image, ImageDraw
import hrender as R, jscenes as S
from hrender import Fo, Fb, Mi, PALE, GOLD, ctext
def grad(im, side, a, start):
    W, H = im.size; g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    if side == 'left':
        for x in range(W): d.line((x, 0, x, H), fill=(0, 0, 0, int(a * max(0, 1 - x / (W * start)))))
    else:
        for y in range(H): d.line((0, y, W, y), fill=(0, 0, 0, int(a * max(0, (y - H * start) / (H * (1 - start))))))
    im.alpha_composite(g); return im
im = R.space_bg().convert('RGBA').copy(); S.draw_globe(im, 1480, 760, 470); d = ImageDraw.Draw(im, 'RGBA'); S.ring_people(d, 1480, 760, 470, 0.45, 24, 70)
im = grad(im, 'left', 210, 0.6); d = ImageDraw.Draw(im, 'RGBA')
d.rounded_rectangle((70, 70, 600, 140), 35, fill=(0, 0, 0, 200)); ctext(d, (335, 105), '実データでシミュレーション', Fb(38), GOLD)
ctext(d, (70, 300), '82億人が同時に', Mi(126), PALE, 'lm', 8); ctext(d, (70, 470), 'ジャンプしたら', Mi(126), PALE, 'lm', 8)
ctext(d, (70, 660), '地震は起きる？', Mi(130), GOLD, 'lm', 8)
ctext(d, (78, 830), 'WHAT IF EVERYONE ON EARTH JUMPED AT ONCE?', Fb(38), (235, 235, 240), 'lm', 2)
im.convert('RGB').resize((1280, 720), Image.LANCZOS).save('/home/claude/jmp/jmp_thumb.jpg', quality=92)
v = R.space_bg(1080, 1920, 7).convert('RGBA').copy(); S.draw_globe(v, 540, 1000, 440); d = ImageDraw.Draw(v, 'RGBA'); S.ring_people(d, 540, 1000, 440, 0.45, 24, 66)
v = grad(v, 'bottom', 220, 0.6); d = ImageDraw.Draw(v, 'RGBA')
ctext(d, (540, 150), '実データでシミュレーション', Fb(48), GOLD, sw=2); ctext(d, (540, 330), '82億人が同時に', Mi(100), PALE, sw=6)
ctext(d, (540, 1540), 'ジャンプしたら', Mi(124), PALE, sw=6); ctext(d, (540, 1710), '地震は起きる？', Mi(124), GOLD, sw=8)
ctext(d, (540, 1850), 'WHAT IF EVERYONE ON EARTH JUMPED AT ONCE?', Fb(34), (230, 230, 235), sw=2)
v.convert('RGB').save('/home/claude/jmp/jmp_short_cover.jpg', quality=92)
