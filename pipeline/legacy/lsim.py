"""バッタ（サバクトビバッタ）N匹 vs 畑（東京ドーム1個分 ≒ 217m四方、トウモロコシ 約50t/ha）
粒子1つ = K匹。飛んでいる（z>0）か、地面で食べているか。
1匹が1日に食べる量 2g（FAO）→ 2.315e-5 kg/s。畑がほぼ食べ尽くされたら終了。
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
FS = 217                  # 畑の一辺（m）
B0 = 5.0                  # 1m²あたりの作物（kg）= 50t/ha
EAT = 2.0e-3 / 86400      # 1匹が1秒に食べる量（kg）
WIND = 4.5                # 追い風（m/s）≒ 時速16km
P = 150000                # 粒子の数

class LocSim:
    def __init__(self, seed, n):
        self.rng = rng = np.random.default_rng(seed); self.n = n; self.K = n / P
        self.x = rng.normal(-70, 28, P).astype(np.float32); self.y = rng.normal(FS / 2, 60, P).astype(np.float32)
        self.z = np.abs(rng.normal(14, 9, P)).astype(np.float32) + 2
        self.vx = np.zeros(P, np.float32); self.vy = np.zeros(P, np.float32)
        self.gr = np.zeros(P, bool)          # 地面にいるか
        b = rng.normal(1, 0.08, (FS, FS)).astype(np.float32); self.B = B0 * np.clip(b, 0.8, 1.2); self.Btot0 = float(self.B.sum())
        self.t = 0.0; self.done = None; self.end = None; self.eaten = 0.0
    def dt(self):
        return 0.1 if (self.t < 150 or self.n > 5e9) else 4.0
    def remain(self): return float(self.B.sum()) / self.Btot0
    def step(self):
        rng = self.rng; dt = self.dt(); self.t += dt
        fl = ~self.gr; idx = np.where(fl)[0]
        # 残っている畑の中心（緑の重心）
        if self.t % 2 < dt or not hasattr(self, 'gc'):
            w = self.B.sum(0); h = self.B.sum(1); tot = w.sum() + 1e-6
            self.gc = (float((w * np.arange(FS)).sum() / tot), float((h * np.arange(FS)).sum() / tot))
        gx, gy = self.gc
        if len(idx):
            x = self.x[idx]; y = self.y[idx]; z = self.z[idx]
            over = (x >= 0) & (x < FS) & (y >= 0) & (y < FS)
            ax = (gx - x); ay = (gy - y); d = np.sqrt(ax * ax + ay * ay) + 1e-3
            tvx = WIND * np.where(x < gx - 20, 1.0, 0.25) + 2.2 * ax / d + rng.normal(0, 1.6, len(idx))
            tvy = 2.2 * ay / d * np.minimum(1, d / 30) + rng.normal(0, 1.6, len(idx))
            k = min(1.0, dt * 1.5)
            self.vx[idx] += (tvx - self.vx[idx]) * k; self.vy[idx] += (tvy - self.vy[idx]) * k
            sx = min(dt, 6.0)
            self.x[idx] += self.vx[idx] * sx; self.y[idx] += self.vy[idx] * sx
            ci = np.clip(self.x[idx].astype(int), 0, FS - 1); cj = np.clip(self.y[idx].astype(int), 0, FS - 1)
            green = over & (self.B[cj, ci] > B0 * 0.25)
            vz = np.where(green, -2.2, np.where(z < 3, 1.2, rng.normal(0, 0.8, len(idx))))
            self.z[idx] = np.clip(z + vz * sx, 0, 60)
            land = green & (self.z[idx] <= 0.3) & (rng.random(len(idx)) < min(1, dt * 2))
            self.gr[idx[land]] = True; self.z[idx[land]] = 0
        # 地面のバッタ：食べる
        g = np.where(self.gr)[0]
        if len(g):
            ci = np.clip(self.x[g].astype(int), 0, FS - 1); cj = np.clip(self.y[g].astype(int), 0, FS - 1)
            cell = cj * FS + ci
            cnt = np.bincount(cell, minlength=FS * FS).reshape(FS, FS).astype(np.float32)
            want = cnt * self.K * EAT * dt
            got = np.minimum(want, self.B); self.B -= got; self.eaten += float(got.sum())
            # 食べ尽くした場所からは、跳ねて移動するか飛び立つ
            empty = self.B[cj, ci] < B0 * 0.06
            e = g[empty]
            if len(e):
                hop = rng.random(len(e)) < 0.7
                h = e[hop]; a = rng.uniform(0, 2 * np.pi, len(h)); r = rng.uniform(2, 12, len(h))
                nx = np.clip(self.x[h] + np.cos(a) * r, 0, FS - 0.01); ny = np.clip(self.y[h] + np.sin(a) * r, 0, FS - 0.01)
                ok = self.B[ny.astype(int), nx.astype(int)] > B0 * 0.25
                self.x[h[ok]] = nx[ok]; self.y[h[ok]] = ny[ok]
                f = np.concatenate([e[~hop], h[~ok]])
                self.gr[f] = False; self.z[f] = rng.uniform(1, 6, len(f)).astype(np.float32)
        if self.done is None and self.remain() < 0.01:
            self.done = 'eaten'; self.end = self.t

def run(seed, n, tag=None, verbose=False, tmax=2e6):
    S = LocSim(seed, n); rec = []; last = -1
    while True:
        S.step()
        rec.append((round(S.t, 2), round(S.remain(), 5), round(S.eaten, 1), int((~S.gr).sum()), int(S.gr.sum())))
        if verbose and int(S.t / 3600) != last: last = int(S.t / 3600); print(round(S.t), rec[-1], flush=True)
        if S.done and S.t > S.end + 4: break
        if S.t > tmax: break
    res = dict(n=n, seed=seed, end=S.end, eaten=S.eaten)
    if tag: json.dump(dict(res=res, rec=rec), open(os.path.join(HERE, f'lsim_{tag}.json'), 'w'))
    return res

if __name__ == '__main__':
    import time; t0 = time.time()
    print(run(int(sys.argv[1]), float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else None, True), time.time() - t0)
