"""熊 vs 鮭：川のシミュレーション結果を描画する（battle.py のカメラ・空・仕上げを流用）"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from scipy import ndimage as nd
import battle as B
from rsim import RY0, RY1, BX0, BX1, GOAL, FPS

PALE = B.PALE; BEAR_C = (235, 150, 70); SAL_C = (240, 92, 84); GOLD = (255, 210, 80)
GX0, GY0, GX1, GY1, GPPM = B.GX0, B.GY0, B.GX1, B.GY1, B.GPPM

class RRound:
    def __init__(self, tag):
        z = np.load(f'/home/claude/bvs/rsim_{tag}.npz')
        self.pos = z['pos'].astype(np.float32); self.st = z['st']; self.face = z['face']; self.nf = len(self.pos)
        for k in ('t0', 'ly', 'v', 'wa', 'wf', 'wp', 'x0', 's_end', 's_res', 's_by', 'cap'): setattr(self, k, z[k])
        self.J = json.load(open(f'/home/claude/bvs/rsim_{tag}.json')); self.NS = len(self.t0); self.NB = self.pos.shape[1]
        rng = np.random.default_rng(5)
        self.var = dict(v=rng.integers(0, 1000, self.NB), sc=rng.uniform(0.86, 1.16, self.NB), br=rng.integers(0, 3, self.NB), ph=rng.uniform(0, 6.28, self.NB))
        self.fsc = rng.uniform(0.85, 1.15, self.NS).astype(np.float32); self.fcol = rng.integers(0, 3, self.NS)
        # 食べられた鮭の位置（しぶき用）
        e = np.where(self.s_res == 1)[0]; self.eat_t = self.s_end[e]; o = np.argsort(self.eat_t); self.eat_i = e[o]; self.eat_t = self.eat_t[o]
        self.eat_xy = self.spos(self.eat_i, self.eat_t)
        # ジャンプする鮭（一部）
        self.leap = np.where((np.arange(self.NS) * 7919 % 53) == 0)[0]
        # 累積カウント用
        g = np.where(self.s_res == 2)[0]; self.goal_t = np.sort(self.s_end[g])
    def frame_idx(self, st): return int(min(self.nf - 1, max(0, round(st * FPS) - 1)))
    def spos(self, idx, t):
        dt = t - self.t0[idx]
        return np.stack([self.x0[idx] - self.v[idx] * dt, self.ly[idx] + self.wa[idx] * np.sin(self.wf[idx] * dt + self.wp[idx])], 1)
    def counts(self, st):
        ne = int(np.searchsorted(self.eat_t, st, 'right')); ng = int(np.searchsorted(self.goal_t, st, 'right'))
        i = self.frame_idx(st); full = int((self.st[i] >= 3).sum())
        return ne, ng, full

# ---------------- 地面（草＋砂利の岸）と水面 ----------------
GROUND = None
def make_ground():
    g = np.asarray(B.make_ground(), np.float32).copy()
    h, w = g.shape[:2]; rng = np.random.default_rng(21)
    yy = (np.arange(h) / GPPM + GY0)[:, None]
    n = nd.gaussian_filter(rng.normal(0, 1, (h // 3, w // 3)), 1.0); n = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((w, h)), np.float32) / 255
    edge = nd.gaussian_filter(rng.normal(0, 1, (1, w)), (0, 40))[0] * 40
    for y0, sgn in ((RY0, -1), (RY1, 1)):
        d = (yy - y0) * sgn + edge[None, :] * 0.05            # 岸からの距離（川の外向き）
        grav = np.clip(1 - (d - 2.5) / 3.0, 0, 1) * (d > -1)
        col = np.array([150, 140, 122], np.float32) * (0.75 + 0.5 * n[..., None])
        wet = np.clip(1 - d / 1.4, 0, 1)[..., None] * 0.45
        col = col * (1 - wet)
        g = g * (1 - grav[..., None]) + col * grav[..., None]
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
WATER = None; WMASK = None; WP = 120   # 水のテクスチャは x 方向に周期 WP(m)
def make_water():
    rng = np.random.default_rng(31); w = (GX1 - GX0 + WP) * GPPM; y0, y1 = RY0 - 4, RY1 + 4; h = int((y1 - y0) * GPPM)
    def per_noise(sx, sy, amp, seed):
        r = np.random.default_rng(seed); px = WP * GPPM
        n = r.normal(0, 1, (max(2, h // sy), max(2, px // sx)))
        n = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((px, h), Image.BICUBIC), np.float32) / 255
        n = np.tile(n, (1, w // px + 1))[:, :w]
        return (n - 0.5) * amp
    st = per_noise(48, 3, 1.0, 1) + per_noise(12, 2, 0.6, 2)      # 流れに沿った筋
    big = per_noise(240, 60, 1.0, 3)
    base = np.array([62, 84, 86], np.float32); hi = np.array([150, 170, 172], np.float32); deep = np.array([40, 58, 62], np.float32)
    yy = np.linspace(0, 1, h)[:, None, None]
    col = base * (1 - np.clip(big[..., None], 0, 1)) + deep * np.clip(big[..., None], 0, 1)
    spec = np.clip((st - 0.25) * 2.2, 0, 1)[..., None] * 0.55
    col = col * (1 - spec) + hi * spec
    # 浅瀬（岸近く）は明るく
    sh = np.clip(1 - np.minimum(np.abs(yy - 4 / (y1 - y0)), np.abs(yy - (1 - 4 / (y1 - y0)))) * 9, 0, 1) * 0.35
    col = col * (1 - sh) + np.array([120, 118, 100], np.float32) * sh
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    # 世界座標の大きな画像にのせる（周期分だけ x を余分に）
    full = Image.new('RGB', (w, (GY1 - GY0) * GPPM), (60, 80, 84)); full.paste(img, (0, int((y0 - GY0) * GPPM)))
    m = Image.new('L', ((GX1 - GX0) * GPPM, (GY1 - GY0) * GPPM), 0); md = ImageDraw.Draw(m)
    ew = nd.gaussian_filter(rng.normal(0, 1, (GX1 - GX0) * GPPM), 30) * 30
    xs = np.arange(0, (GX1 - GX0) * GPPM, 6)
    top = [(int(x), int((RY0 - GY0) * GPPM + ew[x] * 1.5)) for x in xs]; bot = [(int(x), int((RY1 - GY0) * GPPM - ew[x] * 1.5)) for x in xs]
    md.polygon(top + bot[::-1], fill=255); m = m.filter(ImageFilter.GaussianBlur(2))
    return full, m
def draw_ground(cam, st):
    global GROUND, WATER, WMASK
    if GROUND is None: GROUND = make_ground(); WATER, WMASK = make_water()
    cx, camY, camH, hz = B.cam_params(cam)
    g = GROUND.transform((B.W, B.H), Image.PERSPECTIVE, B._persp(cam, GPPM, GX0, GY0), resample=Image.BILINEAR, fillcolor=(150, 140, 100))
    shift = (st * 0.9) % WP     # 流れ（右へ）
    wtr = WATER.transform((B.W, B.H), Image.PERSPECTIVE, B._persp(cam, GPPM, GX0 - WP + shift, GY0), resample=Image.BILINEAR, fillcolor=(60, 80, 84))
    m = WMASK.transform((B.W, B.H), Image.PERSPECTIVE, B._persp(cam, GPPM, GX0, GY0), resample=Image.BILINEAR)
    # 空の映り込み（遠いほど明るい）
    yy = np.arange(B.H, dtype=np.float32); refl = np.clip(1 - (yy - hz) / (B.H * 0.5), 0, 1) ** 2 * 0.45
    wtr = Image.composite(Image.new('RGB', (B.W, B.H), (190, 205, 215)), wtr, Image.fromarray(np.repeat((refl * 255).astype(np.uint8)[:, None], B.W, axis=1)))
    g = Image.composite(wtr, g, m)
    s = B.sky(hz); g.paste(s.crop((0, 0, B.W, int(hz) + 2)), (0, 0))
    dist = np.where(yy > hz + 1, camH * B.FOC / np.maximum(yy - hz, 1), 1e4)
    fog = np.clip((dist - 140) / 380, 0, 1) ** 0.8; fog[yy <= hz + 1] = 0
    g = Image.composite(Image.new('RGB', (B.W, B.H), (214, 208, 188)), g, Image.fromarray(np.repeat((fog * 235).astype(np.uint8)[:, None], B.W, axis=1)))
    return g, m

# ---------------- スプライト ----------------
_BS = {}
def base(name):
    if name not in _BS:
        im = Image.open(f'/home/claude/bvs/spr_{name}.png').convert('RGBA'); s = 240 / im.height
        _BS[name] = im.resize((int(im.width * s), 240), Image.LANCZOS)
    return _BS[name]
SPC = {}
def spr(name, wq, flip, br, crop=0.0, rot=0, squash=1.0):
    k = (name, wq, flip, br, round(crop, 2), rot, squash)
    if k in SPC: return SPC[k]
    b = base(name)
    if rot: b = b.rotate(rot, resample=Image.BICUBIC, expand=True)
    hh = max(3, int(b.height * wq / b.width * squash)); im = b.resize((wq, hh), Image.BILINEAR)
    if crop > 0: im = im.crop((0, 0, wq, max(2, int(hh * (1 - crop)))))
    f = (0.84, 0.96, 1.08)[br]
    if f != 1: a = im.split()[3]; im = ImageEnhance.Brightness(im.convert('RGB')).enhance(f).convert('RGBA'); im.putalpha(a)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    SPC[k] = im
    if len(SPC) > 8000: SPC.clear()
    return im
FISH = {}
def fish_spr(wq, col, alpha, flip=False, rot=0):
    k = (wq, col, alpha, flip, rot)
    if k not in FISH:
        b = base('SAL')
        if rot: b = b.rotate(rot, resample=Image.BICUBIC, expand=True)
        im = b.resize((wq, max(2, int(b.height * wq / b.width))), Image.BILINEAR)
        rgb = im.convert('RGB'); rgb = ImageEnhance.Brightness(rgb).enhance((0.62, 0.72, 0.82)[col] if alpha < 255 else 1.0)
        if alpha < 255: rgb = Image.blend(rgb, Image.new('RGB', rgb.size, (60, 84, 92)), 0.28)
        a = im.split()[3].point(lambda v, al=alpha: v * al // 255); im = rgb.convert('RGBA'); im.putalpha(a)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        FISH[k] = im
        if len(FISH) > 4000: FISH.clear()
    return FISH[k]
RIP = {}
def ripple(wq):
    wq = max(6, wq)
    if wq not in RIP:
        hh = max(3, wq // 5); s = Image.new('L', (wq + 8, hh + 8), 0); d = ImageDraw.Draw(s)
        d.ellipse((4, 4, 4 + wq, 4 + hh), outline=170, width=max(1, wq // 30)); d.ellipse((4 + wq * 0.12, 4 + hh * 0.2, 4 + wq * 0.88, 4 + hh * 0.8), outline=90, width=1)
        s = s.filter(ImageFilter.GaussianBlur(max(0.6, wq / 60))); im = Image.new('RGBA', s.size, (225, 235, 238, 0)); im.putalpha(s); RIP[wq] = im
    return RIP[wq]

VIS_BEAR = 2.7; VIS_FISH = 0.62
def render_frame(R, st, cam, hud):
    W, H = B.W, B.H
    i = R.frame_idx(st); V = R.var
    cx, camY, camH, hz = B.cam_params(cam)
    g, wmask = draw_ground(cam, st); im = g.convert('RGBA')
    # ---- 鮭（水中） ----
    act = np.where((R.t0 <= st) & ((R.s_res == 2) | (R.s_end > st)))[0]
    if len(act):
        p = R.spos(act, st); ok = p[:, 0] > GOAL - 70; act = act[ok]; p = p[ok]
    if len(act):
        sx, sy = B.project(p[:, 0], p[:, 1], cam); sc = B.depth_scale(p[:, 1], cam)
        vis = (p[:, 1] - camY > 2) & (sx > -40) & (sx < W + 40) & (sy > hz) & (sy < H + 20)
        act, sx, sy, sc, p = act[vis], sx[vis], sy[vis], sc[vis], p[vis]
        L = VIS_FISH * sc * R.fsc[act]
        small = L < 5
        # 小さい鮭は点で（numpy で直接塗る）
        if small.any():
            arr = np.asarray(im).copy()
            xs = sx[small].astype(int); ys = sy[small].astype(int); ll = np.maximum(1, L[small].astype(int))
            colr = np.array([[150, 52, 50], [170, 62, 56], [128, 46, 46]], np.uint8)[R.fcol[act[small]]]
            for dx in range(0, 5):
                m = dx < ll; xx = np.clip(xs[m] - dx + 2, 0, W - 1); yy = np.clip(ys[m], 0, H - 1)
                arr[yy, xx, :3] = (arr[yy, xx, :3] * 0.35 + colr[m] * 0.65).astype(np.uint8)
            im = Image.fromarray(arr)
        for k in np.where(~small)[0][np.argsort(p[~small, 1])[::-1]]:
            wq = B._q(L[k]); f = fish_spr(wq, int(R.fcol[act[k]]), 205)
            wob = int(math.sin(st * 9 + act[k]) * wq * 0.03)
            im.alpha_composite(f, (int(sx[k] - f.width / 2), int(sy[k] - f.height * 0.55 + wob)))
    # ---- 熊 ----
    pos = R.pos[i]; stt = R.st[i]; face = R.face[i]; pp = R.pos[max(0, i - 2)]
    bx, by = B.project(pos[:, 0], pos[:, 1], cam); bsc = B.depth_scale(pos[:, 1], cam)
    vis = (pos[:, 1] - camY > 2) & (bx > -200) & (bx < W + 200) & (by > hz - 5) & (by < H + 400)
    moving = np.linalg.norm(pos - pp, axis=1) > 0.04
    inwater = (pos[:, 1] > RY0 - 0.5) & (pos[:, 1] < RY1 + 0.5)
    order = sorted(np.where(vis)[0], key=lambda k: -pos[k, 1])
    # 食べている熊が持つ鮭の向き
    for k in order:
        wpx = VIS_BEAR * bsc[k] * V['sc'][k]
        if wpx < 3: continue
        flip = face[k] < 0; s = int(stt[k]); br = int(V['br'][k]); v = int(V['v'][k])
        crop = 0.26 if inwater[k] else 0.0
        if s == 1:
            o = spr('BATK', B._q(wpx * 1.12), flip, br, crop * 0.6); y0 = by[k] - o.height - (0 if crop else -o.height * 0.05) + o.height * 0.02
        elif s == 2:
            o = spr('BEAT', B._q(wpx * 0.92), flip, br, crop); y0 = by[k] - o.height
        elif s == 4:
            o = spr(B.BEAR_V[v % len(B.BEAR_V)], B._q(wpx), flip, br, 0.0, rot=(-8 if not flip else 8), squash=0.62); y0 = by[k] - o.height * 0.85
        else:
            if crop == 0 and wpx >= 6:
                sh = B.shadow3(wpx); im.alpha_composite(sh, (int(bx[k] - sh.width * 0.42), int(by[k] - sh.height * 0.5)))
            ph = int(st * 6 + V['ph'][k]) if moving[k] else 0
            o = B.gait_sprite(0, v, wpx, flip, br, 'walk', ph)
            if crop: o = o.crop((0, 0, o.width, max(2, int(o.height * (1 - crop)))))
            y0 = by[k] - (o.height if crop else o.height * 0.93)
        im.alpha_composite(o, (int(bx[k] - o.width / 2), int(y0)))
        if crop and wpx >= 8:
            r = ripple(B._q(wpx * (1.15 if s != 1 else 1.4))); im.alpha_composite(r, (int(bx[k] - r.width / 2), int(by[k] - r.height * 0.6)))
    # ---- しぶき（鮭を捕まえた瞬間）＋ジャンプする鮭 ----
    sp = Image.new('L', (W // 2, H // 2), 0); sd = ImageDraw.Draw(sp)
    lo, hi = np.searchsorted(R.eat_t, st - 0.7), np.searchsorted(R.eat_t, st)
    rng = np.random.default_rng(int(st * 30))
    for j in range(lo, hi):
        ex, ey = R.eat_xy[j]; age = (st - R.eat_t[j]) / 0.7
        if ey - camY < 2: continue
        X, Y = B.project(ex, ey, cam); s1 = float(B.depth_scale(ey, cam))
        if not (-50 < X < W + 50): continue
        for q in range(4 if s1 > 6 else 1):
            ang = rng.uniform(0, math.pi); rr = s1 * (0.3 + 1.2 * age) * rng.uniform(0.5, 1.0)
            px = X + math.cos(ang) * rr; py = Y - math.sin(ang) * rr * 0.9 - s1 * 0.4
            r0 = max(0.6, s1 * 0.12 * (1 - age))
            sd.ellipse(((px - r0) / 2, (py - r0) / 2, (px + r0) / 2, (py + r0) / 2), fill=int(230 * (1 - age)))
    lp = R.leap
    if len(lp):
        tj = R.t0[lp] + (R.x0[lp] - 150 - (lp % 13)) / R.v[lp]           # ジャンプ開始時刻
        on = (st >= tj) & (st < tj + 0.75) & ((R.s_res[lp] == 2) | (R.s_end[lp] > tj + 0.75))
        for k, t1 in zip(lp[on], tj[on]):
            u = (st - t1) / 0.75; x, y = R.spos(np.array([k]), st)[0]
            if y - camY < 2: continue
            X, Y = B.project(x, y, cam); s1 = float(B.depth_scale(y, cam))
            if not (-50 < X < W + 50): continue
            Yj = Y - s1 * 1.3 * 4 * u * (1 - u)
            wq = B._q(VIS_FISH * s1 * 1.05)
            if wq >= 4:
                f = fish_spr(wq, 1, 255, False, int((0.5 - u) * 60))
                im.alpha_composite(f, (int(X - f.width / 2), int(Yj - f.height / 2)))
            r0 = s1 * 0.35
            for xx in (X - s1 * 0.3, X + s1 * 0.3):
                if u < 0.25 or u > 0.8: sd.ellipse(((xx - r0) / 2, (Y - r0 * 0.5) / 2, (xx + r0) / 2, (Y + r0 * 0.3) / 2), fill=150)
    sp = sp.filter(ImageFilter.GaussianBlur(0.8)).resize((W, H), Image.BILINEAR)
    wl = Image.new('RGBA', (W, H), (245, 250, 252, 0)); wl.putalpha(sp); im.alpha_composite(wl)
    img = im.convert('RGB')
    fy = H * 0.62; yy = np.arange(H, dtype=np.float32)
    far = np.clip((fy - 90 - yy) / (fy - 90 - hz), 0, 1); near = np.clip((yy - fy - 160) / (H - fy - 160), 0, 1)
    bm = np.clip(np.maximum(far, near) * 1.2, 0, 1)
    if bm.max() > 0:
        bl = img.filter(ImageFilter.GaussianBlur(2.6)); img = Image.composite(bl, img, Image.fromarray(np.repeat((bm * 255).astype(np.uint8)[:, None], W, axis=1)))
    img = B.finish(img, 0.0)
    hud_draw(img, R, i, st, hud)
    return img

def hud_draw(im, R, i, st, hud):
    W, H = B.W, B.H; d = ImageDraw.Draw(im, 'RGBA'); Fo, BK, BD = B.Fo, B.BK, B.BD; BE = lambda s: ImageFont.truetype(B.BEBAS, s)
    ne, ng, full = R.counts(st)
    d.rectangle((0, 0, W, 150), fill=(8, 10, 16, 215))
    d.text((40, 30), '熊に食べられた鮭', font=Fo(BK, 28), fill=BEAR_C, anchor='lm'); d.text((40, 96), f'{ne:,}', font=BE(84), fill=PALE, anchor='lm')
    d.text((40, 136), f'満腹になった熊  {full:,} / {R.NB:,}体', font=Fo(BD, 20), fill=(205, 205, 210), anchor='lm')
    d.text((W - 40, 30), '上流にたどり着いた鮭', font=Fo(BK, 28), fill=SAL_C, anchor='rm'); d.text((W - 40, 96), f'{ng:,}', font=BE(84), fill=PALE, anchor='rm')
    d.text((W - 40, 136), f'鮭  全{R.NS:,}匹', font=Fo(BD, 20), fill=(205, 205, 210), anchor='rm')
    d.text((W / 2, 30), hud.get('round', ''), font=Fo(BK, 32), fill=GOLD, anchor='mm')
    # 到達率バー（50%で鮭の勝ち）
    bx0, bx1 = W / 2 - 330, W / 2 + 330; rate = ng / R.NS; eat = ne / R.NS
    d.rounded_rectangle((bx0, 70, bx1, 98), 8, fill=(255, 255, 255, 40))
    if eat > 0: d.rounded_rectangle((bx0, 70, bx0 + max(10, (bx1 - bx0) * eat), 98), 8, fill=BEAR_C)
    if rate > 0: d.rounded_rectangle((bx1 - max(10, (bx1 - bx0) * rate), 70, bx1, 98), 8, fill=SAL_C)
    d.line((W / 2, 62, W / 2, 106), fill=(255, 255, 255), width=3)
    d.text((W / 2, 126), f'鮭のゴール率 {rate * 100:4.1f}%　（50%以上で鮭の勝ち）', font=Fo(BD, 22), fill=PALE, anchor='mm')
    sp = hud.get('speed', 1.0)
    if sp != 1.0:
        tag = 'スロー' if sp < 1 else f'×{sp:.0f} 早送り'
        d.rounded_rectangle((W / 2 - 90, 160, W / 2 + 90, 198), 8, fill=(200, 60, 60, 225)); d.text((W / 2, 179), tag, font=Fo(BK, 24), fill=(255, 255, 255), anchor='mm')
    m, s = divmod(st, 60); d.text((W / 2 + 470, 96), f'{int(m):02d}:{s:04.1f}', font=BE(46), fill=(220, 220, 225), anchor='mm')
    d.text((W - 24, H - 22), '※実データをもとにした、単純化したシミュレーションです（時間は大きく縮めています）', font=Fo(BD, 20), fill=(235, 235, 235, 200), anchor='rs')
    cap = hud.get('cap')
    if cap:
        f = Fo(BK, 52); tw = f.getlength(cap)
        d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 210))
        d.text((W / 2, H - 125), cap, font=f, fill=hud.get('capcol', PALE), anchor='mm')
B.hud_draw = hud_draw

def focus(R, st, mode='hunt'):
    """カメラの注目点：飛びかかり・食べている熊の中央（いなければ熊エリア中央）"""
    i = R.frame_idx(st); m = (R.st[i] == 1) | (R.st[i] == 2)
    if m.sum() < 5: return (BX1 - 5, (RY0 + RY1) / 2)
    p = R.pos[i][m]; return float(np.median(p[:, 0])), float(np.median(p[:, 1]))
