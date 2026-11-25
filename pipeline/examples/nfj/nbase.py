"""もし人間がノミの跳躍力を持っていたら（共通の部品）"""
import json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1920, 1080, 30
G = '/home/claude/nfj'
NOTO = '/usr/share/fonts/opentype/noto/'
def Fo(s): return ImageFont.truetype(NOTO + 'NotoSansCJK-Black.ttc', s, index=0)
def Fb(s): return ImageFont.truetype(NOTO + 'NotoSansCJK-Bold.ttc', s, index=0)
def Mi(s): return ImageFont.truetype(NOTO + 'NotoSerifCJK-Black.ttc', s, index=0)
PALE = (245, 240, 230); GOLD = (255, 210, 80); RED = (240, 90, 90); BLUE = (120, 190, 255); GREEN = (140, 220, 130); GRAY = (200, 200, 205)
FLEA_C = (205, 140, 90); HOP_C = (150, 215, 120); HUM_C = (235, 225, 210)
DISC = '※実データをもとにした、単純化した空想のシミュレーションです（数値は目安）'
g = 9.8
V_FLEA = 1.9; V_HUM = math.sqrt(2 * g * 0.494); V_HOP = 4.0     # 踏み切りの速さ（m/s）
def hv(v): return v * v / (2 * g)                                # 跳べる高さ（m、空気抵抗なし）

def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return 1 - (1 - u) ** 3
_BG = {}
def bg(w=W, h=H, tint=(18, 22, 36)):
    k = (w, h, tint)
    if k not in _BG:
        y = np.linspace(0, 1, h)[:, None, None]; c0 = np.array(tint, float); c1 = c0 * 0.45
        a = (c0 * (1 - y) + c1 * y) * np.ones((1, w, 1))
        rng = np.random.default_rng(3); im = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
        for _ in range(int(w * h / 9000)):
            x, yy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(0.6, 1.8); al = int(rng.uniform(30, 110))
            d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 255, 255, al))
        _BG[k] = im
    return _BG[k].copy()
def disc(d, w=W, h=H):
    d.text((w - 24, h - 20), DISC, font=Fb(20 if w > h else 24), fill=(215, 215, 220), anchor='rs')

def figure(d, x, yfoot, cm, crouch=0.0, col=HUM_C):
    """横向きの人（身長175cm）。cm：1cmあたりのpx。crouch：0〜1"""
    L = 175 * cm
    if L < 14:
        r = max(3, L / 3); d.ellipse((x - r, yfoot - L - r, x + r, yfoot - L + r * 0.2), fill=col); d.line((x, yfoot - L, x, yfoot), fill=col, width=max(2, int(r * 0.8))); return
    shin = L * 0.25; thigh = L * 0.25; torso = L * 0.32; head = L * 0.12; kb = crouch * 0.95
    ankle = (x, yfoot); knee = (x + shin * math.sin(kb * 0.8), yfoot - shin * math.cos(kb * 0.8))
    hip = (knee[0] - thigh * math.sin(kb * 1.3), knee[1] - thigh * math.cos(kb * 1.3))
    sh = (hip[0] + torso * math.sin(kb * 0.55), hip[1] - torso * math.cos(kb * 0.55)); w = max(2, int(L * 0.07))
    d.line([ankle, knee], fill=col, width=w + max(1, int(L * 0.015))); d.line([knee, hip], fill=col, width=w + max(1, int(L * 0.025)))
    d.line([hip, sh], fill=col, width=w + max(2, int(L * 0.055)))
    d.ellipse((sh[0] - head / 2 + L * 0.015, sh[1] - head - L * 0.01, sh[0] + head / 2 + L * 0.015, sh[1] + L * 0.015), fill=col)
    arm = (sh[0] - L * 0.18 * math.cos(crouch * 1.2), sh[1] + L * 0.2 * (1 - crouch * 1.6)); d.line([sh, arm], fill=col, width=max(2, w - 2))
    d.polygon([(x - L * 0.035, yfoot), (x + L * 0.17, yfoot), (x + L * 0.17, yfoot - L * 0.045), (x - L * 0.015, yfoot - L * 0.055)], fill=(60, 70, 90))

def _rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a); return [(cx + (px - cx) * c - (py - cy) * s, cy + (px - cx) * s + (py - cy) * c) for px, py in pts]
def flea(d, x, y, s, crouch=0.0, col=(150, 85, 45)):
    """横向きのノミ（右向き）。(x,y)：足元の中心、s：体長px"""
    dark = tuple(int(c * 0.55) for c in col); lw = max(2, int(s * 0.05))
    by = y - s * (0.46 - 0.14 * crouch); A, Bb = s * 0.5, s * 0.27
    # 脚
    hip = (x - s * 0.12, by + s * 0.16); knee = (x - s * (0.42 - 0.05 * crouch), by + s * (0.02 + 0.12 * (1 - crouch))); foot = (x - s * (0.05 + 0.25 * crouch), y)
    d.line([hip, knee, foot], fill=dark, width=int(lw * 1.6), joint='curve')
    for hx, kx, fx in [(0.08, 0.2, 0.12), (0.26, 0.42, 0.36)]:
        d.line([(x + s * hx, by + s * 0.18), (x + s * kx, by + s * (0.3 - 0.08 * crouch)), (x + s * fx, y)], fill=dark, width=lw, joint='curve')
    pts = []
    for t in np.linspace(0, 2 * math.pi, 48):
        px, py = A * math.cos(t), Bb * math.sin(t); r = -0.1
        pts.append((x + px * math.cos(r) - py * math.sin(r), by + px * math.sin(r) + py * math.cos(r)))
    d.polygon(pts, fill=col)
    for k in range(5):
        dx = (-0.3 + k * 0.14) * s; hh = Bb * math.sqrt(max(0, 1 - (dx / A) ** 2)) * 0.92
        d.line([(x + dx - hh * 0.1, by - hh - dx * 0.1), (x + dx + hh * 0.1, by + hh - dx * 0.1)], fill=dark, width=max(1, int(s * 0.02)))
    d.ellipse((x - s * 0.32, by - s * 0.2, x + s * 0.05, by - s * 0.1), fill=tuple(min(255, int(c * 1.35)) for c in col))
    hx, hy = x + s * 0.52, by + s * 0.03
    d.ellipse((hx - s * 0.14, hy - s * 0.13, hx + s * 0.14, hy + s * 0.13), fill=col)
    d.ellipse((hx + s * 0.02, hy - s * 0.07, hx + s * 0.08, hy - s * 0.01), fill=(20, 15, 10))
    d.line([(hx + s * 0.1, hy + s * 0.08), (hx + s * 0.15, hy + s * 0.22)], fill=dark, width=max(1, int(s * 0.025)))
def hopper(d, x, y, s, col=(110, 150, 70)):
    """アワフキムシ（右向き）"""
    dark = tuple(int(c * 0.6) for c in col)
    d.line([(x - s * 0.1, y - s * 0.12), (x - s * 0.25, y - s * 0.02), (x - s * 0.15, y)], fill=dark, width=max(2, int(s * 0.06)))
    pts = [(x - s * 0.5, y - s * 0.12), (x + s * 0.25, y - s * 0.4), (x + s * 0.48, y - s * 0.28), (x + s * 0.5, y - s * 0.14), (x + s * 0.2, y - s * 0.08)]
    d.polygon(pts, fill=col); d.line([(x - s * 0.45, y - s * 0.14), (x + s * 0.25, y - s * 0.36)], fill=dark, width=max(1, int(s * 0.03)))
    d.ellipse((x + s * 0.32, y - s * 0.32, x + s * 0.4, y - s * 0.24), fill=(40, 20, 10))
    d.ellipse((x - s * 0.2, y - s * 0.26, x - s * 0.05, y - s * 0.18), fill=(200, 190, 140))
    d.line([(x + s * 0.2, y - s * 0.1), (x + s * 0.25, y)], fill=dark, width=max(1, int(s * 0.04)))

def ruler_m(d, x, ygr, s, hmax_px, col=GRAY, side='r'):
    """メートルの目盛り。s：1mあたりのpx"""
    step = next(v for v in [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100] if v * s >= 70)
    d.line((x, ygr, x, ygr - hmax_px), fill=col, width=4); k = 0
    while k * step * s <= hmax_px:
        y = ygr - k * step * s; v = k * step
        d.line((x, y, x + 20, y), fill=col, width=3)
        lab = f'{v * 100:.0f}cm' if step < 1 else f'{v:.0f}m'
        if k: d.text((x - 12, y), lab, font=Fb(26), fill=col, anchor='rm')
        k += 1
def building(d, x, ygr, wm, hm, s, col=(70, 82, 110), floors=0):
    x0, x1, y0 = x, x + wm * s, ygr - hm * s; d.rectangle((x0, y0, x1, ygr), fill=col)
    if floors and s * hm / floors > 6:
        fh = hm * s / floors
        for f in range(floors):
            yy = ygr - (f + 0.7) * fh
            for c in range(int(wm / 4)):
                xx = x0 + (c + 0.3) * (wm * s / int(wm / 4)); d.rectangle((xx, yy, xx + wm * s / int(wm / 4) * 0.45, yy + fh * 0.45), fill=(210, 200, 120) if (f * 7 + c * 3) % 5 else (95, 105, 135))
    elif floors:
        d.rectangle((x0 + 2, y0 + 2, x1 - 2, ygr), fill=tuple(int(c * 1.15) for c in col))
def caption(d, txt, col=PALE, y=H - 125, w=W):
    f_ = Fo(52); tw = f_.getlength(txt)
    d.rounded_rectangle((w / 2 - tw / 2 - 40, y - 45, w / 2 + tw / 2 + 40, y + 45), 16, fill=(8, 10, 16, 220)); d.text((w / 2, y), txt, font=f_, fill=col, anchor='mm')
def scene(key, dur, draw, cues):
    n = int(dur * FPS); p = writer(f'{G}/c_{key}.mp4')
    for f in range(n):
        im = bg(); d = ImageDraw.Draw(im); draw(im, d, f / FPS); disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, cues
