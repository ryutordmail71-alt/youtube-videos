import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter

W, H = 1080, 1920
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
D = '/usr/share/fonts/opentype/noto/'
def font(name, sz): return ImageFont.truetype(D + name, sz, index=0)
SERIF_B = 'NotoSerifCJK-Black.ttc'; SANS_L = 'NotoSansCJK-Light.ttc'; SANS_M = 'NotoSansCJK-Medium.ttc'; SANS_B = 'NotoSansCJK-Bold.ttc'

def fractal(seed, oct=8, base=4, w=W, h=H):
    g = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        k = base * 2 ** o
        a = g.random((k, int(k * w / h) + 1)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        tot += amp; amp *= 0.52
    acc /= tot; return (acc - acc.min()) / (acc.max() - acc.min())

def pal(v, stops):
    xs = [s[0] for s in stops]
    return np.stack([np.interp(v, xs, [s[1][i] for s in stops]) for i in range(3)], -1).astype(np.float32)

FIRE = [(0, (0, 0, 0)), (0.2, (60, 6, 0)), (0.42, (180, 40, 0)), (0.62, (250, 110, 10)), (0.8, (255, 190, 70)), (0.93, (255, 240, 190)), (1, (255, 252, 240))]
ICE = [(0, (0, 0, 0)), (0.3, (10, 30, 55)), (0.55, (70, 130, 180)), (0.8, (180, 220, 240)), (1, (250, 254, 255))]
WATER = [(0, (0, 0, 0)), (0.3, (0, 25, 60)), (0.55, (10, 100, 170)), (0.8, (120, 200, 240)), (1, (245, 255, 255))]
BEAM = [(0, (0, 0, 0)), (0.25, (70, 15, 0)), (0.5, (230, 90, 0)), (0.72, (255, 180, 50)), (0.9, (255, 245, 200)), (1, (255, 255, 255))]

def jet_field(ox, oy, ang, length, w0, w1, seed, turb=0.7, warp=1.4):
    ca, sa = math.cos(ang), math.sin(ang)
    u = (XX - ox) * ca + (YY - oy) * sa
    v = -(XX - ox) * sa + (YY - oy) * ca
    k = np.clip(u / length, 0, 1.3)
    width = w0 + (w1 - w0) * k ** 0.8
    n = fractal(seed); n2 = fractal(seed + 1, 6, 2)
    vv = v + (n2 - 0.5) * width * warp
    prof = np.exp(-(vv / width) ** 2 * 1.8)
    along = np.clip(u / 80, 0, 1) * np.exp(-np.clip(u - length, 0, None) / (length * 0.18))
    core = np.exp(-(vv / (width * 0.25)) ** 2) * along * (1 - k * 0.6)
    val = prof * along * ((1 - turb) + turb * n ** 1.3 * 1.6) * (1.0 - 0.45 * k) + core * 0.45
    return np.clip(val, 0, 1.2), u, vv, width

def smoke(seed, mask, col, amt):
    n = fractal(seed, 7, 3)
    s = np.clip(n * 1.4 - 0.5, 0, 1) * mask
    return s[..., None] * np.array(col, np.float32) * amt, s

def post(img, tint_shadow, bloom_thr=180, grain=7, vign=0.75, seed=0):
    # bloom
    lum = img.mean(-1)
    bright = np.clip(img - bloom_thr, 0, None)
    b = np.stack([gaussian_filter(bright[..., c], 25) + 0.6 * gaussian_filter(bright[..., c], 80) for c in range(3)], -1)
    img = img + b * 1.1
    # filmic tone
    x = img / 255
    x = x * (1 + x / 3.0) / (1 + x)
    x = x / (1.333 / 2.333) if False else x * 1.9
    img = np.clip(x, 0, 1) * 255
    # shadow tint
    sh = np.clip(1 - img.mean(-1) / 120, 0, 1)[..., None]
    img = img + sh * np.array(tint_shadow, np.float32)
    # vignette
    r = np.sqrt(((XX - W / 2) / (W * 0.75)) ** 2 + ((YY - H * 0.45) / (H * 0.62)) ** 2)
    img *= np.clip(1 - vign * r ** 2.2, 0, 1)[..., None]
    # chromatic aberration (subtle)
    img[..., 0] = np.roll(img[..., 0], 2, 1); img[..., 2] = np.roll(img[..., 2], -2, 1)
    # grain
    g = np.random.default_rng(seed).normal(0, grain, (H, W, 1)).astype(np.float32)
    img = img + g
    return np.clip(img, 0, 255)

def particles(img, n, seed, col, area, size, streak=(0, 0), alpha=(120, 255)):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); g = random.Random(seed)
    for _ in range(n):
        x = g.uniform(area[0], area[2]); y = g.uniform(area[1], area[3]); r = g.uniform(*size)
        c = col + (g.randint(*alpha),)
        if streak != (0, 0):
            L = g.uniform(0.4, 1.4); d.line((x, y, x + streak[0] * L, y + streak[1] * L), fill=c, width=max(1, round(r)))
        else:
            d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    gl = lay.filter(ImageFilter.GaussianBlur(5)); img.paste(gl, (0, 0), gl)
    lay = lay.filter(ImageFilter.GaussianBlur(0.8)); img.paste(lay, (0, 0), lay)

# ---------------- typography ----------------
def spaced(d, xy, s, f, fill, track, anchor_center=True):
    widths = [d.textlength(c, font=f) for c in s]
    total = sum(widths) + track * (len(s) - 1)
    x = xy[0] - total / 2 if anchor_center else xy[0]
    for c, w in zip(s, widths):
        d.text((x, xy[1]), c, font=f, fill=fill, anchor='lm'); x += w + track
    return total

def layout(img, no, en, jp, label, value, unit, accent, path, prefix=''):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # top header
    f_small = font(SANS_M, 30)
    spaced(d, (540, 150), f'SIMULATION  No.{no:02d}', f_small, (255, 255, 255, 200), 7)
    f_hd = font(SANS_B, 58)
    w = spaced(d, (540, 232), 'もし現実で撃ったら', f_hd, (255, 255, 255, 255), 10)
    d.line((540 - w / 2 - 150, 236, 540 - w / 2 - 34, 236), fill=(255, 255, 255, 170), width=2)
    d.line((540 + w / 2 + 34, 236, 540 + w / 2 + 150, 236), fill=(255, 255, 255, 170), width=2)
    # english name + rule
    f_en = font(SANS_L, 40)
    we = spaced(d, (540, 1150), en, f_en, accent + (255,), 16)
    d.line((90, 1150, 540 - we / 2 - 36, 1150), fill=(255, 255, 255, 90), width=2)
    d.line((540 + we / 2 + 36, 1150, 990, 1150), fill=(255, 255, 255, 90), width=2)
    img.paste(lay, (0, 0), lay)
    # japanese title with glow
    f_t = font(SERIF_B, 190)
    dd = ImageDraw.Draw(img)
    tw = dd.textlength(jp, font=f_t)
    sz = 190 if tw < 960 else int(190 * 960 / tw)
    f_t = font(SERIF_B, sz)
    tl = Image.new('RGBA', img.size, (0, 0, 0, 0)); td = ImageDraw.Draw(tl)
    td.text((540, 1300), jp, font=f_t, fill=(255, 255, 255, 255), anchor='mm')
    glow = Image.new('RGBA', img.size, accent + (0,)); glow.putalpha(tl.getchannel('A').filter(ImageFilter.GaussianBlur(26)).point(lambda a: int(a * 0.9)))
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0)); shadow.putalpha(tl.getchannel('A').filter(ImageFilter.GaussianBlur(12)).point(lambda a: int(a * 0.8)))
    img.paste(shadow, (0, 8), shadow); img.paste(glow, (0, 0), glow); img.paste(tl, (0, 0), tl)
    # data readout (HUD)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 150, 1450, 930, 1640
    d.rectangle((x0, y0, x1, y1), fill=(0, 0, 0, 120))
    L = 34
    for (cx, cy, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.line((cx, cy, cx + sx * L, cy), fill=accent + (255,), width=4); d.line((cx, cy, cx, cy + sy * L), fill=accent + (255,), width=4)
    spaced(d, (540, 1494), label, font(SANS_M, 36), (255, 255, 255, 210), 8)
    f_v = font(SANS_B, 104); f_u = font(SANS_M, 56)
    vw = d.textlength(value, font=f_v); uw = d.textlength(unit, font=f_u); pw = d.textlength(prefix, font=f_v) if prefix else 0
    total = pw + vw + 12 + uw; x = 540 - total / 2
    if prefix: d.text((x, 1578), prefix, font=f_v, fill=(255, 255, 255, 255), anchor='lm'); x += pw
    vl = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(vl).text((x, 1578), value, font=f_v, fill=accent + (255,), anchor='lm')
    vg = Image.new('RGBA', img.size, accent + (0,)); vg.putalpha(vl.getchannel('A').filter(ImageFilter.GaussianBlur(14)))
    lay.paste(vg, (0, 0), vg); lay = Image.alpha_composite(lay, vl); d = ImageDraw.Draw(lay)
    x += vw + 12
    d.text((x, 1592), unit, font=f_u, fill=(255, 255, 255, 255), anchor='lm')
    img.paste(lay, (0, 0), lay)
    img.convert('RGB').save(path, quality=95)

def base_bg(top, bot):
    a = np.linspace(0, 1, H)[:, None, None]
    return ((np.array(top) * (1 - a) + np.array(bot) * a) * np.ones((1, W, 1))).astype(np.float32)

def composite(bg, val, stops, gain=1.0):
    col = pal(np.clip(val * gain, 0, 1), stops)
    a = np.clip(val * 1.6, 0, 1)[..., None]
    return bg * (1 - a) + col * a + col * (1 - a) * 0.4

# ======================= moves =======================
def kaen(path):
    bg = base_bg((14, 6, 4), (6, 3, 3))
    v, u, vv, wd = jet_field(-120, 1250, math.radians(-40), 1350, 40, 420, 11, turb=0.85, warp=1.8)
    sm, s = smoke(13, np.exp(-(vv / (wd * 1.9)) ** 2) * (u > 200) * (1 - np.exp(-(vv / (wd * 0.9)) ** 2)), (60, 50, 48), 0.9)
    bg = bg * (1 - s[..., None] * 0.5) + sm
    img = composite(bg, v, FIRE, 1.05)
    img += gaussian_filter(v, 90)[..., None] * np.array([255, 90, 20]) * 0.45   # ambient light
    img = post(img, (10, 4, 0), seed=1)
    im = Image.fromarray(img.astype(np.uint8))
    particles(im, 220, 4, (255, 190, 90), (250, 150, 1080, 1100), (1, 3), streak=(26, -20))
    layout(im, 1, 'FLAMETHROWER', 'かえんほうしゃ', '推定温度', '？？？？', '℃', (255, 140, 40), path)

def bakuhatsu(path):
    bg = base_bg((10, 6, 5), (3, 2, 2))
    cx, cy = 540, 720
    r = np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.1) ** 2)
    n = fractal(21); n2 = fractal(22, 6, 2)
    rr = r * (0.7 + 0.6 * n2)
    v = np.clip(1.3 - rr / 400 + (n - 0.5) * 0.9, 0, 1.2) ** 1.4
    # smoke shell
    shell = np.exp(-((r - 470) / 160) ** 2)
    sm, s = smoke(23, shell, (55, 45, 40), 1.0)
    bg = bg * (1 - s[..., None] * 0.6) + sm
    img = composite(bg, v, FIRE, 1.0)
    ring = np.exp(-((r - 600) / 10) ** 2) * (0.4 + 0.6 * n)
    img += gaussian_filter(ring, 6)[..., None] * np.array([255, 210, 170]) * 1.4
    img += gaussian_filter(v, 120)[..., None] * np.array([255, 100, 30]) * 0.6
    # ground horizon glow
    hz = np.exp(-((YY - 1080) / 30) ** 2) * np.exp(-((XX - cx) / 600) ** 2)
    img += hz[..., None] * np.array([255, 150, 70]) * 0.7
    img[1080:] *= 0.55
    img = post(img, (8, 4, 2), seed=2)
    im = Image.fromarray(img.astype(np.uint8))
    particles(im, 260, 5, (255, 200, 120), (0, 100, 1080, 1100), (1, 2.6))
    layout(im, 2, 'EXPLOSION', 'だいばくはつ', '推定被害半径', '？？？', 'km', (255, 120, 50), path)

def fubuki(path):
    bg = base_bg((16, 30, 46), (4, 9, 16))
    n = fractal(31, 8, 3); n2 = fractal(32, 6, 2)
    u = (XX * 0.85 + YY * 0.55) / 160
    band = (np.sin(u + n2 * 7) * 0.5 + 0.5) ** 2
    fog = np.clip(band * 0.45 + n * 0.35 - 0.15, 0, 1) * np.exp(-((YY - 700) / 800) ** 2)
    img = composite(bg, fog, ICE, 0.9)
    img += gaussian_filter(fog, 60)[..., None] * np.array([120, 180, 230]) * 0.35
    img = post(img, (0, 6, 14), bloom_thr=170, seed=3)
    im = Image.fromarray(img.astype(np.uint8))
    particles(im, 900, 8, (235, 245, 255), (-300, -100, 1080, 1700), (0.8, 2.2), streak=(70, 44), alpha=(60, 220))
    particles(im, 300, 9, (240, 250, 255), (-100, 0, 1080, 1700), (1.5, 4.5), streak=(140, 88), alpha=(30, 120))
    # frost creeping from edges
    arr = np.asarray(im, np.float32)
    fn = fractal(33, 8, 6)
    edge = np.clip(1 - np.minimum(np.minimum(XX, W - XX), np.minimum(YY, H - YY)) / 120 + (fn - 0.5) * 0.9, 0, 1) ** 1.5
    arr = arr * (1 - edge[..., None] * 0.55) + np.array([210, 235, 250]) * edge[..., None] * 0.55
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    layout(im, 3, 'BLIZZARD', 'ふぶき', '到達気温', '？？？', '℃', (140, 210, 255), path, prefix='−')

def hydro(path):
    bg = base_bg((4, 12, 22), (2, 5, 10))
    v, u, vv, wd = jet_field(1200, 1150, math.radians(-148), 1350, 50, 200, 41, turb=0.45, warp=0.9)
    v2, *_ = jet_field(1200, 1150, math.radians(-148), 1350, 16, 50, 43, turb=0.2, warp=0.4)
    mist_mask = np.exp(-(vv / (wd * 2.6)) ** 2) * (u > 300)
    sm, s = smoke(44, mist_mask, (90, 140, 170), 0.6)
    bg = bg + sm
    img = composite(bg, np.clip(v + v2 * 0.7, 0, 1.2), WATER, 1.0)
    img += gaussian_filter(v, 70)[..., None] * np.array([40, 140, 230]) * 0.5
    img = post(img, (0, 4, 10), seed=4)
    im = Image.fromarray(img.astype(np.uint8))
    particles(im, 380, 14, (210, 240, 255), (0, 380, 640, 950), (1, 3.5))
    particles(im, 200, 15, (190, 230, 255), (0, 300, 1000, 1200), (1, 2), streak=(-50, -30))
    layout(im, 4, 'HYDRO PUMP', 'ハイドロポンプ', '推定噴射圧', '？？？', '気圧', (80, 190, 255), path)

def hakai(path):
    bg = base_bg((12, 7, 4), (4, 2, 3))
    ang = math.radians(-12)
    v, u, vv, wd = jet_field(-150, 900, ang, 1500, 110, 150, 51, turb=0.25, warp=0.35)
    img = composite(bg, v, BEAM, 1.15)
    # thin energy rings
    for uc in (300, 620, 940):
        e = np.exp(-(((u - uc) / 26) ** 2 + (vv / 250) ** 2 - 1) ** 2 * 18) * (np.abs(vv) > 60)
        img += e[..., None] * np.array([255, 200, 120]) * 0.7
    # anamorphic flare
    fl = np.exp(-((YY - (900 + (XX + 150) * math.tan(ang))) / 6) ** 2) * 0.6
    img += fl[..., None] * np.array([255, 170, 90])
    img += gaussian_filter(v, 110)[..., None] * np.array([255, 120, 30]) * 0.55
    img = post(img, (8, 4, 0), seed=5)
    im = Image.fromarray(img.astype(np.uint8))
    particles(im, 200, 17, (255, 220, 150), (0, 500, 1080, 1250), (1, 2.4), streak=(70, -15))
    layout(im, 5, 'HYPER BEAM', 'はかいこうせん', '使用者への反動', '？？？', '', (255, 150, 50), path)

if __name__ == '__main__':
    out = '/home/claude/shorts_thumbs_v2'; os.makedirs(out, exist_ok=True)
    kaen(f'{out}/1_kaenhousha.png'); bakuhatsu(f'{out}/2_daibakuhatsu.png'); fubuki(f'{out}/3_fubuki.png')
    hydro(f'{out}/4_hydropump.png'); hakai(f'{out}/5_hakaikousen.png')
