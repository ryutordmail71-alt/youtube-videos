"""Small HDR scene toolkit for cinematic vertical thumbnails (1080x1920)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, map_coordinates, zoom

W, H = 1080, 1920
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

# ---------------- noise ----------------
_tiles = {}
def tile(seed, n=1024, octaves=7, base=4, pers=0.52):
    key = (seed, n, octaves, base, pers)
    if key in _tiles: return _tiles[key]
    g = np.random.default_rng(seed)
    acc = np.zeros((n, n), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        k = base * 2 ** o
        if k > n: break
        r = g.random((k, k)).astype(np.float32)
        acc += amp * zoom(r, n / k, order=3, mode='grid-wrap')[:n, :n]
        tot += amp; amp *= pers
    acc /= tot
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    _tiles[key] = acc
    return acc

def sample(T, x, y):
    n = T.shape[0]
    return map_coordinates(T, [np.mod(y, n), np.mod(x, n)], order=1, mode='grid-wrap')

def fbm(seed, sx=1.0, sy=1.0, ox=0, oy=0, warp=0.0, wseed=None, **kw):
    T = tile(seed, **kw)
    x = XX * sx + ox; y = YY * sy + oy
    if warp:
        Tw = tile(wseed if wseed is not None else seed + 99, **kw)
        x = x + (sample(Tw, XX * sx * 0.5, YY * sy * 0.5) - 0.5) * warp
        y = y + (sample(Tw, XX * sx * 0.5 + 333, YY * sy * 0.5 + 777) - 0.5) * warp
    return sample(T, x, y)

def ridge(v, p=2.0): return (1 - np.abs(2 * v - 1)) ** p

# ---------------- helpers ----------------
def C(*rgb): return np.array(rgb, np.float32)
def lin(rgb255): return (np.array(rgb255, np.float32) / 255) ** 2.2
def blend(base, col, a):
    a = np.clip(a, 0, 1)[..., None]; return base * (1 - a) + col * a
def gauss(x, y, sx, sy=None):
    sy = sy or sx; return np.exp(-(((XX - x) / sx) ** 2 + ((YY - y) / sy) ** 2))
def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def sky(top, mid, hor, horizon):
    t = np.clip(YY / horizon, 0, 1)[..., None]
    a = np.clip(t * 2, 0, 1); b = np.clip(t * 2 - 1, 0, 1)
    return top * (1 - a) + mid * a * (1 - b) + hor * b

def ground_coords(horizon, cx=540, height=1.0):
    """perspective world coords for pixels below horizon"""
    dy = np.clip(YY - horizon, 1, None)
    z = 900.0 * height / dy               # depth
    wx = (XX - cx) * z / 900.0
    return wx, z

def blackbody(T):
    """T 0..1+ -> HDR colour (linear)"""
    stops = [(0.0, (0, 0, 0)), (0.15, (0.25, 0.02, 0.0)), (0.35, (1.0, 0.18, 0.02)), (0.55, (2.4, 0.75, 0.12)),
             (0.75, (4.0, 2.2, 0.6)), (0.9, (6.0, 4.8, 2.6)), (1.0, (8.0, 7.5, 6.5))]
    xs = [s[0] for s in stops]
    T = np.clip(T, 0, 1)
    return np.stack([np.interp(T, xs, [s[1][i] for s in stops]) for i in range(3)], -1).astype(np.float32)

def ramp(T, stops):
    xs = [s[0] for s in stops]; T = np.clip(T, 0, 1)
    return np.stack([np.interp(T, xs, [s[1][i] for s in stops]) for i in range(3)], -1).astype(np.float32)

# ---------------- drawing into HDR ----------------
def lines_layer(segs, width=2, ss_=2, blur=0.0):
    """segs: list of (x0,y0,x1,y1,intensity,width_mult). returns float mask HxW"""
    im = Image.new('F', (W * ss_, H * ss_), 0.0); d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1, a, wm) in segs:
        d.line((x0 * ss_, y0 * ss_, x1 * ss_, y1 * ss_), fill=float(a), width=max(1, int(width * wm * ss_)))
    arr = np.asarray(im, np.float32).reshape(H, ss_, W, ss_).mean((1, 3))
    if blur: arr = gaussian_filter(arr, blur)
    return arr

def dots_layer(pts, ss_=2):
    im = Image.new('F', (W * ss_, H * ss_), 0.0); d = ImageDraw.Draw(im)
    for (x, y, r, a) in pts:
        d.ellipse(((x - r) * ss_, (y - r) * ss_, (x + r) * ss_, (y + r) * ss_), fill=float(a))
    return np.asarray(im, np.float32).reshape(H, ss_, W, ss_).mean((1, 3))

def streak_field(n, seed, area, length, angle_deg, thick=(1, 2.5), inten=(0.2, 1.0), jitter=8):
    g = random.Random(seed); segs = []
    a = math.radians(angle_deg)
    for _ in range(n):
        x, y = g.uniform(area[0], area[2]), g.uniform(area[1], area[3])
        L = g.uniform(*length); aa = a + math.radians(g.uniform(-jitter, jitter))
        segs.append((x, y, x + L * math.cos(aa), y + L * math.sin(aa), g.uniform(*inten), g.uniform(*thick)))
    return lines_layer(segs, 1)

def bolt(x0, y0, x1, y1, seed, depth=7, rough=0.2, branch=0.35, bdepth=0):
    g = random.Random(seed); segs = []
    def mid(a, b, d, w, inten, lvl):
        if d == 0:
            segs.append((a[0], a[1], b[0], b[1], inten, w)); return
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        m = ((a[0] + b[0]) / 2 + g.gauss(0, rough * L), (a[1] + b[1]) / 2 + g.gauss(0, rough * L * 0.35))
        mid(a, m, d - 1, w, inten, lvl); mid(m, b, d - 1, w, inten, lvl)
        if lvl < 2 and d >= 3 and g.random() < branch:
            ang = math.atan2(b[1] - a[1], b[0] - a[0]) + g.choice([-1, 1]) * g.uniform(0.4, 0.9)
            bl = L * g.uniform(0.8, 1.6)
            e = (m[0] + bl * math.cos(ang), m[1] + bl * math.sin(ang))
            mid(m, e, d - 2, w * 0.5, inten * 0.6, lvl + 1)
    mid((x0, y0), (x1, y1), depth, 1.0, 1.0, bdepth)
    return segs

# ---------------- finishing ----------------
def bloom(img, thr=1.0):
    b = np.clip(img - thr, 0, None)
    out = np.zeros_like(img)
    for s, k in ((6, 0.5), (20, 0.4), (60, 0.35), (160, 0.3)):
        out += np.stack([gaussian_filter(b[..., c], s) for c in range(3)], -1) * k
    return img + out

def aces(x):
    x = np.clip(x, 0, None)
    return np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)

def grade(img_lin, expo=1.0, shadow=(0.0, 0.0, 0.0), sat=1.05, contrast=1.08, seed=0, vign=0.55, grain=0.022, ca=2):
    x = aces(img_lin * expo)
    x = x ** (1 / 2.2)                                  # to display
    l = x.mean(-1, keepdims=True)
    x = l + (x - l) * sat
    x = np.clip((x - 0.5) * contrast + 0.5, 0, 1)
    x = x + (1 - l) ** 3 * np.array(shadow, np.float32)  # tint shadows
    r = np.sqrt(((XX - W / 2) / (W * 0.8)) ** 2 + ((YY - H * 0.42) / (H * 0.6)) ** 2)
    x *= np.clip(1 - vign * r ** 2.4, 0, 1)[..., None]
    if ca:
        x[..., 0] = np.roll(x[..., 0], ca, 1); x[..., 2] = np.roll(x[..., 2], -ca, 1)
    gr = np.random.default_rng(seed).normal(0, grain, (H, W)).astype(np.float32)
    gr = gaussian_filter(gr, 0.6)
    x = x + gr[..., None]
    return np.clip(x * 255, 0, 255)

# ---------------- poster typography ----------------
FD = '/usr/share/fonts/opentype/noto/'
def font(name, sz): return ImageFont.truetype(FD + name, sz, index=0)
CX = 510                          # centre of Shorts safe window (x 60-960)

def text_band(arr, top=950, k=0.78):
    y = np.arange(H, dtype=np.float32)[:, None, None]
    m = np.clip((y - top) / 200, 0, 1) * k
    return arr * (1 - m)

def compose_text(arr, jp, label, value, unit, accent, path, prefix=''):
    img = Image.fromarray(text_band(arr).astype(np.uint8)).convert('RGBA')

    def layer_text(xy, s, f, fill, anchor='mm', track=0):
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if track:
            ws = [d.textlength(c, font=f) for c in s]; tot = sum(ws) + track * (len(s) - 1)
            x = xy[0] - tot / 2
            for c, w_ in zip(s, ws):
                d.text((x, xy[1]), c, font=f, fill=fill, anchor='lm'); x += w_ + track
        else:
            d.text(xy, s, font=f, fill=fill, anchor=anchor)
        return lay

    def put(lay, glow=None, gblur=24, shadow=True):
        a = lay.getchannel('A')
        if shadow:
            sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.9)))
            img.alpha_composite(sh, (0, 10))
        if glow:
            gl = Image.new('RGBA', img.size, glow + (0,)); gl.putalpha(a.filter(ImageFilter.GaussianBlur(gblur)).point(lambda v: int(v * 0.75)))
            img.alpha_composite(gl)
        img.alpha_composite(lay)

    # tagline with hairlines
    f_tag = font('NotoSansCJK-Bold.ttc', 60)
    tag = 'もし現実で撃ったら'
    lay = layer_text((CX, 1040), tag, f_tag, (255, 255, 255, 255), track=8)
    d0 = ImageDraw.Draw(lay)
    tw = sum(d0.textlength(c, font=f_tag) for c in tag) + 8 * (len(tag) - 1)
    for sgn in (-1, 1):
        x0 = CX + sgn * (tw / 2 + 26); x1 = CX + sgn * (tw / 2 + 130)
        d0.line((x0, 1044, x1, 1044), fill=accent + (255,), width=4)
    put(lay)
    # title — serif, metallic gradient
    sz = 210
    while font('NotoSerifCJK-Black.ttc', sz).getlength(jp) > 880: sz -= 4
    f_t = font('NotoSerifCJK-Black.ttc', sz)
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).text((CX, 1215), jp, font=f_t, fill=255, anchor='mm')
    bb = m.getbbox()
    gy = np.clip((YY - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)
    top_c, bot_c = np.array([255, 255, 255]), np.array(accent) * 0.35 + np.array([255, 255, 255]) * 0.65
    grad = (top_c * (1 - gy[..., None]) + bot_c * gy[..., None])
    grad[..., :] = grad - 25 * np.exp(-((gy - 0.52) / 0.05) ** 2)[..., None]   # subtle horizon line in letters
    gimg = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert('RGBA'); gimg.putalpha(m)
    put(gimg, glow=accent, gblur=30)
    # hidden-number readout
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 110, 1350, 910, 1530
    d.rectangle((x0, y0, x1, y1), fill=(0, 0, 0, 140))
    d.rectangle((x0, y0, x1, y1), outline=(255, 255, 255, 60), width=2)
    L = 40
    for (cx, cy, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.line((cx, cy, cx + sx * L, cy), fill=accent + (255,), width=6); d.line((cx, cy, cx, cy + sy * L), fill=accent + (255,), width=6)
    img.alpha_composite(lay)
    f_l = font('NotoSansCJK-Bold.ttc', 46); f_v = font('NotoSansCJK-Black.ttc', 118); f_u = font('NotoSansCJK-Bold.ttc', 60)
    lw = f_l.getlength(label); vw = f_v.getlength(prefix + value); uw = f_u.getlength(unit) if unit else 0
    total = lw + 30 + vw + (12 + uw if unit else 0)
    x = CX - total / 2; yc = 1440
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((x, yc + 6), label, font=f_l, fill=(235, 235, 235, 255), anchor='lm'); x += lw + 30
    put(lay, shadow=False)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).text((x, yc), prefix + value, font=f_v, fill=accent + (255,), anchor='lm')
    put(lay, glow=accent, gblur=14, shadow=False); x += vw + 12
    if unit:
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).text((x, yc + 14), unit, font=f_u, fill=(255, 255, 255, 255), anchor='lm')
        put(lay, shadow=False)
    img.convert('RGB').save(path, quality=95)
