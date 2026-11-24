"""巨人（身長50m）vs 人間の綱引き（決定論モデル＋リズム）
・人1人が綱を引く力：63kg重（リンゲルマンの綱引き実験の1人のとき）
・大人数では1人あたりの力が落ちる（リンゲルマン効果：8人で1人あたり49%）。大人数は8人のときと同じと仮定
・巨人の力：筋肉の断面積に比例 → S² ≒ 816倍 → 63×816 ≒ 5万1400kg重
・綱の位置 p（m）：+10 で巨人が引き倒される（人間の勝ち）、-20 で人間が引きずられる（巨人の勝ち）
"""
import numpy as np
S = 50 / 1.75; S2 = S * S
F1 = 63.0
def eff(n):
    tab = [(1, 1.0), (2, 0.93), (3, 0.85), (8, 0.49)]
    if n >= 8: return 0.49
    xs, ys = zip(*tab); return float(np.interp(n, xs, ys))
FG = F1 * S2                      # 巨人の力（kg重）
WIN_H, WIN_G = 10.0, -20.0
VMAX, FSC = 2.0, 60000.0
HEAVE = 0.8 * np.sqrt(S)          # 巨人が引くリズム（秒）
class Model:
    def __init__(self, n, dt=1 / 30, tmax=600, lazy=True):
        self.n = n; e = eff(n) if lazy else 1.0
        t = 0.0; p = 0.0; T, P, FH, FGs = [], [], [], []; self.win = None; self.t_end = None
        while t < tmax:
            ramp = min(1.0, t / 2.0); tire = 0.78 + 0.22 * np.exp(-t / 60)
            fh = n * F1 * e * ramp * tire * (1 + 0.20 * np.sin(2 * np.pi * t / 2.0) + 0.04 * np.sin(2 * np.pi * t / 7.3))
            fg = FG * ramp * tire * (1 + 0.16 * np.sin(2 * np.pi * t / HEAVE + 1.0))
            if self.win is None:
                p += VMAX * np.tanh((fh - fg) / FSC) * dt
                if p >= WIN_H: self.win = 'human'; self.t_end = t
                if p <= WIN_G: self.win = 'giant'; self.t_end = t
            T.append(t); P.append(p); FH.append(fh); FGs.append(fg); t += dt
            if self.win and t > self.t_end + 15: break
        if self.win is None: self.t_end = t
        self.T = np.array(T); self.P = np.array(P); self.FH = np.array(FH); self.FG = np.array(FGs)
    def at(self, t, a): return float(np.interp(t, self.T, a))
    def pos(self, t): return self.at(t, self.P)
    def fh(self, t): return self.at(min(t, self.t_end), self.FH)
    def fg(self, t): return self.at(min(t, self.t_end), self.FG)
if __name__ == '__main__':
    print('giant force kgf', FG, 'threshold', FG / (F1 * 0.49), 'no-lazy', FG / F1)
    for n in (100, 816, 1000, 1500, 1660, 2000):
        m = Model(n); print(n, m.win, round(m.t_end, 1), 'ratio', round(n * F1 * eff(n) / FG, 2))
    m = Model(816, lazy=False); print('816 no lazy', m.win, round(m.t_end, 1))
