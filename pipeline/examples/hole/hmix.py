import json, math, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/hole')
import mixlib as X
import hscenes as S
SR = X.SR; G = '/home/claude/hole'; mode = sys.argv[1]
def chime(g=0.25):
    n = int(1.2 * SR); t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for k, f in enumerate((880, 1320)):
        s = int(k * 0.12 * SR); tt = t[:n - s]; y[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3)
    return (y * g).astype(np.float32)
def wind(n, amp):
    """amp：フレームごと（30fps）の強さ 0..1。高い速さほど明るい風切り音"""
    base = X.rng.normal(0, 1, n).astype(np.float32); lo = X.lp(base, 40); hi = base - X.lp(base, 6)
    a = np.interp(np.arange(n) / SR * 30, np.arange(len(amp)), amp).astype(np.float32)
    return (lo * 1.4 * a + hi * 0.15 * a * a) * 0.5
def battle_sfx(pair, sts, n, ffrom=None):
    amp = []; arrived = {}; y = np.zeros(n, np.float32); stopped = False
    for f, st in enumerate(sts):
        if st < 0: amp.append(0.0); continue
        vs = []
        for who in pair:
            x, v, g, arr = S.person(S.KIND[who], st); vs.append(v)
            if arr and who not in arrived: arrived[who] = f; X.put(y, f / 30, chime())
            if who == 'air' and st >= S.AIR_C and not stopped: stopped = True; X.put(y, f / 30, X.boom(1.6, 40, 0.5))
        amp.append(min(1.0, max(vs) / 9900) ** 0.7 + 0.08)
    X.put(y, (next(i for i, s in enumerate(sts) if s >= 0)) / 30, X.whistle() * 0.6)
    if ffrom is not None:   # 早送りの音（上がっていく音）
        L = 1.2; m = int(L * SR); t = np.arange(m) / SR; f = 200 + 900 * t / L
        X.put(y, ffrom, (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, (L - t) / 0.2) * 0.15).astype(np.float32))
    return y + wind(n, np.array(amp)) * 0.6
if mode == 'main':
    order = ['title', 'data', 'rule', 'r1', 'res1', 'reveal', 'sweep', 'r2', 'res2', 'real', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2'):
            j = json.load(open(f'{G}/c_{k}_st.json')); pair = ('uni', 'prem') if k == 'r1' else ('vac', 'air')
            X.put(sfx, off, battle_sfx(pair, j['st'], int(d * SR), S.R2_HOLD if k == 'r2' else None))
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        if k == 'real': X.put(sfx, off + 0.3, X.boom(2.5, 32, 0.6))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/hole_main.mp4', '1100k')
else:
    import hshort as SH
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    sts = [SH.st_of(f / 30) if f / 30 < m['end0'] else -1 for f in range(int(m['end0'] * 30))]
    sfx = np.zeros(n, np.float32); X.put(sfx, 0, battle_sfx(('vac', 'air'), sts, int(m['end0'] * SR)))
    X.put(sfx, 0.0, X.boom(1.2, 45, 0.6)); X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/hole_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
