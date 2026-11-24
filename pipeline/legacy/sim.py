"""熊1000体 vs カバ1000体 シミュレーション（2D、エージェントベース）
実データ（NPS / BBC Wildlife）をもとに単純化した設定:
  熊(グリズリー): 平均約187kg, 最高時速56〜64km, 爪で何度も攻撃。素早く、群れで囲む。
  カバ: オス1600〜3200kg, 時速30kmは短距離のみ（スタミナ切れ）, 50cm超の牙で一撃が重い。
"""
import numpy as np, json, sys
from scipy.spatial import cKDTree
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
FPS = 30; DT = 1 / FPS
WX, WY = 300.0, 200.0
N = 1000
# ---- パラメータ ----
P = {
 0: dict(name='bear', r=1.1, hp=190, speed=9.0, dmg=(34, 52), cd=0.85, reach=0.9),
 1: dict(name='hippo', r=2.0, hp=1050, speed=6.5, dmg=(150, 230), cd=1.7, reach=1.4),
}
side = np.r_[np.zeros(N, int), np.ones(N, int)]
R = np.where(side == 0, P[0]['r'], P[1]['r'])
HP0 = np.where(side == 0, P[0]['hp'], P[1]['hp']).astype(float)
hp = HP0.copy()
SPD = np.where(side == 0, P[0]['speed'], P[1]['speed'])
# 隊列：熊は左、カバは右（40列×25行）
def formation(cx, spacing, facing):
    cols, rows = 25, 40
    xs, ys = [], []
    for k in range(N):
        c, r = k // rows, k % rows
        xs.append(cx - facing * c * spacing); ys.append(WY / 2 - (rows - 1) * spacing * 0.5 + r * spacing)
    return np.array(xs) + rng.normal(0, 0.3, N), np.array(ys) + rng.normal(0, 0.3, N)
bx, by = formation(100, 2.6, +1)
hx, hy = formation(200, 4.2, -1)
# 範囲内に収める
pos = np.c_[np.r_[bx, hx], np.r_[by, hy]]
pos[:, 1] = np.clip(pos[:, 1], 8, WY - 8)
vel = np.zeros_like(pos)
alive = np.ones(2 * N, bool)
cd = rng.uniform(0, 0.5, 2 * N)
stam = np.ones(2 * N)
target = -np.ones(2 * N, int)
death_t = np.full(2 * N, -1.0)
atk_t = np.full(2 * N, -9.0)   # 最後に攻撃した時刻
hit_t = np.full(2 * N, -9.0)   # 最後に攻撃を受けた時刻
face = np.where(side == 0, 1.0, -1.0)
HOLD = 2.0  # 開始2秒は待機（にらみ合い）

frames_pos, frames_face, frames_hp = [], [], []
events = []   # (t, kind, x, y)
log = []
t = 0.0; step = 0
while True:
    step += 1; t = step * DT
    A = np.where(alive)[0]
    nb, nh = int(alive[:N].sum()), int(alive[N:].sum())
    if step % FPS == 0: log.append((round(t, 1), nb, nh))
    if nb == 0 or nh == 0:
        if not hasattr(sys.modules[__name__], '_end'): END = t
        if t > END + 4: break
        _end = True
    if t > 400: break
    # ターゲット更新（0.5秒ごと or ターゲット死亡）
    if t > HOLD and nb and nh:
        need = (step % 15 == 0) | (target < 0) | ~alive[np.maximum(target, 0)]
        for s in (0, 1):
            me = A[(side[A] == s) & need[A]]
            en = A[side[A] != s]
            if len(me) and len(en):
                tr = cKDTree(pos[en]); kq = min(3, len(en))
                d, j = tr.query(pos[me], k=kq)
                if kq > 1:  # 近い3体からランダム（偏り防止）
                    pick = rng.integers(0, kq, len(me)); j = j[np.arange(len(me)), pick]
                target[me] = en[j]
    # 移動
    stam_eff = np.where(side == 1, 0.4 + 0.6 * stam, 1.0)
    desired = np.zeros_like(pos)
    if t > HOLD:
        tg = target[A]; ok = tg >= 0
        d = pos[tg[ok]] - pos[A[ok]]; dist = np.linalg.norm(d, axis=1) + 1e-6
        stop = dist < (R[A[ok]] + R[tg[ok]] + 0.3)
        sp = SPD[A[ok]] * stam_eff[A[ok]] * np.where(stop, 0.0, 1.0)
        desired[A[ok]] = d / dist[:, None] * sp[:, None]
        face[A[ok]] = np.sign(d[:, 0] + 1e-6)
    vel[A] += (desired[A] - vel[A]) * np.where(side[A] == 0, 0.25, 0.12)[:, None]
    pos[A] += vel[A] * DT
    # カバのスタミナ（走ると減る：時速30kmは短距離のみ）
    spd_now = np.linalg.norm(vel, axis=1)
    hipA = A[side[A] == 1]
    stam[hipA] = np.clip(stam[hipA] - DT * 0.02 * (spd_now[hipA] / P[1]['speed']) - DT * 0.0025 * (t > HOLD), 0.0, 1.0)
    # 衝突（押し合い）
    tr = cKDTree(pos[A]); pairs = tr.query_pairs(2 * P[1]['r'] + 0.2, output_type='ndarray')
    if len(pairs):
        i, j = A[pairs[:, 0]], A[pairs[:, 1]]
        d = pos[j] - pos[i]; dist = np.linalg.norm(d, axis=1) + 1e-6
        ov = (R[i] + R[j]) - dist; m = ov > 0
        if m.any():
            i, j, d, dist, ov = i[m], j[m], d[m], dist[m], ov[m]
            mi = np.where(side[i] == 1, 8.0, 1.0); mj = np.where(side[j] == 1, 8.0, 1.0)  # カバは重い
            push = (d / dist[:, None]) * ov[:, None]
            np.add.at(pos, i, -push * (mj / (mi + mj))[:, None]); np.add.at(pos, j, push * (mi / (mi + mj))[:, None])
            # 突進するカバに跳ね飛ばされる熊（踏みつけ）
            for a, b in ((i, j), (j, i)):
                tm = (side[a] == 1) & (side[b] == 0) & (spd_now[a] > 3.5)
                if tm.any():
                    dmg = 9 * spd_now[a[tm]] * DT * FPS * 0.1
                    np.add.at(hp, b[tm], -dmg)
    pos[:, 0] = np.clip(pos[:, 0], 3, WX - 3); pos[:, 1] = np.clip(pos[:, 1], 5, WY - 5)
    # 攻撃
    cd[A] -= DT * np.where(side[A] == 1, stam_eff[A], 1.0)
    if t > HOLD:
        tg = target[A]; ok = (tg >= 0)
        a, b = A[ok], tg[ok]
        dist = np.linalg.norm(pos[b] - pos[a], axis=1)
        can = alive[b] & (dist < R[a] + R[b] + np.where(side[a] == 0, P[0]['reach'], P[1]['reach'])) & (cd[a] <= 0)
        a, b = a[can], b[can]
        if len(a):
            lo = np.where(side[a] == 0, P[0]['dmg'][0], P[1]['dmg'][0]); hi = np.where(side[a] == 0, P[0]['dmg'][1], P[1]['dmg'][1])
            dmg = rng.uniform(lo, hi)
            np.add.at(hp, b, -dmg)
            cd[a] = np.where(side[a] == 0, P[0]['cd'], P[1]['cd']) * rng.uniform(0.85, 1.15, len(a))
            atk_t[a] = t; hit_t[b] = t
            for k in rng.choice(len(a), min(len(a), 6), replace=False):
                events.append((round(t, 3), 'hit', float(pos[b[k], 0]), float(pos[b[k], 1])))
    # 死亡
    dead = alive & (hp <= 0)
    if dead.any():
        alive[dead] = False; death_t[dead] = t; vel[dead] = 0
        for k in np.where(dead)[0][:8]: events.append((round(t, 3), 'die', float(pos[k, 0]), float(pos[k, 1])))
    frames_pos.append(pos.astype(np.float32).copy()); frames_face.append(face.astype(np.int8).copy())
    frames_hp.append(np.clip(hp / HP0, 0, 1).astype(np.float16))

out = '/home/claude/bvh/sim_out.npz'
np.savez_compressed(out, pos=np.array(frames_pos), face=np.array(frames_face), hp=np.array(frames_hp), side=side, death_t=death_t,
                    atk=np.array([0]), stam=stam)
# 攻撃・被弾時刻は再計算が重いので、フレームごとの記録はイベントから
json.dump(dict(log=log, events=events[:200000], end=END if 'END' in dir() else t, steps=step), open('/home/claude/bvh/sim_log.json', 'w'))
print('END', round(t, 1), 'bears', int(alive[:N].sum()), 'hippos', int(alive[N:].sum()))
for row in log[::5]: print(row)
