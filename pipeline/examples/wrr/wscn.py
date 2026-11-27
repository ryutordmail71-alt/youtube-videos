"""世界記録の選手が全員で100m競争したら の場面"""
import json, math, sys, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/air')
import arnd as R, wcont as C
from arnd import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ORANGE, ctext, fade, ease, writer, foot, note
G = '/home/claude/wrr'; D = json.load(open(f'{G}/dur.json'))
ICE = (170, 225, 255); HORSE = (225, 150, 90); CHEE = (235, 200, 60); HPV = (235, 120, 255)
# 選手：名前, 速さ m/s, 色, 記号, 記録の説明
RUN = ('陸上', 100 / 9.58, (255, 110, 90), '走', '100m 9.58秒')
SWIM = ('水泳', 100 / 46.40, CYAN, '泳', '100m自由形 46.40秒')
SKATE = ('スケート', 500 / 33.61, ICE, '滑', '500m 33.61秒')
BIKE = ('自転車', 200 / 8.857, GOLD, '輪', '助走つき200m 8.857秒')
HRS = ('競走馬', 70.35 / 3.6, HORSE, '馬', '最高 時速70.35km')
RUN10 = ('陸上', 10000 / 1571.0, (255, 110, 90), '走', '10,000m 26分11秒')
SKATE10 = ('スケート', 10000 / 745.69, ICE, '滑', '10,000m 12分25秒69')
BIKE10 = ('自転車', 56792 / 3600, GOLD, '輪', '1時間で56.792km')
CHT = ('チーター', 100 / 5.95, CHEE, 'チ', '100m 5.95秒（止まった状態から）')
HPVL = ('人力の乗り物', 144.17 / 3.6, HPV, '秘', 'カバー付き 時速144.17km（助走つき）')
def kmh(v): return v * 3.6
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
# ---- 背景：夜のスタジアム ----
_BG = {}
def stadium_bg(w=W, h=H, k=1.0):
    k = round(k, 2); key = (w, h, k)
    if key in _BG: return _BG[key]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); yy /= h; xx /= w
    c = np.array((10, 16, 34), np.float32) * (1 - yy[..., None]) + np.array((3, 5, 12), np.float32) * yy[..., None]
    for lx in (0.12, 0.38, 0.62, 0.88):   # 照明の光
        g = np.exp(-(((xx - lx) / 0.09) ** 2 + ((yy - 0.02) / 0.12) ** 2)); c += g[..., None] * np.array((70, 80, 100)) * k
    im = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)); _BG[key] = im; return im
def badge(d, x, y, r, sp, a=255):
    col = sp[2]; d.ellipse((x - r, y - r, x + r, y + r), fill=(12, 16, 28, a), outline=col + (a,), width=max(2, int(r * 0.14)))
    ctext(d, (x, y + 2), sp[3], Fo(int(r * 1.05)), col + (a,))
def bob(t, i): return 4 * math.sin(t * 5 + i * 1.7)
# ---- レース画面（共通） ----
X0, X1 = 370, 1560
def race_frame(vt, lanes, dist, simf, title, sub, ons, tf, caps, fmt, footer, ff_lab=None, lane_on=None, extra=None):
    sim = simf(vt); im = stadium_bg().copy(); d = ImageDraw.Draw(im, 'RGBA')
    n = len(lanes); top = 230; lh = min(130, 620 / n); y0 = top + (680 - lh * n) / 2
    d.rectangle((0, 0, W, 120), fill=(2, 6, 14, 235)); ctext(d, (W / 2, 42), title, Fo(40), GOLD); ctext(d, (W / 2, 94), sub, Fb(28), PALE)
    # 距離の目盛り
    for i in range(11):
        x = X0 + (X1 - X0) * i / 10; d.line((x, y0 - 14, x, y0 + lh * n + 4), fill=(255, 255, 255, 30 if 0 < i < 10 else 0), width=2)
        if i in (0, 5, 10): d.text((x, y0 - 22), f'{dist * i / 10:,.0f}m', font=Fb(24), fill=GREY, anchor='ms')
    d.line((X1, y0 - 10, X1, y0 + lh * n + 8), fill=PALE, width=6); d.line((X0, y0 - 10, X0, y0 + lh * n + 8), fill=GREY, width=3)
    order = sorted(range(n), key=lambda i: dist / lanes[i][1]); fin = [i for i in order if sim >= dist / lanes[i][1]]
    for i, sp in enumerate(lanes):
        y = y0 + lh * (i + 0.5); vis = 1.0 if lane_on is None else lane_on(vt, i)
        if vis <= 0: continue
        a = int(255 * vis)
        d.rounded_rectangle((60, y - lh / 2 + 8, W - 60, y + lh / 2 - 8), 14, fill=(255, 255, 255, int(14 * vis)))
        d.text((90, y), sp[0], font=Fo(int(min(40, lh * 0.36))), fill=sp[2] + (a,), anchor='lm')
        pos = min(dist, sp[1] * sim); x = X0 + (X1 - X0) * pos / dist
        if pos > 0:
            tr = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(tr).rounded_rectangle((max(X0, x - 260), y - 9, x, y + 9), 9, fill=sp[2] + (int(120 * vis),)); g_=tr.filter(ImageFilter.GaussianBlur(5)); im.paste(g_, (0, 0), g_)
            d = ImageDraw.Draw(im, 'RGBA')
        badge(d, x, y + (bob(vt, i) if pos < dist else 0), min(44, lh * 0.36), sp, a)
        if i in fin:
            k = fin.index(i); tt = dist / sp[1]
            d.rounded_rectangle((X1 + 30, y - 34, W - 70, y + 34), 12, fill=(10, 14, 24, 235), outline=GOLD if k == 0 else (90, 95, 110), width=3)
            d.text((X1 + 50, y), f'{k + 1}位', font=Fo(30), fill=GOLD if k == 0 else PALE, anchor='lm'); d.text((W - 86, y), fmt(tt), font=Fo(30), fill=PALE, anchor='rm')
        elif pos > 0 and sim > 0: d.text((X1 + 50, y), f'{pos:,.0f}m', font=Fb(28), fill=GREY, anchor='lm')
    if extra: extra(im, vt, sim)
    d = ImageDraw.Draw(im, 'RGBA')
    if sim > 0:
        d.rounded_rectangle((W / 2 - 220, 930 - 50, W / 2 + 220, 930 + 30), 18, fill=(4, 10, 22, 235), outline=GOLD, width=3)
        ts = fmt(sim, True); f1 = BE(72); f2 = Fo(34); tw = f1.getlength(ts) + 8 + (f2.getlength('秒') if fmt is fmt_s else 0)
        d.text((W / 2 - tw / 2, 932), ts, font=f1, fill=PALE, anchor='ls')
        if fmt is fmt_s: d.text((W / 2 + tw / 2, 928), '秒', font=f2, fill=PALE, anchor='rs')
        if ff_lab and ff_lab(vt): ctext(d, (W / 2 + 330, 905), ff_lab(vt), Fo(32), GOLD)
    if ons:
        labs = ['3', '2', '1', 'スタート']
        for i in range(len(ons)):
            a_ = ons[i]; b_ = ons[i + 1] if i + 1 < len(ons) else a_ + 0.9
            if a_ <= vt < b_:
                u = ease((vt - a_) / 0.2); ctext(d, (W / 2, 560), labs[i], (BE(int(220 * (1.3 - 0.3 * u))) if i < 3 else Mi(int(130 * (1.3 - 0.3 * u)))), PALE if i < 3 else GOLD, sw=6)
    cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None)
    if cap:
        f = Fo(54); tw = f.getlength(cap); d.rounded_rectangle((W / 2 - tw / 2 - 40, 1000 - 45, W / 2 + tw / 2 + 40, 1000 + 40), 18, fill=(4, 8, 16, 240), outline=GOLD, width=3); ctext(d, (W / 2, 998), cap, f, GOLD)
    note(d); d.text((24, H - 8), footer, font=Fb(18), fill=(200, 200, 205), anchor='ls')
    return im.convert('RGB')
def fmt_s(t, timer=False): return f'{t:.2f}' if timer else f'{t:.2f}秒'
def fmt_hms(t, timer=False):
    m = int(t // 60); s = t - m * 60
    return f'{m}:{int(s):02d}' if timer else f'{m}分{int(round(s)):02d}秒'
def caps_for(cues): return [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in cues if k in C.CAP]
def interp(x, xs, ys): return float(np.interp(x, xs, ys))
def race_times(key, kb, kc, kd):
    """kb/kc/kd：(sim 時刻, 最低の実時間間隔)"""
    ons = [0.2 + o for o in onsets(key + 'a')]; tf = ons[3]; t0 = tf + 0.6
    tb = max(0.2 + D[key + 'a'] + 0.3, t0 + kb[1]); tc = max(tb + D[key + 'b'] + 0.3, t0 + kc[1]); td = max(tc + D[key + 'c'] + 0.4, tc + kd[1])
    end = td + D[key + 'd'] + 0.9
    cues = [(0.2, key + 'a'), (tb, key + 'b'), (tc, key + 'c'), (td, key + 'd')]
    th = tc + D[key + 'c'] * 0.7; xs = [t0, tb, tc, th, td, end]; ys = [0, kb[0], kc[0], kc[0] + (kd[0] - kc[0]) * 0.02, kd[0], kd[0] * 1.002]
    return ons, tf, cues, end, (lambda vt: 0.0 if vt < t0 else interp(vt, xs, ys))
R1 = dict(lanes=[BIKE, HRS, SKATE, RUN, SWIM], dist=100)
def r1_parts():
    ons, tf, cues, end, simf = race_times('r1', (100 / BIKE[1], 100 / BIKE[1] * 1.0), (9.58, 9.58 * 1.0), (46.40, 5.0))
    tc = cues[2][0]; ff = lambda vt: '早送り' if vt > tc + 0.5 and simf(vt) < 46.3 else ('スロー' if 0 < simf(vt) < 9.5 and vt < tc else None)
    return ons, tf, cues, end, simf, ff
def r1_frame(vt, P):
    ons, tf, cues, end, simf, ff = P
    return race_frame(vt, R1['lanes'], 100, simf, '1回戦　100m', 'それぞれの世界記録の 平均の速さで進む（水泳は同じ長さのプール）', ons, tf, caps_for(cues), fmt_s,
                      '※平均の速さ＝記録の距離÷記録のタイム。自転車は助走つきの記録、競走馬は記録された最高速度。単純化した目安です', ff_lab=ff)
R2 = dict(lanes=[BIKE10, SKATE10, RUN10], dist=10000)
def r2_parts():
    ons, tf, cues, end, simf = race_times('r2', (10000 / BIKE10[1], 4.5), (10000 / SKATE10[1], 0), (1571.0, 2.2))
    return ons, tf, cues, end, simf, (lambda vt: '早送り' if 0 < simf(vt) < 1570 else None)
def r2_frame(vt, P):
    ons, tf, cues, end, simf, ff = P
    return race_frame(vt, R2['lanes'], 10000, simf, '2回戦　10,000m', '長い距離の世界記録の 平均の速さで（競走馬と水泳は記録がないのでお休み）', ons, tf, caps_for(cues), fmt_hms,
                      '※自転車：1時間で56.792km（アワーレコード）、スケート：10,000m 12分25秒69、陸上：10,000m 26分11秒00。単純化した目安です', ff_lab=ff)
R3 = dict(lanes=[HPVL, BIKE, HRS, CHT], dist=100)
def r3_parts():
    ons, tf, cues, end, simf = race_times('r3', (100 / HPVL[1], 100 / HPVL[1] * 1.6), (100 / HRS[1], 100 / HRS[1] * 1.6), (5.95, 1.0))
    f_hpv = frac('r3a', 'そして、人間側') * D['r3a'] + 0.2; f_ch = frac('r3a', '動物の代表') * D['r3a'] + 0.2
    def lane_on(vt, i):
        if i == 0: return ease((vt - f_hpv) / 0.4)
        if i >= 2: return ease((vt - f_ch) / 0.4)
        return 1.0
    return ons, tf, cues, end, simf, (lambda vt: 'スロー' if 0 < simf(vt) < 5.9 else None), lane_on
def r3_frame(vt, P):
    ons, tf, cues, end, simf, ff, lane_on = P
    return race_frame(vt, R3['lanes'], 100, simf, '決勝戦　100m　人間 vs 動物', '人間代表：自転車＋秘密兵器　動物代表：チーター・競走馬', ons, tf, caps_for(cues), fmt_s,
                      '※人力の乗り物とチーターの記録はギネス世界記録などより。自転車・人力の乗り物は助走つき、チーターは止まった状態から。単純化した目安です', ff_lab=ff, lane_on=lane_on)
def scene_race(nm):
    P = globals()[nm + '_parts'](); fr = globals()[nm + '_frame']; end = P[3]; cues = P[2]
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
    run(f'{G}/c_{nm}.mp4', end, lambda t: fr(t, P)); json.dump(dict(ons=P[0], tf=P[1], cues=cues), open(f'{G}/c_{nm}_t.json', 'w')); return end, cues
# ---- 静的な場面 ----
ALL = [RUN, SWIM, SKATE, BIKE, HRS]
def scene_title():
    dur = 0.5 + D['intro'] + 0.4; k = 'intro'; fq = [frac(k, '陸上'), frac(k, '水泳'), frac(k, 'スケート？'), frac(k, '競走馬')]; f4 = frac(k, '実際')
    def fr(t):
        im = stadium_bg(k=1.0 + 0.15 * math.sin(t * 2)).copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.5)
        for i, sp in enumerate(ALL):   # 右側：走りつづける5人
            y = 230 + i * 130; d.rounded_rectangle((1060, y - 50, 1860, y + 50), 14, fill=(255, 255, 255, 12))
            x = 1100 + ((t * kmh(sp[1]) * 9 + i * 97) % 720); d.rounded_rectangle((max(1080, x - 200), y - 8, x, y + 8), 8, fill=sp[2] + (90,)); badge(d, x, y + bob(t, i), 38, sp)
        d.rounded_rectangle((90, 110, 590, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (340, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (90, 300), '世界記録の選手が', Mi(int(84 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.3: ctext(d, (90, 440), '全員で100m競争', Mi(104), PALE, 'lm', 7)
        if t > 0.6: ctext(d, (90, 590), '1位は 誰？', Mi(130), GOLD, 'lm', 7)
        if t > 0.9: ctext(d, (96, 690), 'IF ALL THE WORLD RECORD HOLDERS RACED 100M TOGETHER', Fb(26), (225, 225, 230), 'lm', 2)
        uu = (t - 0.5) / D['intro']
        for i, (ff, sp) in enumerate(zip(fq, [RUN, SWIM, SKATE, HRS])):
            if uu > ff: x = 90 + i * 240; d.rounded_rectangle((x, 790, x + 220, 870), 16, fill=(4, 12, 26, 230), outline=sp[2], width=3); ctext(d, (x + 110, 830), sp[0] + '？', Fo(34), PALE)
        if uu > f4: ctext(d, (90, 950), '3つの勝負で 確かめる', Fo(44), GOLD, 'lm', 3)
        note(d, size=20); return im.convert('RGB')
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.5, 'intro')]
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.5; k = 'data'
    rows = [(frac(k, '陸上の'), RUN), (frac(k, '水泳の'), SWIM), (frac(k, 'スピード'), SKATE), (frac(k, '自転車の'), BIKE), (frac(k, '競走馬の'), HRS)]
    def fr(t):
        im = stadium_bg().copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '選手しょうかい', Mi(68), GOLD, sw=3); ctext(d, (1500, 170), '時速にすると', Fo(30), GREY)
        for r, (tr, sp) in enumerate(rows):
            if u < tr: continue
            q = ease((u - tr) * dd / 0.8); y = 260 + r * 150
            d.rounded_rectangle((80, y - 62, W - 80, y + 62), 18, fill=(8, 12, 24, 230), outline=sp[2], width=3 if r == len([1 for a, _ in rows if u >= a]) - 1 else 0)
            badge(d, 150, y, 44, sp); d.text((220, y - 22), sp[0], font=Fo(42), fill=sp[2], anchor='lm'); d.text((220, y + 30), sp[4], font=Fb(30), fill=PALE, anchor='lm')
            bw = 620 * kmh(sp[1]) / 82 * q; d.rounded_rectangle((900, y - 20, 900 + max(8, bw), y + 20), 10, fill=sp[2])
            d.text((1820, y), f'約{kmh(sp[1]) * q:.0f}km/h', font=Fo(44), fill=PALE, anchor='rm')
        note(d); foot(d, '※陸上・水泳・スケート・自転車は男子の世界記録。競走馬はギネス世界記録の最高速度（約400mの区間）。時速は計算した目安')
        return im.convert('RGB')
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]
def scene_rule():
    dur = 0.5 + D['rule'] + 0.6; k = 'rule'
    RULES = [('速さ', '世界記録の「平均の速さ」で ずっと進む', frac(k, '全員が')), ('水泳', '同じ長さのプールを泳ぐ', frac(k, '水泳の')),
             ('1回戦', '100m', frac(k, '一回戦')), ('2回戦', '10,000m', frac(k, '二回戦')), ('決勝戦', '秘密兵器が登場！', frac(k, 'そして決勝'))]
    def fr(t):
        im = stadium_bg().copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 90), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 160), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 210 + r * 140; hl = r == 4
            d.rounded_rectangle((140, y, W - 140, y + 110), 18, fill=(8, 12, 24, 230), outline=GOLD if hl else (90, 100, 120), width=3)
            d.rounded_rectangle((170, y + 22, 430, y + 88), 14, fill=GOLD if hl else BLUE); ctext(d, (300, y + 55), who, Fo(34), (10, 14, 24))
            d.text((470, y + 55), txt, font=Fo(46), fill=GOLD if hl else PALE, anchor='lm')
            if hl: ctext(d, (W - 260, y + 55), '？', Mi(80 + int(8 * math.sin(t * 6))), HPV, sw=3)
        note(d); foot(d, '※スタートの反応・加速・カーブなどは考えない、単純化した空想のシミュレーションです')
        return im.convert('RGB')
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]
def rank_card(key, title, big, rows, out, sub, extra=None, bigcol=GOLD):
    """rows: (phrase, 順位文字, sp, 値の文字)"""
    dur = 0.6 + D[key] + 0.5; b = stadium_bg().filter(ImageFilter.GaussianBlur(2))
    def fr(t):
        im = b.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.4)
        ctext(d, (W / 2, 150), title, Fb(38), (220, 220, 225)); ctext(d, (W / 2, 270), big, Mi(int(100 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (ph, rk, sp, val) in enumerate(rows):
            if t < 0.6 + D[key] * frac(key, ph): continue
            q = ease((t - 0.6 - D[key] * frac(key, ph)) / 0.3); y = 410 + r * 112; x0 = W / 2 - 760 + 80 * (1 - q)
            d.rounded_rectangle((x0, y - 48, x0 + 1520, y + 48), 16, fill=(8, 12, 24, 235), outline=GOLD if r == 0 else None, width=3 if r == 0 else 0)
            d.text((x0 + 40, y), rk, font=Fo(44), fill=GOLD if r == 0 else PALE, anchor='lm'); badge(d, x0 + 220, y, 36, sp)
            d.text((x0 + 280, y), sp[0], font=Fo(44), fill=sp[2], anchor='lm'); d.text((x0 + 1480, y), val, font=Fo(48), fill=PALE, anchor='rm')
        if extra: extra(im, t)
        d = ImageDraw.Draw(im, 'RGBA'); foot(d, sub, size=18); note(d)
        return im.convert('RGB')
    run(out, dur, fr); return dur, [(0.6, key)]
def ex_res1(im, t):
    ta = 0.6 + D['res1'] * frac('res1', '人間の足')
    if t < ta: return
    d = ImageDraw.Draw(im, 'RGBA'); q = ease((t - ta) / 0.4)
    d.rounded_rectangle((W / 2 - 620, 960 - 50, W / 2 + 620, 960 + 50), 18, fill=(50, 40, 8, 235), outline=GOLD, width=3)
    ctext(d, (W / 2, 958), f'自転車は 陸上の 約{2.16 * q:.1f}倍の速さ', Fo(50), GOLD)
def ex_res2(im, t):
    ta = 0.6 + D['res2'] * frac('res2', 'でも、')
    if t < ta: return
    d = ImageDraw.Draw(im, 'RGBA'); s = 1 + 0.06 * math.sin(t * 6)
    ctext(d, (W / 2, 965), '速さを比べると…？', Mi(int(64 * s)), RED, sw=3)
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 0.6; k = 'reveal'
    f1 = frac(k, '走る選手'); f2 = frac(k, 'スケートや'); f3 = frac(k, 'ところが'); f4 = frac(k, '空気の抵抗は'); f5 = frac(k, '自転車の選手の')
    def fr(t):
        im = stadium_bg().copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '速さの差を生むのは？', Mi(70), GOLD, sw=3)
        panels = [(f1, '走る', RUN), (f2, 'すべる・転がる', BIKE), (f3, '新しい敵：空気', None)]
        for i, (ff, lab, sp) in enumerate(panels):
            x = 330 + i * 630; on = u >= ff
            d.rounded_rectangle((x - 285, 170, x + 285, 760), 22, fill=(8, 12, 24, 235 if on else 110), outline=(sp[2] if sp else RED) if on else (60, 70, 90), width=4)
            if not on: ctext(d, (x, 450), '？', Mi(120), (80, 90, 110)); continue
            ctext(d, (x, 220), lab, Fo(44), PALE)
            if i < 2:
                pts = []
                for j in range(60):
                    xx = x - 240 + j * 8; ph = (xx - x) / 40 - t * 6
                    yy = 520 - (abs(math.sin(ph)) * 110 if i == 0 else 4 * math.sin(ph * 0.5)); pts.append((xx, yy))
                d.line((x - 250, 600, x + 250, 600), fill=GREY, width=3); d.line(pts, fill=sp[2], width=6)
                bx = x + 20; ph = (bx - x) / 40 - t * 6; by = 520 - (abs(math.sin(ph)) * 110 if i == 0 else 4 * math.sin(ph * 0.5)); badge(d, bx, by - 40, 36, sp)
                ctext(d, (x, 680), '一歩ごとに 体が上下 → むだ' if i == 0 else '体が上下しない → 速い', Fo(32), RED if i == 0 else GREEN)
            else:
                for j in range(7):
                    yy = 330 + j * 50; L = 80 + 120 * (0.5 + 0.5 * math.sin(t * 3 + j)); xx = x + 200 - ((t * 400 + j * 70) % 380)
                    d.line((xx, yy, xx - L * 0.6, yy), fill=(170, 200, 255, 170), width=5)
                badge(d, x - 160, 430, 40, BIKE)
                if u > f4:
                    q = ease((u - f4) * dd / 0.6)
                    d.text((x - 250, 600), '速さ 2倍', font=Fo(36), fill=PALE, anchor='lm'); d.text((x + 250, 600), '抵抗 4倍', font=Fo(44), fill=RED, anchor='rm')
                    for m in range(4): d.rectangle((x + 40 + m * 52, 690 - 50 * q, x + 84 + m * 52, 690), fill=RED)
                    d.rectangle((x - 230, 690 - 50 * q, x - 186, 690), fill=PALE); d.rectangle((x - 176, 690 - 50 * q, x - 132, 690), fill=PALE)
        if u > f5:
            d.rounded_rectangle((260, 820, 1660, 930), 18, fill=(50, 10, 16, 235), outline=RED, width=3)
            ctext(d, (W / 2, 873), '自転車の力の ほとんどは 空気を押しのけるのに使われる', Fo(44), PALE)
        note(d); foot(d, '※空気の抵抗は速さの2乗に比例。競技の自転車では、力の大部分（約8〜9割とされる）が空気の抵抗に使われる（目安）')
        return im.convert('RGB')
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]
SW = [(BIKE, BIKE10, '自転車は'), (RUN, RUN10, '陸上は'), (SKATE, SKATE10, 'スケートは')]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 0.8; k = 'sweep'
    def fr(t):
        u = (t - t0) / dd; im = stadium_bg().copy(); d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 75), '距離が長くなると 速さは？', Mi(64), GOLD, sw=3)
        d.rounded_rectangle((640, 150, 700, 180), 6, fill=(150, 150, 160)); d.text((715, 165), '短い距離（100〜500m）', font=Fb(28), fill=GREY, anchor='lm')
        d.rounded_rectangle((1110, 150, 1170, 180), 6, fill=GOLD); d.text((1185, 165), '長い距離（約10km）', font=Fb(28), fill=GREY, anchor='lm')
        for r, (a, b, ph) in enumerate(SW):
            fr_ = frac(k, ph)
            if u < fr_: continue
            q = ease((u - fr_) * dd / 1.5); y = 300 + r * 230; sp = a
            d.rounded_rectangle((80, y - 90, W - 80, y + 90), 20, fill=(8, 12, 24, 230), outline=GOLD if r == 2 else None, width=4 if r == 2 else 0)
            badge(d, 160, y, 44, sp); d.text((225, y), sp[0], font=Fo(46), fill=sp[2], anchor='lm')
            sc = 900 / 82; v1, v2 = kmh(a[1]), kmh(b[1]); vv = v1 + (v2 - v1) * q
            d.rounded_rectangle((520, y - 60, 520 + v1 * sc, y - 12), 10, fill=(150, 150, 160)); d.text((530 + v1 * sc, y - 36), f'{v1:.0f}km/h', font=Fo(34), fill=PALE, anchor='lm')
            d.rounded_rectangle((520, y + 12, 520 + vv * sc, y + 60), 10, fill=sp[2]); d.text((530 + vv * sc, y + 36), f'{vv:.0f}km/h', font=Fo(34), fill=PALE, anchor='lm')
            if q > 0.95:
                drop = (1 - v2 / v1) * 100; ctext(d, (1700, y), f'-{drop:.0f}%', Mi(80), RED if drop > 20 else GREEN, sw=3)
        if u > frac(k, 'すべる競技'):
            d.rounded_rectangle((360, 960, 1560, 1040), 18, fill=(10, 40, 20, 235), outline=GREEN, width=3); ctext(d, (W / 2, 998), 'すべる競技は 長くても 速さが落ちにくい', Fo(44), GREEN)
        note(d); d.text((24, H - 8), '※短い距離＝1回戦の速さ、長い距離＝2回戦の速さ（各競技の世界記録から計算した目安）', font=Fb(18), fill=(200, 200, 205), anchor='ls')
        return im.convert('RGB')
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]
def ex_res3(im, t):
    ta = 0.6 + D['res3'] * frac('res3', 'ただし')
    d = ImageDraw.Draw(im, 'RGBA')
    if t < ta:
        tb = 0.6 + D['res3'] * frac('res3', '動かして')
        if t > tb: d.rounded_rectangle((W / 2 - 620, 910, W / 2 + 620, 1010), 18, fill=(40, 12, 50, 235), outline=HPV, width=3); ctext(d, (W / 2, 958), 'こいでいるのは 人間の脚の力だけ', Fo(50), HPV)
    else:
        d.rounded_rectangle((W / 2 - 760, 910, W / 2 + 760, 1010), 18, fill=(30, 30, 40, 235), outline=GREY, width=3); ctext(d, (W / 2, 958), 'チーター＝止まった状態から　自転車・人力の乗り物＝助走つき', Fo(42), PALE)
def scene_outro():
    dur = 0.5 + D['outro'] + 1.1; k = 'outro'; f1 = frac(k, '百メートル'); f2 = frac(k, '長い距離'); f3 = frac(k, 'そして'); f5 = frac(k, 'あなたなら')
    def fr(t):
        u = (t - 0.5) / D['outro']; im = stadium_bg().copy(); d = ImageDraw.Draw(im, 'RGBA')
        if u < f5:
            ctext(d, (W / 2, 110), 'まとめ', Mi(80), GOLD, sw=3); ctext(d, (W / 2, 220), '世界記録の選手が 全員で競争したら？', Fo(50), PALE)
            for i, (ff, lab, ans, sub, sp) in enumerate([(f1, '100mの1位', '自転車', '4.4秒', BIKE), (f2, '長い距離', 'スケート', '速さが落ちにくい', SKATE), (f3, '決勝戦', '人力の乗り物', 'チーターより速い', HPVL)]):
                x = 420 + i * 540
                if u < ff:
                    d.rounded_rectangle((x - 250, 300, x + 250, 760), 22, fill=(8, 12, 24, 120), outline=(60, 70, 90), width=4); ctext(d, (x, 380), lab, Fo(44), GREY); ctext(d, (x, 580), '？', Mi(130), (80, 90, 110)); continue
                d.rounded_rectangle((x - 250, 300, x + 250, 760), 22, fill=(8, 12, 24, 235), outline=sp[2], width=4)
                ctext(d, (x, 380), lab, Fo(44), PALE); badge(d, x, 500, 60, sp); ctext(d, (x, 620), ans, Mi(64 if len(ans) < 5 else 52), sp[2], sw=3); ctext(d, (x, 700), sub, Fo(34), PALE)
            if u > frac(k, '速さを決める'):
                d.rounded_rectangle((W / 2 - 640, 820, W / 2 + 640, 930), 22, fill=(50, 40, 8, 235), outline=GOLD, width=4); ctext(d, (W / 2, 875), '速さを決めるのは 筋肉・体の動かし方・空気', Mi(52), PALE)
        else:
            for i, sp in enumerate(ALL + [HPVL]):
                a = 2 * math.pi * i / 6 + t * 0.4; badge(d, 1450 + 260 * math.cos(a), 520 + 260 * math.sin(a), 54, sp)
            ctext(d, (700, 360), 'あなたなら', Mi(70), PALE, sw=4); ctext(d, (700, 480), 'どの世界記録と勝負する？', Mi(70), GOLD, sw=4)
            ctext(d, (700, 600), 'コメントで教えてください', Fo(48), PALE, sw=3)
            if u > f5 + 0.2:
                d.rounded_rectangle((700 - 520, 700, 700 + 520, 870), 24, fill=(8, 12, 24, 225), outline=GOLD, width=4)
                ctext(d, (700, 750), '次に勝負させてほしい 2つは？', Fo(44), PALE); ctext(d, (700, 825), 'リクエスト募集中！', Fo(44), GOLD)
        note(ImageDraw.Draw(im)); return im.convert('RGB')
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]
def statics():
    res = {}
    res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
    res['res1'] = rank_card('res1', 'RESULT  1回戦　100m', '1位は 自転車', [('一位は', '1位', BIKE, '4.4秒'), ('二位は', '2位', HRS, '5.1秒'), ('三位は', '3位', SKATE, '6.7秒'), ('三位は', '4位', RUN, '9.58秒'), ('三位は', '5位', SWIM, '46.40秒')],
                            f'{G}/c_res1.mp4', '※100m÷各記録の平均の速さで計算した目安（自転車 4.43秒、競走馬 5.12秒、スケート 6.72秒）', extra=ex_res1)
    res['res2'] = rank_card('res2', 'RESULT  2回戦　10,000m', '順番は 同じ', [('順番は', '1位', BIKE10, '10分34秒'), ('順番は', '2位', SKATE10, '12分26秒'), ('順番は', '3位', RUN10, '26分11秒'), ('競走馬と', '休み', HRS, '記録なし'), ('競走馬と', '休み', SWIM, '記録なし')],
                            f'{G}/c_res2.mp4', '※自転車は1時間56.792kmの速さで10km＝約10分34秒（計算）。スケート 12分25秒69、陸上 26分11秒00 は10,000mの世界記録', extra=ex_res2)
    res['res3'] = rank_card('res3', 'RESULT  決勝戦　100m', '1位は 人力の乗り物', [('一位は', '1位', HPVL, '2.50秒'), ('一位は', '2位', BIKE, '4.43秒'), ('一位は', '3位', HRS, '5.12秒'), ('一位は', '4位', CHT, '5.95秒')],
                            f'{G}/c_res3.mp4', '※人力の乗り物：200m 時速144.17km（2016年、IHPVA公認）。チーター：100m 5.95秒（2012年、ギネス世界記録）', extra=ex_res3, bigcol=HPV)
    return res
if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static': res = statics()
    elif which in ('r1', 'r2', 'r3'): res[which] = scene_race(which)
    elif which == 'still':
        os.makedirs(f'{G}/stills', exist_ok=True)
        for nm in ('r1', 'r2', 'r3'):
            P = globals()[nm + '_parts'](); ons, tf, cues, end = P[0], P[1], P[2], P[3]; print(nm, tf, end, [round(c[0], 1) for c in cues])
            for vt in (2.0, ons[0] + 0.1, tf + 0.3, cues[1][0] + 0.5, cues[2][0] + 0.5, cues[3][0] + 0.5, end - 0.1): globals()[nm + '_frame'](vt, P).resize((960, 540)).save(f'{G}/stills/{nm}_{vt:04.1f}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
