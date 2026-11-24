"""人間vsゴリラの戦闘音：打撃（素材＋合成の重ね）、風切り音、倒れる音、もみ合い、観客、ドラミング"""
import glob, json, os, subprocess, wave
import numpy as np
SR = 44100
rng = np.random.default_rng(3)

def load(path):
    out = '/tmp/gvh_sfx_' + os.path.basename(path) + '.wav'
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ac', '1', '-ar', str(SR), out], check=True)
    with wave.open(out) as w: a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    a = a / (np.abs(a).max() + 1e-9)
    # 先頭の無音を削る
    nz = np.where(np.abs(a) > 0.05)[0]
    return a[max(0, nz[0] - 50):] if len(nz) else a

def lp(x, k):
    return np.convolve(x, np.ones(k) / k, 'same')

def synth_punch(strength=1.0):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 95 * np.exp(-t * 9) + 48
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    sub = np.sin(2 * np.pi * 42 * t) * np.exp(-t * 7) * 0.8
    crack = rng.normal(0, 1, n) * np.exp(-t * 90); crack = lp(crack, 3) * 0.9
    slap = (rng.normal(0, 1, n) - lp(rng.normal(0, 1, n), 25)) * np.exp(-t * 45) * 0.5
    y = np.tanh((body + sub + crack + slap) * 1.6 * strength)
    return (y / np.abs(y).max()).astype(np.float32)

def whoosh(dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = rng.normal(0, 1, n); env = np.sin(np.pi * t / dur) ** 2
    y = lp(nz, 6) - lp(nz, 40)
    return (y * env / (np.abs(y).max() + 1e-9) * 0.5).astype(np.float32)

def body_fall():
    n = int(0.6 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (70 * np.exp(-t * 6) + 35) * t) * np.exp(-t * 9)
    dirt = lp(rng.normal(0, 1, n), 4) * np.exp(-t * 14) * 0.6
    y = thump + dirt
    return (y / np.abs(y).max() * 0.7).astype(np.float32)

def chest_beat():
    """ゴリラのドラミング（胸をたたく、ポコポコという中が空洞のような音）"""
    out = np.zeros(int(1.6 * SR), np.float32); t0 = 0.0
    for k in range(9):
        n = int(0.18 * SR); t = np.arange(n) / SR; f0 = rng.uniform(150, 210)
        y = (np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 1.9 * t)) * np.exp(-t * 28) + lp(rng.normal(0, 1, n), 5) * np.exp(-t * 120) * 0.5
        s = int(t0 * SR); out[s:s + n] += (y * (0.6 + 0.4 * (k / 8))).astype(np.float32)
        t0 += 0.11 + rng.uniform(-0.015, 0.02)
    return out / np.abs(out).max()

PUNCHES = [load(p) for p in sorted(glob.glob('/home/claude/gvh/sfx/*Punch*')) if not p.endswith('.json')]
CROWD = [load(p) for p in sorted(glob.glob('/home/claude/gvh/sfx/*lucha*'))]
SYN = [synth_punch(s) for s in (0.8, 1.0, 1.2, 1.4)]

def put(buf, at, x, g=1.0):
    s = int(at * SR)
    if s < 0 or s >= len(buf): return
    e = min(len(buf), s + len(x)); buf[s:e] += x[:e - s] * g

def reverb(x, sec=0.6, wet=0.18):
    n = int(sec * SR); ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 7); ir = lp(ir, 8); ir /= np.abs(ir).sum() / 6
    from scipy.signal import fftconvolve
    return x + wet * fftconvolve(x, ir)[:len(x)]

def battle_audio(R, sts, dur, fps=30, crowd=True, beat_at=0.25):
    """R: battle.Round, sts: 各フレームのシミュレーション時刻（R が混在するときは (R, st) のリスト）"""
    n = int(dur * SR) + SR; hit = np.zeros(n, np.float32); amb = np.zeros(n, np.float32)
    frames = [(R, s) if not isinstance(s, (list, tuple)) else s for s in sts]
    prev = None; recent = []
    for f, (RR, st) in enumerate(frames):
        vt = f / fps
        if prev is not None and prev[0] is RR and st > prev[1]:
            a, b = prev[1], st
            ko = np.where((RR.death[:RR.NB] > a) & (RR.death[:RR.NB] <= b))[0]
            speed = max(1.0, (b - a) * fps)
            recent = [r for r in recent if vt - r < 0.25]
            for j in ko:
                g = 1.0 / np.sqrt(1 + len(recent)) / (1 + 0.25 * (speed - 1))
                put(hit, vt - 0.11, whoosh(0.18), 0.45 * g)
                if PUNCHES: put(hit, vt, PUNCHES[int(rng.integers(len(PUNCHES)))], 0.75 * g)
                put(hit, vt, SYN[int(rng.integers(len(SYN)))], 0.85 * g)
                recent.append(vt)
                # 着地（飛ばされた時間ぶん後）
                put(hit, vt + 0.55 / speed, body_fall(), 0.55 * g)
            # 組みつき中の小さな打撃
            evs = [e for e in RR.ev if a < e[0] <= b and e[1] == 'hit']
            for e in evs[:2]:
                p = PUNCHES[int(rng.integers(len(PUNCHES)))] if PUNCHES else SYN[0]
                put(hit, vt + rng.uniform(0, 0.03), p[::1], 0.22 / np.sqrt(speed))
        prev = (RR, st)
    # もみ合い・観客
    act = np.array([float(RR.atk[RR.frame_idx(st)][:RR.NB].sum()) for RR, st in frames])
    env = np.interp(np.arange(n) / SR * fps, np.arange(len(act)), np.clip(act / 7, 0, 1))
    scuffle = lp(rng.normal(0, 1, n), 3) - lp(rng.normal(0, 1, n), 60)
    scuffle *= (0.6 + 0.4 * np.sin(np.arange(n) / SR * 2 * np.pi * 3.1) ** 2)
    amb += (scuffle * env * 0.05).astype(np.float32)
    if crowd and CROWD:
        c = np.concatenate(CROWD); c = np.tile(c, n // len(c) + 1)[:n]
        cenv = 0.35 + 0.65 * env
        amb += (c * cenv * 0.22).astype(np.float32)
        amb[:int(0.8 * SR)] *= np.linspace(0, 1, int(0.8 * SR))
    if beat_at is not None: put(hit, beat_at, chest_beat(), 0.7)
    y = reverb(hit, 0.5, 0.2) + amb
    return y.astype(np.float32)
