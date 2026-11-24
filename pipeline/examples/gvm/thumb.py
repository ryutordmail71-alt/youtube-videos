import sys
sys.path.insert(0, '/home/claude/gvm')
import grender as GR
mode = sys.argv[1]
if mode == 'vert': GR.W, GR.H = 1080, 1920
import gmodel as GM
from PIL import Image, ImageDraw, ImageEnhance
MIN = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'; SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
from PIL import ImageFont
def Mi(s): return ImageFont.truetype(MIN, s, index=0)
def Sa(s): return ImageFont.truetype(SANS, s, index=0)
PALE = (245, 240, 230); GOLD = (255, 210, 80)
def st(d, xy, t, f, fill, anchor='mm', sw=0): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def grad(im, start, alpha, side='bottom'):
    W, H = im.size; g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    if side == 'bottom':
        for y in range(H): d.line((0, y, W, y), fill=(0, 0, 0, int(alpha * max(0, (y - H * start) / (H * (1 - start))))))
    else:
        for x in range(W): d.line((x, 0, x, H), fill=(0, 0, 0, int(alpha * max(0, 1 - x / (W * start)))))
    im.alpha_composite(g); return im
M = GM.Model(2e10)
if mode == 'land':
    im = GR.render(M, 250000, (-19, 31, 22), dict(off=True), f=3).convert('RGBA')
    im = ImageEnhance.Contrast(im.convert('RGB')).enhance(1.1).convert('RGBA'); im = grad(im, 0.62, 225, 'left'); im = grad(im, 0.55, 160)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 90, 560, 150), 30, fill=(0, 0, 0, 200)); st(d, (315, 120), '実データでシミュレーション', Sa(34), GOLD)
    st(d, (80, 300), '巨人', Mi(210), PALE, 'lm', 7)
    st(d, (80, 470), 'vs 蚊200億匹', Mi(120), PALE, 'lm', 6)
    st(d, (80, 640), '巨人は耐えられる？', Mi(96), GOLD, 'lm', 5)
    st(d, (84, 740), 'A 50-METER GIANT vs 20 BILLION MOSQUITOES', Sa(30), (225, 225, 230), 'lm')
    im.convert('RGB').resize((1280, 720)).save('/home/claude/gvm/gvm_thumb.jpg', quality=92)
else:
    im = GR.render(M, 250000, (0, 30, 26), dict(off=True), f=3).convert('RGBA')
    im = grad(im, 0.45, 230); d = ImageDraw.Draw(im)
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(600): gd.line((0, y, 1080, y), fill=(0, 0, 0, int(200 * (1 - y / 600))))
    im.alpha_composite(g); d = ImageDraw.Draw(im)
    st(d, (540, 130), '実データでシミュレーション', Sa(44), GOLD, sw=2)
    st(d, (540, 300), '巨人 vs 蚊', Mi(170), PALE, sw=6)
    st(d, (540, 1450), '何匹いたら', Mi(130), PALE, sw=6)
    st(d, (540, 1610), '危ない？', Mi(160), GOLD, sw=6)
    st(d, (540, 1790), 'A 50-METER GIANT vs MOSQUITOES', Sa(34), (225, 225, 230))
    im.convert('RGB').save('/home/claude/gvm/gvm_short_cover.jpg', quality=92)
