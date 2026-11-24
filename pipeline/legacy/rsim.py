"""熊 vs 鮭：川のシミュレーション
川は x 方向に流れる（右が下流、左が上流）。鮭は右から泳いできて、左のゴール（産卵場）を目指す。
熊は川の中に陣取り、近くの鮭を捕まえて食べる。食べられる数には上限（満腹）があり、満腹になると岸へ上がって休む。
鮭の半分以上がゴールにたどり着けば鮭の勝ち。
使い方: python3 rsim.py SEED N_SALMON TAG [save]
"""
import json, sys
import numpy as np
from scipy.spatial import cKDTree

FPS = 30; DT = 1.0 / FPS
RY0, RY1 = 60.0, 140.0          # 川幅 80m
BX0, BX1 = 95.0, 135.0          # 熊が陣取るエリア
GOAL = 78.0                     # ここより左に行けばゴール
SPAWN_X = 185.0
T_RUN = 60.0                    # 鮭が次々と到着する時間
NB = 1000

def run(seed, ns, tag=None, save=False):
    rng = np.random.default_rng(seed)
    # --- 鮭（進路は解析的：まっすぐ上流へ、少し蛇行）---
    t0 = np.sort(rng.uniform(0, T_RUN, ns)).astype(np.float32)
    ly = rng.uniform(RY0 + 2, RY1 - 2, ns).astype(np.float32)
    v = rng.normal(2.0, 0.25, ns).clip(1.4, 2.7).astype(np.float32)
    wa = rng.uniform(0.3, 1.2, ns).astype(np.float32); wf = rng.uniform(0.5, 1.2, ns).astype(np.float32); wp = rng.uniform(0, 6.28, ns).astype(np.float32)
    x0 = (SPAWN_X + rng.uniform(0, 6, ns)).astype(np.float32)
    def spos(idx, t):
        dt = t - t0[idx]
        return np.stack([x0[idx] - v[idx] * dt, ly[idx] + wa[idx] * np.sin(wf[idx] * dt + wp[idx])], 1)
    s_end = np.full(ns, -1.0, np.float32)     # 食べられた時刻 or ゴール時刻
    s_res = np.zeros(ns, np.int8)              # 0=泳いでいる 1=食べられた 2=ゴール
    s_by = np.full(ns, -1, np.int32)
    t_goal = t0 + (x0 - GOAL) / v              # 蛇行は無視してx方向だけで判定
    # --- 熊 ---
    # 体格（スキル）に応じて満腹までの数：大きなオスは30匹以上、小さな熊はもっと少ない
    cap = np.clip(np.round(8 + 28 * rng.beta(2.2, 2.0, NB)), 6, 36).astype(np.int32)
    gx = int(np.ceil(np.sqrt(NB * (BX1 - BX0) / (RY1 - RY0 - 4))))
    gy = int(np.ceil(NB / gx))
    xs = np.linspace(BX0, BX1, gx); ys = np.linspace(RY0 + 2.5, RY1 - 2.5, gy)
    P = np.array([(x, y) for x in xs for y in ys])[:NB] + rng.normal(0, 0.35, (NB, 2))
    home = P.copy(); pos = P.astype(np.float32).copy()
    face = np.ones(NB, np.float32)             # +1: 右（下流）を向く
    state = np.zeros(NB, np.int8)              # 0=待つ/移動 1=飛びかかる 2=食べる 3=岸へ 4=休む
    timer = np.zeros(NB, np.float32); eaten = np.zeros(NB, np.int32); tgt = np.full(NB, -1, np.int32)
    bank = np.where(pos[:, 1] < (RY0 + RY1) / 2, RY0 - rng.uniform(4, 16, NB), RY1 + rng.uniform(4, 16, NB)).astype(np.float32)
    restx = (pos[:, 0] + rng.normal(0, 8, NB)).astype(np.float32)
    SPD = 2.2; DET = 3.2; REACH = 1.1; P_HIT = 0.42; T_ATK = 0.35; T_EAT = 2.0
    frames_pos = []; frames_st = []; frames_face = []; frames_eat = []
    log = []; t = 0.0; step = 0
    while True:
        # 泳いでいる鮭
        alive = np.where((s_res == 0) & (t0 <= t))[0]
        # ゴール判定
        gl = alive[t_goal[alive] <= t]
        if len(gl): s_res[gl] = 2; s_end[gl] = t
        alive = alive[t_goal[alive] > t]
        sp = spos(alive, t) if len(alive) else np.zeros((0, 2), np.float32)
        claimed = set()
        if len(alive):
            tree = cKDTree(sp)
            hunt = np.where(state == 0)[0]
            if len(hunt):
                d, j = tree.query(pos[hunt], k=1, distance_upper_bound=DET)
                for b, dd, jj in zip(hunt, d, j):
                    if not np.isfinite(dd) or jj in claimed:
                        # 獲物がいなければ定位置へ戻る
                        hv = home[b] - pos[b]; hn = np.hypot(*hv)
                        if hn > 0.3: pos[b] += hv / hn * min(hn, 0.6 * DT)
                        continue
                    claimed.add(jj); fv = sp[jj] - pos[b]
                    if fv[0] != 0: face[b] = np.sign(fv[0])
                    if dd <= REACH:
                        state[b] = 1; timer[b] = T_ATK; tgt[b] = alive[jj]
                    else:
                        pos[b] += fv / dd * min(dd, SPD * DT)
        # 飛びかかり中
        a = np.where(state == 1)[0]
        timer[a] -= DT
        done = a[timer[a] <= 0]
        for b in done:
            s = tgt[b]
            if s_res[s] == 0 and rng.random() < P_HIT:
                s_res[s] = 1; s_end[s] = t; s_by[s] = b; state[b] = 2; timer[b] = T_EAT; eaten[b] += 1
            else:
                state[b] = 0; timer[b] = 0
        # 食べている
        e = np.where(state == 2)[0]; timer[e] -= DT
        fin = e[timer[e] <= 0]
        full = fin[eaten[fin] >= cap[fin]]; state[fin] = 0; state[full] = 3
        # 岸へ向かう
        w = np.where(state == 3)[0]
        if len(w):
            tv = np.stack([restx[w] - pos[w, 0], bank[w] - pos[w, 1]], 1); tn = np.linalg.norm(tv, axis=1) + 1e-6
            pos[w] += tv / tn[:, None] * np.minimum(tn, 1.6 * DT)[:, None]
            face[w] = np.where(np.abs(tv[:, 0]) > 0.3, np.sign(tv[:, 0]), face[w])
            state[w[tn < 0.3]] = 4
        # 押し合い（重なり防止）
        act = np.where(state <= 3)[0]
        if len(act) > 1:
            bt = cKDTree(pos[act]); pr = bt.query_pairs(1.25, output_type='ndarray')
            if len(pr):
                i1, i2 = act[pr[:, 0]], act[pr[:, 1]]; dv = pos[i1] - pos[i2]; dn = np.linalg.norm(dv, axis=1) + 1e-6
                push = (dv / dn[:, None]) * ((1.25 - dn) * 0.25)[:, None]
                np.add.at(pos, i1, push); np.add.at(pos, i2, -push)
        frames_pos.append(pos.astype(np.float16).copy()); frames_st.append(state.copy()); frames_face.append(face.astype(np.int8).copy())
        if step % (FPS * 5) == 0:
            log.append([round(t, 1), int((s_res == 1).sum()), int((s_res == 2).sum()), int(((s_res == 0) & (t0 <= t)).sum()), int((state >= 3).sum())])
        t += DT; step += 1
        if t > T_RUN + 1 and not ((s_res == 0)).any(): break
        if t > 400: break
    nE = int((s_res == 1).sum()); nG = int((s_res == 2).sum())
    end_t = float(s_end.max())
    res = dict(ns=ns, eaten=nE, goal=nG, rate=nG / ns, win='salmon' if nG * 2 >= ns else 'bear', end=end_t, full=int((eaten >= cap).sum()), steps=step, log=log,
               cap_mean=float(cap.mean()))
    if save:
        np.savez_compressed(f'/home/claude/bvs/rsim_{tag}.npz', pos=np.array(frames_pos), st=np.array(frames_st), face=np.array(frames_face),
                            t0=t0, ly=ly, v=v, wa=wa, wf=wf, wp=wp, x0=x0, s_end=s_end, s_res=s_res, s_by=s_by, eaten_final=eaten, cap=cap)
        json.dump(res, open(f'/home/claude/bvs/rsim_{tag}.json', 'w'))
    return res

if __name__ == '__main__':
    seed, ns, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    r = run(seed, ns, tag, len(sys.argv) > 4)
    print(tag, ns, r['win'], r['eaten'], r['goal'], f"{r['rate']*100:.1f}%", 'end', round(r['end'], 1), 'full', r['full'], 'cap', r['cap_mean'], r['log'][-3:])
