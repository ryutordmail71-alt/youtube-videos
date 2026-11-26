"""日本中で同時にトイレを流したら？ の場面"""
import json, math, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import trender as R, tcontent as C
from trender import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ORANGE, WATER, WATER2, ctext, fade, ease, writer, rowbox, foot, note
G = '/home/claude/tlt'; D = json.load(open(f'{G}/dur.json'))
def frac(key, phrase): i = C.NAR[key].index(phrase); return i / len(C.NAR[key])
def onsets(key, last=4):
    """ナレーションの最後の last 個の言葉の始まり（さん・に・いち・流せ）"""
    with wave.open(f'{G}/voice/{key}.wav') as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    k = int(sr * 0.02); e = np.sqrt(np.convolve(a * a, np.ones(k) / k, 'same'))[::k]; on = e > 0.02; res = []; quiet = 0
    for i, v in enumerate(on):
        if v and quiet >= 6: res.append(i * 0.02)
        quiet = 0 if v else quiet + 1
    return res[-last:]
def bg(dark=1.0): return ImageEnhance.Brightness(R.night_bg()).enhance(dark)
def run(out, dur, fn):
    p = writer(out)
    for f in range(int(dur * FPS)): p.stdin.write(fn(f / FPS).tobytes())
    p.stdin.close(); p.wait()
def capbar(d, cap, col, y=945):
    if not cap: return
    fnt = Fo(54); tw = fnt.getlength(cap)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, y - 45, W / 2 + tw / 2 + 40, y + 45), 18, fill=(8, 10, 16, 235), outline=col, width=3); ctext(d, (W / 2, y), cap, fnt, col)
def caps_for(cues): return [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in cues if k in C.CAP]
def countdown(d, t, ons, xy):
    labs = ['3', '2', '1', '流せ！']
    for i in range(len(ons)):
        a = ons[i]; b = ons[i + 1] if i + 1 < len(ons) else a + 1.0
        if a <= t < b:
            u = ease((t - a) / 0.2)
            if i < 3: ctext(d, xy, labs[i], BE(int(170 * (1.3 - 0.3 * u))), PALE, sw=6)
            else: ctext(d, xy, labs[i], Mi(int(120 * (1.3 - 0.3 * u))), GOLD, sw=6)
def header(d, a, b):
    d.rectangle((0, 0, W, 120), fill=(6, 9, 16, 235)); ctext(d, (W / 2, 40), a, Fo(38), GOLD); ctext(d, (W / 2, 92), b, Fb(28), PALE)

# ---- 1回戦：日本中の1億2400万人 vs 下水道 ----
HX = [110, 250, 390, 530, 670, 810]           # 家の位置
GY = 330; BR = 520; TR = 770; PLANT = (980, 640, 1170, 900)
def r1_times():
    ons = [0.2 + o for o in onsets('r1a')]; tf = ons[3]
    cues = [(0.2, 'r1a'), (tf + 0.7, 'r1b')]; cues.append((cues[-1][0] + D['r1b'] + 0.6, 'r1c')); cues.append((cues[-1][0] + D['r1c'] + 0.8, 'r1d'))
    end = cues[-1][0] + D['r1d'] + 1.6; return ons, tf, cues, end
def paths():
    """家 → 枝の管 → 太い管 → 水再生センター"""
    ps = []
    for i, x in enumerate(HX): ps.append([(x, GY - 10), (x, BR), (900, BR), (900, TR), (PLANT[0], TR)])
    return ps
def along(p, s):
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if s <= L: return x0 + (x1 - x0) * s / L, y0 + (y1 - y0) * s / L
        s -= L
    return None
def burst(tau):
    """流してからの時間 → 太い管の水の割合（目安）。ふだん 約0.7%、いちばん多いとき 約6%"""
    if tau < 1.2: return 0.0
    q = tau - 1.2; return 0.053 * (1 - math.exp(-q / 1.2)) * math.exp(-max(0, q - 4.0) / 6.0)
def r1_frame(vt, ons, tf, caps):
    im = bg().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); tau = vt - tf
    header(d, '1回戦　日本中の1億2,400万人 vs 下水道', '全員が同時に「大」で流す（1回 平均8L＝合計 約100万トン）')
    # 地上と地下
    d.rectangle((40, GY, 1180, 1000), fill=(52, 44, 38)); d.rectangle((40, GY, 1180, GY + 10), fill=(90, 120, 70))
    for i, x in enumerate(HX):
        R.house(d, x, GY, 110, 150); R.toilet(d, x + 2, GY - 16, 46, (235, 238, 245), (30, 34, 46))
    d.text((885, GY - 40), '← 家のトイレ（絵は一部）', font=Fb(24), fill=PALE, anchor='lm')
    for p in paths():
        d.line(p[:3], fill=(150, 145, 140), width=16, joint='curve')
    d.line((900, BR - 8, 900, TR), fill=(150, 145, 140), width=30); d.line((60, TR, PLANT[0], TR), fill=(150, 145, 140), width=90)
    d.line((60, TR, PLANT[0], TR), fill=(25, 22, 22), width=74)
    d.text((80, BR + 40), '枝の管', font=Fb(26), fill=GREY, anchor='lm'); d.text((90, TR + 70), '太い管（幹線）', font=Fb(28), fill=GREY, anchor='lm')
    d.rounded_rectangle(PLANT, 16, fill=(30, 60, 90), outline=(140, 190, 240), width=3); ctext(d, ((PLANT[0] + PLANT[2]) / 2, 700), '水再生', Fo(32), PALE); ctext(d, ((PLANT[0] + PLANT[2]) / 2, 745), 'センター', Fo(32), PALE)
    ctext(d, ((PLANT[0] + PLANT[2]) / 2, 830), '（下水処理場）', Fb(22), GREY)
    # ふだんの細い流れ
    fr0 = 0.007 + burst(tau); hh = max(3, 74 * R.seg_h(fr0) / 2)
    d.rectangle((60, TR + 37 - hh, PLANT[0], TR + 37), fill=WATER)
    # 流した水のつぶ
    if tau > 0:
        for i, p in enumerate(paths()):
            for k in range(10):
                s = (tau - k * 0.25) * 420
                if s <= 0: continue
                pt = along(p, s)
                if pt: d.ellipse((pt[0] - 7, pt[1] - 7, pt[0] + 7, pt[1] + 7), fill=WATER2)
        if tau < 0.8:
            for x in HX: R.swirl(d, x - 7, GY - 40, 18, vt)
    countdown(d, vt, ons, (560, 645))
    # 右：太い管の断面
    d.rounded_rectangle((1220, 140, 1880, 880), 20, fill=(8, 12, 20, 225))
    ctext(d, (1550, 185), '太い管（幹線）の断面', Fo(36), PALE)
    d = R.pipe_section(im, 1550, 450, 210, fr0)
    ctext(d, (1550, 710), f'水が使っている太さ　約{fr0 * 100:.0f}%' if fr0 >= 0.01 else '水が使っている太さ　約1%未満', Fo(40), GOLD if tau > 2 else PALE)
    ctext(d, (1550, 765), '（大雨のときは いっぱいまで使う）', Fb(26), GREY)
    tons = 0 if tau < 0 else min(100, 100 * fade((tau - 0.3) / 3.5))
    d.rounded_rectangle((1260, 800, 1840, 860), 14, fill=(20, 40, 70, 230)); d.text((1280, 830), '流した水', font=Fb(30), fill=GREY, anchor='lm')
    d.text((1820, 830), f'約{tons:.0f}万トン', font=Fo(40), fill=WATER2, anchor='rm')
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, GOLD, 960)
    note(d); foot(d, '※管の太さに対する割合は、流した水が数分にちらばって届くとした目安'); return im.convert('RGB')
def scene_r1():
    ons, tf, cues, end = r1_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r1.mp4', end, lambda t: r1_frame(t, ons, tf, caps))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r1_t.json', 'w')); return end, cues

# ---- 決勝：23区のタンク7.6万トン vs 水道 ----
SIMR = 2.6     # 画面1秒 ＝ 2.6分
def r2_times():
    ons = [0.2 + o for o in onsets('r2a')]; tf = ons[3]
    cues = [(0.2, 'r2a'), (tf + 0.7, 'r2b')]; cues.append((cues[-1][0] + D['r2b'] + 0.6, 'r2c')); cues.append((cues[-1][0] + D['r2c'] + 0.8, 'r2d'))
    end = max(cues[-1][0] + D['r2d'] + 1.2, tf + 0.6 + 25 / SIMR + 1.4); return ons, tf, cues, end
def r2_frame(vt, ons, tf, caps, c2):
    im = bg().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); tau = vt - tf
    header(d, '決勝戦　23区のトイレのタンク vs 水道', '流したあと、約950万人ぶんのタンクが いっせいに水をためる（合計 約7.6万トン）')
    sim = max(0.0, (tau - 0.6) * SIMR)                   # 流してからの分
    lev = 1.0 if tau < 0 else (0.0 if tau < 0.6 else min(1.0, sim / 25))
    d.rounded_rectangle((40, 140, 1060, 880), 20, fill=(8, 12, 20, 225))
    for i in range(18):
        x = 140 + (i % 6) * 160; y = 355 + (i // 6) * 205
        R.toilet(d, x, y, 140, (225, 230, 240), (26, 30, 42), tank=lev)
    if not (tau >= 0.6 and sim >= 1.0): ctext(d, (550, 180), 'トイレのタンク（絵は一部）', Fo(32), PALE)
    if tau >= 0.6:
        ctext(d, (550, 835), f'流してから　{min(25, sim):4.1f} 分', Fo(48), GOLD if sim > 1.2 else PALE)
        if 1.0 <= sim: d.rounded_rectangle((330, 152, 770, 208), 14, fill=(160, 30, 40)); ctext(d, (550, 180), 'ふつうなら 約1分で満タン', Fb(30), PALE)
    # 右：水の勢いメーター
    d.rounded_rectangle((1100, 140, 1880, 880), 20, fill=(8, 12, 20, 225)); ctext(d, (1490, 185), '水道の勢い', Fo(36), PALE)
    cx, cy, r = 1490, 460, 220; d.arc((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=GREY, width=8)
    for k in range(11):
        a = math.pi * (1 + k / 10); d.line((cx + (r - 26) * math.cos(a), cy + (r - 26) * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a)), fill=GREY, width=4)
    d.text((cx - r, cy + 30), '弱い', font=Fb(28), fill=RED, anchor='mm'); d.text((cx + r, cy + 30), '強い', font=Fb(28), fill=GREEN, anchor='mm')
    g = 0.75 if tau < 0.6 else 0.75 - 0.5 * ease((tau - 0.6) / 1.2) + (0.5 * ease((sim - 22) / 3) if sim > 22 else 0)
    g += 0.015 * math.sin(vt * 9) if 0.6 < tau and sim < 25 else 0
    a = math.pi * (1 + g); d.line((cx, cy, cx + (r - 40) * math.cos(a), cy + (r - 40) * math.sin(a)), fill=GOLD, width=10); d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=GOLD)
    if vt >= c2:
        u = ease((vt - c2) / 0.6)
        d.text((1140, 600), '必要な勢い（1時間あたり）', font=Fb(28), fill=GREY, anchor='lm'); d.rectangle((1140, 625, 1140 + 700 * u, 665), fill=ORANGE)
        d.text((1840, 690), '約456万トン', font=Fo(34), fill=ORANGE, anchor='rm')
        d.text((1140, 740), '東京都の水道（いちばん多い日）', font=Fb(28), fill=GREY, anchor='lm'); d.rectangle((1140, 765, 1140 + 700 / 24.4 * u, 805), fill=WATER2)
        d.text((1840, 830), '約19万トン → 約24分の1', font=Fo(34), fill=WATER2, anchor='rm')
    countdown(d, vt, ons, (550, 560))
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None); capbar(d, cap, GOLD, 960)
    note(d); foot(d, '※タンクの水 約7.6万トンを1分でためる勢い。東京都の水道：1日最大配水量 約448万m³（2023年度）。ほかの水の使用は考えない目安'); return im.convert('RGB')
def scene_r2():
    ons, tf, cues, end = r2_times(); caps = caps_for(cues)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_r2.mp4', end, lambda t: r2_frame(t, ons, tf, caps, cues[2][0]))
    json.dump(dict(ons=ons, tf=tf), open(f'{G}/c_r2_t.json', 'w')); return end, cues

# ---- 静的な場面 ----
def title_art(im, cx, cy, s, t):
    R.glow(im, cx, cy - s * 0.3, s * 0.9, (60, 140, 255), 150); d = ImageDraw.Draw(im, 'RGBA')
    R.toilet(d, cx + s * 0.1, cy + s * 0.5, s, (240, 244, 250), (24, 32, 52))
    R.swirl(d, cx - s * 0.05, cy + s * 0.04, s * 0.2, t); return d
def scene_title():
    dur = 0.6 + D['intro'] + 0.6
    def fr(t):
        im = bg().convert('RGBA'); d = title_art(im, 1440, 520, 560, t); u = ease(t / 0.5)
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (100, 320), '日本中の人が', Mi(int(92 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (100, 470), '同時にトイレを', Mi(104), GOLD, 'lm', 8)
        if t > 0.6: ctext(d, (100, 610), '流したら？', Mi(96), PALE, 'lm', 6)
        if t > 0.9: ctext(d, (106, 730), 'WHAT IF ALL OF JAPAN FLUSHED AT ONCE?', Fb(32), (225, 225, 230), 'lm', 2)
        if t > 1.2: ctext(d, (100, 840), '下水道は あふれる？', Fo(52), PALE, 'lm', 3)
        note(d, size=20); return im.convert('RGB')
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8; k = 'data'
    rows = [(frac(k, '日本の人口'), '日本の人口', '約1億2,400万人', PALE, False), (frac(k, '新しいトイレ'), 'トイレ1回の水（新しいもの）', '約4.8L', PALE, False),
            (frac(k, '昔のトイレ'), 'トイレ1回の水（昔のもの）', '約13L', PALE, False), (frac(k, 'ここでは'), 'この動画の平均', '8L（仮定）', PALE, False),
            (frac(k, '全員で'), '全員で1回ずつ流すと', '約100万トン', ORANGE, False), (frac(k, 'いっぽう'), '日本の下水（1日あたり）', '約3,800万トン', GOLD, True)]
    fdome = frac(k, '東京ドーム')
    def fr(t):
        im = bg().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 70), '数字をそろえると', Mi(68), GOLD, sw=3)
        if u < rows[4][0]:
            R.toilet(d, 450, 820, 520, (235, 240, 248), (24, 32, 52))
        else:
            q = ease((u - rows[4][0]) / 0.05) if u < fdome else 1
            R.dome(d, 430, 760, 680, 330, 0.61 * ease((u - fdome) / 0.06) if u > fdome else 0)
            ctext(d, (430, 385), '東京ドーム（約124万m³）', Fo(36), PALE, sw=3)
            if u > fdome: ctext(d, (430, 840), '全員のトイレの水 ＝ 約0.8杯ぶん', Fo(40), WATER2, sw=3)
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 200 + r * 132, lab, val, col, 860, 1880, hl, lf=34, vf=48)
        note(d); foot(d, '※人口：総務省 人口推計（2024年）。水の量：TOTO の資料。下水：国土交通省 資料（下水処理量 約140億m³/年）。水1m³＝約1トン')
        return im.convert('RGB')
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; b = bg(0.75); k = 'rule'
    RULES = [('合図', '全員が、ぴったり同時にトイレを流す', frac(k, '合図')), ('トイレ', 'トイレは1人に1つずつあるとする', frac(k, 'トイレは')),
             ('仮定', '下水道がない約2割の家も、つながっているとする', frac(k, '下水道に')), ('勝ち負け', '下水の管が いっぱいになって、あふれたら負け', frac(k, 'そして'))]
    def fr(t):
        im = b.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 170), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 240 + r * 170; last = r == 3
            d.rounded_rectangle((140, y, W - 140, y + 130), 18, fill=(10, 14, 24, 225), outline=GOLD if last else None, width=4 if last else 0)
            d.rounded_rectangle((170, y + 30, 400, y + 100), 14, fill=RED if last else BLUE); ctext(d, (285, y + 65), who, Fo(38), (20, 20, 24))
            d.text((440, y + 65), txt, font=Fo(46), fill=PALE, anchor='lm')
        note(d); foot(d, '※下水道の普及率 約81%（国土交通省、2022年度末）。空想のシミュレーションです')
        return im
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]
def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None):
    dur = 0.6 + D[key] + 0.8; b = ImageEnhance.Brightness(R.night_bg().filter(ImageFilter.GaussianBlur(2))).enhance(0.8)
    def fr(t):
        im = b.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.4)
        ctext(d, (W / 2, 230), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 380), big, Mi(int(110 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 720, y - 48, W / 2 + 720, y + 48), 16, fill=(10, 14, 24, 220))
            d.text((W / 2 - 680, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 680, y), val, font=Fo(50), fill=col, anchor='rm')
        if sub: foot(d, sub)
        note(d)
        return im
    run(out, dur, fr); return dur, [(0.6, key)]
def rain(d, x0, x1, y0, y1, t, n=60, col=(150, 200, 255, 180), seed=2):
    rng = np.random.default_rng(seed); xs = rng.uniform(x0, x1, n); ph = rng.uniform(0, 1, n)
    for x, p in zip(xs, ph):
        y = y0 + ((t * 1.6 + p) % 1) * (y1 - y0); d.line((x, y, x - 6, y + 26), fill=col, width=3)
def gauge_cyl(d, x, yb, w, h, mm, maxmm=50, col=WATER, label=''):
    d.rectangle((x - w / 2, yb - h, x + w / 2, yb), outline=GREY, width=4)
    hh = h * mm / maxmm
    if hh > 0: d.rectangle((x - w / 2 + 4, yb - max(3, hh), x + w / 2 - 4, yb - 2), fill=col)
    for v in range(0, maxmm + 1, 10): yy = yb - h * v / maxmm; d.line((x + w / 2, yy, x + w / 2 + 16, yy), fill=GREY, width=3); d.text((x + w / 2 + 24, yy), f'{v}', font=Fb(24), fill=GREY, anchor='lm')
    d.text((x + w / 2 + 24, yb - h - 30), 'ミリ', font=Fb(24), fill=GREY, anchor='lm'); ctext(d, (x, yb + 40), label, Fo(32), PALE)
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0; k = 'reveal'
    f1 = frac(k, '東京二十三区'); f2 = frac(k, 'そして'); f3 = frac(k, '二十三区のおよそ'); f4 = frac(k, '二十三区の広さ'); f5 = frac(k, 'かさも')
    def fr(t):
        im = bg().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        if u < f3:
            ctext(d, (W / 2, 80), 'なぜ、こんなに余裕がある？', Mi(66), GOLD, sw=3)
            rain(d, 160, 960, 230, 400, t); d.ellipse((140, 170, 520, 260), fill=(90, 100, 120)); d.ellipse((400, 150, 900, 270), fill=(100, 110, 130))
            d.rectangle((100, 420, 1000, 1000), fill=(52, 44, 38)); d.rectangle((100, 420, 1000, 430), fill=(90, 120, 70))
            R.house(d, 300, 420, 150, 190); R.toilet(d, 302, 400, 60, (235, 238, 245), (30, 34, 46))
            d.line((300, 430, 300, 700), fill=(150, 145, 140), width=18); d.line((700, 425, 700, 700), fill=(150, 145, 140), width=18)
            d.rectangle((680, 405, 720, 425), fill=(60, 60, 60)); d.text((740, 395), '雨水ます', font=Fb(26), fill=GREY, anchor='lm')
            d.line((120, 760, 980, 760), fill=(150, 145, 140), width=130); d.line((120, 760, 980, 760), fill=(22, 20, 20), width=110)
            d.rectangle((120, 800, 980, 815), fill=WATER)
            if u > f1: ctext(d, (550, 900), '雨水とトイレの水が 同じ管へ（合流式）', Fo(38), PALE, sw=3)
            if u > f1: rowbox(d, 380, '23区の下水道の多く', '雨とトイレが同じ管', PALE, 1060, 1860, lf=32, vf=42)
            if u > f2: rowbox(d, 560, '流せる雨（23区の基本）', '1時間 50ミリ', GOLD, 1060, 1860, True, lf=32, vf=52, h=70)
            if u > f2: ctext(d, (1460, 720), '＝ 外を歩くのが こわいくらいの大雨', Fo(34), PALE)
            foot(d, '※東京都下水道局：区部は1時間50ミリの雨に対応する整備が基本（重点地区は75ミリ）。合流式の地域が多い')
        else:
            ctext(d, (W / 2, 80), '23区の全員が流した水を、雨にすると', Mi(62), GOLD, sw=3)
            gauge_cyl(d, 320, 900, 160, 600, 50 if u > f2 else 0, label='大雨（設計）'); gauge_cyl(d, 640, 900, 160, 600, 0.134 if u > f4 else 0, col=GOLD, label='トイレ全員')
            if u > f4: d.line((720, 895, 790, 845), fill=GOLD, width=3); d.text((800, 840), '0.13ミリ', font=Fo(36), fill=GOLD, anchor='lm')
            rowbox(d, 260, '23区の約950万人 × 8L', '約7.6万トン', ORANGE, 960, 1860, lf=34, vf=50)
            if u > f4: rowbox(d, 410, '23区の下水道の広さ', '約566km²', PALE, 960, 1860, lf=34, vf=50)
            if u > f4 + 0.03: rowbox(d, 590, '雨にすると', '約0.13ミリ', GOLD, 960, 1860, True, lf=36, vf=64, h=70)
            if u > f5: ctext(d, (1410, 760), 'かさもいらない 小雨', Mi(64), PALE, sw=3)
            foot(d, '※計画人口 約949万人・計画面積 約56,591ha（東京都下水道局 経営レポート2025）。7.6万m³÷566km²＝約0.13mm')
        note(d); return im.convert('RGB')
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]
SWR = [('1回', '約0.13ミリ', '小雨', '一回なら'), ('10回', '約1.3ミリ', '弱い雨', '十回なら'), ('60回（1分ごと）', '約8ミリ', 'ふつうの雨', 'タンクに'),
       ('約370回（10秒に1回）', '50ミリ', '大雨＝下水道の設計', '大雨と同じ')]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; b = bg(0.7); cx = [460, 960, 1360]; k = 'sweep'; fno = frac(k, 'でも、タンク')
    def fr(t):
        im = b.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 70), '何回流せば、あふれる？（23区の全員で）', Mi(62), GOLD, sw=3)
        for j, h in enumerate(['1時間に流す回数', '雨でいうと', '強さ']): ctext(d, (cx[j], 170), h, Fo(32), GREY)
        for r, (nm, mm, lab, ph) in enumerate(SWR):
            if u < frac(k, ph): continue
            y = 270 + r * 135; last = r == 3
            d.rounded_rectangle((80, y - 55, W - 80, y + 55), 16, fill=(10, 14, 24, 230), outline=GOLD if last else None, width=4)
            ctext(d, (cx[0], y), nm, Fo(42), PALE); ctext(d, (cx[1], y), mm, Fo(50), GOLD if last else WATER2); ctext(d, (cx[2], y), lab, Fo(40), PALE)
            if last and u > fno:
                d.rounded_rectangle((1640, y - 42, 1830, y + 42), 12, fill=(160, 30, 40)); ctext(d, (1735, y), 'できない', Fo(36), PALE)
        if u > fno:
            d.rounded_rectangle((260, 850, 1660, 950), 18, fill=(40, 34, 10, 235), outline=GOLD, width=3)
            ctext(d, (W / 2, 900), 'タンクに水がたまるのは 約1分 → 10秒ごとには流せない', Fo(44), GOLD)
        note(d); foot(d, '※1回＝約7.6万トン（約0.13ミリぶん）として計算。タンクに水がたまる時間は約1分（目安）。50ミリ÷0.134ミリ＝約370')
        return im
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]
def scene_real():
    t0 = 0.5; dd = D['real']; dur = t0 + dd + 1.0; k = 'real'; f1 = frac(k, 'サッカー'); f2 = frac(k, '試合から'); f3 = frac(k, '水道局は')
    def curve(x):          # 0..1 の時間 → 使用量（イメージ）
        v = 0.45 + 0.08 * x
        v += 0.12 * math.exp(-((x - 0.12) / 0.04) ** 2)          # 試合前
        v -= 0.10 * fade((x - 0.18) / 0.03) * (1 - fade((x - 0.44) / 0.02)) + 0.10 * fade((x - 0.56) / 0.03) * (1 - fade((x - 0.84) / 0.02))
        v += 0.32 * math.exp(-((x - 0.50) / 0.025) ** 2) + 0.30 * math.exp(-((x - 0.89) / 0.03) ** 2)
        return v
    def fr(t):
        im = bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '本当にあった「みんな同時に」', Mi(66), GOLD, sw=3)
        x0, x1, y0, y1 = 160, 1760, 220, 820; d.rounded_rectangle((100, 170, 1820, 900), 20, fill=(8, 12, 20, 225))
        d.line((x0, y1, x1, y1), fill=GREY, width=3); d.line((x0, y0, x0, y1), fill=GREY, width=3)
        d.text((x0 + 10, y0 - 10), '水道の使用量（イメージ）', font=Fb(28), fill=GREY, anchor='ls')
        for xa, xb, lab in [(0.20, 0.44, '前半'), (0.56, 0.84, '後半')]:
            d.rectangle((x0 + (x1 - x0) * xa, y0 + 20, x0 + (x1 - x0) * xb, y1), fill=(60, 160, 90, 40)); ctext(d, (x0 + (x1 - x0) * (xa + xb) / 2, y1 + 34), lab, Fo(32), GREEN)
        ctext(d, (x0 + (x1 - x0) * 0.50, y1 + 34), 'ハーフタイム', Fo(28), GOLD); ctext(d, (x0 + (x1 - x0) * 0.92, y1 + 34), '試合のあと', Fo(28), GOLD)
        if u > f1:
            m = fade((u - f1) / 0.25); pts = []
            for i in range(int(300 * m) + 1):
                x = i / 300; pts.append((x0 + (x1 - x0) * x, y1 - (y1 - y0) * curve(x)))
            if len(pts) > 1: d.line(pts, fill=WATER2, width=6)
            if m > 0.55: d.text((x0 + (x1 - x0) * 0.50, y1 - (y1 - y0) * curve(0.5) - 30), '急に増える！', font=Fo(36), fill=GOLD, anchor='mb')
            if m > 0.95: d.text((x0 + (x1 - x0) * 0.89, y1 - (y1 - y0) * curve(0.89) - 30), 'また急に！', font=Fo(36), fill=GOLD, anchor='mb')
        if f2 < u < f3: d.rounded_rectangle((360, 925, 1560, 1000), 16, fill=(10, 14, 24, 235), outline=GOLD, width=3); ctext(d, (960, 962), 'トイレやお風呂を、試合のあとにまとめて使うため（と考えられる）', Fo(34), PALE)
        if u > f3: ctext(d, (960, 962), '水道局は、水の量と水圧を見守っている', Fo(40), PALE, sw=3)
        note(d); foot(d, '※グラフは形の説明のためのイメージ。出典：東京都水道局「サッカーW杯 日本戦の区部配水量の変化」（2022年・2026年）、同局の説明（J-CAST ニュース 2026年6月16日）')
        return im.convert('RGB')
    run(f'{G}/c_real.mp4', dur, fr); return dur, [(t0, 'real')]
def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; b = bg(0.75); k = 'outro'; f1 = frac(k, 'いっぽう'); f2 = frac(k, 'みんなが'); f3 = frac(k, 'あなたの')
    def fr(t):
        u = (t - 0.5) / D['outro']; im = b.copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
        if u < f2:
            ctext(d, (W / 2, 120), 'まとめ', Mi(80), GOLD, sw=3)
            rowbox(d, 330, '下水道（出口）は 大雨用に太い', 'トイレ全員でも 約0.13ミリ', GREEN, 140, 1780, lf=38, vf=50)
            if u > f1: rowbox(d, 500, '水道（入口）は ふだんの使い方用', '満タンまで 約25分', RED, 140, 1780, True, lf=38, vf=50, h=70)
        elif u < f3:
            ctext(d, (W / 2, 150), 'みんなが同時に使うと…', Mi(70), PALE, sw=3)
            for i, (lab, col) in enumerate([('水道（入口）', RED), ('家のトイレ', PALE), ('下水道（出口）', GREEN)]):
                x = 380 + i * 580; d.rounded_rectangle((x - 230, 380, x + 230, 520), 20, fill=(10, 14, 24, 230), outline=col, width=5); ctext(d, (x, 450), lab, Fo(44), col)
                if i < 2: d.polygon([(x + 250, 430), (x + 330, 450), (x + 250, 470)], fill=GREY)
            ctext(d, (380, 590), '先に苦しくなる', Fo(44), RED, sw=3); ctext(d, (1540, 590), 'びくともしない', Fo(44), GREEN, sw=3)
            ctext(d, (W / 2, 780), '出口より先に、入口が苦しくなる', Mi(84), GOLD, sw=4)
        else:
            dd = title_art(im, 1560, 560, 420, t)
            ctext(dd, (700, 330), 'あなたの家のトイレは', Mi(72), PALE, sw=4); ctext(dd, (700, 450), '1回に何リットル？', Mi(80), GOLD, sw=4)
            ctext(dd, (700, 570), 'コメントで教えてください', Fo(48), PALE, sw=3)
            if u > f3 + 0.12:
                dd.rounded_rectangle((700 - 500, 680, 700 + 500, 860), 24, fill=(10, 14, 24, 225), outline=GOLD, width=4)
                ctext(dd, (700, 730), '次に見たい「もしも」は？', Fo(50), PALE); ctext(dd, (700, 810), 'リクエスト募集中！', Fo(44), GOLD)
        note(ImageDraw.Draw(im)); return im.convert('RGB')
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep()
        res['real'] = scene_real(); res['outro'] = scene_outro()
        res['res1'] = scene_card('res1', 'RESULT  1回戦', [('日本中の100万トン', 'ふだんの1日の下水の 約40分の1', GOLD), ('時間にすると', 'いつもの 約40分ぶん', PALE), ('太い管の中', 'すき間だらけのまま', PALE)], f'{G}/c_res1.mp4', big='下水道の勝ち',
                                 sub='※日本の下水処理量 約140億m³/年（国土交通省）→ 1日 約3,800万m³')
        res['res2'] = scene_card('res2', 'RESULT  決勝戦', [('タンクが満タンになるまで', '約1分 → 約25分', GOLD), ('そのあいだ', '水の勢いが弱くなる', PALE), ('マンションの高い階など', '水が出にくくなるかも', PALE)], f'{G}/c_res2.mp4', big='トイレの勝ち',
                                 sub='※7.6万m³ ÷（東京都の1日最大配水量 約448万m³ ÷ 24時間）＝約0.41時間＝約25分（目安。ほかの水の使用は考えない）')
    elif which == 'r1': res['r1'] = scene_r1()
    elif which == 'r2': res['r2'] = scene_r2()
    elif which == 'still':
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        ons, tf, cues, end = r1_times(); caps = caps_for(cues); print('r1', ons, tf, end)
        for vt in (ons[0] + 0.1, tf + 0.4, tf + 3.0, tf + 7.0, end - 0.1): r1_frame(vt, ons, tf, caps).save(f'{G}/stills/r1_{vt:04.1f}.jpg')
        ons, tf, cues, end = r2_times(); caps = caps_for(cues); print('r2', ons, tf, end)
        for vt in (ons[1] + 0.1, tf + 2.0, cues[2][0] + 1.0, end - 0.1): r2_frame(vt, ons, tf, caps, cues[2][0]).save(f'{G}/stills/r2_{vt:04.1f}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
