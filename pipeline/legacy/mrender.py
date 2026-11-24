"""蚊vs人間の描画：沼の草地、人（腰から下は草に隠れる）、とまっている蚊、飛びまわる蚊、たたく演出、HUD"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from scipy import ndimage as nd
import battle as B
import mmodel as MM

HX, HY = 100.0, 100.0
MOS_C = (200, 200, 210); BLOOD_C = (230, 80, 80)
SPR = Image.open('/home/claude/mvh/spr_man.png').convert('RGBA')
SPR_H = 1.25                      # スプライトの高さ（m）：頭から太ももまで
SPR_BASE = 0.55                   # スプライトの下端の高さ（m）
_rng = np.random.default_rng(5)
_a = np.asarray(SPR)[..., 3]; _ys, _xs = np.where(_a > 200)
_sel = _rng.choice(len(_xs), 6000, replace=False)
DOTS = np.stack([_xs[_sel] / SPR.width, _ys[_sel] / SPR.height], 1).astype(np.float32)   # 体の上の点（0〜1）

def reed_tex(seed, w_m=2.6, h_m=0.95, ppm=260):
    rng = np.random.default_rng(seed); W_, H_ = int(w_m * ppm), int(h_m * ppm)
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for _ in range(int(220 * w_m)):
        x0 = rng.uniform(0, W_); h = rng.uniform(0.45, 1.0) * H_; lean = rng.normal(0, 0.18) * h
        c = rng.uniform(0, 1); col = (int(96 + 60 * c), int(118 + 40 * c), int(50 + 20 * c), 255)
        pts = [(x0 + lean * (k / 6) ** 2, H_ - h * k / 6) for k in range(7)]
        d.line(pts, fill=col, width=max(1, int(rng.uniform(0.006, 0.012) * ppm)))
    return im
REED_F = reed_tex(1); REED_B = reed_tex(2, 2.2, 0.85)
REEDS = [(HX + _rng.uniform(-22, 22), HY + _rng.uniform(-6, 30), _rng.uniform(0.6, 1.4)) for _ in range(70)]
REEDS = [r for r in REEDS if abs(r[0] - HX) > 2.5 or abs(r[1] - HY) > 2.5]
_RC = {}
def reed_scaled(tex, key, wpx):
    k = (key, max(4, int(wpx // 2 * 2)))
    if k not in _RC:
        _RC[k] = tex.resize((k[1], max(2, int(tex.height * k[1] / tex.width))), Image.BILINEAR)
        if len(_RC) > 3000: _RC.clear()
    return _RC[k]

NF = 14000
_f = np.random.default_rng(9)
FR = (0.25 + 3.5 * _f.random(NF) ** 1.8).astype(np.float32); FA = _f.uniform(0, 6.28, NF).astype(np.float32); FW = (_f.uniform(0.6, 2.5, NF) * _f.choice([-1, 1], NF)).astype(np.float32)
FZ = _f.uniform(0.2, 2.6, NF).astype(np.float32); FZP = _f.uniform(0, 6.28, NF).astype(np.float32)

def render(M, t, cam, hud, f=0, speed=1.0):
    g = B.draw_ground(cam, None, None).convert('RGB')
    gi = np.asarray(g, np.float32); gi = gi * np.array([0.86, 0.95, 0.82], np.float32)        # 少し湿った沼っぽく
    im = Image.fromarray(np.clip(gi, 0, 255).astype(np.uint8)).convert('RGBA')
    cx, camY, camH, hz = B.cam_params(cam)
    # 奥の草むら
    items = []
    for (x, y, s) in REEDS: items.append((y, 'reed', x, s))
    items.append((HY + 0.01, 'man', HX, 1.0))
    for y, kind, x, s in sorted(items, key=lambda z: -z[0]):
        if y - camY < 1.5: continue
        X, Y = B.project(x, y, cam); s1 = float(B.depth_scale(y, cam)); X = float(X); Y = float(Y)
        if kind == 'reed':
            r = reed_scaled(REED_B, 'b', 2.2 * s * s1); im.alpha_composite(r, (int(X - r.width / 2), int(Y - r.height))) if -r.width < X < B.W + r.width and Y < B.H + r.height else None
        else:
            r = reed_scaled(REED_B, 'b', 2.2 * s1); im.alpha_composite(r, (int(X - r.width / 2 + 0.2 * s1), int(Y - r.height - 0.15 * s1)))
            hpx = SPR_H * s1; sp = SPR.resize((max(2, int(SPR.width * hpx / SPR.height)), max(2, int(hpx))), Image.BILINEAR)
            sx0 = int(X - sp.width / 2); sy0 = int(Y - SPR_BASE * s1 - sp.height)
            im.alpha_composite(sp, (sx0, sy0))
            # とまっている蚊
            k = int(len(DOTS) * min(1.0, M.onbody(t) / MM.CAP))
            if k:
                d = ImageDraw.Draw(im); pr = max(1.0, s1 * 0.004)
                jit = np.random.default_rng(f % 5).normal(0, 0.002, (k, 2))
                for (u, v), (jx, jy) in zip(DOTS[:k], jit):
                    px = sx0 + (u + jx) * sp.width; py = sy0 + (v + jy) * sp.height
                    d.ellipse((px - pr, py - pr * 0.7, px + pr, py + pr * 0.7), fill=(28, 24, 22, 230))
            r = reed_scaled(REED_F, 'f', 2.6 * s1); im.alpha_composite(r, (int(X - r.width / 2), int(Y - r.height + 0.05 * s1)))
            man_box = (sx0, sy0, sp.width, sp.height, s1)
    img = im.convert('RGB')
    # 飛んでいる蚊
    k = int(NF * min(1.0, (M.flying(t) / 150000) ** 0.5 + 0.15 * min(1, M.onbody(t) / MM.CAP)))
    if k > 0:
        a = FA[:k] + FW[:k] * t * (1 if speed <= 3 else 0.2)
        x = HX + FR[:k] * np.cos(a); y = HY + FR[:k] * np.sin(a) * 0.8; z = FZ[:k] + 0.15 * np.sin(t * 3 + FZP[:k])
        ok = (y - camY) > 1.0
        X, Y = B.project(x[ok], y[ok], cam); s1 = np.asarray(B.depth_scale(y[ok], cam)); Y = np.asarray(Y) - z[ok] * s1; X = np.asarray(X)
        vis = (X >= 1) & (X < B.W - 2) & (Y >= 1) & (Y < B.H - 2)
        acc = np.zeros((B.H, B.W), np.float32)
        np.add.at(acc, (Y[vis].astype(np.int32), X[vis].astype(np.int32)), 1.0)
        big = np.zeros_like(acc); bv = vis & (s1 > 120)
        np.add.at(big, (Y[bv].astype(np.int32), X[bv].astype(np.int32)), 1.0)
        acc = np.maximum(acc, nd.maximum_filter(big, size=3))
        al = np.clip(acc * 0.75, 0, 0.85)[..., None]
        gi = np.asarray(img, np.float32); gi = gi * (1 - al) + np.array([30, 28, 26], np.float32) * al
        img = Image.fromarray(gi.astype(np.uint8))
    img = B.finish(img, 0.0)
    # たたく演出（パチン）
    d = ImageDraw.Draw(img, 'RGBA')
    if speed <= 2.5 and M.onbody(t) > 30 and t < M.t_end:
        per = 0.8; t0 = math.floor(t / per) * per
        for j in range(2):
            ts = t0 - j * per; age = t - ts
            if age < 0 or age > 0.6: continue
            rr = np.random.default_rng(int(ts * 10)); u, v = rr.uniform(0.15, 0.85), rr.uniform(0.15, 0.7)
            sx0, sy0, sw, sh, s1 = man_box; px = sx0 + u * sw; py = sy0 + v * sh; q = age / 0.6
            R = s1 * (0.05 + 0.18 * q); d.ellipse((px - R, py - R, px + R, py + R), outline=(255, 250, 230, int(220 * (1 - q))), width=max(2, int(s1 * 0.01)))
            kills = int(MM.KILL * M.onbody(ts) * per)
            if kills > 0: d.text((px, py - s1 * (0.1 + 0.25 * q)), f'-{kills:,}匹', font=B.Fo(B.BK, int(max(30, min(64, s1 * 0.12)))), fill=(255, 230, 120, int(255 * (1 - q))), anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0, int(255 * (1 - q))))
    hud_draw(img, M, t, hud)
    return img

def fmt_t(s):
    s = max(0, s); h, r = divmod(int(s), 3600); m, ss = divmod(r, 60); return f'{h:02d}:{m:02d}:{ss:02d}'
def fmt_n(n):
    if n >= 1e4: return f'{n / 1e4:,.0f}万匹' if n >= 1e5 else f'{n / 1e4:,.1f}万匹'
    return f'{int(n):,}匹'

def hud_draw(im, M, t, hud):
    d = ImageDraw.Draw(im, 'RGBA'); BE = lambda s: ImageFont.truetype(B.BEBAS, s); Fo = B.Fo; BK, BD = B.BK, B.BD; W, H = B.W, B.H
    tt = min(t, M.t_end); rem = M.remaining(t); lost = M.blood_lost(t); br = max(0.0, 1 - lost / MM.BLOOD); bites = M.bites(t)
    if W > H:
        d.rectangle((0, 0, W, 132), fill=(8, 10, 16, 215))
        d.text((40, 30), '蚊（ヤブカなど）', font=Fo(BK, 30), fill=MOS_C, anchor='lm')
        d.text((40, 92), f'{int(rem):,}', font=BE(84), fill=B.PALE, anchor='lm')
        bw = 360; x0 = 400
        d.rounded_rectangle((x0, 76, x0 + bw, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x0, 76, x0 + max(8, bw * rem / M.n), 104), 8, fill=MOS_C)
        d.text((x0, 52), f'残っている蚊 / {int(M.n):,}匹', font=Fo(BD, 22), fill=(200, 200, 205), anchor='lm')
        d.text((W - 40, 30), '人間の血液', font=Fo(BK, 30), fill=BLOOD_C, anchor='rm')
        d.text((W - 40, 92), f'{(MM.BLOOD - lost) / 1000:.2f}L', font=BE(84), fill=B.PALE, anchor='rm')
        bw = 420; x1 = W - 260
        d.rounded_rectangle((x1 - bw, 76, x1, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x1 - max(8, bw * br), 76, x1, 104), 8, fill=BLOOD_C)
        xd = x1 - bw * (1 - MM.DANGER); d.line((xd, 68, xd, 112), fill=(255, 220, 90), width=4); d.text((xd, 122), '危険ライン（3割）', font=Fo(BD, 18), fill=(255, 220, 90), anchor='mm')
        d.text((W / 2, 34), hud.get('round', ''), font=Fo(BK, 32), fill=(255, 210, 80), anchor='mm')
        d.text((W / 2, 86), fmt_t(tt), font=BE(60), fill=B.PALE, anchor='mm')
        d.text((W / 2, 122), f'刺された回数  {int(bites):,}回', font=Fo(BD, 20), fill=(200, 200, 205), anchor='mm')
        sp = hud.get('speed', 1.0)
        if sp and sp != 1.0:
            tag = 'スロー' if sp < 1 else f'×{sp:,.0f} 早送り'; tw = Fo(BK, 24).getlength(tag) + 50
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
        d.text((60, 150), '刺された回数', font=Fo(BK, 36), fill=MOS_C, anchor='lm'); d.text((60, 225), f'{int(bites):,}', font=BE(92), fill=B.PALE, anchor='lm')
        d.text((W - 60, 150), '人間の血液', font=Fo(BK, 36), fill=BLOOD_C, anchor='rm'); d.text((W - 60, 225), f'{(MM.BLOOD - lost) / 1000:.2f}L', font=BE(92), fill=B.PALE, anchor='rm')
        x0, x1 = W / 2 + 20, W - 60
        d.rounded_rectangle((x0, 285, x1, 307), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x1 - max(6, (x1 - x0) * br), 285, x1, 307), 8, fill=BLOOD_C)
        xd = x1 - (x1 - x0) * (1 - MM.DANGER); d.line((xd, 278, xd, 314), fill=(255, 220, 90), width=4)
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
