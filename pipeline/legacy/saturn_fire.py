import math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter

W, H = 1080, 1920
FPS, DUR = 30, 16.5
NF = int(FPS * DUR)
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
rng = np.random.default_rng(11)

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def win(t, a, b): return float(ease((t - a) / 0.001)) if False else (1.0 if a <= t < b else 0.0)

# ---------------- geometry ----------------
CX, CY, R = 540, 880, 250
RY0, RY1 = 480, 1290               # scene region rows
RH = RY1 - RY0
TILT = math.radians(-14)
RING_K = 0.30
P_TOUCH = (CX + R * math.cos(math.radians(38)), CY + R * math.sin(math.radians(38)))

def smoothstep(e0, e1, x): return ease((x - e0) / (e1 - e0))

def build_sprites():
    S = 2
    ys, xs = np.mgrid[0:RH * S, 0:W * S].astype(np.float32)
    x = (xs + 0.5) / S - CX
    y = (ys + 0.5) / S + RY0 - CY
    c, s = math.cos(TILT), math.sin(TILT)
    xr = c * x + s * y
    yr = -s * x + c * y
    d = np.sqrt(x * x + y * y) / R
    pa = np.clip((1 - d) * R * S, 0, 1)                        # planet alpha (AA)
    z = np.sqrt(np.clip(1 - d * d, 0, 1))
    L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
    shade = np.clip((x / R) * L[0] + (y / R) * L[1] + z * L[2], 0, 1)
    lat = yr / R
    band = (0.5 + 0.5 * np.sin(lat * 23 + 0.6 * np.sin(lat * 7))) * 0.6 + (0.5 + 0.5 * np.sin(lat * 61)) * 0.4
    base = np.array([232, 204, 150], np.float32)
    alt = np.array([196, 150, 96], np.float32)
    pc = base * (1 - band[..., None] * 0.55) + alt * (band[..., None] * 0.55)
    pc = pc * (0.25 + 0.85 * shade[..., None] ** 0.8)
    # rings
    u, v = xr, yr / RING_K
    r = np.sqrt(u * u + v * v)
    ring = np.zeros_like(r)
    for a0, a1, op in [(318, 345, 0.25), (345, 420, 0.85), (420, 430, 0.5), (437, 470, 0.95), (470, 492, 0.75), (500, 512, 0.55)]:
        ring += op * smoothstep(a0 - 1.2, a0 + 1.2, r) * (1 - smoothstep(a1 - 1.2, a1 + 1.2, r))
    ring *= 0.85 + 0.15 * np.sin(r * 0.9)
    rcol = np.stack([235 - 0.08 * (r - 330), 215 - 0.12 * (r - 330), 175 - 0.15 * (r - 330)], -1).clip(80, 255)
    # planet shadow on back-right of rings
    front = (v > 0).astype(np.float32)
    shadow = ((u > 0) & (np.abs(v * RING_K) < R * 0.9) & (v < 0)).astype(np.float32)
    rcol = rcol * (1 - 0.0 * shadow[..., None])
    def ds(a):
        if a.ndim == 2: return a.reshape(RH, S, W, S).mean((1, 3))
        return a.reshape(RH, S, W, S, a.shape[2]).mean((1, 3))
    out = dict(pa=ds(pa), pc=ds(pc * pa[..., None]) / np.maximum(ds(pa), 1e-4)[..., None],
               shade=ds(shade), ra_b=ds(ring * (1 - front)), ra_f=ds(ring * front),
               rc=ds(rcol), rr=ds(r))
    out['glow'] = gaussian_filter(out['pa'], 45)
    out['glow2'] = gaussian_filter(out['pa'], 140)
    yy, xx = np.mgrid[0:RH, 0:W].astype(np.float32)
    out['dist'] = np.sqrt((xx - P_TOUCH[0]) ** 2 + (yy + RY0 - P_TOUCH[1]) ** 2)
    return out

def fractal(n, octaves=6, seed=0):
    g = np.random.default_rng(seed)
    acc = np.zeros((n, n), np.float32); amp = 1; tot = 0
    for o in range(octaves):
        k = 4 * 2 ** o
        a = g.random((k, k)).astype(np.float32)
        im = Image.fromarray((a * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        acc += amp * np.asarray(im, np.float32) / 255; tot += amp; amp *= 0.55
    acc /= tot
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    return acc

def make_bg():
    a = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array([6, 6, 22]), np.array([22, 12, 40])
    bg = (top * (1 - a) + bot * a) * np.ones((1, W, 1))
    neb = fractal(1024, 5, 3)
    neb = np.asarray(Image.fromarray((neb * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    bg += (np.clip(neb - 0.5, 0, 1) ** 1.5 * 90)[..., None] * np.array([0.6, 0.3, 1.0])
    im = Image.fromarray(bg.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    g = random.Random(5)
    for _ in range(420):
        x, y = g.uniform(0, W), g.uniform(0, H); r = g.choice([0.8, 1, 1, 1.4, 2, 2.6])
        b = g.randint(150, 255)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, min(255, b + 20)))
    return np.asarray(im, np.float32)

FIRE_STOPS = [(0, (40, 0, 0)), (0.3, (150, 20, 0)), (0.55, (240, 90, 10)), (0.75, (255, 170, 40)),
              (0.9, (255, 225, 120)), (1, (255, 252, 230))]
def fire_pal(v):
    xs = [s[0] for s in FIRE_STOPS]
    return np.stack([np.interp(v, xs, [s[1][i] for s in FIRE_STOPS]) for i in range(3)], -1).astype(np.float32)

# ---------------- text ----------------
_fonts = {}
def font(sz):
    if sz not in _fonts: _fonts[sz] = ImageFont.truetype(FONT, sz, index=0)
    return _fonts[sz]

def draw_text(img, txt, cx, cy, size, fill, alpha=1.0, scale=1.0, stroke=10, maxw=980, sc=(20, 10, 30)):
    if alpha <= 0.01: return
    sz = int(size * scale)
    f = font(max(8, sz))
    tmp = ImageDraw.Draw(img)
    w = tmp.textlength(txt, font=f)
    if w > maxw * scale:
        sz = int(sz * maxw * scale / w); f = font(sz)
    l, t, r, b = tmp.textbbox((0, 0), txt, font=f, stroke_width=stroke, anchor='mm')
    layer = Image.new('RGBA', (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((-l + 2, -t + 2), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc, anchor='mm')
    if alpha < 1: layer.putalpha(layer.getchannel('A').point(lambda p: int(p * alpha)))
    img.paste(layer, (int(cx + l - 2), int(cy + t - 2)), layer)

def pop(t, a, b):
    """scale, alpha for a card visible in [a,b)"""
    if t < a or t >= b: return 0, 0
    k = (t - a) / 0.28
    sc = 1.0 if k >= 1 else 0.55 + 0.6 * math.sin(min(1, k) * math.pi * 0.62) / math.sin(math.pi * 0.62) * (1 if k < 0.8 else 1)
    sc = min(sc, 1.12) if k < 1 else 1.0
    al = min(1, (t - a) / 0.08) * min(1, (b - t) / 0.15)
    return sc, al

CARDS = [  # start, end, top, big(fmt), bottom, count_to
    (5.0, 7.3, '人類が使うエネルギーの', '約{}兆年分', '', 70),
    (7.3, 9.6, '地球を', '約{}回', 'こなごなにできる', 200),
    (9.6, 11.6, '太陽が', '約{}年', 'かけて出す光と同じ', 4),
    (11.6, 13.7, 'なのに土星は', '吹き飛ばない', '自分の重力が強すぎるから', None),
    (13.8, 16.6, '燃えたあとは', '巨大な水の玉に', '水素＋酸素＝水', None),
]

# ---------------- match ----------------
def make_match():
    S = 2; im = Image.new('RGBA', (300 * S, 300 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # stick from head at (40,40) to (290,290)
    d.line([(40 * S, 40 * S), (290 * S, 290 * S)], fill=(236, 200, 140), width=14 * S)
    d.line([(46 * S, 40 * S), (296 * S, 290 * S)], fill=(205, 165, 110), width=4 * S)
    d.ellipse((22 * S, 22 * S, 62 * S, 62 * S), fill=(150, 30, 30))
    d.ellipse((28 * S, 26 * S, 44 * S, 40 * S), fill=(200, 70, 60))
    return im.resize((300, 300), Image.LANCZOS)
MATCH = make_match()

def match_flame(t):
    S = 2; im = Image.new('RGBA', (120 * S, 160 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = 1 + 0.12 * math.sin(t * 37) + 0.08 * math.sin(t * 23)
    cx, by = 60, 140
    def fl(w, h, col):
        d.ellipse(((cx - w) * S, (by - h * f) * S, (cx + w) * S, (by) * S), fill=col)
    fl(30, 110, (255, 120, 20, 200)); fl(20, 80, (255, 200, 60, 230)); fl(10, 45, (255, 250, 220, 255))
    im = im.resize((120, 160), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.5))
    return im

# ---------------- particles ----------------
class Ember:
    def __init__(self, g, t):
        a = g.uniform(0, 2 * math.pi)
        self.x = CX + R * 0.98 * math.cos(a); self.y = CY + R * 0.98 * math.sin(a)
        sp = g.uniform(60, 220)
        self.vx = math.cos(a) * sp + g.uniform(-30, 30); self.vy = math.sin(a) * sp - g.uniform(20, 90)
        self.t0 = t; self.life = g.uniform(0.6, 1.4); self.r = g.uniform(10, 30)

def main(out, preview=None):
    sp = build_sprites()
    bg = make_bg()
    N1 = fractal(1600, 6, 1); N2 = fractal(1600, 5, 2)
    g = random.Random(9)
    embers = []
    frames = range(NF) if preview is None else [int(x * FPS) for x in preview]
    proc = None
    if preview is None:
        wav = out + '.wav'; make_audio(wav)
        proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                 '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264',
                                 '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                                 '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    pa = sp['pa'][..., None]
    for fi in frames:
        t = fi / FPS
        # --- intensities
        spread = 0.0 if t < 2.6 else float(ease((t - 2.6) / 1.4))
        I = (0.55 * spread if t < 4.0 else 1.0) * (1 - float(ease((t - 11.6) / 2.4)))
        if t < 2.6: I = 0
        Wt = float(ease((t - 13.0) / 1.6))
        pulse = 1 + 0.12 * math.sin(t * 9) + 0.06 * math.sin(t * 23)
        rad = spread * 2.2 * R
        mask = np.clip((rad - sp['dist'] + 60 * (N2[300:300 + RH, 200:200 + W] - 0.5) * 2) / 50, 0, 1)
        if t >= 4.0: mask = np.ones_like(mask)
        mI = (mask * I)[..., None]
        # --- fire texture
        oy = int(700 - t * 55) % 800; ox = int(260 + 40 * math.sin(t * 0.7))
        n1 = N1[oy:oy + RH, ox:ox + W]
        oy2 = int(500 + t * 35) % 800
        n2 = N2[oy2:oy2 + RH, 300:300 + W]
        v = np.clip(0.18 + 0.95 * (0.62 * n1 + 0.38 * n2) * (0.55 + 0.6 * sp['shade']) * pulse, 0, 1)
        hot = fire_pal(v)
        # --- water
        wn = N2[200:200 + RH, 100:100 + W]
        sh = sp['shade'][..., None]
        water = np.array([20, 70, 170], np.float32) * (1 - sh) + np.array([90, 190, 255], np.float32) * sh
        water = water * (0.85 + 0.3 * wn[..., None]) + 255 * (sp['shade'][..., None] ** 24)
        pcol = sp['pc'] * (1 - mI) + hot * mI
        pcol = pcol * (1 - Wt) + water * Wt
        # --- rings
        rI = I * (0.6 + 0.4 * spread)
        rc = sp['rc'] * (1 - 0.65 * rI) + np.array([255, 150, 70], np.float32) * (0.95 * rI) * (1.15 - sp['rr'][..., None] / 600)
        rc = rc * (1 - 0.3 * Wt) + np.array([200, 225, 255], np.float32) * 0.3 * Wt
        # --- composite
        reg = bg[RY0:RY1].copy()
        ab = sp['ra_b'][..., None]; reg = reg * (1 - ab) + rc * ab
        reg = reg * (1 - pa) + pcol * pa
        af = sp['ra_f'][..., None]; reg = reg * (1 - af) + rc * af
        gI = I * pulse
        reg += sp['glow'][..., None] * np.array([255, 120, 30], np.float32) * 1.3 * gI
        reg += sp['glow2'][..., None] * np.array([255, 80, 20], np.float32) * 1.1 * gI
        reg += sp['glow2'][..., None] * np.array([60, 140, 255], np.float32) * 0.5 * Wt
        # embers
        if I > 0.05:
            nspawn = int(10 * I) if t >= 4.0 else int(4 * spread)
            for _ in range(nspawn): embers.append(Ember(g, t))
        layer = Image.new('RGB', (W, RH), (0, 0, 0)); ld = ImageDraw.Draw(layer)
        alive = []
        for e in embers:
            a = (t - e.t0) / e.life
            if a >= 1 or a < 0: continue
            alive.append(e)
            x = e.x + e.vx * (t - e.t0); y = e.y + e.vy * (t - e.t0) - RY0
            r = e.r * (1 - a * 0.7)
            col = fire_pal(np.array(1 - a * 0.8))
            k = (1 - a) * I
            ld.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(c * k) for c in col))
        embers = alive
        if embers:
            reg += np.asarray(layer.filter(ImageFilter.GaussianBlur(6)), np.float32) * 1.4
        frame = bg.copy(); frame[RY0:RY1] = reg
        # flash
        fl = 0.0
        if 2.6 <= t < 3.0: fl = 0.35 * (1 - (t - 2.6) / 0.4)
        if 4.0 <= t < 4.9: fl = 0.95 * (1 - (t - 4.0) / 0.9) ** 2
        if 13.0 <= t < 13.8: fl = max(fl, 0.25 * math.sin(math.pi * (t - 13.0) / 0.8))
        if fl > 0: frame = frame * (1 - fl) + np.array([255, 245, 225]) * fl
        frame = np.clip(frame, 0, 255).astype(np.uint8)
        # shake
        A = 0
        if 2.6 <= t < 4.0: A = 7 * (t - 2.6) / 1.4
        elif 4.0 <= t < 11.6: A = 4 + 26 * math.exp(-(t - 4.0) * 3)
        if A > 0:
            dx = int(A * math.sin(t * 61)); dy = int(A * math.sin(t * 47 + 1))
            frame = np.roll(frame, (dy, dx), (0, 1))
        img = Image.fromarray(frame)
        # match
        if t < 4.0:
            k = float(ease((t - 0.9) / 1.6))
            hx = lerp(1180, P_TOUCH[0] + 14, k); hy = lerp(1620, P_TOUCH[1] + 14, k)
            img.paste(MATCH, (int(hx - 40), int(hy - 40)), MATCH)
            if t >= 0.6:
                mf = match_flame(t)
                img.paste(mf, (int(hx - 60), int(hy - 140)), mf)
        # texts
        draw_text(img, '土星に火をつけたら…？', 540, 220, 96, (255, 255, 255))
        draw_text(img, '※ 酸素があると仮定', 540, 335, 46, (255, 214, 90), stroke=7)
        if 4.0 <= t < 5.0:
            sc, al = pop(t, 4.0, 5.0)
            draw_text(img, 'ボォォォッ！！', 540, 1430, 150, (255, 140, 30), al, sc * (1 + 0.04 * math.sin(t * 40)), stroke=14)
        for (a, b, top, big, bot, cnt) in CARDS:
            sc, al = pop(t, a, b)
            if al <= 0: continue
            if cnt is not None:
                k = float(ease((t - a) / 0.7))
                bigt = big.format(max(1, int(round(cnt * k))) if cnt > 4 else max(1, int(round(cnt * k))))
            else:
                bigt = big
            draw_text(img, top, 540, 1440, 62, (255, 255, 255), al, sc, stroke=9)
            col = (120, 210, 255) if a >= 13.8 else (255, 222, 70)
            draw_text(img, bigt, 540, 1590, 160, col, al, sc, stroke=14)
            if bot: draw_text(img, bot, 540, 1740, 58, (255, 255, 255), al, sc, stroke=9)
        if t >= 13.8:
            draw_text(img, '※燃やすには土星の約5倍の重さの酸素が必要', 540, 1850, 34, (200, 200, 220), min(1, (t - 13.8) / 0.3), stroke=5)
        if preview is not None:
            img.save(f'{out}_{t:.1f}.png')
        else:
            proc.stdin.write(img.tobytes())
    if proc:
        proc.stdin.close(); proc.wait(); print('done', proc.returncode)

def lerp(a, b, k): return a + (b - a) * k

# ---------------- audio ----------------
def make_audio(path):
    sr = 44100; n = int(sr * DUR); t = np.arange(n) / sr
    g = np.random.default_rng(4)
    out = np.zeros(n)
    def lp(x, fc):
        X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / sr); return np.fft.irfft(X * np.exp(-(f / fc) ** 2), len(x))
    def hp(x, fc):
        X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / sr); return np.fft.irfft(X * (1 - np.exp(-(f / fc) ** 2)), len(x))
    def seg(a, b): return slice(int(a * sr), min(n, int(b * sr)))
    # space drone
    out += 0.05 * np.sin(2 * np.pi * 55 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * t))
    out += 0.04 * np.sin(2 * np.pi * 82.5 * t)
    # match strike
    s = seg(0.55, 0.85); x = hp(g.standard_normal(s.stop - s.start), 2500); e = np.exp(-np.linspace(0, 6, len(x)))
    out[s] += 0.35 * x / np.abs(x).max() * e
    # match flame hiss
    s = seg(0.6, 2.6); x = lp(g.standard_normal(s.stop - s.start), 1500)
    out[s] += 0.05 * x / np.abs(x).max()
    # ignition whoosh
    s = seg(2.6, 4.0); m = s.stop - s.start; x = g.standard_normal(m)
    x = lp(x, 1800); env = np.linspace(0, 1, m) ** 2
    out[s] += 0.5 * x / np.abs(x).max() * env
    # BOOM
    s = seg(4.0, 7.0); m = s.stop - s.start; tt = np.arange(m) / sr
    freq = 30 + 70 * np.exp(-tt * 3)
    boom = np.sin(2 * np.pi * np.cumsum(freq) / sr) * np.exp(-tt * 1.3)
    nb = lp(g.standard_normal(m), 400) ; nb = nb / np.abs(nb).max() * np.exp(-tt * 2.2)
    cr = hp(g.standard_normal(m), 1500); cr = cr / np.abs(cr).max() * np.exp(-tt * 9)
    out[s] += 0.9 * boom + 0.8 * nb + 0.35 * cr
    # fire roar 4 - 14
    s = seg(4.0, 14.2); m = s.stop - s.start; tt = np.arange(m) / sr + 4.0
    x = lp(g.standard_normal(m), 700); x /= np.abs(x).max()
    env = np.clip((tt - 4.0) / 0.3, 0, 1) * np.clip((14.2 - tt) / 2.4, 0, 1)
    crack = np.zeros(m); idx = g.integers(0, m, 900)
    crack[idx] = g.uniform(-1, 1, 900); crack = hp(lp(crack, 5000), 1200); crack /= np.abs(crack).max()
    out[s] += env * (0.45 * x * (1 + 0.2 * np.sin(2 * np.pi * 1.5 * tt)) + 0.25 * crack)
    # card pops + count ticks
    for (a, b, top, big, bot, cnt) in CARDS:
        s = seg(a, a + 0.14); m = s.stop - s.start; tt = np.arange(m) / sr
        f = 700 + 900 * tt / 0.14
        out[s] += 0.28 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 18)
        if cnt is not None:
            for k in np.arange(a + 0.05, a + 0.7, 0.05):
                s = seg(k, k + 0.02); m = s.stop - s.start; tt = np.arange(m) / sr
                out[s] += 0.12 * np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 200)
    # water bloop + shimmer
    s = seg(13.6, 14.6); m = s.stop - s.start; tt = np.arange(m) / sr
    f = 900 * np.exp(-tt * 3) + 180
    out[s] += 0.35 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 3.5)
    s = seg(13.8, DUR); m = s.stop - s.start; tt = np.arange(m) / sr
    for fq in (1046.5, 1318.5, 1568, 2093):
        out[s] += 0.04 * np.sin(2 * np.pi * fq * tt) * np.exp(-tt * 1.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * tt + fq))
    out = np.tanh(out * 1.2)
    out *= np.clip((DUR - t) / 0.3, 0, 1)
    pcm = (out / np.abs(out).max() * 0.9 * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'preview':
        main(sys.argv[1], [0.3, 2.0, 3.3, 4.2, 6.0, 8.0, 12.5, 15.0])
    else:
        main(sys.argv[1])
