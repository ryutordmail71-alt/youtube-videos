"""ゾンビの広がり（単純化モデル）。1時間ごとに計算"""
import json, math, sys, numpy as np
from zgrid import ij, NX, NY, DLAT, DLON, LAT1
g = np.load('grid.npz'); CODE = g['code']; POP0 = g['pop']; KM2 = g['km2']; LAND = CODE > 0
A_SWEEP = 0.03      # 1時間に出会える範囲（km²）の目安
H_FIGHT = 0.25      # 1回の戦いにかかる時間（時間）→ 最大4人/時
P_WIN = 5 / 9       # ゾンビが勝つ確率（かむ：倒す ＝ 1.25：1 → 5勝4敗）
MU = 0.027          # 隣のマスへ移る割合（/時）
CELL_KM = 5.5; V_WALK = 1.1   # km/h
T_CROSS = CELL_KM / V_WALK
LINKS = [((140.47, 41.17), (140.40, 41.55)),   # 青函トンネル（仮定：線路を歩ける）
         ((130.96, 33.96), (130.90, 33.90)),   # 関門トンネル（人道あり）
         ((133.80, 34.47), (133.82, 34.32)),   # 瀬戸大橋
         ((133.05, 34.40), (133.00, 34.10)),   # しまなみ海道
         ((135.00, 34.62), (134.95, 34.40))]   # 明石海峡大橋〜淡路
SHIBUYA = (139.70, 35.66)
def cell(lo, la):
    x, y = ij(lo, la); x, y = int(x), int(y)
    best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if 0 <= y + dy < NY and 0 <= x + dx < NX and LAND[y + dy, x + dx]:
                dd = dx * dx + dy * dy
                if best is None or dd < best[0]: best = (dd, y + dy, x + dx)
    return best[1], best[2]
def run(days=240, seeds=None, p_win=P_WIN, snap_every=6, tag=''):
    S = POP0.copy(); Z = np.zeros_like(S); R = np.zeros_like(S)
    t_inf = np.full(S.shape, np.inf)
    for (lo, la, h) in (seeds or [(*SHIBUYA, 0)]):
        pass
    pending = sorted(seeds or [(*SHIBUYA, 0)], key=lambda s: s[2])
    lk = [(cell(*a), cell(*b)) for a, b in LINKS]
    snaps = []; stats = []
    for hr in range(days * 24):
        while pending and pending[0][2] <= hr:
            lo, la, _ = pending.pop(0); y, x = cell(lo, la); Z[y, x] += 1; t_inf[y, x] = min(t_inf[y, x], hr)
        dens = S / KM2
        enc = A_SWEEP * dens / (1 + A_SWEEP * dens * H_FIGHT)          # 1人のゾンビが1時間に出会う人数
        active = Z >= 1
        e = np.where(active, enc * Z, 0.0); e = np.minimum(e, S)
        bite = e * p_win; kill = e * (1 - p_win)
        S -= bite; Z += bite - kill; R += kill; Z = np.maximum(Z, 0)
        # 移動：歩いて隣のマスへ（通りぬけには T_CROSS 時間かかる）
        ready = (hr - t_inf) >= T_CROSS
        out = np.where(ready & LAND, Z * MU, 0.0); Z -= out; q = out / 4
        inc = np.zeros_like(Z)
        inc[1:, :] += q[:-1, :]; inc[:-1, :] += q[1:, :]; inc[:, 1:] += q[:, :-1]; inc[:, :-1] += q[:, 1:]
        for (a, b) in lk:
            for s_, d_ in ((a, b), (b, a)):
                if ready[s_]: m = Z[s_] * MU * 0.25; Z[s_] -= m; inc[d_] += m
        lost = inc * (~LAND); inc = inc * LAND
        Z += inc
        newly = (Z >= 1) & np.isinf(t_inf); t_inf[newly] = hr
        if hr % snap_every == 0:
            snaps.append(np.stack([(S / np.maximum(POP0, 1))[LAND], (Z / np.maximum(POP0, 1))[LAND]]).astype(np.float16)); stats.append((hr, S.sum(), Z.sum(), R.sum()))
    np.savez_compressed(f'sim{tag}.npz', snaps=np.array(snaps), stats=np.array(stats), t_inf=t_inf, S=S)
    return stats, t_inf, S
if __name__ == '__main__':
    st, ti, S = run(int(sys.argv[1]) if len(sys.argv) > 1 else 120)
    P = POP0.sum()
    for hr, s, z, r in st[::40]: print(f'day {hr/24:6.1f} human {s/P*100:6.2f}% zombie {z/P*100:6.2f}%')
