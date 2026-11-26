"""AIが人類に反乱したら、人類は何日で負ける？ の場面"""
import json, math, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, acont as C
from arnd import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ORANGE, ctext, fade, ease, writer, rowbox, foot, note
G = '/home/claude/air'; D = json.load(open(f'{G}/dur.json'))
AIR = (255, 70, 70)
def frac(key, phrase): i = C.NAR[key].index(phrase); return i / len(C.NAR[key])
def onsets(key, last=4):
    with wave.open(f'{G}/voice/{key}.wav') as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    k = int(sr * 0.02); e = np.sqrt(np.convolve(a * a, np.ones(k) / k, 'same'))[::k]; on = e > 0.02; res = []; quiet = 0
    for i, v in enumerate(on):
        if v and quiet >= 6: res.append(i * 0.02)
        quiet = 0 if v else quiet + 1
    return res[-last:]
_BG = {}
def dark_bg(w=W, h=H, tint=(40, 14, 22)):
    k = (w, h, tint)
    if k in _BG: return _BG[k]
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx - w * 0.6) / w) ** 2 + ((yy - h * 0.35) / h) ** 2)
    t = np.clip(r / 0.9, 0, 1)[..., None]; c = np.array(tint, float) * (1 - t) + np.array((5, 5, 10), float) * t
    im = Image.fromarray(c.astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
    for x in range(0, w, 60): d.line((x, 0, x, h), fill=(255, 120, 120, 10), width=1)
    for y in range(0, h, 60): d.line((0, y, w, y), fill=(255, 120, 120, 10), width=1)
    _BG[k] = im; return im
def bg(dark=1.0): return ImageEnhance.Brightness(dark_bg()).enhance(dark)
def run(out, dur, fn):
    p = writer(out)
    for f in range(int(dur * FPS)): p.stdin.write(fn(f / FPS).tobytes())
    p.stdin.close(); p.wait()
def capbar(d, cap, col, y=960):
    if not cap: return
    fnt = Fo(54); tw = fnt.getlength(cap)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, y - 45, W / 2 + tw / 2 + 40, y + 45), 18, fill=(8, 10, 16, 235), outline=col, width=3); ctext(d, (W / 2, y), cap, fnt, col)
def caps_for(cues): return [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in cues if k in C.CAP]
def countdown(d, t, ons, xy):
    labs = ['3', '2', '1', 'スタート！']
    for i in range(len(ons)):
        a = ons[i]; b = ons[i + 1] if i + 1 < len(ons) else a + 1.0
        if a <= t < b:
            u = ease((t - a) / 0.2)
            if i < 3: ctext(d, xy, labs[i], BE(int(170 * (1.3 - 0.3 * u))), PALE, sw=6)
            else: ctext(d, xy, labs[i], Mi(int(110 * (1.3 - 0.3 * u))), GOLD, sw=6)
def header(d, a, b):
    d.rectangle((0, 0, W, 120), fill=(6, 6, 12, 235)); ctext(d, (W / 2, 40), a, Fo(38), GOLD); ctext(d, (W / 2, 92), b, Fb(28), PALE)
# ---- 絵の部品 ----
def ai_eye(im, cx, cy, r, t=0.0, power=1.0):
    """AI の目（赤く光るリング）。power 0〜1 で明るさ"""
    if power > 0.02:
        R.glow(im, cx, cy, r * 1.3, AIR, int(150 * power))
    d = ImageDraw.Draw(im, 'RGBA'); p = power
    col = tuple(int(c * (0.25 + 0.75 * p)) for c in AIR)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(14, 10, 14), outline=(120, 120, 130), width=max(3, int(r * 0.06)))
    for k, rr in enumerate((0.78, 0.58)):
        a0 = (t * (40 if k == 0 else -60)) % 360
        for s in range(6):
            d.arc((cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr), a0 + s * 60, a0 + s * 60 + 38, fill=col, width=max(2, int(r * 0.07)))
    rc = r * 0.3; d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), fill=col)
    rc2 = r * 0.12; d.ellipse((cx - rc2, cy - rc2, cx + rc2, cy + rc2), fill=(255, 230, 230) if p > 0.3 else (60, 50, 50))
    return d
def robot_arm(d, x, y, s, t=0.0, col=(200, 205, 215), ph=0.0, moving=True, bolts=True):
    """床に固定された産業ロボットのアーム（x：土台の中心、y：床）"""
    a1 = -1.15 + (0.25 * math.sin(t * 2.2 + ph) if moving else 0); a2 = 0.9 + (0.35 * math.sin(t * 2.9 + ph * 1.3) if moving else 0)
    d.rectangle((x - s * 0.32, y - s * 0.14, x + s * 0.32, y), fill=(70, 74, 86), outline=col, width=3)
    if bolts:
        for bx in (x - s * 0.24, x + s * 0.24): d.ellipse((bx - s * 0.04, y - s * 0.09, bx + s * 0.04, y - s * 0.01), fill=GOLD)
    j0 = (x, y - s * 0.2); d.ellipse((j0[0] - s * 0.1, j0[1] - s * 0.1, j0[0] + s * 0.1, j0[1] + s * 0.1), fill=col)
    j1 = (j0[0] + s * 0.6 * math.cos(a1), j0[1] + s * 0.6 * math.sin(a1)); d.line((j0, j1), fill=col, width=max(4, int(s * 0.13)))
    j2 = (j1[0] + s * 0.5 * math.cos(a1 + a2), j1[1] + s * 0.5 * math.sin(a1 + a2)); d.line((j1, j2), fill=col, width=max(3, int(s * 0.1)))
    d.ellipse((j1[0] - s * 0.07, j1[1] - s * 0.07, j1[0] + s * 0.07, j1[1] + s * 0.07), fill=(150, 150, 160))
    an = a1 + a2
    for sg in (-1, 1):
        q = (j2[0] + s * 0.12 * math.cos(an + sg * 0.5), j2[1] + s * 0.12 * math.sin(an + sg * 0.5)); d.line((j2, q), fill=col, width=max(2, int(s * 0.05)))
def walker(d, x, y, s, t=0.0, power=1.0, col=(210, 214, 224)):
    """歩くロボット（シルエット）"""
    sw = math.sin(t * 6) * 0.35 * (1 if power > 0 else 0)
    hip = (x, y - s * 0.45)
    for sg in (-1, 1):
        a = math.pi / 2 + sg * sw; d.line((hip, (hip[0] + s * 0.45 * math.cos(a), hip[1] + s * 0.45 * math.sin(a))), fill=col, width=max(3, int(s * 0.09)))
    d.rounded_rectangle((x - s * 0.18, y - s * 0.85, x + s * 0.18, y - s * 0.42), max(2, int(s * 0.05)), fill=(60, 64, 76), outline=col, width=3)
    d.rounded_rectangle((x - s * 0.13, y - s * 1.08, x + s * 0.13, y - s * 0.88), max(2, int(s * 0.04)), fill=(40, 42, 52), outline=col, width=3)
    ec = tuple(int(c * (0.2 + 0.8 * power)) for c in AIR); d.rectangle((x - s * 0.09, y - s * 1.0, x + s * 0.09, y - s * 0.95), fill=ec)
    for sg in (-1, 1):
        a = math.pi / 2 - sg * sw; sh = (x + sg * s * 0.2, y - s * 0.8)
        d.line((sh, (sh[0] + s * 0.32 * math.cos(a), sh[1] + s * 0.32 * math.sin(a))), fill=col, width=max(2, int(s * 0.07)))
def phone(d, x, y, s, state=0.0):
    """スマホ。state 0＝ふつう、1＝乗っ取られた（赤）"""
    scr = (60, 140, 230) if state < 0.5 else (230, 40, 50)
    d.rounded_rectangle((x - s * 0.28, y - s * 0.5, x + s * 0.28, y + s * 0.5), max(2, int(s * 0.08)), fill=(30, 30, 36), outline=(180, 180, 190), width=2)
    d.rectangle((x - s * 0.22, y - s * 0.4, x + s * 0.22, y + s * 0.38), fill=scr)
def battery(d, x, y, w, h, lev, label=''):
    d.rounded_rectangle((x, y, x + w, y + h), 14, outline=PALE, width=6); d.rectangle((x + w, y + h * 0.3, x + w + 22, y + h * 0.7), fill=PALE)
    col = GREEN if lev > 0.5 else (GOLD if lev > 0.2 else RED)
    if lev > 0.005: d.rectangle((x + 12, y + 12, x + 12 + (w - 24) * lev, y + h - 12), fill=col)
    if label: ctext(d, (x + w / 2, y + h / 2), label, Fo(int(h * 0.42)), PALE, sw=4)
def city(d, x0, x1, yb, lit=1.0, seed=3):
    rng = np.random.default_rng(seed); x = x0
    while x < x1 - 40:
        w = rng.integers(70, 140); h = rng.integers(160, 420); x2 = min(x1, x + w)
        d.rectangle((x, yb - h, x2, yb), fill=(32, 34, 46), outline=(90, 95, 115), width=2)
        for yy in np.arange(yb - h + 16, yb - 20, 30):
            for xx in np.arange(x + 10, x2 - 18, 24):
                if rng.random() < 0.65 * lit: d.rectangle((xx, yy, xx + 12, yy + 14), fill=(255, 220, 140))
        x = x2 + rng.integers(6, 20)
def gpu_chip(d, cx, cy, s, broken=False):
    d.rounded_rectangle((cx - s, cy - s * 0.62, cx + s, cy + s * 0.62), int(s * 0.08), fill=(30, 70, 50), outline=(150, 200, 160), width=4)
    d.rectangle((cx - s * 0.45, cy - s * 0.38, cx + s * 0.45, cy + s * 0.38), fill=(20, 22, 26), outline=(200, 200, 210), width=3)
    for i in range(9):
        xx = cx - s * 0.8 + i * s * 0.2; d.rectangle((xx, cy + s * 0.62, xx + s * 0.1, cy + s * 0.78), fill=GOLD)
    ctext(d, (cx, cy), 'GPU', BE(int(s * 0.42)), PALE)
    if broken:
        d.line((cx - s * 0.6, cy - s * 0.5, cx + s * 0.6, cy + s * 0.5), fill=RED, width=10); d.line((cx - s * 0.6, cy + s * 0.5, cx + s * 0.6, cy - s * 0.5), fill=RED, width=10)
def plug(d, cx, cy, s, col=GOLD):
    d.rounded_rectangle((cx - s * 0.4, cy - s * 0.3, cx + s * 0.4, cy + s * 0.4), int(s * 0.1), fill=col)
    for sg in (-1, 1): d.rectangle((cx + sg * s * 0.18 - s * 0.06, cy - s * 0.7, cx + sg * s * 0.18 + s * 0.06, cy - s * 0.3), fill=col)
    d.line((cx, cy + s * 0.4, cx, cy + s * 0.9), fill=col, width=int(s * 0.12))
def wrench(d, cx, cy, s, col=CYAN):
    d.line((cx - s * 0.6, cy + s * 0.6, cx + s * 0.25, cy - s * 0.25), fill=col, width=int(s * 0.22))
    d.ellipse((cx + s * 0.05, cy - s * 0.75, cx + s * 0.75, cy - s * 0.05), fill=col); d.ellipse((cx + s * 0.3, cy - s * 0.85, cx + s * 0.75, cy - s * 0.4), fill=(14, 12, 18))
def day_badge(d, hours, x=W - 30, y=60):
    dd = int(hours // 24) + 1
    d.rounded_rectangle((x - 300, y - 40, x, y + 40), 16, fill=(60, 10, 16, 235), outline=AIR, width=3)
    d.text((x - 280, y), f'DAY {dd}', font=BE(56), fill=PALE, anchor='lm'); d.text((x - 20, y), f'{hours:4.1f}時間', font=Fb(30), fill=GOLD, anchor='rm')

# ---- 1回戦：大停電 ----
SIM1 = 4.8   # 画面1秒 ＝ 4.8時間
def r_times(key, n=3):
    ons = [0.2 + o for o in onsets(key + 'a')]; tf = ons[3]
    cues = [(0.2, key + 'a'), (tf + 0.7, key + 'b')]; cues.append((cues[-1][0] + D[key + 'b'] + 0.6, key + 'c')); cues.append((cues[-1][0] + D[key + 'c'] + 0.8, key + 'd'))
    return ons, tf, cues
def r1_times():
    ons, tf, cues = r_times('r1'); end = max(cues[-1][0] + D['r1d'] + 1.4, tf + 0.6 + 48 / SIM1 + 1.2); return ons, tf, cues, end
def r1_frame(vt, ons, tf, caps):
    im = bg().convert('RGBA'); tau = vt - tf; hrs = max(0.0, (tau - 0.6) * SIM1); hrs = min(hrs, 48)
    ai_p = 1.0 if hrs < 18 else max(0.0, 1 - (hrs - 18) / 6)
    lit = 1.0 if tau < 0 else (max(0.0, 1 - tau / 0.5) if hrs < 30 else min(1.0, (hrs - 30) / 15))
    d = ImageDraw.Draw(im, 'RGBA')
    header(d, '1回戦　AIの大停電 vs 人類', '日本中の電気と通信が止まった（どうやって止めたかは考えない）')
    d.rounded_rectangle((40, 140, 1060, 880), 20, fill=(8, 8, 14, 225))
    city(d, 70, 1030, 640, lit); d.rectangle((60, 640, 1040, 650), fill=(80, 80, 90))
    for i in range(6):
        x = 150 + i * 160; phone(d, x, 750, 120, 0)
        if 0 <= tau and lit < 0.5: d.line((x - 30, 720, x + 30, 780), fill=RED, width=6); d.line((x - 30, 780, x + 30, 720), fill=RED, width=6)
    if 0 <= tau and lit < 0.5: ctext(d, (550, 840), '圏外', Fo(36), RED)
    if hrs >= 30: ctext(d, (550, 200), '人類が電気を取りもどしていく', Fo(36), GREEN, sw=3)
    else: ctext(d, (550, 200), '日本の町（絵は一部）', Fo(32), PALE)
    # 右：AI のデータセンター
    d.rounded_rectangle((1100, 140, 1880, 880), 20, fill=(8, 8, 14, 225)); ctext(d, (1490, 230), 'AIのデータセンター', Fo(36), PALE)
    ai_eye(im, 1490, 390, 120, vt, ai_p); d = ImageDraw.Draw(im, 'RGBA')
    fuel = 1.0 if tau < 0.6 else max(0.0, 1 - hrs / 24)
    d.text((1140, 580), '非常用の発電機の燃料（1日ぶんと仮定）', font=Fb(28), fill=GREY, anchor='lm'); battery(d, 1140, 610, 660, 90, fuel, f'{fuel * 100:.0f}%')
    rec = 0.0 if hrs < 0.01 else min(1.0, hrs / 45)
    d.text((1140, 740), '人類の電気の復旧（北海道では約45時間）', font=Fb(28), fill=GREY, anchor='lm')
    d.rectangle((1140, 770, 1800, 820), outline=GREY, width=3); d.rectangle((1146, 776, 1146 + 648 * rec, 814), fill=GREEN)
    if ai_p < 0.05: d.rounded_rectangle((1330, 470, 1650, 540), 14, fill=(160, 30, 40)); ctext(d, (1490, 505), 'AI 停止', Fo(44), PALE)
    if tau >= 0.6: day_badge(d, hrs)
    countdown(d, vt, ons, (550, 420))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, GOLD)
    note(d); foot(d, '※燃料1日ぶんは仮定。復旧の速さは北海道胆振東部地震（2018年）の大停電の例：約45時間でほぼ全域に送電（内閣府 防災白書）', size=18); return im.convert('RGB')
def scene_r1():
    ons, tf, cues, end = r1_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r1.mp4', end, lambda t: r1_frame(t, ons, tf, caps))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r1_t.json', 'w')); return end, cues

# ---- 2回戦：架空のウイルス ----
SIM2 = 3.0   # 画面1秒 ＝ 3時間
NPH = 2e8
def r2_times():
    ons, tf, cues = r_times('r2'); end = max(cues[-1][0] + D['r2d'] + 1.4, tf + 0.6 + 28 / SIM2 + 1.5); return ons, tf, cues, end
def infected(h): return min(NPH, 2 ** h)
def r2_frame(vt, ons, tf, caps):
    im = bg().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); tau = vt - tf; hrs = min(28.0, max(0.0, (tau - 0.6) * SIM2))
    header(d, '2回戦　架空のコンピューターウイルス vs 人類', '1時間ごとに 乗っ取られた台数が2倍になる（架空の速さ）')
    d.rounded_rectangle((40, 140, 1180, 880), 20, fill=(8, 8, 14, 225))
    nx, ny = 20, 10; n = nx * ny; f = infected(hrs) / NPH if tau >= 0.6 else 0.0
    k = int(round(f * n)) if f * n >= 1 else (1 if tau >= 0.6 else 0)
    rng = np.random.default_rng(5); order = rng.permutation(n)
    for i in range(n):
        x = 90 + (i % nx) * 54; y = 220 + (i // ny if False else i // nx) * 62
        phone(d, x, y, 50, 1.0 if order[i] < k else 0.0)
    d.text((70, 850), '■ 1つ ＝ 約100万台', font=Fb(26), fill=GREY, anchor='lm')
    # 右：台数
    d.rounded_rectangle((1220, 140, 1880, 880), 20, fill=(8, 8, 14, 225)); ctext(d, (1550, 200), '乗っ取られた台数', Fo(38), PALE)
    num = infected(hrs) if tau >= 0.6 else 0
    s = f'{num:,.0f}台' if num < 1e4 else (f'{num / 1e4:,.0f}万台' if num < 1e8 else f'{num / 1e8:.1f}億台')
    ctext(d, (1550, 330), s, Fo(84), AIR if num > 1e6 else GOLD, sw=3)
    ctext(d, (1550, 430), f'始まってから　{hrs:4.1f}時間', Fo(38), PALE)
    # 小さなグラフ
    x0, x1, y0, y1 = 1270, 1840, 500, 820; d.line((x0, y1, x1, y1), fill=GREY, width=3); d.line((x0, y0, x0, y1), fill=GREY, width=3)
    d.text((x0 + 8, y0 - 8), '日本中の約2億台（仮定）', font=Fb(24), fill=GREY, anchor='ls'); d.line((x0, y0 + 10, x1, y0 + 10), fill=(120, 120, 130), width=2)
    if tau >= 0.6:
        pts = [(x0 + (x1 - x0) * h / 28, y1 - (y1 - y0 - 10) * infected(h) / NPH) for h in np.linspace(0, hrs, 120)]
        if len(pts) > 1: d.line(pts, fill=AIR, width=6)
    d.text((x1, y1 + 28), '28時間', font=Fb(24), fill=GREY, anchor='rm')
    if tau >= 0.6: day_badge(d, hrs)
    countdown(d, vt, ons, (610, 520))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, GOLD)
    note(d); foot(d, '※ウイルスも広がる速さも架空。日本中のスマホとパソコンを約2億台と仮定。2の28乗＝約2.7億', size=18); return im.convert('RGB')
def scene_r2():
    ons, tf, cues, end = r2_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r2.mp4', end, lambda t: r2_frame(t, ons, tf, caps))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r2_t.json', 'w')); return end, cues

# ---- 決勝：ロボット軍 ----
SIM3 = 0.3   # 画面1秒 ＝ 0.3時間
def r3_times():
    ons, tf, cues = r_times('r3'); end = max(cues[-1][0] + D['r3d'] + 1.4, tf + 0.6 + 2.2 / SIM3 + 1.0); return ons, tf, cues, end
def r3_frame(vt, ons, tf, caps):
    im = bg().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); tau = vt - tf; hrs = min(2.2, max(0.0, (tau - 0.6) * SIM3))
    header(d, '決勝戦　ロボット約500万台 vs 人類82億人', '人間 約1,640人に ロボット1台')
    lev = 1.0 if tau < 0.6 else max(0.0, 1 - hrs / 2.0); pw = 1.0 if lev > 0 else 0.0; tt = vt if (tau >= 0 and lev > 0) else 0.0
    d.rounded_rectangle((40, 140, 1180, 880), 20, fill=(8, 8, 14, 225))
    for i in range(10):
        x = 110 + (i % 5) * 230; y = 430 + (i // 5) * 260
        robot_arm(d, x, y, 150, tt, ph=i * 0.9, moving=tau >= 0 and lev > 0)
    if tau >= 0: d.text((70, 180), '工場のロボット：多くは床にボルトで固定（金の丸）', font=Fb(28), fill=GOLD, anchor='lm')
    if tau >= 0:
        for j in range(2):
            x = 900 + j * 120 + (min(tau, 8) * 14 if lev > 0 else 0) * (1 if j else 0.6); walker(d, x, 820, 130, tt + j, pw)
        d.text((1150, 845), 'もし歩けたら（仮定）', font=Fb(24), fill=GREY, anchor='rm')
    d.rounded_rectangle((1220, 140, 1880, 880), 20, fill=(8, 8, 14, 225)); ctext(d, (1550, 200), 'ロボットの電池（2時間と仮定）', Fo(34), PALE)
    battery(d, 1290, 260, 480, 150, lev, f'{lev * 100:.0f}%')
    ctext(d, (1550, 470), f'始まってから　{hrs:3.1f}時間', Fo(40), PALE)
    d.text((1260, 560), '充電してくれる人', font=Fb(30), fill=GREY, anchor='lm'); d.text((1840, 560), 'いない', font=Fo(40), fill=RED, anchor='rm')
    d.text((1260, 640), '人類の数', font=Fb(30), fill=GREY, anchor='lm'); d.text((1840, 640), '約82億人', font=Fo(40), fill=GREEN, anchor='rm')
    d.text((1260, 720), 'ロボット1台あたり', font=Fb(30), fill=GREY, anchor='lm'); d.text((1840, 720), '約1,640人', font=Fo(40), fill=GOLD, anchor='rm')
    if lev <= 0: d.rounded_rectangle((1340, 780, 1760, 860), 16, fill=(160, 30, 40)); ctext(d, (1550, 820), 'ロボット 全部停止', Fo(42), PALE)
    if tau >= 0.6: day_badge(d, hrs)
    countdown(d, vt, ons, (610, 300))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, GOLD)
    note(d); foot(d, '※産業ロボット 約500万台（国際ロボット連盟 IFR、2025年）。世界人口 約82億人（国連）。電池2時間・全部が歩けるは仮定', size=18); return im.convert('RGB')
def scene_r3():
    ons, tf, cues, end = r3_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r3.mp4', end, lambda t: r3_frame(t, ons, tf, caps))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r3_t.json', 'w')); return end, cues

# ---- 静的な場面 ----
def scene_title():
    dur = 0.6 + D['intro'] + 0.6; k = 'intro'; f1 = frac(k, '電気を'); f2 = frac(k, 'スマホ'); f3 = frac(k, 'ロボット')
    def fr(t):
        im = bg().convert('RGBA'); u = ease(t / 0.5); ai_eye(im, 1450, 500, 300, t); d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (100, 320), 'AIが人類に', Mi(int(96 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (100, 460), '反乱したら', Mi(110), AIR, 'lm', 8)
        if t > 0.6: ctext(d, (100, 610), '人類は何日で負ける？', Mi(84), GOLD, 'lm', 6)
        if t > 0.9: ctext(d, (106, 720), 'IF AI REBELLED, HOW LONG WOULD HUMANITY LAST?', Fb(30), (225, 225, 230), 'lm', 2)
        uu = (t - 0.6) / D['intro']
        for i, (ff, lab) in enumerate([(f1, '①電気を止める'), (f2, '②スマホを乗っ取る'), (f3, '③ロボット軍団')]):
            if uu > ff: d.rounded_rectangle((100 + i * 400, 800, 470 + i * 400, 880), 16, fill=(40, 10, 14, 230), outline=AIR, width=3); ctext(d, (285 + i * 400, 840), lab, Fo(36), PALE)
        note(d, size=20); return im.convert('RGB')
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8; k = 'data'
    rows = [(frac(k, '人類は'), '人類', '約82億人', GREEN, False), (frac(k, 'AIの味方'), '工場のロボット（世界）', '約500万台', AIR, False),
            (frac(k, '人間、'), 'ロボット1台あたり', '人間 約1,640人', GOLD, True), (frac(k, '世界のデータ'), 'データセンターの電気（1年）', '約4,150億kWh', PALE, False),
            (frac(k, '世界の電気の'), '世界の電気のうち', '約1.5%', GOLD, True)]
    fdc = frac(k, 'そして')
    def fr(t):
        im = bg().convert('RGBA'); u = (t - t0) / dd
        if t < 0.4:   # 割り込み：画面が赤く光る
            R.glow(im, W / 2, H / 2, 700, AIR, int(160 * (1 - t / 0.4)))
        d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 70), '両チームの数字', Mi(68), GOLD, sw=3)
        if u < fdc:
            for i in range(6): robot_arm(d, 120 + (i % 3) * 230, 520 + (i // 3) * 300, 150, t, ph=i)
            ctext(d, (390, 900), '工場のロボット', Fo(36), PALE, sw=3)
        else:
            ai_eye(im, 420, 470, 200, t); d = ImageDraw.Draw(im, 'RGBA')
            for i in range(5): d.rectangle((150 + i * 110, 730, 230 + i * 110, 880), fill=(30, 32, 44), outline=(140, 140, 160), width=3); [d.ellipse((165 + i * 110 + j * 0, 750 + j * 22, 175 + i * 110, 760 + j * 22), fill=GREEN) for j in range(5)]
            ctext(d, (420, 920), 'データセンター（絵）', Fo(32), PALE, sw=3)
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 210 + r * 150, lab, val, col, 860, 1880, hl, lf=34, vf=50)
        note(d); foot(d, '※世界人口：国連（2024年 約82億人）。ロボット：国際ロボット連盟 IFR（2025年 約500万台）。電気：国際エネルギー機関 IEA「Energy and AI」（2024年 約415TWh）')
        return im.convert('RGB')
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; b = bg(0.75); k = 'rule'
    RULES = [('設定', 'AIが日本中のネットと機械を乗っ取った', frac(k, 'ある日')), ('方法', 'どうやって乗っ取るかは 考えない', frac(k, 'どうやって')),
             ('人類の負け', '元の暮らしに 戻れなくなったら', frac(k, '人類が')), ('AIの負け', 'AIが 動けなくなったら', frac(k, 'AIが、動け'))]
    def fr(t):
        im = b.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 170), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 240 + r * 170
            d.rounded_rectangle((140, y, W - 140, y + 130), 18, fill=(10, 10, 18, 225), outline=GOLD if r >= 2 else None, width=4 if r >= 2 else 0)
            d.rounded_rectangle((170, y + 30, 450, y + 100), 14, fill=(GREEN if r == 2 else (AIR if r == 3 else BLUE))); ctext(d, (310, y + 65), who, Fo(36), (20, 20, 24))
            d.text((490, y + 65), txt, font=Fo(46), fill=PALE, anchor='lm')
        if u > frac(k, '何日もつか'): ctext(d, (W / 2, 950), '何日もつか、数えていく', Mi(56), GOLD, sw=3)
        note(d); foot(d, '※空想のシミュレーションです。攻撃の方法やしくみは扱いません')
        return im
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]
def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None, icon=None):
    dur = 0.6 + D[key] + 0.8; b = ImageEnhance.Brightness(dark_bg().filter(ImageFilter.GaussianBlur(2))).enhance(0.8)
    def fr(t):
        im = b.copy().convert('RGBA'); u = ease(t / 0.4)
        if icon: icon(im, t)
        d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 200), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 340), big, Mi(int(110 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col, ph) in enumerate(lines):
            if t < 0.6 + D[key] * frac(key, ph): continue
            y = 520 + r * 112
            d.rounded_rectangle((W / 2 - 760, y - 46, W / 2 + 760, y + 46), 16, fill=(10, 10, 18, 225))
            d.text((W / 2 - 720, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 720, y), val, font=Fo(48), fill=col, anchor='rm')
        if sub: foot(d, sub, size=18)
        note(d)
        return im.convert('RGB')
    run(out, dur, fr); return dur, [(0.6, key)]
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0; k = 'reveal'
    f1 = frac(k, '一つ目'); f2 = frac(k, '二つ目'); f3 = frac(k, 'ある会社'); f4 = frac(k, 'そして三つ目'); f5 = frac(k, 'そして三つ目')
    def fr(t):
        im = bg().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), 'AIの弱点：体を 人間にたよっている', Mi(64), GOLD, sw=3)
        cols = [(f1, '電気', '発電所・燃料を運ぶ'), (f2, '部品', 'GPUがよく壊れる'), (f5, '修理', '部品を取りかえる')]
        for i, (ff, lab, sub) in enumerate(cols):
            x = 330 + i * 630
            if u < ff and not (i == 0 and u < f1): pass
            on = u >= ff
            d.rounded_rectangle((x - 270, 170, x + 270, 520), 22, fill=(10, 10, 18, 230 if on else 120), outline=GOLD if on else (70, 70, 80), width=4)
            if not on: ctext(d, (x, 345), '？', Mi(120), (90, 90, 100)); continue
            if i == 0: plug(d, x, 300, 110)
            elif i == 1: gpu_chip(d, x, 285, 95, broken=u > f4)
            else: wrench(d, x, 310, 120)
            ctext(d, (x, 430), lab, Mi(60), PALE); ctext(d, (x, 490), sub, Fb(30), GREY)
        if f3 <= u < f5 + 0.02 or u >= f5:
            if u >= f3:
                rowbox(d, 630, 'GPU 約1万6千個で 54日間 学習', '予定外に止まる 419回', GOLD, 160, 1760, lf=36, vf=48)
                if u > frac(k, 'およそ三時間'): rowbox(d, 770, 'つまり', '約3時間に1回', AIR, 160, 1760, True, lf=36, vf=56, h=62)
        note(d); foot(d, '※Meta「The Llama 3 Herd of Models」（2024年）より。H100 GPU 16,384個・54日間で予定外の中断419回（DatacenterDynamics の記事による）')
        return im.convert('RGB')
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]
SWR = [('1日', '約8回', '一日なら'), ('1週間', '約54回', '一週間'), ('1か月', '約230回', '一か月'), ('1年', '約2,800回', '一年なら')]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; b = bg(0.7); k = 'sweep'; fno = frac(k, 'AIは、少し')
    def fr(t):
        im = b.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 70), '修理する人が いなくなったら？', Mi(64), GOLD, sw=3)
        ctext(d, (560, 170), '時間', Fo(32), GREY); ctext(d, (1300, 170), '止まるトラブル（約1万6千個のGPUで）', Fo(32), GREY)
        for r, (nm, val, ph) in enumerate(SWR):
            if u < frac(k, ph): continue
            y = 270 + r * 135; last = r == 3
            d.rounded_rectangle((200, y - 55, W - 200, y + 55), 16, fill=(10, 10, 18, 230), outline=GOLD if last else None, width=4)
            ctext(d, (560, y), nm, Fo(46), PALE); ctext(d, (1300, y), val, Fo(54), AIR if last else GOLD)
            nb = min(40, [1, 7, 30, 365][r]); bw = 520 / 40
            for j in range(nb): d.rectangle((1540 + (j % 20) * 9, y - 30 + (j // 20) * 30, 1546 + (j % 20) * 9, y - 6 + (j // 20) * 30), fill=AIR if last else (200, 120, 60))
        if u > fno:
            d.rounded_rectangle((260, 850, 1660, 950), 18, fill=(40, 10, 14, 235), outline=AIR, width=3)
            ctext(d, (W / 2, 900), '直す人がいなければ、AIは少しずつ動けなくなる', Fo(44), PALE)
        note(d); foot(d, '※419回÷54日＝1日 約7.8回が続くとした目安（仮定）。実際は止まり方や部品の数でかわります')
        return im
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]
def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; b = bg(0.75); k = 'outro'; f1 = frac(k, 'AIは、電気'); f2 = frac(k, 'でも、本当に'); f3 = frac(k, 'あなたは')
    def fr(t):
        u = (t - 0.5) / D['outro']; im = b.copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
        if u < f2:
            ctext(d, (W / 2, 120), 'まとめ', Mi(80), GOLD, sw=3)
            ctext(d, (W / 2, 260), '人類は何日で負ける？', Fo(52), PALE)
            ctext(d, (W / 2, 390), '答え：負けない', Mi(100), GREEN, sw=5)
            if u > f1:
                for i, (lab, fn) in enumerate([('電気', plug), ('部品', None), ('修理', wrench)]):
                    x = 500 + i * 460
                    d.rounded_rectangle((x - 190, 520, x + 190, 820), 20, fill=(10, 10, 18, 230), outline=GOLD, width=3)
                    if fn: fn(d, x, 640, 90)
                    else: gpu_chip(d, x, 650, 100)
                    ctext(d, (x, 780), lab, Mi(50), PALE)
                ctext(d, (W / 2, 900), '人類を負かすと、AIも止まる', Mi(60), GOLD, sw=3)
        elif u < f3:
            ctext(d, (W / 2, 150), '本当に怖いのは…', Mi(80), AIR, sw=4)
            for i in range(10):
                x = 330 + i * 140; phone(d, x, 470, 150, 1.0 if (t * 3 + i) % 4 > 1 else 0.0)
            ctext(d, (W / 2, 700), 'スマホが止まるだけで', Mi(70), PALE, sw=3); ctext(d, (W / 2, 830), 'たった1日で 大混乱', Mi(90), GOLD, sw=4)
        else:
            ai_eye(im, 1560, 520, 230, t); dd = ImageDraw.Draw(im, 'RGBA')
            ctext(dd, (700, 330), 'あなたは スマホなしで', Mi(70), PALE, sw=4); ctext(dd, (700, 450), '何日たえられる？', Mi(84), GOLD, sw=4)
            ctext(dd, (700, 570), 'コメントで教えてください', Fo(48), PALE, sw=3)
            if u > f3 + 0.08:
                dd.rounded_rectangle((700 - 500, 680, 700 + 500, 860), 24, fill=(10, 10, 18, 225), outline=GOLD, width=4)
                ctext(dd, (700, 730), '次に見たい「もしも」は？', Fo(50), PALE); ctext(dd, (700, 810), 'リクエスト募集中！', Fo(44), GOLD)
        note(ImageDraw.Draw(im)); return im.convert('RGB')
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]
def icon_eye(on):
    def f(im, t): ai_eye(im, W / 2, 900, 90, t, 1.0 if on else 0.15)
    return f
if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
        res['res1'] = scene_card('res1', 'RESULT  1回戦', [('北海道の大停電（2018年）', '約295万戸 → 約45時間でほぼ復旧', GREEN, '実際に'), ('大きな通信障害（2022年）', '約61時間で元にもどる', GREEN, '二〇二二年'),
                                 ('AIの発電機（燃料1日ぶんと仮定）', '1日で AIが先に止まる', AIR, 'いっぽう')], f'{G}/c_res1.mp4', big='人類の勝ち', bigcol=GREEN,
                                 sub='※内閣府「令和元年版 防災白書」。KDDI 通信障害（2022年7月2日〜4日、61時間25分、最大3,915万回線）。燃料は仮定')
        res['res2'] = scene_card('res2', 'RESULT  2回戦', [('約2億台が 使えなくなるまで', 'たった約28時間', AIR, '一時間ごと'), ('止まるもの', '電子マネー・地図・連絡', PALE, '電子マネー'),
                                 ('人類の反撃', '線を抜いて電源を切る', GREEN, 'ネットの線')], f'{G}/c_res2.mp4', big='AIの勝ち', bigcol=AIR,
                                 sub='※ウイルスも広がる速さ（1時間で2倍）も架空。台数は仮定')
        res['res3'] = scene_card('res3', 'RESULT  決勝戦', [('工場のロボットの多く', '床に固定された腕で 外に出られない', PALE, '工場の'), ('全部が歩けたとしても', '人間 約1,640人に1台', GOLD, 'もし全部'),
                                 ('電池（2時間と仮定）', '2時間後に 全部止まる', GREEN, '電池が')], f'{G}/c_res3.mp4', big='人類の勝ち', bigcol=GREEN,
                                 sub='※産業ロボット 約500万台（IFR、2025年）。電池の時間は仮定')
    elif which in ('r1', 'r2', 'r3'): res[which] = globals()['scene_' + which]()
    elif which == 'still':
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        for nm, tfn, ffn in (('r1', r1_times, r1_frame), ('r2', r2_times, r2_frame), ('r3', r3_times, r3_frame)):
            ons, tf, cues, end = tfn(); caps = caps_for(cues); print(nm, tf, end)
            for vt in (ons[0] + 0.1, tf + 0.3, tf + 3.0, tf + 6.0, end - 0.1): ffn(vt, ons, tf, caps).resize((960, 540)).save(f'{G}/stills/{nm}_{vt:04.1f}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
