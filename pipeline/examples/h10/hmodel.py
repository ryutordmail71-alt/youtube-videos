"""心臓がN個あったら？（決定論モデル・目安）
・1個の心臓が全力で送る血：約25L/分（よく鍛えた人の目安）。N個なら 25N L/分（仮定：全部が肺を通る）
・肺の毛細血管にいる血：全力運動時 約146mL（仮定）→ 1個なら通過時間 約0.35秒（安静時は約0.75秒）
・酸素の受け取り：約0.25秒でほぼ満タン（95%）→ 1−exp(−t/0.083)
・動脈の酸素：満タンで 200mL/L、戻ってくる血 40mL/L（全力運動時の目安・仮定）
・肺動脈の平均圧 = 15 + 1.5×(血の量−5)（Naeije ほか 2013 の健康な人の傾き 1.5 mmHg/(L/分)）
・肺の毛細血管の圧力 ≒ (肺動脈圧 + 左心房圧10)/2（仮定）。50を超えると血がにじみ、取りこみ効率が下がる（仮定）
"""
import numpy as np
QH = 25.0; VC = 0.146; TAU = 0.25 / 3.0; CMAX = 200.0; CV = 40.0; LIM = 50.0
def steady(N, q=None):
    Q = QH * N if q is None else q; tt = VC / (Q / 60.0); f = 1 - np.exp(-tt / TAU)
    ca = CV + (CMAX - CV) * f; o2 = Q * (ca - CV) / 1000.0
    pa = 15 + 1.5 * (Q - 5); pc = (pa + 10) / 2
    return dict(Q=Q, tt=tt, sat=ca / CMAX * 100, o2=o2, pa=pa, pc=pc)
class Run:
    """スタートから全力まで5秒で上がる。T秒ぶん"""
    def __init__(self, N, T=24.0, dt=1 / 30):
        self.N = N; ts = np.arange(0, T, dt); dmg = 0.0; out = []
        for t in ts:
            r = min(1.0, t / 5.0); r = r * r * (3 - 2 * r); Q = 5 * N + (QH * N - 5 * N) * r
            s = steady(N, Q)
            if s['pc'] > LIM: dmg = min(0.85, dmg + (s['pc'] - LIM) / LIM / 6 * dt)
            o2 = s['o2'] * (1 - dmg); sat = (CV + (s['sat'] / 100 * CMAX - CV) * (1 - dmg)) / CMAX * 100
            out.append((t, Q, s['tt'], sat, o2, s['pc'], dmg))
        self.a = np.array(out); self.T = T
    def at(self, t, k):
        i = int(min(len(self.a) - 1, max(0, round(t * 30)))); return float(self.a[i, k])
    def leak_t(self):
        w = np.where(self.a[:, 6] > 0.01)[0]; return float(self.a[w[0], 0]) if len(w) else None
if __name__ == '__main__':
    for N in (1, 2, 3, 4, 5, 10):
        s = steady(N); print(N, {k: round(v, 3) for k, v in s.items()})
    for N in (2, 3, 10):
        R = Run(N); print('run', N, 'leak', R.leak_t(), 'o2@5', round(R.at(5, 4), 2), 'o2@12', round(R.at(12, 4), 2), 'o2@20', round(R.at(20, 4), 2), 'sat20', round(R.at(20, 3)))
    R3 = Run(3); R2 = Run(2)
    for t in np.arange(5, 24, 1): print(t, round(R3.at(t, 4), 2), round(R2.at(t, 4), 2))
