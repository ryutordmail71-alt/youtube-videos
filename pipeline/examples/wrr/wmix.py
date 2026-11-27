import json, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/wrr')
import mixlib as X
SR = X.SR; G = '/home/claude/wrr'; mode = sys.argv[1]
rng = np.random.default_rng(5)
def beep(f, L=0.16, g=0.15):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.minimum(1, (L - t) / 0.03) * np.minimum(1, t / 0.005) * g).astype(np.float32)
def whoosh(L=0.8, g=0.2):
    n = int(L * SR); t = np.arange(n) / SR; y = X.lp(rng.normal(0, 1, n), 20) * 3; env = np.sin(np.pi * t / L) ** 2; return (y * env * g).astype(np.float32)
def ping(f=1150, g=0.12):
    n = int(1.2 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 4) * np.minimum(1, t / 0.004) * g).astype(np.float32)
def crowd(L=2.5, g=0.12):
    n = int(L * SR); t = np.arange(n) / SR; y = rng.normal(0, 1, n); y = X.lp(y, 6) - X.lp(y, 60)
    env = np.minimum(1, t / 0.3) * np.exp(-np.maximum(0, t - 0.6) * 1.2); return (y * env * g * 3).astype(np.float32)
def pistol(g=0.4):
    n = int(0.35 * SR); t = np.arange(n) / SR; y = rng.normal(0, 1, n) * np.exp(-t * 30); return (y * g).astype(np.float32)
def ff(L, g=0.05):
    """早送りのチリチリ音"""
    n = int(L * SR); t = np.arange(n) / SR; y = np.sign(np.sin(2 * np.pi * 9 * t)) * X.lp(rng.normal(0, 1, n), 3)
    return (y * g * np.minimum(1, t / 0.2) * np.minimum(1, np.maximum(0, L - t) / 0.2)).astype(np.float32)
def race_sfx(y, off, nm, d):
    import wscn as S
    P = getattr(S, nm + '_parts')(); ons, tf, cues, end, simf = P[:5]; lanes = getattr(S, nm.upper())['lanes']; dist = getattr(S, nm.upper())['dist']
    for o in ons[:3]: X.put(y, off + o, beep(660))
    X.put(y, off + tf, pistol()); X.put(y, off + tf + 0.05, beep(990, 0.3, 0.17))
    ts = np.arange(0, end, 1 / 60); sims = np.array([simf(t) for t in ts])
    for k, T in enumerate(sorted(dist / sp[1] for sp in lanes)):
        i = np.argmax(sims >= T - 1e-6)
        if sims[i] >= T - 1e-6:
            X.put(y, off + ts[i], ping(1320 if k == 0 else 990, 0.14 if k == 0 else 0.09))
            if k == 0: X.put(y, off + ts[i], crowd(2.5, 0.1)); X.put(y, off + ts[i] - 0.3, whoosh(0.7, 0.25))
    # 早送り区間
    fast = [ts[j] for j in range(1, len(ts)) if (sims[j] - sims[j - 1]) * 60 > 3]
    if fast: X.put(y, off + fast[0], ff(fast[-1] - fast[0]))
ORDER = ['title', 'jingle', 'data', 'rule', 'r1', 'res1', 'rh1', 'r2', 'res2', 'sweep', 'wow2', 'reveal', 'rh2', 'r3', 'wow3', 'res3', 'outro']
if mode == 'main':
    meta = {}
    for w in ('static', 'r1', 'r2', 'r3', 'ins'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in ORDER]; X.concat(clips, f'{G}/main_video.mp4')
    T = X.dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(ORDER, clips):
        d = X.dur(c)
        for t, key in meta[k][1]: X.put(voice, off + t, X.rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2', 'r3'): race_sfx(sfx, off, k, d)
        if k == 'title': X.put(sfx, 0.0, beep(1320, 0.08, 0.08)); X.put(sfx, 0.1, whoosh(1.0, 0.15)); X.put(sfx, 0.3, crowd(2.0, 0.05))
        if k in ('data', 'rule', 'reveal', 'sweep', 'outro'): X.put(sfx, off, whoosh(0.8, 0.18))
        if k.startswith('res'): X.put(sfx, off + 0.05, X.thump(60, 0.5, 0.5)); X.put(sfx, off + 0.1, crowd(2.2, 0.07))
        if k == 'jingle': X.put(sfx, off + 0.05, beep(988, 0.12, 0.18)); X.put(sfx, off + 0.17, beep(1318, 0.35, 0.18))
        if k in ('wow2', 'wow3'): X.put(sfx, off, X.boom(1.4, 42, 0.5)); X.put(sfx, off, X.thump(70, 0.4, 0.7))
        if k in ('rh1', 'rh2'): X.put(sfx, off, whoosh(0.9, 0.25)); X.put(sfx, off + 0.05, X.thump(50, 0.6, 0.5, 6))
        off += d
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Volatile_Reaction.mp3', f'{G}/wrr_main.mp4', '1100k')
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    X.put(sfx, 0.0, beep(1320, 0.08, 0.1)); X.put(sfx, 0.3, whoosh(0.8, 0.2))
    for s in m['steps']: X.put(sfx, s, whoosh(0.6, 0.2)); X.put(sfx, s + 0.05, pistol(0.25)); X.put(sfx, s + 1.6, ping(990, 0.12))
    X.put(sfx, m['steps'][0] + 0.1, ff(1.4))
    X.put(sfx, m['end0'], whoosh(0.7, 0.2)); X.put(sfx, m['endc'], beep(988, 0.12, 0.15)); X.put(sfx, m['endc'] + 0.12, beep(1318, 0.3, 0.15))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/wrr_short.mp4', '2500k', maxrate='4000k')
print('mixed', mode)
