"""巨人が立ち上がると気絶する？の描画"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/gfa'); sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/gvm')
import arender as A
import fmodel as FM
GR = A.GR
Fo, Fb, Mi, BE = GR.Fo, GR.Fb, GR.Mi, GR.BE
PALE, GOLD, GIANT_C = GR.PALE, GR.GOLD, GR.GIANT_C
BLOOD = (235, 70, 70); HUM_C = (150, 220, 120); RED = (255, 110, 110)
Z_HEART = 50 * 1.27 / 1.75; Z_BRAIN = Z_HEART + 0.35 * FM.S
def scr(x, z, k, cam): return GR.scr(x, z, k, cam)

def stand_person(hp, col=(60, 80, 120)):
    """まっすぐ立った人（足元が下中央）"""
    s = 3; L = int(hp * s); w = int(L * 0.42); im = Image.new('RGBA', (w, L + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx = w / 2
    skin = (215, 170, 135, 255); dark = (40, 44, 56, 255); c = col + (255,)
    d.rounded_rectangle((cx - L * 0.075, L * 0.52, cx - L * 0.01, L), radius=L * 0.02, fill=dark); d.rounded_rectangle((cx + L * 0.01, L * 0.52, cx + L * 0.075, L), radius=L * 0.02, fill=dark)
    d.rounded_rectangle((cx - L * 0.12, L * 0.17, cx + L * 0.12, L * 0.56), radius=L * 0.05, fill=c)
    d.rounded_rectangle((cx - L * 0.17, L * 0.18, cx - L * 0.11, L * 0.52), radius=L * 0.03, fill=c); d.rounded_rectangle((cx + L * 0.11, L * 0.18, cx + L * 0.17, L * 0.52), radius=L * 0.03, fill=c)
    d.ellipse((cx - L * 0.07, L * 0.02, cx + L * 0.07, L * 0.17), fill=skin); d.chord((cx - L * 0.075, L * 0.0, cx + L * 0.075, L * 0.13), 180, 360, fill=(50, 36, 28, 255))
    return im.resize((w // s, (L + 4) // s), Image.LANCZOS)

def heart_icon(d, x, y, r, col, beat=0.0):
    r = r * (1 + 0.25 * beat)
    d.ellipse((x - r, y - r * 0.6, x, y + r * 0.35), fill=col); d.ellipse((x, y - r * 0.6, x + r, y + r * 0.35), fill=col)
    d.polygon([(x - r * 0.97, y - r * 0.05), (x + r * 0.97, y - r * 0.05), (x, y + r * 1.05)], fill=col)
def beat_at(t, hr):
    ph = (t * hr / 60.0) % 1.0; return math.exp(-ph * 14) if t >= 0 else 0.0

def pcol(pb):
    if pb >= 60: return BLOOD
    if pb >= 30: return (240, 160, 60)
    return (130, 130, 140)

def scene_bg(cam):
    cx, cz, ppm = cam; W, H = GR.W, GR.H
    im = GR.sky().convert('RGBA'); d = ImageDraw.Draw(im)
    km = 0.22; xs = np.linspace(cx - W / 2 / (ppm * km), cx + W / 2 / (ppm * km), 200)
    pts = [scr(x, GR.mountains(x) * 0.25, km, cam) for x in xs]; _, Ym = scr(0, 0, km, cam)
    d.polygon(pts + [(W, Ym), (0, Ym)], fill=(132, 156, 178, 255))
    if Ym < H: d.rectangle((0, max(0, Ym), W, H), fill=(92, 120, 80, 255))
    GR.paste_strip(im, GR.FOREST_B, 0.82, cam)
    _, Yb = scr(0, 0, 0.82, cam)
    if Yb < H: d.rectangle((0, max(0, Yb), W, H), fill=(34, 60, 32, 255))
    return im

def render(M, t, cam, hud, f=0):
    """M：fmodel.Model。t<0 はスタート前（寝ている）"""
    W, H = GR.W, GR.H; cx, cz, ppm = cam; tt = max(0.0, t)
    a = M.at(tt, M.A) if t >= 0 else 0.0; pb = M.at(tt, M.Pb) if t >= 0 else 90 - 0; ph = M.at(tt, M.Ph) if t >= 0 else 90.0
    lost = M.at(tt, M.L) if t >= 0 else 0.0
    giant = M.h_brain > 1
    im = scene_bg(cam); d = ImageDraw.Draw(im)
    ang = 88.0 * (1 - a)
    if giant:
        lay, (px_, py_) = A.giant_layer(ppm, ang); X, Y = scr(0, 0, 1.0, cam)
        if lay.width < 9000: im.alpha_composite(lay, (int(X - px_), int(Y - py_)))
        GR.paste_strip(im, A.FOREST_FA, 1.1, cam)
        _, Yf = scr(0, 0, 1.1, cam); d = ImageDraw.Draw(im)
        if Yf < H: d.rectangle((0, max(0, Yf), W, H), fill=(30, 52, 28, 255))
        kv = 1.2; _, Yv = scr(0, 0, kv, cam)
        if Yv < H: d.rectangle((0, max(0, Yv - 2 * ppm * kv), W, H), fill=(70, 104, 56, 255))
        for hx, hw, hh, rc in GR.HOUSES:
            if hx < 0: continue
            X0, Y0 = scr(hx - hw / 2, 0, kv, cam); X1, Y1 = scr(hx + hw / 2, hh, kv, cam)
            Yr = Y1 - (X1 - X0) * 0.35
            d.rectangle((X0, Y1, X1, Y0), fill=(226, 220, 205, 255)); d.polygon([(X0 - 0.3 * ppm, Y1), (X1 + 0.3 * ppm, Y1), ((X0 + X1) / 2, Yr)], fill=rc + (255,))
        zh, zb = Z_HEART, Z_BRAIN
    else:
        _, Yg = scr(0, 0, 1.0, cam)
        if Yg < H: d.rectangle((0, max(0, Yg), W, H), fill=(84, 118, 62, 255))
        sp = stand_person(1.75 * ppm); L2 = sp.height + 4
        can = Image.new('RGBA', (2 * L2, 2 * L2), (0, 0, 0, 0)); can.alpha_composite(sp, (int(L2 - sp.width / 2), int(L2 - sp.height)))
        can = can.rotate(ang, resample=Image.BICUBIC, center=(L2, L2))
        X, Y = scr(0, 0, 1.0, cam); im.alpha_composite(can, (int(X - L2), int(Y - L2 - min(0.12 * ppm, 0.2 * ppm * math.sin(math.radians(ang))) * 0 )))
        zh, zb = 1.27, 1.62
        d = ImageDraw.Draw(im)
    # 心臓→脳の線
    r_ = math.radians(ang)
    hx, hz = -zh * math.sin(r_), zh * math.cos(r_); bx_, bz = -zb * math.sin(r_), zb * math.cos(r_)
    HX, HY = scr(hx, hz, 1.0, cam); BX, BY = scr(bx_, bz, 1.0, cam)
    if a > 0.02 or hud.get('marks'):
        d.line((HX, HY, BX, BY), fill=pcol(pb) + (255,), width=max(4, int(ppm * (0.35 if giant else 0.03))))
        rb = max(10, ppm * (1.6 if giant else 0.08)); d.ellipse((BX - rb, BY - rb, BX + rb, BY + rb), fill=pcol(pb) + (255,), outline=(255, 255, 255, 255), width=3)
        heart_icon(d, HX, HY, max(12, ppm * (1.5 if giant else 0.08)), BLOOD + (255,), beat_at(tt, M.hr))
        fs = int(max(26, min(48, ppm * (1.5 if giant else 0.07))))
        d.text((BX + rb + 10, BY), '脳', font=Fo(fs), fill=PALE, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((HX + rb + 10, HY), '心臓', font=Fo(fs), fill=PALE, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
    img = im.convert('RGB')
    # 倒れたときのゆれと土けむり
    shake = 0.0
    if M.faint_t is not None and giant and t > M.faint_t:
        tf = M.faint_t + M.t_up * 0.5
        if t > tf:
            q = t - tf; shake = 16 * math.exp(-q * 2.2); A.dust(img, -GR.GIANT_H * 0.6, q, cam)
    img = GR.finish(img, shake, f)
    # 意識が遠のく：まわりが暗く、色がうすく
    v = min(1.0, lost / 7.0)
    if M.faint_t is not None and t > M.faint_t: v = max(0.0, 1 - (t - M.faint_t) / 2.5) * 1.0 + 0.0
    if v > 0.02:
        g = ImageEnhance.Color(img).enhance(1 - 0.8 * v)
        key = (W, H)
        if key not in _V:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); _V[key] = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        r = _V[key]; m = np.clip((r - (1.25 - 1.0 * v)) / 0.35, 0, 1)[..., None] * min(1, v * 1.4)
        img = Image.fromarray((np.asarray(g, np.float32) * (1 - m * 0.95)).astype(np.uint8))
    if not hud.get('off'): hud_draw(img, M, t, hud, pb, ph, lost)
    return img
_V = {}

def fmt_t(s):
    s = max(0.0, s); m, ss = divmod(s, 60); return f'{int(m):02d}:{ss:04.1f}'
def hud_draw(im, M, t, hud, pb, ph, lost):
    W, H = GR.W, GR.H; d = ImageDraw.Draw(im, 'RGBA'); tt = max(0.0, t)
    fainted = M.faint_t is not None and t >= M.faint_t
    def num(x, y, v, s, side, col=PALE):
        txt = f'{v:,.0f}'.replace('-', '−'); fu = Fo(int(s * 0.32)); uw = fu.getlength('mmHg') + 8; tw = BE(s).getlength(txt)
        if side == 'r': x = x - uw - tw
        d.text((x, y), txt, font=BE(s), fill=col, anchor='lm'); d.text((x + tw + 8, y + s * 0.18), 'mmHg', font=fu, fill=(210, 210, 215), anchor='ls')
    if W > H:
        d.rectangle((0, 0, W, 140), fill=(8, 10, 16, 215))
        d.text((40, 30), '脳の血圧', font=Fo(30), fill=pcol(pb), anchor='lm'); num(40, 94, pb, 80, 'l', RED if pb < 30 else PALE)
        d.text((330, 30), '気絶ライン 30', font=Fb(20), fill=(200, 200, 205), anchor='lm')
        d.text((W - 40, 30), '心臓の血圧', font=Fo(30), fill=BLOOD, anchor='rm'); num(W - 110, 94, ph, 80, 'r')
        heart_icon(d, W - 62, 92, 20, BLOOD, beat_at(tt, M.hr))
        d.text((W - 300, 30), f'心拍 {M.hr:.1f}回/分' if M.hr < 10 else f'心拍 {M.hr:.0f}回/分', font=Fb(22), fill=(200, 200, 205), anchor='rm')
        d.text((W / 2, 28), hud.get('round', ''), font=Fo(30), fill=GOLD, anchor='mm')
        d.text((W / 2, 72), fmt_t(tt), font=BE(50), fill=PALE, anchor='mm')
        x0, x1, y = W / 2 - 260, W / 2 + 260, 116; u = min(1.0, lost / 7.0)
        d.rounded_rectangle((x0, y - 11, x1, y + 11), 11, fill=(255, 255, 255, 40))
        if u > 0: d.rounded_rectangle((x0, y - 11, x0 + max(22, (x1 - x0) * u), y + 11), 11, fill=(255, int(200 * (1 - u)), 60))
        lab = '気絶！' if fainted else (f'気絶まで あと{max(0, 7 - lost):.1f}秒' if lost > 0.05 else '意識あり')
        d.text((x1 + 14, y), lab, font=Fb(22), fill=RED if lost > 0.05 else HUM_C, anchor='lm'); d.text((x0 - 14, y), '意識', font=Fb(22), fill=(200, 200, 205), anchor='rm')
        d.text((W - 24, H - 22), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(20), fill=(235, 235, 235, 200), anchor='rs')
        cap = hud.get('cap')
        if cap:
            f = Fo(52); tw = f.getlength(cap)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 210))
            d.text((W / 2, H - 125), cap, font=f, fill=hud.get('capcol', PALE), anchor='mm')
    else:
        d.rectangle((0, 0, W, 360), fill=(8, 10, 16, 220))
        d.text((W / 2, 60), hud.get('title', ''), font=Fo(50), fill=PALE, anchor='mm')
        d.text((60, 140), '脳の血圧', font=Fo(38), fill=pcol(pb), anchor='lm'); num(60, 215, pb, 84, 'l', RED if pb < 30 else PALE)
        d.text((W - 60, 140), '心臓の血圧', font=Fo(38), fill=BLOOD, anchor='rm'); num(W - 60, 215, ph, 84, 'r')
        x0, x1, y = 80, W - 80, 305; u = min(1.0, lost / 7.0)
        d.rounded_rectangle((x0, y - 14, x1, y + 14), 14, fill=(255, 255, 255, 40))
        if u > 0: d.rounded_rectangle((x0, y - 14, x0 + max(28, (x1 - x0) * u), y + 14), 14, fill=(255, int(200 * (1 - u)), 60))
        lab = '気絶！' if fainted else (f'気絶まで あと{max(0, 7 - lost):.1f}秒' if lost > 0.05 else '意識あり')
        d.text((W / 2, y + 40), lab, font=Fb(30), fill=RED if lost > 0.05 else HUM_C, anchor='mm')
        cap = hud.get('cap')
        if cap:
            f = Fo(64); lines = cap.split('\n'); hh = 90 * len(lines); tw = max(f.getlength(l) for l in lines)
            d.rounded_rectangle((W / 2 - tw / 2 - 40, 1420, W / 2 + tw / 2 + 40, 1420 + hh + 40), 18, fill=(8, 10, 16, 215))
            for k, l in enumerate(lines): d.text((W / 2, 1420 + 20 + 45 + k * 90), l, font=f, fill=hud.get('capcol', PALE), anchor='mm')
        d.text((W / 2, H - 40), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(24), fill=(235, 235, 235, 210), anchor='mm')
