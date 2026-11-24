import math, random, subprocess, sys, wave, os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scripts import MOVES, FILES

W, H = 1080, 1920
FPS = 30
CX = 510
FD = '/usr/share/fonts/opentype/noto/'
_fc = {}
def font(name, sz):
    k = (name, sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name, sz, index=0)
    return _fc[k]
SANS_B = 'NotoSansCJK-Black.ttc'; SANS_BD = 'NotoSansCJK-Bold.ttc'; SERIF = 'NotoSerifCJK-Black.ttc'

def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def back(x):  # overshoot pop
    x = min(1, max(0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------------- timing ----------------
def speak_dur(t):
    mora = 0.0; pause = 0.0
    for ch in t:
        if ch in '、，': pause += 0.18
        elif ch in '。！？…': pause += 0.28
        elif re.match(r'[一-鿿]', ch): mora += 1.8
        elif re.match(r'[0-9０-９]', ch): mora += 1.6
        elif ch in '〜「」（）・ ': pass
        else: mora += 1.0
    return mora / 7.6 + pause + 0.35

def timeline(lines):
    t = 0.35; out = []
    for ln in lines:
        d = max(1.6, speak_dur(ln['text']))
        if ln.get('reveal'): d += 0.6
        out.append((t, t + d)); t += d + 0.12
    return out, t + 0.9

# ---------------- text layers ----------------
def text_layer(s, f, fill, stroke=0, stroke_fill=(0, 0, 0), glow=None, gblur=18, shadow=True, track=0):
    d0 = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    if track:
        ws = [f.getlength(c) for c in s]; tw = sum(ws) + track * (len(s) - 1)
    l, t, r, b = d0.textbbox((0, 0), s, font=f, stroke_width=stroke)
    if track: r = l + tw + stroke * 2
    pad = 50
    lay = Image.new('RGBA', (int(r - l + 2 * pad), int(b - t + 2 * pad)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if track:
        x = pad - l
        for c, w_ in zip(s, ws):
            d.text((x, pad - t), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill); x += w_ + track
    else:
        d.text((pad - l, pad - t), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    a = lay.getchannel('A')
    out = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.85)))
        out.alpha_composite(sh, (0, 6))
    if glow:
        gl = Image.new('RGBA', lay.size, tuple(glow) + (0,)); gl.putalpha(a.filter(ImageFilter.GaussianBlur(gblur)).point(lambda v: int(v * 0.8)))
        out.alpha_composite(gl)
    out.alpha_composite(lay)
    return out

def wrap(text, n=13):
    # break at punctuation near the middle when long
    if len(text) <= n: return [text]
    best = None
    for i, ch in enumerate(text):
        if ch in '、。！？…' and 3 < i < len(text) - 2:
            score = abs((i + 1) - len(text) / 2)
            if best is None or score < best[0]: best = (score, i + 1)
    if best and best[1] <= n + 4 and len(text) - best[1] <= n + 4:
        k = best[1]
    else:
        k = (len(text) + 1) // 2
    return [text[:k], text[k:]]

def paste_c(img, lay, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.01: return
    if abs(scale - 1) > 0.01:
        lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.BILINEAR)
    if alpha < 0.99:
        lay = lay.copy(); lay.putalpha(lay.getchannel('A').point(lambda v: int(v * alpha)))
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

# ---------------- audio ----------------
SR = 44100
def make_audio(name, tl, dur, path):
    n = int(SR * dur); t = np.arange(n) / SR; g = np.random.default_rng(1)
    def lp(x, fc):
        X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X * np.exp(-(f / fc) ** 2), len(x))
    def hp(x, fc):
        X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X * (1 - np.exp(-(f / fc) ** 2)), len(x))
    def norm(x): return x / (np.abs(x).max() + 1e-9)
    out = np.zeros(n)
    noise = g.standard_normal(n)
    on = np.clip((t - 0.45) / 0.3, 0, 1) * np.clip((dur - t) / 0.8, 0, 1)
    bed = {'kaen': norm(lp(noise, 500)) * (1 + 0.25 * np.sin(2 * np.pi * 1.3 * t)) + 0.3 * norm(hp(lp(noise, 6000), 2500)) * (g.random(n) < 0.002) * 3,
           'bakuhatsu': norm(lp(noise, 160)) * 1.2,
           'fubuki': norm(lp(hp(noise, 300), 1800)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.23 * t + np.sin(2 * np.pi * 0.11 * t) * 2)),
           'hydro': norm(lp(hp(noise, 200), 2500)),
           'hakai': norm(lp(noise, 300)) * 0.6 + 0.5 * np.sin(2 * np.pi * 55 * t) * (1 + 0.3 * np.sin(2 * np.pi * 6 * t)) + 0.25 * np.sin(2 * np.pi * 110.5 * t),
           'volt': norm(lp(noise, 250)) * 0.6 + norm(hp(noise, 3000)) * (g.random(n) < 0.004) * 2.5 + 0.15 * np.sin(2 * np.pi * 50 * t) * (1 + np.sign(np.sin(2 * np.pi * 7 * t)))}[name]
    out += 0.12 * norm(bed) * on
    def seg(a, b): return slice(int(a * SR), min(n, int(b * SR)))
    # ignition whoosh + hit
    s = seg(0.0, 0.6); m = s.stop - s.start; x = norm(lp(g.standard_normal(m), 3000)) * np.linspace(0, 1, m) ** 2
    out[s] += 0.35 * x
    s = seg(0.5, 2.5); m = s.stop - s.start; tt = np.arange(m) / SR
    out[s] += 0.55 * np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-tt * 5)) / SR) * np.exp(-tt * 2.2) + 0.3 * norm(lp(g.standard_normal(m), 600)) * np.exp(-tt * 3)
    lines = MOVES[name]['lines']
    for (a, b), ln in zip(tl, lines):
        if ln.get('card'):
            s = seg(a, a + 0.12); m = s.stop - s.start; tt = np.arange(m) / SR
            out[s] += 0.16 * np.sin(2 * np.pi * np.cumsum(900 + 900 * tt / 0.12) / SR) * np.exp(-tt * 20)
        if ln.get('reveal_pre'):    # riser into the reveal
            s = seg(a + 0.2, b + 0.1); m = s.stop - s.start; tt = np.arange(m) / SR
            out[s] += 0.12 * norm(hp(g.standard_normal(m), 1500)) * (tt / tt[-1]) ** 2
            out[s] += 0.08 * np.sin(2 * np.pi * np.cumsum(200 + 600 * (tt / tt[-1]) ** 2) / SR)
        if ln.get('reveal'):
            s = seg(a, a + 2.2); m = s.stop - s.start; tt = np.arange(m) / SR
            out[s] += 0.7 * np.sin(2 * np.pi * np.cumsum(35 + 80 * np.exp(-tt * 6)) / SR) * np.exp(-tt * 1.8)
            out[s] += 0.35 * norm(lp(g.standard_normal(m), 900)) * np.exp(-tt * 4)
            out[s] += 0.12 * norm(hp(g.standard_normal(m), 4000)) * np.exp(-tt * 14)
    out = np.tanh(out * 1.1) * 0.85
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

# ---------------- srt ----------------
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}'

def write_srt(name, tl, path):
    with open(path, 'w', encoding='utf-8') as f:
        for i, ((a, b), ln) in enumerate(zip(tl, MOVES[name]['lines'])):
            f.write(f'{i + 1}\n{ts(a)} --> {ts(b)}\n{ln["text"]}\n\n')

# ---------------- main render ----------------
def render(name, outdir, preview=None):
    M = MOVES[name]; acc = tuple(M['accent'])
    tl, dur = timeline(M['lines'])
    nvar = len([f for f in os.listdir('/home/claude/video/frames') if f.startswith(name + '_')])
    V = [np.load(f'/home/claude/video/frames/{name}_{i}.npy').astype(np.float32) for i in range(nvar)]
    order = list(range(nvar)) + list(range(nvar - 2, 0, -1))      # ping-pong
    y = np.arange(H, dtype=np.float32)[:, None, None]
    band = 1 - np.clip((y - 960) / 220, 0, 1) * 0.62
    top = 1 - np.clip(1 - y / 330, 0, 1) * 0.35
    shade = (band * top).astype(np.float32)

    # cached text
    f_sub = font(SANS_B, 62)
    subs = [[text_layer(s, f_sub, (255, 255, 255, 255), stroke=9) for s in wrap(ln['text'])] for ln in M['lines']]
    hook_a = text_layer('もし現実で', font(SANS_B, 84), (255, 255, 255, 255), stroke=0, track=6)
    sz = 220
    while font(SERIF, sz).getlength(M['title']) > 900: sz -= 4
    hook_b = text_layer(M['title'], font(SERIF, sz), (255, 255, 255, 255), glow=acc, gblur=30)
    hook_c = text_layer('を撃ったら？', font(SANS_B, 84), (255, 255, 255, 255), track=6)
    header = text_layer(f'もし現実で{M["title"]}を撃ったら', font(SANS_BD, 42), (255, 255, 255, 235))
    cards = []
    for ln in M['lines']:
        if ln.get('card'):
            lab, big = ln['card']
            bsz = 150
            while font(SANS_B, bsz).getlength(big) > 900: bsz -= 6
            cards.append((text_layer(lab, font(SANS_BD, 50), (255, 255, 255, 255)),
                          text_layer(big, font(SANS_B, bsz), acc + (255,), glow=acc, gblur=20)))
        else:
            cards.append(None)
    q_lab = text_layer(M['label'], font(SANS_BD, 52), (255, 255, 255, 255))
    q_hid = text_layer(M['hidden'] + M['unit'], font(SANS_B, 150), acc + (255,), glow=acc, gblur=22)
    asz = 170
    while font(SANS_B, asz).getlength(M['answer']) > 940: asz -= 6
    q_ans = text_layer(M['answer'], font(SANS_B, asz), acc + (255,), glow=acc, gblur=26)
    reveal_t = [a for (a, b), ln in zip(tl, M['lines']) if ln.get('reveal')][0]
    pre_t = [a for (a, b), ln in zip(tl, M['lines']) if ln.get('reveal_pre')][0]

    proc = None
    frames = range(int(dur * FPS)) if preview is None else [int(x * FPS) for x in preview]
    if preview is None:
        wav = f'{outdir}/{name}.wav'; make_audio(name, tl, dur, wav)
        proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                                 '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                                 '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                                 f'{outdir}/{FILES[name]}.mp4'], stdin=subprocess.PIPE)
    for fi in frames:
        t = fi / FPS
        # background variant crossfade
        p = t * 3.0
        i0 = order[int(p) % len(order)]; i1 = order[(int(p) + 1) % len(order)]; k = p - int(p)
        bg = V[i0] * (1 - k) + V[i1] * k
        # ignition: dark start, flash at 0.5s
        ign = ease((t - 0.35) / 0.35)
        bg = bg * (0.18 + 0.82 * ign)
        flash = max(0.0, 1 - abs(t - 0.62) / 0.22) * 0.55
        rv = t - reveal_t
        if 0 <= rv < 0.35: flash = max(flash, (1 - rv / 0.35) * 0.75)
        flick = 1 + 0.035 * math.sin(t * 23) + 0.02 * math.sin(t * 41)
        bg = bg * flick
        if flash > 0: bg = bg * (1 - flash) + 255 * flash
        bg = bg * shade
        im = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
        # camera push-in + shake
        z = 1.0 + 0.07 * (t / dur)
        sh = 0.0
        if 0.5 <= t < 1.4: sh = 14 * (1 - (t - 0.5) / 0.9)
        if 0 <= rv < 1.0: sh = max(sh, 26 * (1 - rv))
        dx = sh * math.sin(t * 71); dy = sh * math.cos(t * 59)
        cw, ch = W / z, H / z
        x0 = (W - cw) / 2 + dx; y0 = (H - ch) * 0.42 + dy
        im = im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), resample=Image.BILINEAR)
        im = im.convert('RGBA')
        # ---- overlays
        a0, b0 = tl[0]
        if t < b0 + 0.25:                                    # hook title
            al = min(1, (t - 0.3) / 0.2) * (1 - ease((t - b0) / 0.25))
            paste_c(im, hook_a, CX, 640, 1.0, al)
            paste_c(im, hook_b, CX, 820, back((t - 0.45) / 0.35) if t > 0.45 else 0.01, al if t > 0.45 else 0)
            paste_c(im, hook_c, CX, 1010, 1.0, al * ease((t - 0.7) / 0.2))
        else:
            paste_c(im, header, CX, 430, 1.0, ease((t - b0 - 0.1) / 0.3))
        for j, ((a, b), ln) in enumerate(zip(tl, M['lines'])):
            if a <= t < b + 0.12:
                # subtitle
                lines = subs[j]
                ys = [1405] if len(lines) == 1 else [1365, 1450]
                al = min(1, (t - a) / 0.1)
                for L, yy in zip(lines, ys): paste_c(im, L, CX, yy, 1.0, al)
                if j == 0: pass
                if cards[j]:
                    sc = back((t - a) / 0.28); al2 = min(1, (t - a) / 0.12) * min(1, (b + 0.12 - t) / 0.15)
                    paste_c(im, cards[j][0], CX, 1080, 1.0, al2)
                    paste_c(im, cards[j][1], CX, 1210, sc, al2)
                if ln.get('reveal_pre'):
                    pulse = 1 + 0.04 * math.sin(t * 12)
                    al2 = min(1, (t - a) / 0.15)
                    paste_c(im, q_lab, CX, 1080, 1.0, al2)
                    paste_c(im, q_hid, CX, 1210, pulse, al2)
        # answer stays from reveal to end
        if rv >= 0:
            paste_c(im, q_lab, CX, 1080, 1.0, 1.0)
            paste_c(im, q_ans, CX, 1215, back(rv / 0.35) * (1.25 - 0.25 * ease(rv / 0.35)) if rv < 0.5 else 1.0, 1.0)
        fr = im.convert('RGB')
        if preview is not None:
            fr.save(f'{outdir}/prev_{name}_{t:.1f}.png')
        else:
            proc.stdin.write(fr.tobytes())
    if proc:
        proc.stdin.close(); proc.wait()
        write_srt(name, tl, f'{outdir}/{FILES[name]}.srt')
        print('video done', name, round(dur, 1), 's', flush=True)
    return tl, dur

if __name__ == '__main__':
    name = sys.argv[1]
    out = '/home/claude/video/out'; os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[2] == 'preview':
        tl, dur = timeline(MOVES[name]['lines'])
        pts = [0.2, 0.7, 1.5] + [ (a + b) / 2 for a, b in tl[1:]]
        render(name, out, preview=pts)
        print([round(a, 1) for a, b in tl], round(dur, 1))
    else:
        render(name, out)
