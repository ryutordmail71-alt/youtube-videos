"""アリの群れの描画：地面のアリ（密度レイヤー）、ゾウの体にのぼったアリ、踏みつけの演出、HUD"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as nd
import battle as B
import asim as A

DT = A.DT; K = A.K; CAP = A.C['CAP']
ANT_C = (225, 95, 55); ELE_C = B.GOR_C
GX0, GY0, GW_, GH_, GP = 76.0, 80.0, 48.0, 40.0, 20     # アリ層の範囲（m）と解像度（1mあたりのセル数）

class ARound:
    """ゾウ1頭ぶんの Round 互換オブジェクト＋アリのシミュレーション再生"""
    def __init__(self, tag):
        L = json.load(open(f'/home/claude/ave/asim_{tag}.json')); self.res = L['res']; rec = np.array(L['rec'], np.float64)
        self.rec = rec; self.n = int(self.res['n']); self.seed = int(self.res['seed'])
        self.t = rec[:, 0]; self.alive = rec[:, 1]; self.onb = rec[:, 2]
        self.nf = len(rec)
        self.pos = np.zeros((self.nf, 1, 2), np.float32); self.pos[:, 0, 0] = rec[:, 4]; self.pos[:, 0, 1] = rec[:, 5]
        self.face = rec[:, 6].astype(np.int8)[:, None]; self.hp = rec[:, 3].astype(np.float32)[:, None]
        self.atk = (rec[:, 7] > 0.2)[:, None]
        self.side = np.ones(1, np.int8); self.death = np.full(1, -1.0, np.float32); self.NB = 0; self.NH = 1
        self.aev = L['ev']; ev = []
        for t, kind, x, y, k in L['ev']:
            if kind == 'stomp': ev.append([t, 'hit', x, y])
            elif kind == 'sweep': ev.append([t, 'hit', x, y])
            elif kind == 'dust':
                for a in np.linspace(0, 2 * np.pi, 7, endpoint=False): ev.append([t, 'die', x + math.cos(a) * 2.6, y + math.sin(a) * 1.2])
        self.ev = sorted(ev); self.evt = np.array([e[0] for e in self.ev]) if self.ev else np.zeros(0)
        self.stomps = [(t, x, y, k) for t, kind, x, y, k in L['ev'] if kind == 'stomp']
        self.stt = np.array([s[0] for s in self.stomps])
        self.dusts = [(t, x, y, k) for t, kind, x, y, k in L['ev'] if kind == 'dust']
        self.end = float(self.res['end']); self.win = self.res['win']
        self.sim = None
    def frame_idx(self, st): return int(min(self.nf - 1, max(0, round(st / DT) - 1)))
    def ants_at(self, st):
        if self.sim is None or self.sim.t > st + 1e-6: self.sim = A.AntSim(self.seed, self.n)
        while self.sim.t + DT <= st + 1e-6 and not (self.sim.done and self.sim.t > self.end + 4.5): self.sim.step()
        return self.sim

# ---------- 地面のアリ ----------
_GRAIN = np.random.default_rng(5).random((int(GH_ * GP), int(GW_ * GP))).astype(np.float32)
_SCR = {}
def screen_grain(k):
    key = (B.W, B.H, k % 4)
    if key not in _SCR:
        r = np.random.default_rng(100 + k % 4).random((B.H, B.W)).astype(np.float32)
        _SCR[key] = r
    return _SCR[key]
CUR = dict(R=None, st=0.0, cam=None, speed=1.0, f=0)
def ant_layer(R, st, cam):
    S = R.ants_at(st); g = S.st == 0
    x = S.x[g]; y = S.y[g]
    ix = ((x - GX0) * GP).astype(np.int32); iy = ((y - GY0) * GP).astype(np.int32)
    ok = (ix >= 0) & (ix < GW_ * GP) & (iy >= 0) & (iy < GH_ * GP)
    cnt = np.bincount(iy[ok] * int(GW_ * GP) + ix[ok], minlength=int(GW_ * GP * GH_ * GP)).reshape(int(GH_ * GP), int(GW_ * GP)).astype(np.float32)
    dens = cnt * K * GP * GP                       # 1m²あたりの匹数
    dens = nd.gaussian_filter(dens, 0.8)
    a = 1 - np.exp(-dens / 450.0)
    a = np.clip(a * (0.75 + 0.5 * _GRAIN), 0, 1)
    m = Image.fromarray((a * 255).astype(np.uint8))
    return m.transform((B.W, B.H), Image.PERSPECTIVE, B._persp(cam, GP, GX0, GY0), resample=Image.BILINEAR)
_draw_ground0 = B.draw_ground
def draw_ground(cam, R=None, i=None):
    g = _draw_ground0(cam, None, None)
    R = CUR['R']
    if R is None: return g
    m = ant_layer(R, CUR['st'], cam)
    ma = np.asarray(m, np.float32) / 255
    sg = screen_grain(CUR['f'])
    ma = np.clip(ma * (0.55 + 0.7 * sg), 0, 1)
    gi = np.asarray(g.convert('RGB'), np.float32)
    dark = np.array([46, 20, 12], np.float32); red = np.array([150, 52, 26], np.float32)
    col = dark + (red - dark) * (sg[..., None] > 0.86)
    out = gi * (1 - ma[..., None]) + col * ma[..., None]
    return Image.fromarray(out.astype(np.uint8))
B.draw_ground = draw_ground

# ---------- ゾウの体にのぼったアリ ----------
_gait0 = B.gait_sprite
_COV = {}
def gait_sprite(kind, v, wpx, flip, br, state, phase):
    im = _gait0(kind, v, wpx, flip, br, state, phase)
    R = CUR['R']
    if kind != 1 or R is None: return im
    cov = float(R.onb[R.frame_idx(CUR['st'])]) / CAP
    q = int(round(cov * 24))
    if q <= 0: return im
    key = (id(im), q, CUR['f'] % 3)
    if key in _COV: return _COV[key]
    a = np.asarray(im).copy(); h, w = a.shape[:2]
    rng = np.random.default_rng(q * 7 + CUR['f'] % 3)
    nz = rng.random((h, w)).astype(np.float32)
    nz = nd.gaussian_filter(nz, 0.7); nz = (nz - nz.min()) / (nz.max() - nz.min() + 1e-6)
    yf = (np.arange(h, dtype=np.float32) / h)[:, None]
    lvl = (q / 24) * 1.5 - (1 - yf) * 0.75             # 足もとから上へ広がる
    m = (nz < lvl) & (a[..., 3] > 30)
    a[m, 0] = (a[m, 0] * 0.15 + 40).astype(np.uint8); a[m, 1] = (a[m, 1] * 0.1 + 16).astype(np.uint8); a[m, 2] = (a[m, 2] * 0.1 + 10).astype(np.uint8)
    out = Image.fromarray(a); _COV[key] = out
    if len(_COV) > 3000: _COV.clear()
    return out
B.gait_sprite = gait_sprite

# ---------- 踏みつけの演出 ----------
def extra_hits(st):
    R = CUR['R']
    if R is None or CUR['speed'] > 2.5: return []
    lo, hi = np.searchsorted(R.stt, st - 0.35), np.searchsorted(R.stt, st)
    return [(st - R.stomps[j][0], np.array([R.stomps[j][1], R.stomps[j][2]]), 0.55) for j in range(lo, hi)]
def extra_lands(st):
    R = CUR['R']
    if R is None or CUR['speed'] > 6: return []
    lo, hi = np.searchsorted(R.stt, st - 0.9), np.searchsorted(R.stt, st)
    return [(st - R.stomps[j][0], np.array([R.stomps[j][1], R.stomps[j][2]])) for j in range(lo, hi)]
B.EXTRA_HITS = extra_hits; B.EXTRA_LANDS = extra_lands

# ---------- HUD ----------
def hud_draw(im, R, i, st, hud):
    d = ImageDraw.Draw(im, 'RGBA'); BE = lambda s: ImageFont.truetype(B.BEBAS, s); Fo = B.Fo; BK, BD = B.BK, B.BD; W, H = B.W, B.H
    if W > H:
        al = int(R.alive[i]); onb = int(R.onb[i]); hp = float(R.hp[i][0]) / 100
        d.rectangle((0, 0, W, 132), fill=(8, 10, 16, 215))
        d.text((40, 30), 'アリ（サスライアリ）', font=Fo(BK, 30), fill=ANT_C, anchor='lm')
        d.text((40, 92), f'{al:,}', font=BE(84), fill=B.PALE, anchor='lm')
        bw = 420; x0 = 380
        d.rounded_rectangle((x0, 76, x0 + bw, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x0, 76, x0 + max(8, bw * al / R.n), 104), 8, fill=ANT_C)
        d.text((x0, 52), f'まだ戦えるアリ / {R.n:,}匹', font=Fo(BD, 22), fill=(200, 200, 205), anchor='lm')
        d.text((x0, 120), f'ゾウの体にいるアリ  {onb:,}匹', font=Fo(BD, 20), fill=(255, 200, 150), anchor='lm')
        d.text((W - 40, 30), 'ゾウ（アフリカゾウ・オス）', font=Fo(BK, 30), fill=ELE_C, anchor='rm')
        d.text((W - 40, 92), f'{int(math.ceil(hp * 100 - 1e-6))}%', font=BE(84), fill=B.PALE, anchor='rm')
        bw = 420; x1 = W - 260
        d.rounded_rectangle((x1 - bw, 76, x1, 104), 8, fill=(255, 255, 255, 40)); d.rounded_rectangle((x1 - max(8, bw * hp), 76, x1, 104), 8, fill=ELE_C)
        d.text((x1, 120), 'ゾウのがまん（0で逃げ出す）', font=Fo(BD, 20), fill=(200, 200, 205), anchor='rm')
        d.text((W / 2, 36), hud.get('round', ''), font=Fo(BK, 32), fill=(255, 210, 80), anchor='mm')
        tt = min(st, R.end); m, s2 = divmod(tt, 60)
        d.text((W / 2, 88), f'{int(m):02d}:{int(s2):02d}', font=BE(60), fill=B.PALE, anchor='mm')
        d.text((W / 2, 122), '制限時間 10:00', font=Fo(BD, 18), fill=(200, 200, 205), anchor='mm')
        if hud.get('speed') and hud['speed'] != 1.0:
            tag = 'スロー' if hud['speed'] < 1 else f'×{hud["speed"]:.0f} 早送り'
            d.rounded_rectangle((W / 2 - 100, 142, W / 2 + 100, 182), 8, fill=(200, 60, 60, 220)); d.text((W / 2, 162), tag, font=Fo(BK, 24), fill=(255, 255, 255), anchor='mm')
        d.text((W - 24, H - 22), '※実データをもとにした、単純化したシミュレーションです', font=Fo(BD, 20), fill=(235, 235, 235, 200), anchor='rs')
        cap = hud.get('cap')
        if cap:
            f = Fo(BK, 52); tw = f.getlength(cap)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 210))
            d.text((W / 2, H - 125), cap, font=f, fill=hud.get('capcol', B.PALE), anchor='mm')
    # 踏みつけでつぶしたアリの数（ポップ）
    cam = CUR['cam']
    if cam is not None and CUR['speed'] <= 2.5:
        lo, hi = np.searchsorted(R.stt, st - 0.9), np.searchsorted(R.stt, st)
        for j in range(lo, hi):
            t0, x, y, k = R.stomps[j]
            if k < 200: continue
            u = (st - t0) / 0.9; X, Y = B.project(x, y, cam); s1 = float(B.depth_scale(y, cam))
            a = int(255 * (1 - u) ** 1.2); fs = int(min(70, max(30, s1 * 0.5)))
            d.text((float(X), float(Y) - s1 * (0.6 + 1.2 * u)), f'-{k:,}匹', font=Fo(BK, fs), fill=(255, 230, 120, a), anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0, a))
B.hud_draw = hud_draw

def render(R, st, cam, hud, f=0):
    CUR.update(R=R, st=st, cam=cam, speed=hud.get('speed', 1.0) or 1.0, f=f)
    return B.render_frame(R, st, cam, hud)
