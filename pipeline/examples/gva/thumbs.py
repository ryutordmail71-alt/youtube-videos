import sys
mode = sys.argv[1]
sys.path.insert(0, '/home/claude/gfa'); sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/gvm')
import grender as GR
if mode.endswith('v'): GR.W, GR.H = 1080, 1920
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
MIN = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'; SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def Mi(s): return ImageFont.truetype(MIN, s, index=0)
def Sa(s): return ImageFont.truetype(SANS, s, index=0)
PALE = (245, 240, 230); GOLD = (255, 210, 80)
def st(d, xy, t, f, fill, anchor='mm', sw=0): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def grad(im, start, alpha, side):
    W, H = im.size; g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    if side == 'bottom':
        for y in range(H): d.line((0, y, W, y), fill=(0, 0, 0, int(alpha * max(0, (y - H * start) / (H * (1 - start))))))
    elif side == 'top':
        for y in range(H): d.line((0, y, W, y), fill=(0, 0, 0, int(alpha * max(0, 1 - y / (H * start)))))
    else:
        for x in range(W): d.line((x, 0, x, H), fill=(0, 0, 0, int(alpha * max(0, 1 - x / (W * start)))))
    im.alpha_composite(g); return im
if mode.startswith('a'):
    import arender as A, amodel as AM
    M = AM.Model(2000)
    if mode == 'a':
        im = A.render(M, 13.4, (-34, 22, 12.5), dict(off=True), f=3).convert('RGBA'); im = grad(im, 0.5, 230, 'top')
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((60, 40, 560, 100), 30, fill=(0, 0, 0, 200)); st(d, (310, 70), '実データでシミュレーション', Sa(34), GOLD)
        st(d, (70, 215), '巨人 vs 人間', Mi(150), PALE, 'lm', 7)
        st(d, (70, 380), '何人で勝てる？', Mi(130), GOLD, 'lm', 6)
        st(d, (74, 480), 'A 50-METER GIANT vs A HUMAN ARMY', Sa(30), (235, 235, 240), 'lm', 2)
        im.convert('RGB').resize((1280, 720)).save('/home/claude/gva/gva_thumb.jpg', quality=92)
    else:
        im = A.render(M, 13.4, (-26, 26, 11), dict(off=True), f=3).convert('RGBA'); im = grad(im, 0.4, 220, 'top'); im = grad(im, 0.7, 200, 'bottom')
        d = ImageDraw.Draw(im)
        st(d, (540, 130), '実データでシミュレーション', Sa(44), GOLD, sw=2); st(d, (540, 300), '巨人 vs 人間', Mi(150), PALE, sw=6)
        st(d, (540, 1500), '何人で', Mi(150), PALE, sw=6); st(d, (540, 1680), '勝てる？', Mi(170), GOLD, sw=6)
        st(d, (540, 1840), 'A 50-METER GIANT vs A HUMAN ARMY', Sa(34), (225, 225, 230))
        im.convert('RGB').save('/home/claude/gva/gva_short_cover.jpg', quality=92)
else:
    import frender as R, fmodel as FM
    M = FM.Model(pmax=120)
    if mode == 'f':
        im = R.render(M, 8.2, (-18, 30, 15), dict(off=True), f=3).convert('RGBA'); im = grad(im, 0.62, 200, 'left')
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((60, 60, 560, 120), 30, fill=(0, 0, 0, 200)); st(d, (310, 90), '実データでシミュレーション', Sa(34), GOLD)
        st(d, (70, 290), '巨人は', Mi(150), PALE, 'lm', 7)
        st(d, (70, 480), '立つと気絶？', Mi(150), GOLD, 'lm', 7)
        st(d, (74, 600), 'CAN A 50-METER GIANT STAND UP?', Sa(30), (235, 235, 240), 'lm', 2)
        im.convert('RGB').resize((1280, 720)).save('/home/claude/gfa/gfa_thumb.jpg', quality=92)
    else:
        im = R.render(M, 8.2, (-8, 32, 17), dict(off=True), f=3).convert('RGBA'); im = grad(im, 0.35, 160, 'top')
        d = ImageDraw.Draw(im)
        st(d, (540, 130), '実データでシミュレーション', Sa(44), GOLD, sw=2); st(d, (540, 300), '身長50mの巨人', Mi(120), PALE, sw=6)
        st(d, (540, 1500), '立ち上がると', Mi(130), PALE, sw=6); st(d, (540, 1680), '気絶する？', Mi(170), GOLD, sw=6)
        st(d, (540, 1840), 'CAN A 50-METER GIANT STAND UP?', Sa(34), (225, 225, 230))
        im.convert('RGB').save('/home/claude/gfa/gfa_short_cover.jpg', quality=92)
