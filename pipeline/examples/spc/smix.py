import json, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/spc')
import mixlib as X
SR = X.SR; G = '/home/claude/spc'; mode = sys.argv[1]
rng = np.random.default_rng(5)
def beep(f, L=0.16, g=0.15):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.03) * np.minimum(1, t / 0.005) * g).astype(np.float32)
def hiss(L=2.0, g=0.25):
    """空気が抜ける音"""
    n = int(L * SR); t = np.arange(n) / SR; y = rng.normal(0, 1, n).astype(np.float32); y = y - X.lp(y, 6)
    return (y * np.minimum(1, t / 0.03) * np.exp(-t * 1.6) * g).astype(np.float32)
def drone(L, f=55, g=0.08):
    n = int(L * SR); t = np.arange(n) / SR; y = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t + np.sin(t * 0.7)) + X.lp(rng.normal(0, 1, n), 200) * 3
    env = np.minimum(1, t / 1.0) * np.minimum(1, np.maximum(0, L - t) / 1.0); return (y * env * g).astype(np.float32)
def pop(g=0.08):
    n = int(0.05 * SR); t = np.arange(n) / SR; f = rng.uniform(600, 1400); return (np.sin(2 * np.pi * f * t * (1 + 3 * t)) * np.exp(-t * 90) * g).astype(np.float32)
def tick(g=0.12):
    n = int(0.03 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 200) * g).astype(np.float32)
def whoosh(L=0.8, g=0.2):
    n = int(L * SR); t = np.arange(n) / SR; y = X.lp(rng.normal(0, 1, n), 20) * 3; env = np.sin(np.pi * t / L) ** 2; return (y * env * g).astype(np.float32)
def round_sfx(y, off, j, d, kind):
    for o in j['ons'][:3]: X.put(y, off + o, beep(660))
    X.put(y, off + j['tf'], beep(990, 0.3, 0.17))
    if kind == 'r1':
        X.put(y, off + j['tf'] + 0.4, hiss(2.5, 0.3))
        for k in range(30): X.put(y, off + j['tf'] + 1.2 + rng.uniform(0, d - j['tf'] - 2), pop(0.06))
    elif kind == 'r2':
        for k in range(int((d - j['tf'] - 0.6) * 2)): X.put(y, off + j['tf'] + 0.6 + k * 0.5, tick(0.1))
    else:
        t = j['tf'] + 0.6; k = 0
        while t < d - 0.5:
            X.put(y, off + t, X.heartbeat(50, 0.28, 0.35 + 0.02 * k, 12)); t += 0.85 + 0.03 * k; k += 1
if mode == 'main':
    order = ['title', 'jingle', 'data', 'rule', 'r1', 'res1', 'rh1', 'r2', 'wow2', 'res2', 'reveal', 'sweep', 'rh2', 'r3', 'wow3', 'res3', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2', 'r3', 'ins'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2', 'r3'): round_sfx(sfx, off, json.load(open(f'{G}/c_{k}_t.json')), d, k)
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.4))
        if k == 'title': X.put(sfx, 0.0, drone(d, 55, 0.07)); X.put(sfx, 0.05, whoosh(1.2, 0.15))
        if k == 'data': X.put(sfx, off, whoosh(0.8, 0.2))
        if k == 'jingle': X.put(sfx, off + 0.05, beep(988, 0.12, 0.18)); X.put(sfx, off + 0.17, beep(1318, 0.35, 0.18))
        if k in ('wow2', 'wow3'): X.put(sfx, off + 0.0, X.boom(1.4, 42, 0.55)); X.put(sfx, off + 0.0, X.thump(70, 0.4, 0.7))
        if k in ('rh1', 'rh2'): X.put(sfx, off + 0.0, whoosh(0.9, 0.25)); X.put(sfx, off + 0.05, X.thump(50, 0.6, 0.5, 6))
        if k in ('reveal', 'sweep'): X.put(sfx, off, drone(d, 49, 0.06))
        if k == 'reveal': X.put(sfx, off + 0.05, X.boom(1.5, 38, 0.35))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/spc_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    X.put(sfx, 0.0, hiss(1.2, 0.25)); X.put(sfx, 0.3, X.thump(60, 0.5, 0.6))
    s0, s1, s2 = m['steps']
    X.put(sfx, s0, whoosh(0.6, 0.2)); X.put(sfx, s0 + 0.3, hiss(2.0, 0.2))
    for k in range(10): X.put(sfx, s0 + 1 + k * 0.4, pop(0.05))
    X.put(sfx, s1, whoosh(0.6, 0.2))
    for k in range(12): X.put(sfx, s1 + 0.5 + k * 0.5, tick(0.08))
    X.put(sfx, s2, whoosh(0.6, 0.2))
    for k in range(5): X.put(sfx, s2 + 0.3 + k * 0.85, X.heartbeat(50, 0.28, 0.4, 12))
    X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.4))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/spc_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
