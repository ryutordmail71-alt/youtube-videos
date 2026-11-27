"""月が今の半分の距離まで近づいたら？ の場面"""
import json, math, sys, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/air')
import arnd as R, ncont as C
from arnd import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ctext, fade, ease, writer, rowbox, foot, note
G = '/home/claude/mon'; D = json.load(open(f'{G}/dur.json'))
MOON = (228, 224, 212); SEA = (70, 150, 235); SILV = (190, 205, 225)
D0 = 384400.0            # 今の距離 km
RM = 3474.0 / 2          # 月の半径 km
ROCHE = 18400.0          # ロッシュ限界（流体、地球の中心から km）
ROCHE_R = 9500.0         # ロッシュ限界（剛体）
def tide(d): return (D0 / d) ** 3
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
# ---- 宇宙の背景（星空） ----
_ST = np.random.default_rng(7).uniform(0, 1, (260, 4))
_SKY = {}
def sky(w=W, h=H, warm=0.0):
    k = (w, h, round(warm, 2))
    if k in _SKY: return _SKY[k]
    yy = np.linspace(0, 1, h)[:, None, None]; xx = np.linspace(0, 1, w)[None, :, None]
    top = np.array((4, 6, 18), float); bot = np.array((10, 20, 46), float) * (1 - warm) + np.array((30, 22, 40), float) * warm
    c = top * (1 - yy) + bot * yy + 0 * xx
    c = c + np.exp(-(((xx - 0.5) ** 2) / 0.18 + ((yy - 0.9) ** 2) / 0.05)) * np.array((16, 26, 48))
    im = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
    for x0, y0, s, ph in _ST:
        x = x0 * w; y = y0 * h * 0.82; r = 0.6 + 1.9 * s ** 2; a = int(70 + 170 * s)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(235, 240, 255, a))
    _SKY[k] = im; return im
_MOONTEX = {}
def moon_img(px):
    """月の絵（クレーターと海）。px＝直径"""
    px = max(8, int(px))
    if px in _MOONTEX: return _MOONTEX[px]
    S = px * 2; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = S / 2; r = px / 2
    d.ellipse((c - r, c - r, c + r, c + r), fill=MOON + (255,))
    rng = np.random.default_rng(3)
    for mx, my, ms in ((-0.30, -0.28, 0.30), (0.10, -0.36, 0.22), (0.28, -0.06, 0.26), (-0.12, 0.02, 0.34), (-0.40, 0.18, 0.18), (0.16, 0.26, 0.20)):
        rr = ms * r; d.ellipse((c + mx * r - rr, c + my * r - rr, c + mx * r + rr, c + my * r + rr), fill=(186, 184, 178, 255))
    for i in range(46):
        a = rng.uniform(0, 2 * math.pi); q = math.sqrt(rng.uniform(0, 1)) * 0.93; rr = r * rng.uniform(0.015, 0.075)
        x = c + math.cos(a) * q * r; y = c + math.sin(a) * q * r
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(206, 202, 194, 255), outline=(244, 242, 236, 180))
    # 右下をほんの少し暗く（立体感）
    sh = Image.new('RGBA', (S, S), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.ellipse((c - r * 0.2, c - r * 0.1, c + r * 1.5, c + r * 1.5), fill=(2, 4, 12, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, px * 0.09)))
    mask = Image.new('L', (S, S), 0); ImageDraw.Draw(mask).ellipse((c - r, c - r, c + r, c + r), fill=255)
    im.paste(Image.alpha_composite(im.crop((0, 0, S, S)), sh), (0, 0), mask)
    _MOONTEX[px] = im; return im
def draw_moon(im, cx, cy, px, glow_a=70, squash=1.0):
    m = moon_img(px)
    if squash != 1.0: m = m.resize((int(m.width * squash), m.height), Image.LANCZOS)
    R.glow(im, cx, cy, px * 0.72, (190, 210, 255), glow_a)
    im.alpha_composite(m, (int(cx - m.width / 2), int(cy - m.height / 2)))
def earth_limb(im, cy=1010, h=260, w=W):
    """下にふくらむ地球のふち"""
    l = Image.new('RGBA', (w, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l)
    d.ellipse((-w * 0.6, cy, w * 1.6, cy + h * 7), fill=(28, 72, 140, 255))
    d.ellipse((-w * 0.6, cy + 10, w * 1.6, cy + h * 7), fill=(16, 48, 104, 255))
    gl = Image.new('RGBA', (w, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((-w * 0.6, cy - 26, w * 1.6, cy + h * 7), fill=(120, 190, 255, 150))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(26))); im.alpha_composite(l)
_PH = {}
def photo(w=W, h=H, zoom=1.0, cx=0.5, cy=0.5):
    k = (w, h, zoom, cx, cy)
    if k not in _PH:
        p = Image.open(f'{G}/dl/iss072e618284.jpg').convert('RGB'); s = max(w / p.width, h / p.height) * zoom
        p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS); _PH[k] = ImageEnhance.Brightness(p).enhance(1.0)
    return _PH[k]
def photo_frame(t, w=W, h=H, dur=20.0, zoom=1.15):
    p = photo(w, h, zoom); u = t / dur
    x = int((p.width - w) * (0.5 + 0.08 * u)); y = int((p.height - h) * (0.55 - 0.12 * u))
    return p.crop((x, y, x + w, y + h))
# ---- 計器 ----
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
            else: ctext(d, xy, labs[i], Mi(int(110 * (1.3 - 0.3 * u))), CYAN, sw=6)
def dist_bar(d, x0, x1, y, dist, col=CYAN):
    """横の距離メーター（0〜38万4,400km）"""
    d.rounded_rectangle((x0 - 6, y - 22, x1 + 6, y + 22), 20, fill=(8, 12, 22), outline=GREY, width=3)
    xx = x1 - (x1 - x0) * (1 - min(1, dist / D0)); xx = max(x0, min(x1, xx))
    d.rounded_rectangle((x0, y - 14, xx, y + 14), 12, fill=col)
    d.polygon([(xx, y - 28), (xx - 14, y - 50), (xx + 14, y - 50)], fill=GOLD)
    d.text((x0, y + 42), '地球', font=Fb(26), fill=GREY, anchor='lm'); d.text((x1, y + 42), '38万4,400km', font=Fb(26), fill=GREY, anchor='rm')
def bigval(d, xy, val, unit, col=PALE, s=140):
    d.text((xy[0], xy[1]), val, font=BE(s), fill=col, anchor='rm'); d.text((xy[0] + 16, xy[1] + s * 0.17), unit, font=Fo(int(s * 0.42)), fill=col, anchor='lm')
def tide_panel(d, x0, y0, x1, y1, mult, lab='潮の満ち引き'):
    """海の高さの棒（今の何倍か）"""
    d.rounded_rectangle((x0, y0, x1, y1), 20, fill=(4, 8, 16, 225))
    ctext(d, ((x0 + x1) / 2, y0 + 44), lab, Fo(36), PALE)
    base = y1 - 70; top = y0 + 110; h0 = 28
    for i, (nm, m) in enumerate((('いま', 1.0), ('この距離', mult))):
        cx = x0 + 150 + i * 240; hh = min(base - top, h0 * m)
        d.rectangle((cx - 72, base - hh, cx + 72, base), fill=SEA if i == 0 else (90, 180, 255))
        for k in range(3):
            yy = base - hh + 6 + k * 9
            if yy < base: d.line((cx - 72, yy, cx + 72, yy), fill=(170, 220, 255, 160), width=2)
        ctext(d, (cx, base + 34), nm, Fb(30), GREY)
        ctext(d, (cx, base - hh - 36), f'{m:,.0f}倍' if m >= 2 else '1倍', Fo(40), GOLD if i else PALE)
def gauge_x(d, cx, cy, r, val, vmax, unit='倍', col=GOLD):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(8, 12, 22), outline=PALE, width=5)
    for i in range(11):
        a = math.radians(135 + 270 * i / 10); d.line((cx + r * 0.82 * math.cos(a), cy + r * 0.82 * math.sin(a), cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)), fill=GREY, width=4)
    a = math.radians(135 + 270 * max(0, min(1, val / vmax))); d.line((cx, cy, cx + r * 0.75 * math.cos(a), cy + r * 0.75 * math.sin(a)), fill=RED, width=8)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=PALE)
    ctext(d, (cx, cy + r * 0.45), f'{val:,.1f}' if val < 10 else f'{val:,.0f}', Fo(int(r * 0.32)), PALE); ctext(d, (cx, cy + r * 0.72), unit, Fb(int(r * 0.16)), GREY)
def coin_scale(d, cx, cy, s, deg, lab=True):
    """五円玉の穴と月の見かけの大きさ（0.5度＝穴にすっぽり）"""
    d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=(190, 160, 70), outline=(230, 205, 120), width=4)
    hole = s * 0.33; d.ellipse((cx - hole, cy - hole, cx + hole, cy + hole), fill=(6, 10, 20))
    mr = hole * (deg / 0.52) * 0.92
    d.ellipse((cx - mr, cy - mr, cx + mr, cy + mr), fill=MOON)
    if lab: ctext(d, (cx, cy + s + 34), '腕をのばした五円玉の穴', Fb(26), GREY)
# ---- 1回戦：見かけの大きさ ----
def r_times(key):
    ons = [0.2 + o for o in onsets(key + 'a')]; tf = ons[3]
    cues = [(0.2, key + 'a'), (tf + 0.85, key + 'b')]; cues.append((cues[-1][0] + D[key + 'b'] + 0.85, key + 'c')); cues.append((cues[-1][0] + D[key + 'c'] + 0.85, key + 'd'))
    return ons, tf, cues
def interp(x, xs, ys): return float(np.interp(x, xs, ys))
def r1_times():
    ons, tf, cues = r_times('r1'); end = cues[-1][0] + D['r1d'] + 1.0; return ons, tf, cues, end
def r1_frame(vt, ons, tf, caps, cues):
    t0 = tf + 0.6; tb, tc, td = cues[1][0], cues[2][0], cues[3][0]
    dist = D0 if vt < t0 else interp(vt, [t0, tb, tc, td, td + 10], [D0, 300000, 250000, D0 / 2, D0 / 2])
    im = sky().copy().convert('RGBA'); earth_limb(im)
    px = 150 * (D0 / dist)
    draw_moon(im, 620, 470, px, glow_a=int(60 + 50 * (D0 / dist - 1)))
    d = ImageDraw.Draw(im, 'RGBA'); header(d, '1回戦　うわさ1「空が月でいっぱいになる」', '月を ゆっくり半分の距離まで近づける（早送り）')
    d.rounded_rectangle((1180, 150, 1880, 880), 20, fill=(4, 8, 16, 225))
    ctext(d, (1530, 215), '距離', Fo(36), GREY); bigval(d, (1700, 320), f'{dist / 10000:,.1f}', '万km', PALE, 130)
    rows = [('今の距離の', f'{dist / D0 * 100:,.0f}%', CYAN), ('見かけの幅', f'{D0 / dist:.2f}倍', GOLD), ('見かけの面積', f'{(D0 / dist) ** 2:.2f}倍', GOLD)]
    for i, (a, b, col) in enumerate(rows):
        y = 470 + i * 110; d.text((1230, y), a, font=Fb(32), fill=GREY, anchor='lm'); d.text((1840, y), b, font=Fo(46), fill=col, anchor='rm')
    dist_bar(d, 1240, 1830, 820, dist)
    if vt >= t0: ctext(d, (W - 230, 135), '早送り', Fb(26), GOLD)
    countdown(d, vt, ons, (620, 470))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, CYAN)
    note(d); foot(d, '※月の見かけの大きさは 距離に反比例（幅）。絵は見やすさのため大きさを強調しています', size=18); return im.convert('RGB')
def scene_r1():
    ons, tf, cues, end = r1_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r1.mp4', end, lambda t: r1_frame(t, ons, tf, caps, cues))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r1_t.json', 'w')); return end, cues
# ---- 2回戦：潮の満ち引き ----
def r2_times():
    ons, tf, cues = r_times('r2'); end = cues[-1][0] + D['r2d'] + 1.1; return ons, tf, cues, end
def r2_frame(vt, ons, tf, caps, cues):
    t0 = tf + 0.6; tb, tc, td = cues[1][0], cues[2][0], cues[3][0]
    dist = D0 if vt < t0 else interp(vt, [t0, tb, tc, td, td + 10], [D0, 300000, 250000, D0 / 2, D0 / 2])
    mult = tide(dist)
    im = sky(warm=0.15).copy().convert('RGBA')
    draw_moon(im, 1500, 300, 110 * (D0 / dist) * 0.8, glow_a=70)
    d = ImageDraw.Draw(im, 'RGBA')
    # 海の断面（左）
    x0, x1 = 90, 1000; base = 800
    d.rounded_rectangle((x0 - 20, 440, x1 + 20, 890), 20, fill=(4, 8, 16, 200))
    ctext(d, ((x0 + x1) / 2, 490), '海の高さ（断面）', Fo(36), PALE)
    hh = min(300, 26 * mult)
    wave = [(x, base - hh * (0.55 + 0.45 * math.cos((x - x0) / (x1 - x0) * math.pi * 2 + vt * 0.8))) for x in range(x0, x1 + 1, 10)]
    d.polygon([(x0, base + 50)] + wave + [(x1, base + 50)], fill=(40, 110, 200))
    d.line(wave, fill=(150, 215, 255), width=4)
    d.rectangle((x0, base + 50, x1, 880), fill=(50, 44, 38))
    d.line((x0, base, x1, base), fill=(120, 130, 150, 200), width=2); d.text((x0 + 12, base + 18), 'ふだんの海面', font=Fb(26), fill=GREY, anchor='lm')
    bh = min(300, 26 * mult)
    d.line((x1 - 120, base, x1 - 120, base - bh), fill=GOLD, width=5)
    ctext(d, (x1 - 120, base - bh - 34), f'×{mult:,.1f}' if mult < 10 else f'×{mult:,.0f}', Fo(46), GOLD, sw=3)
    header(d, '2回戦　うわさ2「潮の満ち引きが8倍」', '月を半分の距離まで近づけ、海の高さをはかる（早送り）')
    d.rounded_rectangle((1060, 400, 1880, 890), 20, fill=(4, 8, 16, 225))
    ctext(d, (1240, 460), '距離', Fo(32), GREY); ctext(d, (1240, 530), f'{dist / 10000:,.1f}万km', Fo(50), PALE)
    ctext(d, (1660, 460), '潮を起こす力', Fo(32), GREY)
    gauge_x(d, 1660, 640, 130, mult, 9.0)
    d.text((1100, 820), 'ファンディ湾 最大16m なら', font=Fb(32), fill=GREY, anchor='lm')
    d.text((1840, 820), f'約{16 * mult:,.0f}m', font=Fo(50), fill=RED if mult > 4 else PALE, anchor='rm')
    if vt >= t0: ctext(d, (W - 230, 135), '早送り', Fb(26), GOLD)
    countdown(d, vt, ons, (540, 660))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, CYAN, y=975)
    note(d); foot(d, '※潮を起こす力は距離の3乗に反比例（目安）。実際の潮の高さは湾の形にも大きく左右されます', size=18); return im.convert('RGB')
def scene_r2():
    ons, tf, cues, end = r2_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r2.mp4', end, lambda t: r2_frame(t, ons, tf, caps, cues))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r2_t.json', 'w')); return end, cues
# ---- 決勝：月は壊れる？ ----
def r3_times():
    ons, tf, cues = r_times('r3'); end = cues[-1][0] + D['r3d'] + 1.4; return ons, tf, cues, end
def r3_frame(vt, ons, tf, caps, cues):
    t0 = tf + 0.6; tb, tc, td = cues[1][0], cues[2][0], cues[3][0]
    dist = D0 / 2 if vt < t0 else interp(vt, [t0, tb, tc, td, td + 10], [D0 / 2, 100000, 50000, ROCHE, ROCHE])
    broken = vt > td + 0.5
    im = sky().copy().convert('RGBA'); earth_limb(im, cy=1040)
    px = min(520, 150 * (D0 / dist))
    squash = 1.0 if dist > 60000 else 1.0 + 0.3 * (60000 - dist) / 42000
    if not broken:
        draw_moon(im, 640, 520, px, glow_a=70, squash=squash)
    else:
        q = min(1, (vt - td - 0.5) / 1.2); rng = np.random.default_rng(13); d2 = ImageDraw.Draw(im, 'RGBA')
        R.glow(im, 640, 520, px * 0.8, (190, 210, 255), 60); d2 = ImageDraw.Draw(im, 'RGBA')
        for i in range(90):
            a = rng.uniform(0, 2 * math.pi); rr = px / 2 * math.sqrt(rng.uniform(0, 1))
            x = 640 + math.cos(a) * (rr + q * 420 * (0.4 + rng.uniform(0, 1))); y = 520 + math.sin(a) * (rr + q * 90) * (1 - q * 0.55)
            s = px * rng.uniform(0.012, 0.045)
            d2.ellipse((x - s, y - s, x + s, y + s), fill=(214, 210, 200, 255))
    d = ImageDraw.Draw(im, 'RGBA'); header(d, '決勝戦　うわさ3「月はこなごなに壊れる」', '半分の距離から さらに近づける（早送り）')
    d.rounded_rectangle((1180, 150, 1880, 900), 20, fill=(4, 8, 16, 225))
    ctext(d, (1530, 215), '距離', Fo(36), GREY); bigval(d, (1700, 320), f'{dist / 10000:,.1f}', '万km', PALE if dist > ROCHE * 1.05 else RED, 130)
    rows = [('潮を起こす力', f'{tide(dist):,.0f}倍' if tide(dist) >= 10 else f'{tide(dist):,.1f}倍', GOLD),
            ('ロッシュ限界まで', f'{max(0, dist - ROCHE) / 10000:,.1f}万km', CYAN if dist > ROCHE * 1.05 else RED),
            ('月の形', '丸い' if dist > 60000 else ('少しゆがむ' if dist > ROCHE * 1.05 else 'こわれる'), PALE if dist > 60000 else (GOLD if dist > ROCHE * 1.05 else RED))]
    for i, (a, b, col) in enumerate(rows):
        y = 470 + i * 110; d.text((1230, y), a, font=Fb(32), fill=GREY, anchor='lm'); d.text((1840, y), b, font=Fo(44), fill=col, anchor='rm')
    dist_bar(d, 1240, 1830, 830, dist, col=RED if dist <= ROCHE * 1.05 else CYAN)
    if dist <= ROCHE * 1.05:
        d.rounded_rectangle((1210, 870, 1850, 940), 16, fill=(60, 10, 16, 235), outline=RED, width=3) if False else None
        ctext(d, (640, 880), 'ロッシュ限界 約1万8,000km', Fo(46), RED, sw=4)
    if vt >= t0: ctext(d, (W - 230, 135), '早送り', Fb(26), GOLD)
    countdown(d, vt, ons, (640, 520))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, CYAN, y=975)
    note(d); foot(d, '※ロッシュ限界は地球の中心からの距離。やわらかい天体で約1万8,400km、かたい天体で約9,500km（計算した目安）', size=18); return im.convert('RGB')
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
    dur = 0.5 + D['intro'] + 0.4; k = 'intro'
    f1 = frac(k, '空は'); f2 = frac(k, '潮の満ち引きは'); f3 = frac(k, 'そして、月は'); f4 = frac(k, '実際')
    def fr(t):
        im = photo_frame(t, dur=dur).convert('RGBA'); u = ease(t / 0.5); shade_left(im)
        d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (100, 320), '月が今の半分の', Mi(int(96 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (100, 470), '距離に近づいたら', Mi(118), CYAN, 'lm', 8)
        if t > 0.6: ctext(d, (100, 620), 'どうなる？', Mi(120), GOLD, 'lm', 6)
        if t > 0.9: ctext(d, (106, 720), 'WHAT IF THE MOON CAME TWICE AS CLOSE?', Fb(28), (225, 225, 230), 'lm', 2)
        uu = (t - 0.5) / D['intro']
        for i, (ff, lab) in enumerate([(f1, 'うわさ　空がいっぱい？'), (f2, 'うわさ　潮は何倍？'), (f3, 'うわさ　月は壊れる？')]):
            if uu > ff: d.rounded_rectangle((100 + i * 420, 800, 500 + i * 420, 880), 16, fill=(4, 12, 26, 230), outline=CYAN, width=3); ctext(d, (300 + i * 420, 840), lab, Fo(34), PALE)
        if uu > f4: ctext(d, (100, 950), '3つの勝負で 確かめる', Fo(44), GOLD, 'lm', 3)
        d.text((W - 24, 30), '背景の写真：NASA（iss072e618284）', font=Fb(22), fill=(225, 225, 230), anchor='rm')
        note(d, size=20); return im.convert('RGB')
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.5, 'intro')]
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.5; k = 'data'
    rows = [(frac(k, '地球から月'), '地球から月までの距離（平均）', '約38万4,400km', PALE, False), (frac(k, '地球を、'), '地球を ならべると', '約9周半ぶん', CYAN, False),
            (frac(k, '月の直径'), '月の直径', '約3,474km', PALE, False), (frac(k, 'そして月は'), 'いま 月は', '1年に約3.8cm 遠ざかる', GOLD, False),
            (frac(k, 'この月を'), 'この月を 半分の距離へ', '19万2,200km', RED, True)]
    def fr(t):
        im = sky().copy().convert('RGBA'); u = (t - t0) / dd
        d = ImageDraw.Draw(im, 'RGBA'); ctext(d, (W / 2, 70), '月の数字', Mi(68), GOLD, sw=3)
        # 左：地球と月の距離の図
        d.rounded_rectangle((100, 150, 700, 960), 20, fill=(4, 8, 16, 210))
        ex, ey = 230, 560; d.ellipse((ex - 70, ey - 70, ex + 70, ey + 70), fill=(30, 90, 170), outline=(120, 190, 255), width=3)
        ctext(d, (ex, ey + 100), '地球', Fb(28), GREY)
        half = u >= rows[4][0]
        mx = 600 if not half else 420
        d.line((ex + 80, ey, mx - 40, ey), fill=GREY, width=3)
        draw_moon(im, mx, ey, 56 if not half else 72, glow_a=40); d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (mx, ey + 90), '月', Fb(28), GREY)
        ctext(d, ((ex + mx) / 2, ey - 60), '38万4,400km' if not half else '19万2,200km', Fo(32), GOLD if half else PALE, sw=3)
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 240 + r * 150, lab, val, col, 760, 1860, hl, lf=34, vf=50)
        note(d); foot(d, '※距離は平均（軌道はだ円なので 約36万〜40万kmの間で変わります）')
        return im.convert('RGB')
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]
def scene_rule():
    dur = 0.5 + D['rule'] + 0.6; k = 'rule'
    RULES = [('近づける', '月を 半分の距離（19万2,200km）へ', frac(k, '月を、')), ('そのまま', '月の重さ・大きさ、地球の自転は そのまま', frac(k, '月の重さ')),
             ('うわさ1', '空が 月でいっぱいになる', frac(k, 'うわさ一')), ('うわさ2', '潮の満ち引きが 8倍になる', frac(k, 'うわさ二')), ('うわさ3', '月は こなごなに壊れる', frac(k, 'うわさ三'))]
    def fr(t):
        im = sky().copy().convert('RGBA')
        draw_moon(im, 1700, 250, 150, glow_a=60)
        d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 90), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 160), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 210 + r * 140
            d.rounded_rectangle((140, y, W - 340, y + 110), 18, fill=(4, 8, 16, 225), outline=CYAN if r >= 2 else None, width=3 if r >= 2 else 0)
            d.rounded_rectangle((170, y + 22, 480, y + 88), 14, fill=(CYAN if r >= 2 else BLUE)); ctext(d, (325, y + 55), who, Fo(34), (10, 14, 24))
            d.text((520, y + 55), txt, font=Fo(42), fill=PALE, anchor='lm')
        if u > frac(k, '三つの'): ctext(d, (W / 2, 950), '変えるのは 距離だけ', Mi(52), GOLD, sw=3)
        note(d); foot(d, '※空想のシミュレーションです。実際に月を動かすことはできません')
        return im.convert('RGB')
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]
def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None, icon=None, warm=0.0):
    dur = 0.5 + D[key] + 0.5; b = sky(warm=warm)
    def fr(t):
        im = b.copy().convert('RGBA'); u = ease(t / 0.4)
        if icon: icon(im, t)
        d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 190), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 320), big, Mi(int(110 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col, ph) in enumerate(lines):
            if t < 0.5 + D[key] * frac(key, ph): continue
            y = 470 + r * 108
            d.rounded_rectangle((W / 2 - 820, y - 46, W / 2 + 820, y + 46), 16, fill=(4, 8, 16, 225))
            d.text((W / 2 - 780, y), lab, font=Fb(34), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 780, y), val, font=Fo(44), fill=col, anchor='rm')
        if sub: foot(d, sub, size=18)
        note(d)
        return im.convert('RGB')
    run(out, dur, fr); return dur, [(0.5, key)]
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 0.8; k = 'reveal'
    f1 = frac(k, '距離が半分'); f2 = frac(k, 'それなら'); f3 = frac(k, 'じつは'); f4 = frac(k, 'この差が'); f5 = frac(k, 'ちなみに')
    def fr(t):
        im = sky(warm=0.1).copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), 'なぜ 4倍ではなく 8倍？', Mi(70), GOLD, sw=3)
        # 地球の両側にかかる力の差
        ex, ey = 700, 520
        d.ellipse((ex - 190, ey - 190, ex + 190, ey + 190), fill=(28, 80, 150), outline=(120, 190, 255), width=4)
        ctext(d, (ex, ey), '地球', Fo(44), PALE)
        draw_moon(im, 1430, ey, 150, glow_a=50); d = ImageDraw.Draw(im, 'RGBA')
        if u > f3:
            for i, (xx, ln, lab, col) in enumerate(((ex - 190, 90, '遠い側：弱い', BLUE), (ex + 190, 190, '近い側：強い', GOLD))):
                d.line((xx, ey, xx + ln, ey), fill=col, width=12)
                d.polygon([(xx + ln + 26, ey), (xx + ln, ey - 18), (xx + ln, ey + 18)], fill=col)
                ctext(d, (xx + ln / 2, ey - 56 + i * 112), lab, Fo(32), col, sw=3)
        if u > f4:
            d.rounded_rectangle((W / 2 - 760, 790, W / 2 + 760, 890), 18, fill=(10, 30, 60, 235), outline=CYAN, width=3)
            ctext(d, (W / 2, 840), '潮を起こすのは「引っぱる力の差」→ 距離の3乗で効く', Fo(46), PALE)
        if u > f1:
            d.rounded_rectangle((60, 190, 540, 420), 20, fill=(4, 8, 16, 230), outline=GREY, width=3)
            ctext(d, (300, 240), '引っぱる力そのもの', Fo(32), GREY); ctext(d, (300, 320), '距離の2乗 → 4倍', Fo(44), BLUE)
            ctext(d, (300, 385), '（潮は これではない）' if u > f3 else '', Fb(26), GREY)
        if u > f2:
            d.rounded_rectangle((1400, 190, 1880, 420), 20, fill=(4, 8, 16, 230), outline=GOLD, width=3)
            ctext(d, (1640, 240), '引っぱられ方の差', Fo(32), GREY); ctext(d, (1640, 320), '距離の3乗 → 8倍', Fo(44), GOLD)
        if u > f5: ctext(d, (W / 2, 950), '月が体を引っぱる力は 地球の重力の約30万分の1 → 体重は変わらない', Fo(40), PALE, sw=3)
        note(d); foot(d, '※月の引力による加速度は 地表で約0.000033m/s²（地球の重力の約30万分の1）。半分の距離でも約7万分の1')
        return im.convert('RGB')
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]
SWR = [('いまの距離', '38万4,400km', '1倍', 'では', PALE), ('半分', '19万2,200km', '8倍', '半分の、', GOLD), ('4分の1', '9万6,100km', '64倍', '四分の一', GOLD),
       ('10分の1', '3万8,440km', '約1,000倍', '十分の一', RED), ('ロッシュ限界', '約1万8,000km', '月が壊れる', 'そして、およそ', RED)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 0.9; k = 'sweep'
    def fr(t):
        u = (t - t0) / dd; n = sum(1 for r in SWR if u >= frac(k, r[3]) - 0.01)
        im = sky(warm=0.05 * n).copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 70), 'もっと近づけると？', Mi(64), GOLD, sw=3)
        ex, ey = 230, 560
        d.ellipse((ex - 60, ey - 60, ex + 60, ey + 60), fill=(30, 90, 170), outline=(120, 190, 255), width=3); ctext(d, (ex, ey + 92), '地球', Fb(26), GREY)
        if n:
            dists = [D0, D0 / 2, D0 / 4, D0 / 10, ROCHE][n - 1]
            mx = ex + 60 + (430 - 60) * (dists / D0) ** 0.45 + 40
            draw_moon(im, mx, ey, 48 + 40 * (1 - (dists / D0) ** 0.4), glow_a=40); d = ImageDraw.Draw(im, 'RGBA')
            if n == 5:
                for i in range(26):
                    a = i / 26 * 2 * math.pi; rr = 46 + 10 * math.sin(i * 1.7)
                    d.ellipse((mx + math.cos(a) * rr - 5, ey + math.sin(a) * rr * 0.35 - 5, mx + math.cos(a) * rr + 5, ey + math.sin(a) * rr * 0.35 + 5), fill=(214, 210, 200))
        ctext(d, (900, 170), '距離', Fo(30), GREY); ctext(d, (1360, 170), '月まで', Fo(30), GREY); ctext(d, (1730, 170), '潮を起こす力', Fo(30), GREY)
        for r, (nm, km, mult, ph, col) in enumerate(SWR[:n]):
            y = 250 + r * 150; last = r == 4
            d.rounded_rectangle((640, y - 58, W - 60, y + 58), 16, fill=(4, 8, 16, 230), outline=RED if last else None, width=4)
            d.text((690, y), nm, font=Fo(40), fill=PALE, anchor='lm'); ctext(d, (1360, y), km, Fo(42), col); ctext(d, (1730, y), mult, Fo(46), col)
        note(d); foot(d, '※潮を起こす力は距離の3乗に反比例として計算した目安。ロッシュ限界は地球の中心からの距離')
        return im.convert('RGB')
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]
def scene_outro():
    dur = 0.5 + D['outro'] + 1.2; k = 'outro'
    f1 = frac(k, '空は'); f2 = frac(k, '潮の満ち引きは'); f3 = frac(k, 'そして、月は'); f4 = frac(k, '満月から'); f5 = frac(k, 'もし、本当に')
    f6 = frac(k, 'ひと月が'); f7 = frac(k, 'カレンダー')
    def fr(t):
        u = (t - 0.5) / D['outro']; im = sky().copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
        if u < f5:
            ctext(d, (W / 2, 100), 'まとめ', Mi(76), GOLD, sw=3); ctext(d, (W / 2, 200), '月が今の半分の距離に近づいたら？', Fo(50), PALE)
            for i, (ff, lab, ans, sub, col) in enumerate([(f1, '空がいっぱい', 'ウソ', '幅2倍・面積4倍', GREEN), (f2, '潮が8倍', 'ホント', '距離の3乗で効く', GOLD), (f3, '月が壊れる', 'ウソ', '限界はずっと内側', GREEN)]):
                x = 420 + i * 540
                if u < ff:
                    d.rounded_rectangle((x - 240, 280, x + 240, 700), 22, fill=(4, 8, 16, 120), outline=(60, 70, 90), width=4); ctext(d, (x, 360), lab, Fo(44), GREY); ctext(d, (x, 540), '？', Mi(130), (80, 90, 110)); continue
                d.rounded_rectangle((x - 240, 280, x + 240, 700), 22, fill=(4, 8, 16, 230), outline=col, width=4)
                ctext(d, (x, 360), lab, Fo(44), PALE); ctext(d, (x, 510), ans, Mi(120), col, sw=4); ctext(d, (x, 650), sub, Fo(32), PALE)
            if u > f4:
                d.rounded_rectangle((W / 2 - 560, 760, W / 2 + 560, 860), 22, fill=(20, 30, 60, 235), outline=CYAN, width=4)
                days = 29.5 - 19.5 * min(1, max(0, (u - f4) / max(0.02, f6 - f4)))
                ctext(d, (W / 2, 810), f'ひと月（満月から満月）は 約29.5日 → 約{days:.1f}日', Fo(44), PALE if days > 11 else GOLD)
            if u > f6:   # 新しいカレンダー（10日ぶん）が1日ずつ入る
                n = int(1 + 9 * min(1, (u - f6) / max(0.02, f7 - f6 + 0.04)))
                for i in range(10):
                    x = W / 2 - 450 + (i % 10) * 100; y = 920
                    on = i < n
                    d.rounded_rectangle((x - 44, y - 42, x + 44, y + 42), 12, fill=(10, 20, 44, 235) if on else (6, 8, 16, 120), outline=GOLD if on else (60, 70, 90), width=3)
                    if on: ctext(d, (x, y), str(i + 1), Fo(42), PALE)
                ctext(d, (W / 2 - 610, 920), '新しい ひと月', Fb(32), GOLD)
            if u > f7: ctext(d, (W / 2, 1002), 'カレンダーも 作り直し', Fb(36), CYAN)
        else:
            draw_moon(im, 1500 + 10 * math.sin(t * 0.35), 420 + 16 * math.sin(t * 0.5), 300, glow_a=int(75 + 12 * math.sin(t * 0.9))); dd = ImageDraw.Draw(im, 'RGBA')
            ctext(dd, (680, 330), 'もし月が近づいたら', Mi(68), PALE, sw=4); ctext(dd, (680, 450), '何を 見てみたい？', Mi(84), GOLD, sw=4)
            ctext(dd, (680, 570), 'コメントで教えてください', Fo(46), PALE, sw=3)
            if u > f5 + 0.15:
                dd.rounded_rectangle((180, 680, 1180, 860), 24, fill=(4, 8, 16, 225), outline=GOLD, width=4)
                ctext(dd, (680, 730), '次に検証してほしい「もしも」は？', Fo(44), PALE); ctext(dd, (680, 810), 'リクエスト募集中！', Fo(44), GOLD)
        note(ImageDraw.Draw(im)); return im.convert('RGB')
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]
def icon_coin(im, t):
    k = 'res1'; ta = 0.5 + D[k] * frac(k, '腕をのばして')
    d = ImageDraw.Draw(im, 'RGBA')
    if t > ta:
        coin_scale(d, W / 2 - 300, 880, 90, 0.52, lab=False); ctext(d, (W / 2 - 300, 772), 'いま（0.5度）', Fb(30), GREY)
        if t > 0.5 + D[k] * frac(k, '半分の距離'):
            coin_scale(d, W / 2 + 300, 880, 90, 1.04, lab=False); ctext(d, (W / 2 + 300, 772), '半分の距離（1度）', Fb(30), GOLD)
        ctext(d, (W / 2, 1000), '腕をのばした五円玉の穴とくらべると', Fb(28), GREY)
def icon_tide(im, t):
    d = ImageDraw.Draw(im, 'RGBA'); k = 'res2'; ta = 0.5 + D[k] * frac(k, '世界で')
    if t > ta:
        base = 960
        for i, (nm, m) in enumerate((('いま 約16m', 1), ('8倍 約128m', 8))):
            x = W / 2 - 330 + i * 660; hh = 14 * m
            d.rectangle((x - 90, base - hh, x + 90, base), fill=SEA if i == 0 else (90, 180, 255))
            ctext(d, (x, base - hh - 30), nm, Fo(32), PALE if i == 0 else GOLD)
def icon_roche(im, t):
    d = ImageDraw.Draw(im, 'RGBA'); k = 'res3'; ta = 0.5 + D[k] * frac(k, 'でも、もし')
    if t > ta:
        cx, cy = W / 2, 900
        d.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill=(30, 90, 170), outline=(120, 190, 255), width=3)
        for i in range(40):
            a = i / 40 * 2 * math.pi; rr = 150 + 14 * math.sin(i * 2.3)
            d.ellipse((cx + math.cos(a) * rr - 5, cy + math.sin(a) * rr * 0.3 - 5, cx + math.cos(a) * rr + 5, cy + math.sin(a) * rr * 0.3 + 5), fill=(214, 210, 200))
        ctext(d, (cx + 330, cy), '土星のような輪に', Fo(36), GOLD, sw=3)
def statics():
    res = {}
    res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
    res['res1'] = scene_card('res1', 'RESULT  1回戦', [('満月の見かけの大きさ（いま）', '約0.5度', PALE, '満月の'), ('半分の距離では', '約1度（幅2倍）', GOLD, '半分の距離'),
                             ('見かけの面積・明るさ', '約4倍', CYAN, '幅が二倍')], f'{G}/c_res1.mp4', big='うわさ1は ウソ', bigcol=GREEN, icon=icon_coin,
                             sub='※見かけの大きさ（視直径）は 約0.52度。腕をのばして持った五円玉の穴（約0.9度）に入る大きさ')
    res['res2'] = scene_card('res2', 'RESULT  2回戦', [('潮を起こす力', '距離の3乗に反比例', PALE, '潮の満ち引きを'), ('距離が2分の1なら', '2×2×2＝8倍', GOLD, '距離が二分の一'),
                             ('ファンディ湾 最大 約16m', '単純計算で 約128m', RED, '世界で'), ('30階だてのビルくらいの高さ', '1日に2回 上下する', CYAN, '三十階')], f'{G}/c_res2.mp4',
                             big='うわさ2は ホント', bigcol=GOLD, icon=icon_tide, warm=0.12,
                             sub='※ファンディ湾の潮差は世界最大級（最大約16m）。8倍は単純計算の目安で、実際は湾の形にも大きく左右されます')
    res['res3'] = scene_card('res3', 'RESULT  決勝戦', [('ロッシュ限界（地球の中心から）', '約9,500〜1万8,400km', PALE, '地球と月'), ('半分の距離 19万2,200kmは', 'その10倍以上 外側', GREEN, '半分の距離'),
                             ('もっと内側に入ったら', 'ばらばらになり 輪になる', RED, 'でも、もし')], f'{G}/c_res3.mp4', big='うわさ3も ウソ', bigcol=GREEN, icon=icon_roche,
                             sub='※ロッシュ限界は 地球と月の密度から計算した目安（やわらかい天体 約1万8,400km／かたい天体 約9,500km）')
    return res
if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static': res = statics()
    elif which in ('r1', 'r2', 'r3'): res[which] = globals()['scene_' + which]()
    elif which == 'still':
        os.makedirs(f'{G}/stills', exist_ok=True)
        for nm, tfn, ffn in (('r1', r1_times, r1_frame), ('r2', r2_times, r2_frame), ('r3', r3_times, r3_frame)):
            ons, tf, cues, end = tfn(); caps = caps_for(cues); print(nm, round(tf, 2), round(end, 2))
            for vt in (ons[0] + 0.1, tf + 0.3, cues[1][0] + 0.5, cues[2][0] + 0.5, cues[3][0] + 0.5, end - 0.2): ffn(vt, ons, tf, caps, cues).resize((960, 540)).save(f'{G}/stills/{nm}_{vt:04.1f}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
