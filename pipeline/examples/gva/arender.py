"""巨人vs人間の綱引きの描画（gvm の背景と巨人を使う）"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/gvm'); sys.path.insert(0, '/home/claude/gva')
import grender as GR
import amodel as AM
GR.SPR = Image.open('/home/claude/gva/spr_clean.png').convert('RGBA')
Fo, Fb, Mi, BE = GR.Fo, GR.Fb, GR.Mi, GR.BE
PALE, GOLD, GIANT_C = GR.PALE, GR.GOLD, GR.GIANT_C
HUM_C = (150, 220, 120)
WAIST = 27.0

def scr(x, z, k, cam): return GR.scr(x, z, k, cam)

# ---------- 巨人（回転つき） ----------
_rot = {}
def giant_layer(ppm, ang):
    """足元を中心に ang 度（反時計回り＝左に倒れる）回した巨人。戻り値：画像、足元の画像内座標"""
    key = (round(ppm, 2), round(ang * 4) / 4)
    if key in _rot: return _rot[key]
    sp = GR.giant_sprite(GR.SPR_HM * ppm, 0)
    R = int(GR.GIANT_H * ppm) + 4; cw = 2 * R; ch = R + 4
    can = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    can.alpha_composite(sp, (int(R - sp.width / 2), int(ch - 4 - GR.SPR_BASE * ppm - sp.height)))
    if abs(key[1]) > 0.01: can = can.rotate(key[1], resample=Image.BICUBIC, center=(R, ch - 4))
    if len(_rot) > 24: _rot.clear()
    _rot[key] = (can, (R, ch - 4)); return _rot[key]
def body_point(xg, ang, z):
    """体の高さ z の点が、ang 度傾いたときの (x, z)"""
    a = math.radians(ang); return xg - z * math.sin(a), z * math.cos(a)

# ---------- 人 ----------
UNI = [(92, 104, 62), (80, 92, 56), (104, 112, 70), (86, 96, 60), (70, 82, 52), (98, 100, 66)]
_st = {}
def person(hp, lean, ci, pose):
    """hp：身長のピクセル。lean：後ろ（左）へのかたむき（度）。pose：pull / fall / run"""
    hp = max(4, int(hp)); lean = int(round(lean / 5) * 5); key = (hp, lean, ci, pose)
    if key in _st: return _st[key]
    s = 3; L = hp * s; cw = int(L * 1.6); ch = int(L * 1.3)
    im = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fx, fy = cw * 0.55, ch - 2                                     # 足元
    col = UNI[ci] + (255,); skin = (205, 160, 125, 255); dark = (40, 44, 30, 255); helm = (62, 72, 44, 255)
    if pose == 'fall':
        y = fy - L * 0.09
        d.rounded_rectangle((fx - L * 0.55, y - L * 0.09, fx + L * 0.25, y + L * 0.05), radius=L * 0.05, fill=col)
        d.ellipse((fx + L * 0.2, y - L * 0.12, fx + L * 0.36, y + L * 0.03), fill=skin); d.ellipse((fx + L * 0.2, y - L * 0.14, fx + L * 0.37, y - L * 0.04), fill=helm)
        d.line((fx - L * 0.55, y, fx - L * 0.95, y + L * 0.03), fill=dark, width=max(2, int(L * 0.08)))
    else:
        a = math.radians(lean)
        hipx, hipy = fx - L * 0.47 * math.sin(a) * 0.6, fy - L * 0.47 * math.cos(a * 0.6)
        if pose == 'run':
            d.line((hipx, hipy, fx - L * 0.2, fy), fill=dark, width=max(2, int(L * 0.09))); d.line((hipx, hipy, fx + L * 0.18, fy - L * 0.08), fill=dark, width=max(2, int(L * 0.09)))
        else:
            d.line((hipx, hipy, fx + L * 0.12, fy), fill=dark, width=max(2, int(L * 0.09))); d.line((hipx, hipy, fx - L * 0.06, fy), fill=dark, width=max(2, int(L * 0.09)))
        shx, shy = hipx - L * 0.36 * math.sin(a), hipy - L * 0.36 * math.cos(a)
        d.line((hipx, hipy, shx, shy), fill=col, width=max(3, int(L * 0.17)))
        hx, hy = shx - L * 0.1 * math.sin(a), shy - L * 0.1 * math.cos(a)
        d.ellipse((hx - L * 0.075, hy - L * 0.09, hx + L * 0.075, hy + L * 0.06), fill=skin)
        d.chord((hx - L * 0.09, hy - L * 0.12, hx + L * 0.09, hy + L * 0.06), 180, 360, fill=helm)
        if pose == 'run': d.line((shx, shy + L * 0.03, shx - L * 0.2, shy + L * 0.12), fill=col, width=max(2, int(L * 0.07)))
        else: d.line((shx, shy + L * 0.03, shx + L * 0.28, hipy - L * 0.05), fill=col, width=max(2, int(L * 0.07)))
    im = im.resize((cw // s, ch // s), Image.LANCZOS)
    if len(_st) > 3000: _st.clear()
    _st[key] = (im, (fx / s, fy / s)); return _st[key]

def crowd_layout(n):
    rows = max(1, math.ceil(n / 170)); per = math.ceil(n / rows); sp = 0.75 if n <= 200 else 0.55
    rng = np.random.default_rng(n)
    P = []
    for r in range(rows):
        k = 1.17 + 0.3 * (r / max(1, rows - 1)) if rows > 1 else 1.22
        m = min(per, n - r * per)
        for j in range(m):
            P.append((r, k, -16 - j * sp + rng.normal(0, 0.08), int(rng.integers(6)), rng.uniform(-6, 6), rng.uniform(0, 6.28)))
    return P, rows
_lay = {}

def render(M, t, cam, hud, f=0, giant_ang=None, end_state=None):
    """t：シミュレーションの時刻（<0 はスタート前）"""
    n = M.n
    if n not in _lay: _lay[n] = crowd_layout(n)
    P, rows = _lay[n]
    cx, cz, ppm = cam
    tt = max(0.0, t); p = M.pos(tt) if t > 0 else 0.0
    W, H = GR.W, GR.H
    im = GR.sky().convert('RGBA'); d = ImageDraw.Draw(im)
    km = 0.22; xs = np.linspace(cx - W / 2 / (ppm * km), cx + W / 2 / (ppm * km), 200)
    pts = [scr(x, GR.mountains(x) * 0.25, km, cam) for x in xs]; _, Ym = scr(0, 0, km, cam)
    d.polygon(pts + [(W, Ym), (0, Ym)], fill=(132, 156, 178, 255))
    if Ym < H: d.rectangle((0, max(0, Ym), W, H), fill=(92, 120, 80, 255))
    GR.paste_strip(im, GR.FOREST_B, 0.82, cam)
    _, Yb = scr(0, 0, 0.82, cam)
    if Yb < H: d.rectangle((0, max(0, Yb), W, H), fill=(34, 60, 32, 255))
    # 巨人：力の差で、後ろにかたむく
    xg = -p
    if giant_ang is None:
        if t <= 0: giant_ang = -1.0
        else:
            fg, fh = M.fg(tt), M.fh(tt); giant_ang = -(3.0 + 4.0 * min(1.5, fg / AM.FG))
            if M.win == 'human' and tt > M.t_end: giant_ang = topple_angle(tt - M.t_end, giant_ang)
    lay, (px_, py_) = giant_layer(ppm, giant_ang)
    X, Y = scr(xg, 0, 1.0, cam)
    if lay.width < 9000: im.alpha_composite(lay, (int(X - px_), int(Y - py_)))
    wx, wz = body_point(xg, giant_ang, WAIST); WX, WY = scr(wx, wz, 1.0, cam)
    GR.paste_strip(im, FOREST_FA, 1.1, cam)
    _, Yf = scr(0, 0, 1.1, cam); d = ImageDraw.Draw(im)
    if Yf < H: d.rectangle((0, max(0, Yf), W, H), fill=(30, 52, 28, 255))
    # 手前の原っぱ
    _, Yv = scr(0, 0, 1.17, cam)
    if Yv < H: d.rectangle((0, max(0, Yv - 3 * ppm), W, H), fill=(84, 118, 62, 255))
    for hx, hw, hh, rc in GR.HOUSES:
        if hx < 0: continue
        X0, Y0 = scr(hx - hw / 2 + 10, 0, 1.2, cam); X1, Y1 = scr(hx + hw / 2 + 10, hh, 1.2, cam)
        if X1 < -50 or X0 > W + 50: continue
        Yr = Y1 - (X1 - X0) * 0.35
        d.rectangle((X0, Y1, X1, Y0), fill=(226, 220, 205, 255)); d.polygon([(X0 - 0.3 * ppm, Y1), (X1 + 0.3 * ppm, Y1), ((X0 + X1) / 2, Yr)], fill=rc + (255,))
    # 人と綱
    after = tt - M.t_end if (M.win and t > 0 and tt > M.t_end) else -1
    heave = 0.5 + 0.5 * math.sin(2 * math.pi * tt / 2.0) if t > 0 else 0.0
    front = {}
    order = sorted(range(len(P)), key=lambda i: P[i][1])
    stamps = []
    for i in order:
        r, k, x0, ci, lj, ph = P[i]
        x = x0 - p; pose = 'pull'; lean = (8 if t <= 0 else 24 + 8 * heave) + lj
        if M.win == 'giant' and after >= 0:
            pose = 'fall' if (after * 9 > (-x0 - 16) * 0.3 + (ph * 0.3)) else 'pull'; lean = 5
        if M.win == 'human' and after > 0.8:
            run = (after - 0.8) * (4 + ph * 0.3); x -= run * 1.0; pose = 'run'; lean = -12
        elif t > 0 and M.win != 'giant' and p < -0.2:
            lean -= 6
        if t > 0 and M.win != 'giant' and M.at(tt, M.P) - M.at(max(0, tt - 0.5), M.P) < -0.25: lean -= 10
        X_, Y_ = scr(x, 0, k, cam); hp = 1.75 * ppm * k
        if X_ < -60 or X_ > W + 60: continue
        if r not in front or x > front[r][0]: front[r] = (x, k)
        stamps.append((k, X_, Y_, hp, lean, ci, pose))
    rope_ok = not (M.win == 'human' and after > 0.8) and not (M.win == 'giant' and after > 1.5)
    if rope_ok:
        for r, (x, k) in front.items():
            hx, hy = scr(x + 0.3, 1.05, k, cam); tail = scr(x - 120, 1.05, k, cam)
            mx, my = (hx + WX) / 2, (hy + WY) / 2 + abs(hx - WX) * 0.02
            d.line([(WX, WY), (mx, my), (hx, hy)], fill=(196, 170, 120, 255), width=max(2, int(ppm * k * 0.12)), joint='curve')
            d.line([(hx, hy), tail], fill=(196, 170, 120, 255), width=max(2, int(ppm * k * 0.12)))
    for k, X_, Y_, hp, lean, ci, pose in stamps:
        st, (fx, fy) = person(hp, lean, ci, pose); im.alpha_composite(st, (int(X_ - fx), int(Y_ - fy)))
    img = im.convert('RGB')
    # 倒れたときの土けむりとゆれ
    shake = 0.0
    if M.win == 'human' and after >= 0:
        ta = TOPPLE_T
        if after > ta:
            q = after - ta; shake = max(0.0, 18 * math.exp(-q * 2.2)) * min(1, ppm / 12)
            dust(img, xg - GR.GIANT_H * 0.7, q, cam)
    if 0 < tt < 2.5 and t > 0: shake = max(shake, 4 * (1 - tt / 2.5))
    if hud.get('ruler'):
        d2 = ImageDraw.Draw(img); rx = xg + GR.SPR_WM * 0.62; X0_, Y0_ = scr(rx, 0, 1.0, cam); _, Y50 = scr(rx, GR.GIANT_H, 1.0, cam)
        d2.line((X0_, Y0_, X0_, Y50), fill=(255, 220, 90), width=5)
        for zz in range(0, 51, 10):
            _, yy = scr(rx, zz, 1.0, cam); d2.line((X0_ - 10, yy, X0_ + 10, yy), fill=(255, 220, 90), width=4)
        d2.text((X0_ + 18, Y50), '身長 50m', font=Fo(max(30, int(ppm * 2.6))), fill=GOLD, anchor='lm', stroke_width=4, stroke_fill=(0, 0, 0))
    img = GR.finish(img, shake, f)
    if not hud.get('off'): hud_draw(img, M, t, hud)
    return img

TOPPLE_T = 4.2
FOREST_FA = GR.make_forest(2, -420, 420, 21.0, GR.FT, 0.8)
def topple_angle(q, a0):
    """倒れはじめてから q 秒の角度（左に倒れる＝正）"""
    if q <= 0: return a0
    u = min(1.0, q / TOPPLE_T); return a0 + (88 - a0) * (u ** 2.6)
_dz = np.random.default_rng(5).normal(0, 1, (400, 3))
def dust(img, x0, q, cam):
    d = ImageDraw.Draw(img, 'RGBA'); cx, cz, ppm = cam
    for i in range(160):
        a, b, c = _dz[i]
        x = x0 + a * 22 * (0.4 + q * 0.6) + i * 0.0; z = abs(b) * 6 * (0.3 + q) + 2
        X, Y = scr(x, z, 1.05, cam); R = ppm * (4 + abs(c) * 3) * (0.5 + q * 0.5)
        al = int(max(0, 150 * math.exp(-q * 0.45) * (0.6 + 0.4 * abs(c) / 2)))
        d.ellipse((X - R, Y - R * 0.7, X + R, Y + R * 0.7), fill=(170, 150, 120, al))

def fmt_t(s):
    s = max(0.0, s); m, ss = divmod(s, 60); return f'{int(m):02d}:{ss:04.1f}'
def hud_draw(im, M, t, hud):
    W, H = GR.W, GR.H; d = ImageDraw.Draw(im, 'RGBA'); tt = max(0.0, t)
    fh = M.fh(tt) if t > 0 else 0.0; fg = M.fg(tt) if t > 0 else 0.0; p = M.pos(tt) if t > 0 else 0.0
    if W > H:
        d.rectangle((0, 0, W, 132), fill=(8, 10, 16, 215))
        d.text((40, 30), f'人間チーム  {M.n:,}人', font=Fo(30), fill=HUM_C, anchor='lm')
        num(d, 40, 92, fh, 80, 'l')
        d.text((W - 40, 30), '巨人', font=Fo(30), fill=GIANT_C, anchor='rm')
        num(d, W - 40, 92, fg, 80, 'r')
        d.text((W / 2, 30), hud.get('round', ''), font=Fo(30), fill=GOLD, anchor='mm')
        d.text((W / 2, 74), fmt_t(tt), font=BE(52), fill=PALE, anchor='mm')
        bx0, bx1, by = W / 2 - 330, W / 2 + 330, 112
        meter(d, bx0, bx1, by, p, 18, small=True)
        d.text((W - 24, H - 22), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(20), fill=(235, 235, 235, 200), anchor='rs')
        cap = hud.get('cap')
        if cap:
            f = Fo(52); tw = f.getlength(cap)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 210))
            d.text((W / 2, H - 125), cap, font=f, fill=hud.get('capcol', PALE), anchor='mm')
    else:
        d.rectangle((0, 0, W, 360), fill=(8, 10, 16, 220))
        d.text((W / 2, 60), hud.get('title', ''), font=Fo(52), fill=PALE, anchor='mm')
        d.text((60, 140), f'人間 {M.n:,}人', font=Fo(38), fill=HUM_C, anchor='lm'); num(d, 60, 215, fh, 84, 'l')
        d.text((W - 60, 140), '巨人', font=Fo(38), fill=GIANT_C, anchor='rm'); num(d, W - 60, 215, fg, 84, 'r')
        meter(d, 80, W - 80, 300, p, 26)
        cap = hud.get('cap')
        if cap:
            f = Fo(64); lines = cap.split('\n'); hh = 90 * len(lines); tw = max(f.getlength(l) for l in lines)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, 1420, W / 2 + tw / 2 + 40, 1420 + hh + 40), 18, fill=(8, 10, 16, 215))
            for k, l in enumerate(lines): d.text((W / 2, 1420 + 20 + 45 + k * 90), l, font=f, fill=hud.get('capcol', PALE), anchor='mm')
        d.text((W / 2, H - 40), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(24), fill=(235, 235, 235, 210), anchor='mm')
def num(d, x, y, v, s, side):
    t = f'{v:,.0f}'; fu = Fo(int(s * 0.4)); uw = fu.getlength('kg') + 8; tw = BE(s).getlength(t)
    if side == 'r': x = x - uw - tw
    d.text((x, y), t, font=BE(s), fill=PALE, anchor='lm'); d.text((x + tw + 8, y + s * 0.18), 'kg', font=fu, fill=(210, 210, 215), anchor='ls')
def meter(d, x0, x1, y, p, h, small=False):
    """綱の位置メーター。左端 +10m（人間の勝ち）、右端 -20m（巨人の勝ち）"""
    span = AM.WIN_H - AM.WIN_G
    def X(v): return x0 + (AM.WIN_H - v) / span * (x1 - x0)
    d.rounded_rectangle((x0, y - h / 2, x1, y + h / 2), int(h / 2), fill=(255, 255, 255, 40))
    xc = X(0.0); xp = X(max(AM.WIN_G, min(AM.WIN_H, p)))
    if xp < xc: d.rounded_rectangle((xp, y - h / 2, xc, y + h / 2), int(h / 2), fill=HUM_C)
    else: d.rounded_rectangle((xc, y - h / 2, xp, y + h / 2), int(h / 2), fill=GIANT_C)
    d.line((xc, y - h, xc, y + h), fill=(255, 255, 255), width=3)
    d.ellipse((xp - h * 0.7, y - h * 0.7, xp + h * 0.7, y + h * 0.7), fill=GOLD, outline=(0, 0, 0), width=2)
    fs = 17 if small else 24
    if small: d.text((x0 - 10, y), '人間の勝ち', font=Fb(fs), fill=HUM_C, anchor='rm'); d.text((x1 + 10, y), '巨人の勝ち', font=Fb(fs), fill=GIANT_C, anchor='lm')
    else: d.text((x0, y + h + 8), '← 人間の勝ち', font=Fb(fs), fill=HUM_C, anchor='lt'); d.text((x1, y + h + 8), '巨人の勝ち →', font=Fb(fs), fill=GIANT_C, anchor='rt')
