"""高級感のあるサムネの共通部品（1920×1080 で描いて 1280×720 に縮小）"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1920, 1080
GOLD = (255, 210, 80); WHITE = (250, 248, 242)
N = '/usr/share/fonts/opentype/noto/'
def F(name, s): return ImageFont.truetype(N + name, s, index=0)
MIN = lambda s: F('NotoSerifCJK-Black.ttc', s)
SANS = lambda s: F('NotoSansCJK-Bold.ttc', s)
def cover(img, w=W, h=H, cx=0.5, cy=0.5, zoom=1.0):
    """写真を画面いっぱいに（cx,cy＝写真のどこを中心にするか 0〜1）"""
    s = max(w / img.width, h / img.height) * zoom
    im = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    x = int(min(max(0, im.width * cx - w / 2), im.width - w)); y = int(min(max(0, im.height * cy - h / 2), im.height - h))
    global MAP
    MAP = lambda px, py: (px * s - x, py * s - y)
    return im.crop((x, y, x + w, y + h)).convert('RGBA')
def grade(im, contrast=1.15, sat=1.05, bright=1.0):
    rgb = im.convert('RGB'); rgb = ImageEnhance.Contrast(rgb).enhance(contrast); rgb = ImageEnhance.Color(rgb).enhance(sat); rgb = ImageEnhance.Brightness(rgb).enhance(bright)
    return rgb.convert('RGBA')
def left_shade(im, strength=0.88, end=0.62):
    a = np.zeros((H, W), np.float32); x = np.arange(W) / W
    a[:] = np.clip(1 - x / end, 0, 1) ** 1.6 * strength
    sh = Image.fromarray((a * 255).astype(np.uint8)); blk = Image.new('RGBA', (W, H), (4, 5, 10, 255)); im.paste(blk, (0, 0), sh); return im
def vignette(im, k=0.55):
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = np.clip((r - 0.75) / 0.7, 0, 1) * k; sh = Image.fromarray((a * 255).astype(np.uint8)); im.paste(Image.new('RGBA', (W, H), (0, 0, 0, 255)), (0, 0), sh); return im
def glow(im, x, y, r, col, a=200):
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g); d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(a),))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.5))); return im
def _shadow_text(im, xy, t, f, fill, blur=14, off=(0, 6), sa=200, stroke=0, glowcol=None):
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    d.text((xy[0] + off[0], xy[1] + off[1]), t, font=f, fill=(0, 0, 0, sa), anchor='ls', stroke_width=stroke + 4, stroke_fill=(0, 0, 0, sa))
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(blur)))
    if glowcol:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text(xy, t, font=f, fill=glowcol + (150,), anchor='ls')
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(22)))
    ImageDraw.Draw(im).text(xy, t, font=f, fill=fill, anchor='ls', stroke_width=stroke, stroke_fill=(10, 8, 6))
def spaced(d, xy, t, f, fill, sp=6):
    x, y = xy
    for ch in t: d.text((x, y), ch, font=f, fill=fill, anchor='ls'); x += f.getlength(ch) + sp
    return x
def headline(im, line1, line2, x=110, y1=430, y2=640, s1=150, s2=170, max_w=1080, english=''):
    """上：小さな肩書き／1行目：白／2行目：金（いちばん大事な言葉）"""
    def fit(t, s):
        while MIN(s).getlength(t) > max_w and s > 70: s -= 4
        return s
    s1 = fit(line1, s1); s2 = fit(line2, s2)
    d = ImageDraw.Draw(im)
    ky = y1 - s1 - 40; d.line((x, ky - 12, x + 70, ky - 12), fill=GOLD, width=4)
    spaced(d, (x + 92, ky), '実データでシミュレーション', SANS(36), GOLD, 5)
    _shadow_text(im, (x, y1), line1, MIN(s1), WHITE, stroke=2)
    _shadow_text(im, (x, y2), line2, MIN(s2), GOLD, stroke=2, glowcol=(255, 170, 40))
    if english: spaced(ImageDraw.Draw(im), (x + 4, y2 + 80), english.upper(), SANS(28), (230, 228, 222, 210), 4)
    return im
def grain(im, amt=5):
    n = np.random.default_rng(1).normal(0, amt, (H, W, 1)); a = np.asarray(im.convert('RGB')).astype(np.float32) + n
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
def save(im, path):
    grain(im).resize((1280, 720), Image.LANCZOS).save(path, quality=93)
