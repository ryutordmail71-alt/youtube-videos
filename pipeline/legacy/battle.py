"""シミュレーション結果を、俯瞰の戦場アニメーションとして描画する"""
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H, FPS = 1920, 1080, 30
NF = '/usr/share/fonts/opentype/noto/'; FD = '/home/claude/fonts/'
def Fo(n, s): return ImageFont.truetype(NF + n, s, index=0)
BK, BD = 'NotoSansCJK-Black.ttc', 'NotoSansCJK-Bold.ttc'
BEBAS = FD + 'BebasNeue-Regular.ttf'
BEAR_C = (235, 150, 70); HIP_C = (150, 160, 235); PALE = (240, 236, 226)

# ---------- 地面テクスチャ（世界座標 4px/m） ----------
GX0, GY0, GX1, GY1, GPPM = -120, -80, 380, 280, 4
def make_ground():
    w, h = (GX1 - GX0) * GPPM, (GY1 - GY0) * GPPM
    rng = np.random.default_rng(3)
    base = np.zeros((h, w, 3), np.float32)
    def noise(sc, amp):
        n = rng.normal(0, 1, (h // sc + 2, w // sc + 2)).astype(np.float32)
        im = Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        return (np.asarray(im, np.float32) / 255 - 0.5) * amp
    n = noise(80, 1.0) + noise(20, 0.5) + noise(4, 0.35)
    g1 = np.array([120, 128, 66], np.float32); g2 = np.array([166, 150, 86], np.float32)  # 乾いた草原
    u = np.clip(0.5 + n * 0.7, 0, 1)[..., None]
    base = g1 * (1 - u) + g2 * u
    base += noise(2, 18)[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    return im
GROUND = None

# ---------- スプライト ----------
def _load(p, warm=1.0):
    im = Image.open(p).convert('RGBA')
    if warm != 1.0:
        rgb = ImageEnhance.Color(im.convert('RGB')).enhance(warm); a = im.split()[3]; im = rgb.convert('RGBA'); im.putalpha(a)
    return im
SRC = None
def src():
    global SRC
    if SRC is None:
        b = _load('/home/claude/bvh/cut_bside.png')          # 右向き
        h = _load('/home/claude/bvh/cut_hside.png', 0.55)    # 左向き（色味を自然に）
        h = ImageEnhance.Brightness(h).enhance(0.85)
        hm = _load('/home/claude/bvh/cut_hmouth.png', 0.9)   # 左向き・口を開けた
        SRC = dict(bear=b, hippo=h.transpose(Image.FLIP_LEFT_RIGHT), hippo_atk=hm.transpose(Image.FLIP_LEFT_RIGHT))
    return SRC
VIS_LEN = {0: 3.4, 1: 5.4}   # 見た目の体長（m）
SP = {}
def sprite(kind, state, wpx, flip):
    wpx = max(6, int(wpx))
    k = (kind, state, wpx, flip)
    if k in SP: return SP[k]
    S = src()
    if kind == 0:
        base = S['bear']
        if state == 'atk': base = base.rotate(14, resample=Image.BICUBIC, expand=True)  # 立ち上がって爪をふるう
    else:
        base = S['hippo_atk'] if state == 'atk' else S['hippo']
    ww = wpx if state != 'atk' or kind == 0 else int(wpx * 1.05)
    im = base.resize((ww, max(4, int(base.height * ww / base.width))), Image.BILINEAR)
    if state == 'hit':
        rgb = ImageEnhance.Brightness(im.convert('RGB')).enhance(1.8); a = im.split()[3]; im = rgb.convert('RGBA'); im.putalpha(a)
    if state == 'dead':
        im = im.rotate(180 if kind == 0 else 175, resample=Image.BICUBIC, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        im = im.resize((im.width, max(3, int(im.height * 0.55))))
        rgb = ImageEnhance.Brightness(ImageEnhance.Color(im.convert('RGB')).enhance(0.3)).enhance(0.55); a = im.split()[3].point(lambda v: int(v * 0.75)); im = rgb.convert('RGBA'); im.putalpha(a)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    SP[k] = im; return im
SHADOW = {}
def shadow(wpx):
    wpx = max(6, int(wpx))
    if wpx not in SHADOW:
        s = Image.new('RGBA', (wpx, max(3, wpx // 4)), (0, 0, 0, 0)); ImageDraw.Draw(s).ellipse((0, 0, wpx - 1, max(2, wpx // 4) - 1), fill=(0, 0, 0, 70))
        SHADOW[wpx] = s
    return SHADOW[wpx]

def lerp(a, b, u): return a + (b - a) * u
def ease(u): return u * u * (3 - 2 * u)

class Round:
    def __init__(self, tag):
        z = np.load(f'/home/claude/bvh/sim_{tag}.npz'); self.pos = z['pos']; self.face = z['face']; self.hp = z['hp']; self.side = z['side']
        self.death = z['death_t']; self.atk = z['atk']; self.nf = len(self.pos)
        L = json.load(open(f'/home/claude/bvh/sim_{tag}.json')); self.log = L; self.ev = L['events']
        self.NB = int((self.side == 0).sum()); self.NH = int((self.side == 1).sum())
        self.evt = np.array([e[0] for e in self.ev]) if self.ev else np.zeros(0)
    def frame_idx(self, st): return int(min(self.nf - 1, max(0, round(st * FPS) - 1)))

def project(x, y, cam):
    cx, cy, ppm = cam
    return W / 2 + (x - cx) * ppm, H / 2 + 40 + (y - cy) * ppm * 0.55

def draw_ground(cam):
    global GROUND
    if GROUND is None: GROUND = make_ground()
    cx, cy, ppm = cam
    # 出力(sx,sy) -> 世界(x,y) -> テクスチャ(u,v)
    # x = cx + (sx - W/2)/ppm ; y = cy + (sy - H/2 - 40)/(ppm*0.55)
    a = GPPM / ppm; c = (cx - W / 2 / ppm - GX0) * GPPM
    e = GPPM / (ppm * 0.55); f = (cy - (H / 2 + 40) / (ppm * 0.55) - GY0) * GPPM
    return GROUND.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, f), resample=Image.BILINEAR)

def render_frame(R, st, cam, hud):
    i = R.frame_idx(st)
    im = draw_ground(cam).convert('RGBA')
    pos = R.pos[i]; face = R.face[i]; hp = R.hp[i]; atk = R.atk[i]
    prev_hp = R.hp[max(0, i - 4)]
    cx, cy, ppm = cam
    sx, sy = project(pos[:, 0], pos[:, 1], cam)
    persp = 0.85 + 0.3 * (pos[:, 1] / 200.0)
    vis = (sx > -80) & (sx < W + 80) & (sy > -80) & (sy < H + 80)
    dead = (R.death >= 0) & (R.death <= st)
    order = np.argsort(sy + np.where(dead, -2000, 0))  # 死体を先に（下に）描く
    bob_t = st * 9
    for k in order:
        if not vis[k]: continue
        kind = int(R.side[k]); wpx = VIS_LEN[kind] * ppm * persp[k]
        if dead[k]:
            age = st - R.death[k]
            spr = sprite(kind, 'dead', wpx, face[k] < 0 if kind == 0 else face[k] > 0)
            im.alpha_composite(spr, (int(sx[k] - spr.width / 2), int(sy[k] - spr.height * 0.7)))
            continue
        state = 'atk' if atk[k] else ('hit' if hp[k] < prev_hp[k] else 'walk')
        flip = (face[k] < 0) if kind == 0 else (face[k] > 0)
        spr = sprite(kind, state, wpx, flip)
        bob = 0 if state != 'walk' else abs(math.sin(bob_t + k)) * wpx * 0.04
        sh = shadow(wpx * 0.9); im.alpha_composite(sh, (int(sx[k] - sh.width / 2), int(sy[k] - sh.height / 2)))
        lunge = (wpx * 0.12 * (face[k])) if state == 'atk' else 0
        im.alpha_composite(spr, (int(sx[k] - spr.width / 2 + lunge), int(sy[k] - spr.height * 0.92 - bob)))
    # 土ぼこり
    d = ImageDraw.Draw(im, 'RGBA')
    if len(R.evt):
        lo, hi = np.searchsorted(R.evt, st - 0.45), np.searchsorted(R.evt, st)
        for e in R.ev[lo:hi]:
            age = (st - e[0]) / 0.45; ex, ey = project(e[2], e[3], cam)
            rr = (0.6 + 1.8 * age) * ppm * (1.2 if e[1] == 'die' else 0.8)
            a = int(150 * (1 - age))
            d.ellipse((ex - rr, ey - rr * 0.6 - ppm, ex + rr, ey + rr * 0.6 - ppm), fill=(205, 190, 150, a))
    hud_draw(im, R, i, st, hud)
    return im.convert('RGB')

def hud_draw(im, R, i, st, hud):
    d = ImageDraw.Draw(im, 'RGBA')
    alive = ~((R.death >= 0) & (R.death <= st))
    nb = int(alive[:R.NB].sum()); nh = int(alive[R.NB:].sum())
    d.rectangle((0, 0, W, 132), fill=(8, 10, 16, 215))
    # 左：熊
    d.text((40, 30), '熊（グリズリー）', font=Fo(BK, 30), fill=BEAR_C, anchor='lm')
    d.text((40, 92), f'{nb:,}', font=ImageFont.truetype(BEBAS, 84), fill=PALE, anchor='lm')
    bw = 560; d.rounded_rectangle((300, 76, 300 + bw, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((300, 76, 300 + max(8, bw * nb / R.NB), 104), 8, fill=BEAR_C)
    d.text((300, 52), f'/ {R.NB:,}体', font=Fo(BD, 24), fill=(200, 200, 205), anchor='lm')
    # 右：カバ
    d.text((W - 40, 30), 'カバ', font=Fo(BK, 30), fill=HIP_C, anchor='rm')
    d.text((W - 40, 92), f'{nh:,}', font=ImageFont.truetype(BEBAS, 84), fill=PALE, anchor='rm')
    d.rounded_rectangle((W - 300 - bw, 76, W - 300, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((W - 300 - max(8, bw * nh / R.NH), 76, W - 300, 104), 8, fill=HIP_C)
    d.text((W - 300, 52), f'/ {R.NH:,}体', font=Fo(BD, 24), fill=(200, 200, 205), anchor='rm')
    # 中央
    d.text((W / 2, 40), hud['round'], font=Fo(BK, 34), fill=(255, 210, 80), anchor='mm')
    m, s = divmod(max(0, st - 2.0), 60)
    d.text((W / 2, 94), f'{int(m):02d}:{s:04.1f}', font=ImageFont.truetype(BEBAS, 56), fill=PALE, anchor='mm')
    if hud.get('speed') and hud['speed'] != 1.0:
        tag = 'スロー' if hud['speed'] < 1 else f'×{hud["speed"]:.0f} 早送り'
        d.rounded_rectangle((W / 2 + 110, 76, W / 2 + 290, 112), 8, fill=(200, 60, 60, 220)); d.text((W / 2 + 200, 94), tag, font=Fo(BK, 24), fill=(255, 255, 255), anchor='mm')
    d.text((W - 24, H - 22), '※実データをもとにした、単純化したシミュレーションです', font=Fo(BD, 20), fill=(235, 235, 235, 200), anchor='rs')
    cap = hud.get('cap')
    if cap:
        f = Fo(BK, 52); tw = f.getlength(cap)
        d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 210))
        d.text((W / 2, H - 125), cap, font=f, fill=PALE, anchor='mm')

def centroid(R, st, which='fight'):
    i = R.frame_idx(st); alive = ~((R.death >= 0) & (R.death <= st))
    m = alive & R.atk[i] if which == 'fight' else alive
    if m.sum() < 5: m = alive
    p = R.pos[i][m]
    return float(np.median(p[:, 0])), float(np.median(p[:, 1]))
