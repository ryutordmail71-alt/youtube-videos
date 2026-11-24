"""人間N人 vs ゴリラ1頭（素手）のシミュレーション
side 0 = 人間（左）、side 1 = ゴリラ（右）
人間はゴリラに組みつき（同時に組みつけるのは最大 SLOTS 人）、ゴリラの体力を削る。
ゴリラは近くの人間を払いのけ／殴り、戦闘不能にする。組みつかれるほど動きが鈍り、スタミナも減る。
ゴリラの体力が0 → 取り押さえ成功（人間の勝ち）。人間が全員戦闘不能 → ゴリラの勝ち。
使い方: python3 gsim.py SEED N TAG [save]
"""
import json, sys
import numpy as np
FPS = 30; DT = 1 / FPS
SLOTS = 7          # ゴリラの体のまわりに同時に組みつける人数
G_HP = 520.0       # ゴリラの「取り押さえ耐性」
H_SPD = 5.5; G_SPD = 7.0
DMG = 1.6          # 組みついた人1人が1秒あたりに削る量
CD = 0.62          # ゴリラの攻撃間隔（基本）

def run(seed, n, tag=None, save=False):
    rng = np.random.default_rng(seed)
    N = n + 1; G = n
    pos = np.zeros((N, 2), np.float32)
    k = int(np.ceil(np.sqrt(n * 1.6)))
    for i in range(n):
        pos[i] = (70 - (i // k) * 1.3 + rng.normal(0, 0.25), 100 - k * 0.6 + (i % k) * 1.2 + rng.normal(0, 0.25))
    pos[G] = (112, 100)
    side = np.zeros(N, np.int8); side[G] = 1
    hp = np.ones(N, np.float32) * 100; hp[G] = G_HP
    death = np.full(N, -1.0, np.float32)
    face = np.ones(N, np.float32); face[G] = -1
    spd = rng.normal(H_SPD, 0.5, n).clip(4.2, 6.8)
    grip = rng.uniform(0.7, 1.3, n)                     # 人ごとの力の差
    ang = np.full(n, np.nan)                            # 組みつき位置（角度）
    gcd = 0.0; stam = 1.0; t = 0.0; HOLD = 1.2
    P, F, HPs, A = [], [], [], []; ev = []; log = []; step = 0
    while True:
        alive = death < 0; ah = np.where(alive[:n])[0]
        gp = pos[G]
        d = np.linalg.norm(pos[:n] - gp, axis=1)
        atk = np.zeros(N, bool)
        if t > HOLD:
            # 組みついている人
            grab = ah[(d[ah] < 1.35) & ~np.isnan(ang[ah])]
            # 空きスロットに近い順で組みつく
            free = SLOTS - len(grab)
            cand = ah[(d[ah] < 1.6) & np.isnan(ang[ah])]
            if free > 0 and len(cand):
                cand = cand[np.argsort(d[cand])][:free]
                for c in cand:
                    ang[c] = np.arctan2(pos[c, 1] - gp[1], pos[c, 0] - gp[0]) + rng.normal(0, 0.2)
                grab = np.concatenate([grab, cand])
            ng = len(grab)
            # 人間の移動：ゴリラへ向かう（組みついた人はゴリラに張りつく）
            for i in ah:
                if not np.isnan(ang[i]) and i in grab:
                    tgt = gp + 0.95 * np.array([np.cos(ang[i]), np.sin(ang[i])])
                    pos[i] += (tgt - pos[i]) * 0.5; face[i] = np.sign(gp[0] - pos[i, 0]) or 1; atk[i] = True
                else:
                    v = gp - pos[i]; dn = np.linalg.norm(v) + 1e-6
                    want = 1.0 if ng < SLOTS else 2.4            # 満員なら少し外で待つ
                    if dn > want: pos[i] += v / dn * min(dn - want, spd[i] * DT)
                    face[i] = np.sign(v[0]) or 1
            # ゴリラ：組みつかれるほど遅く、スタミナが減る
            slow = 1.0 / (1 + 0.35 * ng)
            if ng == 0 and len(ah):
                j = ah[np.argmin(d[ah])]; v = pos[j] - gp; dn = np.linalg.norm(v) + 1e-6
                pos[G] += v / dn * min(max(0, dn - 1.2), G_SPD * DT); face[G] = np.sign(v[0]) or -1
            stam = max(0.25, stam - DT * (0.006 + 0.0035 * ng))
            gcd -= DT
            near = ah[d[ah] < 2.1]
            if gcd <= 0 and len(near):
                atk[G] = True
                j = near[np.argmin(d[near])]
                tgt = [j]
                # 腕の振りで隣の人も巻きこむことがある
                others = near[near != j]
                if len(others) and rng.random() < 0.35: tgt.append(rng.choice(others))
                for j in tgt:
                    if rng.random() < 0.9:
                        death[j] = t; hp[j] = 0; ang[j] = np.nan
                        # 吹き飛ばされる
                        v = pos[j] - pos[G]; dn = np.linalg.norm(v) + 1e-6; pos[j] += v / dn * rng.uniform(1.0, 2.5)
                        ev.append([round(t, 3), 'die', float(pos[j, 0]), float(pos[j, 1])])
                    else:
                        ev.append([round(t, 3), 'hit', float(pos[j, 0]), float(pos[j, 1])])
                gcd = CD * (1 + 0.12 * ng) / (0.35 + 0.65 * stam) * rng.uniform(0.8, 1.2)
            if gcd > 0 and gcd < 0.25: atk[G] = True
            # ゴリラの体力を削る
            if ng: hp[G] -= DT * DMG * grip[grab[grab < n]].sum() * (1.3 - 0.3 * stam)
            if ng >= SLOTS - 1 and rng.random() < DT * 2: ev.append([round(t, 3), 'hit', float(gp[0]), float(gp[1])])
        P.append(pos.copy()); F.append(np.sign(face).astype(np.int8)); HPs.append(hp.copy()); A.append(atk.copy())
        if step % (FPS * 5) == 0: log.append([round(t, 1), int((death[:n] < 0).sum()), round(float(hp[G]), 1), round(stam, 2)])
        t += DT; step += 1
        if hp[G] <= 0:
            death[G] = t; win = 'human'; break
        if not (death[:n] < 0).any(): win = 'gorilla'; break
        if t > 300: win = 'none'; break
    end = t
    for _ in range(int(4 * FPS)):     # 決着後の余韻
        P.append(pos.copy()); F.append(F[-1]); HPs.append(hp.copy()); A.append(np.zeros(N, bool)); t += DT
    res = dict(n=n, win=win, end=round(end, 2), left=int((death[:n] < 0).sum()), ko=int((death[:n] >= 0).sum()), log=log, events=ev, steps=len(P))
    if save:
        np.savez_compressed(f'/home/claude/gvh/sim_{tag}.npz', pos=np.array(P, np.float32), face=np.array(F), hp=np.array(HPs, np.float32),
                            side=side, death_t=death, atk=np.array(A))
        json.dump(res, open(f'/home/claude/gvh/sim_{tag}.json', 'w'))
    return res

if __name__ == '__main__':
    seed, n, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    r = run(seed, n, tag, len(sys.argv) > 4)
    print(tag, n, r['win'], 'end', r['end'], 'left', r['left'], 'ko', r['ko'], r['log'][-2:])
