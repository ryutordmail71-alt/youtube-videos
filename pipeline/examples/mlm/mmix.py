import json, sys, math
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/mlm')
import mixlib as X
G = '/home/claude/mlm'; SR = X.SR; mode = sys.argv[1]
ORDER = ['title', 'myth', 'rule', 'r1', 'res1', 'r2', 'res2', 'sweep', 'r3', 'res3', 'outro']
def whoosh():
    n = int(0.5 * SR); t = np.arange(n) / SR; y = X.lp(X.rng.normal(0, 1, n), 12) * np.sin(np.pi * t / 0.5) ** 2
    return (y * 0.25).astype(np.float32)
def snap():
    n = int(0.4 * SR); t = np.arange(n) / SR; y = X.rng.normal(0, 1, n) * np.exp(-t * 40); y = y - X.lp(y, 5)
    return (y * 0.6 + X.thump(70, 0.4, 0.6, 10)[:n]).astype(np.float32)
def jump_sfx(k, t_jump, broke):
    import mscenes as M
    y = []
    if broke: return [(t_jump + 0.12, snap()), (t_jump + 0.6, X.thump(50, 0.6, 0.9, 6))]
    h = M.jump_h(k); tf = 2 * math.sqrt(2 * 9.8 * h) / 9.8
    return [(t_jump + 0.25, X.thump(90, 0.25, 0.4, 20)), (t_jump + 0.3 + tf, X.thump(60, 0.4, 0.8, 12))]
if mode == 'main':
    meta = json.load(open(f'{G}/scenes.json')); clips = [f'{G}/c_{k}.mp4' for k in ORDER]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(ORDER, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        X.put(sfx, off, whoosh())
        if k in ('r1', 'r2', 'r3'):
            s = json.load(open(f'{G}/c_{k}_st.json')); X.put(sfx, off + s['t_jump'] - 0.3, X.whistle())
            for at, y in jump_sfx(s['k'], s['t_jump'], k == 'r3'): X.put(sfx, off + at, y)
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/mlm_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    for tj, k in [(5.0, 1.0), (10.2, 1 / 0.9)]:
        for at, y in jump_sfx(k, tj, False): X.put(sfx, at, y)
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/mlm_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
