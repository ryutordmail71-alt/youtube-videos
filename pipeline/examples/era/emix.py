import json, math, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva')
import mixlib as X
SR = X.SR; G = '/home/claude/era'; mode = sys.argv[1]
def bubble_snd(g=0.25):
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 500 + 1800 * t / 0.12
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * g).astype(np.float32)
def splash(g=0.5):
    n = int(0.9 * SR); t = np.arange(n) / SR; c = X.rng.normal(0, 1, n) * np.exp(-t * 6); return ((c - X.lp(c, 5)) * 0.5 * g).astype(np.float32)
def beep(f=1200, L=0.12, g=0.22):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.02) * g).astype(np.float32)
def underwater(n):
    return (X.lp(X.lp(X.rng.normal(0, 1, n), 200), 200) * 1.2).astype(np.float32)
def battle_sfx(sts, ends, n, fps=30, start_at=None):
    """もぐる音、ときどき泡、心臓の音（ゆっくり）、限界の警告音と水から上がる音"""
    y = underwater(n) * 0.5; started = False; done = set()
    rng = np.random.default_rng(3)
    for f, st in enumerate(sts):
        at = f / fps
        if st >= 0 and not started: X.put(y, at, splash()); started = True
        if st >= 0 and rng.random() < 0.05: X.put(y, at, bubble_snd(0.15))
        if st >= 0 and f % 24 == 0: X.put(y, at, X.heartbeat(55, 0.25, 0.25, 16))
        for i, e in enumerate(ends):
            if e is not None and st >= e and i not in done:
                done.add(i)
                for k in range(3): X.put(y, at + k * 0.22, beep())
                X.put(y, at + 0.9, splash(0.35))
    return y
if mode == 'main':
    order = ['title', 'data', 'fish', 'rule', 'r1', 'res1', 'reveal', 'sweep', 'r2', 'res2', 'heat', 'temp', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2'):
            j = json.load(open(f'{G}/c_{k}_st.json')); X.put(sfx, off, battle_sfx(j['st'], j['ends'], int(d * SR)))
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/era_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    sts = [max(0.0, (f / 30 - m['pre']) * m['rate']) if f / 30 < m['end0'] else -1 for f in range(int(m['end0'] * 30))]
    sfx = np.zeros(n, np.float32); X.put(sfx, 0, battle_sfx(sts, m['ends'], int(m['end0'] * SR)))
    X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/era_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
