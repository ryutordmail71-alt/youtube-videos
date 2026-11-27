"""宇宙に生身で放り出されたら、何秒もつ？ の場面"""
import json, math, sys, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/air')
import arnd as R, scont as C
from arnd import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ctext, fade, ease, writer, rowbox, foot, note
G = '/home/claude/spc'; D = json.load(open(f'{G}/dur.json'))
ICE = (140, 215, 255); SKIN = (40, 52, 74)
def frac(key, phrase): i = C.NAR[key].index(phrase); return i / len(C.NAR[key])
def onsets(key, last=4):
    with wave.open(f'{G}/voice/{key}.wav') as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    k = int(sr * 0.02); e = np.sqrt(np.convolve(a * a, np.ones(k) / k, 'same'))[::k]; on = e > 0.02; res = []; quiet = 0
    for i, v in enumerate(on):
        if v and quiet >= 6: res.append(i * 0.02)
        quiet = 0 if v else quiet + 1
    return res[-last:]
# ---- 背景 ----
_BG = {}
def space_bg(w=W, h=H, seed=3, earth=True):
    k = (w, h, seed, earth)
    if k in _BG: return _BG[k]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w * 0.5) / w) ** 2 + ((yy - h * 0.3) / h) ** 2); t = np.clip(r / 0.9, 0, 1)[..., None]
    c = np.array((12, 18, 36), float) * (1 - t) + np.array((2, 3, 8), float) * t
    if earth:   # 下に地球のふち（青い大気の光）
        R0 = w * 1.6; cy = h + R0 - h * 0.17; dd = np.sqrt((xx - w * 0.5) ** 2 + (yy - cy) ** 2) - R0
        rim = np.exp(-np.maximum(dd, 0) / (h * 0.025)) * (dd > -2)
        c = c + rim[..., None] * np.array((60, 130, 230), float) * 0.9
        inside = (dd < 0)[..., None]; c = np.where(inside, np.array((6, 14, 30), float) + np.clip(-dd / (h * 0.3), 0, 1)[..., None] * -4, c)
    rng = np.random.default_rng(seed); a = np.clip(c, 0, 255).astype(np.uint8); im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 4000)):
        x, y = rng.uniform(0, w), rng.uniform(0, h); b = int(rng.uniform(80, 255)); s = rng.choice([0, 0, 0, 1])
        if earth and y > h * 0.8: continue
        d.ellipse((x - s, y - s, x + s, y + s), fill=(b, b, min(255, b + 20)))
    _BG[k] = im; return im
def bg(dark=1.0, earth=True): return ImageEnhance.Brightness(space_bg(earth=earth)).enhance(dark)
_PH = {}
def photo(w=W, h=H):
    k = (w, h)
    if k not in _PH:
        p = Image.open(f'{G}/dl/iss044e045215.jpg').convert('RGB'); s = max(w / p.width, h / p.height) * 1.12
        p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS); _PH[k] = ImageEnhance.Brightness(p).enhance(0.75)
    return _PH[k]
def photo_frame(t, w=W, h=H, dur=20.0):
    """NASA の写真をゆっくり動かす"""
    p = photo(w, h); u = t / dur; x = int((p.width - w) * (0.2 + 0.6 * u)); y = int((p.height - h) * 0.85)
    return p.crop((x, y, x + w, y + h))
def run(out, dur, fn):
    p = writer(out)
    for f in range(int(dur * FPS)): p.stdin.write(fn(f / FPS).tobytes())
    p.stdin.close(); p.wait()
# ---- 人のシルエット（光るふち） ----
_FIG = {}
def _fig_layer(s, swell, col):
    key = (int(s), round(swell, 2), col)
    if key in _FIG: return _FIG[key]
    S = int(s * 2.4); im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    th = s * 0.11 * swell; fill = SKIN + (255,)
    def limb(p, q, wdt):
        d.line((p, q), fill=fill, width=int(wdt));
        for x, y in (p, q): d.ellipse((x - wdt / 2, y - wdt / 2, x + wdt / 2, y + wdt / 2), fill=fill)
    hip = (c, c + s * 0.12); sh = (c, c - s * 0.32); hw = s * 0.15 * swell
    limb((c - hw * 0.5, hip[1]), (c - s * 0.32, c + s * 0.62), th * 1.2); limb((c + hw * 0.5, hip[1]), (c + s * 0.22, c + s * 0.7), th * 1.2)   # 脚
    limb((c - hw, sh[1] + s * 0.04), (c - s * 0.52, c - s * 0.55), th); limb((c + hw, sh[1] + s * 0.04), (c + s * 0.5, c - s * 0.1), th)          # 腕
    d.rounded_rectangle((c - hw * 1.25, sh[1] - s * 0.02, c + hw * 1.25, hip[1] + s * 0.04), int(s * 0.08 * swell), fill=fill)            # 胴
    hr = s * 0.13 * (1 + (swell - 1) * 0.6); d.ellipse((c - hr, sh[1] - s * 0.08 - hr * 2, c + hr, sh[1] - s * 0.08), fill=fill)         # 頭
    a = im.split()[3]; edge = a.filter(ImageFilter.MaxFilter(5)); rim = Image.new('RGBA', (S, S), col + (255,)); out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(rim, (0, 0), edge); gl = out.filter(ImageFilter.GaussianBlur(s * 0.06)); res = Image.alpha_composite(gl, out); res = Image.alpha_composite(res, im)
    _FIG[key] = res; return res
def figure(im, cx, cy, s, ang=0.0, swell=1.0, col=ICE):
    L = _fig_layer(s, swell, col).rotate(ang, resample=Image.BICUBIC); im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))
def bubbles(d, cx, cy, s, t, n=26, amt=1.0, col=(200, 235, 255)):
    rng = np.random.default_rng(7)
    for i in range(int(n * amt)):
        a = rng.uniform(0, 2 * math.pi); sp = rng.uniform(0.4, 1.0); ph = rng.uniform(0, 1); u = (t * 0.45 * sp + ph) % 1
        r = s * (0.35 + 0.9 * u); x = cx + r * math.cos(a); y = cy + r * math.sin(a) * 0.9; rr = 3 + 7 * (1 - u)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col + (int(220 * (1 - u)),), width=2)
def timer(d, sec, x=W - 30, y=60, col=ICE):
    d.rounded_rectangle((x - 380, y - 44, x, y + 44), 18, fill=(4, 10, 22, 235), outline=col, width=3)
    d.text((x - 360, y), '経過', font=Fb(30), fill=GREY, anchor='lm'); d.text((x - 20, y + 4), f'{sec:5.1f}', font=BE(78), fill=PALE, anchor='rm')
    d.text((x - 20, y + 4), '', font=Fb(30), fill=PALE, anchor='lm')
    d.text((x - 150, y + 30), '秒', font=Fb(1), fill=PALE)
def timer2(d, sec, x=W - 30, y=60, col=ICE):
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
            else: ctext(d, xy, labs[i], Mi(int(110 * (1.3 - 0.3 * u))), ICE, sw=6)
def thermo(d, x, y, h, temp, lo=30.0, hi=40.0, label=True):
    d.rounded_rectangle((x - 28, y - h, x + 28, y), 28, fill=(14, 18, 28), outline=PALE, width=4); d.ellipse((x - 55, y - 20, x + 55, y + 90), fill=RED, outline=PALE, width=4)
    lev = (temp - lo) / (hi - lo); top = y - h * max(0, min(1, lev)); d.rectangle((x - 14, top, x + 14, y + 20), fill=RED)
    for v in range(int(lo), int(hi) + 1, 2):
        yy = y - h * (v - lo) / (hi - lo); d.line((x + 32, yy, x + 52, yy), fill=GREY, width=3); d.text((x + 62, yy), f'{v}', font=Fb(26), fill=GREY, anchor='lm')
def gauge(d, cx, cy, r, val, vmax=1013, label='気圧'):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(8, 12, 22), outline=PALE, width=5)
    for i in range(11):
        a = math.radians(135 + 270 * i / 10); d.line((cx + r * 0.82 * math.cos(a), cy + r * 0.82 * math.sin(a), cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)), fill=GREY, width=4)
    a = math.radians(135 + 270 * max(0, min(1, val / vmax))); d.line((cx, cy, cx + r * 0.75 * math.cos(a), cy + r * 0.75 * math.sin(a)), fill=RED, width=8); d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=PALE)
    ctext(d, (cx, cy + r * 0.45), f'{val:,.0f}', Fo(int(r * 0.3)), PALE); ctext(d, (cx, cy + r * 0.72), 'hPa', Fb(int(r * 0.14)), GREY)
def lungs(d, cx, cy, s, col=(230, 140, 150), fill=(60, 24, 34)):
    d.line((cx, cy - s * 0.9, cx, cy - s * 0.35), fill=col, width=int(s * 0.1))
    for sg in (-1, 1):
        d.line((cx, cy - s * 0.35, cx + sg * s * 0.25, cy - s * 0.15), fill=col, width=int(s * 0.08))
        d.rounded_rectangle((cx + sg * s * 0.12 - (s * 0.55 if sg < 0 else 0), cy - s * 0.5, cx + sg * s * 0.12 + (s * 0.55 if sg > 0 else 0), cy + s * 0.6), int(s * 0.25), fill=fill, outline=col, width=5)
def brain(d, cx, cy, s, col=(230, 190, 220), fill=(50, 30, 50)):
    d.ellipse((cx - s, cy - s * 0.7, cx + s, cy + s * 0.7), fill=fill, outline=col, width=5); d.line((cx, cy - s * 0.65, cx, cy + s * 0.6), fill=col, width=4)
    for k in range(3):
        for sg in (-1, 1): d.arc((cx + sg * s * 0.5 - s * 0.3, cy - s * 0.5 + k * s * 0.32, cx + sg * s * 0.5 + s * 0.3, cy - s * 0.1 + k * s * 0.32), 200, 340, fill=col, width=3)
def vignette_dark(im, k):
    """視界が暗くなる（k 0〜1）"""
    if k <= 0.01: return im
    global _VG
    try: _VG
    except NameError:
        yy, xx = np.mgrid[0:H, 0:W]; _VG = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2).astype(np.float32)
    a = np.clip((_VG - (1.25 - 1.1 * k)) / 0.45, 0, 1) * min(1, 0.4 + k)
    im.paste(Image.new('RGBA', (W, H), (0, 0, 0, 255)), (0, 0), Image.fromarray((a * 255).astype(np.uint8))); return im

# ---- 試合（3回）共通 ----
def r_times(key):
    ons = [0.2 + o for o in onsets(key + 'a')]; tf = ons[3]
    cues = [(0.2, key + 'a'), (tf + 0.9, key + 'b')]; cues.append((cues[-1][0] + D[key + 'b'] + 0.7, key + 'c')); cues.append((cues[-1][0] + D[key + 'c'] + 0.8, key + 'd'))
    return ons, tf, cues
def r1_times():
    ons, tf, cues = r_times('r1'); end = cues[-1][0] + D['r1d'] + 1.6; return ons, tf, cues, end
def r1_frame(vt, ons, tf, caps):
    im = bg().convert('RGBA'); tau = vt - tf; sec = max(0.0, tau - 0.4)
    pres = 1013 if tau < 0.4 else 1013 * math.exp(-sec * 6)
    sw = 1.0 + 0.22 * ease((sec - 1.0) / 4.0) if tau > 0 else 1.0
    ang = 8 * math.sin(vt * 0.5) + (sec * 6 if tau > 0 else 0)
    if tau > 0.8: d0 = ImageDraw.Draw(im, 'RGBA'); bubbles(d0, 560, 560, 260, vt, amt=min(1.0, (sec - 0.4) / 2))
    figure(im, 560, 560, 300, ang, sw); d = ImageDraw.Draw(im, 'RGBA')
    header(d, '1回戦　うわさ1「体が破裂する」', '宇宙服なしで 宇宙ステーションの外へ（空想の設定）')
    if tau > 1.5: ctext(d, (560, 880), f'ふくらみ（イメージ）', Fb(30), GREY, sw=2)
    d.rounded_rectangle((1080, 150, 1880, 880), 20, fill=(4, 8, 16, 225))
    ctext(d, (1300, 200), 'まわりの気圧', Fo(36), PALE); gauge(d, 1300, 400, 170, pres)
    ctext(d, (1680, 200), '体の水の沸点', Fo(36), PALE)
    bp = 100 if tau < 0.4 else max(20, 100 - (100 - 20) * min(1, sec / 1.2))
    d.rounded_rectangle((1560, 250, 1800, 560), 16, fill=(10, 14, 24), outline=GREY, width=3)
    ctext(d, (1680, 350), f'{bp:.0f}℃', Fo(80), RED if bp <= 37 else PALE); ctext(d, (1680, 450), '体温 37℃', Fb(30), GREY)
    if bp <= 37: ctext(d, (1680, 510), '体温で沸騰！', Fo(36), RED)
    rows = [('水分が気体に', 'はじまる' if sec > 1.2 else '…', ICE), ('体', 'ふくらむ' if sec > 2.5 else '…', GOLD), ('皮膚', 'たえる！' if (caps and vt >= caps[-1][0]) else '…', GREEN)]
    for i, (a, b, col) in enumerate(rows):
        y = 650 + i * 76; d.text((1120, y), a, font=Fb(34), fill=GREY, anchor='lm'); d.text((1840, y), b, font=Fo(44), fill=col, anchor='rm')
    if tau >= 0.4: timer2(d, sec)
    countdown(d, vt, ons, (560, 560))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, ICE)
    note(d); foot(d, '※体の水が体温（37℃）で沸騰する気圧は 約63hPa（アームストロング限界）。ふくらみ方はイメージです', size=18); return im.convert('RGB')
def scene_r1():
    ons, tf, cues, end = r1_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r1.mp4', end, lambda t: r1_frame(t, ons, tf, caps))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r1_t.json', 'w')); return end, cues
# 2回戦：凍る？（画面1秒＝6秒）
SIM2 = 6.0; RATE = 0.22   # ℃/分（目安）
def r2_times():
    ons, tf, cues = r_times('r2'); end = max(cues[-1][0] + D['r2d'] + 1.4, tf + 0.6 + 72 / SIM2 + 1.0); return ons, tf, cues, end
def r2_frame(vt, ons, tf, caps):
    im = bg().convert('RGBA'); tau = vt - tf; sec = min(72.0, max(0.0, (tau - 0.6) * SIM2)); temp = 37.0 - RATE * sec / 60
    figure(im, 520, 540, 280, 10 * math.sin(vt * 0.4) - 15 + sec * 0.6); d = ImageDraw.Draw(im, 'RGBA')
    if tau > 0.6:   # 赤外線で逃げる熱（波線）
        for k in range(8):
            a = k * math.pi / 4 + 0.3; u = (vt * 0.5 + k * 0.13) % 1; r0 = 230 + 220 * u
            pts = [(520 + (r0 + j * 6) * math.cos(a) + 10 * math.sin(j * 0.9) * -math.sin(a), 540 + (r0 + j * 6) * math.sin(a) + 10 * math.sin(j * 0.9) * math.cos(a)) for j in range(12)]
            d.line(pts, fill=(255, 140, 90, int(200 * (1 - u))), width=4)
    header(d, '2回戦　うわさ2「一瞬で凍る」', '宇宙の温度は マイナス270℃（宇宙の背景の温度 約2.7K）')
    d.rounded_rectangle((1060, 150, 1880, 880), 20, fill=(4, 8, 16, 225)); ctext(d, (1470, 200), '体温（体全体の平均・目安）', Fo(34), PALE)
    thermo(d, 1200, 760, 470, temp, 30, 40); ctext(d, (1560, 400), f'{temp:.2f}℃', Fo(96), PALE if temp > 36.9 else ICE, sw=3)
    ctext(d, (1560, 510), f'下がった温度　{37 - temp:.2f}℃', Fb(34), GREY)
    if tau > 0.6:
        d.text((1340, 610), '逃げる熱', font=Fb(32), fill=GREY, anchor='lm'); d.text((1840, 610), '約800W', font=Fo(44), fill=(255, 150, 90), anchor='rm')
        d.text((1340, 690), '熱を運ぶ空気', font=Fb(32), fill=GREY, anchor='lm'); d.text((1840, 690), 'ない', font=Fo(44), fill=GREEN, anchor='rm')
        d.text((1340, 770), '凍るまで', font=Fb(32), fill=GREY, anchor='lm'); d.text((1840, 770), '何時間も先', font=Fo(44), fill=GOLD, anchor='rm')
    if tau >= 0.6:
        timer2(d, sec); ctext(d, (W - 210, 135), '早送り ×6', Fb(26), GOLD)
    countdown(d, vt, ons, (520, 540))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, ICE)
    note(d); foot(d, '※体重60kg・体の表面1.8m²・日かげ・皮膚33℃として、赤外線で逃げる熱を計算した目安（体の中で作る熱 約100Wを差し引き）', size=18); return im.convert('RGB')
def scene_r2():
    ons, tf, cues, end = r2_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r2.mp4', end, lambda t: r2_frame(t, ons, tf, caps))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r2_t.json', 'w')); return end, cues
# 決勝：息（実時間）
def r3_times():
    ons = [0.2 + o for o in onsets('r3a')]; tf = ons[3]; t0 = tf + 0.6
    cues = [(0.2, 'r3a'), (t0 + 5.0, 'r3b'), (t0 + 10.0, 'r3c'), (t0 + 15.0, 'r3d')]; end = t0 + 15.0 + D['r3d'] + 1.8
    return ons, tf, cues, end
def r3_frame(vt, ons, tf, caps):
    im = bg().convert('RGBA'); tau = vt - tf; sec = min(16.5, max(0.0, tau - 0.6)); o2 = 1.0 if sec < 3 else max(0.08, 1 - (sec - 3) / 13)
    figure(im, 560, 560, 290, 6 * math.sin(vt * 0.6) + sec * 2.5); d = ImageDraw.Draw(im, 'RGBA')
    header(d, '決勝戦　うわさ3「息がもたない」', '人間は 何秒で 気を失う？（実際の時間で数えます）')
    d.rounded_rectangle((1080, 150, 1880, 880), 20, fill=(4, 8, 16, 225))
    lungs(d, 1290, 400, 170); brain(d, 1690, 360, 130)
    if tau > 0.6:
        for k in range(6):   # 肺から逃げる酸素
            u = (vt * 0.7 + k / 6) % 1; x = 1290 + (k - 2.5) * 40; y = 300 - 260 * u
            d.ellipse((x - 12, y - 12, x + 12, y + 12), outline=ICE + (int(255 * (1 - u)),), width=3); d.text((x, y), 'O₂' if False else 'O', font=Fb(16), fill=ICE + (int(255 * (1 - u)),), anchor='mm')
    ctext(d, (1290, 640), '肺', Fo(36), PALE); ctext(d, (1690, 640), '脳', Fo(36), PALE)
    d.text((1120, 730), '脳に届く酸素（イメージ）', font=Fb(30), fill=GREY, anchor='lm')
    d.rectangle((1120, 770, 1840, 830), outline=GREY, width=3); col = GREEN if o2 > 0.6 else (GOLD if o2 > 0.35 else RED); d.rectangle((1126, 776, 1126 + 708 * o2, 824), fill=col)
    for s_, lab in ((5, '5秒'), (10, '10秒'), (15, '15秒')):
        if sec >= s_: ctext(d, (560, 170 + (s_ // 5 - 1) * 0), '', Fb(10), PALE)
    im = vignette_dark(im, 0 if sec < 6 else 0.72 * min(1, (sec - 6) / 10)); d = ImageDraw.Draw(im, 'RGBA')
    if tau >= 0.6: timer2(d, sec, col=RED if sec > 10 else ICE)
    countdown(d, vt, ons, (560, 560))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, ICE)
    note(d); foot(d, '※意識が続くのは 約10〜15秒（ヨーロッパ宇宙機関 ESA の専門家）。酸素のバーと画面の暗さはイメージです', size=18); return im.convert('RGB')
def scene_r3():
    ons, tf, cues, end = r3_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r3.mp4', end, lambda t: r3_frame(t, ons, tf, caps))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r3_t.json', 'w')); return end, cues

# ---- 静的な場面 ----
def scene_title():
    dur = 0.6 + D['intro'] + 0.6; k = 'intro'; f1 = frac(k, '体が'); f2 = frac(k, '一瞬'); f3 = frac(k, '映画'); f4 = frac(k, '実際')
    def fr(t):
        im = photo_frame(t, dur=dur).convert('RGBA'); u = ease(t / 0.5)
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); a = np.clip(1 - np.arange(W) / (W * 0.62), 0, 1) ** 1.5 * 200
        sh.putalpha(Image.fromarray(np.repeat(a[None, :], H, 0).astype(np.uint8))); im.alpha_composite(sh)
        figure(im, 1480 - t * 8, 470 + 20 * math.sin(t * 0.5), 260, -20 + t * 3); d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (100, 320), '宇宙に生身で', Mi(int(100 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (100, 470), '放り出されたら', Mi(110), ICE, 'lm', 8)
        if t > 0.6: ctext(d, (100, 620), '何秒もつ？', Mi(110), GOLD, 'lm', 6)
        if t > 0.9: ctext(d, (106, 720), 'HOW LONG COULD YOU SURVIVE IN SPACE WITHOUT A SUIT?', Fb(30), (225, 225, 230), 'lm', 2)
        uu = (t - 0.6) / D['intro']
        for i, (ff, lab) in enumerate([(f1, 'うわさ1　破裂する？'), (f2, 'うわさ2　一瞬で凍る？'), (f3, 'うわさ3　？？？')]):
            if uu > ff: d.rounded_rectangle((100 + i * 420, 800, 500 + i * 420, 880), 16, fill=(4, 12, 26, 230), outline=ICE, width=3); ctext(d, (300 + i * 420, 840), lab, Fo(34), PALE)
        if uu > f4: ctext(d, (100, 950), '3つの勝負で 確かめる', Fo(44), GOLD, 'lm', 3)
        d.text((W - 24, 30), '背景の写真：NASA（iss044e045215）', font=Fb(20), fill=(200, 200, 205), anchor='rm')
        note(d, size=20); return im.convert('RGB')
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8; k = 'data'
    rows = [(frac(k, '地上の空気'), '地上の気圧', '約1,013 hPa', PALE, False), (frac(k, '宇宙ステーション'), '高さ400km（宇宙ステーション）', 'ほぼ0（真空）', ICE, False),
            (frac(k, '体温と'), '37℃の水が沸騰する気圧', '約63 hPa', RED, True), (frac(k, '地上の、'), '地上とくらべると', '約16分の1', GOLD, True)]
    def fr(t):
        im = bg(earth=False).convert('RGBA'); u = (t - t0) / dd
        if t < 0.4: R.glow(im, W / 2, H / 2, 700, ICE, int(120 * (1 - t / 0.4)))
        d = ImageDraw.Draw(im, 'RGBA'); ctext(d, (W / 2, 70), '地上と宇宙の数字', Mi(68), GOLD, sw=3)
        # 左：気圧の柱
        cur = 1013 if u < rows[1][0] else (0 if u < rows[2][0] else 63)
        d.rounded_rectangle((160, 180, 700, 940), 20, fill=(4, 8, 16, 225)); ctext(d, (430, 220), '空気の重さ（気圧）', Fo(34), PALE)
        hh = 600 * cur / 1013; d.rectangle((330, 880 - 600, 530, 880), outline=GREY, width=3)
        if hh > 1: d.rectangle((334, 880 - hh, 526, 876), fill=(90, 160, 240) if cur > 100 else RED)
        lab = {1013: '地上', 0: '宇宙', 63: '体の水が沸騰'}[cur]; ctext(d, (430, 910), lab, Fo(32), PALE if cur else ICE)
        if cur == 0: ctext(d, (430, 600), 'ほぼ0', Mi(70), ICE, sw=3)
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 260 + r * 170, lab, val, col, 760, 1860, hl, lf=36, vf=54)
        note(d); foot(d, '※気圧：標準大気。37℃の水の蒸気圧 約6.3kPa＝63hPa（アームストロング限界）')
        return im.convert('RGB')
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; b = bg(0.75).convert('RGBA'); k = 'rule'
    RULES = [('設定', '宇宙服なしで ステーションの外へ', frac(k, '宇宙ステーション')), ('方法', 'どうして放り出されたかは 考えない', frac(k, 'どうして')),
             ('うわさ1', '体が 破裂する', frac(k, 'うわさ一')), ('うわさ2', '一瞬で 凍る', frac(k, 'うわさ二')), ('うわさ3', '息が もたない', frac(k, 'うわさ三'))]
    def fr(t):
        im = b.copy(); figure(im, 1650, 230, 150, t * 6); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 90), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 160), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 210 + r * 140
            d.rounded_rectangle((140, y, W - 140, y + 110), 18, fill=(4, 8, 16, 225), outline=ICE if r >= 2 else None, width=3 if r >= 2 else 0)
            d.rounded_rectangle((170, y + 22, 450, y + 88), 14, fill=(ICE if r >= 2 else BLUE)); ctext(d, (310, y + 55), who, Fo(34), (10, 14, 24))
            d.text((490, y + 55), txt, font=Fo(46), fill=PALE, anchor='lm')
        if u > frac(k, '秒数'): ctext(d, (W / 2, 950), '秒数を数えながら 確かめる', Mi(52), GOLD, sw=3)
        note(d); foot(d, '※空想のシミュレーションです。実在の事故は扱いません')
        return im.convert('RGB')
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]
def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None, icon=None):
    dur = 0.6 + D[key] + 0.8; b = ImageEnhance.Brightness(space_bg().filter(ImageFilter.GaussianBlur(2))).enhance(0.8)
    def fr(t):
        im = b.copy().convert('RGBA'); u = ease(t / 0.4)
        if icon: icon(im, t)
        d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 200), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 340), big, Mi(int(110 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col, ph) in enumerate(lines):
            if t < 0.6 + D[key] * frac(key, ph): continue
            y = 520 + r * 112
            d.rounded_rectangle((W / 2 - 800, y - 46, W / 2 + 800, y + 46), 16, fill=(4, 8, 16, 225))
            d.text((W / 2 - 760, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 760, y), val, font=Fo(46), fill=col, anchor='rm')
        if sub: foot(d, sub, size=18)
        note(d)
        return im.convert('RGB')
    run(out, dur, fr); return dur, [(0.6, key)]
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0; k = 'reveal'
    f1 = frac(k, '宇宙では'); f2 = frac(k, '息を止める'); f3 = frac(k, 'そして、もっと'); f4 = frac(k, '肺の中が'); f5 = frac(k, '酸素の少ない')
    def fr(t):
        im = bg(0.8).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '本当に怖いのは「息」', Mi(70), RED, sw=3)
        # 3つの段
        cols = [(f1, '肺の空気が 吸い出される'), (f3, '血の酸素が 外へ逃げる'), (f5, '脳に酸素が 届かない')]
        for i, (ff, lab) in enumerate(cols):
            x = 330 + i * 630; on = u >= ff
            d.rounded_rectangle((x - 280, 170, x + 280, 700), 22, fill=(4, 8, 16, 230 if on else 120), outline=ICE if on else (60, 70, 90), width=4)
            if not on: ctext(d, (x, 430), '？', Mi(120), (80, 90, 110)); continue
            if i == 0:
                lungs(d, x, 420, 150)
                for j in range(5):
                    uu = (t * 0.8 + j / 5) % 1; yy = 250 - 60 * uu; d.line((x - 60 + j * 30, 300 - 80 * uu, x - 60 + j * 30, 270 - 80 * uu), fill=ICE + (int(255 * (1 - uu)),), width=5)
            elif i == 1:
                for j in range(7):
                    xx = x - 200 + j * 66; d.ellipse((xx - 26, 400 - 16, xx + 26, 400 + 16), fill=(170, 40, 50))
                for j in range(6):
                    uu = (t * 0.6 + j / 6) % 1; xx = x - 180 + j * 70; yy = 380 - 150 * uu; d.ellipse((xx - 12, yy - 12, xx + 12, yy + 12), outline=ICE + (int(255 * (1 - uu)),), width=3)
                ctext(d, (x, 500), '酸素 O', Fo(34), ICE)
            else:
                brain(d, x, 420, 150);
                if u > f5 + 0.05: d.line((x - 140, 300, x + 140, 540), fill=RED, width=10)
            ctext(d, (x, 640), lab, Fo(36), PALE)
        if u > f2:
            d.rounded_rectangle((260, 760, 1660, 860), 18, fill=(50, 10, 16, 235), outline=RED, width=3)
            ctext(d, (W / 2, 810), '息を止めると 肺が傷つく → 息は止めない', Fo(46), PALE)
        if u > f5 + 0.1: ctext(d, (W / 2, 950), '→ 気を失う', Mi(64), GOLD, sw=3)
        note(d); foot(d, '※Scientific American「Survival in Space Unprotected Is Possible--Briefly」、Live Science（ESA の専門家の話）より')
        return im.convert('RGB')
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]
SWR = [('富士山の頂上', '3,776m', '約634hPa', '地上の約6割', '富士山', GREEN), ('エベレストの頂上', '8,849m', '約314hPa', '約3分の1', 'エベレスト', GREEN),
       ('旅客機が飛ぶ高さ', '10,000m', '約264hPa', '約4分の1', '旅客機', GOLD), ('アームストロング限界', '約19km', '約63hPa', '体の水が37℃で沸騰', 'そして、高さ', RED)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; b = bg(0.7).convert('RGBA'); k = 'sweep'
    def fr(t):
        im = b.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 70), 'どの高さから 危なくなる？', Mi(64), GOLD, sw=3)
        n = sum(1 for r in SWR if u >= frac(k, r[4]))
        # 左：高さの目盛り（対数っぽく）
        d.line((200, 180, 200, 960), fill=GREY, width=4)
        ys = [880, 720, 620, 600, 300]
        for i, (nm, alt, p, rat, ph, col) in enumerate(SWR[:n]):
            y = [850, 700, 610, 330][i]; d.ellipse((188, y - 12, 212, y + 12), fill=col); d.text((230, y), alt, font=Fb(30), fill=col, anchor='lm')
        d.text((230, 950), '地上 0m', font=Fb(28), fill=GREY, anchor='lm')
        if n: figure(im, 330, [850, 700, 610, 330][n - 1] - 90, 90, t * 10); d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (920, 170), '場所', Fo(30), GREY); ctext(d, (1380, 170), '気圧', Fo(30), GREY); ctext(d, (1680, 170), '地上とくらべると', Fo(30), GREY)
        for r, (nm, alt, p, rat, ph, col) in enumerate(SWR[:n]):
            y = 270 + r * 150; last = r == 3
            d.rounded_rectangle((560, y - 58, W - 60, y + 58), 16, fill=(4, 8, 16, 230), outline=RED if last else None, width=4)
            d.text((600, y), nm, font=Fo(42), fill=PALE, anchor='lm'); ctext(d, (1380, y), p, Fo(48), col); ctext(d, (1680, y), rat, Fo(38 if last else 46), col)
        if u > frac(k, 'アームストロング') - 0.03:
            d.rounded_rectangle((560, 860, W - 60, 950), 18, fill=(50, 10, 16, 235), outline=RED, width=3)
            ctext(d, (1210, 905), 'ここより上は 宇宙服がないと 体の水が沸騰する', Fo(40), PALE)
        note(d); foot(d, '※気圧は国際標準大気で計算した目安。アームストロング限界は約18〜19km、約6.3kPa')
        return im.convert('RGB')
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]
def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; b = bg(0.75).convert('RGBA'); k = 'outro'; f1 = frac(k, '体は'); f2 = frac(k, '一瞬で'); f3 = frac(k, '本当に'); f4 = frac(k, '動けるのは'); f5 = frac(k, 'もし、あなた')
    def fr(t):
        u = (t - 0.5) / D['outro']; im = b.copy(); d = ImageDraw.Draw(im, 'RGBA')
        if u < f4:
            ctext(d, (W / 2, 120), 'まとめ', Mi(80), GOLD, sw=3); ctext(d, (W / 2, 240), '宇宙に生身で放り出されたら？', Fo(52), PALE)
            for i, (ff, lab, ans, col) in enumerate([(f1, '体が破裂する', 'ウソ', GREEN), (f2, '一瞬で凍る', 'ウソ', GREEN), (f3, '息がもたない', '本当', RED)]):
                x = 420 + i * 540
                if u < ff:
                    d.rounded_rectangle((x - 240, 340, x + 240, 760), 22, fill=(4, 8, 16, 120), outline=(60, 70, 90), width=4); ctext(d, (x, 430), lab, Fo(44), GREY); ctext(d, (x, 600), '？', Mi(130), (80, 90, 110)); continue
                d.rounded_rectangle((x - 240, 340, x + 240, 760), 22, fill=(4, 8, 16, 230), outline=col, width=4)
                ctext(d, (x, 430), lab, Fo(44), PALE); ctext(d, (x, 600), ans, Mi(130), col, sw=4)
        elif u < f5:
            ctext(d, (W / 2, 130), '分かれ目は 2つの数字', Mi(64), GOLD, sw=3)
            x0, x1, y = 200, 1720, 520; d.line((x0, y, x1, y), fill=GREY, width=6)
            for sv, lab, col in ((0, '0秒', PALE), (15, '約15秒\n意識がもつ', ICE), (90, '約90秒\n助かる分かれ目', GOLD), (120, '2分', RED)):
                x = x0 + (x1 - x0) * sv / 120; d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=col)
                for j, ln in enumerate(lab.split('\n')): ctext(d, (x, y + 70 + j * 60), ln, Fo(44 if j == 0 else 32), col)
            m = min(120, (u - f4) / (f5 - f4) * 140); xm = x0 + (x1 - x0) * m / 120; d.polygon([(xm, y - 30), (xm - 18, y - 60), (xm + 18, y - 60)], fill=RED)
        else:
            figure(im, 1560, 520, 260, t * 5); dd = ImageDraw.Draw(im, 'RGBA')
            ctext(dd, (700, 330), 'もし放り出されたら', Mi(70), PALE, sw=4); ctext(dd, (700, 450), 'その15秒で 何をする？', Mi(80), GOLD, sw=4)
            ctext(dd, (700, 570), 'コメントで教えてください', Fo(48), PALE, sw=3)
            if u > f5 + 0.08:
                dd.rounded_rectangle((700 - 500, 680, 700 + 500, 860), 24, fill=(4, 8, 16, 225), outline=GOLD, width=4)
                ctext(dd, (700, 730), '次に検証してほしい「怖いうわさ」は？', Fo(44), PALE); ctext(dd, (700, 810), 'リクエスト募集中！', Fo(44), GOLD)
        note(ImageDraw.Draw(im)); return im.convert('RGB')
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]
def icon_fig(sw=1.0):
    def f(im, t): figure(im, W / 2, 880, 120, t * 8, sw)
    return f
def statics():
    res = {}
    res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
    res['res1'] = scene_card('res1', 'RESULT  1回戦', [('63hPaより低い気圧', '体の水分が 体温のまま気体に', ICE, '気圧が'), ('体', 'ふくらむ', GOLD, 'そのため'),
                             ('人間の皮膚', '丈夫で 破裂しない', GREEN, 'でも、人間'), ('血管の中の血', '血圧で 沸騰しないとされる', PALE, '血管')], f'{G}/c_res1.mp4', big='うわさ1は ウソ', bigcol=GREEN,
                             sub='※Wikipedia「Armstrong limit」、Live Science（ESA の専門家の話）、Scientific American より')
    res['res2'] = scene_card('res2', 'RESULT  2回戦', [('真空', '熱を運ぶ空気がない（魔法瓶と同じ）', ICE, '真空には'), ('逃げる熱（日かげ・60kg）', '約800W（赤外線）', (255, 150, 90), '体重'),
                             ('体温が下がる速さ', '1分で 約0.2℃', GOLD, '体温が'), ('凍るのは', '何時間も 先', GREEN, '凍るのは')], f'{G}/c_res2.mp4', big='うわさ2も ウソ', bigcol=GREEN,
                             sub='※赤外線の放射（シュテファン＝ボルツマンの法則）で計算した目安。体の比熱 約3.5kJ/(kg・℃)。実際は皮膚の表面から先に冷えます')
    res['res3'] = scene_card('res3', 'RESULT  決勝戦', [('意識がもつのは', '約10〜15秒', RED, 'ヨーロッパ'), ('動物実験の記録', '約90秒以内に戻れば 助かった', GOLD, '昔の'),
                             ('2分をこえると', '助からないことが 多い', RED, '二分')], f'{G}/c_res3.mp4', big='うわさ3は 本当', bigcol=RED,
                             sub='※Live Science（ESA の専門家）、Scientific American（1960年代の動物実験の記録）より。目安です')
    return res
if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static': res = statics()
    elif which in ('r1', 'r2', 'r3'): res[which] = globals()['scene_' + which]()
    elif which == 'still':
        os.makedirs(f'{G}/stills', exist_ok=True)
        for nm, tfn, ffn in (('r1', r1_times, r1_frame), ('r2', r2_times, r2_frame), ('r3', r3_times, r3_frame)):
            ons, tf, cues, end = tfn(); caps = caps_for(cues); print(nm, tf, end)
            for vt in (ons[0] + 0.1, tf + 0.3, tf + 3.0, tf + 8.0, end - 0.1): ffn(vt, ons, tf, caps).resize((960, 540)).save(f'{G}/stills/{nm}_{vt:04.1f}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
