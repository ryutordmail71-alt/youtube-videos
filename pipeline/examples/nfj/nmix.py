import json, sys, math, glob
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/nfj')
import mixlib as X
import nbase as B
G = '/home/claude/nfj'; SR = X.SR; mode = sys.argv[1]
ORDER = ['title', 'data', 'rule', 'r1', 'res1', 'secret', 'scale', 'table', 'r3', 'res3', 'outro']
def whoosh(L=0.5, g=0.25):
    n = int(L * SR); t = np.arange(n) / SR; y = X.lp(X.rng.normal(0, 1, n), 12) * np.sin(np.pi * t / L) ** 2
    return (y * g).astype(np.float32)
def rise(L=3.0):
    n = int(L * SR); t = np.arange(n) / SR; f = 200 + 900 * (t / L) ** 1.5; ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, t / 0.05) * (1 - t / L) ** 0.5
    return ((np.sin(ph) * 0.12 + X.lp(X.rng.normal(0, 1, n), 6) * 0.15) * env).astype(np.float32)
def boing(f0=500, L=0.35):
    n = int(L * SR); t = np.arange(n) / SR; f = f0 * (1 + 0.6 * np.exp(-t * 12)) * (1 + 0.04 * np.sin(2 * np.pi * 30 * t)); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 7) * 0.22).astype(np.float32)
def sad():
    out = []
    for i, f in enumerate([392, 370, 349, 311]):
        L = 0.35 if i < 3 else 0.9; n = int(L * SR); t = np.arange(n) / SR; ph = 2 * np.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * np.pi * 5 * t))) / SR
        y = (np.sign(np.sin(ph)) * 0.3 + np.sin(ph)) * np.minimum(1, t / 0.02) * np.minimum(1, (L - t) / 0.08); out.append(X.lp(y.astype(np.float32), 4) * 0.12)
    return np.concatenate(out).astype(np.float32)
if mode == 'main':
    meta = {}
    for f in glob.glob(f'{G}/scenes_*.json'): meta.update(json.load(open(f)))
    clips = [f'{G}/c_{k}.mp4' for k in ORDER]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(ORDER, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        X.put(sfx, off, whoosh())
        if k == 'r1':
            s = json.load(open(f'{G}/c_r1_st.json')); tj = s['t_jump']
            X.put(sfx, off + tj - 0.8, X.whistle()); X.put(sfx, off + tj, boing(300)); X.put(sfx, off + tj, rise(s['TR']))
        if k == 'r3':
            s = json.load(open(f'{G}/c_r3_st.json')); tj = s['t_jump']; sl = s['slow']
            X.put(sfx, off + tj - 0.8, X.whistle()); X.put(sfx, off + tj, boing(420))
            for v in (B.V_FLEA, B.V_HUM, B.V_HOP): X.put(sfx, off + tj + 2 * v / B.g / sl, X.thump(70, 0.35, 0.7, 14))
            c3 = [t for t, key in meta[k][1] if key == 'r3c'][0]; X.put(sfx, off + c3 + 0.9, sad())
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/nfj_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    for h in m['hops']: X.put(sfx, h, boing(700, 0.25)); X.put(sfx, h + 0.6, X.thump(120, 0.15, 0.3, 30))
    X.put(sfx, m['tj'], boing(300)); X.put(sfx, m['tj'], rise(3.4)); X.put(sfx, 15.5, whoosh()); X.put(sfx, 22.0, whoosh())
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/nfj_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
