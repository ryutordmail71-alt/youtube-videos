import math, sys
sys.path.insert(0, '/home/claude/db'); sys.argv = ['x', 'main']
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import chara
NF = '/usr/share/fonts/opentype/noto/'; FD = '/home/claude/fonts/'
from PIL import ImageFont
def Fo(n, s): return ImageFont.truetype(NF + n, s, index=0)
def Fx(n, s): return ImageFont.truetype(FD + n, s)
BK = 'NotoSansCJK-Black.ttc'

def burst(W, H, cx, cy):
    im = Image.new('RGB', (W, H), (20, 10, 14)); d = ImageDraw.Draw(im)
    for k in range(36):
        a0 = 2 * math.pi * k / 36; a1 = a0 + 2 * math.pi / 72
        col = (150, 30, 30) if k % 2 == 0 else (90, 16, 22)
        R = 3000; d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=col)
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((cx - 420, cy - 420, cx + 420, cy + 420), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(160)); glow = Image.new('RGB', (W, H), (255, 170, 60))
    im = Image.composite(glow, im, g.point(lambda v: int(v * 0.75)))
    # 周辺減光
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).ellipse((-W * 0.2, -H * 0.3, W * 1.2, H * 1.3), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(200)); return Image.composite(im, Image.new('RGB', (W, H), (0, 0, 0)), v)

def spiky(d, cx, cy, w, h, n=26):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n; r = 1.0 if k % 2 == 0 else 0.8
        pts.append((cx + w / 2 * r * math.cos(a), cy + h / 2 * r * math.sin(a)))
    d.polygon(pts, fill=(255, 255, 255), outline=(20, 20, 20))

def stroke_text(d, xy, t, f, fill, sw, anchor='lm', sf=(0, 0, 0)):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=sf)

def main():
    W, H = 1280, 720
    im = burst(W, H, 930, 430).convert('RGBA')
    c = chara.draw(520, mouth=1.0, eyes='squint', sweat=True); im.alpha_composite(c, (930 - c.width // 2, 470 - int(c.height * 0.55)))
    d = ImageDraw.Draw(im)
    spiky(d, 990, 120, 470, 190); stroke_text(d, (990, 120), 'なっとう！！！', Fx('RocknRollOne-Regular.ttf', 66), (220, 30, 30), 2, 'mm', (120, 0, 0))
    d.rounded_rectangle((50, 60, 220, 120), 12, fill=(255, 210, 80)); d.text((135, 90), '検証', font=Fo(BK, 42), fill=(20, 20, 30), anchor='mm')
    stroke_text(d, (54, 225), '声をどんどん', Fo(BK, 84), (245, 240, 230), 8)
    stroke_text(d, (54, 330), '大きくしたら', Fo(BK, 84), (245, 240, 230), 8)
    f = Fx('BebasNeue-Regular.ttf', 300)
    stroke_text(d, (40, 560), '194', f, (255, 230, 90), 12, 'lm', (150, 20, 20))
    stroke_text(d, (40 + f.getlength('194') + 18, 600), 'dB', Fo(BK, 110), (255, 255, 255), 8, 'lm', (150, 20, 20))
    d.text((56, 690), 'What happens as the decibels keep rising?', font=Fo('NotoSansCJK-Bold.ttc', 24), fill=(230, 230, 235), anchor='lm')
    im.convert('RGB').save('/home/claude/db/db_thumb.jpg', quality=92)

def vert():
    W, H = 1080, 1920
    im = burst(W, H, 540, 1180).convert('RGBA')
    c = chara.draw(760, mouth=1.0, eyes='squint', sweat=True); im.alpha_composite(c, (540 - c.width // 2, 1240 - int(c.height * 0.55)))
    d = ImageDraw.Draw(im)
    spiky(d, 560, 760, 720, 260); stroke_text(d, (560, 760), 'なっとう！！！', Fx('RocknRollOne-Regular.ttf', 92), (220, 30, 30), 3, 'mm', (120, 0, 0))
    d.text((540, 150), '検証', font=Fo(BK, 60), fill=(255, 210, 80), anchor='mm')
    stroke_text(d, (540, 270), '声をどんどん', Fo(BK, 120), (245, 240, 230), 9, 'mm')
    stroke_text(d, (540, 420), '大きくしたら？', Fo(BK, 120), (255, 210, 80), 9, 'mm')
    f = Fx('BebasNeue-Regular.ttf', 330); wn = f.getlength('194'); x0 = 540 - (wn + 20 + 170) / 2
    stroke_text(d, (x0, 1700), '194', f, (255, 230, 90), 12, 'lm', (150, 20, 20))
    stroke_text(d, (x0 + wn + 20, 1740), 'dB', Fo(BK, 120), (255, 255, 255), 8, 'lm', (150, 20, 20))
    d.text((540, 1860), 'What happens as the decibels keep rising?', font=Fo('NotoSansCJK-Bold.ttc', 34), fill=(230, 230, 235), anchor='mm')
    im.convert('RGB').save('/home/claude/db/db_short_cover.jpg', quality=92)

main(); vert()
a = Image.open('/home/claude/db/db_thumb.jpg').resize((960, 540)); b = Image.open('/home/claude/db/db_short_cover.jpg').resize((304, 540))
o = Image.new('RGB', (1264, 540)); o.paste(a, (0, 0)); o.paste(b, (960, 0)); o.save('/tmp/claude-0/-home-claude/3f2fb178-41da-56af-8da6-007907094230/scratchpad/dbth.jpg')
