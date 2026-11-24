"""場面をつなぎ、ナレーション・戦闘音・BGMをミックスする"""
import json, subprocess, sys, wave
import numpy as np
SR = 44100
mode = sys.argv[1]  # main / short
def rd(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
        return a
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def battle_noise(act, n):
    """戦闘中の音：ドドドという地響き＋ぶつかる音（活動量に比例）"""
    rng = np.random.default_rng(5); y = np.zeros(n, np.float32)
    a = np.array(act, np.float32); a = np.sqrt(a / max(1, a.max()))
    env = np.interp(np.arange(n) / SR * 30, np.arange(len(a)), a)
    br = np.cumsum(rng.normal(0, 1, n)).astype(np.float32); br -= np.convolve(br, np.ones(2000) / 2000, 'same'); br /= np.abs(br).max() + 1e-9
    y += br * env * 0.28
    # 衝突音
    k = 0
    for f in range(len(act)):
        cnt = int(rng.poisson(min(4, act[f] / 60)))
        for _ in range(cnt):
            s = int((f / 30 + rng.uniform(0, 1 / 30)) * SR); L = int(0.18 * SR)
            if s + L >= n: continue
            tt = np.arange(L) / SR; fr = rng.uniform(70, 140)
            y[s:s + L] += (np.sin(2 * np.pi * fr * tt) * np.exp(-tt * 28) + rng.normal(0, 0.4, L) * np.exp(-tt * 60)).astype(np.float32) * rng.uniform(0.08, 0.2)
    return y
if mode == 'main':
    order = ['title', 'stats', 'r1', 'res1', 'sweep', 'r2', 'res2', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2'): meta.update(json.load(open(f'/home/claude/bvh/scene_{w}.json')))
    clips = [f'/home/claude/bvh/c_{k}.mp4' for k in order]
    open('/home/claude/bvh/concat.txt', 'w').write(''.join(f"file '{c}'\n" for c in clips))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', '/home/claude/bvh/concat.txt', '-c', 'copy', '/home/claude/bvh/main_video.mp4'], check=True)
    T = dur('/home/claude/bvh/main_video.mp4'); n = int(T * SR) + SR
    voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = dur(c)
        for t, key in meta[k][1]:
            a = rd(f'/home/claude/bvh/voice/{key}.wav'); s = int((off + t) * SR); voice[s:s + len(a)] += a[:n - s]
        if k in ('r1', 'r2'):
            act = json.load(open(f'/home/claude/bvh/c_{k}_act.json')); y = battle_noise(act, int(d * SR)); s = int(off * SR); sfx[s:s + len(y)] += y[:n - s]
        off += d
    video = '/home/claude/bvh/main_video.mp4'; out = '/home/claude/bvh/bvh_main.mp4'
else:
    m = json.load(open('/home/claude/bvh/s_meta.json')); T = m['dur']; n = int(T * SR) + SR
    voice = np.zeros(n, np.float32)
    for t, key in m['cues']:
        a = rd(f'/home/claude/bvh/voice/{key}.wav'); s = int(t * SR); voice[s:s + len(a)] += a[:n - s]
    sfx = np.zeros(n, np.float32); y = battle_noise(m['act'], int(T * SR)); sfx[:len(y)] += y
    video = '/home/claude/bvh/s_video.mp4'; out = '/home/claude/bvh/bvh_short.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', '/home/claude/bgm/Volatile_Reaction.mp3', '-t', str(T + 1), '-ac', '1', '-ar', str(SR), '/tmp/bvh_bgm.wav'], check=True)
bgm = rd('/tmp/bvh_bgm.wav')[:n]; bgm = np.pad(bgm, (0, n - len(bgm)))
# ナレーション中はBGMを下げる
env = np.abs(voice); k = int(0.3 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); duck = np.where(env > 0.01, 0.45, 1.0)
duck = np.convolve(duck, np.ones(k) / k, 'same')
fade = np.ones(n); fl = int(2.5 * SR); fade[int(T * SR) - fl:int(T * SR)] = np.linspace(1, 0, fl); fade[int(T * SR):] = 0
mix = voice * 1.0 + sfx * 0.9 + bgm * 0.22 * duck * fade
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
with wave.open('/tmp/bvh_mix.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', '/tmp/bvh_mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ac', '2', '-shortest', '-movflags', '+faststart', out], check=True)
print('mixed', out, T)
