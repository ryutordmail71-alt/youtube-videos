import json, sys, glob
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/zmb')
import mixlib as X
G = '/home/claude/zmb'; SR = X.SR; mode = sys.argv[1]
ORDER = ['title', 'data', 'rule', 'r1', 'res1', 'secret', 'table', 'r3', 'res3', 'outro']
def whoosh(L=0.7, g=0.22):
    n = int(L * SR); t = np.arange(n) / SR; y = X.lp(X.rng.normal(0, 1, n), 20) * np.sin(np.pi * t / L) ** 2
    return (y * g).astype(np.float32)
def drone(L, f0=55, g=0.08, *a, **k):
    """（2026-11-27 変更）低いうなり・ザラザラしたノイズは音割れっぽく聞こえるので使わない。代わりに小さく澄んだ和音（110Hz以上）"""
    n = int(L * SR); t = np.arange(n) / SR; f = max(110.0, float(f0) * 2)
    y = np.sin(2 * np.pi * f * t) * 0.6 + np.sin(2 * np.pi * f * 1.5 * t) * 0.3 + np.sin(2 * np.pi * f * 2 * t) * 0.15
    env = np.minimum(1, t / 1.5) * np.minimum(1, np.maximum(0, L - t) / 1.5); return (y * env * g * 0.5).astype(np.float32)
def groan(L=1.4, g=0.16):
    n = int(L * SR); t = np.arange(n) / SR; f = 85 * (1 - 0.25 * t / L) * (1 + 0.03 * np.sin(2 * np.pi * 6 * t)); ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sign(np.sin(ph)) * 0.4 + np.sin(ph)) + X.lp(X.rng.normal(0, 1, n), 3) * 0.5
    y = X.lp(y.astype(np.float32), 10); env = np.sin(np.pi * t / L) ** 1.5
    return (y * env * g).astype(np.float32)
def tick(g=0.18):
    n = int(0.05 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120) * g).astype(np.float32)
def hit():
    return (X.boom(2.0, 38, 0.5)).astype(np.float32)
if mode == 'main':
    meta = {}
    for f in glob.glob(f'{G}/scenes_*.json'): meta.update(json.load(open(f)))
    clips = [f'{G}/c_{k}.mp4' for k in ORDER]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(ORDER, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        X.put(sfx, off, whoosh())
        if k == 'title':
            X.put(sfx, off + 0.1, groan()); X.put(sfx, off + 0.3, drone(d - 0.3, 49, 0.08))
            for b in np.arange(0.5, d - 1, 1.1): X.put(sfx, off + b, X.heartbeat(50, 0.26, 0.35))
        if k == 'r1':
            s = json.load(open(f'{G}/c_r1_st.json')); tj = s['t_jump']
            X.put(sfx, off + tj - 0.3, groan(1.2, 0.2))
            for h in range(28): X.put(sfx, off + tj + h * 9.0 / 27, tick())
            X.put(sfx, off + tj + 9.0, hit())
        if k == 'secret': X.put(sfx, off + 0.3, drone(d - 0.5, 44, 0.06))
        if k == 'r3':
            s = json.load(open(f'{G}/c_r3_st.json')); tj = s['t_jump']
            X.put(sfx, off + tj - 0.3, groan(1.5, 0.2)); X.put(sfx, off + tj, drone(d - tj, 41, 0.12))
            for b in np.arange(tj, d - 1, 0.9): X.put(sfx, off + b, X.heartbeat(48, 0.24, 0.3))
        if k == 'res3': X.put(sfx, off + 0.4, hit())
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/zmb_main.mp4', '1100k', bgm_gain=0.18)
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    X.put(sfx, 0.0, groan(1.2, 0.2)); X.put(sfx, 0.0, drone(T, 46, 0.08))
    for b in np.arange(0.3, 4.5, 1.0): X.put(sfx, b, X.heartbeat(50, 0.26, 0.35))
    for h in range(28): X.put(sfx, m['tj'] + h * 6.0 / 27, tick())
    X.put(sfx, m['tj'] + 6.0, hit()); X.put(sfx, 12.0, whoosh()); X.put(sfx, 20.3, whoosh()); X.put(sfx, 20.5, hit())
    for b in np.arange(12.6, 20.0, 0.8): X.put(sfx, b, X.heartbeat(48, 0.24, 0.3))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/zmb_short.mp4', '2500k', maxrate='4000k', bgm_gain=0.18)
print('mixed', mode)
