import json, sys
import numpy as np
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/bie')
import mixlib as X
import pcont as C
SR = X.SR; G = '/home/claude/bie'; mode = sys.argv[1]; D = json.load(open(f'{G}/dur.json'))
rng = np.random.default_rng(7)
def tone(f, L, g, dec=3.0, att=0.004):
    n = int(L * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * dec) * np.minimum(1, t / att) * np.minimum(1, (L - t) / 0.05) * g).astype(np.float32)
def chime(g=0.07):   # 小さく澄んだ鐘（場面の始まり）
    y = tone(880, 2.4, g, 2.0); y[:int(2.0 * SR)] += tone(1320, 2.0, g * 0.5, 2.6); y[:int(1.6 * SR)] += tone(1760, 1.6, g * 0.25, 3.4); return y
def blips(g=0.05):   # ゲーム機の電子音（ゆっくりした下降アルペジオ）
    y = np.zeros(int(1.6 * SR), np.float32)
    for k, f in enumerate([1046, 880, 784, 659, 523]): X.put(y, k * 0.22, tone(f, 0.25, g, 8))
    return y
def whoosh(L=1.0, g=0.08):
    n = int(L * SR); t = np.arange(n) / SR; y = rng.normal(0, 1, n).astype(np.float32); y = X.lp(y, 12) - X.lp(y, 60)
    return (y * np.sin(np.pi * t / L) ** 2 * g * 3).astype(np.float32)
def pad(L, f=220, g=0.03):   # ほんのり聞こえる澄んだ和音（110Hz以上）
    n = int(L * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * 0.5 + np.sin(2 * np.pi * f * 1.2 * t) * 0.3 + np.sin(2 * np.pi * f * 1.5 * t) * 0.25
    env = np.minimum(1, t / 1.5) * np.minimum(1, np.maximum(0, L - t) / 1.5); return (y * env * g).astype(np.float32)
def tick(g=0.05):
    n = int(0.04 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120) * g).astype(np.float32)
if mode == 'main':
    P = json.load(open(f'{G}/main_plan.json')); T = P['total']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    def at(k, sub, off, pre): s_ = C.NAR[k]; return off + pre + D[k] * s_.index(sub) / len(s_)
    for k, off, d, pre in P['scenes']:
        X.put(voice, off + pre, X.rd(f'{G}/voice/{k}.wav'))
        if k != 'hook': X.put(sfx, off, whoosh(0.9, 0.05))
        if k in ('title', 'l1', 'l2', 'l3', 'now1'): X.put(sfx, off + 0.05, chime(0.06))
        if k == 'l1':
            for sub in ('あなたは', 'ビーレフェルトに、行った', 'ビーレフェルトに行ったことがある'): X.put(sfx, at(k, sub, off, pre), tick(0.06))
        if k == 'l2b': X.put(sfx, off + 0.2, whoosh(2.5, 0.06)); X.put(sfx, at(k, '閉まって', off, pre), tick(0.07))
        if k in ('rh', 'l2', 'l3', 'outro'): X.put(sfx, off, pad(d, 196 if k != 'rh' else 233, 0.018))
        if k == 'spread': X.put(sfx, at(k, '賞金', off, pre), blips(0.04))
        if k == 'now2': X.put(sfx, at(k, '結果の', off, pre), chime(0.07))
        if k == 'hook': X.put(sfx, 0.0, chime(0.06)); X.put(sfx, 0.0, pad(d, 220, 0.015))
    X.finish(f'{G}/main_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/bie_main.mp4', '1100k', bgm_gain=0.16)
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR; voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32)
    for t, key in m['cues']: X.put(voice, t, X.rd(f'{G}/voice/{key}.wav'))
    S1, S2, S3, END0, TC, TH = m['S']
    X.put(sfx, 0.0, chime(0.06))
    for s in (S1, S2, S3, END0): X.put(sfx, s - 0.1, whoosh(0.8, 0.05))
    X.put(sfx, S3, pad(END0 - S3, 196, 0.018)); X.put(sfx, END0 + 0.1, chime(0.06)); X.put(sfx, TH, tick(0.06))
    X.finish(f'{G}/s_video.mp4', voice, sfx, T, '/home/claude/bgm/Investigations.mp3', f'{G}/bie_short.mp4', '2500k', maxrate='4000k', bgm_gain=0.16)
print('mixed', mode)
