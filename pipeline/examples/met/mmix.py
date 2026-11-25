import json, sys, glob
import numpy as np
sys.path.insert(0, '/home/claude/gva')
import mixlib as X
G = '/home/claude/met'; SR = X.SR; mode = sys.argv[1]
ORDER = ['title', 'data', 'rule', 'r1', 'res1', 'r2', 'res2', 'secret', 'r3', 'res3', 'odds', 'outro']
def whoosh(L=0.7, g=0.22):
    n = int(L * SR); t = np.arange(n) / SR; y = X.lp(X.rng.normal(0, 1, n), 20) * np.sin(np.pi * t / L) ** 2
    return (y * g).astype(np.float32)
def fallwhine(L, g=0.12):
    n = int(L * SR); t = np.arange(n) / SR; f = 900 - 650 * t / L; ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * 0.3 + X.lp(X.rng.normal(0, 1, n), 4) * 0.7; return (y * np.minimum(1, t / 0.5) * g).astype(np.float32)
def drone(L, f0=45, g=0.08):
    n = int(L * SR); t = np.arange(n) / SR; y = np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 1.5 * t)
    return (y * np.minimum(1, t / 1.5) * np.minimum(1, (L - t) / 1.5) * g).astype(np.float32)
BIG = {'r1': (0.5, 50), 'r2': (0.9, 40), 'r3': (1.2, 32)}
if mode == 'main':
    meta = {}
    for f in glob.glob(f'{G}/scenes_*.json'): meta.update(json.load(open(f)))
    clips = [f'{G}/c_{k}.mp4' for k in ORDER]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(ORDER, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        X.put(sfx, off, whoosh())
        if k in BIG:
            s = json.load(open(f'{G}/c_{k}_st.json')); X.put(sfx, off + s['t_jump'], fallwhine(s['t_burst'] - s['t_jump']))
            g, f0 = BIG[k]; X.put(sfx, off + s['t_burst'], X.boom(3.0, f0, g))
        if k in ('title', 'odds'): X.put(sfx, off + 0.3, drone(d - 0.5))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/met_main.mp4', '1100k', bgm_gain=0.2)
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    X.put(sfx, 0.0, fallwhine(6.6)); X.put(sfx, 6.6, X.boom(2.5, 50, 0.5)); X.put(sfx, 10.5, fallwhine(3.1)); X.put(sfx, 13.6, X.boom(3.0, 40, 0.9))
    X.put(sfx, 18.5, fallwhine(3.5)); X.put(sfx, 22.0, whoosh()); X.put(sfx, 22.0, drone(T - 22.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/met_short.mp4', '2500k', maxrate='4000k', bgm_gain=0.2)
print('mixed', mode)
