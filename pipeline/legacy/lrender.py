"""バッタvs畑の描画：畑（トウモロコシ→食べつくされた土）、地面のバッタ、飛んでいる群れ、HUD"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as nd
import battle as B
import lmodel as LM

FP = 4                                   # 畑テクスチャ：1mあたりのピクセル
LOC_C = (235, 190, 70); FIELD_C = (120, 200, 90)
_TEX = {}
def textures():
    if _TEX: return _TEX
    rng = np.random.default_rng(3); n = LM.FS * FP
    def nz(sc, amp):
        a = rng.normal(0, 1, (n // sc + 3, n // sc + 3)).astype(np.float32)
        return nd.zoom(a, sc, order=1)[:n, :n] * amp
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    rows = 0.5 + 0.5 * np.cos(2 * np.pi * xx / (0.75 * FP))          # 0.75m間隔のうね
    leaf = np.clip(0.55 + nz(3, 0.25) + nz(1, 0.18), 0, 1)
    g = np.stack([58 + 40 * leaf, 102 + 62 * leaf, 34 + 22 * leaf], -1) * (0.78 + 0.22 * rows)[..., None]
    g *= (0.9 + nz(60, 0.12))[..., None]
    soil = np.stack([132 + 0 * xx, 104 + 0 * xx, 72 + 0 * xx], -1) * (0.85 + nz(2, 0.12) + 0.08 * rows)[..., None]
    stub = (rng.random((n, n)) < 0.05) & (rows > 0.7)
    soil[stub] = (150, 132, 86)                                      # 食べ残しの茎
    _TEX['green'] = np.clip(g, 0, 255).astype(np.float32); _TEX['soil'] = np.clip(soil, 0, 255).astype(np.float32)
    _TEX['edge'] = np.clip(0.5 + nz(1, 0.35), 0, 1)
    return _TEX

def field_layer(M, t, cam):
    T = textures(); n = LM.FS * FP
    rm = M.remain_map(t)
    m = nd.zoom(rm, FP, order=1)[:n, :n]
    m = np.clip((m - (1 - T['edge']) * 0.6) * 2.2, 0, 1)
    img = T['soil'] * (1 - m[..., None]) + T['green'] * m[..., None]
    a = np.full((n, n), 255, np.uint8)
    im = Image.fromarray(np.concatenate([img.astype(np.uint8), a[..., None]], -1), 'RGBA')
    return im.transform((B.W, B.H), Image.PERSPECTIVE, B._persp(cam, FP, 0, 0), resample=Image.BILINEAR, fillcolor=(0, 0, 0, 0))

_SG = {}
def sgrain(k):
    key = (B.W, B.H, k % 4)
    if key not in _SG: _SG[key] = np.random.default_rng(50 + k % 4).random((B.H, B.W)).astype(np.float32)
    return _SG[key]

def ground_locusts(M, t, cam, f):
    x, y = M.ground_pts(t)
    if len(x) == 0: return None
    GP = 3; n = LM.FS * GP
    ix = np.clip((x * GP).astype(np.int32), 0, n - 1); iy = np.clip((y * GP).astype(np.int32), 0, n - 1)
    cnt = np.bincount(iy * n + ix, minlength=n * n).reshape(n, n).astype(np.float32)
    cnt = nd.gaussian_filter(cnt, 0.7)
    a = 1 - np.exp(-cnt * 0.9)
    m = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return m.transform((B.W, B.H), Image.PERSPECTIVE, B._persp(cam, GP, 0, 0), resample=Image.BILINEAR)

def flying_layer(M, t, cam):
    x, y, z = M.flying_pts(t)
    cx, camY, camH, hz = B.cam_params(cam)
    ok = (y - camY) > 3
    x, y, z = x[ok], y[ok], z[ok]
    X, Y = B.project(x, y, cam); s1 = B.depth_scale(y, cam); Y = Y - z * s1
    X = np.asarray(X); Y = np.asarray(Y)
    vis = (X >= 0) & (X < B.W - 1) & (Y >= 0) & (Y < B.H - 1)
    X, Y, s1 = X[vis], Y[vis], np.asarray(s1)[vis]
    acc = np.zeros((B.H, B.W), np.float32)
    w = np.clip(s1 * 0.05, 0.25, 1.0)
    np.add.at(acc, (Y.astype(np.int32), X.astype(np.int32)), w)
    big = s1 > 25
    if big.any():
        a2 = np.zeros_like(acc); np.add.at(a2, (Y[big].astype(np.int32), X[big].astype(np.int32)), 1.0)
        acc = np.maximum(acc, nd.maximum_filter(a2, size=3) * 0.9)
    return np.clip(1 - np.exp(-acc * 1.6), 0, 1)

def render(M, t, cam, hud, f=0, haze=0.0):
    g = B.draw_ground(cam, None, None).convert('RGBA')
    fl = field_layer(M, t, cam); g.alpha_composite(fl)
    gi = np.asarray(g.convert('RGB'), np.float32)
    gm = ground_locusts(M, t, cam, f)
    sg = sgrain(f)
    if gm is not None:
        ma = np.asarray(gm, np.float32) / 255
        ma = np.clip(ma * (0.35 + 0.9 * sg), 0, 1)
        col = np.array([92, 70, 26], np.float32) + np.array([110, 95, 40], np.float32) * (sg[..., None] > 0.82)
        gi = gi * (1 - ma[..., None]) + col * ma[..., None]
    fa = flying_layer(M, t, cam)
    gi = gi * (1 - fa[..., None] * 0.92) + np.array([42, 36, 24], np.float32) * fa[..., None] * 0.92
    if haze > 0:
        L = M.landed(t); hz_ = haze * (1 - 0.55 * L)
        yy = np.linspace(1, 0.35, B.H, dtype=np.float32)[:, None, None]
        gi = gi * (1 - hz_ * 0.55 * yy) + np.array([70, 62, 45], np.float32) * hz_ * 0.55 * yy
    img = Image.fromarray(np.clip(gi, 0, 255).astype(np.uint8))
    img = B.finish(img, 0.0)
    hud_draw(img, M, t, hud)
    return img

def fmt_n(n):
    if n >= 1e8: v = n / 1e8; return (f'{v:,.0f}億' if v >= 10 or v == int(v) else f'{v:.1f}億') + '匹'
    if n >= 1e4: return f'{n / 1e4:,.0f}万匹'
    return f'{int(n):,}匹'
def fmt_t(s):
    s = max(0, s); d, r = divmod(int(s), 86400); h, r = divmod(r, 3600); m, ss = divmod(r, 60)
    return (f'{d}日 ' if d else '') + f'{h:02d}:{m:02d}:{ss:02d}'

def hud_draw(im, M, t, hud):
    d = ImageDraw.Draw(im, 'RGBA'); BE = lambda s: ImageFont.truetype(B.BEBAS, s); Fo = B.Fo; BK, BD = B.BK, B.BD; W, H = B.W, B.H
    tt = max(0.0, min(t, M.t_end) - LM.T_ARR); rem = 1 - M.frac(t) if t < M.t_end else 0.0
    eaten = M.eaten(t) / 1000
    if W > H:
        d.rectangle((0, 0, W, 132), fill=(8, 10, 16, 215))
        d.text((40, 30), 'バッタ（サバクトビバッタ）', font=Fo(BK, 30), fill=LOC_C, anchor='lm')
        d.text((40, 92), fmt_n(M.n), font=Fo(BK, 62), fill=B.PALE, anchor='lm')
        d.text((W - 40, 30), '畑（東京ドーム1個分）', font=Fo(BK, 30), fill=FIELD_C, anchor='rm')
        d.text((W - 40, 92), f'{int(math.ceil(rem * 100 - 1e-6))}%', font=BE(84), fill=B.PALE, anchor='rm')
        bw = 420; x1 = W - 260
        d.rounded_rectangle((x1 - bw, 76, x1, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x1 - max(8, bw * rem), 76, x1, 104), 8, fill=FIELD_C)
        d.text((x1, 120), '畑の残り', font=Fo(BD, 20), fill=(200, 200, 205), anchor='rm')
        d.text((W / 2, 34), hud.get('round', ''), font=Fo(BK, 32), fill=(255, 210, 80), anchor='mm')
        d.text((W / 2, 86), fmt_t(tt), font=BE(60), fill=B.PALE, anchor='mm')
        d.text((W / 2, 122), f'食べた量  {eaten:,.1f} トン', font=Fo(BD, 20), fill=(200, 200, 205), anchor='mm')
        sp = hud.get('speed', 1.0)
        if sp and sp != 1.0:
            tag = 'スロー' if sp < 1 else (f'×{sp:,.0f} 早送り')
            tw = Fo(BK, 24).getlength(tag) + 50
            d.rounded_rectangle((W / 2 - tw / 2, 142, W / 2 + tw / 2, 182), 8, fill=(200, 60, 60, 220)); d.text((W / 2, 162), tag, font=Fo(BK, 24), fill=(255, 255, 255), anchor='mm')
        d.text((W - 24, H - 22), '※実データをもとにした、単純化したシミュレーションです', font=Fo(BD, 20), fill=(235, 235, 235, 200), anchor='rs')
        cap = hud.get('cap')
        if cap:
            f = Fo(BK, 52); tw = f.getlength(cap)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 210))
            d.text((W / 2, H - 125), cap, font=f, fill=hud.get('capcol', B.PALE), anchor='mm')
    else:
        d.rectangle((0, 0, W, 330), fill=(8, 10, 16, 220))
        d.text((W / 2, 64), hud.get('title', ''), font=Fo(BK, 54), fill=B.PALE, anchor='mm')
        d.text((60, 150), 'バッタ', font=Fo(BK, 40), fill=LOC_C, anchor='lm'); d.text((60, 225), '???匹' if hud.get('mask') else fmt_n(M.n), font=Fo(BK, 70), fill=B.PALE, anchor='lm')
        d.text((W - 60, 150), '畑の残り', font=Fo(BK, 40), fill=FIELD_C, anchor='rm'); d.text((W - 60, 225), f'{int(math.ceil(rem * 100 - 1e-6))}%', font=BE(100), fill=B.PALE, anchor='rm')
        d.rounded_rectangle((W / 2 + 20, 285, W - 60, 307), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((W - 60 - max(6, (W / 2 - 80) * rem), 285, W - 60, 307), 8, fill=FIELD_C)
        d.text((60, 296), fmt_t(tt), font=BE(48), fill=B.PALE, anchor='lm')
        sp = hud.get('speed', 1.0)
        if sp and sp != 1.0:
            tag = 'スロー' if sp < 1 else f'×{sp:,.0f} 早送り'; tw = Fo(BK, 30).getlength(tag) + 60
            d.rounded_rectangle((W / 2 - tw / 2, 350, W / 2 + tw / 2, 400), 10, fill=(200, 60, 60, 230)); d.text((W / 2, 375), tag, font=Fo(BK, 30), fill=(255, 255, 255), anchor='mm')
        cap = hud.get('cap')
        if cap:
            f = Fo(BK, 64); lines = cap.split('\n'); hh = 90 * len(lines); tw = max(f.getlength(l) for l in lines)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, 1420, W / 2 + tw / 2 + 40, 1420 + hh + 40), 18, fill=(8, 10, 16, 215))
            for k, l in enumerate(lines): d.text((W / 2, 1420 + 20 + 45 + k * 90), l, font=f, fill=hud.get('capcol', B.PALE), anchor='mm')
        d.text((W / 2, H - 40), '※実データをもとにした、単純化したシミュレーションです', font=Fo(BD, 24), fill=(235, 235, 235, 210), anchor='mm')
