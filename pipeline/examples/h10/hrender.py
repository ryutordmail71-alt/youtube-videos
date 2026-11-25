"""心臓が10個あったら？ の描画部品"""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import hmodel as HM
W, H, FPS = 1920, 1080, 30
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'; NOTOB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'; BEBAS = '/home/claude/fonts/BebasNeue-Regular.ttf'
_F = {}
def font(p, s):
    k = (p, s)
    if k not in _F: _F[k] = ImageFont.truetype(p, s, index=0) if p.endswith('.ttc') else ImageFont.truetype(p, s)
    return _F[k]
def Fo(s): return font(NOTO, s)
def Fb(s): return font(NOTOB, s)
def Mi(s): return font(SERIF, s)
def BE(s): return font(BEBAS, s)
PALE = (240, 240, 245); GOLD = (255, 210, 80); RED = (255, 95, 95); GREEN = (150, 220, 120); GREY = (200, 200, 208); BLUE = (120, 190, 255)
BLOOD = (225, 40, 50); DARKB = (95, 40, 85)
NOTE = '※実データをもとにした、単純化した空想のシミュレーションです'
def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return u * u * (3 - 2 * u)
def f2(x): return f'{math.floor(x * 100 + 0.5) / 100:.2f}'
def mix(a, b, u): return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
def bcol(f): return mix(DARKB, BLOOD, max(0.0, min(1.0, f)))     # 酸素の満タン度 0..1 → 血の色

def heart_icon(d, x, y, r, col, beat=0.0):
    r = r * (1 + 0.22 * beat)
    d.ellipse((x - r, y - r * 0.6, x, y + r * 0.35), fill=col); d.ellipse((x, y - r * 0.6, x + r, y + r * 0.35), fill=col)
    d.polygon([(x - r * 0.97, y - r * 0.05), (x + r * 0.97, y - r * 0.05), (x, y + r * 1.05)], fill=col)
def beat_at(t, hr=170):
    ph = (t * hr / 60.0) % 1.0; return math.exp(-ph * 10) if t >= 0 else 0.0
def hearts_row(d, x, y, n, r, t, hr=170, col=BLOOD, per=5):
    """x,y：中心。n個を最大 per 個ずつ並べる"""
    rows = math.ceil(n / per); k = 0
    for j in range(rows):
        m = min(per, n - j * per)
        for i in range(m):
            cx = x + (i - (m - 1) / 2) * r * 2.3; cy = y + (j - (rows - 1) / 2) * r * 2.1
            heart_icon(d, cx, cy, r, col, beat_at(t + k * 0.037, hr)); k += 1

def sky(w, h, top=(20, 30, 60), bot=(70, 90, 130)):
    a = np.linspace(0, 1, h)[:, None, None]; c = np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a
    return Image.fromarray(np.repeat(c, w, 1).astype(np.uint8))

# ---- 走る人 ----
def runner(d, x, y, h, ph, col=(60, 110, 200), slump=0.0):
    """足元 (x,y)、身長 h px、ph：走りの位相（ラジアン）。slump：へばり具合 0..1"""
    skin = (225, 180, 145); dark = (40, 44, 56); lw = max(4, int(h * 0.075))
    hip = (x, y - h * 0.5); lean = 0.18 + 0.25 * slump
    sh = (x + h * 0.3 * lean, y - h * 0.82 + h * 0.05 * slump)
    amp = 1.0 - 0.5 * slump
    for side, c in ((1, dark), (-1, dark)):
        a = math.sin(ph + (0 if side > 0 else math.pi)) * 0.9 * amp
        kx = hip[0] + math.sin(a) * h * 0.24; ky = hip[1] + math.cos(a) * h * 0.24
        b = a - 0.6 - 0.6 * max(0, -math.cos(ph + (0 if side > 0 else math.pi)))
        fx = kx + math.sin(b) * h * 0.25; fy = min(y, ky + math.cos(b) * h * 0.25)
        d.line((hip, (kx, ky), (fx, fy)), fill=c if side > 0 else (70, 74, 88), width=lw, joint='curve')
    d.line((hip, sh), fill=col, width=int(lw * 2.2))
    for side in (1, -1):
        a = -math.sin(ph + (0 if side > 0 else math.pi)) * 0.9 * amp
        ex = sh[0] + math.sin(a) * h * 0.16; ey = sh[1] + math.cos(a) * h * 0.16
        hx = ex + math.sin(a + 1.4) * h * 0.15; hy = ey - math.cos(a + 1.4) * h * 0.05
        d.line((sh, (ex, ey), (hx, hy)), fill=skin if side > 0 else (200, 160, 130), width=max(3, int(lw * 0.8)), joint='curve')
    hr_ = h * 0.085; hc = (sh[0] + h * 0.05, sh[1] - h * 0.11)
    d.ellipse((hc[0] - hr_, hc[1] - hr_, hc[0] + hr_, hc[1] + hr_), fill=skin)
    d.chord((hc[0] - hr_ * 1.05, hc[1] - hr_ * 1.1, hc[0] + hr_ * 1.05, hc[1] + hr_ * 0.6), 180, 360, fill=(50, 36, 28))
    return ((hip[0] + sh[0]) / 2, (hip[1] + sh[1]) / 2 - h * 0.05)    # 胸のあたり

# ---- 肺の毛細血管（チューブ）----
class Tube:
    """長さ L px のチューブ。血が tt 秒で通り抜ける（SLOW 倍のスロー）"""
    def __init__(self, n=14, slow=8.0): self.pos = 0.0; self.n = n; self.slow = slow
    def step(self, tt, dt): self.pos = (self.pos + dt / (tt * self.slow)) % 1.0
    def draw(self, d, x0, y, L, th, tt, dmg=0.0, t=0.0, label=True, fs=24, below=False):
        d.rounded_rectangle((x0 - 6, y - th / 2 - 6, x0 + L + 6, y + th / 2 + 6), int(th / 2 + 6), fill=(250, 200, 200), outline=(255, 235, 235), width=3)
        d.rounded_rectangle((x0, y - th / 2, x0 + L, y + th / 2), int(th / 2), fill=(70, 20, 30))
        for i in range(self.n):
            u = (self.pos + i / self.n) % 1.0; age = u * tt; f = 1 - math.exp(-age / HM.TAU); f *= (1 - dmg)
            cx = x0 + u * L; r = th * 0.36
            d.ellipse((cx - r, y - r, cx + r, y + r), fill=bcol(f), outline=(30, 10, 15))
        # 0.25秒（満タン）の位置
        if label:
            mx = x0 + L * min(1.0, 0.25 / tt)
            if 0.25 <= tt:
                d.line((mx, y - th / 2 - 16, mx, y + th / 2 + 16), fill=GOLD, width=4)
                if below: d.text((mx, y + th / 2 + 20), '0.25秒で満タン', font=Fb(fs), fill=GOLD, anchor='mt')
                else: d.text((mx, y - th / 2 - 20), '0.25秒で満タン', font=Fb(fs), fill=GOLD, anchor='md')
            else:
                d.text((x0 + L + 14, y), '満タン前に出口！', font=Fb(fs), fill=RED, anchor='lm')
        if dmg > 0.01:
            rng = np.random.default_rng(int(t * 30) // 3)
            for k in range(int(3 + 14 * min(1, dmg * 2))):
                ux = rng.uniform(0.1, 0.9); dy = rng.uniform(0.1, 1.0) * (th * 0.9); r = rng.uniform(3, 7)
                cx = x0 + ux * L; cy = y + (th / 2 + 8 + dy) * (1 if k % 2 else -1)
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(200, 30, 40))
        d.text((x0 - 14, y), '入口', font=Fb(fs), fill=GREY, anchor='rm') if label else None

# ---- 対決 ----
class Battle:
    def __init__(self, NA, NB, T): self.A = HM.Run(NA, T + 1); self.B = HM.Run(NB, T + 1); self.T = T
    def dist(self, R, t):
        i = int(min(len(R.a) - 1, max(0, round(t * 30)))); return float(R.a[:i + 1, 4].sum() / 30 * 0.9)
TRACK = None
def track_bg():
    global TRACK
    if TRACK is None:
        im = sky(W, H).convert('RGBA'); d = ImageDraw.Draw(im)
        for i in range(0, W, 60): d.rectangle((i, 150, i + 40, 200), fill=(40, 50, 80))     # 観客席
        rng = np.random.default_rng(2)
        for k in range(600):
            x = rng.uniform(0, W); y = rng.uniform(150, 250); c = tuple(int(v) for v in rng.integers(60, 200, 3)); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=c)
        d.rectangle((0, 255, W, 268), fill=(240, 240, 240)); d.rectangle((0, 268, W, 660), fill=(178, 72, 52))
        for yy in (268, 460, 652): d.rectangle((0, yy - 3, W, yy + 3), fill=(245, 240, 235))
        TRACK = im
    return TRACK
def name_of(n): return 'ふつうの人（心臓1個）' if n == 1 else f'心臓{n}個の人'
def battle_frame(B, st, title, cap=None, capcol=PALE, tubes=None, f=0):
    im = track_bg().copy(); d = ImageDraw.Draw(im, 'RGBA'); stt = max(0.0, st)
    dA, dB = B.dist(B.A, stt), B.dist(B.B, stt); mid = (dA + dB) / 2; k = 9.0
    # 距離の目もり（流れる）
    for m in range(int(mid - 120), int(mid + 120)):
        if m % 10: continue
        x = W / 2 + (m - mid) * k
        if -50 < x < W + 50:
            d.line((x, 270, x, 650), fill=(230, 210, 200, 90), width=3)
            if m >= 0: d.text((x + 6, 640), f'{m}m', font=Fb(20), fill=(250, 235, 225), anchor='ld')
    for i, (R, dd, ly) in enumerate(((B.A, dA, 440), (B.B, dB, 632))):
        x = W / 2 + (dd - mid) * k + (0 if st >= 0 else 0); slump = min(1.0, R.at(stt, 6) * 1.6)
        sp = R.at(stt, 4) if st >= 0 else 0.0; ph = (dd * 1.7) if st >= 0 else 0.0
        chest = runner(d, x, ly, 175, ph, (60, 110, 200) if i == 0 else (210, 90, 60), slump)
        hearts_row(d, chest[0], chest[1] - 2, R.N, 7 if R.N > 3 else 9, stt, 150 + 10 * min(R.N, 3), per=5)
        lab = name_of(R.N); tw = Fo(28).getlength(lab)
        lx = x - 120 - tw / 2; d.rounded_rectangle((lx - tw / 2 - 14, ly - 120, lx + tw / 2 + 14, ly - 76), 12, fill=(10, 12, 18, 200)); ctext(d, (lx, ly - 98), lab, Fo(28), PALE)
    # 上のバー
    d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 225))
    ctext(d, (W / 2, 36), title, Fo(36), GOLD)
    if st < 0:
        c = '位置について' if st < -1.2 else 'よーい'
        ctext(d, (W / 2, 88), c, Fo(40), PALE)
    else:
        v = f'{stt:4.1f}'; tw = BE(56).getlength(v); d.text((W / 2 - 20, 90), v, font=BE(56), fill=PALE, anchor='rm'); d.text((W / 2 - 12, 96), '秒', font=Fo(30), fill=GREY, anchor='lm')
    # 下のパネル
    d.rectangle((0, 668, W, H), fill=(10, 12, 20, 235))
    for i, R in enumerate((B.A, B.B)):
        x0 = 40 + i * 960; tt = R.at(stt, 2) if st >= 0 else 0.75 / R.N * 1.0
        dmg = R.at(stt, 6) if st >= 0 else 0.0; sat = R.at(stt, 3) if st >= 0 else 98.0; o2 = R.at(stt, 4) if st >= 0 else 0.3 * R.N; pc = R.at(stt, 5) if st >= 0 else 12.0
        d.text((x0, 700), name_of(R.N), font=Fo(30), fill=(150, 190, 255) if i == 0 else (255, 160, 120), anchor='lm')
        d.text((x0 + 880, 700), f'肺を通る時間 {f2(tt)}秒', font=Fb(26), fill=GREY, anchor='rm')
        if tubes: tubes[i].step(max(tt, 0.02), 1 / FPS); tubes[i].draw(d, x0 + 70, 770, 640, 34, max(tt, 0.02), dmg, st, label=True, fs=22, below=True)
        # 数字
        cols = [('取りこむ酸素', f'{o2:.1f}', 'L/分', PALE), ('酸素の満タン度', f'{sat:.0f}', '%', bcol((sat - 20) / 78) if sat < 97 else (255, 120, 120)), ('肺の血管の圧力', f'{pc:.0f}', '', RED if pc > HM.LIM else GREEN)]
        for j, (lab, v, u, c) in enumerate(cols):
            cx = x0 + 140 + j * 300
            d.text((cx, 850), lab, font=Fb(24), fill=GREY, anchor='mm')
            tw = BE(76).getlength(v); uw = Fb(26).getlength(u)
            d.text((cx - (tw + uw + 6) / 2, 920), v, font=BE(76), fill=c, anchor='lm'); d.text((cx - (tw + uw + 6) / 2 + tw + 6, 935), u, font=Fb(26), fill=GREY, anchor='lm')
        # 圧力バー（危険ライン50）
        bx0, bx1, by = x0 + 30, x0 + 870, 1000; vmax = 200.0
        d.rounded_rectangle((bx0, by - 10, bx1, by + 10), 10, fill=(255, 255, 255, 40))
        L = (bx1 - bx0) * min(1.0, pc / vmax); d.rounded_rectangle((bx0, by - 10, bx0 + max(20, L), by + 10), 10, fill=RED if pc > HM.LIM else GREEN)
        lx = bx0 + (bx1 - bx0) * HM.LIM / vmax; d.line((lx, by - 20, lx, by + 20), fill=GOLD, width=4)
        d.text((lx, by + 24), '危険ライン 50（仮定）', font=Fb(18), fill=GOLD, anchor='mt')
        if dmg > 0.01: d.text((bx1, by - 22), '血がにじんでいる！', font=Fo(24), fill=RED, anchor='rb')
    if cap:
        fnt = Fo(50); tw = fnt.getlength(cap)
        d.rounded_rectangle((W / 2 - tw / 2 - 36, 132, W / 2 + tw / 2 + 36, 210), 16, fill=(8, 10, 16, 225)); ctext(d, (W / 2, 171), cap, fnt, capcol)
    d.text((W - 16, H - 6), NOTE + '（進む距離は取りこむ酸素に比例）', font=Fb(17), fill=(220, 220, 225), anchor='rs')
    return im.convert('RGB')
