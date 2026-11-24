"""立ち上がったときの、脳の血圧（決定論モデル）
・血の重さによる圧力：1mあたり 約78mmHg（ρ=1060kg/m³）
・人：心臓から脳まで 0.35m、心臓から足まで 1.3m、心拍 70回/分、立ち上がるのに 2秒
・巨人（×29）：心臓から脳まで 約10m、足まで 約37m。心拍は 体重^(-1/4) → 70/12.4 ≒ 5.7回/分、立ち上がるのに 2×√29 ≒ 11秒
・心臓の圧力（平均）P：寝ているとき 90mmHg。立つと、圧受容器反射で「脳に70mmHg届く圧力」をめざして上がる（上限 Pmax、時定数＝3拍）
・立ち上がるとき、血が足にたまって一時的に 20mmHg 下がる（3拍で回復）
・脳の血圧が 30mmHg を下回る時間が 合計7秒 を超えたら気絶（実験では血流が止まって4〜10秒）
"""
import numpy as np
S = 50 / 1.75; KM = 1060 * 9.81 / 133.32
class Model:
    def __init__(self, giant=True, pmax=120.0, t_up=None, tmax=200.0, dt=0.05, t0=1.0):
        sc = S if giant else 1.0
        self.h_brain = 0.35 * sc; self.h_feet = 1.3 * sc
        self.hr = 70.0 / (S ** 0.75 ** 0 if False else (S ** 3) ** 0.25) if giant else 70.0
        self.t_up = t_up if t_up else (2.0 * np.sqrt(S) if giant else 2.0)
        self.tau = 3 * 60.0 / self.hr; self.pmax = pmax; self.t0 = t0
        P = 90.0; lost = 0.0; self.faint_t = None
        T, Pa, Pb, Pf, A, L = [], [], [], [], [], []
        t = 0.0; fallen_at = None
        while t < tmax:
            if self.faint_t is None:
                u = min(1.0, max(0.0, (t - t0) / self.t_up)); a = u * u * (3 - 2 * u)
            else:
                q = min(1.0, (t - self.faint_t) / (self.t_up * 0.5)); a = max(0.0, a_f * (1 - q * q))
            tgt = min(self.pmax, 70.0 + KM * self.h_brain * a) if a > 0.01 else 90.0
            P += (tgt - P) * dt / self.tau
            dip = 20.0 * a * np.exp(-max(0.0, t - t0) / self.tau)
            ph = P - dip; pb = ph - KM * self.h_brain * a; pf = ph + KM * self.h_feet * a
            if pb < 30: lost += dt
            else: lost = max(0.0, lost - 2 * dt)
            if self.faint_t is None and lost >= 7.0: self.faint_t = t; a_f = a
            T.append(t); Pa.append(ph); Pb.append(pb); Pf.append(pf); A.append(a); L.append(lost)
            t += dt
            if self.faint_t is not None and t > self.faint_t + self.t_up * 0.5 + 6: break
            if self.faint_t is None and t > t0 + self.t_up + 6 * self.tau and a >= 1: break
        self.T, self.Ph, self.Pb, self.Pf, self.A, self.L = map(np.array, (T, Pa, Pb, Pf, A, L))
        self.t_end = T[-1]
    def at(self, t, a): return float(np.interp(t, self.T, a))
if __name__ == '__main__':
    print('KM', KM, 'giant hr', 70 / (S ** 3) ** 0.25, 'need at heart', 70 + KM * 0.35 * S, 'feet', 70 + KM * 0.35 * S + KM * 1.3 * S, 'human feet', 93 + KM * 1.3)
    for name, kw in [('human', dict(giant=False)), ('giant human heart', dict(pmax=120)), ('giant giraffe', dict(pmax=250)), ('giant super quick', dict(pmax=900))]:
        m = Model(**kw); print(name, 'faint', m.faint_t, 'min brain', round(m.Pb.min()), 'max feet', round(m.Pf.max()), 'tend', round(m.t_end, 1), 'tau', round(m.tau, 1))
    for tu in (30, 60, 90, 120, 150, 180, 240):
        m = Model(pmax=900, t_up=tu, tmax=600); print('slow', tu, m.faint_t, round(m.Pb.min()), round(m.Pf.max()))
