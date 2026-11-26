"""地球の中心まで穴を掘って飛び込んだら（決定論モデル・目安）
・PREM（Dziewonski & Anderson 1981）の密度で重力 g(r) を計算
・均一な地球：g = g0 r/R
・穴は北極→南極（自転の影響なし）、壁は熱・圧力に耐える（空想）
"""
import math
import numpy as np
G = 6.674e-11; R = 6371e3
def rho_prem(r):
    x = r / R; rk = r / 1e3
    if rk < 1221.5: v = 13.0885 - 8.8381 * x * x
    elif rk < 3480: v = 12.5815 - 1.2638 * x - 3.6426 * x**2 - 5.5281 * x**3
    elif rk < 5701: v = 7.9565 - 6.4761 * x + 5.5283 * x**2 - 3.0807 * x**3
    elif rk < 5771: v = 5.3197 - 1.4836 * x
    elif rk < 5971: v = 11.2494 - 8.0298 * x
    elif rk < 6151: v = 7.1089 - 3.8045 * x
    elif rk < 6346.6: v = 2.6910 + 0.6924 * x
    elif rk < 6356: v = 2.9
    elif rk < 6368: v = 2.6
    else: v = 1.02
    return v * 1000
N = 6372; rs = np.linspace(0, R, N); dr = rs[1] - rs[0]
rho = np.array([rho_prem(r) for r in rs])
Mr = np.concatenate([[0], np.cumsum(4 * math.pi * ((rs[1:] + rs[:-1]) / 2)**2 * (rho[1:] + rho[:-1]) / 2 * dr)])
gp = np.where(rs > 0, G * Mr / np.maximum(rs, 1)**2, 0)
M = Mr[-1]; G0 = gp[-1]; RHOBAR = M / (4 / 3 * math.pi * R**3)
def g_prem(r): return float(np.interp(abs(r), rs, gp))
def g_uni(r, g0=None): return (g0 or G0) * abs(r) / R
def fall(gf, air=None, T=3e6, dt=0.5, stop_on_exit=True):
    """x：中心からの位置（+R から出発）。air：終端速度(地表) m/s。返り値：t, x, v の配列"""
    x = R; v = 0.0; t = 0.0; out = [(0, x, 0)]
    while t < T:
        a = -math.copysign(gf(x), x)
        if air:
            vt = air * math.sqrt(max(gf(x), 1e-6) / G0); a -= 9.81 * 0 + gf(x) * math.copysign((v / vt)**2, v) if vt > 0 else 0
        v += a * dt; x += v * dt; t += dt; out.append((t, x, v))
        if stop_on_exit and x <= -R: break
        if air and t > 1000 and abs(v) < 1e-3 and abs(x) < 1e3: break
    return np.array(out)
def period_uniform(rho_mean): return math.pi / math.sqrt(4 / 3 * math.pi * G * rho_mean)
if __name__ == '__main__':
    print('M', M, 'g0', G0, 'rhobar', RHOBAR, 'gmax', gp.max(), 'at', rs[gp.argmax()] / 1e3, 'depth', (R - rs[gp.argmax()]) / 1e3)
    print('rho center', rho[0], 'surface', rho_prem(6360e3))
    for name, gf in (('uni', lambda r: g_uni(r, 9.81)), ('prem', g_prem)):
        a = fall(gf); tc = a[np.argmin(np.abs(a[:, 1])), 0]
        print(name, 'one-way min', a[-1, 0] / 60, 'center min', tc / 60, 'vmax', np.abs(a[:, 2]).max(), 'km/h', np.abs(a[:, 2]).max() * 3.6)
    for nm, d in (('earth', 5.51), ('moon', 3.34), ('mars', 3.93), ('jupiter', 1.33), ('saturn', 0.687), ('sun', 1.41), ('iron', 7.87), ('water', 1.0)):
        print(nm, period_uniform(d * 1000) / 60)
    # 空気：終端速度 55 m/s、空気の密さは地表と同じ（仮定）
    vt0 = 55; tcen = 2 * R / vt0; print('air analytic center (uniform) h', tcen / 3600, 'days', tcen / 86400)
    # PREM 版：積分 dr / (vt0 sqrt(g/g0))
    tt = np.sum(dr / (vt0 * np.sqrt(np.maximum(gp[1:], 1e-3) / G0))); print('air prem center h', tt / 3600, tt / 86400)
# エネルギー保存で正確に：v(r)=sqrt(2∫_r^R g dr)
def speed_profile(gf_arr):
    W = np.concatenate([[0], np.cumsum((gf_arr[1:] + gf_arr[:-1]) / 2 * dr)])  # ∫0^r g
    return np.sqrt(np.maximum(0, 2 * (W[-1] - W)))
VP = speed_profile(gp); VU = speed_profile(G0 * rs / R)
def t_center(V):
    m = (V[1:] + V[:-1]) / 2; return float(np.sum(dr / np.maximum(m, 1e-9)))
def time_profile(V):
    """地表から深さ d までの時間（rs の順＝中心→地表 に対応する配列）"""
    m = (V[1:] + V[:-1]) / 2; seg = dr / np.maximum(m, 1e-9); cum = np.concatenate([[0], np.cumsum(seg[::-1])])[::-1]
    return cum  # cum[i] = 地表から r=rs[i] までの時間
TP = time_profile(VP); TU = time_profile(VU)
def state(t, prem=True):
    """飛びこんでから t 秒後の位置（中心からの符号付き距離, +が出発側）、速さ、重力"""
    TT = TP if prem else TU; V = VP if prem else VU; g = gp if prem else G0 * rs / R
    tc = TT[0]; tt = t % (4 * tc); sgn = 1
    if tt > 2 * tc: tt = 4 * tc - tt   # 戻り（往復）
    if tt <= tc: r = float(np.interp(tt, TT[::-1], rs[::-1])); x = r
    else: r = float(np.interp(2 * tc - tt, TT[::-1], rs[::-1])); x = -r
    return x, float(np.interp(r, rs, V)), float(np.interp(r, rs, g))
if __name__ == '__main__':
    print('PREM center', t_center(VP) / 60, 'one-way', 2 * t_center(VP) / 60, 'vmax', VP[0], VP[0] * 3.6)
    print('UNI center', t_center(VU) / 60, 'one-way', 2 * t_center(VU) / 60, 'vmax', VU[0])
    for d in (100, 1000, 2891, 5150, 6371):
        i = int(round((R - d * 1e3) / dr)); print('depth', d, 'tP min', TP[i] / 60, 'vP', VP[i], 'gP', gp[i], '| tU', TU[i] / 60, 'vU', VU[i])
VT0 = 55.0   # スカイダイバーの終端速度（地表、約200km/h）
def air_fall(T=3 * 86400, dt=0.5):
    x = R; v = 0.0; t = 0.0; out = [(0.0, x, 0.0)]; k = 0
    while t < T:
        g = g_prem(x); a = -math.copysign(g, x) - G0 * (v / VT0)**2 * math.copysign(1, v)
        v += a * dt; x += v * dt; t += dt; k += 1
        if k % 20 == 0: out.append((t, x, v))
    return np.array(out)
_AIR = None
def air_state(t):
    global _AIR
    if _AIR is None:
        import os
        f = '/home/claude/hole/air.npy'
        if os.path.exists(f): _AIR = np.load(f)
        else: _AIR = air_fall(); np.save(f, _AIR)
    a = _AIR; return float(np.interp(t, a[:, 0], a[:, 1])), float(abs(np.interp(t, a[:, 0], a[:, 2])))
