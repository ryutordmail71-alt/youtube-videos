"""地球の中心まで穴を掘って飛び込んだら の描画部品"""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import hmodel as HM
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
PALE = (240, 240, 245); GOLD = (255, 210, 80); RED = (255, 95, 95); GREEN = (150, 220, 120); GREY = (200, 200, 208); BLUE = (120, 190, 255); CYAN = (120, 225, 240)
NOTE = '※実データをもとにした、単純化した空想のシミュレーションです'
def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return u * u * (3 - 2 * u)
def mix(a, b, u): u = fade(u); return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
def mmss(m): s = int(round(m * 60)); return f'{s // 60}:{s % 60:02d}'
ORANGE = (255, 150, 60)
def kmh(v): return v * 3.6
# ---- 宇宙の背景 ----
_BG = {}
def space_bg(w=W, h=H, seed=4):
    k = (w, h, seed)
    if k in _BG: return _BG[k]
    a = np.linspace(0, 1, h)[:, None, None]; c = np.array((14, 16, 32))[None, None] * (1 - a) + np.array((4, 4, 10))[None, None] * a
    im = Image.fromarray(np.repeat(c, w, 1).astype(np.uint8)); d = ImageDraw.Draw(im); rng = np.random.default_rng(seed)
    for _ in range(int(w * h / 3000)):
        x, y = rng.uniform(0, w), rng.uniform(0, h); b = int(rng.uniform(80, 255)); r = rng.choice([0.6, 1, 1.5])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, min(255, b + 20)))
    _BG[k] = im; return im
LAYERS = [(6371, (120, 96, 76), '地殻'), (6346, (175, 70, 45), 'マントル'), (3480, (245, 150, 50), '外核（液体の鉄）'), (1221, (255, 235, 160), '内核（固体の鉄）')]
_EARTH = {}
def earth_img(rad, uniform=False):
    k = (rad, uniform)
    if k in _EARTH: return _EARTH[k]
    s = 2 * rad + 8; yy, xx = np.mgrid[0:s, 0:s]; r = np.hypot(xx - s / 2, yy - s / 2) / rad * 6371
    img = np.zeros((s, s, 4), np.float32)
    if uniform:
        col = np.array((150, 110, 85), np.float32); sh = 0.85 + 0.15 * (1 - r / 6371)
        img[..., :3] = col * sh[..., None]; img[..., 3] = (r <= 6371) * 255
    else:
        for i, (rr, col, _) in enumerate(LAYERS):
            inner = LAYERS[i + 1][0] if i + 1 < len(LAYERS) else 0
            m = (r <= rr) & (r > inner); q = (r - inner) / max(1, rr - inner)
            c2 = np.array(col, np.float32) * (1.08 - 0.18 * q[..., None])
            img[m, :3] = np.clip(c2[m], 0, 255); img[m, 3] = 255
        if True:   # マントルの中の濃さの変化
            m = (r > 3480) & (r <= 6346); img[m, :3] *= (0.85 + 0.25 * ((r[m] - 3480) / 2866))[:, None] ** 0.5
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im); c = s / 2; d.ellipse((c - rad, c - rad, c + rad, c + rad), outline=(90, 160, 230), width=4)
    _EARTH[k] = im; return im
def draw_earth(im, cx, cy, rad, uniform=False, tunnel=True, labels=False):
    e = earth_img(rad, uniform); im.paste(e, (int(cx - e.width / 2), int(cy - e.height / 2)), e)
    d = ImageDraw.Draw(im, 'RGBA')
    if tunnel:
        d.rectangle((cx - 7, cy - rad - 4, cx + 7, cy + rad + 4), fill=(8, 8, 14)); d.line((cx - 8, cy - rad, cx - 8, cy + rad), fill=(200, 200, 210, 160), width=2); d.line((cx + 8, cy - rad, cx + 8, cy + rad), fill=(200, 200, 210, 160), width=2)
    if labels and not uniform:
        for rr, col, lab in LAYERS[1:]:
            y = cy - rr / 6371 * rad * 0.72 - (0 if rr > 2000 else 0); x = cx + rr / 6371 * rad * 0.69
            d.text((x + 20, y), lab, font=Fb(max(18, int(rad * 0.06))), fill=PALE, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
    return d
def faller(d, x, y, s, t, col=(240, 240, 245), glow=0.0, spin=True):
    """宇宙服の人（上から見て落ちていく、頭が下）"""
    if glow > 0: d.ellipse((x - s * 1.4, y - s * 1.4, x + s * 1.4, y + s * 1.4), fill=(255, 220, 120, int(90 * glow)))
    a = math.sin(t * 3) * 0.3 if spin else 0
    for side in (-1, 1):
        d.line((x, y - s * 0.1, x + side * s * 0.75, y - s * 0.45 + side * a * s * 0.2), fill=col, width=max(3, int(s * 0.28)))   # 腕
        d.line((x + side * s * 0.15, y - s * 0.5, x + side * s * 0.45, y - s * 1.05), fill=col, width=max(3, int(s * 0.3)))   # 脚
    d.rounded_rectangle((x - s * 0.33, y - s * 0.6, x + s * 0.33, y + s * 0.2), int(s * 0.2), fill=col)
    d.ellipse((x - s * 0.36, y + s * 0.05, x + s * 0.36, y + s * 0.75), fill=col); d.ellipse((x - s * 0.24, y + s * 0.22, x + s * 0.24, y + s * 0.62), fill=(60, 130, 200))
def bar(d, x0, y, x1, frac, col, h=26, back=(255, 255, 255, 40)):
    d.rounded_rectangle((x0, y - h / 2, x1, y + h / 2), int(h / 2), fill=back)
    if frac > 0.005: d.rounded_rectangle((x0, y - h / 2, x0 + max(h, (x1 - x0) * fade(frac)), y + h / 2), int(h / 2), fill=col)
def hms(m):
    s = int(round(m * 60))
    if s >= 3600: return f'{s // 3600}時間{(s % 3600) // 60:02d}分'
    return f'{s // 60}:{s % 60:02d}'
