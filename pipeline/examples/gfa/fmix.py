import json, math, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/gfa')
import mixlib as X, fmodel as FM
SR = X.SR; G = '/home/claude/gfa'; mode = sys.argv[1]
def battle(M, sts, n, fps=30):
    """心臓の音（巨人は低く、ゆっくり）、気が遠くなる耳鳴り、倒れる音"""
    y = np.zeros(n, np.float32); giant = M.h_brain > 1; prev = None; ring = []
    for f, st in enumerate(sts):
        at = f / fps
        if st is None or st < -50: prev = None; ring.append(0.0); continue
        if prev is not None:
            b0, b1 = math.floor(max(prev, -30) * M.hr / 60), math.floor(st * M.hr / 60)
            if b1 != b0: X.put(y, at, X.heartbeat(38 if giant else 62, 0.45 if giant else 0.25, 0.9 if giant else 0.55, 6 if giant else 14))
            if M.faint_t is not None and prev < M.faint_t <= st: X.put(y, at, X.boom(2.0, 30, 0.35))
            if M.faint_t is not None and giant:
                tf = M.faint_t + M.t_up * 0.5
                if prev < tf <= st: X.put(y, at, X.boom(3.0, 36, 1.0))
        lost = M.at(max(0, st), M.L) if st >= 0 else 0.0
        if M.faint_t is not None and st > M.faint_t: lost = 0.0
        ring.append(min(1.0, lost / 7.0)); prev = st
    env = np.interp(np.arange(n) / SR * fps, np.arange(len(ring)), ring).astype(np.float32)
    y += X.tone(3800, n, 0.05) * X.lp(env, 2000) ** 1.5
    return y
if mode == 'main':
    order = ['title', 'heart', 'rule', 'r1', 'res1', 'r2', 'res2', 'super', 'r3', 'res3', 'sweep', 'feet', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2', 'r3'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    Ms = {'r1': FM.Model(giant=False, pmax=120), 'r2': FM.Model(pmax=120), 'r3': FM.Model(pmax=900)}
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in Ms: X.put(sfx, off, battle(Ms[k], json.load(open(f'{G}/c_{k}_st.json'))['st'], int(d * SR)))
        if k in ('res2', 'res3'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/gfa_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    sfx = np.zeros(n, np.float32); Ms = [FM.Model(pmax=120), FM.Model(pmax=900)]
    for idx in (0, 1):
        sts = [s[1] if s[0] == idx else -99 for s in m['st']]
        X.put(sfx, 0, battle(Ms[idx], sts, int(T * SR)))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/gfa_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
