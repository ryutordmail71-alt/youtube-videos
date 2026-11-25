import sys
sys.path.insert(0, '/home/claude/nfj')
from nbase import *
from PIL import Image, ImageDraw
def grad(im, side, a, start):
    w, h = im.size; g_ = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g_)
    if side == 'left':
        for x in range(w): d.line((x, 0, x, h), fill=(0, 0, 0, int(a * max(0, 1 - x / (w * start)))))
    else:
        for y in range(h): d.line((0, y, w, y), fill=(0, 0, 0, int(a * max(0, (y - h * start) / (h * (1 - start))))))
    im.alpha_composite(g_); return im
def scene_img(w, h, bx, fx, fy, fs, px, py, ps, btop=160):
    im = bg(w, h, (30, 36, 62)); d = ImageDraw.Draw(im); GR = h - 90
    d.rectangle((0, GR, w, h), fill=(52, 58, 76))
    building(d, bx, GR, 32, 150, (GR - btop) / 150, floors=40)
    for k in range(14):
        al = int(160 * (1 - k / 14)); yy = py + k * 40; d.ellipse((px - 6, yy, px + 6, yy + 12), fill=(255, 210, 80, al))
    figure(d, px, py, ps, crouch=0.0, col=FLEA_C)
    d.ellipse((px - 60, py - 175 * ps - 30, px + 60, py + 30), outline=GOLD, width=6)
    flea(d, fx, fy, fs)
    return im, d
im, d = scene_img(1920, 1080, 1500, 1370, 1000, 380, 1350, 330, 0.9)
im = grad(im, 'left', 200, 0.7); d = ImageDraw.Draw(im)
d.rounded_rectangle((70, 70, 600, 140), 35, fill=(0, 0, 0, 200)); ctext(d, (335, 105), '実データでシミュレーション', Fb(38), GOLD)
ctext(d, (70, 320), 'ノミの跳躍力', Mi(170), PALE, 'lm', 8); ctext(d, (70, 540), '人間なら何m？', Mi(170), GOLD, 'lm', 8)
ctext(d, (78, 720), 'WHAT IF HUMANS COULD JUMP LIKE FLEAS?', Fb(40), (235, 235, 240), 'lm', 2)
im.convert('RGB').resize((1280, 720), Image.LANCZOS).save(f'{G}/nfj_thumb.jpg', quality=92)
v, d = scene_img(1080, 1920, 640, 330, 1820, 400, 480, 1040, 0.9, btop=1060); d = ImageDraw.Draw(v)
ctext(d, (540, 150), '実データでシミュレーション', Fb(48), GOLD, sw=2); ctext(d, (540, 330), 'ノミの跳躍力', Mi(140), PALE, sw=7)
ctext(d, (540, 500), '人間が持ったら', Mi(110), PALE, sw=6); ctext(d, (540, 670), '何m跳べる？', Mi(140), GOLD, sw=8)
ctext(d, (540, 780), 'WHAT IF HUMANS COULD JUMP LIKE FLEAS?', Fb(36), (230, 230, 235), sw=2)
v.convert('RGB').save(f'{G}/nfj_short_cover.jpg', quality=92)
