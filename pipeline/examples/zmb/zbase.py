"""渋谷にゾンビが1人現れたら（共通の部品）"""
import json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 30
G = '/home/claude/zmb'
NOTO = '/usr/share/fonts/opentype/noto/'
_F = {}
def _font(n, s):
    k = (n, s)
    if k not in _F: _F[k] = ImageFont.truetype(NOTO + n, s, index=0)
    return _F[k]
def Fo(s): return _font('NotoSansCJK-Black.ttc', s)
def Fb(s): return _font('NotoSansCJK-Bold.ttc', s)
def Mi(s): return _font('NotoSerifCJK-Black.ttc', s)
PALE = (240, 236, 228); GOLD = (255, 210, 80); RED = (235, 70, 60); BLUE = (120, 180, 255); GREEN = (150, 200, 120); GRAY = (190, 190, 198)
ZC = (120, 140, 105); HC = (225, 215, 200)
DISC = '※実データをもとにした、単純化した空想のシミュレーションです（数値は目安・仮定を含みます）'

def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return 1 - (1 - u) ** 3
_BG = {}
def bg(w=W, h=H, tint=(22, 16, 26)):
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

# ---- 人とゾンビ（横向き） ----
def person(d, x, yfoot, L, col=HC, phase=0.0):
    """歩く人（右向き）。L：身長px"""
    sw = math.sin(phase) * 0.35; w = max(2, int(L * 0.075))
    hip = (x, yfoot - L * 0.5); sh = (x + L * 0.02, yfoot - L * 0.82)
    for s in (sw, -sw):
        knee = (hip[0] + L * 0.25 * math.sin(s), hip[1] + L * 0.25 * math.cos(s)); d.line([hip, knee, (knee[0] + L * 0.25 * math.sin(s * 0.5), yfoot)], fill=col, width=w, joint='curve')
    d.line([hip, sh], fill=col, width=int(w * 1.7))
    hd = L * 0.12; d.ellipse((sh[0] - hd / 2, sh[1] - hd * 1.05, sh[0] + hd / 2, sh[1] - hd * 0.05), fill=col)
    for s in (-sw, sw): d.line([sh, (sh[0] + L * 0.28 * math.sin(s), sh[1] + L * 0.28 * math.cos(s))], fill=col, width=max(2, w - 1))
def zombie(d, x, yfoot, L, col=ZC, phase=0.0, eye=(255, 70, 60)):
    """ゾンビ（右向き）：前かがみ、腕を前に出す。グロ表現なし"""
    sw = math.sin(phase) * 0.22; w = max(2, int(L * 0.08)); dark = tuple(int(c * 0.6) for c in col)
    hip = (x, yfoot - L * 0.5); sh = (x + L * 0.1, yfoot - L * 0.8)
    for s, c in ((sw, dark), (-sw, col)):
        knee = (hip[0] + L * 0.25 * math.sin(s) + L * 0.02, hip[1] + L * 0.25 * math.cos(s)); d.line([hip, knee, (knee[0] - L * 0.02, yfoot)], fill=c, width=w, joint='curve')
    d.line([hip, sh], fill=col, width=int(w * 1.8))
    d.line([sh, (sh[0] + L * 0.3, sh[1] + L * 0.02 + L * 0.02 * math.sin(phase * 2))], fill=dark, width=max(2, w - 1))
    d.line([(sh[0] - L * 0.02, sh[1] + L * 0.03), (sh[0] + L * 0.28, sh[1] + L * 0.06 + L * 0.02 * math.cos(phase * 2))], fill=col, width=max(2, w - 1))
    hd = L * 0.13; hx, hy = sh[0] + L * 0.06, sh[1] - hd * 0.45
    d.ellipse((hx - hd / 2, hy - hd / 2, hx + hd / 2, hy + hd / 2), fill=col)
    er = max(1.5, L * 0.014); d.ellipse((hx + hd * 0.18 - er, hy - hd * 0.08 - er, hx + hd * 0.18 + er, hy - hd * 0.08 + er), fill=eye)
    return (hx + hd * 0.18, hy - hd * 0.08)
def glow(im, x, y, r, col, a=150):
    g_ = Image.new('RGBA', im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(g_)
    dd.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,)); g_ = g_.filter(ImageFilter.GaussianBlur(r * 0.45)); im.alpha_composite(g_)

# ---- 地図 ----
from zgrid import NX, NY, LAT1, DLAT, DLON, LON0, ij
_g = np.load(f'{G}/grid.npz'); CODE = _g['code']; POP0 = _g['pop']; KM2 = _g['km2']; LAND = CODE > 0
DENS = POP0 / KM2
SX0, SY0, SW_, SH_ = 96, 0, 275, 300                 # 本土の切り出し（セル）
OX0, OY0, OW_, OH_ = 58, 368, 36, 30                  # 沖縄本島まわり
LIGHT = np.clip((np.log10(DENS + 1) - 0.6) / 3.6, 0, 1) ** 1.3
def cells_rgba(h, z, front=None):
    """h：人間の残り（0〜1）、z：ゾンビの割合（0〜1）。land だけの値の配列"""
    hh = np.ones((NY, NX)); zz = np.zeros((NY, NX)); ff = np.zeros((NY, NX))
    if h is not None: hh[LAND] = h; zz[LAND] = z
    if front is not None: ff[LAND] = front
    base = np.array([42, 46, 60], float); ash = np.array([40, 22, 26], float)
    lit = LIGHT * hh
    zr = np.clip(zz * 5, 0, 0.8)
    dead = np.clip((1 - hh) * 1.0, 0, 1)
    rgb = base[None, None] * (1 - dead[..., None]) + ash[None, None] * dead[..., None]
    rgb = rgb + np.array([255, 205, 120])[None, None] * (lit[..., None] * 0.95)
    rgb = rgb * (1 - zr[..., None]) + np.array([150, 22, 28])[None, None] * zr[..., None]
    rgb = rgb * (1 - ff[..., None]) + np.array([255, 70, 40])[None, None] * ff[..., None]
    a = LAND.astype(float) * 255
    return np.dstack([np.clip(rgb, 0, 255), a]).astype(np.uint8)
def map_layer(h=None, z=None, k=3.2, region='main', arr=None, front=None):
    a = cells_rgba(h, z, front) if arr is None else arr
    x0, y0, w0, h0 = (SX0, SY0, SW_, SH_) if region == 'main' else (OX0, OY0, OW_, OH_)
    sub = Image.fromarray(np.ascontiguousarray(a[y0:y0 + h0, x0:x0 + w0]), 'RGBA')
    return sub.resize((int(w0 * k), int(h0 * k)), Image.BILINEAR)
def lonlat_px(lo, la, ox, oy, k, region='main'):
    x, y = ij(lo, la); x0, y0 = (SX0, SY0) if region == 'main' else (OX0, OY0)
    return ox + (x - x0) * k, oy + (y - y0) * k
SHIBUYA = (139.70, 35.66)
CITIES = {'東京': (139.70, 35.68), '名古屋': (136.90, 35.17), '大阪': (135.50, 34.70), '仙台': (140.87, 38.27), '青森': (140.74, 40.82), '札幌': (141.35, 43.06),
          '福岡': (130.40, 33.59), '鹿児島': (130.56, 31.60), '広島': (132.46, 34.40), '新潟': (139.04, 37.91), '那覇': (127.68, 26.21)}
def okinawa_inset(im, d, x, y, k, h=None, z=None, label=True, arr=None):
    lay = map_layer(h, z, k, 'okinawa', arr=arr); w0, h0 = lay.size
    d.rectangle((x - 6, y - 6, x + w0 + 6, y + h0 + 6), outline=(120, 120, 130), width=2)
    im.alpha_composite(lay, (int(x), int(y)))
    if label: d.text((x + w0 / 2, y + h0 + 14), '沖縄（位置をずらして表示）', font=Fb(20), fill=GRAY, anchor='mt')
def scene(key, dur, draw, cues):
    n = int(dur * FPS); p = writer(f'{G}/c_{key}.mp4')
    for f in range(n):
        im = bg(); d = ImageDraw.Draw(im); draw(im, d, f / FPS); disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, cues
