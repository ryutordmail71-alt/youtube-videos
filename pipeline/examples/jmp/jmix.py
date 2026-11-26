import json, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/jmp')
import mixlib as X
SR = X.SR; G = '/home/claude/jmp'; mode = sys.argv[1]
def beep(f, L=0.16, g=0.18):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.03) * g).astype(np.float32)
def whoosh(L=0.5, g=0.25):
    n = int(L * SR); t = np.arange(n) / SR; y = X.rng.normal(0, 1, n).astype(np.float32); y = y - X.lp(y, 5)
    return (y * np.sin(np.pi * t / L) * g).astype(np.float32)
def jump_sfx(y, off, j, big):
    for o in j['ons'][:3]: X.put(y, off + o, beep(660))
    X.put(y, off + j['ons'][3], beep(990, 0.3, 0.22)); X.put(y, off + j['tj'], whoosh())
    X.put(y, off + j['land'], X.thump(50, 0.6, 0.9, 8)); X.put(y, off + j['land'] + 0.02, X.boom(2.2, 38, big))
if mode == 'main':
    order = ['title', 'data', 'rule', 'r1', 'res1', 'reveal', 'sweep', 'r2', 'res2', 'real', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2'): jump_sfx(sfx, off, json.load(open(f'{G}/c_{k}_t.json')), 0.2 if k == 'r1' else 0.9)
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        if k == 'title': X.put(sfx, 0.1, X.boom(2.0, 40, 0.5))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/jmp_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    X.put(sfx, 0.0, X.boom(1.2, 45, 0.6))
    for L, a in zip(m['lands'], m['amps']): X.put(sfx, L - 0.6, whoosh(0.4, 0.15)); X.put(sfx, L, X.thump(50, 0.6, 0.6 + 0.08 * a, 8)); X.put(sfx, L + 0.02, X.boom(1.6, 40, 0.1 + 0.12 * a))
    X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/jmp_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
