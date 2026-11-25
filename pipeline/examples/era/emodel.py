"""エラがあったら水中で暮らせる？（決定論モデル・目安）
・体重70kgの大人。休んでいるときの酸素 250mL/分（約3.5mL/kg/分）。酸素1mL = 1.429mg
・水にとける酸素（淡水・1気圧・飽和）：Benson & Krause の式（USGS DOTABLES と同じ）。20℃で約9.1mg/L
・エラ：通した水の酸素の67%を取りこむ（マスの安静時 %U=67%、Eom & Wood 2023）
・マス並みのエラ：体重1kgあたり 毎分0.3Lの水（同論文の安静時 V̇w≈300mL/kg/分）→ 70kgで 21L/分
・体にためておける（使える）酸素：約1L（仮定）
・体温：エラを通った血は水と同じ温度になる（教科書 Life 11e 図39.11）。心臓が送る血 5L/分、血の熱 3.8kJ/(L・℃)
  体の熱容量 70kg×3.47kJ/(kg・℃)、体が作る熱 = 酸素1Lあたり20.1kJ
"""
import math
import numpy as np
MASS = 70; VO2 = 250.0; MGML = 1.429; STORE = 1000.0; U = 0.67; TROUT = 0.3 * MASS
CB = 5.0 * 3.8; CBODY = MASS * 3.47; TB = 37.0
def DO(tc):
    T = tc + 273.15
    return math.exp(-139.34411 + 1.575701e5 / T - 6.642308e7 / T**2 + 1.2438e10 / T**3 - 8.621949e11 / T**4)
def need_water(tc, vo2=VO2): return vo2 * MGML / (DO(tc) * U)
def uptake(qw, tc): return min(VO2, qw * DO(tc) * U / MGML)
def t_to(Tx, tw, vo2=VO2):
    P = vo2 / 1000 * 20.1; Ts = tw + P / CB; tau = CBODY / CB
    return None if Tx <= Ts else tau * math.log((TB - Ts) / (Tx - Ts))
class Sim:
    """qw=None は息止め。T分まで、1/120分きざみ。列：t, 酸素の残り(mL), 体温, 取りこみ(mL/分)"""
    def __init__(self, qw, tw, T=12.0, dt=1 / 600):
        o = STORE; tb = TB; out = []
        for i in range(int(T / dt) + 1):
            t = i * dt; up = 0.0 if qw is None else uptake(qw, tw)
            out.append((t, max(0.0, o), tb, up))
            o -= (VO2 - up) * dt
            if qw is not None: tb += ((VO2 / 1000 * 20.1) - CB * (tb - tw)) / CBODY * dt
        self.a = np.array(out); self.dt = dt; self.qw = qw; self.tw = tw
    def at(self, t, k):
        i = int(min(len(self.a) - 1, max(0, round(t / self.dt)))); return float(self.a[i, k])
    def end(self):
        """限界の時刻：酸素0 か 体温28℃"""
        w = np.where((self.a[:, 1] <= 0) | (self.a[:, 2] <= 28.0))[0]; return float(self.a[w[0], 0]) if len(w) else None
if __name__ == '__main__':
    for tc in (10, 20, 26, 30, 36): print(tc, round(DO(tc), 2), 'need', round(need_water(tc), 1), 't35', t_to(35, tc), 't32', t_to(32, tc), 't28', t_to(28, tc))
    print('trout', TROUT, 'up36', uptake(TROUT, 36), 'up20', uptake(TROUT, 20))
    for qw, tw in ((None, 36), (TROUT, 36), (None, 20), (60, 20)):
        s = Sim(qw, tw); print(qw, tw, 'end', s.end(), 'T@4', s.at(4, 2), 'T@end', s.at(s.end() or 12, 2))
    for v in (250, 1000, 3000): print(v, round(need_water(20, v)), round(need_water(20, v) / TROUT, 1), round(need_water(20, v) / 2))
    print('air ratio', 278 / DO(20), 'P W', VO2 / 1000 * 20.1 * 1000 / 60, 'loss W at 20', CB * 17 * 1000 / 60)
