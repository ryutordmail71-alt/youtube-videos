"""バッタの群れ vs 畑（決定論モデル）
・畑：217m四方（東京ドーム1個分 ≒ 4.7ha）、トウモロコシ 50t/ha（≒5kg/m²）→ 約235t
・食べる量：1匹 1日2g（FAO）。全体の食べる速さ = 匹数 × 2g/日（着地した割合に比例）
・どこから食べるか：風上（左）から、むらのある「食べる前線」が右へ進む
"""
import numpy as np
from scipy import ndimage as nd
FS = 217; B0 = 5.0; EAT = 2.0e-3 / 86400
BTOT = B0 * FS * FS
NG, NF = 90000, 60000            # 描画用：地面の粒子数、飛んでいる粒子数
T_ARR = 12.0; T_LAND = 6.0        # 到着までの時間、着地しきるまでの時間（いずれも実時間の秒）

def _rank():
    rng = np.random.default_rng(7)
    def nz(sc):
        n = rng.normal(0, 1, (FS // sc + 3, FS // sc + 3)).astype(np.float32)
        return nd.zoom(n, sc, order=3)[:FS, :FS]
    x = np.arange(FS, dtype=np.float32)[None, :] / FS
    r = x + 0.10 * nz(40) + 0.05 * nz(12) + 0.02 * nz(4)
    r = (r - r.min()) / (r.max() - r.min())
    order = np.argsort(r.ravel(), kind='stable'); rk = np.empty(FS * FS, np.float32); rk[order] = np.arange(FS * FS) / (FS * FS - 1)
    return rk.reshape(FS, FS), order
RANK, ORDER = _rank()
W_BAND = 0.035

class Model:
    def __init__(self, n, flying_scale=1.0):
        self.n = n; self.rate = n * EAT                          # kg/s（全員が食べているとき）
        rng = np.random.default_rng(11)
        self.gq = rng.random(NG).astype(np.float32); self.gjx = rng.uniform(-0.5, 0.5, NG).astype(np.float32); self.gjy = rng.uniform(-0.5, 0.5, NG).astype(np.float32)
        self.gph = rng.uniform(0, 6.28, NG).astype(np.float32)
        self.fq = rng.random(NF).astype(np.float32); self.fr = np.abs(rng.normal(0, 1, NF)).astype(np.float32)
        self.fa = rng.uniform(0, 6.28, NF).astype(np.float32); self.fw = rng.uniform(0.05, 0.4, NF).astype(np.float32) * rng.choice([-1, 1], NF)
        self.fz = np.abs(rng.normal(9, 7, NF)).astype(np.float32) + 1.5; self.fzp = rng.uniform(0, 6.28, NF).astype(np.float32)
        self.fs = flying_scale
        # 終了時刻（着地しはじめから、2%を残して食べ終わるまで）
        e_land = self.rate * T_LAND / 2
        self.t_end = T_ARR + T_LAND + (0.98 * BTOT - e_land) / self.rate
    def landed(self, t): return float(np.clip((t - T_ARR) / T_LAND, 0, 1))
    def eaten(self, t):
        if t <= T_ARR: return 0.0
        a = min(t, T_ARR + T_LAND) - T_ARR; e = self.rate * a * a / (2 * T_LAND)
        if t > T_ARR + T_LAND: e += self.rate * (t - T_ARR - T_LAND)
        return min(e, 0.98 * BTOT) if t <= self.t_end else 0.98 * BTOT
    def frac(self, t): return self.eaten(t) / BTOT
    def remain_map(self, t):
        f = self.frac(t)
        return np.clip((RANK - f) / W_BAND + 0.0, 0, 1) if f > 0 else np.ones((FS, FS), np.float32)
    def front(self, t):
        """いま食べている前線の中心（x, y）"""
        f = self.frac(t); lo = int(np.clip(f - 0.02, 0, 1) * (FS * FS - 1)); hi = int(np.clip(f + 0.06, 0, 1) * (FS * FS - 1))
        idx = ORDER[lo:hi + 1:max(1, (hi - lo) // 400)]
        return float((idx % FS).mean()) + 0.5, float((idx // FS).mean()) + 0.5
    def ground_pts(self, t):
        L = self.landed(t); k = int(NG * L)
        if k == 0: return np.zeros(0, np.float32), np.zeros(0, np.float32)
        f = self.frac(t); done = t > self.t_end
        q = self.gq[:k]
        if done: pos = q                                             # 食べ終わったあとは畑じゅうに散らばる
        else: pos = np.clip(f - 0.025 + q * 0.07, 0, 1) if f > 0.001 else q * 0.06
        ci = ORDER[(pos * (FS * FS - 1)).astype(np.int64)]
        x = (ci % FS).astype(np.float32) + 0.5 + self.gjx[:k] + 0.15 * np.sin(t * 0.7 + self.gph[:k])
        y = (ci // FS).astype(np.float32) + 0.5 + self.gjy[:k] + 0.15 * np.cos(t * 0.6 + self.gph[:k])
        return x, y
    def flying_pts(self, t):
        L = self.landed(t); keep = 1.0 - 0.8 * L
        k = int(NF * keep); fx, fy = self.front(t) if t > T_ARR else (30.0, FS / 2)
        sp = 6.0
        cx = fx - max(0.0, T_ARR - t) * sp * 1.3; cy = fy
        R = (28 + 35 * self.fs) * self.fr[:k]
        a = self.fa[:k] + self.fw[:k] * t
        x = cx + R * np.cos(a) * 1.4 + (self.fq[:k] - 0.5) * 30 * self.fs
        y = cy + R * np.sin(a)
        z = self.fz[:k] * (0.7 + 0.6 * self.fs) * (0.8 + 0.2 * np.sin(t * 0.9 + self.fzp[:k])) * (1 - 0.6 * L) + 0.5
        return x.astype(np.float32), y.astype(np.float32), z.astype(np.float32)

if __name__ == '__main__':
    for n in (1e7, 1e8, 1e9, 1e10, 2e11):
        M = Model(n); d = M.t_end - T_ARR; h, r = divmod(d, 3600); m, s = divmod(r, 60)
        print(f'{n:.0e}', f'{d:.1f} s', f'{int(h)}h{int(m)}m{s:.0f}s', f'{d/86400:.2f} days')
