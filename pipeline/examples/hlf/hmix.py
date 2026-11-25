import json, sys, math
import numpy as np
sys.path.insert(0, '/home/claude/gva')
import mixlib as X
G = '/home/claude/hlf'; SR = X.SR; mode = sys.argv[1]
ORDER = ['title', 'rule', 'run', 'heart', 'breath', 'sleep', 'food', 'hair', 'rank', 'pct', 'outro']
def whoosh():
    n = int(0.5 * SR); t = np.arange(n) / SR; y = X.lp(X.rng.normal(0, 1, n), 12) * np.sin(np.pi * t / 0.5) ** 2
    return (y * 0.25).astype(np.float32)
def tick(): return X.thump(1800, 0.03, 0.05, 120)
if mode == 'main':
    meta = json.load(open(f'{G}/scenes.json')); clips = [f'{G}/c_{k}.mp4' for k in ORDER]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(ORDER, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        X.put(sfx, off, whoosh())
        if k == 'heart':
            for b in np.arange(0, d, 60 / 70): X.put(sfx, off + b, X.heartbeat(60, 0.25, 0.45, 14))
        if k == 'run':
            for b in np.arange(0.9, d - 1.5, 0.09): X.put(sfx, off + b, tick())
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/hlf_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    t2 = dict((k, t) for t, k in m['cues'])['v2']
    for b in np.arange(0, t2, 60 / 70): X.put(sfx, b, X.heartbeat(60, 0.25, 0.45, 14))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/hlf_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
