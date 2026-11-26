import json, math, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva')
import mixlib as X
SR = X.SR; G = '/home/claude/wng'; mode = sys.argv[1]
def wind(n, g=0.35):
    c = X.rng.normal(0, 1, n); c = X.lp(X.lp(c, 40), 40); m = 0.6 + 0.4 * np.sin(np.arange(n) / SR * 0.7)
    return (c * m * g * 3).astype(np.float32)
def flap(g=0.3):
    n = int(0.22 * SR); t = np.arange(n) / SR; c = X.rng.normal(0, 1, n); c = X.lp(c, 12) * np.sin(np.pi * t / 0.22) ** 2
    return (c * g * 2).astype(np.float32)
def beep(f=1100, L=0.12, g=0.22):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.02) * g).astype(np.float32)
def chime(g=0.25):
    out = np.zeros(int(1.2 * SR), np.float32)
    for k, f in enumerate((880, 1109, 1319)):
        n = int(0.9 * SR); t = np.arange(n) / SR; X.put(out, k * 0.12, (np.sin(2 * np.pi * f * t) * np.exp(-t * 4) * g).astype(np.float32))
    return out
def battle_sfx(sts, ends, wps, n, fps=30, goal=None, flapping=True):
    """風の音、羽ばたきの音（飛んでいる間）、体力切れの警告音、着地の音、ゴールの音"""
    y = wind(n) * 0.5; done = set(); wdone = set(); gdone = False; last = -1
    for f, st in enumerate(sts):
        at = f / fps
        alive = st >= 0 and any(e is None or st < e for e in ends)
        if flapping and alive and at - last >= 0.45: X.put(y, at, flap(0.25)); last = at
        for i, w in enumerate(wps):
            if w is not None and st >= w and i not in wdone:
                wdone.add(i)
                for k in range(3): X.put(y, at + k * 0.22, beep())
        for i, e in enumerate(ends):
            if e is not None and st >= e and i not in done: done.add(i); X.put(y, at, X.thump(60, 0.4, 0.6))
        if goal and st >= goal and not gdone: gdone = True; X.put(y, at, chime())
    return y
if mode == 'main':
    order = ['title', 'data', 'power', 'rule', 'r1', 'res1', 'reveal', 'sweep', 'r2', 'res2', 'law', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    import wmodel as M, wscenes as S
    WPS = {'r1': [16.35, 16.35], 'r2': [281.0, None]}
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2'):
            j = json.load(open(f'{G}/c_{k}_st.json')); X.put(sfx, off, battle_sfx(j['st'], j['ends'], WPS[k], int(d * SR), goal=j['goal'], flapping=(k == 'r1')))
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/wng_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    sts = [max(0.0, (f / 30 - m['pre']) * m['rate']) if f / 30 >= m['pre'] else -1 for f in range(int(m['end0'] * 30))]
    sfx = np.zeros(n, np.float32); X.put(sfx, 0, battle_sfx(sts, m['ends'], [m['wp']], int(m['end0'] * SR)))
    X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/wng_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
