"""巨人vs蚊の描画（2.5Dのジオラマ）：空、遠くの山、森（奥・手前）、巨人、蚊の群れ、たたく演出、HUD
座標：x（横, m）、z（高さ, m）、k（奥行き倍率。巨人=1、奥<1、手前>1）
カメラ：(cx, cz, ppm) … 巨人の位置で1mあたりppmピクセル
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from scipy import ndimage as nd
import gmodel as GM

W, H = 1920, 1080
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'; NOTOB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'; BEBAS = '/home/claude/fonts/BebasNeue-Regular.ttf'
_F = {}
def font(path, s):
    k = (path, s)
    if k not in _F: _F[k] = ImageFont.truetype(path, s, index=0) if path.endswith('.ttc') else ImageFont.truetype(path, s)
    return _F[k]
def Fo(s): return font(NOTO, s)
def Fb(s): return font(NOTOB, s)
def Mi(s): return font(SERIF, s)
def BE(s): return font(BEBAS, s)
PALE = (240, 240, 245); GOLD = (255, 210, 80); MOS_C = (210, 210, 220); BLOOD_C = (230, 80, 80); GIANT_C = (120, 190, 255)

GIANT_H = 50.0; SPR = Image.open('/home/claude/gvm/spr_giant.png').convert('RGBA')
SPR_HM = GIANT_H * (SPR.height / SPR.height) * (1.25 / 1.75)    # 見えている部分（頭〜太もも）の高さ m
SPR_BASE = GIANT_H - SPR_HM
SPR_WM = SPR_HM * SPR.width / SPR.height
GCX, GCZ = 0.0, SPR_BASE + SPR_HM * 0.55                       # 巨人の体の中心

def scr(x, z, k, cam):
    cx, cz, ppm = cam
    return W / 2 + (x - cx) * ppm * k, H / 2 - (z - cz) * ppm * k

# ---------- 背景素材 ----------
def make_forest(seed, x0, x1, top, ppm_tex, dark, haze=0.0):
    rng = np.random.default_rng(seed); w = int((x1 - x0) * ppm_tex); h = int((top + 8) * ppm_tex)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    base = [(28, 58, 30), (36, 70, 34), (24, 50, 28), (44, 78, 38)]
    n = int((x1 - x0) / 2.2)
    xs = rng.uniform(x0, x1, n * 3); tops = top * rng.uniform(0.62, 1.0, n * 3); rs = rng.uniform(2.2, 5.0, n * 3)
    d.rectangle((0, h - top * 0.6 * ppm_tex, w, h), fill=tuple(int(v * dark * 0.7) for v in base[2]) + (255,))
    order = np.argsort(tops)
    for i in order:
        x, t, r = xs[i], tops[i], rs[i]; c = np.array(base[int(rng.integers(4))], float) * dark
        cx = (x - x0) * ppm_tex; cy = h - t * ppm_tex
        for q in range(7):
            ox = rng.normal(0, r * 0.4); oy = rng.uniform(0, r * 1.6); rr = r * rng.uniform(0.5, 0.9)
            sh = 0.8 + 0.45 * (1 - min(1, oy / (r * 1.6))) + rng.normal(0, 0.06)
            col = tuple(int(min(255, v * sh)) for v in c) + (255,)
            d.ellipse((cx + (ox - rr) * ppm_tex, cy + (oy - rr) * ppm_tex, cx + (ox + rr) * ppm_tex, cy + (oy + rr) * ppm_tex), fill=col)
    a = np.asarray(im).astype(np.float32)
    nz = nd.gaussian_filter(rng.normal(0, 1, a.shape[:2]), 1.0)[..., None]
    a[..., :3] = np.clip(a[..., :3] * (1 + 0.12 * nz), 0, 255)
    if haze: a[..., :3] = a[..., :3] * (1 - haze) + np.array([150, 175, 195], np.float32) * haze
    return Image.fromarray(a.astype(np.uint8)), x0, ppm_tex, h
FT = 12
HOUSES = [(-62, 9, 6, (170, 60, 50)), (-48, 7, 5, (60, 80, 140)), (-34, 10, 7, (150, 70, 40)), (30, 8, 6, (60, 90, 120)), (44, 11, 7, (170, 60, 50)), (60, 7, 5, (90, 90, 90))]
PERSON_X = -40.5
FOREST_B = make_forest(1, -420, 420, 24.0, FT, 0.95, haze=0.3)
FOREST_F = make_forest(2, -420, 420, 21.0, FT, 0.62)
def mountains(x):
    return 160 + 90 * np.sin(x / 260 + 1.3) + 60 * np.sin(x / 117 + 0.2) + 25 * np.sin(x / 41)

_SKY = {}
def sky():
    if (W, H) not in _SKY:
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        top = np.array([96, 140, 196], np.float32); bot = np.array([196, 214, 226], np.float32)
        a = top * (1 - y) + bot * y; a = np.broadcast_to(a, (H, W, 3)).copy()
        rng = np.random.default_rng(3); cl = nd.gaussian_filter(rng.normal(0, 1, (H // 8, W // 8)), 6)
        cl = np.kron(np.clip((cl - 0.15) * 2.2, 0, 1), np.ones((8, 8)))[:H, :W][..., None] * (1 - y) * 0.6
        a = a * (1 - cl) + 245 * cl
        _SKY[(W, H)] = Image.fromarray(a.astype(np.uint8))
    return _SKY[(W, H)].copy()

def paste_strip(im, F, k, cam, shade=1.0):
    tex, x0, ppm_tex, hpx = F; cx, cz, ppm = cam; s = ppm * k / ppm_tex
    xl = cx - W / 2 / (ppm * k); xr = cx + W / 2 / (ppm * k)
    a = int(max(0, (xl - x0) * ppm_tex) - 2); b = int(min(tex.width, (xr - x0) * ppm_tex) + 2)
    if b <= a: return
    crop = tex.crop((a, 0, b, hpx)); tw = max(1, int(crop.width * s)); th = max(1, int(crop.height * s))
    if tw > 6000 or th > 6000: return
    crop = crop.resize((tw, th), Image.BILINEAR)
    X0, _ = scr(x0 + a / ppm_tex, 0, k, cam); _, Yg = scr(0, 0, k, cam)
    im.alpha_composite(crop, (int(X0), int(Yg - th)))
    return Yg

# ---------- 蚊 ----------
NF = 30000
_r = np.random.default_rng(9)
FA = _r.uniform(0, 6.28, NF).astype(np.float32); FR = (4 + 40 * _r.random(NF) ** 1.6).astype(np.float32)
FW = (_r.uniform(0.05, 0.25, NF) * _r.choice([-1, 1], NF)).astype(np.float32); FK = _r.uniform(0.9, 1.12, NF).astype(np.float32)
FP = _r.uniform(0, 6.28, NF).astype(np.float32)
_NZ = np.random.default_rng(4).random((SPR.height // 3, SPR.width // 3)).astype(np.float32)
_spr_cache = {}
def giant_sprite(hpx, cov):
    key = (int(hpx), int(cov * 40))
    if key in _spr_cache: return _spr_cache[key]
    sp = SPR.resize((max(2, int(SPR.width * hpx / SPR.height)), max(2, int(hpx))), Image.BILINEAR)
    if cov > 0.01:
        m = Image.fromarray(((_NZ < cov * 0.32) * 255).astype(np.uint8)).resize(sp.size, Image.NEAREST)
        dark = Image.new('RGBA', sp.size, (26, 22, 20, 255)); a = sp.split()[3]
        mm = Image.fromarray((np.minimum(np.asarray(m), np.asarray(a))).astype(np.uint8))
        sp = Image.composite(dark, sp, mm); sp.putalpha(a)
    if len(_spr_cache) > 200: _spr_cache.clear()
    _spr_cache[key] = sp; return sp

def render(M, t, cam, hud, f=0, speed=1.0, giant_dark=0.0):
    cx, cz, ppm = cam
    im = sky().convert('RGBA'); d = ImageDraw.Draw(im)
    # 遠くの山と平原
    km = 0.22; xs = np.linspace(cx - W / 2 / (ppm * km), cx + W / 2 / (ppm * km), 200)
    pts = [scr(x, mountains(x) * 0.25, km, cam) for x in xs]
    _, Ym = scr(0, 0, km, cam)
    d.polygon(pts + [(W, Ym), (0, Ym)], fill=(132, 156, 178, 255))
    if Ym < H: d.rectangle((0, max(0, Ym), W, H), fill=(92, 120, 80, 255))
    paste_strip(im, FOREST_B, 0.82, cam)
    _, Yb = scr(0, 0, 0.82, cam)
    if Yb < H: d.rectangle((0, max(0, Yb), W, H), fill=(34, 60, 32, 255))
    # 巨人
    hpx = SPR_HM * ppm; cov = min(1.0, M.onbody(t) / GM.CAP) if M else 0.0
    sp = giant_sprite(hpx, cov)
    X, Y = scr(GCX, SPR_BASE + SPR_HM, 1.0, cam)
    if sp.width < 9000: im.alpha_composite(sp, (int(X - sp.width / 2), int(Y)))
    box = (X - sp.width / 2, Y, sp.width, sp.height)
    # 手前の森
    paste_strip(im, FOREST_F, 1.1, cam)
    _, Yf = scr(0, 0, 1.1, cam); d = ImageDraw.Draw(im)
    if Yf < H: d.rectangle((0, max(0, Yf), W, H), fill=(22, 40, 22, 255))
    # 手前の村（大きさの目安）
    kv = 1.2; _, Yv = scr(0, 0, kv, cam)
    if Yv < H + 400 * kv:
        if Yv < H: d.rectangle((0, max(0, Yv - 2 * ppm * kv), W, H), fill=(70, 104, 56, 255))
        for hx, hw, hh, rc in HOUSES:
            X0, Y0 = scr(hx - hw / 2, 0, kv, cam); X1, Y1 = scr(hx + hw / 2, hh, kv, cam)
            if X1 < -50 or X0 > W + 50: continue
            Yr = Y1 - (X1 - X0) * 0.35
            d.rectangle((X0, Y1, X1, Y0), fill=(226, 220, 205, 255)); d.polygon([(X0 - 0.3 * ppm, Y1), (X1 + 0.3 * ppm, Y1), ((X0 + X1) / 2, Yr)], fill=rc + (255,))
            wx = (X1 - X0) * 0.18
            if wx > 2: d.rectangle((X0 + wx, Y1 + (Y0 - Y1) * 0.35, X0 + 2 * wx, Y1 + (Y0 - Y1) * 0.6), fill=(70, 90, 110, 255))
        px, _ = scr(PERSON_X, 0, kv, cam); hpx_ = 1.75 * ppm * kv
        if hpx_ >= 6:
            pw = hpx_ * 0.28; d.ellipse((px - pw * 0.4, Yv - hpx_, px + pw * 0.4, Yv - hpx_ + pw * 0.8), fill=(30, 30, 40, 255))
            d.rounded_rectangle((px - pw / 2, Yv - hpx_ + pw * 0.75, px + pw / 2, Yv), radius=max(1, pw * 0.25), fill=(30, 30, 40, 255))
            if hud.get('ruler'):
                d.text((px, Yv - hpx_ - 6), 'ふつうの人', font=Fo(max(16, int(ppm * 1.2))), fill=PALE, anchor='md', stroke_width=3, stroke_fill=(0, 0, 0))
    img = im.convert('RGB')
    # 蚊の群れ
    if M is not None:
        fl = M.flying(t); k = int(NF * min(1.0, (fl / (GM.CAP * 3)) ** 0.5 + 0.25 * cov))
        if k > 0:
            sp_ = 1.0 if speed <= 3 else 0.15
            a = FA[:k] + FW[:k] * t * sp_
            x = GCX + FR[:k] * np.cos(a) * 1.2; z = GCZ + FR[:k] * np.sin(a) * 0.6 + 2 * np.sin(t * 0.7 * sp_ + FP[:k])
            X_, Y_ = scr(x, z, FK[:k], cam)
            vis = (X_ >= 1) & (X_ < W - 2) & (Y_ >= 1) & (Y_ < H - 2)
            acc = np.zeros((H, W), np.float32); np.add.at(acc, (Y_[vis].astype(np.int32), X_[vis].astype(np.int32)), 1.0)
            dot = nd.maximum_filter(acc, size=2 if ppm < 40 else 3)
            smoke = nd.gaussian_filter(acc, 10) * (60.0 / max(8.0, ppm)) * 2.0
            al = np.clip(1 - np.exp(-(dot * 0.9 + smoke)), 0, 0.92)[..., None]
            gi = np.asarray(img, np.float32); gi = gi * (1 - al) + np.array([30, 28, 26], np.float32) * al
            img = Image.fromarray(gi.astype(np.uint8))
    # たたく演出・「刺せない！」
    shake = 0.0
    d = ImageDraw.Draw(img, 'RGBA')
    if M is not None and speed <= 3 and M.onbody(t) > 1000 and t < M.t_end:
        per = GM.SWAT; t0 = math.floor(t / per) * per
        for j in range(2):
            ts = t0 - j * per; age = t - ts
            if age < 0 or age > 0.9: continue
            rr = np.random.default_rng(abs(int(ts * 10))); u, v = rr.uniform(0.15, 0.85), rr.uniform(0.15, 0.7)
            px = box[0] + u * box[2]; py = box[1] + v * box[3]; q = age / 0.9
            R = ppm * (1.5 + 6 * q); d.ellipse((px - R, py - R, px + R, py + R), outline=(255, 250, 230, int(230 * (1 - q))), width=max(3, int(ppm * 0.25)))
            kills = GM.KILL * M.onbody(ts) * per
            txt = f'-{kills / 1e4:.1f}万匹' if kills >= 1e4 else f'-{int(kills):,}匹'
            fs = int(max(34, min(80, ppm * 2.2)))
            d.text((px, py - ppm * (3 + 6 * q)), txt, font=Fo(fs), fill=(255, 230, 120, int(255 * (1 - q))), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0, int(255 * (1 - q))))
            if age < 0.15: shake = max(shake, (1 - age / 0.15) * min(14, ppm * 0.4))
        if not M.can_bite:
            for j in range(3):
                tq = math.floor(t / 0.7) * 0.7 - j * 0.23; age = t - tq
                if age < 0 or age > 0.7: continue
                rr = np.random.default_rng(abs(int(tq * 100)) + 7); u, v = rr.uniform(0.2, 0.8), rr.uniform(0.1, 0.8)
                px = box[0] + u * box[2]; py = box[1] + v * box[3]; q = age / 0.7; fs = int(max(26, min(56, ppm * 1.4)))
                d.text((px, py - q * ppm * 2), '刺せない！', font=Fo(fs), fill=(255, 255, 255, int(255 * (1 - q))), anchor='mm', stroke_width=3, stroke_fill=(200, 40, 40, int(255 * (1 - q))))
    if hud.get('ruler'):
        rx = GCX + SPR_WM * 0.62; X0_, Y0_ = scr(rx, 0, 1.0, cam); _, Y50 = scr(rx, GIANT_H, 1.0, cam)
        d.line((X0_, Y0_, X0_, Y50), fill=(255, 220, 90, 255), width=5)
        for zz in range(0, 51, 10):
            _, yy = scr(rx, zz, 1.0, cam); d.line((X0_ - 10, yy, X0_ + 10, yy), fill=(255, 220, 90, 255), width=4)
        d.text((X0_ + 18, Y50), '身長 50m', font=Fo(max(30, int(ppm * 2.6))), fill=GOLD, anchor='lm', stroke_width=4, stroke_fill=(0, 0, 0))
    img = finish(img, shake, f)
    if not hud.get("off"): hud_draw(img, M, t, hud)
    return img

_G = {}
def finish(img, shake, f):
    if shake > 0.5:
        dx = int(np.random.default_rng(f).normal(0, shake)); dy = int(np.random.default_rng(f + 1).normal(0, shake))
        img = img.transform(img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR)
    key = (W, H)
    if key not in _G:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _G[key] = (np.clip(1 - 0.32 * np.clip(r - 0.55, 0, 1) ** 1.4, 0, 1)[..., None]).astype(np.float32)
    a = np.asarray(img, np.float32) * _G[key]
    a = (a - 128) * 1.06 + 128 + np.random.default_rng(f % 7).normal(0, 3, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def fmt_t(s):
    s = max(0, s); h, r = divmod(int(s), 3600); m, ss = divmod(r, 60); return f'{h:02d}:{m:02d}:{ss:02d}'
def fmt_big(n):
    if n >= 1e8: v = n / 1e8; return (f'{v:.0f}' if v >= 10 or abs(v - round(v)) < 1e-6 else f'{v:.1f}') + '億匹'
    if n >= 1e4: return f'{n / 1e4:,.0f}万匹'
    return f'{int(n):,}匹'

def hud_draw(im, M, t, hud):
    if M is None: return
    d = ImageDraw.Draw(im, 'RGBA')
    tt = min(t, M.t_end); rem = M.remaining(t); lost = M.blood_lost(t); left_l = (GM.BLOOD - lost) / 1000; br = max(0.0, 1 - lost / GM.BLOOD); bites = M.bites(t)
    if W > H:
        d.rectangle((0, 0, W, 132), fill=(8, 10, 16, 215))
        d.text((40, 30), '蚊の大群', font=Fo(30), fill=MOS_C, anchor='lm')
        d.text((40, 92), fmt_big(rem), font=Fo(56), fill=PALE, anchor='lm')
        bw = 340; x0 = 420
        d.rounded_rectangle((x0, 76, x0 + bw, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x0, 76, x0 + max(8, bw * rem / M.n), 104), 8, fill=MOS_C)
        d.text((x0, 52), f'残っている蚊 / {fmt_big(M.n)}', font=Fb(22), fill=(200, 200, 205), anchor='lm')
        d.text((W - 40, 30), '巨人の血液', font=Fo(30), fill=BLOOD_C, anchor='rm')
        d.text((W - 40, 92), f'{left_l:,.0f}L', font=BE(80), fill=PALE, anchor='rm')
        bw = 400; x1 = W - 290
        d.rounded_rectangle((x1 - bw, 76, x1, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x1 - max(8, bw * br), 76, x1, 104), 8, fill=BLOOD_C)
        xd = x1 - bw * (1 - GM.DANGER); d.line((xd, 68, xd, 112), fill=(255, 220, 90), width=4); d.text((xd, 122), '危険ライン（3割）', font=Fb(18), fill=(255, 220, 90), anchor='mm')
        d.text((W / 2, 34), hud.get('round', ''), font=Fo(32), fill=GOLD, anchor='mm')
        d.text((W / 2, 86), fmt_t(tt), font=BE(60), fill=PALE, anchor='mm')
        d.text((W / 2, 122), f'刺された回数  {int(bites):,}回', font=Fb(20), fill=(200, 200, 205), anchor='mm')
        sp = hud.get('speed', 1.0)
        if sp and sp != 1.0:
            tag = 'スロー' if sp < 1 else f'×{sp:,.0f} 早送り'; tw = Fo(24).getlength(tag) + 50
            d.rounded_rectangle((W / 2 - tw / 2, 142, W / 2 + tw / 2, 182), 8, fill=(200, 60, 60, 220)); d.text((W / 2, 162), tag, font=Fo(24), fill=(255, 255, 255), anchor='mm')
        d.text((W - 24, H - 22), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(20), fill=(235, 235, 235, 200), anchor='rs')
        cap = hud.get('cap')
        if cap:
            f = Fo(52); tw = f.getlength(cap)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 210))
            d.text((W / 2, H - 125), cap, font=f, fill=hud.get('capcol', PALE), anchor='mm')
    else:
        d.rectangle((0, 0, W, 330), fill=(8, 10, 16, 220))
        d.text((W / 2, 64), hud.get('title', ''), font=Fo(54), fill=PALE, anchor='mm')
        d.text((60, 150), '刺された回数', font=Fo(36), fill=MOS_C, anchor='lm'); d.text((60, 225), f'{int(bites):,}', font=BE(92), fill=PALE, anchor='lm')
        d.text((W - 60, 150), '巨人の血液', font=Fo(36), fill=BLOOD_C, anchor='rm'); d.text((W - 60, 225), f'{left_l:,.0f}L', font=BE(88), fill=PALE, anchor='rm')
        x0, x1 = W / 2 + 20, W - 60
        d.rounded_rectangle((x0, 285, x1, 307), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x1 - max(6, (x1 - x0) * br), 285, x1, 307), 8, fill=BLOOD_C)
        xd = x1 - (x1 - x0) * (1 - GM.DANGER); d.line((xd, 278, xd, 314), fill=(255, 220, 90), width=4)
        d.text((60, 296), fmt_t(tt), font=BE(48), fill=PALE, anchor='lm')
        sp = hud.get('speed', 1.0)
        if sp and sp != 1.0:
            tag = 'スロー' if sp < 1 else f'×{sp:,.0f} 早送り'; tw = Fo(30).getlength(tag) + 60
            d.rounded_rectangle((W / 2 - tw / 2, 350, W / 2 + tw / 2, 400), 10, fill=(200, 60, 60, 230)); d.text((W / 2, 375), tag, font=Fo(30), fill=(255, 255, 255), anchor='mm')
        cap = hud.get('cap')
        if cap:
            f = Fo(64); lines = cap.split('\n'); hh = 90 * len(lines); tw = max(f.getlength(l) for l in lines)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, 1420, W / 2 + tw / 2 + 40, 1420 + hh + 40), 18, fill=(8, 10, 16, 215))
            for k, l in enumerate(lines): d.text((W / 2, 1420 + 20 + 45 + k * 90), l, font=f, fill=hud.get('capcol', PALE), anchor='mm')
        d.text((W / 2, H - 40), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(24), fill=(235, 235, 235, 210), anchor='mm')
