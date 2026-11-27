"""マリアナ海溝の底に落ちたら？ の場面"""
import json, math, sys, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/air')
import arnd as R, mcont as C
from arnd import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ctext, fade, ease, writer, rowbox, foot, note
G = '/home/claude/mrt'; D = json.load(open(f'{G}/dur.json'))
AQUA = (110, 220, 235); SKIN = (36, 50, 70); BOTTOM = 10920
def frac(key, phrase): i = C.NAR[key].index(phrase); return i / len(C.NAR[key])
def onsets(key, last=4):
    with wave.open(f'{G}/voice/{key}.wav') as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    k = int(sr * 0.02); e = np.sqrt(np.convolve(a * a, np.ones(k) / k, 'same'))[::k]; on = e > 0.02; res = []; quiet = 0
    for i, v in enumerate(on):
        if v and quiet >= 6: res.append(i * 0.02)
        quiet = 0 if v else quiet + 1
    return res[-last:]
def run(out, dur, fn):
    p = writer(out)
    for f in range(int(dur * FPS)): p.stdin.write(fn(f / FPS).tobytes())
    p.stdin.close(); p.wait()
def atm(depth): return 1 + depth / 10.0 * (1070 / 1092)   # 10mで約1気圧、底で約1,070気圧になるよう少しだけ補正
# ---- 海の背景（深さで暗くなる） ----
def light(depth): return math.exp(-depth / 170.0)
_BG = {}
def sea_bg(depth, w=W, h=H):
    L = light(depth); k = (w, h, round(L * 80) if L > 0.004 else -1)
    if k in _BG: return _BG[k]
    sw, sh = w // 8, h // 8; yy = np.linspace(0, 1, sh)[:, None, None]; xx = np.linspace(0, 1, sw)[None, :, None]
    deep = np.array((4, 14, 30), float); mid = np.array((10, 40, 80), float); top = np.array((40, 130, 190), float)
    Lt = min(1, L * 1.3); Lb = L * 0.6
    ct = deep + (mid - deep) * min(1, Lt * 3) + (top - mid) * Lt; cb = deep + (mid - deep) * min(1, Lb * 3) + (top - mid) * Lb
    c = ct * (1 - yy) + cb * yy + 0 * xx
    if L > 0.02:   # 上からの光の筋
        for x0, wd in ((0.2, 0.05), (0.38, 0.03), (0.55, 0.06), (0.74, 0.035), (0.88, 0.04)):
            ray = np.exp(-((xx - x0 - 0.12 * yy) / wd) ** 2) * np.clip(1 - yy * 1.2, 0, 1); c = c + ray * np.array((60, 110, 130)) * L * 0.9
    c = c * (0.55 + 0.45 * np.cos((xx - 0.5) * 2.2))   # 左右を少し暗く
    im = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC); _BG[k] = im; return im
_SN = np.random.default_rng(11).uniform(0, 1, (90, 4))
def snow(d, t, speed=1.0, w=W, h=H, a=1.0):
    """マリンスノー（沈んでいくので上へ流れる）"""
    for x0, y0, s, ph in _SN:
        y = (y0 * h - t * speed * (40 + 80 * s)) % h; x = x0 * w + 8 * math.sin(t * 0.7 + ph * 6); r = 1 + 2.5 * s
        r = 0.8 + 1.6 * s; d.ellipse((x - r * 1.6, y - r, x + r * 1.6, y + r), fill=(120, 165, 185, int(90 * a * (0.3 + s * 0.7))))
_PH = {}
def photo(w=W, h=H, zoom=1.12):
    k = (w, h, zoom)
    if k not in _PH:
        p = Image.open(f'{G}/dl/PIA11019.jpg').convert('RGB'); s = max(w / p.width, h / p.height) * zoom
        p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS); _PH[k] = ImageEnhance.Brightness(p).enhance(0.85)
    return _PH[k]
def photo_frame(t, w=W, h=H, dur=20.0, zoom=1.12):
    p = photo(w, h, zoom); u = t / dur; x = int((p.width - w) * (0.3 + 0.4 * u)); y = int((p.height - h) * (0.3 + 0.5 * u))
    return p.crop((x, y, x + w, y + h))
# ---- 人形（光るふち）と胸の空気の袋 ----
_FIG = {}
def _fig_layer(s, col):
    key = (int(s), col)
    if key in _FIG: return _FIG[key]
    S = int(s * 2.4); im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    th = s * 0.11; fill = SKIN + (255,)
    def limb(p, q, wdt):
        d.line((p, q), fill=fill, width=int(wdt))
        for x, y in (p, q): d.ellipse((x - wdt / 2, y - wdt / 2, x + wdt / 2, y + wdt / 2), fill=fill)
    hip = (c, c + s * 0.12); sh = (c, c - s * 0.32); hw = s * 0.15
    limb((c - hw * 0.5, hip[1]), (c - s * 0.25, c + s * 0.66), th * 1.2); limb((c + hw * 0.5, hip[1]), (c + s * 0.2, c + s * 0.68), th * 1.2)
    limb((c - hw, sh[1] + s * 0.04), (c - s * 0.45, c - s * 0.62), th); limb((c + hw, sh[1] + s * 0.04), (c + s * 0.45, c - s * 0.62), th)
    d.rounded_rectangle((c - hw * 1.25, sh[1] - s * 0.02, c + hw * 1.25, hip[1] + s * 0.04), int(s * 0.08), fill=fill)
    hr = s * 0.13; d.ellipse((c - hr, sh[1] - s * 0.08 - hr * 2, c + hr, sh[1] - s * 0.08), fill=fill)
    for jy in (sh[1] - s * 0.08 - hr, sh[1] + s * 0.18):   # 人形らしい関節の線
        d.line((c - hw * 0.9, jy + s * 0.12, c + hw * 0.9, jy + s * 0.12), fill=(60, 78, 104, 255), width=2)
    a = im.split()[3]; edge = a.filter(ImageFilter.MaxFilter(5)); rim = Image.new('RGBA', (S, S), col + (255,)); out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(rim, (0, 0), edge); gl = out.filter(ImageFilter.GaussianBlur(s * 0.06)); res = Image.alpha_composite(gl, out); res = Image.alpha_composite(res, im)
    _FIG[key] = res; return res
def figure(im, cx, cy, s, ang=0.0, col=AQUA, bag=None, lamp=False):
    """bag：空気の袋の体積（1＝6L）。lamp：頭にライト"""
    L = _fig_layer(s, col)
    if bag is not None or lamp:
        L = L.copy(); d = ImageDraw.Draw(L); c = L.width / 2
        if bag is not None:
            r = s * 0.13 * max(bag, 1e-9) ** (1 / 3); y = c - s * 0.12
            d.ellipse((c - r, y - r, c + r, y + r), fill=(170, 230, 255, 230), outline=(255, 255, 255, 255), width=max(1, int(s * 0.012)))
        if lamp: y = c - s * 0.52; d.ellipse((c - s * 0.05, y - s * 0.05, c + s * 0.05, y + s * 0.05), fill=(255, 245, 200, 255))
    L = L.rotate(ang, resample=Image.BICUBIC); im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))
def timer_hm(d, sec, x=W - 30, y=60, col=AQUA, label='経過'):
    d.rounded_rectangle((x - 400, y - 44, x, y + 44), 18, fill=(4, 10, 22, 235), outline=col, width=3)
    d.text((x - 380, y), label, font=Fb(30), fill=GREY, anchor='lm'); h = int(sec // 3600); m = int(sec % 3600 // 60); s = int(sec % 60)
    d.text((x - 24, y + 6), f'{h}:{m:02d}:{s:02d}', font=BE(80), fill=PALE, anchor='rm')
def timer_s(d, sec, x=W - 30, y=60, col=AQUA):
    d.rounded_rectangle((x - 360, y - 44, x, y + 44), 18, fill=(4, 10, 22, 235), outline=col, width=3)
    d.text((x - 340, y), '経過', font=Fb(30), fill=GREY, anchor='lm'); d.text((x - 70, y + 6), f'{sec:4.1f}', font=BE(80), fill=PALE, anchor='rm')
    d.text((x - 22, y + 4), '秒', font=Fo(40), fill=PALE, anchor='rm')
def header(d, a, b):
    d.rectangle((0, 0, W, 120), fill=(2, 6, 14, 235)); ctext(d, (W / 2 - 200, 40), a, Fo(38), GOLD); ctext(d, (W / 2 - 200, 92), b, Fb(28), PALE)
def capbar(d, cap, col, y=960):
    if not cap: return
    fnt = Fo(54); tw = fnt.getlength(cap)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, y - 45, W / 2 + tw / 2 + 40, y + 45), 18, fill=(4, 8, 16, 235), outline=col, width=3); ctext(d, (W / 2, y), cap, fnt, col)
def caps_for(cues): return [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in cues if k in C.CAP]
def countdown(d, t, ons, xy):
    labs = ['3', '2', '1', 'スタート']
    for i in range(len(ons)):
        a = ons[i]; b = ons[i + 1] if i + 1 < len(ons) else a + 1.0
        if a <= t < b:
            u = ease((t - a) / 0.2)
            if i < 3: ctext(d, xy, labs[i], BE(int(170 * (1.3 - 0.3 * u))), PALE, sw=6)
            else: ctext(d, xy, labs[i], Mi(int(110 * (1.3 - 0.3 * u))), AQUA, sw=6)
def gauge(d, cx, cy, r, val, vmax=1100, unit='気圧'):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(8, 12, 22), outline=PALE, width=5)
    for i in range(11):
        a = math.radians(135 + 270 * i / 10); d.line((cx + r * 0.82 * math.cos(a), cy + r * 0.82 * math.sin(a), cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)), fill=GREY, width=4)
    a = math.radians(135 + 270 * max(0, min(1, val / vmax))); d.line((cx, cy, cx + r * 0.75 * math.cos(a), cy + r * 0.75 * math.sin(a)), fill=RED, width=8); d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=PALE)
    ctext(d, (cx, cy + r * 0.45), f'{val:,.0f}', Fo(int(r * 0.3)), PALE); ctext(d, (cx, cy + r * 0.72), unit, Fb(int(r * 0.14)), GREY)
def depth_bar(d, x, y0, y1, depth, marks=((200, '200m 光が届かない'), (1000, '1,000m 真っ暗'))):
    """縦の水深計（0〜10,920m）"""
    d.rounded_rectangle((x - 22, y0 - 6, x + 22, y1 + 6), 20, fill=(8, 12, 22), outline=GREY, width=3)
    yy = y0 + (y1 - y0) * min(1, depth / BOTTOM); d.rounded_rectangle((x - 14, y0, x + 14, max(y0 + 2, yy)), 12, fill=AQUA)
    d.polygon([(x + 26, yy), (x + 50, yy - 14), (x + 50, yy + 14)], fill=GOLD)
    d.text((x - 34, y0), '0m', font=Fb(24), fill=GREY, anchor='rm'); d.text((x - 34, y1), '10,920m', font=Fb(24), fill=GREY, anchor='rm')
def amphipod(d, x, y, s, ang=0.0, a=255, col=(235, 215, 200)):
    """ヨコエビ（横から見た丸まった体）"""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v): return (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    for i in range(9):
        th = math.pi * (0.15 + 0.75 * i / 8); u = -math.cos(th) * 0.9; v = -math.sin(th) * 0.45; r = 0.2 * (1 - abs(i - 3.5) / 7)
        p = P(u, v); d.ellipse((p[0] - r * s, p[1] - r * s * 0.9, p[0] + r * s, p[1] + r * s * 0.9), fill=col + (a,))
    h = P(-0.8, -0.2); d.line([h, P(-1.5, -0.7), P(-1.9, -0.6)], fill=col + (a,), width=max(1, int(s * 0.05)))
    for i in range(5):
        p = P(-0.5 + i * 0.25, -0.1); d.line([p, P(-0.55 + i * 0.25, 0.35)], fill=col + (int(a * 0.8),), width=max(1, int(s * 0.04)))
    e = P(-0.72, -0.35); d.ellipse((e[0] - s * 0.05, e[1] - s * 0.05, e[0] + s * 0.05, e[1] + s * 0.05), fill=(40, 20, 20, a))
def cup(d, cx, cy, s, col=(240, 240, 235)):
    d.polygon([(cx - s * 0.5, cy - s * 0.6), (cx + s * 0.5, cy - s * 0.6), (cx + s * 0.34, cy + s * 0.6), (cx - s * 0.34, cy + s * 0.6)], fill=col, outline=(160, 160, 160))
    d.ellipse((cx - s * 0.5, cy - s * 0.68, cx + s * 0.5, cy - s * 0.52), fill=(210, 210, 205), outline=(160, 160, 160))
def fish(d, cx, cy, s, col=(150, 170, 200)):
    d.ellipse((cx - s, cy - s * 0.38, cx + s * 0.7, cy + s * 0.38), fill=col); d.polygon([(cx + s * 0.6, cy), (cx + s * 1.1, cy - s * 0.4), (cx + s * 1.1, cy + s * 0.4)], fill=col)
    d.ellipse((cx - s * 0.75, cy - s * 0.12, cx - s * 0.57, cy + s * 0.06), fill=(20, 20, 30))
def sphere_sub(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(120, 130, 145), outline=PALE, width=4); ri = r * 0.72
    d.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), fill=(150, 210, 240)); ctext(d, (cx, cy), '空気', Fo(int(r * 0.32)), (10, 30, 50))
    ctext(d, (cx, cy + r + 34), '分厚い金属の壁', Fb(30), GREY)

# ---- 1回戦：沈む時間（早送り） ----
SPD = 0.5   # m/s（仮定）
def r_times(key):
    ons = [0.2 + o for o in onsets(key + 'a')]; tf = ons[3]
    cues = [(0.2, key + 'a'), (tf + 1.2, key + 'b')]; cues.append((cues[-1][0] + D[key + 'b'] + 1.2, key + 'c')); cues.append((cues[-1][0] + D[key + 'c'] + 1.2, key + 'd'))
    return ons, tf, cues
def r1_times():
    ons, tf, cues = r_times('r1'); end = cues[-1][0] + D['r1d'] + 1.2; return ons, tf, cues, end
def interp(x, xs, ys): return float(np.interp(x, xs, ys))
def r1_frame(vt, ons, tf, caps, cues):
    t0 = tf + 0.6; tb, tc, td = cues[1][0], cues[2][0], cues[3][0]
    sim = 0.0 if vt < t0 else interp(vt, [t0, tb, tc, td, td + 10], [0, 400, 2000, 3600, 3900]); depth = sim * SPD
    im = sea_bg(depth).copy().convert('RGBA'); d0 = ImageDraw.Draw(im, 'RGBA'); snow(d0, vt, 2.5 if vt > t0 else 0.2, a=0.5 + 0.5 * min(1, depth / 300 + 0.3))
    figure(im, 560, 560, 300, 8 * math.sin(vt * 0.5) + 4, col=AQUA if depth < 900 else (90, 150, 190))
    d = ImageDraw.Draw(im, 'RGBA'); header(d, '1回戦　うわさ1「底まで一瞬」', '人と同じ重さ・形の人形を 海面から沈める（空想の設定）')
    d.rounded_rectangle((1060, 150, 1880, 880), 20, fill=(4, 8, 16, 225))
    depth_bar(d, 1180, 200, 820, depth)
    ctext(d, (1530, 210), '水深', Fo(36), GREY); d.text((1640, 320), f'{depth:,.0f}', font=BE(150), fill=PALE, anchor='rm'); d.text((1660, 345), 'm', font=Fo(60), fill=PALE, anchor='lm')
    rows = [('沈む速さ（仮定）', '秒速 約0.5m', PALE), ('光', '明るい' if depth < 150 else ('ほとんど届かない' if depth < 900 else 'ほぼゼロ'), GOLD if depth < 900 else RED),
            ('底まで あと', f'{(BOTTOM - depth):,.0f}m', AQUA)]
    for i, (a, b, col) in enumerate(rows):
        y = 520 + i * 100; d.text((1290, y), a, font=Fb(32), fill=GREY, anchor='lm'); d.text((1850, y), b, font=Fo(42), fill=col, anchor='rm')
    if vt >= t0: timer_hm(d, sim); ctext(d, (W - 230, 135), '早送り', Fb(26), GOLD)
    countdown(d, vt, ons, (560, 560))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, AQUA)
    note(d); foot(d, '※沈む速さは 人と同じくらいの重さ・形の物として仮定した目安です', size=18); return im.convert('RGB')
def scene_r1():
    ons, tf, cues, end = r1_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r1.mp4', end, lambda t: r1_frame(t, ons, tf, caps, cues))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r1_t.json', 'w')); return end, cues
# ---- 2回戦：ぺちゃんこ？（一気に底まで） ----
def r2_times():
    ons, tf, cues = r_times('r2'); end = cues[-1][0] + D['r2d'] + 1.4; return ons, tf, cues, end
def r2_frame(vt, ons, tf, caps, cues):
    t0 = tf + 0.6; tb, tc, td = cues[1][0], cues[2][0], cues[3][0]
    depth = 0.0 if vt < t0 else interp(vt, [t0, tb, tb + D['r2b'] + 0.4, tc + D['r2c'], td], [0, 1000, 1000, 6500, BOTTOM]); P = atm(depth); bag = 1 / P
    im = sea_bg(depth).copy().convert('RGBA'); d0 = ImageDraw.Draw(im, 'RGBA'); snow(d0, vt, 6 if t0 < vt < td else 0.3)
    figure(im, 520, 560, 300, 6 * math.sin(vt * 0.5), col=AQUA if depth < 900 else (90, 150, 190), bag=bag)
    d = ImageDraw.Draw(im, 'RGBA'); header(d, '2回戦　うわさ2「水圧でぺちゃんこ」', '人形の胸には 肺と同じ6Lの空気の袋（一気に底まで早送り）')
    ctext(d, (520, 840), f'水深 {depth:,.0f}m', Fo(44), PALE, sw=3)
    d.rounded_rectangle((900, 150, 1880, 880), 20, fill=(4, 8, 16, 225))
    ctext(d, (1100, 200), '水圧', Fo(36), PALE); gauge(d, 1100, 390, 160, P)
    ctext(d, (1560, 200), '空気の袋', Fo(36), PALE)
    r = 150 * bag ** (1 / 3); d.ellipse((1560 - 150, 390 - 150, 1560 + 150, 390 + 150), outline=(90, 100, 120), width=2)
    d.ellipse((1560 - r, 390 - r, 1560 + r, 390 + r), fill=(170, 230, 255, 220), outline=PALE, width=3)
    ml = 6000 * bag; ctext(d, (1560, 590), (f'{ml / 1000:.1f}L' if ml >= 1000 else f'{ml:,.0f}mL'), Fo(54), AQUA)
    d.text((940, 680), '体の水（体積）', font=Fb(32), fill=GREY, anchor='lm')
    shr = 1 - 0.05 * min(1, depth / BOTTOM); d.rectangle((940, 720, 1840, 780), outline=GREY, width=3); d.rectangle((946, 726, 946 + 888 * shr, 774), fill=(70, 150, 235))
    d.text((1840, 680), f'{shr * 100:.0f}%', font=Fo(44), fill=GREEN, anchor='rm')
    d.text((940, 830), '空気の袋（体積）', font=Fb(32), fill=GREY, anchor='lm'); d.text((1840, 830), f'{bag * 100:.1f}%' if bag > 0.01 else f'{bag * 100:.2f}%', font=Fo(44), fill=RED if bag < 0.5 else PALE, anchor='rm')
    if vt >= t0: timer_s(d, max(0.0, vt - t0)); ctext(d, (W - 210, 135), '一気に早送り', Fb(26), GOLD)
    countdown(d, vt, ons, (520, 560))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, AQUA)
    note(d); foot(d, '※空気はボイルの法則（気圧が10倍なら体積は10分の1）。水が縮むのは約1,000気圧で約5%（目安）', size=18); return im.convert('RGB')
def scene_r2():
    ons, tf, cues, end = r2_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r2.mp4', end, lambda t: r2_frame(t, ons, tf, caps, cues))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r2_t.json', 'w')); return end, cues
# ---- 決勝：底に生き物は？ ----
_AM = np.random.default_rng(21).uniform(0, 1, (46, 5))
def r3_times():
    ons, tf, cues = r_times('r3'); end = cues[-1][0] + D['r3d'] + 1.6; return ons, tf, cues, end
def r3_frame(vt, ons, tf, caps, cues):
    t0 = tf + 0.6; tb, tc, td = cues[1][0], cues[2][0], cues[3][0]
    im = sea_bg(BOTTOM).copy().convert('RGBA'); on = vt >= t0
    if on:   # ライトの光（円すい）
        k = min(1, (vt - t0) / 0.4); l = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(l)
        dl.polygon([(420, 470), (980, 250), (980, 900)], fill=(200, 225, 255, int(70 * k))); dl.ellipse((620, 330, 1000, 820), fill=(200, 225, 255, int(40 * k)))
        im.alpha_composite(l.filter(ImageFilter.GaussianBlur(40)))
    d0 = ImageDraw.Draw(im, 'RGBA'); d0.rectangle((0, 880, W, H), fill=(18, 16, 14, 255)) if False else None
    for x in range(0, W, 6): d0.line((x, 905 + 10 * math.sin(x * 0.01), x + 6, 905 + 10 * math.sin((x + 6) * 0.01)), fill=(60, 58, 52, 255), width=3)
    d0.rectangle((0, 912, W, H), fill=(28, 26, 24, 255)) if True else None
    snow(d0, vt, 0.4, a=0.4)
    n = 0 if vt < tb else (int(1 + 3 * (vt - tb) / max(0.1, tc - tb)) if vt < tc else int(4 + 42 * min(1, (vt - tc) / (td + 1.0 - tc))))
    for i in range(min(n, len(_AM))):
        x0, y0, s, ph, sp = _AM[i]; x = 640 + 330 * x0 + 30 * math.sin(vt * (0.8 + sp) + ph * 6); y = 340 + 520 * y0 + 14 * math.sin(vt * 1.3 + ph * 4)
        amphipod(d0, x, y, 22 + 18 * s, ang=0.5 * math.sin(vt + ph * 6), a=230 if on else 40)
    figure(im, 330, 640, 240, 70, col=(80, 130, 170), lamp=True)
    d = ImageDraw.Draw(im, 'RGBA'); header(d, '決勝戦　うわさ3「底には何もいない」', '水深10,920m　人形のライトをつけて待つ（実際の時間で）')
    d.rounded_rectangle((1160, 150, 1880, 760), 20, fill=(4, 8, 16, 225))
    rows = [('水深', '10,920m', PALE), ('水圧', '約1,070気圧', PALE), ('光', 'ゼロ（真っ暗）', RED), ('水温', '数℃', AQUA), ('見つけた生き物', f'{min(n, len(_AM))}匹', GOLD)]
    for i, (a, b, col) in enumerate(rows):
        y = 220 + i * 110; d.text((1200, y), a, font=Fb(32), fill=GREY, anchor='lm'); d.text((1850, y), b, font=Fo(46), fill=col, anchor='rm')
    if on: timer_s(d, vt - t0)
    countdown(d, vt, ons, (560, 520))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, AQUA)
    note(d); foot(d, '※生き物はカイコウオオソコエビ（ヨコエビの仲間）のイメージ。数と動きは空想です', size=18); return im.convert('RGB')
def scene_r3():
    ons, tf, cues, end = r3_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r3.mp4', end, lambda t: r3_frame(t, ons, tf, caps, cues))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r3_t.json', 'w')); return end, cues

# ---- 静的な場面 ----
def shade_left(im, a0=210, wfrac=0.62):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); a = np.clip(1 - np.arange(W) / (W * wfrac), 0, 1) ** 1.5 * a0
    sh.putalpha(Image.fromarray(np.repeat(a[None, :], H, 0).astype(np.uint8))); im.alpha_composite(sh)
def scene_title():
    dur = 0.6 + D['intro'] + 0.6; k = 'intro'; f1 = frac(k, '水圧'); f2 = frac(k, '底まで、'); f3 = frac(k, '実際') - 0.02; f4 = frac(k, '実際')
    def fr(t):
        im = photo_frame(t, dur=dur).convert('RGBA'); u = ease(t / 0.5); shade_left(im)
        dd = ImageDraw.Draw(im, 'RGBA'); snow(dd, t, 0.6, a=0.6)
        figure(im, 1450, 300 + t * 14, 200, 15 * math.sin(t * 0.6) + 10, col=AQUA); d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (100, 320), 'マリアナ海溝の底に', Mi(int(96 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (100, 470), '落ちたら', Mi(120), AQUA, 'lm', 8)
        if t > 0.6: ctext(d, (100, 620), 'どうなる？', Mi(120), GOLD, 'lm', 6)
        if t > 0.9: ctext(d, (106, 720), 'WHAT IF YOU FELL TO THE BOTTOM OF THE MARIANA TRENCH?', Fb(28), (225, 225, 230), 'lm', 2)
        uu = (t - 0.6) / D['intro']
        for i, (ff, lab) in enumerate([(f1, 'うわさ　ぺちゃんこ？'), (f2, 'うわさ　底まで一瞬？'), (f3, 'うわさ　？？？')]):
            if uu > ff: d.rounded_rectangle((100 + i * 420, 800, 500 + i * 420, 880), 16, fill=(4, 12, 26, 230), outline=AQUA, width=3); ctext(d, (300 + i * 420, 840), lab, Fo(34), PALE)
        if uu > f4: ctext(d, (100, 950), '3つの勝負で 確かめる', Fo(44), GOLD, 'lm', 3)
        d.text((W - 24, 30), '背景の写真：NASA（PIA11019、バハマの深い海の入り口。マリアナ海溝ではありません）', font=Fb(20), fill=(220, 220, 225), anchor='rm')
        note(d, size=20); return im.convert('RGB')
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8; k = 'data'
    rows = [(frac(k, 'チャレンジャー'), 'いちばん深い所（チャレンジャー海淵）', '約10,920m', PALE, False), (frac(k, 'エベレスト'), 'エベレスト（8,849m）を沈めても', '上に 約2,000mの水', AQUA, False),
            (frac(k, '水は、'), '10m もぐるごとに', '約1気圧ずつ増える', PALE, False), (frac(k, '底の水圧'), '底の水圧', '約1,070気圧', RED, True), (frac(k, '指先'), '指先ほど（1cm²）に', '約1.1トン', GOLD, True)]
    def fr(t):
        im = sea_bg(600).copy().convert('RGBA'); u = (t - t0) / dd
        if t < 0.4: R.glow(im, W / 2, H / 2, 700, AQUA, int(120 * (1 - t / 0.4)))
        d = ImageDraw.Draw(im, 'RGBA'); ctext(d, (W / 2, 70), '深さの数字', Mi(68), GOLD, sw=3)
        # 左：断面図（海面〜底、エベレスト）
        x0, x1, ys, yb = 120, 680, 200, 900; d.rounded_rectangle((x0 - 20, 150, x1 + 20, 960), 20, fill=(4, 8, 16, 200))
        dep = lambda m: ys + (yb - ys) * m / BOTTOM
        for yy in range(ys, yb, 6):
            c = 1 - (yy - ys) / (yb - ys); d.rectangle((x0, yy, x1, yy + 6), fill=(int(10 + 40 * c), int(30 + 100 * c), int(60 + 120 * c)))
        d.line((x0, ys, x1, ys), fill=PALE, width=3); d.text((x0 + 8, ys - 26), '海面', font=Fb(26), fill=PALE, anchor='lm')
        if u >= rows[1][0]:
            d.polygon([(x0 + 60, yb), (x0 + 230, dep(BOTTOM - 8849)), (x0 + 400, yb)], fill=(120, 110, 100), outline=PALE)
            ctext(d, (x0 + 230, dep(BOTTOM - 8849) + 70), 'エベレスト', Fb(28), PALE)
            yE = dep(BOTTOM - 8849); d.line((x0 + 470, ys, x0 + 470, yE), fill=GOLD, width=4); ctext(d, (x0 + 470 + 2, (ys + yE) / 2), '約2,000m', Fo(28), GOLD, 'lm' if False else 'mm', sw=3)
        d.text((x1 - 8, yb + 26), '10,920m', font=Fb(28), fill=GOLD, anchor='rm')
        mk = min(1, max(0, u / max(0.01, rows[0][0] + 0.05))); yy = ys + (yb - ys) * mk
        d.ellipse((x1 - 50 - 12, yy - 12, x1 - 50 + 12, yy + 12), fill=GOLD)
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 230 + r * 150, lab, val, col, 760, 1860, hl, lf=34, vf=50)
        note(d); foot(d, '※深さ・水圧：UCL（1,086バール）など。1気圧＝1.013バール。1cm²あたりの重さは計算した目安')
        return im.convert('RGB')
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; k = 'rule'
    RULES = [('人形', '人と同じ重さ・形の人形を沈める', frac(k, '本物')), ('胸', '肺と同じ 6Lの空気の袋', frac(k, '人形の胸')),
             ('うわさ1', '底まで 一瞬', frac(k, 'うわさ一')), ('うわさ2', '水圧で ぺちゃんこ', frac(k, 'うわさ二')), ('うわさ3', '底には 何もいない', frac(k, 'うわさ三'))]
    def fr(t):
        im = sea_bg(120).copy().convert('RGBA'); dd = ImageDraw.Draw(im, 'RGBA'); snow(dd, t, 0.5, a=0.5)
        figure(im, 1680, 220, 140, 8 * math.sin(t * 0.7), bag=1.0 if t > 0.5 + D['rule'] * frac(k, '人形の胸') else None); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 90), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 160), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 210 + r * 140
            d.rounded_rectangle((140, y, W - 340, y + 110), 18, fill=(4, 8, 16, 225), outline=AQUA if r >= 2 else None, width=3 if r >= 2 else 0)
            d.rounded_rectangle((170, y + 22, 450, y + 88), 14, fill=(AQUA if r >= 2 else BLUE)); ctext(d, (310, y + 55), who, Fo(34), (10, 14, 24))
            d.text((490, y + 55), txt, font=Fo(46), fill=PALE, anchor='lm')
        if u > frac(k, '三つの'): ctext(d, (W / 2, 950), '水深計を見ながら 確かめる', Mi(52), GOLD, sw=3)
        note(d); foot(d, '※空想のシミュレーションです。本物の人は沈めません。実在の事故は扱いません')
        return im.convert('RGB')
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]
def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None, icon=None, depth=3000):
    dur = 0.6 + D[key] + 0.8; b = sea_bg(depth).filter(ImageFilter.GaussianBlur(2))
    def fr(t):
        im = b.copy().convert('RGBA'); u = ease(t / 0.4); dd = ImageDraw.Draw(im, 'RGBA'); snow(dd, t, 0.4, a=0.5)
        if icon: icon(im, t)
        d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 200), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 340), big, Mi(int(110 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col, ph) in enumerate(lines):
            if t < 0.6 + D[key] * frac(key, ph): continue
            y = 500 + r * 108
            d.rounded_rectangle((W / 2 - 820, y - 46, W / 2 + 820, y + 46), 16, fill=(4, 8, 16, 225))
            d.text((W / 2 - 780, y), lab, font=Fb(34), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 780, y), val, font=Fo(44), fill=col, anchor='rm')
        if sub: foot(d, sub, size=18)
        note(d)
        return im.convert('RGB')
    run(out, dur, fr); return dur, [(0.6, key)]
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0; k = 'reveal'
    f1 = frac(k, '空気の入った'); f2 = frac(k, '発泡'); f3 = frac(k, 'だから'); f4 = frac(k, '体の中が'); f5 = frac(k, 'そして潜水艇')
    def fr(t):
        im = sea_bg(4000).copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); snow(d, t, 0.4, a=0.5); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '本当に怖いのは「空気」', Mi(70), RED, sw=3)
        cols = [(f2, '発泡スチロールのカップ'), (f3, '深海の魚'), (f5, '潜水艇')]
        for i, (ff, lab) in enumerate(cols):
            x = 330 + i * 630; on = u >= ff
            d.rounded_rectangle((x - 280, 170, x + 280, 700), 22, fill=(4, 8, 16, 230 if on else 120), outline=AQUA if on else (60, 70, 90), width=4)
            if not on: ctext(d, (x, 430), '？', Mi(120), (80, 90, 110)); continue
            if i == 0:
                q = ease((u - ff) / 0.08); cup(d, x - 110, 420, 160); ctext(d, (x - 110, 540), '海面', Fb(28), GREY)
                d.polygon([(x + 20, 420), (x - 10, 400), (x - 10, 440)], fill=GOLD)
                cup(d, x + 140, 420 + 40 * q, 160 * (1 - 0.5 * q)); ctext(d, (x + 140, 540), '深海から', Fb(28), GREY)
            elif i == 1:
                fish(d, x, 400, 170)
                if u > f4: d.rounded_rectangle((x - 150, 520, x + 150, 580), 12, fill=(10, 40, 20, 230), outline=GREEN, width=3); ctext(d, (x, 550), '中は水でいっぱい', Fo(30), GREEN)
            else:
                sphere_sub(d, x, 400, 140)
            ctext(d, (x, 650), lab, Fo(36), PALE)
        if u > f1:
            d.rounded_rectangle((260, 760, 1660, 860), 18, fill=(50, 10, 16, 235), outline=RED, width=3)
            ctext(d, (W / 2, 810), '空気の入った物は 水圧で どんどん縮む', Fo(46), PALE)
        if u > f4: ctext(d, (W / 2, 950), '水は ほとんど縮まない → 水圧に負けない', Mi(54), GOLD, sw=3)
        note(d); foot(d, '※カップが縮む実験：UCL などで紹介。深海魚の多くは空気の入った浮き袋を持たない')
        return im.convert('RGB')
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]
SWR = [('水深10m', '2気圧', '海面の2倍', '水深十', PALE), ('水深200m', '21気圧', '光がほとんど届かない', '水深二百', AQUA), ('水深1,000m', '約100気圧', '光はほぼゼロ', '水深千', AQUA),
       ('水深8,200m', '約820気圧', '魚がすめる限界（と考えられる）', '水深八千', GOLD), ('底 10,920m', '約1,070気圧', 'エビの仲間はいる', 'そして、底', RED)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; k = 'sweep'
    def fr(t):
        u = (t - t0) / dd; n = sum(1 for r in SWR if u >= frac(k, r[3]) - 0.01); dep = [10, 200, 1000, 8200, BOTTOM][n - 1] if n else 0
        im = sea_bg(dep).copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); snow(d, t, 0.5)
        ctext(d, (W / 2, 70), '深さで 何が変わる？', Mi(64), GOLD, sw=3)
        ctext(d, (760, 170), '深さ', Fo(30), GREY); ctext(d, (1130, 170), '水圧', Fo(30), GREY); ctext(d, (1560, 170), 'どうなる？', Fo(30), GREY)
        d.line((200, 200, 200, 960), fill=GREY, width=4); d.text((230, 200), '海面', font=Fb(28), fill=GREY, anchor='lm')
        for i in range(n):
            y = [260, 380, 500, 800, 930][i]; col = SWR[i][4]; d.ellipse((188, y - 12, 212, y + 12), fill=col)
        if n: figure(im, 330, [260, 380, 500, 800, 930][n - 1] - 20, 90, t * 10, bag=1 / atm(dep)); d = ImageDraw.Draw(im, 'RGBA')
        for r, (nm, p, what, ph, col) in enumerate(SWR[:n]):
            y = 260 + r * 150; last = r == 4
            d.rounded_rectangle((560, y - 58, W - 60, y + 58), 16, fill=(4, 8, 16, 230), outline=RED if last else None, width=4)
            d.text((600, y), nm, font=Fo(40), fill=PALE, anchor='lm'); ctext(d, (1130, y), p, Fo(46), col); ctext(d, (1560, y), what, Fo(34), col)
        note(d); foot(d, '※水圧は 10mで約1気圧として計算した目安（底は実測の約1,086バール）。魚の限界：ロンドン自然史博物館の記事より')
        return im.convert('RGB')
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]
def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; k = 'outro'; f1 = frac(k, '底までは'); f2 = frac(k, '体の形'); f3 = frac(k, '本当に'); f4 = frac(k, 'そして'); f5 = frac(k, 'もし、')
    def fr(t):
        u = (t - 0.5) / D['outro']; im = sea_bg(2000).copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); snow(d, t, 0.4, a=0.5)
        if u < f5:
            ctext(d, (W / 2, 110), 'まとめ', Mi(80), GOLD, sw=3); ctext(d, (W / 2, 220), 'マリアナ海溝の底に落ちたら？', Fo(52), PALE)
            for i, (ff, lab, ans, sub, col) in enumerate([(f1, '底まで一瞬', 'ウソ', '約6時間', GREEN), (f2, 'ぺちゃんこ', 'ウソ', '水はほぼ縮まない', GREEN), (f4, '何もいない', 'ウソ', 'エビの仲間がいる', GREEN)]):
                x = 420 + i * 540
                if u < ff:
                    d.rounded_rectangle((x - 240, 300, x + 240, 720), 22, fill=(4, 8, 16, 120), outline=(60, 70, 90), width=4); ctext(d, (x, 380), lab, Fo(44), GREY); ctext(d, (x, 560), '？', Mi(130), (80, 90, 110)); continue
                d.rounded_rectangle((x - 240, 300, x + 240, 720), 22, fill=(4, 8, 16, 230), outline=col, width=4)
                ctext(d, (x, 380), lab, Fo(44), PALE); ctext(d, (x, 530), ans, Mi(130), col, sw=4); ctext(d, (x, 660), sub, Fo(34), PALE)
            if u > f3: d.rounded_rectangle((W / 2 - 520, 790, W / 2 + 520, 900), 22, fill=(50, 10, 16, 235), outline=RED, width=4); ctext(d, (W / 2, 845), '本当に怖いのは「空気」', Mi(60), PALE)
        else:
            figure(im, 1560, 520, 220, 70, lamp=True); dd = ImageDraw.Draw(im, 'RGBA')
            for i in range(8): amphipod(dd, 1350 + (i % 4) * 120 + 20 * math.sin(t + i), 760 + (i // 4) * 80, 26, 0.4 * math.sin(t + i))
            ctext(dd, (700, 330), 'もし潜水艇で行けたら', Mi(70), PALE, sw=4); ctext(dd, (700, 450), '底で 何を見たい？', Mi(84), GOLD, sw=4)
            ctext(dd, (700, 570), 'コメントで教えてください', Fo(48), PALE, sw=3)
            if u > f5 + 0.15:
                dd.rounded_rectangle((700 - 500, 680, 700 + 500, 860), 24, fill=(4, 8, 16, 225), outline=GOLD, width=4)
                ctext(dd, (700, 730), '次に検証してほしい「怖いうわさ」は？', Fo(44), PALE); ctext(dd, (700, 810), 'リクエスト募集中！', Fo(44), GOLD)
        note(ImageDraw.Draw(im)); return im.convert('RGB')
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]
def icon_sub(im, t):
    d = ImageDraw.Draw(im, 'RGBA'); x = W / 2 + 40 * math.sin(t * 0.4); d.ellipse((x - 70, 830, x + 70, 970), fill=(120, 130, 145), outline=PALE, width=3); d.ellipse((x - 35, 865, x + 35, 935), fill=(150, 210, 240))
def icon_bag(im, t):
    d = ImageDraw.Draw(im, 'RGBA')
    for i, v in enumerate((1, 0.1, 0.001)):
        r = 45 * v ** (1 / 3); x = W / 2 - 260 + i * 260; d.ellipse((x - r, 960 - r, x + r, 960 + r), fill=(170, 230, 255, 220), outline=PALE, width=2)
        d.text((x + 60, 960), ['6L', '600mL', '6mL'][i], font=Fb(26), fill=GREY, anchor='lm')
def icon_amph(im, t):
    d = ImageDraw.Draw(im, 'RGBA'); k = 'res3'; ta = 0.6 + D[k] * frac(k, 'ただし'); tb = 0.6 + D[k] * frac(k, '魚は、'); tc = 0.6 + D[k] * frac(k, '体のたんぱく')
    if t < ta:
        for i in range(5): amphipod(d, W / 2 - 300 + i * 150, 940 + 10 * math.sin(t * 2 + i), 30, 0.3 * math.sin(t + i))
    elif t < tc:
        for i in range(3):
            x = W / 2 - 360 + i * 140 + 10 * math.sin(t + i); fish(d, x, 930, 45)
        u = ease((t - ta) / 0.3); d.line((W / 2 - 440, 930, W / 2 - 440 + 420 * u, 930), fill=RED, width=0)
        if t > tb:
            d.line((W / 2 + 20, 880, W / 2 + 20, 990), fill=GOLD, width=4)
            d.text((W / 2 + 50, 905), '約8,200〜8,400mより下', font=Fo(34), fill=GOLD, anchor='lm'); d.text((W / 2 + 50, 960), '魚は いない', font=Fo(40), fill=RED, anchor='lm')
            d.line((W / 2 - 420, 880, W / 2 - 20, 990), fill=RED, width=8); d.line((W / 2 - 420, 990, W / 2 - 20, 880), fill=RED, width=8)
    else:
        u = ease((t - tc) / 0.3); fish(d, W / 2 - 560, 930, 50)
        d.rounded_rectangle((W / 2 - 470, 885, W / 2 + 700, 975), 18, fill=(4, 8, 16, int(230 * u)), outline=GOLD, width=3)
        d.text((W / 2 - 440, 930), '体のたんぱく質が うまく働かなくなる（仮説）', font=Fo(40), fill=PALE, anchor='lm')
def statics_res3():
    return scene_card('res3', 'RESULT  決勝戦', [('底は', '真っ暗・水温は数℃', PALE, '真っ暗'), ('カイコウオオソコエビ', '大きいもので 約5cm', GOLD, 'カイコウ'),
                             ('魚がすめる限界', '水深 約8,200〜8,400m', AQUA, 'ただし')], f'{G}/c_res3.mp4', big='うわさ3は ウソ', bigcol=GREEN, icon=icon_amph, depth=BOTTOM,
                             sub='※National Geographic（ヨコエビ）、ロンドン自然史博物館（魚の限界は仮説。撮影された最も深い魚は8,336m）より')
def statics():
    res = {}
    res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
    res['res1'] = scene_card('res1', 'RESULT  1回戦', [('沈む速さ（仮定）', '秒速 約0.5m', PALE, '人形が'), ('底に着くまで', '約6時間', GOLD, 'すると'),
                             ('1960年 潜水艇「トリエステ」', '4時間47分', AQUA, '一九六〇')], f'{G}/c_res1.mp4', big='うわさ1は ウソ', bigcol=GREEN, icon=icon_sub, depth=1500,
                             sub='※10,920m を 秒速0.5m で割ると 約2万1,800秒＝約6時間（目安）。トリエステ：アメリカ海軍歴史遺産司令部（NHHC）の記事より')
    res['res2'] = scene_card('res2', 'RESULT  2回戦', [('人の体', '約6割が 水', AQUA, '人の体'), ('水を約1,000気圧で押すと', '約5%しか 縮まない', GREEN, '千気圧'),
                             ('6Lの空気は 底では', '約1,000分の1（約6mL）', RED, '六リットル'), ('6mL', '小さじ1杯ほど', GOLD, '小さじ')], f'{G}/c_res2.mp4', big='うわさ2も ウソ', bigcol=GREEN, icon=icon_bag, depth=BOTTOM,
                             sub='※水の縮みやすさ（圧縮率）から計算した目安。空気はボイルの法則。小さじ1杯＝5mL')
    res['res3'] = scene_card('res3', 'RESULT  決勝戦', [('底は', '真っ暗・水温は数℃', PALE, '真っ暗'), ('カイコウオオソコエビ', '大きいもので 約5cm', GOLD, 'カイコウ'),
                             ('魚がすめる限界', '水深 約8,200〜8,400m', AQUA, 'ただし')], f'{G}/c_res3.mp4', big='うわさ3は ウソ', bigcol=GREEN, icon=icon_amph, depth=BOTTOM,
                             sub='※National Geographic（ヨコエビ）、ロンドン自然史博物館（魚の限界は仮説。撮影された最も深い魚は8,336m）より')
    return res
if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static': res = statics()
    elif which == 'res3':
        old = json.load(open(f'{G}/scene_static.json')); r = statics_res3(); old['res3'] = r; json.dump(old, open(f'{G}/scene_static.json', 'w')); print('done res3'); raise SystemExit
    elif which in ('r1', 'r2', 'r3'): res[which] = globals()['scene_' + which]()
    elif which == 'still':
        os.makedirs(f'{G}/stills', exist_ok=True)
        for nm, tfn, ffn in (('r1', r1_times, r1_frame), ('r2', r2_times, r2_frame), ('r3', r3_times, r3_frame)):
            ons, tf, cues, end = tfn(); caps = caps_for(cues); print(nm, tf, end)
            for vt in (ons[0] + 0.1, tf + 0.3, cues[1][0] + 0.5, cues[2][0] + 0.5, cues[3][0] + 0.5, end - 0.1): ffn(vt, ons, tf, caps, cues).resize((960, 540)).save(f'{G}/stills/{nm}_{vt:04.1f}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
