import json, math, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva')
import mixlib as X, amodel as AM, arender as A
SR = X.SR; G = '/home/claude/gva'; mode = sys.argv[1]
def battle(M, sts, n, fps=30):
    y = np.zeros(n, np.float32); g = 0.5 + 0.5 * math.log10(M.n) / math.log10(2000)
    prev = None; vel = []
    for f, st in enumerate(sts):
        at = f / fps
        if prev is not None and prev < 0 <= st: X.put(y, at, X.whistle())
        if st > 0 and prev is not None and prev > 0 and st <= M.t_end + 0.1:
            k0, k1 = math.floor((prev - 0.5) / 2.0), math.floor((st - 0.5) / 2.0)
            if k1 != k0: X.put(y, at, X.grunt(g))
            ph0 = (prev / AM.HEAVE) + (1 - (math.pi / 2 - 1) / (2 * math.pi)); ph1 = (st / AM.HEAVE) + (1 - (math.pi / 2 - 1) / (2 * math.pi))
            if math.floor(ph1) != math.floor(ph0): X.put(y, at, X.thump(36, 0.6, 0.5, 6)); X.put(y, at + 0.05, X.creak(1.0))
        if st > 0 and prev is not None and prev > 0: vel.append(abs(M.pos(st) - M.pos(prev)) * fps)
        else: vel.append(0.0)
        if M.win == 'human' and prev is not None and prev < M.t_end + A.TOPPLE_T <= st: X.put(y, at, X.boom(3.0, 38, 1.0))
        if M.win == 'human' and prev is not None and prev < M.t_end <= st: X.put(y, at, X.creak(2.0))
        if M.win == 'giant' and prev is not None and prev < M.t_end <= st:
            for j in range(10): X.put(y, at + j * 0.07, X.thump(90 + 20 * j % 40, 0.2, 0.25, 25))
        prev = st
    env = np.interp(np.arange(n) / SR * fps, np.arange(len(vel)), np.minimum(1, np.array(vel) / 1.5)).astype(np.float32)
    y += X.drag_noise(n) * X.lp(env, 3000) * 0.35
    return y
if mode == 'main':
    order = ['title', 'stats', 'rule', 'r1', 'res1', 'r2', 'ringel', 'sweep', 'r3', 'res3', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2', 'r3'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    Ms = {'r1': AM.Model(100), 'r2': AM.Model(816), 'r3': AM.Model(2000)}
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in Ms: X.put(sfx, off, battle(Ms[k], json.load(open(f'{G}/c_{k}_st.json'))['st'], int(d * SR)))
        if k in ('res1', 'res3'): X.put(sfx, off + 0.05, X.boom(1.5, 50, 0.5))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/gva_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    sfx = np.zeros(n, np.float32); sts = [s if s > -50 else -99 for s in m['st']]
    X.put(sfx, 0, battle(AM.Model(816), sts, int(T * SR)))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/gva_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
