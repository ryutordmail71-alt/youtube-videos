"""世界中の人が同時にジャンプしたら地震になる？ の場面"""
import json, math, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import hrender as R, jcontent as C
from hrender import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ORANGE, ctext, fade, ease, writer
G = '/home/claude/jmp'; D = json.load(open(f'{G}/dur.json'))
AIR = 0.495            # 30cm ジャンプの滞空時間（秒）
def frac(key, phrase): i = C.NAR[key].index(phrase); return i / len(C.NAR[key])
def onsets(key, last=4):
    """ナレーションの最後の last 個の言葉の始まり（さん・に・いち・ジャンプ）"""
    with wave.open(f'{G}/voice/{key}.wav') as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    k = int(sr * 0.02); e = np.sqrt(np.convolve(a * a, np.ones(k) / k, 'same'))[::k]; on = e > 0.02; res = []; quiet = 0
    for i, v in enumerate(on):
        if v and quiet >= 6: res.append(i * 0.02)
        quiet = 0 if v else quiet + 1
    return res[-last:]
def dark_bg(): return Image.new('RGB', (W, H), (8, 10, 20))
def sbg(dark=1.0): return ImageEnhance.Brightness(R.space_bg()).enhance(dark)
def foot(d, s): d.text((W - 24, H - 16), s, font=Fb(20), fill=(200, 200, 205), anchor='rs')
def rowbox(d, y, lab, val, col, x0=W / 2 - 600, x1=W / 2 + 600, hl=False, lf=40, vf=60, h=55):
    d.rounded_rectangle((x0, y - h, x1, y + h), 18, fill=(10, 12, 18, 230), outline=GOLD if hl else None, width=4 if hl else 0)
    d.text((x0 + 36, y), lab, font=Fo(lf), fill=PALE, anchor='lm'); d.text((x1 - 36, y), val, font=Fo(vf), fill=col, anchor='rm')
def run(out, dur, fn):
    p = writer(out)
    for f in range(int(dur * FPS)): p.stdin.write(fn(f / FPS).tobytes())
    p.stdin.close(); p.wait()


# ---- 外から見た地球（海と陸）----
_GL = {}
def land_val(x, y):
    """x, y：-1..1（円の中）。正なら陸"""
    v = 0.0
    for (bx, by, r, w) in [(-0.45, -0.35, 0.38, 1.0), (-0.2, 0.35, 0.3, 0.9), (0.4, -0.25, 0.42, 1.0), (0.55, 0.4, 0.22, 0.8), (0.0, -0.7, 0.2, 0.7), (-0.65, 0.2, 0.18, 0.6)]:
        v += w * np.exp(-((x - bx) ** 2 + (y - by) ** 2) / (r * r))
    return v + 0.18 * np.sin(x * 9 + 1) * np.cos(y * 7) - 0.55
def globe_img(rad):
    if rad in _GL: return _GL[rad]
    s = 2 * rad + 8; yy, xx = np.mgrid[0:s, 0:s]; x = (xx - s / 2) / rad; y = (yy - s / 2) / rad; r2 = x * x + y * y
    lv = land_val(x, y); img = np.zeros((s, s, 4), np.float32)
    sea = np.array((40, 95, 170), np.float32); land = np.array((80, 150, 85), np.float32)
    col = np.where((lv > 0)[..., None], land, sea); shade = (1.05 - 0.45 * np.clip(r2, 0, 1) ** 1.5 - 0.15 * (x + y))[..., None]
    img[..., :3] = np.clip(col * shade, 0, 255); img[..., 3] = (r2 <= 1) * 255
    im = Image.fromarray(img.astype(np.uint8), 'RGBA'); d = ImageDraw.Draw(im); c = s / 2
    d.ellipse((c - rad, c - rad, c + rad, c + rad), outline=(130, 190, 250), width=4); _GL[rad] = im; return im
def draw_globe(im, cx, cy, rad):
    e = globe_img(rad); im.paste(e, (int(cx - e.width / 2), int(cy - e.height / 2)), e); return ImageDraw.Draw(im, 'RGBA')
# ---- 人の絵（横から）----
PCOL = [(240, 200, 150), (150, 200, 255), (255, 170, 110), (170, 230, 170), (230, 170, 230), (240, 240, 245)]
def person(d, x, yf, s, col, crouch=0.0, arms=0.0):
    """yf：足の位置。s：身長(px)。crouch 0..1：しゃがみ。arms 0..1：手を上げる"""
    k = 1 - 0.18 * crouch; hip = yf - s * 0.47 * k; sh = yf - s * 0.8 * k; hd = yf - s * 0.9 * k; w = max(2, int(s * 0.09))
    kx = s * 0.12 * crouch
    d.line((x - s * 0.08, yf, x - s * 0.08 + kx, (yf + hip) / 2, x - s * 0.04, hip), fill=col, width=w); d.line((x + s * 0.08, yf, x + s * 0.08 + kx, (yf + hip) / 2, x + s * 0.04, hip), fill=col, width=w)
    d.line((x, hip, x, sh), fill=col, width=int(w * 1.5))
    ay = sh + s * 0.3 * (1 - arms) - s * 0.25 * arms
    d.line((x, sh + s * 0.02, x - s * 0.2, ay), fill=col, width=w); d.line((x, sh + s * 0.02, x + s * 0.2, ay), fill=col, width=w)
    r = s * 0.075; d.ellipse((x - r, hd - r, x + r, hd + r), fill=col)
def jump_h(tj):
    """跳んでからの実時間 tj（秒）→ 高さ（0〜1：最高点が1）"""
    if tj < 0 or tj > AIR: return 0.0
    u = tj / AIR; return 4 * u * (1 - u)
def pose(tj):
    """tj：跳ぶ瞬間からの実時間。しゃがみ・手の位置"""
    if -0.35 < tj < 0: return (tj + 0.35) / 0.35, 0.0
    if 0 <= tj <= AIR: return 0.0, 1.0
    if AIR < tj < AIR + 0.3: return 1 - (tj - AIR) / 0.3, 1 - (tj - AIR) / 0.3
    return 0.0, 0.0
_CROWD = {}
def crowd_layout(n, x0, x1, yb, rows, s0, seed=3):
    k = (n, x0, x1, yb, rows, s0, seed)
    if k in _CROWD: return _CROWD[k]
    rng = np.random.default_rng(seed); out = []
    for r in range(rows):
        s = s0 * (0.62 + 0.38 * (r + 1) / rows); y = yb - (rows - 1 - r) * s0 * 0.33; m = n // rows
        for i in range(m):
            x = x0 + (i + 0.5 + rng.uniform(-0.3, 0.3)) * (x1 - x0) / m
            out.append((x, y, s * rng.uniform(0.85, 1.1), PCOL[rng.integers(len(PCOL))], rng.uniform(-0.03, 0.03)))
    _CROWD[k] = out; return out
def draw_crowd(d, lay, tj, scale_px):
    for x, y, s, col, jit in lay:
        c, a = pose(tj - jit); hh = jump_h(tj - jit) * 0.3 / 1.7 * s
        person(d, x, y - hh, s, col, c, a)
# ---- 地震計 ----
def seis_val(tau, events, noise=1.0):
    v = noise * (0.5 * math.sin(tau * 23.1) + 0.3 * math.sin(tau * 41.7 + 1) + 0.2 * math.sin(tau * 67.3 + 2))
    for t0, A in events:
        q = tau - t0
        if q > 0: v += A * math.exp(-q / 0.9) * math.sin(2 * math.pi * 4.2 * q) * min(1, q / 0.08)
    return v
def seismo(d, box, t, events, label, noise=1.0, span=6.0, col=(120, 230, 150), scale=1.0):
    x0, y0, x1, y1 = box; d.rounded_rectangle(box, 16, fill=(240, 238, 228)); cy = (y0 + y1) / 2
    for gx in np.linspace(x0 + 20, x1 - 20, 13): d.line((gx, y0 + 46, gx, y1 - 14), fill=(210, 205, 190), width=1)
    d.line((x0 + 20, cy + 16, x1 - 20, cy + 16), fill=(200, 195, 180), width=1)
    pts = []; n = 360; amp = (y1 - y0 - 70) / 2
    for i in range(n):
        tau = t - span + span * i / (n - 1); v = seis_val(tau, events, noise) * scale
        pts.append((x0 + 20 + (x1 - x0 - 40) * i / (n - 1), cy + 16 - max(-1, min(1, v / 10)) * amp))
    d.line(pts, fill=(30, 30, 40), width=3); d.ellipse((pts[-1][0] - 6, pts[-1][1] - 6, pts[-1][0] + 6, pts[-1][1] + 6), fill=(200, 40, 40))
    d.text((x0 + 22, y0 + 12), label, font=Fb(26), fill=(40, 40, 50), anchor='lt')
# ---- 大きさのはしご（対数）----
LAD = [(1.7, '人の身長'), (0.3, 'ジャンプ'), (1e-4, '髪の毛の太さ'), (1e-6, '細菌'), (1e-10, '原子'), (1e-14, '原子核')]
def ladder(d, box, show_mark, t):
    x0, y0, x1, y1 = box; d.rounded_rectangle(box, 16, fill=(10, 12, 18, 225))
    d.text((x0 + 24, y0 + 18), '大きさくらべ（1目もり＝10分の1）', font=Fb(26), fill=GREY, anchor='lt')
    ya = y0 + 150; X = lambda v: x0 + 50 + (x1 - x0 - 100) * (0.3 - math.log10(v)) / 15.3
    d.line((x0 + 50, ya, x1 - 50, ya), fill=GREY, width=3)
    for e in range(0, 16): xx = X(10 ** -e); d.line((xx, ya - 8, xx, ya + 8), fill=GREY, width=2)
    for i, (v, lab) in enumerate(LAD):
        xx = X(v); d.ellipse((xx - 8, ya - 8, xx + 8, ya + 8), fill=PALE)
        yy = ya + 40 if lab in ('ジャンプ', '細菌') else ya - 40; d.text((xx, yy), lab, font=Fb(24), fill=PALE, anchor='mm')
    d.text((x0 + 50, ya + 190), '← 大きい', font=Fb(22), fill=GREY, anchor='lm'); d.text((x1 - 50, ya + 190), '小さい →', font=Fb(22), fill=GREY, anchor='rm')
    if show_mark:
        xx = X(2.1e-14); u = ease(show_mark)
        d.polygon([(xx, ya + 14), (xx - 16, ya + 50), (xx + 16, ya + 50)], fill=GOLD)
        d.rounded_rectangle((xx - 330, ya + 62, xx + 30, ya + 132), 14, fill=(40, 34, 10, int(230 * u)), outline=GOLD, width=3)
        d.text((xx - 150, ya + 97), '地球が動いた距離', font=Fo(32), fill=GOLD, anchor='mm')
def capbar(d, cap, col):
    if not cap: return
    fnt = Fo(54); tw = fnt.getlength(cap)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, 900, W / 2 + tw / 2 + 40, 990), 18, fill=(8, 10, 16, 235), outline=col, width=3); ctext(d, (W / 2, 945), cap, fnt, col)
def caps_for(cues):
    return [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in cues if k in C.CAP]
def countdown(d, t, ons, xy):
    labs = ['3', '2', '1', 'JUMP!']
    for i in range(len(ons)):
        a = ons[i]; b = ons[i + 1] if i + 1 < len(ons) else a + 1.0
        if a <= t < b:
            u = ease((t - a) / 0.2); f = BE(int(170 * (1.3 - 0.3 * u))) if i < 3 else BE(int(140 * (1.3 - 0.3 * u)))
            ctext(d, xy, labs[i], f, GOLD if i == 3 else PALE, sw=6)

# ---- 1回戦：82億人 vs 地球 ----
SLOW = 7.0
def r1_times():
    ons = [0.2 + o for o in onsets('r1a')]; tj = ons[3]; land = tj + AIR * SLOW
    cues = [(0.2, 'r1a'), (tj + 0.4, 'r1b'), (land + 0.1, 'r1c'), (land + 0.1 + D['r1c'] + 0.4, 'r1d')]
    end = cues[-1][0] + D['r1d'] + 1.4; return ons, tj, land, cues, end
def real_tj(vt, tj):
    """画面の時刻 → 跳んでからの実時間（スロー）"""
    if vt < tj: return vt - tj
    q = (vt - tj) / SLOW
    if q <= AIR + 0.3: return q
    return AIR + 0.3 + (vt - tj - (AIR + 0.3) * SLOW)
def r1_frame(vt, ons, tj, land, caps):
    im = R.space_bg().copy(); d = ImageDraw.Draw(im, 'RGBA'); rt = real_tj(vt, tj)
    d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 235)); ctext(d, (W / 2, 40), '1回戦　82億人 vs 地球', Fo(38), GOLD)
    ctext(d, (W / 2, 92), '世界中のみんなが、今いる場所で同時にジャンプ', Fb(28), PALE)
    # 左：地面と人
    d.rectangle((40, 640, 940, 860), fill=(70, 60, 50)); d.rectangle((40, 640, 940, 652), fill=(110, 150, 80))
    lay = crowd_layout(42, 70, 910, 640, 3, 150); draw_crowd(d, lay, rt, 150)
    d.text((60, 820), '世界中で 約82億人（絵は一部）', font=Fb(26), fill=PALE, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
    countdown(d, vt, ons, (490, 390))
    if 0 <= rt <= AIR + 0.3 and vt < land + 0.5:
        d.rounded_rectangle((60, 140, 330, 196), 14, fill=(160, 30, 40)); ctext(d, (195, 168), 'スロー 7分の1', Fo(30), PALE)
    hp = jump_h(rt) * 0.30; ue = hp / 0.3
    d.rounded_rectangle((360, 140, 940, 196), 14, fill=(10, 12, 18, 220)); d.text((380, 168), '人：', font=Fb(30), fill=GREY, anchor='lm'); d.text((920, 168), f'{hp * 100:4.1f} cm 上へ', font=Fo(36), fill=PALE, anchor='rm')
    d.rounded_rectangle((60, 206, 940, 262), 14, fill=(10, 12, 18, 220)); d.text((80, 234), '地球：', font=Fb(30), fill=GREY, anchor='lm')
    d.text((920, 234), f'{2.06e-14 * ue:.15f} m 下へ', font=Fo(36), fill=GOLD if ue > 0.01 else PALE, anchor='rm')
    # 右：地震計とはしご
    seismo(d, (990, 140, 1880, 440), vt, [(land, 0.25)], '地震計（世界のどこでも）', noise=0.35)
    mk = fade((vt - (tj + 0.4)) / 0.4) if vt >= tj + 0.4 else 0
    ladder(d, (990, 470, 1880, 860), mk, vt)
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, GOLD)
    d.text((W - 16, H - 6), R.NOTE, font=Fb(17), fill=(220, 220, 225), anchor='rs'); return im
def scene_r1():
    ons, tj, land, cues, end = r1_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r1.mp4', end, lambda t: r1_frame(t, ons, tj, land, caps))
    json.dump(dict(ons=ons, tj=tj, land=land), open(f'{G}/c_r1_t.json', 'w')); return end, cues

# ---- 決勝：散らばった82億人 vs 1か所に集まった82億人 ----
R2SLOW = 2.0
def r2_times():
    ons = [0.2 + o for o in onsets('r2a')]; tj = ons[3]; land = tj + AIR * R2SLOW
    cues = [(0.2, 'r2a'), (land + 0.05, 'r2b'), (land + 0.05 + D['r2b'] + 0.5, 'r2c')]; cues.append((cues[-1][0] + D['r2c'] + 0.4, 'r2d'))
    end = cues[-1][0] + D['r2d'] + 1.4; return ons, tj, land, cues, end
_DOTS = None
def spread_dots():
    global _DOTS
    if _DOTS is None:
        rng = np.random.default_rng(9); pts = []
        while len(pts) < 260:
            x, y = rng.uniform(-1, 1, 2)
            if x * x + y * y < 0.85 and land_val(x, y) > 0.05: pts.append((x, y))
        _DOTS = pts
    return _DOTS
def r2_frame(vt, ons, tj, land, caps, c2, c3):
    im = R.space_bg().copy(); d = ImageDraw.Draw(im, 'RGBA'); rt = (vt - tj) / R2SLOW if vt >= tj else vt - tj
    d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 235)); ctext(d, (W / 2, 40), '決勝戦　散らばった82億人 vs 1か所に集まった82億人', Fo(38), GOLD)
    ctext(d, (W / 2, 92), '1か所なら：1m²に2人ずつ ＝ 約4,100km²（東京都の約2つぶん）', Fb(28), PALE)
    fl = fade(1 - (vt - land) / 0.6) if vt >= land else 0
    for i in range(2):
        cx, cy, rad = 480 + i * 960, 385, 215
        d = draw_globe(im, cx, cy, rad)
        if i == 0:
            for x, y in spread_dots():
                px, py = cx + x * rad, cy + y * rad; r = 3 + 3 * fl; d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 240, 170, 230))
            ctext(d, (cx, cy + rad + 40), '散らばった82億人', Fo(40), (150, 200, 255), sw=3)
        else:
            px, py = cx - 60, cy - 90; r = 16 + 10 * fl; d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 230, 120, 255))
            if vt >= land:
                for k in range(3):
                    q = (vt - land) * 220 - k * 60
                    if 0 < q < 260: d.ellipse((px - q, py - q, px + q, py + q), outline=(255, 210, 80, int(220 * (1 - q / 260))), width=5)
            ctext(d, (cx, cy + rad + 40), '1か所に集まった82億人', Fo(40), (255, 170, 110), sw=3)
    ev0 = [(land, 0.9)]; ev1 = [(land, 7.5), (land + 0.6, 4.0)]
    seismo(d, (60, 690, 900, 880), vt, ev0, '近くの地震計', noise=0.35)
    seismo(d, (1020, 690, 1860, 880), vt, ev1, '近くの地震計', noise=0.35)
    if vt >= c2: d.rounded_rectangle((1420, 140, 1860, 220), 16, fill=(160, 30, 40)); ctext(d, (1640, 180), 'M 約4.9相当', Fo(44), PALE)
    if vt >= c3: d.rounded_rectangle((60, 140, 560, 220), 16, fill=(30, 60, 110)); ctext(d, (310, 180), '大きな町でも M3くらい', Fo(36), PALE)
    countdown(d, vt, ons, (W / 2, 420))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, GOLD)
    d.text((W - 16, H - 6), R.NOTE, font=Fb(17), fill=(220, 220, 225), anchor='rs'); return im
def scene_r2():
    ons, tj, land, cues, end = r2_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    c2 = cues[2][0]; c3 = cues[3][0]
    run(f'{G}/c_r2.mp4', end, lambda t: r2_frame(t, ons, tj, land, caps, c2, c3))
    json.dump(dict(ons=ons, tj=tj, land=land), open(f'{G}/c_r2_t.json', 'w')); return end, cues

# ---- 静的な場面 ----
def ring_people(d, cx, cy, rad, t, n=26, s=34):
    for k in range(n):
        a = math.pi * (1.1 + 0.8 * k / (n - 1)); tj = ((t * 0.9 + k * 0.13) % 1.2) - 0.35
        hh = jump_h(tj) * s * 0.35; x = cx + (rad + hh) * math.cos(a); y = cy + (rad + hh) * math.sin(a)
        # 地面の向きに合わせて立たせる（簡略：上半分だけなので縦に描く）
        person(d, x, y, s, PCOL[k % len(PCOL)], *pose(tj))
def scene_title():
    dur = 0.6 + D['intro'] + 0.6
    def fr(t):
        im = R.space_bg().copy(); draw_globe(im, 1450, 700, 400); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.5)
        ring_people(d, 1450, 700, 400, t)
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (100, 320), '世界中の82億人が', Mi(int(92 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (100, 480), '同時にジャンプ', Mi(110), GOLD, 'lm', 8)
        if t > 0.6: ctext(d, (100, 620), 'したら？', Mi(96), PALE, 'lm', 6)
        if t > 0.9: ctext(d, (106, 740), 'WHAT IF EVERYONE ON EARTH JUMPED AT ONCE?', Fb(32), (225, 225, 230), 'lm', 2)
        if t > 1.2: ctext(d, (100, 850), '地震は起きる？ 地球は動く？', Fo(52), PALE, 'lm', 3)
        d.text((W - 24, H - 16), R.NOTE, font=Fb(20), fill=(220, 220, 225), anchor='rs'); return im
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8; k = 'data'
    rows = [(frac(k, '世界の人口'), '世界の人口', '約82億人', PALE, False), (frac(k, '大人の平均'), '大人の平均体重', '約62kg', PALE, False),
            (frac(k, '子どもも'), '1人の体重（子どもも合わせて）', '平均50kg（仮定）', PALE, False), (frac(k, 'ジャンプの高さ'), 'ジャンプの高さ', '約30cm（目安）', PALE, False),
            (frac(k, '全員の重さ'), '全員の重さ', '約4億トン', ORANGE, False), (frac(k, 'いっぽう'), '地球の重さ', '約60垓（がい）トン', GOLD, True)]
    def fr(t):
        im = R.space_bg().copy(); draw_globe(im, 450, 600, 330); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 70), '数字をそろえると', Mi(68), GOLD, sw=3)
        if u > rows[4][0]:
            d.ellipse((450 - 3, 270 - 3 - 4, 450 + 3, 270 + 3 - 4), fill=GOLD); d.line((450, 255, 450, 225), fill=GOLD, width=3)
            ctext(d, (450, 200), '人類全員（点よりずっと小さい）', Fb(28), GOLD, sw=3)
        if u > rows[5][0] + 0.06: ctext(d, (450, 990), '6のあとに 0が21個', Fo(44), GOLD, sw=3)
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 200 + r * 132, lab, val, col, 860, 1880, hl, lf=34, vf=48)
        foot(d, '※人口：国連「世界人口推計2024」。大人の平均体重：Walpole ほか（2012）。地球の重さ：約5.97×10の24乗kg（NASA）')
        return im
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; bg = sbg(0.7); k = 'rule'
    RULES = [('合図', '全員が、ぴったり同時にジャンプ', frac(k, '合図')), ('着地', '着地のエネルギーは、ぜんぶ地面のゆれになる', frac(k, '着地')),
             ('最悪', 'いちばんゆれが大きくなる場合で計算', frac(k, 'これは')), ('比べ方', 'ゆれの大きさをマグニチュードに置きかえる', frac(k, 'そして'))]
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 170), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 240 + r * 170; last = r == 2
            d.rounded_rectangle((140, y, W - 140, y + 130), 18, fill=(10, 12, 18, 225), outline=GOLD if last else None, width=4 if last else 0)
            d.rounded_rectangle((170, y + 30, 370, y + 100), 14, fill=RED if last else BLUE); ctext(d, (270, y + 65), who, Fo(38), (20, 20, 24))
            d.text((410, y + 65), txt, font=Fo(48), fill=PALE, anchor='lm')
        foot(d, '※エネルギーとマグニチュード：log10(E)＝1.5M＋4.8（E：ジュール、グーテンベルグ・リヒターの式）。空想のシミュレーションです')
        return im
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]
def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None):
    dur = 0.6 + D[key] + 0.8; bg = ImageEnhance.Brightness(R.space_bg().filter(ImageFilter.GaussianBlur(2))).enhance(0.8)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.4)
        ctext(d, (W / 2, 230), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 380), big, Mi(int(110 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 700, y - 48, W / 2 + 700, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 660, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 660, y), val, font=Fo(50), fill=col, anchor='rm')
        if sub: foot(d, sub)
        return im
    run(out, dur, fr); return dur, [(0.6, key)]
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0; k = 'reveal'
    fE = frac(k, 'エネルギーで'); f2 = frac(k, '人がジャンプ'); f3 = frac(k, 'でも、重さ'); f4 = frac(k, '全員で'); f5 = frac(k, '大きく聞こえ')
    def fr(t):
        im = R.space_bg().copy(); u = (t - t0) / dd
        if u < fE:
            draw_globe(im, 1350, 600, 360); d = ImageDraw.Draw(im, 'RGBA')
            ctext(d, (W / 2, 80), 'なぜ、こんなに動かない？', Mi(66), GOLD, sw=3)
            d.ellipse((1350 - 4, 240 - 8, 1350 + 4, 240), fill=GOLD); d.text((1380, 200), '人類全員 約4億トン', font=Fb(30), fill=GOLD, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
            ctext(d, (1350, 1010), '地球 約60垓トン', Fo(40), PALE, sw=3)
            ctext(d, (460, 300), '地球は人類全員の', Fo(50), PALE, sw=3); ctext(d, (460, 420), '約15兆倍', Mi(120), GOLD, sw=5); ctext(d, (460, 520), '重い', Fo(56), PALE, sw=3)
            if u > f2:
                person(d, 300, 760, 150, PCOL[2], 0, 1); d.line((300, 780, 300, 880), fill=RED, width=10); d.polygon([(280, 870), (320, 870), (300, 910)], fill=RED)
                d.line((620, 880, 620, 780), fill=GREEN, width=10); d.polygon([(600, 790), (640, 790), (620, 750)], fill=GREEN)
                d.text((340, 900), '地面をける', font=Fb(28), fill=RED, anchor='lm'); d.text((650, 760), '人は上へ', font=Fb(28), fill=GREEN, anchor='lm')
                d.text((340, 950), '→ 地球は反対向き（下）へ押される', font=Fb(28), fill=PALE, anchor='lm')
            if u > f3:
                d.rounded_rectangle((60, 990, 900, 1050), 14, fill=(40, 34, 10, 230), outline=GOLD, width=3); ctext(d, (480, 1020), '30cm ÷ 15兆 ＝ 約0.00000000000002m', Fo(36), GOLD)
        else:
            d = ImageDraw.Draw(im, 'RGBA'); ctext(d, (W / 2, 80), 'エネルギーで見ると', Mi(66), GOLD, sw=3)
            rowbox(d, 260, '着地1回（1人）', '約150ジュール', PALE, 200, 1720, lf=40, vf=56)
            if u > f4: rowbox(d, 410, '全員（82億人）で', '約1兆2000億ジュール', ORANGE, 200, 1720, lf=40, vf=56)
            if u > f5: rowbox(d, 560, '太陽が地球に当てる光（1秒あたり）', '約17京ジュール', PALE, 200, 1720, lf=40, vf=56)
            if u > f5 + 0.05:
                rowbox(d, 760, '全員のジャンプ ＝ 太陽の光の', '約14万分の1秒ぶん', GOLD, 200, 1720, True, lf=40, vf=60, h=70)
            foot(d, '※1回の着地：50kg×9.8m/s²×0.3m＝約147J。太陽の光：1m²あたり約1,361W（太陽定数）×地球の断面積')
        if u < fE: foot(d, '※地球 約5.97×10の24乗kg ÷ 人類 約4.1×10の11乗kg ＝ 約15兆倍。跳ぶときに地球が押される距離＝30cm÷15兆')
        return im
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]
SWR = [('1人', '約150J', '−1.8', '一人なら'), ('学校（1,000人）', '約15万J', '0.2', '千人の学校'), ('スタジアム（7万人）', '約1,000万J', '1.5', '七万人'),
       ('東京（1,400万人）', '約21億J', '3.0', '東京の'), ('日本（1.2億人）', '約180億J', '3.6', '日本の'), ('世界（82億人）', '約1.2兆J', '？', None)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; bg = sbg(0.6); cx = [470, 1060, 1540]; k = 'sweep'; fst = frac(k, 'じつは'); fend = 0.97
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 70), 'みんなが1か所に集まって跳んだら？', Mi(62), GOLD, sw=3)
        for j, h in enumerate(['人数', '着地のエネルギー', 'マグニチュード相当']): ctext(d, (cx[j], 160), h, Fo(32), GREY)
        for r, (nm, e, m, ph) in enumerate(SWR):
            tr = frac(k, ph) if ph else fend
            if u < tr: continue
            y = 240 + r * 108; hl = r == 2 and u > fst
            d.rounded_rectangle((80, y - 46, W - 80, y + 46), 16, fill=(10, 12, 18, 230), outline=GOLD if hl else None, width=4)
            ctext(d, (cx[0], y), nm, Fo(38), PALE); ctext(d, (cx[1], y), e, Fo(42), PALE); ctext(d, (cx[2], y), ('M ' + m) if m != '？' else '決勝で！', Fo(50), GOLD if m == '？' else PALE)
            if hl:
                d.rounded_rectangle((1720, y - 40, 1835, y + 40), 12, fill=(160, 30, 40)); ctext(d, (1777, y - 13), '実際の', Fb(22), PALE); ctext(d, (1777, y + 15), '記録', Fb(22), PALE)
        if u > fst:
            d.rounded_rectangle((260, 900, 1660, 990), 18, fill=(40, 34, 10, 235), outline=GOLD, width=3)
            ctext(d, (W / 2, 945), '実際のスタジアム：喜んで跳ぶ観客で M1〜2くらいの記録', Fo(42), GOLD)
        foot(d, '※着地のエネルギーがすべてゆれになるとした計算（上限の目安）。記録：米シアトルのスタジアム（2013年、PNSN／ワシントン大学の地震計）')
        return im
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]
def scene_real():
    t0 = 0.5; dd = D['real']; dur = t0 + dd + 1.0; k = 'real'; f1 = frac(k, 'マグニチュード四台'); f2 = frac(k, '毎日'); f3 = frac(k, '人類全員')
    rng = np.random.default_rng(5); ang = np.sort(rng.uniform(0, 2 * math.pi, 30)); rr = rng.uniform(0.35, 0.85, 30)
    def fr(t):
        im = dark_bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 90), 'でも… M4.9は「ありふれた大きさ」', Mi(66), GOLD, sw=3)
        cx, cy, rad = 470, 590, 330
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(18, 22, 36), outline=GREY, width=4)
        for h in range(24):
            a = h / 24 * 2 * math.pi - math.pi / 2; d.line((cx + (rad - 20) * math.cos(a), cy + (rad - 20) * math.sin(a), cx + rad * math.cos(a), cy + rad * math.sin(a)), fill=GREY, width=3)
        ctext(d, (cx, cy - rad - 36), '1日（24時間）', Fo(34), PALE)
        if u > f2:
            m = int(30 * fade((u - f2) / 0.25))
            for i in range(m):
                a = ang[i] - math.pi / 2; x, y = cx + rad * rr[i] * math.cos(a), cy + rad * rr[i] * math.sin(a)
                gold = i == 17 and u > f3; r = 18 if gold else 11
                d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD if gold else (255, 110, 90))
            if u > f3: d.text((cx + 20, cy + rad + 40), '● このどれか1つが、人類全員のジャンプ', font=Fb(28), fill=GOLD, anchor='mm')
        if u > f1: rowbox(d, 330, 'M4台の地震（世界）', '1年に 約1万回', PALE, 920, 1860, lf=36, vf=52)
        if u > f2: rowbox(d, 500, '1日あたり', '約30回', ORANGE, 920, 1860, lf=36, vf=56)
        if u > f3: rowbox(d, 670, '人類全員のジャンプ', 'そのうちの1回', GOLD, 920, 1860, True, lf=36, vf=56)
        foot(d, '※USGS（アメリカ地質調査所）の世界の地震の記録：M4.0〜4.9は2000〜2008年に1年あたり約8,000〜14,000回')
        return im
    run(f'{G}/c_real.mp4', dur, fr); return dur, [(t0, 'real')]
def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; bg = sbg(0.7); k = 'outro'; f1 = frac(k, 'もし'); f2 = frac(k, 'ゆれの大きさを決める'); f3 = frac(k, 'あなたは')
    def fr(t):
        u = (t - 0.5) / D['outro']; im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA')
        if u < f2:
            ctext(d, (W / 2, 120), 'まとめ', Mi(80), GOLD, sw=3)
            rowbox(d, 330, 'マグニチュードが1上がると、エネルギーは', '約32倍', GOLD, 160, 1760, lf=40, vf=64)
            rowbox(d, 500, '82億人が1か所で跳んでも', 'M 約4.9相当', PALE, 160, 1760, lf=40, vf=60)
            if u > f1: rowbox(d, 690, 'M9をジャンプで起こすには', '人類の約170万倍の人数', RED, 160, 1760, True, lf=40, vf=56, h=70)
            foot(d, '※M9のエネルギー：log10(E)＝1.5×9＋4.8 から 約200京J。全員の着地 約1.2兆J で割ると 約170万')
        elif u < f3:
            ctext(d, (W / 2, 330), 'ゆれを決めるのは', Mi(84), PALE, sw=4); ctext(d, (W / 2, 500), '人数より「集まり方」', Mi(110), GOLD, sw=5)
            ctext(d, (W / 2, 690), '地球は、思っているより ずっと大きい', Fo(56), PALE, sw=3)
        else:
            draw_globe(im, 1570, 640, 300); d = ImageDraw.Draw(im, 'RGBA'); ring_people(d, 1570, 640, 300, t, 20, 28)
            ctext(d, (700, 330), 'あなたは何人いれば', Mi(72), PALE, sw=4); ctext(d, (700, 450), '地震を起こせると思った？', Mi(72), GOLD, sw=4)
            ctext(d, (700, 570), 'コメントで教えてください', Fo(48), PALE, sw=3)
            if u > f3 + 0.12:
                d.rounded_rectangle((700 - 500, 680, 700 + 500, 860), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (700, 730), '次に見たい「もしも」は？', Fo(50), PALE); ctext(d, (700, 810), 'リクエスト募集中！', Fo(44), GOLD)
        return im
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep()
        res['real'] = scene_real(); res['outro'] = scene_outro()
        res['res1'] = scene_card('res1', 'RESULT  1回戦', [('地球が動いた距離', '約0.00000000000002m', GOLD), ('大きさでいうと', '原子核くらい', PALE), ('着地すると', '地球も元の場所へ', PALE)], f'{G}/c_res1.mp4', big='地球の勝ち')
        res['res2'] = scene_card('res2', 'RESULT  決勝戦', [('1か所に集まった82億人', 'M 約4.9相当', GOLD), ('散らばった82億人', '大きな町でも M3くらい', PALE), ('散らばると', '1km²に平均 約55人', PALE)], f'{G}/c_res2.mp4', big='優勝は 1か所に集合',
                                  sub='※陸の面積 約1.49億km²で計算（目安）。1か所の広さ：82億人÷2人/m²＝約4,100km²')
    elif which == 'r1': res['r1'] = scene_r1()
    elif which == 'r2': res['r2'] = scene_r2()
    elif which == 'still':
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        ons, tj, land, cues, end = r1_times(); caps = caps_for(cues); print('r1', ons, tj, land, end)
        for vt in (ons[0] + 0.1, tj + 1.5, land + 0.6, land + 3.0): r1_frame(vt, ons, tj, land, caps).save(f'{G}/stills/r1_{vt:04.1f}.jpg')
        ons, tj, land, cues, end = r2_times(); caps = caps_for(cues); print('r2', ons, tj, land, end)
        for vt in (ons[1] + 0.1, land + 0.4, cues[3][0] + 1.0): r2_frame(vt, ons, tj, land, caps, cues[2][0], cues[3][0]).save(f'{G}/stills/r2_{vt:04.1f}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
