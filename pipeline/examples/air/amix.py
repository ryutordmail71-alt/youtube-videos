import json, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/air')
import mixlib as X
SR = X.SR; G = '/home/claude/air'; mode = sys.argv[1]
def beep(f, L=0.16, g=0.18):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.03) * g).astype(np.float32)
def powerdown(L=1.6, g=0.3):
    """電気が落ちる音（高い音が下がっていく）"""
    n = int(L * SR); t = np.arange(n) / SR; f = 900 * np.exp(-t * 2.2) + 40
    ph = 2 * np.pi * np.cumsum(f) / SR; y = np.sin(ph) * 0.6 + np.sign(np.sin(ph)) * 0.15
    return (y * np.exp(-t * 1.1) * g).astype(np.float32)
def glitch(L=0.5, g=0.18, seed=1):
    """デジタルなノイズ"""
    rng = np.random.default_rng(seed); n = int(L * SR); y = np.zeros(n, np.float32); i = 0
    while i < n:
        k = int(rng.uniform(0.01, 0.05) * SR); f = rng.choice([400, 800, 1600, 2400])
        t = np.arange(min(k, n - i)) / SR; y[i:i + len(t)] = np.sign(np.sin(2 * np.pi * f * t)) * rng.uniform(0.3, 1); i += k + int(rng.uniform(0, 0.03) * SR)
    return (X.lp(y, 6) * g * 0.7).astype(np.float32)
def servo(L=0.6, g=0.12):
    n = int(L * SR); t = np.arange(n) / SR; f = 180 + 120 * np.sin(2 * np.pi * 1.5 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 40 * t)); env = np.minimum(1, t / 0.05) * np.minimum(1, (L - t) / 0.1)
    return (y * env * g).astype(np.float32)
def hum(L, g=0.06):
    n = int(L * SR); t = np.arange(n) / SR; y = np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)
    env = np.minimum(1, t / 0.5) * np.minimum(1, np.maximum(0, L - t) / 0.5); return (y * env * g).astype(np.float32)
def round_sfx(y, off, j, d, kind):
    for o in j['ons'][:3]: X.put(y, off + o, beep(660))
    X.put(y, off + j['tf'], beep(990, 0.3, 0.2))
    if kind == 'r1': X.put(y, off + j['tf'] + 0.1, powerdown(2.0, 0.35)); X.put(y, off + j['tf'] + 4.0, X.boom(1.5, 40, 0.35))
    elif kind == 'r2':
        for k in range(14): X.put(y, off + j['tf'] + 0.6 + k * 0.7, glitch(0.25, 0.06 + 0.012 * k, k))
    else:
        for k in range(16): X.put(y, off + j['tf'] + 0.3 + k * 0.55, servo(0.5, 0.1))
        X.put(y, off + d - 1.6, powerdown(1.4, 0.3))
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
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        if k == 'title': X.put(sfx, 0.05, X.boom(2.0, 38, 0.45)); X.put(sfx, 0.1, hum(3.0, 0.05))
        if k == 'data': X.put(sfx, off + 0.0, glitch(0.4, 0.18, 7)); X.put(sfx, off + 0.05, X.boom(1.2, 50, 0.4))
        if k == 'jingle': X.put(sfx, off + 0.05, beep(988, 0.12, 0.22)); X.put(sfx, off + 0.17, beep(1318, 0.35, 0.22)); X.put(sfx, off + 0.05, X.boom(0.8, 60, 0.3))
        if k in ('wow2', 'wow3'): X.put(sfx, off + 0.0, X.boom(1.4, 42, 0.75)); X.put(sfx, off + 0.0, X.thump(70, 0.4, 0.8))
        if k in ('rh1', 'rh2'): X.put(sfx, off + 0.0, glitch(0.35, 0.16, 9)); X.put(sfx, off + 0.05, X.boom(1.0, 50, 0.4))
        if k == 'reveal': X.put(sfx, off + 0.05, X.boom(1.5, 38, 0.45))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/air_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    X.put(sfx, 0.0, X.boom(1.2, 45, 0.6)); X.put(sfx, 0.0, glitch(0.3, 0.15, 3))
    s0, s1, s2 = m['steps']
    X.put(sfx, s0, beep(880, 0.12, 0.15)); X.put(sfx, s0 + 0.3, powerdown(1.6, 0.3))
    X.put(sfx, s1, beep(880, 0.12, 0.15))
    for k in range(6): X.put(sfx, s1 + 0.4 + k * 0.6, glitch(0.25, 0.08 + 0.015 * k, k))
    X.put(sfx, s2, beep(880, 0.12, 0.15))
    for k in range(7): X.put(sfx, s2 + 0.3 + k * 0.55, servo(0.5, 0.1))
    X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/air_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
