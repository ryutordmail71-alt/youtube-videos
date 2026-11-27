"""共通：ナレーション・効果音・BGMのミックスと書き出し、効果音の合成"""
import json, subprocess, wave
import numpy as np
SR = 44100
rng = np.random.default_rng(11)
def rd(p):
    with wave.open(p) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    if sr != SR: a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a).astype(np.float32)
    return a
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same').astype(np.float32)
def put(buf, at, x, g=1.0):
    s = int(at * SR)
    if s < 0 or s >= len(buf): return
    e = min(len(buf), s + len(x)); buf[s:e] += x[:e - s] * g
def boom(L=2.5, f0=40, g=1.0):
    n = int(L * SR); t = np.arange(n) / SR
    b = np.sin(2 * np.pi * (f0 + 50 * np.exp(-t * 10)) * t) * np.exp(-t * 2.2)
    rum = lp(rng.normal(0, 1, n), 60) * np.exp(-t * 1.4) * 6
    cr = rng.normal(0, 1, n) * np.exp(-t * 25); cr = cr - lp(cr, 8)
    return ((b + rum * 0.6 + cr * 0.3) * g).astype(np.float32)
def thump(f0=55, L=0.35, g=1.0, dec=14):
    n = int(L * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (f0 + 30 * np.exp(-t * 30)) * t) * np.exp(-t * dec) * g).astype(np.float32)
def heartbeat(f0=55, gap=0.28, g=1.0, dec=14):
    a = thump(f0, 0.5, g, dec); b = thump(f0 * 0.9, 0.5, g * 0.7, dec); n = int(gap * SR)
    out = np.zeros(len(a) + n, np.float32); out[:len(a)] += a; out[n:n + len(b)] += b; return out
def whistle():
    n = int(0.7 * SR); t = np.arange(n) / SR
    f = 2900 + 120 * np.sign(np.sin(2 * np.pi * 28 * t)); ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, t / 0.02) * np.minimum(1, (0.7 - t) / 0.05)
    return (np.sin(ph) * env * 0.25).astype(np.float32)
def grunt(g=1.0):
    """大勢の「せーの！」っぽい、こもった声のかたまり"""
    n = int(0.45 * SR); t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for k in range(12):
        f0 = rng.uniform(110, 190); ph = 2 * np.pi * np.cumsum(f0 * (1 - 0.15 * t / 0.45)) / SR
        y += (np.sign(np.sin(ph)) * 0.5 + np.sin(ph)) * rng.uniform(0.5, 1)
    y = lp(y, 14) + lp(rng.normal(0, 1, n), 4) * 0.8
    env = np.minimum(1, t / 0.05) * np.exp(-np.maximum(0, t - 0.15) * 7)
    return (y * env * 0.05 * g).astype(np.float32)
def creak(g=1.0):
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 70 + 30 * np.sin(2 * np.pi * 3 * t); ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) > 0.7).astype(np.float32) - 0.3; y = lp(y, 6) * np.sin(np.pi * t / 0.6)
    return (y * 0.12 * g).astype(np.float32)
def drag_noise(n):
    return (lp(rng.normal(0, 1, n), 30) * 0.5).astype(np.float32)
def tone(f, n, g):
    t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) * g).astype(np.float32)

def _ff_eq(x, out, flt):
    """numpy の音に ffmpeg のフィルターをかけて戻す"""
    with wave.open(out + '.in.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out + '.in.wav', '-af', flt, '-ar', str(SR), '-ac', '1', out + '.eq.wav'], check=True)
    y = rd(out + '.eq.wav'); return np.pad(y, (0, max(0, len(x) - len(y))))[:len(x)]
# ナレーションがこもらないように（ユーザー指示 2026-11-27）：
#  声＝低いこもり（80Hz以下）を切り、もわっとする帯（300Hz）を少し下げ、言葉がはっきりする帯（3kHz）を少し上げる
#  BGM＝声とぶつかる帯（1〜4kHz）をへこませて、声の通り道をあける
VOICE_EQ = 'highpass=f=80,equalizer=f=300:t=q:w=1.0:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=6500:t=q:w=1.5:g=1.5'
BGM_EQ = 'highpass=f=60,equalizer=f=2500:t=q:w=1.0:g=-5,equalizer=f=1000:t=q:w=1.0:g=-2'
def finish(video, voice, sfx, T, bgmf, out, br, bgm_gain=0.22, maxrate='2000k'):
    n = len(voice)
    if np.abs(voice).max() > 0: voice = _ff_eq(voice, out + '.v', VOICE_EQ)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', bgmf, '-t', str(T + 1), '-ac', '1', '-ar', str(SR), out + '.bgm.wav'], check=True)
    bgm = rd(out + '.bgm.wav')[:n]; bgm = np.pad(bgm, (0, n - len(bgm)))
    if np.abs(bgm).max() > 0: bgm = _ff_eq(bgm, out + '.b', BGM_EQ)
    env = np.abs(voice); k = int(0.3 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); duck = np.where(env > 0.01, 0.35, 1.0)
    duck = np.convolve(duck, np.ones(k) / k, 'same')
    fade = np.ones(n); fl = int(2.5 * SR); e = int(T * SR); fade[max(0, e - fl):e] = np.linspace(1, 0, min(fl, e)); fade[e:] = 0
    mix = voice * 1.0 + sfx * 0.8 + bgm * bgm_gain * duck * fade
    mix = mix / max(1.0, np.abs(mix).max() / 0.95)
    with wave.open(out + '.mix.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', out + '.mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-b:v', br, '-maxrate', maxrate, '-bufsize', '4000k',
                    '-pix_fmt', 'yuv420p', '-af', 'highpass=f=40,acompressor=threshold=-18dB:ratio=3:attack=10:release=200,loudnorm=I=-14:TP=-2.5:LRA=11,alimiter=limit=0.8', '-ar', '48000',
                    '-c:a', 'aac', '-b:a', '160k', '-ac', '2', '-shortest', '-movflags', '+faststart', out], check=True)
def concat(clips, out):
    lst = out + '.txt'; open(lst, 'w').write(''.join(f"file '{c}'\n" for c in clips))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out], check=True)
