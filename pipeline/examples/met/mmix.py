import json, sys, glob
import numpy as np
sys.path.insert(0, '/home/claude/gva')
import mixlib as X
G = '/home/claude/met'; SR = X.SR; mode = sys.argv[1]
ORDER = ['title', 'data', 'rule', 'r1', 'res1', 'r2', 'res2', 'secret', 'r3', 'res3', 'odds', 'outro']
def whoosh(L=0.7, g=0.22):
    n = int(L * SR); t = np.arange(n) / SR; y = X.lp(X.rng.normal(0, 1, n), 20) * np.sin(np.pi * t / L) ** 2
    return (y * g).astype(np.float32)
def fallwhine(L, g=0.12):
    n = int(L * SR); t = np.arange(n) / SR; f = 900 - 650 * t / L; ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * 0.3 + X.lp(X.rng.normal(0, 1, n), 4) * 0.7; return (y * np.minimum(1, t / 0.5) * g).astype(np.float32)
def drone(L, f0=55, g=0.08, *a, **k):
    """（2026-11-27 変更）低いうなり・ザラザラしたノイズは音割れっぽく聞こえるので使わない。代わりに小さく澄んだ和音（110Hz以上）"""
    n = int(L * SR); t = np.arange(n) / SR; f = max(110.0, float(f0) * 2)
    y = np.sin(2 * np.pi * f * t) * 0.6 + np.sin(2 * np.pi * f * 1.5 * t) * 0.3 + np.sin(2 * np.pi * f * 2 * t) * 0.15
    env = np.minimum(1, t / 1.5) * np.minimum(1, np.maximum(0, L - t) / 1.5); return (y * env * g * 0.5).astype(np.float32)
