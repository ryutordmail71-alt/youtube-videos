"""蚊N匹 vs 人間1人（決定論モデル）
・1回に吸う血：約0.005mL（目安。0.001〜0.01mLと言われる）
・人間の血液：約5L。3割（1.5L）を失うと命が危ない → 30万回で危険ライン
・体にとまれる蚊は最大 CAP 匹。1匹が吸い終わるまで TAU 秒。人間は手でたたき、とまっている蚊を1秒に KILL の割合で倒す
・蚊は、まわりの沼から ARR 秒くらいかけて集まってくる
"""
import numpy as np
V = 0.005; BLOOD = 5000.0; DANGER = 0.30
CAP = 3000.0; TAU = 100.0; KILL = 0.06; ARR = 300.0; LAND = 0.25
DT = 0.5

class Model:
    def __init__(self, n):
        self.n = n
        t = 0.0; W = 0.0; O = 0.0; bites = 0.0; dead = 0.0; arrived = 0.0
        T, Ws, Os, Bs, Ds, As = [], [], [], [], [], []
        self.win = None; self.t_end = None
        while True:
            a_new = n * (1 - np.exp(-(t + DT) / ARR)) - arrived; arrived += a_new; W += a_new
            land = min(W * LAND * DT, max(0.0, CAP - O)); W -= land; O += land
            fin = O * DT / TAU; kil = O * KILL * DT; O -= fin + kil; bites += fin; dead += kil
            t += DT
            T.append(t); Ws.append(W); Os.append(O); Bs.append(bites); Ds.append(dead); As.append(arrived)
            if self.win is None and bites * V >= BLOOD * DANGER: self.win = 'mosq'; self.t_end = t
            if self.win is None and arrived > n * 0.999 and W + O < max(50.0, n * 0.0005): self.win = 'human'; self.t_end = t
            if self.win and t > self.t_end + 6: break
            if t > 3e5: break
        self.T = np.array(T); self.W = np.array(Ws); self.O = np.array(Os); self.Bt = np.array(Bs); self.D = np.array(Ds); self.A = np.array(As)
    def at(self, t, arr):
        return float(np.interp(t, self.T, arr))
    def bites(self, t): return self.at(min(t, self.t_end), self.Bt)
    def blood_lost(self, t): return self.bites(t) * V           # mL
    def onbody(self, t): return self.at(t, self.O)
    def flying(self, t): return self.at(t, self.W)
    def killed(self, t): return self.at(min(t, self.t_end), self.D)
    def remaining(self, t): return max(0.0, self.n - self.killed(t) - self.bites(t))

def threshold():
    lo, hi = 1e5, 2e7
    for _ in range(40):
        mid = (lo + hi) / 2
        m = Model(mid)
        if m.win == 'mosq': hi = mid
        else: lo = mid
    return hi

if __name__ == '__main__':
    for n in (5e5, 1e6, 1.5e6, 2e6, 3e6):
        m = Model(n); print(f'{n:.1e}', m.win, round(m.t_end), 'bites', int(m.bites(m.t_end)), 'blood mL', round(m.blood_lost(m.t_end)), 'killed', int(m.killed(m.t_end)))
    print('threshold', threshold())
