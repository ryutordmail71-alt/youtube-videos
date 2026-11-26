import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
NA = '/home/claude/thumbs/nasa/'
def streak(im, x, y, ang, L, r):
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    for k in range(60):
        q = k / 60; xx = x + math.cos(ang) * L * q; yy = y - math.sin(ang) * L * q
        rr = r * (1 - q) ** 1.2 + 1; c = (255, int(240 - 150 * q), int(200 - 180 * q), int(255 * (1 - q) ** 1.5))
        d.ellipse((xx - rr, yy - rr, xx + rr, yy + rr), fill=c)
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(3))); im.alpha_composite(l)
    glow(im, x, y, r * 6, (255, 170, 60), 230); glow(im, x, y, r * 2.2, (255, 250, 230), 255)
# 1) 隕石：東京の夜景（ISS）＋火の玉
im = grade(cover(Image.open(NA + 'iss036e030793.jpg'), cx=0.5, cy=0.52, zoom=1.15), 1.2, 1.1)
glow(im, 1300, 640, 320, (255, 90, 30), 140)
streak(im, 1300, 600, math.radians(35), 950, 30)
im = left_shade(im, 0.93, 0.6); im = vignette(im)
headline(im, '東京に隕石', '1kmなら？', english='What if an asteroid hit Tokyo?')
save(im, 'out/met_thumb.jpg')
# 2) ゾンビ：日本の夜景（ISS）＋東京から赤い広がり
import thumbkit as TK
src = Image.open(NA + 'iss040e081462.jpg')
im = grade(cover(src, cx=0.47, cy=0.64, zoom=1.2), 1.25, 0.95, 1.35)
tx, ty = TK.MAP(1230, 1040)
red = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for (px, py, r, a) in [(1230, 1040, 260, 150), (1180, 900, 220, 120), (1150, 760, 180, 90), (1000, 980, 200, 90), (1230, 1040, 110, 200)]:
    x, y = TK.MAP(px, py); glow(red, x, y, r, (230, 25, 20), a)
im.alpha_composite(red)
glow(im, tx, ty, 26, (255, 200, 190), 255)
im = left_shade(im, 0.92, 0.55); im = vignette(im, 0.6)
headline(im, '渋谷にゾンビ1人', '日本は何日で全滅？', s2=140, english='One zombie in Shibuya. How long would Japan last?')
save(im, 'out/zmb_thumb.jpg')
# 3) 地球をつらぬく穴：地球（NASA）＋切り口の核
src = Image.open(NA + 'GSFC_20171208_Archive_e001386.jpg').convert('RGBA')
im = Image.new('RGBA', (W, H), (3, 4, 10, 255))
rng = np.random.default_rng(3); d = ImageDraw.Draw(im)
for _ in range(500):
    x, y = rng.uniform(0, W), rng.uniform(0, H); b = int(rng.uniform(80, 230)); d.point((x, y), fill=(b, b, b))
R = 430; cx, cy = 1520, 560
e = src.resize((int(src.width * 2 * R / 1460), int(src.height * 2 * R / 1460)), Image.LANCZOS)
im.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))
# 手前側をくさび形に切って、中の層を見せる
cut = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(cut)
layers = [(1.0, (150, 60, 25)), (0.86, (190, 80, 30)), (0.55, (240, 140, 40)), (0.30, (255, 220, 120)), (0.16, (255, 250, 220))]
for f, col in layers: dc.pieslice((cx - R * f, cy - R * f, cx + R * f, cy + R * f), 200, 290, fill=col + (255,))
im.alpha_composite(cut); glow(im, cx, cy, 160, (255, 200, 90), 160)
# 中心をつらぬく線（穴）と落ちる人の光
ImageDraw.Draw(im).line((cx, cy - R * 0.98, cx, cy + R * 0.98), fill=(15, 10, 8), width=12)
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).pieslice((cx - R, cy - R, cx + R, cy + R), 200, 245, fill=(0, 0, 0, 90)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
glow(im, cx, cy - R * 0.55, 26, (180, 230, 255), 255)
im = left_shade(im, 0.8, 0.45); im = vignette(im, 0.5)
headline(im, '地球をつらぬく穴', '反対側まで何分？', s1=120, s2=130, max_w=900, english='What if you jumped through the Earth?')
save(im, 'out/hole_thumb.jpg')
# 4) 82億人ジャンプ：地球の縁（ISS）＋人のシルエット＋地震の波
src = Image.open(NA + 'iss040e080833.jpg')
im = grade(cover(src, cx=0.5, cy=0.45, zoom=1.05), 1.15, 1.1, 1.0)
d = ImageDraw.Draw(im); rng = np.random.default_rng(7)
# 地平線（縁）に沿って人を並べる：y ≈ 660 付近の弧
def person(d, x, y, h, up):
    hd = h * 0.16; d.ellipse((x - hd, y - h, x + hd, y - h + 2 * hd), fill=(8, 8, 12))
    d.line((x, y - h + 2 * hd, x, y - h * 0.45), fill=(8, 8, 12), width=max(3, int(h * 0.12)))
    a = h * 0.32 if up else h * 0.22
    d.line((x, y - h * 0.75, x - h * 0.25, y - h * 0.75 - a), fill=(8, 8, 12), width=max(2, int(h * 0.08)))
    d.line((x, y - h * 0.75, x + h * 0.25, y - h * 0.75 - a), fill=(8, 8, 12), width=max(2, int(h * 0.08)))
    d.line((x, y - h * 0.45, x - h * 0.15, y), fill=(8, 8, 12), width=max(2, int(h * 0.09))); d.line((x, y - h * 0.45, x + h * 0.15, y), fill=(8, 8, 12), width=max(2, int(h * 0.09)))
for k, r in enumerate([120, 230, 350, 480]):
    ring = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((1300 - r * 2.2, 760 - r * 0.5, 1300 + r * 2.2, 760 + r * 0.5), outline=(255, 210, 80, 220 - k * 45), width=6)
    im.alpha_composite(ring.filter(ImageFilter.GaussianBlur(6))); im.alpha_composite(ring.filter(ImageFilter.GaussianBlur(1.2)))
im = left_shade(im, 0.85, 0.55); im = vignette(im, 0.5)
headline(im, '82億人が同時に跳ぶと', '地震は起きる？', y1=360, y2=560, s1=110, s2=150, max_w=950, english='What if everyone on Earth jumped at once?')
save(im, 'out/jmp_thumb.jpg')
# 5) エラ：深い水の中＋人のシルエット＋光るエラ
yy, xx = np.mgrid[0:H, 0:W]
top = np.array([30, 110, 130], np.float32); bot = np.array([2, 10, 22], np.float32)
t = (yy / H)[..., None] ** 0.8; base = top * (1 - t) + bot * t
im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
rays = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(rays); rng = np.random.default_rng(4)
for _ in range(9):
    x0 = rng.uniform(700, 1900); w0 = rng.uniform(40, 120); sk = rng.uniform(-260, -120)
    dr.polygon([(x0, -10), (x0 + w0, -10), (x0 + w0 + sk + w0 * 2, H), (x0 + sk, H)], fill=(170, 235, 240, int(rng.uniform(25, 55))))
im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(25)))
# 大きく光るエラ（3本のすじ）
cx, cy = 1460, 560
for k in range(3):
    x = cx - 110 + k * 110; l = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(l).arc((x - 120, cy - 260, x + 120, cy + 260), 290, 70, fill=(255, 210, 80, 255), width=16)
    for _ in range(3): im.alpha_composite(l.filter(ImageFilter.GaussianBlur(26)))
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(8))); im.alpha_composite(l)
db = ImageDraw.Draw(im)
for _ in range(70):
    x, y, r = rng.normal(1500, 160), rng.uniform(0, cy - 120), rng.uniform(3, 14)
    db.ellipse((x - r, y - r, x + r, y + r), outline=(200, 240, 245, int(rng.uniform(60, 150))), width=2)
im = left_shade(im, 0.7, 0.5); im = vignette(im, 0.6)
headline(im, 'エラがあれば', '水中で暮らせる？', english='What if humans had gills?')
save(im, 'out/era_thumb.jpg')
print('ok')
