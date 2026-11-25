import json, math, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva')
import mixlib as X, hmodel as HM
SR = X.SR; G = '/home/claude/h10'; mode = sys.argv[1]
def pistol():
    n = int(0.5 * SR); t = np.arange(n) / SR; c = X.rng.normal(0, 1, n) * np.exp(-t * 18); return (c - X.lp(c, 6)).astype(np.float32) * 0.9
def beep(f=1200, L=0.12, g=0.25):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.02) * g).astype(np.float32)
def battle_sfx(sts, NA, NB, n, fps=30):
    """スタートの合図、心臓の音（数が多いほど速く重なる）、危険ラインを超えた警告音"""
    y = np.zeros(n, np.float32); started = False; warned = set()
    Rs = [HM.Run(NA, 60), HM.Run(NB, 60)]; prev = None
    for f, st in enumerate(sts):
        at = f / fps
        if st >= 0 and not started: X.put(y, at, pistol()); started = True
        if st >= 0 and prev is not None:
            for i, R in enumerate(Rs):
                hr = 160 + 10 * min(R.N, 3); b0, b1 = math.floor(prev * hr / 60), math.floor(st * hr / 60)
                if b1 != b0: X.put(y, at, X.heartbeat(60 if i == 0 else 52, 0.16, 0.25 * min(2.0, 0.7 + 0.15 * R.N), 18))
                if R.at(st, 5) > HM.LIM and i not in warned:
                    warned.add(i)
                    for k in range(3): X.put(y, at + k * 0.22, beep())
        prev = st if st >= 0 else prev if prev is not None else None
        if st >= 0 and prev is None: prev = st
    return y
if mode == 'main':
    order = ['title', 'heart', 'rule', 'r1', 'res1', 'reveal', 'r2', 'res2', 'sweep', 'r3', 'res3', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2', 'r3'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2', 'r3'):
            j = json.load(open(f'{G}/c_{k}_st.json')); X.put(sfx, off, battle_sfx(j['st'], j['NA'], j['NB'], int(d * SR)))
        if k.startswith('res'): X.put(sfx, off + 0.05, X.boom(1.5, 45, 0.5))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/h10_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    sts = [f / 30 - m['pre'] if f / 30 < m['end0'] else -99 for f in range(int(T * 30))]
    sts = [s if s > -50 else -1 for s in sts]
    sfx = np.zeros(n, np.float32); y = battle_sfx([s if i / 30 < m['end0'] else -1 for i, s in enumerate(sts)], 1, 10, int(m['end0'] * SR)); X.put(sfx, 0, y)
    X.put(sfx, m['end0'] + 0.05, X.boom(1.5, 45, 0.5))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/h10_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
