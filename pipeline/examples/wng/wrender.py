"""翼があったら人間は飛べる？ の描画部品"""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import wmodel as M
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
PALE = (240, 240, 245); GOLD = (255, 210, 80); RED = (255, 95, 95); GREEN = (150, 220, 120); GREY = (200, 200, 208); BLUE = (120, 190, 255); CYAN = (120, 225, 240); ORANGE = (255, 160, 90)
NOTE = '※実データをもとにした、単純化した空想のシミュレーションです'
def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return u * u * (3 - 2 * u)
def mix(a, b, u): u = fade(u); return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
def hms(s):
    s = int(round(s))
    if s >= 3600: return f'{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}'
    return f'{s // 60}:{s % 60:02d}'

# ---- 空の背景 ----
_BG = {}
def sky_bg(w=W, h=H, ground=0.86, dusk=0.0):
    k = (w, h, ground, dusk)
    if k in _BG: return _BG[k]
    top = mix((40, 100, 190), (30, 30, 70), dusk); bot = mix((170, 215, 245), (240, 150, 110), dusk)
    a = np.linspace(0, 1, h)[:, None, None]; c = np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a
    im = Image.fromarray(np.repeat(c, w, 1).astype(np.uint8)).convert('RGBA')
    rng = np.random.default_rng(3); cl = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dc = ImageDraw.Draw(cl)
    for _ in range(14):
        x = rng.uniform(0, w); y = rng.uniform(h * 0.05, h * 0.55); s = rng.uniform(60, 180)
        for j in range(5): dc.ellipse((x + j * s * 0.5 - s, y - s * 0.35 - (j % 2) * s * 0.2, x + j * s * 0.5 + s * 0.4, y + s * 0.3), fill=(255, 255, 255, 120))
    im.alpha_composite(cl.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im); gy = h * ground
    pts = [(0, gy)] + [(x, gy - 60 - 50 * math.sin(x / 210) - 30 * math.sin(x / 77 + 1)) for x in range(0, w + 20, 20)] + [(w, gy)]
    d.polygon(pts, fill=(120, 150, 175))
    d.rectangle((0, gy, w, h), fill=(70, 120, 60))
    _BG[k] = im; return im

# ---- 翼のある人（正面から） ----
def winged(d, x, y, span, t, flap=1.0, col=(240, 236, 225), kind='bird', dim=0.0, suit=(210, 90, 60)):
    """(x,y)：肩の中心。span：翼の幅 px。flap：羽ばたきの強さ 0..1"""
    s = max(span, 60); bodyh = min(90, s * 0.32) if kind == 'bird' else 46
    col = mix(col, (120, 120, 130), dim); skin = mix((228, 182, 148), (140, 140, 150), dim); suit = mix(suit, (100, 100, 110), dim)
    if kind == 'bird':
        ang = math.sin(t * 7.0) * 0.45 * flap
        for side in (1, -1):
            half = s / 2; pts = []
            tipx = x + side * half * math.cos(ang); tipy = y - half * math.sin(ang) * 0.9
            midx = x + side * half * 0.5 * math.cos(ang * 0.6); midy = y - half * 0.5 * math.sin(ang * 0.6) * 0.9
            # 前縁 → 先端 → 羽の後ろ縁
            d.polygon([(x, y - bodyh * 0.05), (midx, midy - s * 0.06), (tipx, tipy), (tipx - side * half * 0.06, tipy + s * 0.09),
                       (midx, midy + s * 0.16), (x, y + bodyh * 0.45)], fill=col)
            for k in range(6):   # 風切り羽
                q = 0.45 + k * 0.1; px = x + side * half * q * math.cos(ang * (0.6 + 0.4 * q)); py = y - half * q * math.sin(ang * (0.6 + 0.4 * q)) * 0.9
                d.line((px, py + s * 0.02, px - side * s * 0.02, py + s * (0.17 - 0.08 * q)), fill=mix(col, (90, 80, 70), 0.45), width=max(1, int(s * 0.008)))
            d.line([(x, y - bodyh * 0.05), (midx, midy - s * 0.06), (tipx, tipy)], fill=mix(col, (140, 120, 90), 0.4), width=max(2, int(s * 0.012)))
    else:   # 人力飛行機：まっすぐ長い翼、下に人とプロペラ
        bend = s * 0.03
        d.line([(x - s / 2, y - bend), (x, y), (x + s / 2, y - bend)], fill=col, width=max(6, int(s * 0.018)), joint='curve')
        for k in range(-6, 7): d.line((x + k * s / 13, y - abs(k) / 6 * bend - 4, x + k * s / 13, y - abs(k) / 6 * bend + 4), fill=mix(col, (80, 80, 90), 0.5), width=2)
        d.line((x, y, x, y + 40), fill=(90, 90, 100), width=4)
        pr = 34; a = t * 30
        d.ellipse((x - pr, y + 40 - pr * 0.25, x + pr, y + 40 + pr * 0.25), outline=(220, 220, 230, 150), width=2)
        d.line((x - math.cos(a) * pr, y + 40, x + math.cos(a) * pr, y + 40), fill=(60, 60, 70), width=4)
        y = y + 40
    hr = max(9, bodyh * 0.22) if kind == 'bird' else 12
    d.rounded_rectangle((x - hr * 0.9, y - hr * 0.2, x + hr * 0.9, y + bodyh * 0.75), int(hr * 0.6), fill=suit)
    for side in (1, -1): d.line((x + side * hr * 0.4, y + bodyh * 0.7, x + side * hr * 0.5, y + bodyh * 1.15), fill=skin, width=max(3, int(hr * 0.55)))
    d.ellipse((x - hr, y - hr * 2.1, x + hr, y - hr * 0.1), fill=skin); d.chord((x - hr * 1.02, y - hr * 2.15, x + hr * 1.02, y - hr * 0.9), 180, 360, fill=(45, 32, 26))
    d.line((x - hr * 0.45, y - hr * 1.05, x - hr * 0.2, y - hr * 1.05), fill=(30, 30, 30), width=2); d.line((x + hr * 0.2, y - hr * 1.05, x + hr * 0.45, y - hr * 1.05), fill=(30, 30, 30), width=2)

def bar(d, x0, y, x1, frac, col, h=26, back=(255, 255, 255, 40)):
    d.rounded_rectangle((x0, y - h / 2, x1, y + h / 2), int(h / 2), fill=back)
    if frac > 0.005: d.rounded_rectangle((x0, y - h / 2, x0 + max(h, (x1 - x0) * fade(frac)), y + h / 2), int(h / 2), fill=col)

# ---- 対決 ----
GY = 620; TOPY = 190; X0 = 250; X1 = 1820
class Battle:
    def __init__(self, specs, names, maxdist, spans_px, kinds=('bird', 'bird'), goal=None):
        """specs：[(b, ar, cp), ...]"""
        self.F = [M.Flight(b, ar, cp) for b, ar, cp in specs]; self.names = names; self.maxdist = maxdist; self.spans = spans_px; self.kinds = kinds; self.goal = goal
        self.ends = [f.end for f in self.F]; self.specs = specs
    def endall(self):
        e = [x for x in self.ends if x is not None]
        if self.goal: e.append(self.goal / self.F[1].v)
        return max(e)
def hy(h): return GY - (GY - TOPY) * h / 35.0
def state(F, st, goal=None):
    tt = st
    if goal is not None: tt = min(st, goal / F.v)
    if F.end is not None: tt = min(tt, F.end)
    return F.at(tt, 1), F.at(tt, 2), F.at(tt, 3), F.at(tt, 4), (F.end is not None and st >= F.end), (goal is not None and F.at(tt, 2) >= goal - 1)
COLS = [(255, 170, 120), (150, 200, 255)]; SUITS = [(210, 90, 60), (60, 110, 200)]
def battle_frame(Bt, st, title, cap=None, capcol=PALE, vt=0.0):
    im = sky_bg(W, H, GY / H).convert('RGB'); d = ImageDraw.Draw(im, 'RGBA'); stt = max(0.0, st)
    # 丘（高さ30m）
    d.polygon([(0, hy(30) - 4), (X0 - 40, hy(30) - 4), (X0 + 30, GY), (0, GY)], fill=(90, 135, 70)); d.line((0, hy(30) - 4, X0 - 40, hy(30) - 4), fill=(60, 100, 50), width=6)
    for h in (10, 20, 30):
        d.line((X0, hy(h), X1, hy(h)), fill=(255, 255, 255, 50), width=2); d.text((X1 + 8, hy(h)), f'{h}m', font=Fb(24), fill=(255, 255, 255), anchor='lm')
    if Bt.goal:
        gx = X0 + (X1 - X0) * Bt.goal / Bt.maxdist; d.line((gx, TOPY - 20, gx, GY), fill=GOLD, width=5); ctext(d, (gx - 10, TOPY - 40), f'ゴール {Bt.goal / 1000:.1f}km', Fo(30), GOLD, 'rm', 3)
    for k in range(5):
        dist = Bt.maxdist * k / 4; xx = X0 + (X1 - X0) * k / 4; d.line((xx, GY, xx, GY + 12), fill=PALE, width=3)
        lab = f'{dist / 1000:.0f}km' if Bt.maxdist >= 5000 else f'{dist:.0f}m'; d.text((xx, GY + 16), lab, font=Fb(22), fill=PALE, anchor='mt')
    for i, F in enumerate(Bt.F):
        h, x, p, w, landed, goal = state(F, stt, Bt.goal)
        # 軌跡
        n = int(min(stt, F.a[-1, 0]) / F.dt); idx = np.linspace(0, max(1, n), 60).astype(int); idx = idx[idx < len(F.a)]
        pts = [(X0 + (X1 - X0) * F.a[j, 2] / Bt.maxdist, hy(F.a[j, 1])) for j in idx]
        if Bt.goal: pts = [(min(px, X0 + (X1 - X0) * Bt.goal / Bt.maxdist), py) for px, py in pts]
        if len(pts) > 1: d.line(pts, fill=COLS[i] + (200,), width=5)
        px = X0 + (X1 - X0) * x / Bt.maxdist; py = hy(h)
        flap = 0.0 if (landed or goal) else (0.3 + 0.7 * min(1, p / 800)) if Bt.kinds[i] == 'bird' else 0
        winged(d, px, py - (14 if landed else 0) - 40, Bt.spans[i], vt + i * 0.37, flap, kind=Bt.kinds[i], dim=0.5 if landed else 0, suit=SUITS[i])
        tag = Bt.names[i].split('（')[0].replace('の翼の人', '')
        if not landed and not goal:
            tw = Fb(26).getlength(tag)
            if i == 1: lx = px + Bt.spans[i] / 2 + tw / 2 + 16; ly = py - 40
            else: lx = px; ly = py + (60 if Bt.kinds[i] == 'bird' else 110)
            d.rounded_rectangle((lx - tw / 2 - 10, ly - 18, lx + tw / 2 + 10, ly + 18), 10, fill=(10, 12, 18, 190)); ctext(d, (lx, ly), tag, Fb(26), COLS[i])
        if landed: ctext(d, (px, py - 130), '着地', Fo(36), RED, sw=3)
        if goal: ctext(d, (px - 60, py - 140), 'ゴール！', Fo(40), GOLD, sw=3)
    d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 225))
    ctext(d, (W / 2, 36), title, Fo(36), GOLD)
    if st < 0: ctext(d, (W / 2, 90), '飛び立つ準備…（高さ30mの丘）', Fo(34), PALE)
    else:
        v = hms(stt); d.text((W / 2 + 20, 92), v, font=BE(60), fill=PALE, anchor='rm'); d.text((W / 2 + 32, 96), '経過（早送り）', font=Fb(26), fill=GREY, anchor='lm')
    d.rectangle((0, 668, W, H), fill=(10, 12, 20, 240))
    for i, F in enumerate(Bt.F):
        h, x, p, w, landed, goal = state(F, stt, Bt.goal); x0 = 40 + i * 960
        d.text((x0, 705), Bt.names[i], font=Fo(34), fill=COLS[i], anchor='lm')
        b, ar, cp = Bt.specs[i]; d.text((x0 + 880, 705), f'翼の幅 {b:g}m・必要なパワー 約{F.preq:,.0f}W', font=Fb(26), fill=GREY, anchor='rm')
        d.text((x0, 770), '高さ', font=Fb(26), fill=GREY, anchor='lm'); hv = f'{h:.1f}'
        hc = GREEN if h >= 29.5 else (GOLD if h > 10 else RED)
        d.text((x0, 830), hv, font=BE(84), fill=hc, anchor='lm'); d.text((x0 + BE(84).getlength(hv) + 6, 842), 'm', font=Fo(34), fill=hc, anchor='lm')
        d.text((x0 + 300, 770), '飛んだ距離', font=Fb(26), fill=GREY, anchor='lm'); dv = f'{x / 1000:.1f}' if x >= 1000 else f'{x:.0f}'
        d.text((x0 + 300, 830), dv, font=BE(84), fill=PALE, anchor='lm'); d.text((x0 + 300 + BE(84).getlength(dv) + 6, 842), 'km' if x >= 1000 else 'm', font=Fo(34), fill=PALE, anchor='lm')
        if landed: d.rounded_rectangle((x0 + 620, 790, x0 + 880, 850), 12, fill=(160, 30, 40)); ctext(d, (x0 + 750, 820), f'着地 {hms(F.end)}', Fo(30), PALE)
        if goal: d.rounded_rectangle((x0 + 620, 790, x0 + 880, 850), 12, fill=(150, 110, 20)); ctext(d, (x0 + 750, 820), f'ゴール {hms(Bt.goal / F.v)}', Fo(30), PALE)
        pw = 0 if (landed or goal) else p
        d.text((x0, 905), '出しているパワー', font=Fb(26), fill=GREY, anchor='lm'); d.text((x0 + 880, 905), f'{pw:,.0f} / 必要 {F.preq:,.0f} W', font=Fo(30), fill=GREEN if pw >= F.preq - 1 else RED, anchor='rm')
        scale = max(800, F.preq * 1.05); bar(d, x0, 950, x0 + 880, pw / scale, GREEN if pw >= F.preq - 1 else ORANGE, 26)
        nx = x0 + 880 * F.preq / scale; d.line((nx, 930, nx, 970), fill=GOLD, width=4)
        d.text((x0, 1010), '体力（がんばれる量）', font=Fb(26), fill=GREY, anchor='lm')
        wc = GREEN if w > 0.5 else (GOLD if w > 0.2 else RED); bar(d, x0 + 300, 1010, x0 + 760, w, wc, 26); d.text((x0 + 880, 1010), f'{w * 100:.0f}%', font=BE(56), fill=wc, anchor='rm')
    if cap:
        fnt = Fo(50); tw = fnt.getlength(cap)
        d.rounded_rectangle((W / 2 - tw / 2 - 36, 132, W / 2 + tw / 2 + 36, 210), 16, fill=(8, 10, 16, 225)); ctext(d, (W / 2, 171), cap, fnt, capcol)
    d.text((W - 16, H - 6), NOTE, font=Fb(17), fill=(220, 220, 225), anchor='rs')
    return im
