"""日本中で同時にトイレを流したら の描画部品"""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 30
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'; NOTOB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'; BEBAS = '/home/claude/fonts/BebasNeue-Regular.ttf'
_F = {}
def font(p, s):
    k = (p, s)
    if k not in _F: _F[k] = ImageFont.truetype(p, s, index=0) if p.endswith('.ttc') else ImageFont.truetype(p, s)
    return _F[k]
def Fo(s): return font(NOTO, s)
def Fb(s): return font(NOTOB, s)
def Mi(s): return font(SERIF, s)
def BE(s): return font(BEBAS, s)
PALE = (240, 240, 245); GOLD = (255, 210, 80); RED = (255, 95, 95); GREEN = (150, 220, 120); GREY = (200, 200, 208); BLUE = (120, 190, 255); CYAN = (120, 225, 240); ORANGE = (255, 150, 60)
WATER = (70, 150, 235); WATER2 = (130, 200, 255)
NOTE = '※実データをもとにした、単純化した空想のシミュレーションです'
def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return u * u * (3 - 2 * u)
_BG = {}
def night_bg(w=W, h=H, seed=4, grid=True):
    """深い青のグラデーション＋うすい方眼（設計図っぽさ）"""
    k = (w, h, seed, grid)
    if k in _BG: return _BG[k]
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx - w * 0.6) / w) ** 2 + ((yy - h * 0.35) / h) ** 2)
    t = np.clip(r / 0.9, 0, 1)[..., None]; c = np.array((18, 36, 66), float) * (1 - t) + np.array((4, 7, 16), float) * t
    im = Image.fromarray(c.astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
    if grid:
        for x in range(0, w, 60): d.line((x, 0, x, h), fill=(120, 170, 255, 14), width=1)
        for y in range(0, h, 60): d.line((0, y, w, y), fill=(120, 170, 255, 14), width=1)
    _BG[k] = im; return im
def foot(d, s, w=W, h=H, size=20): d.text((w - 24, h - 38), s, font=Fb(size), fill=(200, 200, 205), anchor='rs')
def note(d, w=W, h=H, size=18): d.text((w - 24, h - 8), NOTE, font=Fb(size), fill=(220, 220, 225), anchor='rs')
def rowbox(d, y, lab, val, col, x0=W / 2 - 600, x1=W / 2 + 600, hl=False, lf=40, vf=60, h=55):
    d.rounded_rectangle((x0, y - h, x1, y + h), 18, fill=(10, 14, 24, 230), outline=GOLD if hl else None, width=4 if hl else 0)
    d.text((x0 + 36, y), lab, font=Fo(lf), fill=PALE, anchor='lm'); d.text((x1 - 36, y), val, font=Fo(vf), fill=col, anchor='rm')
# ---- トイレの絵（横から見たシルエット）----
def toilet(d, x, y, s, col=(235, 238, 245), fill=None, tank=None):
    """x：中心、y：床、s：高さ(px)。tank：タンクの水の量 0〜1（None なら描かない）"""
    lw = max(2, int(s * 0.035))
    tx0, tx1, ty0, ty1 = x + s * 0.05, x + s * 0.42, y - s, y - s * 0.55       # タンク
    d.rounded_rectangle((tx0, ty0, tx1, ty1), max(2, int(s * 0.05)), fill=fill, outline=col, width=lw)
    if tank is not None:
        lev = ty1 - lw - (ty1 - ty0 - 2 * lw) * max(0, min(1, tank))
        if tank > 0.01: d.rectangle((tx0 + lw, lev, tx1 - lw, ty1 - lw), fill=WATER)
    d.line((tx0 + s * 0.08, ty0 + s * 0.08, tx0 + s * 0.18, ty0 + s * 0.08), fill=col, width=lw)            # レバー
    d.rounded_rectangle((x - s * 0.42, y - s * 0.55, x + s * 0.12, y - s * 0.43), max(2, int(s * 0.03)), fill=fill, outline=col, width=lw)  # 便座
    d.chord((x - s * 0.40, y - s * 0.72, x + s * 0.10, y - s * 0.20), 0, 180, fill=fill, outline=col, width=lw)  # 便器
    d.polygon([(x - s * 0.22, y - s * 0.30), (x - s * 0.02, y - s * 0.30), (x + s * 0.02, y), (x - s * 0.26, y)], fill=fill, outline=col)
    d.line((x - s * 0.26, y, x + s * 0.02, y), fill=col, width=lw)
def house(d, x, y, w, h, col=(200, 210, 230), win=(255, 220, 140)):
    d.polygon([(x - w * 0.55, y - h * 0.62), (x, y - h), (x + w * 0.55, y - h * 0.62)], fill=(60, 70, 95), outline=col)
    d.rectangle((x - w / 2, y - h * 0.62, x + w / 2, y), fill=(45, 55, 78), outline=col, width=2)
    d.rectangle((x - w * 0.3, y - h * 0.5, x - w * 0.05, y - h * 0.28), fill=win); d.rectangle((x + w * 0.05, y - h * 0.5, x + w * 0.3, y - h * 0.28), fill=win)
def building(d, x0, y, w, h, col=(200, 210, 230), win=(255, 220, 140), seed=1):
    d.rectangle((x0, y - h, x0 + w, y), fill=(40, 50, 72), outline=col, width=2); rng = np.random.default_rng(seed)
    for yy in np.arange(y - h + 14, y - 16, 26):
        for xx in np.arange(x0 + 10, x0 + w - 16, 24):
            if rng.random() < 0.7: d.rectangle((xx, yy, xx + 12, yy + 12), fill=win)
# ---- 管の断面（水がどこまで入っているか）----
def seg_h(frac):
    """円の面積の frac を満たす水の高さ（半径1あたり 0〜2）"""
    lo, hi = 0.0, 2.0
    for _ in range(30):
        m = (lo + hi) / 2; th = 2 * math.acos(1 - m); a = (th - math.sin(th)) / (2 * math.pi)
        lo, hi = (m, hi) if a < frac else (lo, m)
    return lo
def pipe_section(im, cx, cy, r, frac, col=WATER):
    d = ImageDraw.Draw(im, 'RGBA'); d.ellipse((cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18), fill=(110, 105, 100))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(18, 20, 28))
    hgt = seg_h(max(0.0, min(1.0, frac))) * r
    if hgt > 0.5:
        m = Image.new('L', im.size, 0); md = ImageDraw.Draw(m); md.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
        md.rectangle((0, 0, im.width, cy + r - hgt), fill=0); layer = Image.new('RGBA', im.size, col + (255,)); im.paste(layer, (0, 0), m)
        d = ImageDraw.Draw(im, 'RGBA'); yl = cy + r - hgt; hw = math.sqrt(max(0, r * r - (yl - cy) ** 2)); d.line((cx - hw, yl, cx + hw, yl), fill=WATER2, width=3)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(170, 165, 160), width=4); return d
# ---- 東京ドームの形（横から）----
def dome(d, cx, yb, w, h, fill_frac=0.0, col=(220, 225, 235)):
    pts = [(cx - w / 2 + w * i / 60, yb - h * math.sqrt(max(0, 1 - ((i / 60) * 2 - 1) ** 2)) ** 0.9) for i in range(61)]
    if fill_frac > 0:
        yl = yb - h * fill_frac; poly = [(x, max(y, yl)) for x, y in pts]; d.polygon(poly + [(cx + w / 2, yb), (cx - w / 2, yb)], fill=WATER + (230,))
    d.line(pts, fill=col, width=5); d.line((cx - w / 2 - 20, yb, cx + w / 2 + 20, yb), fill=col, width=5)
def glow(im, x, y, r, col, a=200):
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g); d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(a),))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.5))); return im
def swirl(d, cx, cy, r, t, col=WATER2, n=5):
    """渦（流れる水）"""
    for k in range(n):
        ph = t * 4 + k * 2 * math.pi / n; pts = []
        for i in range(40):
            u = i / 39; rr = r * (1 - 0.85 * u); a = ph + u * 4.5
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.45))
        d.line(pts, fill=col, width=max(2, int(r * 0.05)))
