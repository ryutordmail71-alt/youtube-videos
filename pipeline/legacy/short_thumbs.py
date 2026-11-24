import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, map_coordinates

W, H = 1080, 1920
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
def F(sz): return ImageFont.truetype(FB, sz, index=0)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

def fractal(w, h, seed, oct=6, base=3):
    g = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        k = base * 2 ** o
        a = g.random((k, k)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        tot += amp; amp *= 0.55
    acc /= tot; return (acc - acc.min()) / (acc.max() - acc.min())

def pal(v, stops):
    xs = [s[0] for s in stops]
    return np.stack([np.interp(v, xs, [s[1][i] for s in stops]) for i in range(3)], -1).astype(np.float32)

FIRE = [(0, (0, 0, 0)), (0.25, (110, 8, 0)), (0.5, (235, 70, 0)), (0.7, (255, 160, 20)), (0.88, (255, 235, 140)), (1, (255, 255, 250))]
ICE = [(0, (0, 0, 0)), (0.3, (10, 40, 90)), (0.55, (60, 150, 230)), (0.78, (170, 230, 255)), (1, (255, 255, 255))]
WATER = [(0, (0, 0, 0)), (0.3, (0, 30, 110)), (0.55, (0, 110, 230)), (0.78, (80, 210, 255)), (1, (240, 255, 255))]
BEAM = [(0, (0, 0, 0)), (0.3, (120, 30, 0)), (0.55, (255, 120, 0)), (0.75, (255, 210, 60)), (0.9, (255, 250, 200)), (1, (255, 255, 255))]

def bg_grad(top, bot, seed, tint):
    a = np.linspace(0, 1, H)[:, None, None]
    bg = (np.array(top) * (1 - a) + np.array(bot) * a) * np.ones((1, W, 1))
    n = fractal(W, H, seed, 5)
    bg += (np.clip(n - 0.45, 0, 1) * 120)[..., None] * np.array(tint) / 255
    return bg.astype(np.float32)

def jet(ox, oy, ang, length, w0, w1, stops, seed, turb=0.55, gain=1.0):
    """turbulent jet field from origin along angle"""
    ca, sa = math.cos(ang), math.sin(ang)
    u = (XX - ox) * ca + (YY - oy) * sa
    v = -(XX - ox) * sa + (YY - oy) * ca
    k = np.clip(u / length, 0, 1.3)
    width = w0 + (w1 - w0) * k
    n = fractal(W, H, seed, 6, 4)
    n2 = fractal(W, H, seed + 1, 5, 2)
    # warp coordinates for flame tongues
    vv = v + (n2 - 0.5) * width * 1.4
    prof = np.exp(-(vv / width) ** 2 * 1.6)
    along = np.clip(u / 60, 0, 1) * np.exp(-np.clip(u - length, 0, None) / (length * 0.15))
    core = np.exp(-(vv / (width * 0.35)) ** 2) * along
    val = prof * along * (1 - turb + turb * n * 1.4) * (1.05 - 0.35 * k)
    val = np.clip(val * gain + core * 0.35, 0, 1)
    return val

def add(img, val, stops, strength=1.0, glow=40):
    col = pal(np.clip(val, 0, 1), stops)
    g = gaussian_filter(val, glow)[..., None] * pal(np.full_like(val, 0.7), stops)
    return img * (1 - np.clip(val, 0, 1)[..., None] * 0.85) + col * strength + g * 0.9

def speedlines(img, cx, cy, n, seed, col, r0=380):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); g = random.Random(seed)
    for _ in range(n):
        a = g.uniform(0, 2 * math.pi); rr = g.uniform(r0, r0 + 250); r1 = 2400; w = g.uniform(0.004, 0.014)
        d.polygon([(cx + rr * math.cos(a), cy + rr * math.sin(a)), (cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)),
                   (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))], fill=col)
    img.paste(lay, (0, 0), lay)

def particles(img, n, seed, colfn, area, size, streak=(0, 0)):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); g = random.Random(seed)
    for _ in range(n):
        x = g.uniform(area[0], area[2]); y = g.uniform(area[1], area[3]); r = g.uniform(*size)
        c = colfn(g)
        if streak != (0, 0):
            L = g.uniform(0.5, 1.5)
            d.line((x, y, x + streak[0] * L, y + streak[1] * L), fill=c, width=max(1, int(r)))
        else:
            d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    glow = lay.filter(ImageFilter.GaussianBlur(6))
    img.paste(glow, (0, 0), glow); img.paste(lay, (0, 0), lay)

# ---------------- text ----------------
def ctext(img, s, cy, size, grad, inner=(0, 0, 0), outer=(255, 255, 255), i_w=14, o_w=28, maxw=1000, rot=0, cx=540, italic=0.0):
    f = F(size); d0 = ImageDraw.Draw(img)
    wtxt = d0.textlength(s, font=f)
    if wtxt > maxw - 2 * o_w:
        size = int(size * (maxw - 2 * o_w) / wtxt); f = F(size)
    l, t, r, b = d0.textbbox((0, 0), s, font=f, stroke_width=o_w)
    pad = 40
    lay = Image.new('RGBA', (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); o = (pad - l, pad - t)
    if outer: d.text(o, s, font=f, fill=outer, stroke_width=o_w, stroke_fill=outer)
    if inner: d.text(o, s, font=f, fill=inner, stroke_width=i_w, stroke_fill=inner)
    m = Image.new('L', lay.size, 0); ImageDraw.Draw(m).text(o, s, font=f, fill=255)
    gy = np.linspace(0, 1, lay.size[1])[:, None, None]
    stops = np.array(grad, np.float32)
    idx = gy * (len(stops) - 1); i0 = np.clip(np.floor(idx).astype(int), 0, len(stops) - 2); fr = idx - i0
    gi = stops[i0[:, 0, 0]] * (1 - fr[:, :, :1][:, 0]) [:, None] if False else None
    rows = []
    for yv in np.linspace(0, 1, lay.size[1]):
        p = yv * (len(stops) - 1); j = min(int(p), len(stops) - 2); q = p - j
        rows.append(stops[j] * (1 - q) + stops[j + 1] * q)
    gi = np.array(rows)[:, None, :] * np.ones((1, lay.size[0], 1))
    gimg = Image.fromarray(gi.astype(np.uint8)).convert('RGBA'); gimg.putalpha(m)
    lay = Image.alpha_composite(lay, gimg)
    # glossy highlight on upper half
    hl = Image.new('RGBA', lay.size, (255, 255, 255, 0))
    hm = np.zeros(lay.size[::-1], np.uint8); hm[: int(lay.size[1] * 0.45)] = 70
    hm = (np.asarray(m, np.float32) / 255 * hm).astype(np.uint8)
    hl.putalpha(Image.fromarray(hm)); lay = Image.alpha_composite(lay, hl)
    if italic:
        lay = lay.transform(lay.size, Image.AFFINE, (1, italic, -italic * lay.size[1] / 2, 0, 1, 0), resample=Image.BICUBIC)
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel('A').point(lambda a: int(a * 0.7)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    px, py = int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)
    img.paste(sh, (px + 10, py + 14), sh); img.paste(lay, (px, py), lay)

def ribbon(img, s, cy, bg, fg, size=64, skew=30, padx=50, cx=540, rot=0, border=(0, 0, 0)):
    f = F(size); d0 = ImageDraw.Draw(img)
    tw = d0.textlength(s, font=f); w = tw + 2 * padx; h = size * 1.5
    lay = Image.new('RGBA', (int(w + 2 * skew + 40), int(h + 40)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0 = 20 + skew, 20
    d.polygon([(x0 - 10, y0 - 10), (x0 + w + skew + 10, y0 - 10), (x0 + w + 10, y0 + h + 10), (x0 - skew - 10, y0 + h + 10)], fill=border)
    d.polygon([(x0, y0), (x0 + w + skew, y0), (x0 + w, y0 + h), (x0 - skew, y0 + h)], fill=bg)
    d.text((x0 + w / 2 + skew / 2 - skew / 2, y0 + h / 2), s, font=f, fill=fg, anchor='mm')
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

def hook_box(img, parts, cy, accent, size=78):
    """parts: list of (text, color). '？？？' gets highlighted box"""
    f = F(size); d0 = ImageDraw.Draw(img)
    widths = [d0.textlength(t, font=f) + (40 if q else 0) for t, q in parts]
    total = sum(widths) + 20 * (len(parts) - 1)
    bw = total + 100; bh = size * 1.7
    x = 540 - bw / 2; y = cy - bh / 2
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x - 8, y - 8, x + bw + 8, y + bh + 8), 34, fill=(255, 255, 255))
    d.rounded_rectangle((x, y, x + bw, y + bh), 28, fill=(15, 15, 25))
    cxp = x + 50
    for (t, q), wdt in zip(parts, widths):
        if q:
            d.rounded_rectangle((cxp, cy - size * 0.68, cxp + wdt, cy + size * 0.68), 16, fill=accent)
            d.text((cxp + wdt / 2, cy), t, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0))
        else:
            d.text((cxp, cy), t, font=f, fill=(255, 255, 255), anchor='lm')
        cxp += wdt + 20
    img.paste(lay, (0, 0), lay)

def finish(img, theme_col, title_grad, name, hook, accent, path, name_rot=-4):
    ribbon(img, 'もし現実で撃ったら', 250, theme_col, (255, 255, 255), size=66, rot=-3)
    ctext(img, name, 1290, 230, title_grad, rot=name_rot, italic=-0.12)
    hook_box(img, hook, 1530, accent)
    # subtle bottom fade for Shorts UI area
    a = np.clip((np.arange(H) - 1680) / 240, 0, 1)[:, None, None] * 0.55
    arr = np.asarray(img, np.float32); arr = arr * (1 - a)
    Image.fromarray(arr.astype(np.uint8)).save(path)

def to_img(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ======================= moves =======================
def kaen(path):
    img = bg_grad((30, 4, 0), (10, 0, 0), 1, (255, 60, 0))
    v = jet(-80, 1150, math.radians(-38), 1250, 50, 360, FIRE, 11, gain=1.25)
    img = add(img, v, FIRE, glow=50)
    im = to_img(img)
    speedlines(im, 540, 700, 70, 3, (255, 200, 120, 60), r0=520)
    particles(im, 160, 4, lambda g: (255, g.randint(140, 230), 40, 255), (300, 200, 1080, 1100), (2, 6), streak=(40, -30))
    finish(im, (220, 50, 0), [(255, 255, 200), (255, 200, 40), (255, 90, 0), (200, 20, 0)], 'かえんほうしゃ',
           [('温度', 0), ('？？？', 1), ('℃', 0)], (230, 40, 0), path)

def bakuhatsu(path):
    img = bg_grad((20, 8, 0), (5, 0, 0), 2, (255, 120, 0))
    cx, cy = 540, 760
    r = np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.05) ** 2); th = np.arctan2(YY - cy, XX - cx)
    n = fractal(W, H, 21, 6, 4); n2 = fractal(W, H, 22, 5, 2)
    rr = r * (0.75 + 0.5 * n2)
    v = np.clip(1.25 - rr / 420 + (n - 0.5) * 0.7, 0, 1) ** 1.2
    img = add(img, v, FIRE, glow=70)
    # shockwave ring
    ring = np.exp(-((r - 560) / 26) ** 2) * (0.6 + 0.4 * n)
    img += ring[..., None] * np.array([255, 220, 180]) * 0.8
    img += gaussian_filter(ring, 18)[..., None] * np.array([255, 150, 60]) * 1.2
    im = to_img(img)
    speedlines(im, cx, cy, 110, 5, (255, 230, 180, 70), r0=600)
    g = random.Random(7); d = ImageDraw.Draw(im)
    for _ in range(40):   # debris
        a = g.uniform(0, 2 * math.pi); dist = g.uniform(450, 900); s = g.uniform(8, 26)
        x, y = cx + dist * math.cos(a), cy + dist * math.sin(a)
        pts = [(x + s * math.cos(a + k * 2.1 + g.uniform(-.4, .4)), y + s * math.sin(a + k * 2.1)) for k in range(3)]
        d.polygon(pts, fill=(40, 20, 10)); d.line(pts + [pts[0]], fill=(255, 140, 40), width=2)
    finish(im, (200, 20, 20), [(255, 255, 220), (255, 220, 60), (255, 110, 0), (180, 10, 0)], 'だいばくはつ',
           [('半径', 0), ('？？？', 1), ('km消滅', 0)], (220, 20, 20), path)

def fubuki(path):
    img = bg_grad((10, 30, 60), (2, 8, 25), 3, (120, 200, 255))
    n = fractal(W, H, 31, 6, 3)
    # swirling storm: diagonal bands
    u = (XX * 0.8 + YY * 0.6) / 140
    band = (np.sin(u + n * 6) * 0.5 + 0.5) ** 3
    v = np.clip(band * 0.55 * np.exp(-((YY - 760) / 700) ** 2) + n * 0.25, 0, 1)
    img = add(img, v, ICE, glow=30)
    im = to_img(img)
    particles(im, 520, 8, lambda g: (255, 255, 255, g.randint(150, 255)), (-200, 0, 1080, 1700), (2, 7), streak=(110, 70))
    particles(im, 160, 9, lambda g: (220, 245, 255, 255), (0, 0, 1080, 1700), (3, 9))
    # ice crystals (snowflakes)
    d = ImageDraw.Draw(im); g = random.Random(12)
    for _ in range(9):
        x, y, s = g.uniform(60, 1020), g.uniform(380, 1100), g.uniform(30, 80)
        for k in range(6):
            a = k * math.pi / 3
            ex, ey = x + s * math.cos(a), y + s * math.sin(a)
            d.line((x, y, ex, ey), fill=(230, 250, 255), width=5)
            for f in (0.5, 0.75):
                bx, by = x + s * f * math.cos(a), y + s * f * math.sin(a)
                for sgn in (-1, 1):
                    d.line((bx, by, bx + s * 0.25 * math.cos(a + sgn * 0.8), by + s * 0.25 * math.sin(a + sgn * 0.8)), fill=(230, 250, 255), width=4)
    # frost on edges
    arr = np.asarray(im, np.float32)
    edge = np.clip(1 - np.minimum(np.minimum(XX, W - XX), np.minimum(YY, H - YY)) / 140, 0, 1) * (0.5 + 0.5 * n)
    arr = arr * (1 - edge[..., None] * 0.7) + np.array([220, 245, 255]) * edge[..., None] * 0.7
    im = to_img(arr)
    finish(im, (20, 120, 220), [(255, 255, 255), (200, 240, 255), (90, 180, 255), (20, 80, 200)], 'ふぶき',
           [('−', 0), ('？？？', 1), ('℃で即凍結', 0)], (20, 120, 230), path, name_rot=-3)

def hydro(path):
    img = bg_grad((0, 15, 45), (0, 3, 15), 4, (0, 140, 255))
    v = jet(1180, 1200, math.radians(-150), 1300, 60, 230, WATER, 41, turb=0.35, gain=1.3)
    v2 = jet(1180, 1200, math.radians(-150), 1300, 20, 70, WATER, 43, turb=0.2, gain=1.0)
    img = add(img, np.clip(v + v2 * 0.6, 0, 1), WATER, glow=35)
    im = to_img(img)
    # spray droplets near tip (upper-left) and along jet
    particles(im, 260, 14, lambda g: (200, 240, 255, g.randint(180, 255)), (0, 380, 600, 900), (3, 10))
    particles(im, 120, 15, lambda g: (160, 220, 255, 220), (0, 300, 900, 1200), (2, 5), streak=(-60, -35))
    speedlines(im, 140, 600, 60, 16, (180, 230, 255, 60), r0=420)
    finish(im, (0, 110, 230), [(240, 255, 255), (120, 220, 255), (0, 140, 255), (0, 60, 180)], 'ハイドロポンプ',
           [('水圧で', 0), ('？？？', 1), ('も切断', 0)], (0, 120, 240), path)

def hakai(path):
    img = bg_grad((25, 10, 0), (5, 0, 5), 5, (255, 140, 0))
    v = jet(-100, 980, math.radians(-14), 1400, 120, 170, BEAM, 51, turb=0.18, gain=1.6)
    img = add(img, v, BEAM, glow=60)
    # energy rings around the beam
    ca, sa = math.cos(math.radians(-14)), math.sin(math.radians(-14))
    u = (XX + 100) * ca + (YY - 980) * sa; vv = -(XX + 100) * sa + (YY - 980) * ca
    for uc in (250, 560, 870):
        e = np.exp(-(((u - uc) / 34) ** 2 + (vv / 270) ** 2 - 1) ** 2 * 6)
        img += e[..., None] * np.array([255, 230, 150]) * 0.9
    im = to_img(img)
    speedlines(im, 900, 760, 120, 6, (255, 220, 150, 70), r0=300)
    particles(im, 140, 17, lambda g: (255, 240, 180, 255), (0, 600, 1080, 1300), (2, 5), streak=(120, -30))
    finish(im, (230, 120, 0), [(255, 255, 230), (255, 230, 80), (255, 130, 0), (190, 40, 0)], 'はかいこうせん',
           [('撃った本人は', 0), ('？？？', 1)], (230, 110, 0), path)

if __name__ == '__main__':
    import sys
    out = '/home/claude/shorts_thumbs'
    import os; os.makedirs(out, exist_ok=True)
    kaen(f'{out}/1_kaenhousha.png'); bakuhatsu(f'{out}/2_daibakuhatsu.png'); fubuki(f'{out}/3_fubuki.png')
    hydro(f'{out}/4_hydropump.png'); hakai(f'{out}/5_hakaikousen.png')
