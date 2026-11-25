"""エラがあったら水中で暮らせる？ の描画部品"""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import emodel as EM
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
PALE = (240, 240, 245); GOLD = (255, 210, 80); RED = (255, 95, 95); GREEN = (150, 220, 120); GREY = (200, 200, 208); BLUE = (120, 190, 255); CYAN = (120, 225, 240)
NOTE = '※実データをもとにした、単純化した空想のシミュレーションです'
def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return u * u * (3 - 2 * u)
def mix(a, b, u): u = fade(u); return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
def mmss(m): s = int(round(m * 60)); return f'{s // 60}:{s % 60:02d}'
def tcol(T):
    """体温の色：37 白緑 → 32 黄 → 28 青"""
    if T >= 36: return GREEN
    if T >= 32: return mix(GOLD, GREEN, (T - 32) / 4)
    return mix(BLUE, GOLD, (T - 28) / 4)

# ---- 水の中の背景 ----
_BG = {}
def water_bg(kind='lake', w=W, h=H):
    k = (kind, w, h)
    if k in _BG: return _BG[k]
    if kind == 'pool': top, bot = (90, 200, 230), (20, 110, 160)
    elif kind == 'cold': top, bot = (40, 90, 120), (6, 20, 36)
    else: top, bot = (50, 120, 130), (8, 34, 44)
    a = np.linspace(0, 1, h)[:, None, None]; c = np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a
    im = Image.fromarray(np.repeat(c, w, 1).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
    rng = np.random.default_rng(5)
    if kind == 'pool':
        for x in range(-40, w + 40, 90): d.line((x, h * 0.62, x + (x - w / 2) * 0.6, h), fill=(255, 255, 255, 40), width=3)
        for yy in np.linspace(h * 0.62, h, 7): d.line((0, yy, w, yy), fill=(255, 255, 255, 30), width=2)
        d.rectangle((0, h * 0.42, w, h * 0.44), fill=(20, 40, 120, 90))
    else:
        for k2 in range(40):
            x = rng.uniform(0, w); hh = rng.uniform(h * 0.08, h * 0.3); ph = rng.uniform(0, 6)
            pts = [(x + math.sin(ph + j * 0.5) * 14, h - j * hh / 10) for j in range(11)]
            d.line(pts, fill=(30, 80, 50, 160), width=int(rng.uniform(5, 12)), joint='curve')
        d.rectangle((0, h - 30, w, h), fill=(30, 40, 30, 200))
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for k2 in range(7):
        x = rng.uniform(0, w); ww = rng.uniform(40, 140)
        dl.polygon([(x, 0), (x + ww, 0), (x + ww * 2 + 260, h), (x + 260, h)], fill=(255, 255, 255, 22))
    lay = lay.filter(ImageFilter.GaussianBlur(18)); im.alpha_composite(lay); _BG[k] = im; return im
def bubbles(d, t, x0, x1, y0, y1, n=30, seed=1, r=(3, 8)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = rng.uniform(x0, x1); sp = rng.uniform(40, 90); ph = rng.uniform(0, 1); rr = rng.uniform(*r)
        y = y1 - ((t * sp / (y1 - y0) + ph) % 1.0) * (y1 - y0); x += math.sin(t * 2 + k) * 6
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(230, 250, 255, 170), width=2)

# ---- 泳ぐ人（横向き、頭が右）----
def swimmer(d, x, y, L, t, kind='gill', cold=0.0, gsize=1.0, suit=(210, 90, 60), flow=0.0, dim=0.0):
    """(x,y)：胴体の中心。L：身長 px。cold 0..1 で肌が青白く。gsize：エラの大きさ。flow：水の流れの強さ"""
    skin = mix((228, 182, 148), (170, 190, 215), cold); skin = mix(skin, (120, 125, 135), dim); suit = mix(suit, (110, 110, 120), dim)
    lw = max(4, int(L * 0.075)); bob = math.sin(t * 1.6) * L * 0.015; y = y + bob
    hip = (x - L * 0.12, y); sh = (x + L * 0.2, y - L * 0.02)
    for side in (1, -1):    # 脚（ゆっくりバタ足）
        a = math.sin(t * 4 + (0 if side > 0 else math.pi)) * 0.18 * (1 - dim)
        kx = hip[0] - L * 0.24; ky = hip[1] + math.sin(a) * L * 0.2
        fx = kx - L * 0.22; fy = ky + math.sin(a * 1.6) * L * 0.25
        d.line((hip, (kx, ky), (fx, fy)), fill=skin if side > 0 else mix(skin, (0, 0, 0), 0.15), width=lw, joint='curve')
    d.line((hip, sh), fill=suit, width=int(lw * 2.3))
    for side in (1, -1):    # 腕
        a = math.sin(t * 1.5 + (0 if side > 0 else 1.5)) * 0.35 * (1 - dim)
        ex = sh[0] + L * 0.16; ey = sh[1] + L * 0.06 + math.sin(a) * L * 0.08
        hx = ex + L * 0.14; hy = ey + math.sin(a) * L * 0.1
        d.line((sh, (ex, ey), (hx, hy)), fill=skin if side > 0 else mix(skin, (0, 0, 0), 0.15), width=max(3, int(lw * 0.8)), joint='curve')
    hr = L * 0.085; hc = (sh[0] + L * 0.14, sh[1] - L * 0.03)
    if kind == 'hold':
        d.ellipse((hc[0] - hr * 1.05, hc[1] - hr, hc[0] + hr * 1.15, hc[1] + hr * 1.05), fill=skin)
        d.ellipse((hc[0] + hr * 0.25, hc[1] + hr * 0.1, hc[0] + hr * 0.95, hc[1] + hr * 0.75), fill=mix(skin, (240, 120, 120), 0.35))   # ふくらんだほお
    else:
        d.ellipse((hc[0] - hr, hc[1] - hr, hc[0] + hr, hc[1] + hr), fill=skin)
    d.chord((hc[0] - hr * 1.05, hc[1] - hr * 1.1, hc[0] + hr * 1.05, hc[1] + hr * 0.5), 180, 330, fill=(45, 32, 26))
    d.line((hc[0] + hr * 0.35, hc[1] - hr * 0.15, hc[0] + hr * 0.65, hc[1] - hr * 0.15), fill=(30, 30, 30), width=max(2, int(hr * 0.12)))   # 目（とじ気味）
    nk = (hc[0] - hr * 0.55, hc[1] + hr * 0.75)
    if kind == 'gill':   # 首の後ろのエラ（ウーパールーパーのような外エラ）
        n = 3; gl = hr * (1.3 + 1.5 * gsize)
        for i in range(n):
            a = math.radians(-150 + i * 32) + math.sin(t * 3 + i) * 0.08
            p0 = (nk[0], nk[1] - hr * 0.2 + i * hr * 0.25)
            p1 = (p0[0] + math.cos(a) * gl, p0[1] + math.sin(a) * gl * 0.75)
            d.line((p0, p1), fill=mix((230, 70, 90), (150, 150, 200), cold * 0.6), width=max(3, int(hr * 0.22)))
            for j in range(1, 6):
                q = j / 6; px = p0[0] + (p1[0] - p0[0]) * q; py = p0[1] + (p1[1] - p0[1]) * q; fl = hr * 0.35 * (0.6 + gsize * 0.6)
                for s in (1, -1):
                    d.line((px, py, px + math.cos(a + s * 1.2) * fl, py + math.sin(a + s * 1.2) * fl), fill=mix((255, 120, 140), (170, 170, 220), cold * 0.6), width=max(2, int(hr * 0.1)))
        if flow > 0:   # エラを通る水
            for k in range(int(4 + 8 * flow)):
                u = (t * (0.6 + flow) + k / (4 + 8 * flow)) % 1.0; px = nk[0] + hr * 2.4 - u * hr * 4.5; py = nk[1] - hr * 0.6 + math.sin(k * 2.3) * hr * 0.8
                d.line((px, py, px + hr * 0.5, py), fill=(200, 240, 255, int(200 * (1 - abs(u - 0.5) * 2))), width=3)
    else:
        if dim < 0.5 and (t * 0.7) % 1.0 < 0.25:
            d.ellipse((hc[0] + hr * 0.9, hc[1] - hr * 1.0 - (t * 0.7 % 1.0) * hr * 4, hc[0] + hr * 1.2, hc[1] - hr * 0.7 - (t * 0.7 % 1.0) * hr * 4), outline=(230, 250, 255, 200), width=2)
    return hc

def trout(d, cx, cy, s, t, gill_glow=1.0):
    col = (150, 160, 120); back = (90, 110, 80); wig = math.sin(t * 4) * 0.08
    body = [(cx + s * 0.55, cy), (cx + s * 0.35, cy - s * 0.17), (cx, cy - s * 0.22), (cx - s * 0.4, cy - s * 0.12), (cx - s * 0.6, cy - s * 0.02 + wig * s),
            (cx - s * 0.4, cy + s * 0.12), (cx, cy + s * 0.2), (cx + s * 0.35, cy + s * 0.15)]
    d.polygon(body, fill=col, outline=back)
    d.polygon([(cx - s * 0.58, cy + wig * s), (cx - s * 0.85, cy - s * 0.2 + wig * s * 2), (cx - s * 0.78, cy + wig * s), (cx - s * 0.85, cy + s * 0.2 + wig * s * 2)], fill=back)
    d.polygon([(cx - s * 0.05, cy - s * 0.21), (cx - s * 0.2, cy - s * 0.32), (cx - s * 0.25, cy - s * 0.17)], fill=back)
    d.line([(cx - s * 0.45, cy), (cx + s * 0.25, cy - s * 0.02)], fill=(220, 120, 140), width=max(3, int(s * 0.03)))   # 赤い帯（ニジマス）
    for k in range(25):
        rng = (k * 37 % 100) / 100; d.ellipse((cx - s * 0.4 + rng * s * 0.7 - 3, cy - s * 0.15 + (k * 53 % 100) / 100 * s * 0.12 - 3, cx - s * 0.4 + rng * s * 0.7 + 3, cy - s * 0.15 + (k * 53 % 100) / 100 * s * 0.12 + 3), fill=(60, 60, 50))
    d.ellipse((cx + s * 0.36, cy - s * 0.07, cx + s * 0.42, cy - s * 0.01), fill=(250, 245, 220)); d.ellipse((cx + s * 0.38, cy - s * 0.055, cx + s * 0.41, cy - s * 0.025), fill=(10, 10, 10))
    d.arc((cx + s * 0.12, cy - s * 0.16, cx + s * 0.32, cy + s * 0.14), 110, 250, fill=mix((120, 60, 60), (255, 60, 80), gill_glow), width=max(4, int(s * 0.03)))

# ---- 対決 ----
class Battle:
    def __init__(self, qa, qb, tw, gsize=1.0, T=12.0):
        self.A = EM.Sim(qa, tw, T); self.B = EM.Sim(qb, tw, T); self.tw = tw; self.gsize = gsize
        self.endA = self.A.end(); self.endB = self.B.end()
def bar(d, x0, y, x1, frac, col, h=26, back=(255, 255, 255, 40)):
    d.rounded_rectangle((x0, y - h / 2, x1, y + h / 2), int(h / 2), fill=back)
    if frac > 0.005: d.rounded_rectangle((x0, y - h / 2, x0 + max(h, (x1 - x0) * fade(frac)), y + h / 2), int(h / 2), fill=col)
def person_state(Bt, R, end, st):
    """st：シミュレーション分。返り値 (酸素の割合, 体温, 取りこみ, 限界からの分 or None)"""
    s = min(st, end) if end is not None else st
    o = R.at(s, 1) / EM.STORE; T = R.at(s, 2); up = R.at(s, 3)
    gone = (st - end) if (end is not None and st >= end) else None
    return o, T, up, gone
NAMES = ('息を止めた人', 'エラの人')
def battle_frame(Bt, st, title, cap=None, capcol=PALE, vt=0.0, rate=0.3, gname='エラの人'):
    kind = 'pool' if Bt.tw >= 30 else 'lake'
    im = water_bg(kind).convert('RGB'); d = ImageDraw.Draw(im, 'RGBA'); stt = max(0.0, st)
    bubbles(d, vt, 0, W, 130, 660, 26, 3)
    for i, (R, end, ly) in enumerate(((Bt.A, Bt.endA, 330), (Bt.B, Bt.endB, 540))):
        o, T, up, gone = person_state(Bt, R, end, stt)
        cold = fade((37 - T) / 9); rise = 0.0 if gone is None else ease(gone / (rate * 1.6)) * 520
        x = W / 2 - 80; y = ly - rise
        hc = swimmer(d, x, y, 440, vt, 'hold' if i == 0 else 'gill', cold, Bt.gsize, (60, 110, 200) if i == 0 else (210, 90, 60), flow=(0 if i == 0 else (0.4 + 0.6 * min(1, (R.qw or 0) / 60))) * (1 if gone is None else 0), dim=0 if gone is None else 0.6)
        lab = NAMES[0] if i == 0 else gname; tw = Fo(30).getlength(lab)
        lx = x - 420
        if rise < 80: d.rounded_rectangle((lx - tw / 2 - 14, y - 26, lx + tw / 2 + 14, y + 22), 12, fill=(10, 12, 18, 200)); ctext(d, (lx, y - 3), lab, Fo(30), PALE)
        if gone is not None and rise > 30:
            ctext(d, (x + 60, y + 40), '限界 → 水から上がる', Fo(32), RED, sw=3)
    d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 225))
    ctext(d, (W / 2, 36), title, Fo(36), GOLD)
    d.text((60, 92), f'水温 {Bt.tw}℃', font=Fo(32), fill=CYAN, anchor='lm')
    if st < 0: ctext(d, (W / 2, 90), 'もぐる準備…', Fo(36), PALE)
    else:
        v = mmss(stt); d.text((W / 2 + 20, 92), v, font=BE(60), fill=PALE, anchor='rm'); d.text((W / 2 + 32, 96), '経過（早送り）', font=Fb(26), fill=GREY, anchor='lm')
    d.rectangle((0, 668, W, H), fill=(10, 12, 20, 235))
    for i, (R, end) in enumerate(((Bt.A, Bt.endA), (Bt.B, Bt.endB))):
        o, T, up, gone = person_state(Bt, R, end, stt); x0 = 40 + i * 960
        d.text((x0, 700), NAMES[0] if i == 0 else gname, font=Fo(32), fill=(150, 190, 255) if i == 0 else (255, 160, 120), anchor='lm')
        if R.qw is None: sub = 'エラなし・息つぎなし'
        else: sub = f'エラを通る水 毎分{R.qw:.0f}L'
        d.text((x0 + 880, 700), sub, font=Fb(26), fill=GREY, anchor='rm')
        d.text((x0, 770), '体にためた酸素の残り', font=Fb(26), fill=GREY, anchor='lm')
        oc = GREEN if o > 0.5 else (GOLD if o > 0.2 else RED)
        bar(d, x0, 815, x0 + 700, o, oc, 34); d.text((x0 + 880, 815), f'{o * 100:.0f}%', font=BE(64), fill=oc, anchor='rm')
        d.text((x0, 880), '取りこむ酸素', font=Fb(26), fill=GREY, anchor='lm')
        upv = f'{up:.0f}' if R.qw is not None else '0'
        d.text((x0, 940), upv, font=BE(72), fill=PALE if up < 249 else GREEN, anchor='lm'); d.text((x0 + BE(72).getlength(upv) + 8, 952), '/ 必要250 mL/分', font=Fb(24), fill=GREY, anchor='lm')
        d.text((x0 + 560, 880), '体温', font=Fb(26), fill=GREY, anchor='lm')
        tv = f'{T:.1f}'; d.text((x0 + 560, 940), tv, font=BE(80), fill=tcol(T), anchor='lm'); d.text((x0 + 560 + BE(80).getlength(tv) + 6, 950), '℃', font=Fo(34), fill=tcol(T), anchor='lm')
        bar(d, x0, 1015, x0 + 880, (T - 26) / 11, tcol(T), 18)
        for th, lb in ((35, '35'), (32, '32'), (28, '28 限界')):
            lx = x0 + 880 * (th - 26) / 11; d.line((lx, 1000, lx, 1030), fill=GOLD, width=3); d.text((lx, 1034), lb, font=Fb(18), fill=GOLD, anchor='mt')
        if gone is not None:
            d.rounded_rectangle((x0 + 330, 752, x0 + 590, 790), 10, fill=(160, 30, 40)); ctext(d, (x0 + 460, 770), f'限界 {mmss(end)}', Fo(28), PALE)
    if cap:
        fnt = Fo(50); tw = fnt.getlength(cap)
        d.rounded_rectangle((W / 2 - tw / 2 - 36, 132, W / 2 + tw / 2 + 36, 210), 16, fill=(8, 10, 16, 225)); ctext(d, (W / 2, 171), cap, fnt, capcol)
    d.text((W - 16, H - 6), NOTE, font=Fb(17), fill=(220, 220, 225), anchor='rs')
    return im
