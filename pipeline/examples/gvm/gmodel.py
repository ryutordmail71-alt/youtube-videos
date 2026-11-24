"""巨人（身長50m）vs 蚊の大群（決定論モデル）
大きさ S = 50/1.75 ≒ 28.6倍。重さ・血液は S³ ≒ 2万3300倍、体の表面は S² ≒ 816倍。
・1回に吸う血 0.005mL、危険ラインは血液の3割
・体にとまれる蚊：人の3000匹 × S²
・たたく速さ：体が大きいほど動きはゆっくり（√S 倍の時間）→ 1秒に倒せる割合は 0.06/√S
・1回戦：巨人の皮膚は S 倍の厚さ → 針が血管に届かない（吸えない）。蚊は GIVEUP 秒であきらめて離れる
・2回戦：皮膚が人と同じ薄さだったら → 100秒で吸い終わる
"""
import numpy as np
S = 50 / 1.75
V = 0.005; BLOOD = 5000.0 * S ** 3; DANGER = 0.30
CAP = 3000.0 * S ** 2; KILL = 0.06 / np.sqrt(S); LAND = 0.25; TAU = 100.0; GIVEUP = 25.0
SWAT = 0.8 * np.sqrt(S)          # たたく間隔（秒）

class Model:
    def __init__(self, n, can_bite=True, arr=600.0, dt=2.0):
        self.n = n; self.can_bite = can_bite
        t = 0.0; W = 0.0; O = 0.0; bites = 0.0; dead = 0.0; arrived = 0.0; gone = 0.0
        T, Ws, Os, Bs, Ds, Gs = [], [], [], [], [], []
        self.win = None; self.t_end = None
        while True:
            a_new = n * (1 - np.exp(-(t + dt) / arr)) - arrived; arrived += a_new; W += a_new
            land = min(W * LAND * dt, max(0.0, CAP - O)); W -= land; O += land
            if can_bite: fin = O * dt / TAU; bites += fin
            else: fin = O * dt / GIVEUP; gone += fin
            kil = O * KILL * dt; O -= fin + kil; dead += kil
            t += dt
            T.append(t); Ws.append(W); Os.append(O); Bs.append(bites); Ds.append(dead); Gs.append(gone)
            if self.win is None and bites * V >= BLOOD * DANGER: self.win = 'mosq'; self.t_end = t
            if self.win is None and arrived > n * 0.999 and W + O < max(50.0, n * 0.0005): self.win = 'giant'; self.t_end = t
            if self.win and t > self.t_end + 20: break
            if t > 2e6: break
        self.T = np.array(T); self.W = np.array(Ws); self.O = np.array(Os); self.Bt = np.array(Bs); self.D = np.array(Ds); self.G = np.array(Gs)
    def at(self, t, arr): return float(np.interp(t, self.T, arr))
    def bites(self, t): return self.at(min(t, self.t_end), self.Bt)
    def blood_lost(self, t): return self.bites(t) * V            # mL
    def onbody(self, t): return self.at(t, self.O) if t <= self.t_end + 1 else self.at(t, self.O) * 0.3
    def flying(self, t): return self.at(t, self.W)
    def killed(self, t): return self.at(min(t, self.t_end), self.D)
    def gaveup(self, t): return self.at(min(t, self.t_end), self.G)
    def remaining(self, t): return max(0.0, self.n - self.killed(t) - self.bites(t) - self.gaveup(t))

if __name__ == '__main__':
    print('weight t', 70 * S ** 3 / 1000, 'blood L', BLOOD / 1000, 'cap', CAP, 'swat s', SWAT, 'kills/swat at cap', KILL * CAP * SWAT)
    m = Model(1e8, can_bite=False); print('R1', m.win, m.t_end, 'killed %.3g gave up %.3g' % (m.killed(m.t_end), m.gaveup(m.t_end)))
    for n in (1e9, 5e9, 1e10, 1.5e10, 2e10):
        m = Model(n); print(f'{n:.0e}', m.win, round(m.t_end / 3600, 2), 'h', 'blood L', round(m.blood_lost(m.t_end) / 1000), '%', round(m.blood_lost(m.t_end) / BLOOD * 100, 1), 'killed %.3g' % m.killed(m.t_end))
