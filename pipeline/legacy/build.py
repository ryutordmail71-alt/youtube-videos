import json, subprocess, wave, os
import numpy as np
os.chdir('/home/claude/trivia')
durs = json.load(open('durs.json'))
FADE, LEAD, TAIL = 0.7, 0.9, 1.1
os.makedirs('segs', exist_ok=True)
starts = []; t = 0.0; lst = []
for i, d in enumerate(durs):
    L = FADE + LEAD + d + TAIL + FADE
    starts.append(t + FADE + LEAD)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', f'{L:.3f}', '-i', f'slides/{i:02d}.png',
                    '-vf', f'fade=t=in:st=0:d={FADE},fade=t=out:st={L - FADE:.3f}:d={FADE},format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-tune', 'stillimage', '-r', '30', f'segs/{i:02d}.mp4'], check=True)
    lst.append(f"file 'segs/{i:02d}.mp4'"); t += L
open('segs.txt', 'w').write('\n'.join(lst))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'segs.txt', '-c', 'copy', 'video.mp4'], check=True)
total = t
SR = 44100
b = np.fromfile('/home/claude/sleep/bgm_orig.raw', np.int16).astype(np.float32).reshape(-1, 2) / 32768
n = int(total * SR) + SR
out = b.copy()
while len(out) < n:
    src = b[int(30 * SR):]; xf = int(4 * SR); fade = np.linspace(0, 1, xf)[:, None]
    out[-xf:] = out[-xf:] * (1 - fade) + src[:xf] * fade
    out = np.concatenate([out, src[xf:]])
bgm = out[:n]; fo = int(3 * SR); bgm[-fo:] *= np.linspace(1, 0, fo)[:, None]
fi = int(2 * SR); bgm[:fi] *= np.linspace(0, 1, fi)[:, None]
voice = np.zeros(n, np.float32)
for i, st in enumerate(starts):
    with wave.open(f'voice/{i:02d}.wav') as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    s0 = int(st * SR); voice[s0:s0 + len(x)] += x[:n - s0]
voice /= np.abs(voice).max() + 1e-9
env = np.convolve(np.abs(voice), np.ones(int(SR * 0.3)) / (SR * 0.3), mode='same')
mix = bgm * (1 - 0.45 * np.clip(env * 10, 0, 1))[:, None] + voice[:, None] * 0.55
pcm = (np.clip(np.tanh(mix * 1.05), -1, 1) * 32767).astype(np.int16)
with wave.open('mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'video.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                'trivia20_sleep.mp4'], check=True)
json.dump(starts, open('starts.json', 'w'))
print('total', round(total, 1))
