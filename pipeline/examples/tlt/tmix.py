import json, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/tlt')
import mixlib as X
SR = X.SR; G = '/home/claude/tlt'; mode = sys.argv[1]
def beep(f, L=0.16, g=0.18):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.03) * g).astype(np.float32)
def flush(L=2.6, g=0.35):
    """水を流す音（ザーッ → ゴボゴボ）"""
    n = int(L * SR); t = np.arange(n) / SR; y = X.rng.normal(0, 1, n).astype(np.float32)
    y = X.lp(y, 3) - X.lp(y, 40); env = np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 0.6) * 1.3)
    gur = np.sin(2 * np.pi * (120 + 60 * np.sin(2 * np.pi * 7 * t)) * t) * (np.sin(2 * np.pi * 9 * t) > 0.3) * np.exp(-np.maximum(0, t - 1.0) * 2) * 0.25
    return ((y * env + gur * np.minimum(1, t / 0.6)) * g).astype(np.float32)
def rush(L, g=0.25):
    n = int(L * SR); t = np.arange(n) / SR; y = X.lp(X.rng.normal(0, 1, n).astype(np.float32), 12)
    env = np.minimum(1, t / 0.5) * np.minimum(1, (L - t) / 1.0); return (y * env * g * 2).astype(np.float32)
def hiss(L, g=0.12):
    n = int(L * SR); t = np.arange(n) / SR; y = X.rng.normal(0, 1, n).astype(np.float32); y = y - X.lp(y, 6)
    env = np.minimum(1, t / 0.3) * np.minimum(1, np.maximum(0, L - t) / 0.5); return (y * env * g).astype(np.float32)
def round_sfx(y, off, j, d, kind):
    for o in j['ons'][:3]: X.put(y, off + o, beep(660))
    X.put(y, off + j['tf'], beep(990, 0.3, 0.2)); X.put(y, off + j['tf'] + 0.05, flush(3.0, 0.4))
    if kind == 'r1': X.put(y, off + j['tf'] + 1.0, rush(max(1.5, d - j['tf'] - 2.0), 0.18))
    else: X.put(y, off + j['tf'] + 0.6, hiss(max(1.5, d - j['tf'] - 1.5)))
if mode == 'main':
    order = ['title', 'data', 'rule', 'r1', 'res1', 'reveal', 'sweep', 'r2', 'res2', 'real', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2'): round_sfx(sfx, off, json.load(open(f'{G}/c_{k}_t.json')), d, k)
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        if k == 'title': X.put(sfx, 0.1, flush(2.6, 0.3))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/tlt_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    X.put(sfx, 0.0, X.boom(1.2, 45, 0.6)); X.put(sfx, 0.3, flush(2.6, 0.3))
    for s in m['steps']: X.put(sfx, s, beep(880, 0.12, 0.15)); X.put(sfx, s + 0.2, rush(1.6, 0.12))
    X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/tlt_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
