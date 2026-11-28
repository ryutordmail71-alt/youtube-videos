"""サムネ（上品型）と縦カバー：地下通路の写真（神田駅, Kirin7739, CC BY 4.0）＋開かずの扉の絵"""
import sys
import numpy as np
sys.path.insert(0, '/home/claude/youtube-videos/pipeline/thumbs'); sys.path.insert(0, '/home/claude/tkc')
from thumbkit import *
from thumbkit import _shadow_text
import tdraw as T
G = '/home/claude/tkc'
photo = Image.open(f'{G}/ph/diet2.jpg').convert('RGB')
def under(img, y0, cx, ph=0.0):
    w, h = img.size; yy = np.linspace(0, 1, h)[:, None]
    a = np.clip((yy * h - y0) / 90, 0, 1) * 0.9
    img.paste(Image.new('RGBA', (w, h), (16, 11, 8, 255)), (0, 0), Image.fromarray((np.repeat(a, w, 1) * 255).astype(np.uint8)))
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g); c = (255, 210, 80, 255); k = h / 1080
    T.dashed(gd, [(cx, y0 - 20 * k), (cx, y0 + 110 * k), (cx - 380 * k, y0 + 170 * k), (cx - 900 * k, y0 + 150 * k)], c, int(9 * k))
    T.dashed(gd, [(cx, y0 + 110 * k), (cx + 420 * k, y0 + 190 * k), (cx + 900 * k, y0 + 160 * k)], c, int(9 * k))
    gl = g.filter(ImageFilter.GaussianBlur(12)); img.alpha_composite(gl); img.alpha_composite(gl); img.alpha_composite(g)
bg = Image.new('RGBA', (W, H), (8, 12, 24, 255))
ph = photo.resize((int(photo.width * H * 1.05 / photo.height), int(H * 1.05)), Image.LANCZOS)
m = np.clip(np.linspace(0, 1, ph.width) / 0.3, 0, 1) ** 1.5; m = Image.fromarray((np.repeat(m[None, :], ph.height, 0) * 255).astype(np.uint8))
bg.paste(ph.convert('RGBA'), (W - ph.width + 150, -40), m)
im = grade(bg, 1.2, 0.5, 0.75)
im.alpha_composite(Image.new('RGBA', im.size, (15, 30, 75, 100)))
glow(im, 1330, 260, 280, (255, 220, 150), 35)
under(im, 860, 1330)
im = left_shade(im, 0.95, 0.58); im = vignette(im, 0.5)
x, y1, y2 = 100, 470, 690
d = ImageDraw.Draw(im); ky = y1 - 150 - 40; d.line((x, ky - 12, x + 70, ky - 12), fill=GOLD, width=4)
spaced(d, (x + 92, ky), '都市伝説', SANS(40), GOLD, 8)
_shadow_text(im, (x, y1), '国会議事堂の地下に', MIN(112), WHITE, stroke=2)
_shadow_text(im, (x, y2), '秘密の通路？', MIN(176), GOLD, stroke=2, glowcol=(255, 170, 40))
spaced(ImageDraw.Draw(im), (x + 4, y2 + 95), 'SECRET TUNNELS UNDER TOKYO', SANS(30), (230, 228, 222, 210), 4)
ImageDraw.Draw(im).text((1890, 1050), '点線はうわさのイメージ', font=SANS(26), fill=(220, 220, 225), anchor='rs')
save(im, f'{G}/tkc_thumb.jpg')
v = grade(cover(photo, 1080, 1920, cx=0.5, cy=0.5, zoom=1.0), 1.2, 0.5, 0.75); v.alpha_composite(Image.new('RGBA', v.size, (15, 30, 75, 100)))
under(v, 1260, 540)
yy = np.linspace(0, 1, 1920)[:, None]; a = (np.clip((0.34 - yy) / 0.34, 0, 1) + np.clip((yy - 0.85) / 0.15, 0, 1)) * 0.9
v.paste(Image.new('RGBA', (1080, 1920), (3, 4, 10, 255)), (0, 0), Image.fromarray((np.repeat(a, 1080, 1) * 255).astype(np.uint8)))
d = ImageDraw.Draw(v); d.text((540, 150), '都市伝説', font=SANS(50), fill=GOLD, anchor='mm')
for t, y, s, c in [('国会議事堂の地下に', 310, 96, WHITE), ('秘密の通路？', 470, 130, GOLD), ('地図にない地下道のうわさ', 1700, 70, WHITE)]:
    l = Image.new('RGBA', v.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((540, y + 8), t, font=MIN(s), fill=(0, 0, 0, 210), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, 210))
    v.alpha_composite(l.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(v).text((540, y), t, font=MIN(s), fill=c, anchor='mm', stroke_width=2, stroke_fill=(10, 8, 6))
ImageDraw.Draw(v).text((540, 1830), 'SECRET TUNNELS UNDER TOKYO', font=SANS(30), fill=(230, 228, 222), anchor='mm')
v.convert('RGB').save(f'{G}/tkc_short_cover.jpg', quality=92)
print('thumb done')
