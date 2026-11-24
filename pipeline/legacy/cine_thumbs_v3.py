import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
from cine_thumbs import (W, H, XX, YY, fractal, pal, FIRE, ICE, WATER, BEAM, jet_field, smoke, post,
                         particles, layout, base_bg, composite)

def god_rays(arr, cx, cy, color, thr=170, n=28, step=0.035, k=0.9):
    bright = np.clip(arr.mean(-1) - thr, 0, None)
    bi = Image.fromarray(np.clip(bright * 2, 0, 255).astype(np.uint8))
    acc = np.zeros((H, W), np.float32)
    for i in range(n):
        s = 1 + i * step
        im = bi.transform((W, H), Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s), resample=Image.BILINEAR)
        acc += np.asarray(im, np.float32) * (1 - i / n)
    acc /= n
    return arr + acc[..., None] * np.array(color, np.float32) / 255 * k

def bokeh(arr, n, seed, col, area, rmin, rmax, amin=0.15, amax=0.5):
    g = random.Random(seed)
    lay = np.zeros((H, W), np.float32); cols = np.zeros((H, W, 3), np.float32)
    for _ in range(n):
        x, y, r = g.uniform(area[0], area[2]), g.uniform(area[1], area[3]), g.uniform(rmin, rmax)
        a = g.uniform(amin, amax)
        x0, x1, y0, y1 = int(max(0, x - r - 3)), int(min(W, x + r + 3)), int(max(0, y - r - 3)), int(min(H, y + r + 3))
        if x0 >= x1 or y0 >= y1: continue
        d = np.sqrt((XX[y0:y1, x0:x1] - x) ** 2 + (YY[y0:y1, x0:x1] - y) ** 2)
        disc = np.clip((r - d) / 2.5, 0, 1) * (0.75 + 0.25 * (d / r) ** 3) * a
        lay[y0:y1, x0:x1] += disc
    return arr + lay[..., None] * np.array(col, np.float32)

def streaks(arr, cx, cy, n, seed, col, r0, r1, width=(1, 3), alpha=(0.3, 0.9)):
    g = random.Random(seed)
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    for _ in range(n):
        a = g.uniform(0, 2 * math.pi); a0 = g.uniform(r0, r0 * 1.5); a1 = a0 + g.uniform(80, r1)
        d.line((cx + a0 * math.cos(a), cy + a0 * math.sin(a), cx + a1 * math.cos(a), cy + a1 * math.sin(a)),
               fill=int(255 * g.uniform(*alpha)), width=int(g.uniform(*width)))
    m = np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    gl = gaussian_filter(m, 6)
    return arr + (m + gl * 1.5)[..., None] * np.array(col, np.float32)

def finish(arr, im_fn):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

# ======================= moves =======================
def kaen(path):
    bg = base_bg((16, 6, 3), (6, 3, 3))
    v, u, vv, wd = jet_field(-180, 1150, math.radians(-46), 1500, 120, 980, 11, turb=0.7, warp=1.6)
    sm, s = smoke(13, np.exp(-(vv / (wd * 1.7)) ** 2) * np.clip((u - 150) / 400, 0, 1) * (1 - np.exp(-(vv / (wd * 0.8)) ** 2)), (55, 44, 40), 1.0)
    bg = bg * (1 - s[..., None] * 0.5) + sm
    img = composite(bg, np.clip(v * 1.2, 0, 1.2), FIRE, 1.1)
    img += gaussian_filter(v, 110)[..., None] * np.array([255, 90, 20]) * 0.8
    img = god_rays(img, 160, 1000, (255, 150, 60), thr=160, k=1.4)
    img = post(img, (12, 4, 0), seed=1, vign=0.6)
    img = bokeh(img, 26, 3, (255, 140, 50), (0, 0, W, 1300), 14, 46, 0.15, 0.55)
    im = finish(img, None)
    particles(im, 420, 4, (255, 190, 90), (150, 100, 1080, 1300), (1, 3.4), streak=(34, -28))
    layout(im, 1, 'FLAMETHROWER', 'かえんほうしゃ', '推定温度', '？？？？', '℃', (255, 140, 40), path)

def bakuhatsu(path):
    bg = base_bg((12, 6, 4), (3, 2, 2))
    cx, cy = 540, 700
    r = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    g = np.random.default_rng(5)
    Dn = np.zeros((H, W), np.float32)
    for i in range(110):
        a = g.uniform(0, 2 * np.pi); rr = 520 * g.random() ** 0.6
        bx, by = cx + rr * np.cos(a), cy + rr * np.sin(a) * 0.85
        br = g.uniform(90, 260) * (1.15 - rr / 800)
        Dn += np.exp(-(((XX - bx) ** 2 + (YY - by) ** 2) / br ** 2) * 2.2)
    nf = fractal(21, 8, 6)
    Dn = np.clip(Dn, 0, 3) * (0.7 + 0.6 * nf)
    T = np.clip(Dn / 3.0, 0, 1) ** 0.75 * np.exp(-(r / 640) ** 2) * (0.6 + 0.8 * nf ** 1.4)
    sm, s_ = smoke(23, np.clip(Dn / 1.5, 0, 1) * np.clip(r / 500, 0, 1), (60, 46, 40), 1.0)
    bg = bg * (1 - s_[..., None] * 0.7) + sm
    img = composite(bg, np.clip(T, 0, 1.15), FIRE, 1.05)
    # shockwave: bright thin ring + distortion haze
    ring = np.exp(-((r - 720) / 9) ** 2) * (0.35 + 0.65 * nf)
    img += gaussian_filter(ring, 4)[..., None] * np.array([255, 220, 190]) * 1.2
    img += gaussian_filter(ring, 30)[..., None] * np.array([255, 140, 60]) * 2.0
    img += gaussian_filter(T, 140)[..., None] * np.array([255, 100, 30]) * 1.0
    # ground + dust wave
    hz = np.exp(-((YY - 1110) / 26) ** 2) * np.exp(-((XX - cx) / 700) ** 2)
    img += hz[..., None] * np.array([255, 160, 80]) * 1.2
    dust, ds = smoke(24, np.exp(-((YY - 1080) / 70) ** 2), (120, 80, 50), 1.0)
    img = img + dust * 0.8
    img[1120:] *= 0.5
    img = streaks(img, cx, cy, 160, 7, (255, 190, 120), 520, 700, width=(1, 4))
    img = god_rays(img, cx, cy, (255, 170, 90), thr=160, k=1.6, step=0.045)
    img = post(img, (10, 4, 2), seed=2, vign=0.55)
    img = bokeh(img, 30, 5, (255, 150, 70), (0, 0, W, 1150), 10, 40, 0.12, 0.45)
    im = finish(img, None)
    particles(im, 300, 6, (255, 190, 110), (0, 50, 1080, 1100), (1, 2.6))
    layout(im, 2, 'EXPLOSION', 'だいばくはつ', '推定被害半径', '？？？', 'km', (255, 120, 50), path)

def fubuki(path):
    bg = base_bg((14, 26, 40), (3, 7, 13))
    cx, cy = 760, 520
    big = fractal(31, 8, 3, w=W * 3, h=H)
    im_n = Image.fromarray((big * 255).astype(np.uint8)).rotate(-32, resample=Image.BICUBIC)
    n = np.asarray(im_n.crop((W, 0, 2 * W, H)), np.float32) / 255
    n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    r = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2); th = np.arctan2(YY - cy, XX - cx)
    swirl = (np.sin(th * 3 + r / 90 + n * 5) * 0.5 + 0.5) ** 2
    light = np.exp(-(r / 520) ** 2)
    fog = np.clip((n - 0.25) * 1.6, 0, 1) * (0.35 + 0.9 * light) + swirl * light * 0.5
    img = composite(bg, np.clip(fog, 0, 1.1), ICE, 1.0)
    img += light[..., None] * np.array([140, 200, 255]) * 0.9
    img += np.exp(-(r / 160) ** 2)[..., None] * np.array([255, 255, 255]) * 0.8
    img[1150:] *= np.linspace(1, 0.5, H - 1150)[:, None, None]
    img = streaks(img, cx, cy, 420, 9, (200, 230, 255), 150, 900, width=(1, 3), alpha=(0.15, 0.7))
    img = god_rays(img, cx, cy, (170, 220, 255), thr=150, k=1.3, step=0.04)
    img = post(img, (0, 6, 16), bloom_thr=165, seed=3, vign=0.6)
    img = bokeh(img, 34, 11, (200, 230, 255), (0, 0, W, 1400), 10, 50, 0.1, 0.4)
    im = finish(img, None)
    particles(im, 1300, 8, (200, 225, 245), (-300, -100, 1080, 1750), (0.8, 2.2), streak=(70, 44), alpha=(40, 170))
    particles(im, 300, 9, (220, 238, 255), (-100, 0, 1080, 1750), (2, 6), streak=(170, 105), alpha=(20, 80))
    layout(im, 3, 'BLIZZARD', 'ふぶき', '到達気温', '？？？', '℃', (140, 210, 255), path, prefix='−')

def hydro(path):
    bg = base_bg((4, 12, 24), (2, 5, 10))
    ang = math.radians(-148)
    v, u, vv, wd = jet_field(1250, 1180, ang, 1250, 110, 360, 41, turb=0.5, warp=1.0)
    v2, *_ = jet_field(1250, 1180, ang, 1250, 30, 90, 43, turb=0.2, warp=0.4)
    mist_mask = np.exp(-(vv / (wd * 2.6)) ** 2) * np.clip((u - 200) / 500, 0, 1)
    sm, s = smoke(44, mist_mask, (90, 150, 190), 0.8)
    bg = bg + sm
    img = composite(bg, np.clip(v + v2 * 0.8, 0, 1.2), WATER, 1.1)
    # impact splash at the tip
    tx, ty = 1250 + 1250 * math.cos(ang), 1180 + 1250 * math.sin(ang)
    tx, ty = max(tx, 90), ty
    rr = np.sqrt((XX - tx) ** 2 + (YY - ty) ** 2)
    sp = np.clip(1 - rr / 380, 0, 1) ** 1.5 * (0.5 + 0.8 * fractal(45, 8, 8))
    img += pal(np.clip(sp, 0, 1), WATER) * 0.9
    img += gaussian_filter(v, 90)[..., None] * np.array([40, 150, 255]) * 0.8
    img = streaks(img, tx, ty, 200, 12, (190, 235, 255), 120, 500, width=(1, 4))
    img = god_rays(img, tx, ty, (120, 200, 255), thr=160, k=1.3)
    img = post(img, (0, 4, 12), seed=4, vign=0.6)
    img = bokeh(img, 40, 13, (150, 210, 255), (0, 0, W, 1300), 10, 48, 0.12, 0.45)
    im = finish(img, None)
    particles(im, 600, 14, (210, 240, 255), (0, 200, 760, 1000), (1, 4))
    particles(im, 260, 15, (190, 230, 255), (0, 200, 1080, 1250), (1, 2.4), streak=(-60, -36))
    layout(im, 4, 'HYDRO PUMP', 'ハイドロポンプ', '推定噴射圧', '？？？', '気圧', (80, 190, 255), path)

def hakai(path):
    bg = base_bg((14, 7, 3), (4, 2, 3))
    ang = math.radians(-13)
    v, u, vv, wd = jet_field(-150, 930, ang, 1600, 200, 260, 51, turb=0.25, warp=0.3)
    img = composite(bg, np.clip(v * 1.25, 0, 1.2), BEAM, 1.2)
    # heat haze sheath
    sheath = np.exp(-(vv / (wd * 2.2)) ** 2) * (0.5 + 0.5 * fractal(52, 7, 4))
    img += sheath[..., None] * np.array([255, 110, 20]) * 0.5
    # source flare
    src = np.exp(-(((XX + 30) / 330) ** 2 + ((YY - 900) / 330) ** 2))
    img += src[..., None] * np.array([255, 220, 150]) * 1.3
    # anamorphic streak full width
    fl = np.exp(-((YY - (930 + (XX + 150) * math.tan(ang))) / 5) ** 2)
    img += fl[..., None] * np.array([255, 200, 140]) * 0.9
    img += gaussian_filter(v, 130)[..., None] * np.array([255, 120, 30]) * 0.9
    # ground-scatter sparks shooting off the beam
    img = streaks(img, -150, 930 - 150 * math.tan(ang), 220, 18, (255, 200, 120), 300, 900, width=(1, 3), alpha=(0.2, 0.8))
    img = god_rays(img, 0, 900, (255, 170, 80), thr=165, k=1.4, step=0.05)
    img = post(img, (10, 4, 0), seed=5, vign=0.55)
    img = bokeh(img, 30, 17, (255, 170, 80), (0, 0, W, 1300), 10, 46, 0.12, 0.5)
    im = finish(img, None)
    particles(im, 360, 17, (255, 220, 150), (0, 400, 1080, 1300), (1, 2.6), streak=(90, -20))
    layout(im, 5, 'HYPER BEAM', 'はかいこうせん', '使用者への反動', '？？？', '', (255, 150, 50), path)

if __name__ == '__main__':
    import sys
    out = '/home/claude/shorts_thumbs_v3'; os.makedirs(out, exist_ok=True)
    which = sys.argv[1:] or ['1', '2', '3', '4', '5']
    fns = {'1': (kaen, '1_kaenhousha'), '2': (bakuhatsu, '2_daibakuhatsu'), '3': (fubuki, '3_fubuki'),
           '4': (hydro, '4_hydropump'), '5': (hakai, '5_hakaikousen')}
    for w in which:
        f, n = fns[w]; f(f'{out}/{n}.png')
