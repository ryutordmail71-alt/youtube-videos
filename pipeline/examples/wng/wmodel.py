"""翼があったら人間は飛べる？（決定論モデル・目安）"""
import math
import numpy as np
RHO = 1.225; G = 9.81; K = 1.2; ETA = 0.8; CDA = 0.1; CD0 = 0.02; CLMAX = 1.5
BODY = 60.0; WKG_PER_M = 1.0
PEAK = 12.7 * BODY; MEAN30 = 8.5 * BODY; CP = 3.5 * BODY; WPRIME = (MEAN30 - CP) * 30
def mass(b): return BODY + WKG_PER_M * b
def preq_v(b, ar, v, m=None):
    m = m or mass(b); Sd = math.pi * b * b / 4; Sw = b * b / ar
    pi = K * (m * G) ** 2 / (2 * RHO * v * Sd); pp = 0.5 * RHO * v ** 3 * CDA; pr = 0.5 * RHO * v ** 3 * Sw * CD0
    return (pi + pp + pr) / ETA
def vstall(b, ar, m=None):
    m = m or mass(b); return math.sqrt(2 * m * G / (RHO * (b * b / ar) * CLMAX))
def pmin(b, ar, m=None):
    vs = vstall(b, ar, m) * 1.15; best = None
    for v in np.arange(max(vs, 2), 60, 0.05):
        p = preq_v(b, ar, v, m)
        if best is None or p < best[0]: best = (p, v)
    return best
def glide(b, ar, m=None):
    """パワー0で滑空：沈む速さ（最小沈下） = P(η=1)/mg"""
    m = m or mass(b); p, v = pmin(b, ar, m); return p * ETA / (m * G), v
if __name__ == '__main__':
    print('GA check', pmin(29.77, 19.7, 98))
    for name, b, ar in [('pigeon', 3.6, 7), ('eagle', 5.0, 6.5), ('bustard', 4.1, 6), ('albatross', 5.8, 15), ('8m', 8, 12), ('12m', 12, 15), ('20m', 20, 18), ('30m', 30, 19.7)]:
        p, v = pmin(b, ar); s, _ = glide(b, ar)
        print(name, b, 'm', round(mass(b),1), 'P', round(p), 'W at', round(v,1), 'm/s', 'sink', round(s,2), 'L/D', round(v/s,1), 'muscle kg@89', round(p*ETA/89,1))
    print('PEAK', PEAK, 'MEAN30', MEAN30, 'CP', CP, 'Wp', WPRIME)

H0 = 30.0
class Flight:
    """幅b・細長さarの翼。cp：長く続けられる力(W)。高さH0から、必要なパワーを出せるだけ出す。
    列：t秒, 高さm, 距離m, 出している力W, 体力の残り(0-1)"""
    def __init__(self, b, ar, cp=CP, wp=WPRIME, peak=PEAK, T=8000, dt=0.05):
        self.b = b; self.ar = ar; self.m = mass(b); self.preq, self.v = pmin(b, ar); self.cp = cp
        h = H0; x = 0.0; w = wp; out = []; t = 0.0
        while t <= T:
            want = min(self.preq, peak)
            if want > cp and w > 0: p = want
            else: p = min(want, cp)
            out.append((t, max(0.0, h), x, p, max(0.0, w / wp)))
            if h <= 0: break
            if p > cp: w -= (p - cp) * dt
            h -= (self.preq - p) * ETA / (self.m * G) * dt; x += self.v * dt; t += dt
        self.a = np.array(out); self.dt = dt; self.end = float(self.a[-1, 0]) if self.a[-1, 1] <= 0 else None
    def at(self, t, k):
        i = int(min(len(self.a) - 1, max(0, round(t / self.dt)))); return float(self.a[i, k])
if __name__ == '__main__':
    for b, ar, cp in [(4.0, 6, CP), (8, 10, CP), (12, 14, CP), (20, 18, CP), (30, 19.7, CP), (30, 19.7, 300)]:
        f = Flight(b, ar, cp); g = glide(b, ar)
        print(b, 'P', round(f.preq), 'v', round(f.v, 1), 'end', f.end, 'dist', round(f.a[-1, 2]), 'glide-only s', round(H0 / g[0], 1), round(H0 / g[0] * g[1]), 'muscle kg', round(f.preq / 89, 1), round(f.preq / 89 / 60 * 100))
