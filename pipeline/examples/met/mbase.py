"""東京に隕石が落ちたら（共通の部品）"""
import json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 30
G = '/home/claude/met'
NOTO = '/usr/share/fonts/opentype/noto/'
_F = {}
def _font(n, s):
    k = (n, s)
    if k not in _F: _F[k] = ImageFont.truetype(NOTO + n, s, index=0)
    return _F[k]
def Fo(s): return _font('NotoSansCJK-Black.ttc', s)
def Fb(s): return _font('NotoSansCJK-Bold.ttc', s)
def Mi(s): return _font('NotoSerifCJK-Black.ttc', s)
PALE = (240, 236, 228); GOLD = (255, 210, 80); RED = (235, 70, 60); BLUE = (120, 180, 255); GRAY = (190, 190, 198); ORANGE = (255, 150, 60)
DISC = '※実データをもとにした、単純化した空想のシミュレーションです（数値は目安・仮定を含みます）'
def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return 1 - (1 - u) ** 3
_BG = {}
def bg(w=W, h=H, tint=(14, 16, 30)):
    k = (w, h, tint)
    if k not in _BG:
        yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx - w / 2) / (w * 0.7)) ** 2 + ((yy - h / 2) / (h * 0.7)) ** 2)
        v = np.clip(1.15 - r * 0.9, 0.25, 1.0)[..., None]
        rng = np.random.default_rng(5); n = rng.normal(0, 3.0, (h, w, 1))
        a = np.clip(np.array(tint, float) * v + n, 0, 255)
        _BG[k] = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
    return _BG[k].copy()
def disc(d, w=W, h=H):
    d.text((w - 24, h - 20), DISC, font=Fb(20 if w > h else 22), fill=(205, 205, 210), anchor='rs')
def caption(d, txt, col=PALE, y=H - 125, w=W, fs=52):
    f_ = Fo(fs); tw = f_.getlength(txt)
    d.rounded_rectangle((w / 2 - tw / 2 - 40, y - 45, w / 2 + tw / 2 + 40, y + 45), 16, fill=(8, 6, 10, 225)); d.text((w / 2, y), txt, font=f_, fill=col, anchor='mm')
def glow(im, x, y, r, col, a=150):
    g_ = Image.new('RGBA', im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(g_)
    dd.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(a),)); g_ = g_.filter(ImageFilter.GaussianBlur(max(1, r * 0.45))); im.alpha_composite(g_)
# ---- 地図（dataofjapan/land の都道府県の形）----
TOKYO = (139.767, 35.681)        # 東京駅
COSL = math.cos(math.radians(35.7)); KM_DEG = 111.0
def km_xy(lo, la):  # 東京駅からの km（東・南が正）
    return (lo - TOKYO[0]) * KM_DEG * COSL, (TOKYO[1] - la) * KM_DEG
_POLY = None
def polys():
    global _POLY
    if _POLY is None:
        d = json.load(open('/home/claude/dl/japan.geojson')); _POLY = []
        for f in d['features']:
            g = f['geometry']; P = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
            for p in P:
                ring = np.array(p[0]); 
                if len(ring) < 4: continue
                x = (ring[:, 0] - TOKYO[0]) * KM_DEG * COSL; y = (TOKYO[1] - ring[:, 1]) * KM_DEG
                _POLY.append(np.stack([x, y], 1))
    return _POLY
_MAP = {}
def map_img(ppk, w=W, h=H, cx=W / 2, cy=H / 2, land=(52, 58, 74), edge=(95, 105, 130)):
    """ppk：1kmあたりのピクセル。東京駅が (cx, cy)"""
    k = (round(ppk, 3), w, h, cx, cy)
    if k not in _MAP:
        if len(_MAP) > 40: _MAP.clear()
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for p in polys():
            q = p * ppk + [cx, cy]
            if q[:, 0].max() < -50 or q[:, 0].min() > w + 50 or q[:, 1].max() < -50 or q[:, 1].min() > h + 50: continue
            if ppk < 3: q = q[::max(1, int(3 / ppk))]
            if len(q) < 3: continue
            d.polygon([tuple(v) for v in q], fill=land, outline=edge)
        _MAP[k] = im
    return _MAP[k]
CITIES = {'東京駅': (139.767, 35.681), '横浜': (139.638, 35.444), 'さいたま': (139.645, 35.861), '千葉': (140.123, 35.605), '宇都宮': (139.883, 36.555),
          '水戸': (140.447, 36.366), '前橋': (139.061, 36.391), '甲府': (138.568, 35.664), '静岡': (138.383, 34.976), '福島': (140.468, 37.750),
          '名古屋': (136.906, 35.181), '新潟': (139.036, 37.916), '仙台': (140.872, 38.268), '大阪': (135.502, 34.694)}
def city(d, name, ppk, cx=W / 2, cy=H / 2, col=PALE, fs=30, dx=12, dy=-10):
    x, y = km_xy(*CITIES[name]); x = cx + x * ppk; y = cy + y * ppk
    d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=col); d.text((x + dx, y + dy), name, font=Fb(fs), fill=col, anchor='lb', stroke_width=3, stroke_fill=(0, 0, 0))
def ring(im, cx, cy, r, col, a_fill=60, a_line=230, width=4):
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (int(a_fill),), outline=col + (int(a_line),), width=width); im.alpha_composite(l)
def rock(d, x, y, r, seed=1, col=(120, 110, 100)):
    rng = np.random.default_rng(seed); n = 14; ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rr = r * (1 + rng.uniform(-0.15, 0.12, n)); pts = [(x + rr[i] * math.cos(ang[i]), y + rr[i] * math.sin(ang[i])) for i in range(n)]
    d.polygon(pts, fill=col); dark = tuple(int(c * 0.65) for c in col)
    for i in range(4):
        a = rng.uniform(0, 6.28); q = rng.uniform(0.2, 0.6) * r; s = rng.uniform(0.12, 0.22) * r
        d.ellipse((x + q * math.cos(a) - s, y + q * math.sin(a) - s, x + q * math.cos(a) + s, y + q * math.sin(a) + s), fill=dark)
def scene(key, dur, draw, cues):
    n = int(dur * FPS); p = writer(f'{G}/c_{key}.mp4')
    for f in range(n):
        im = bg(); d = ImageDraw.Draw(im); draw(im, d, f / FPS); disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, cues
