"""場面をつなぎ、ナレーション・羽音・たたく音・BGMをミックスする"""
import json, math, subprocess, sys, wave
import numpy as np
sys.path.insert(0, '/home/claude/gvm')
import gmodel as GM
SR = 44100; G = '/home/claude/gvm'
mode = sys.argv[1]
def rd(p):
    with wave.open(p) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    if sr != SR: a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a).astype(np.float32)
    return a
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
rng = np.random.default_rng(11)
def lp(x, k):
    return np.convolve(x, np.ones(k) / k, 'same').astype(np.float32)
def slap(g=1.0):
    """大きな手でたたく音：低いドン＋パン"""
    L = int(0.9 * SR); t = np.arange(L) / SR
    boom = np.sin(2 * np.pi * (55 + 40 * np.exp(-t * 18)) * t) * np.exp(-t * 5.5)
    crack = rng.normal(0, 1, L) * np.exp(-t * 45); crack = crack - lp(crack, 6)
    body = lp(rng.normal(0, 1, L), 18) * np.exp(-t * 14) * 3
    return ((boom * 0.9 + crack * 0.35 + body * 0.5) * g).astype(np.float32)
def tink():
    L = int(0.12 * SR); t = np.arange(L) / SR
    return (np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 60) * 0.08).astype(np.float32)
def whine(n):
    """蚊の羽音：少しずつずれた音程をたくさん重ねる"""
    t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for k in range(10):
        f0 = rng.uniform(430, 640); vib = rng.uniform(3, 9); ph = rng.uniform(0, 6.28)
        fr = f0 * (1 + 0.03 * np.sin(2 * np.pi * vib * t + ph) + 0.02 * np.sin(2 * np.pi * 0.3 * t + ph))
        phase = 2 * np.pi * np.cumsum(fr) / SR
        y += (np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)) * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.2, 1.2) * t + ph))
    return (y / 10).astype(np.float32)
def put(buf, at, x):
    s = int(at * SR)
    if s < 0 or s >= len(buf): return
    e = min(len(buf), s + len(x)); buf[s:e] += x[:e - s]
def battle_audio(M, sts, n, fps=30):
    y = np.zeros(n, np.float32)
    act = []
    for st in sts:
        if st < 0: act.append(0.0); continue
        a = M.flying(st) + M.onbody(st) if st <= M.t_end + 1 else 0.0
        act.append(min(1.0, math.log10(1 + a) / 8.5))
    env = np.interp(np.arange(n) / SR * fps, np.arange(len(act)), act).astype(np.float32); env = lp(env, 4000)
    y += whine(n) * env * 0.22
    prev = None
    for f, st in enumerate(sts):
        if st < 0: prev = None; continue
        sp = (sts[f] - sts[f - 1]) * fps if f > 0 and sts[f - 1] >= 0 else 1.0
        k = math.floor(st / GM.SWAT)
        if prev is not None and k != prev and sp <= 3 and M.onbody(st) > 1000 and st < M.t_end: put(y, f / fps, slap(0.55))
        prev = k
        if not M.can_bite and sp <= 3 and st < M.t_end and M.onbody(st) > 1000:
            if f > 0 and math.floor(st / 0.7) != math.floor(sts[f - 1] / 0.7): put(y, f / fps, tink())
    return y
M1 = GM.Model(1e8, can_bite=False); M2 = GM.Model(2e10)
if mode == 'main':
    order = ['title', 'stats', 'skin', 'r1', 'res1', 'sweep', 'r2', 'res2', 'outro']
    meta = {}
    for w in ('static', 'r1', 'r2'): meta.update(json.load(open(f'{G}/scene_{w}.json')))
    clips = [f'{G}/c_{k}.mp4' for k in order]
    open(f'{G}/concat.txt', 'w').write(''.join(f"file '{c}'\n" for c in clips))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{G}/concat.txt', '-c', 'copy', f'{G}/main_video.mp4'], check=True)
    T = dur(f'{G}/main_video.mp4'); n = int(T * SR) + SR
    voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); off = 0.0
    for k, c in zip(order, clips):
        d = dur(c)
        for t, key in meta[k][1]: put(voice, off + t, rd(f'{G}/voice/{key}.wav'))
        if k in ('r1', 'r2'):
            sts = json.load(open(f'{G}/c_{k}_st.json'))['st']; y = battle_audio(M1 if k == 'r1' else M2, sts, int(d * SR)); put(sfx, off, y)
        if k in ('res1', 'res2'): put(sfx, off + 0.05, slap(0.7) * 0.8)
        off += d
    video = f'{G}/main_video.mp4'; out = f'{G}/gvm_main.mp4'; bgmf = '/home/claude/bgm/Investigations.mp3'
else:
    m = json.load(open(f'{G}/s_meta.json')); T = m['dur']; n = int(T * SR) + SR
    voice = np.zeros(n, np.float32)
    for t, key in m['cues']: put(voice, t, rd(f'{G}/voice/{key}.wav'))
    sfx = np.zeros(n, np.float32); put(sfx, 0, battle_audio(M1, m['st'], int(T * SR)))
    video = f'{G}/s_video.mp4'; out = f'{G}/gvm_short.mp4'; bgmf = '/home/claude/bgm/Volatile_Reaction.mp3'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', bgmf, '-t', str(T + 1), '-ac', '1', '-ar', str(SR), '/tmp/gvm_bgm.wav'], check=True)
bgm = rd('/tmp/gvm_bgm.wav')[:n]; bgm = np.pad(bgm, (0, n - len(bgm)))
env = np.abs(voice); k = int(0.3 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); duck = np.where(env > 0.01, 0.45, 1.0)
duck = np.convolve(duck, np.ones(k) / k, 'same')
fade = np.ones(n); fl = int(2.5 * SR); fade[int(T * SR) - fl:int(T * SR)] = np.linspace(1, 0, fl); fade[int(T * SR):] = 0
mix = voice * 1.0 + sfx * 0.8 + bgm * 0.22 * duck * fade
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
with wave.open('/tmp/gvm_mix.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
br = '1100k' if mode == 'main' else '2500k'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', '/tmp/gvm_mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-b:v', br, '-maxrate', '2000k' if mode == 'main' else '4000k', '-bufsize', '4000k',
                '-pix_fmt', 'yuv420p', '-af', 'acompressor=threshold=-18dB:ratio=3:attack=10:release=200,loudnorm=I=-14:TP=-2.5:LRA=11,alimiter=limit=0.84', '-ar', '48000',
                '-c:a', 'aac', '-b:a', '160k', '-ac', '2', '-shortest', '-movflags', '+faststart', out], check=True)
print('mixed', out, T)
