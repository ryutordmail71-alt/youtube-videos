import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import hrender as R, hmodel as HM, hcontent as C
from hrender import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ORANGE, ctext, fade, ease, writer
G = '/home/claude/hole'; D = json.load(open(f'{G}/dur.json'))
TP1 = 2 * HM.t_center(HM.VP) / 60; TU1 = 2 * HM.t_center(HM.VU) / 60      # 反対側までの分（本当の地球 / 中身が同じ地球）
AIR_C = 45.79 * 60                                                          # 空気の人が中心に着く（分）
def dark_bg(): return Image.new('RGB', (W, H), (8, 10, 20))
def sbg(dark=1.0): return ImageEnhance.Brightness(R.space_bg()).enhance(dark)
def foot(d, s): d.text((W - 24, H - 16), s, font=Fb(20), fill=(200, 200, 205), anchor='rs')
def rowbox(d, y, lab, val, col, x0=W / 2 - 600, x1=W / 2 + 600, hl=False, lf=40, vf=60):
    d.rounded_rectangle((x0, y - 55, x1, y + 55), 18, fill=(10, 12, 18, 230), outline=GOLD if hl else None, width=4 if hl else 0)
    d.text((x0 + 40, y), lab, font=Fo(lf), fill=PALE, anchor='lm'); d.text((x1 - 40, y), val, font=Fo(vf), fill=col, anchor='rm')
def run(out, dur, fn):
    p = writer(out)
    for f in range(int(dur * FPS)):
        im = fn(f / FPS); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

# ---- 落ちる人の状態（st：飛びこんでからの分）----
def person(kind, st):
    """返り値：x（中心からの符号付き距離 m、+が北極側）, 速さ m/s, 重力 m/s², 到着したか"""
    if kind == 'air':
        x, v = HM.air_state(st * 60); return x, v, HM.g_prem(x), False
    prem = kind == 'prem'; T1 = TP1 if prem else TU1
    if st >= T1: return -HM.R, 0.0, HM.G0, True
    x, v, g = HM.state(st * 60, prem); return x, v, g, False
NAMES = {'uni': '教科書の地球（中身が同じ）', 'prem': '本当の地球', 'vac': '真空の穴', 'air': '空気の入った穴'}
KIND = {'uni': 'uni', 'prem': 'prem', 'vac': 'prem', 'air': 'air'}
COLS = {'uni': (150, 200, 255), 'prem': (255, 170, 110), 'vac': (255, 170, 110), 'air': (150, 230, 200)}
def battle_frame(pair, st, title, cap=None, capcol=PALE, vt=0.0, ff=False):
    im = R.space_bg().copy(); d = ImageDraw.Draw(im, 'RGBA'); stt = max(0.0, st)
    for i, who in enumerate(pair):
        cx, cy, rad = 480 + i * 960, 515, 300
        R.draw_earth(im, cx, cy, rad, uniform=(who == 'uni')); d = ImageDraw.Draw(im, 'RGBA')
        d.text((cx - 24, cy - rad + 6), '北極', font=Fb(24), fill=PALE, anchor='rt', stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((cx - 24, cy + rad - 6), '南極（出口）', font=Fb(24), fill=PALE, anchor='rb', stroke_width=3, stroke_fill=(0, 0, 0))
        x, v, g, arr = person(KIND[who], stt) if st >= 0 else (HM.R, 0, HM.G0, False)
        y = cy - x / HM.R * rad
        if arr: y = cy + rad + 22
        if st < 0: y = cy - rad - 26
        R.faller(d, cx, y, 22, vt, COLS[who], glow=fade(v / 9000) * 0.8)
        if arr:
            d.rounded_rectangle((cx + 30, cy + rad - 10, cx + 330, cy + rad + 44), 12, fill=(30, 110, 50)); ctext(d, (cx + 180, cy + rad + 17), f'到着 {R.hms(TP1 if KIND[who] == "prem" else TU1)}', Fo(30), PALE)
        if who == 'air' and stt >= AIR_C:
            d.rounded_rectangle((cx + 30, cy - 30, cx + 360, cy + 30), 12, fill=(160, 30, 40)); ctext(d, (cx + 195, cy), '中心で止まった', Fo(32), PALE)
    d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 235))
    ctext(d, (W / 2, 36), title, Fo(36), GOLD)
    if st < 0: ctext(d, (W / 2, 90), '飛びこむ準備…', Fo(36), PALE)
    else:
        d.text((W / 2 + 20, 92), R.hms(stt), font=Fo(46) if stt >= 60 else BE(60), fill=PALE, anchor='rm')
        d.text((W / 2 + 32, 96), '経過（早送り）' if not ff else '経過（超早送り ▶▶）', font=Fb(26), fill=RED if ff else GREY, anchor='lm')
    d.rectangle((0, 850, W, H), fill=(10, 12, 20, 240))
    for i, who in enumerate(pair):
        x0 = 40 + i * 960; x, v, g, arr = person(KIND[who], stt) if st >= 0 else (HM.R, 0, HM.G0, False)
        d.text((x0, 885), NAMES[who], font=Fo(34), fill=COLS[who], anchor='lm')
        left = 0 if arr else (x + HM.R) / 1000
        d.text((x0, 950), '出口まで', font=Fb(26), fill=GREY, anchor='lm'); d.text((x0 + 120, 952), f'{left:,.0f}', font=BE(70), fill=PALE, anchor='lm'); d.text((x0 + 120 + BE(70).getlength(f'{left:,.0f}') + 8, 960), 'km', font=Fo(30), fill=GREY, anchor='lm')
        sp = f'{R.kmh(v):,.0f}'; sc = GOLD if v > 7000 else PALE
        d.text((x0 + 480, 950), '速さ 時速', font=Fb(26), fill=GREY, anchor='lm'); d.text((x0 + 600, 952), sp, font=BE(70), fill=sc, anchor='lm'); d.text((x0 + 600 + BE(70).getlength(sp) + 8, 960), 'km', font=Fo(30), fill=GREY, anchor='lm')
        d.text((x0, 1025), '重力', font=Fb(26), fill=GREY, anchor='lm'); gc = RED if g > HM.G0 * 1.03 else PALE
        R.bar(d, x0 + 80, 1025, x0 + 700, g / 11.0, gc, 22); d.text((x0 + 880, 1025), f'{g:.1f} m/s²', font=Fo(34), fill=gc, anchor='rm')
        lx = x0 + 80 + 620 * HM.G0 / 11.0; d.line((lx, 1008, lx, 1042), fill=GOLD, width=3); d.text((lx, 1046), '地上', font=Fb(18), fill=GOLD, anchor='mt')
    if cap:
        fnt = Fo(48); tw = fnt.getlength(cap)
        d.rounded_rectangle((W / 2 - tw / 2 - 36, 130, W / 2 + tw / 2 + 36, 204), 16, fill=(8, 10, 16, 230)); ctext(d, (W / 2, 167), cap, fnt, capcol)
    d.text((W - 16, H - 6), R.NOTE, font=Fb(17), fill=(220, 220, 225), anchor='rs')
    return im

def scene_battle(pair, title, pre, stmap, cues, out, endvt, ffrom=None):
    """stmap(vt)→分。cues：(画面の秒, key)"""
    dur = endvt; n = int(dur * FPS)
    for (a, k1), (b, k2) in zip(cues, cues[1:]): assert a + D[k1] < b + 0.05, (k1, a + D[k1], k2, b)
    caps = [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in cues if k in C.CAP]; p = writer(out); sts = []
    for f in range(n):
        vt = f / FPS; st = stmap(vt) if vt >= pre else -1
        cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None)
        col = RED if cap and any(w in cap for w in ('止ま', '速くならない', 'まだ')) else (GOLD if cap else PALE)
        im = battle_frame(pair, st, title, cap, col, vt, ff=(ffrom is not None and vt >= ffrom)); p.stdin.write(im.tobytes()); sts.append(round(st, 3))
    p.stdin.close(); p.wait(); json.dump(dict(st=sts), open(out.replace('.mp4', '_st.json'), 'w')); return dur, cues

# 1回戦：一定の早送り
R1_PRE = D['r1a'] + 0.4; R1_RATE = 1.3
def st1(vt): return (vt - R1_PRE) * R1_RATE
def vt1(st): return R1_PRE + st / R1_RATE
# 決勝：38分までは 2分/秒、そのあと加速して 46時間へ
R2_PRE = D['r2a'] + 0.4; R2_RATE = 3.0; R2_HOLD = R2_PRE + 40 / R2_RATE; R2_LEN = 10.0
def st2(vt):
    if vt < R2_HOLD: return (vt - R2_PRE) * R2_RATE
    q = (vt - R2_HOLD) / R2_LEN; return 40 + (AIR_C + 60 - 40) * (math.exp(4 * min(q, 1.0)) - 1) / (math.exp(4) - 1) + max(0, q - 1) * 30
def vt2(st):
    lo, hi = R2_PRE, R2_HOLD + R2_LEN
    for _ in range(60):
        m = (lo + hi) / 2
        if st2(m) < st: lo = m
        else: hi = m
    return hi

def scene_title():
    dur = 0.6 + D['intro'] + 0.6
    def fr(t):
        im = R.space_bg().copy(); d = R.draw_earth(im, 1480, 560, 420); u = ease(t / 0.5)
        y = 560 - 420 + ((t * 0.08) % 1.0) * 300; R.faller(d, 1480, y, 30, t, (255, 170, 110))
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (100, 330), '地球をつらぬく穴に', Mi(int(96 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (100, 500), '飛びこんだら？', Mi(120), GOLD, 'lm', 8)
        if t > 0.8: ctext(d, (106, 650), 'WHAT IF YOU JUMPED THROUGH THE EARTH?', Fb(32), (225, 225, 230), 'lm', 2)
        if t > 1.0: ctext(d, (100, 770), '反対側まで約42分…のはず？', Fo(50), PALE, 'lm', 3)
        d.text((W - 24, H - 16), R.NOTE, font=Fb(20), fill=(220, 220, 225), anchor='rs'); return im
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]

def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8
    def fr(t):
        im = R.space_bg().copy(); d = R.draw_earth(im, 470, 590, 380, tunnel=False, labels=True); u = (t - t0) / dd
        ctext(d, (W / 2, 70), '地球の中をのぞくと', Mi(68), GOLD, sw=3)
        if u > 0.2:
            d.line((470, 210, 470, 232), fill=RED, width=8); d.line((480, 220, 600, 160), fill=RED, width=3)
            d.text((610, 160), 'コラの穴（約12km）', font=Fo(30), fill=RED, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
        rows = [(0.05, '地球の半径', '約6,370km', PALE, False), (0.18, 'いちばん深い穴（コラ半島）', '約12km', PALE, False), (0.36, '半径とくらべると', 'わずか0.2%', RED, True),
                (0.5, '穴の底の岩の温度', '約180℃', ORANGE, False), (0.65, '中心の温度', '5,000℃以上', RED, True), (0.85, '中心の圧力', '約360万気圧', GOLD, False)]
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 200 + r * 135, lab, val, col, 930, 1870, hl, lf=34, vf=52)
        foot(d, '※コラ超深度掘削坑：1989年に12,262m。中心の温度は研究で幅があります（目安）。圧力はPREMモデルから')
        return im
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]

RULES = [('穴', '北極から南極まで、まっすぐ（自転の影響なし）', 0.03), ('壁', '熱にも圧力にもこわれない、空想の壁', 0.33), ('人', '熱から守る特別な宇宙服を着ている', 0.6),
         ('中', '穴の中は真空（空気なし）', 0.82)]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; bg = sbg(0.7)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 170), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 240 + r * 170; last = r == 3
            d.rounded_rectangle((140, y, W - 140, y + 130), 18, fill=(10, 12, 18, 225), outline=GOLD if last else None, width=4 if last else 0)
            d.rounded_rectangle((170, y + 30, 350, y + 100), 14, fill=RED if last else BLUE); ctext(d, (260, y + 65), who, Fo(38), (20, 20, 24))
            d.text((390, y + 65), txt, font=Fo(48), fill=PALE, anchor='lm')
        foot(d, '※空想のシミュレーションです。本当にこんな穴は掘れません')
        return im
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]

def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None):
    dur = 0.6 + D[key] + 0.8; bg = ImageEnhance.Brightness(R.space_bg().filter(ImageFilter.GaussianBlur(2))).enhance(0.8)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.4)
        ctext(d, (W / 2, 230), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 380), big, Mi(int(120 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 640, y - 48, W / 2 + 640, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 600, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 600, y), val, font=Fo(52), fill=col, anchor='rm')
        if sub: foot(d, sub)
        return im
    run(out, dur, fr); return dur, [(0.6, key)]

def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0
    dens = [('地殻・上のマントル', 3.3, (175, 90, 60)), ('下のマントル（深さ2,900km）', 5.6, (200, 80, 45)), ('外核（液体の鉄）', 9.9, ORANGE), ('中心（固体の鉄）', 13.1, (255, 225, 140))]
    ds = np.linspace(0, 6371, 400); gpv = [HM.g_prem((6371 - x) * 1e3) for x in ds]; guv = [HM.G0 * (6371 - x) / 6371 for x in ds]
    def fr(t):
        im = dark_bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), 'なぜ、本当の地球のほうが速い？', Mi(66), GOLD, sw=3)
        if u < 0.4:
            ctext(d, (W / 2, 190), '1cm³あたりの重さ（密度）', Fo(44), PALE)
            for i, (lab, v, col) in enumerate(dens):
                y = 320 + i * 140; d.text((120, y), lab, font=Fo(40), fill=col, anchor='lm')
                R.bar(d, 760, y, 760 + 900 * v / 13.1 * ease((u - 0.05 - i * 0.06) / 0.1), 1, col, 64)
                d.text((1690, y), f'約{v}g', font=Fo(48), fill=PALE, anchor='lm')
            if u > 0.25: ctext(d, (W / 2, 900), '重いものが、中心に集まっている', Mi(70), GOLD, sw=3)
        else:
            x0, x1, y0, y1 = 220, 1500, 280, 860
            ctext(d, (W / 2, 190), '深さと重力（m/s²）', Fo(44), PALE)
            d.line((x0, y1, x1, y1), fill=GREY, width=3); d.line((x0, y0, x0, y1), fill=GREY, width=3)
            for gv in (0, 5, 10): yy = y1 - gv / 11 * (y1 - y0); d.text((x0 - 14, yy), str(gv), font=Fb(28), fill=GREY, anchor='rm'); d.line((x0, yy, x1, yy), fill=(255, 255, 255, 30), width=1)
            for dk in (0, 2000, 4000, 6371): xx = x0 + dk / 6371 * (x1 - x0); d.text((xx, y1 + 14), f'{dk:,}km', font=Fb(26), fill=GREY, anchor='mt')
            d.text((x1, y1 + 50), '深さ →（6,371km＝中心）', font=Fb(26), fill=GREY, anchor='rt')
            q = ease((u - 0.42) / 0.2); m = max(2, int(len(ds) * q))
            P = lambda arr: [(x0 + ds[i] / 6371 * (x1 - x0), y1 - arr[i] / 11 * (y1 - y0)) for i in range(m)]
            d.line(P(guv), fill=(150, 200, 255), width=6); d.line(P(gpv), fill=ORANGE, width=8)
            d.text((1520, 330), '本当の地球', font=Fo(36), fill=ORANGE, anchor='lm'); d.text((1520, 400), '中身が同じ地球', font=Fo(32), fill=(150, 200, 255), anchor='lm')
            if u > 0.62:
                xx = x0 + 2891 / 6371 * (x1 - x0); yy = y1 - 10.69 / 11 * (y1 - y0); d.ellipse((xx - 14, yy - 14, xx + 14, yy + 14), outline=RED, width=5)
                d.rounded_rectangle((xx + 30, yy - 10, xx + 640, yy + 80), 14, fill=(10, 12, 18, 230)); d.text((xx + 50, yy + 35), '深さ2,900km：地上の約1.09倍', font=Fo(34), fill=RED, anchor='lm')
            if u > 0.82:
                d.rounded_rectangle((520, 950, 1400, 1040), 18, fill=(10, 12, 18, 235), outline=GOLD, width=4); ctext(d, (960, 995), '最高 秒速 約10km（時速 約3万6000km）', Fo(46), GOLD)
        foot(d, '※密度・重力：PREM（Dziewonski & Anderson 1981）から計算。最高速度は真空の穴での計算値')
        return im
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]

SW = [('月', 3.34, 0.10), ('火星', 3.93, 0.2), ('木星', 1.33, 0.3), ('土星', 0.69, 0.4), ('地球（中身が同じ）', 5.51, 0.55), ('地球と同じ密度の小さな星', 5.51, 0.85)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; bg = sbg(0.6); cx = [430, 980, 1500]
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 70), 'ほかの星に穴を掘ったら？', Mi(66), GOLD, sw=3)
        for j, h in enumerate(['星', '密度（1cm³あたり）', '反対側まで']): ctext(d, (cx[j], 165), h, Fo(32), GREY)
        for r, (nm, rho, tr) in enumerate(SW):
            if u < tr: continue
            y = 250 + r * 112; last = r == 5; m = HM.period_uniform(rho * 1000) / 60
            d.rounded_rectangle((80, y - 48, W - 80, y + 48), 16, fill=(10, 12, 18, 230), outline=GOLD if (last or r == 4) and u > 0.85 else None, width=5)
            ctext(d, (cx[0], y), nm, Fo(40 if len(nm) < 10 else 34), PALE); ctext(d, (cx[1], y), f'約{rho:.1f}g', Fo(44), PALE)
            ctext(d, (cx[2], y), f'約{m:.0f}分' if m < 100 else '約2時間', Fo(52), GOLD if last or r == 4 else PALE)
        if u > 0.62: ctext(d, (W / 2, 950), '時間を決めるのは、大きさではなく「密度」！', Mi(60), GOLD, sw=3)
        foot(d, '※中身がどこでも同じとした計算（目安）。時間＝π÷√(4πGρ/3)。木星・土星はガスの星なので本当は掘れません')
        return im
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]

def scene_real():
    t0 = 0.5; dd = D['real']; dur = t0 + dd + 1.0
    def fr(t):
        im = dark_bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        # 地面の断面：深さとともに赤くなる
        for k in range(60):
            y = 300 + k * 10; c = R.mix((90, 70, 55), (230, 80, 30), k / 60); d.rectangle((120, y, 900, y + 10), fill=c)
        d.rectangle((500, 260, 520, 300 + min(1, ease(u / 0.4)) * 600), fill=(10, 10, 14))
        d.polygon([(470, 260), (550, 260), (510, 140)], outline=GREY, width=4)
        ctext(d, (510, 110), 'コラの穴', Fo(36), PALE)
        d.text((540, 905), '深さ 約12km：約180℃', font=Fo(34), fill=ORANGE, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
        ctext(d, (1420, 160), '本当に怖いのは…', Mi(76), RED, sw=3)
        if u > 0.2: rowbox(d, 380, 'コラの穴（1989年）', '深さ12kmで中止', PALE, 980, 1860, lf=34, vf=44)
        if u > 0.38: rowbox(d, 530, '理由', '熱い岩がやわらかくなる', ORANGE, 980, 1860, lf=34, vf=44)
        if u > 0.6: rowbox(d, 680, '中心', '5,000℃以上・約360万気圧', RED, 980, 1860, True, lf=34, vf=44)
        if u > 0.8: ctext(d, (1420, 880), '近づくことすら、できない', Mi(64), PALE, sw=3)
        foot(d, '※コラ超深度掘削坑（ロシア）：12,262m。温度は予想の約100℃より高い約180℃だった')
        return im
    run(f'{G}/c_real.mp4', dur, fr); return dur, [(t0, 'real')]

def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; bg = sbg(0.7)
    def fr(t):
        u = (t - 0.5) / D['outro']; im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA')
        if u < 0.42:
            ctext(d, (W / 2, 120), 'まとめ', Mi(80), GOLD, sw=3)
            rowbox(d, 360, '真空の穴で、反対側まで（本当の地球）', '約38分', GOLD, 200, 1720, True, lf=42, vf=64)
            if u > 0.2: rowbox(d, 540, 'かかる時間を決めるのは', '密度', GOLD, 200, 1720, lf=42, vf=64)
            if u > 0.08: rowbox(d, 720, '空気の入った穴だと', '中心で止まる', RED, 200, 1720, lf=42, vf=56)
        elif u < 0.78:
            d2 = R.draw_earth(im, 620, 560, 400, tunnel=False); d = ImageDraw.Draw(im, 'RGBA')
            a1, a2 = math.radians(-120), math.radians(-60)
            p1 = (620 + 400 * math.cos(a1), 560 + 400 * math.sin(a1)); p2 = (620 + 400 * math.cos(a2), 560 + 400 * math.sin(a2))
            d.line((p1, p2), fill=(10, 10, 14), width=16); d.line((p1, p2), fill=GOLD, width=3)
            d.line(((620, 160), (620, 960)), fill=(10, 10, 14), width=16)
            ctext(d, (p1[0] - 20, p1[1] - 40), '東京', Fo(36), PALE, sw=3); ctext(d, (p2[0] + 20, p2[1] - 40), '大阪', Fo(36), PALE, sw=3)
            ctext(d, (1450, 380), 'どこからどこへ', Mi(64), PALE, sw=3); ctext(d, (1450, 490), 'まっすぐ掘っても', Mi(64), PALE, sw=3)
            ctext(d, (1450, 640), '約42分', Mi(120), GOLD, sw=5); ctext(d, (1450, 760), '（中身が同じ地球なら）', Fo(36), GREY)
            foot(d, '※東京〜大阪のトンネルは、わかりやすく大げさに描いています。摩擦・空気なしの計算')
        else:
            R.draw_earth(im, 1570, 620, 320); d = ImageDraw.Draw(im, 'RGBA')
            ctext(d, (680, 330), 'あなたなら、どこから', Mi(72), PALE, sw=4); ctext(d, (680, 450), 'どこへ掘る？', Mi(84), GOLD, sw=4)
            ctext(d, (680, 570), 'コメントで教えてください', Fo(48), PALE, sw=3)
            if u > 0.92:
                d.rounded_rectangle((680 - 500, 680, 680 + 500, 860), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (680, 730), '次に見たい「もしも」は？', Fo(50), PALE); ctext(d, (680, 810), 'リクエスト募集中！', Fo(44), GOLD)
        return im
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['data'] = scene_data(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep()
        res['real'] = scene_real(); res['outro'] = scene_outro()
        res['res1'] = scene_card('res1', 'RESULT  1回戦', [('本当の地球（反対側まで）', f'約{TP1:.0f}分', GOLD), ('教科書の地球（中身が同じ）', f'約{TU1:.0f}分', PALE), ('差', '約4分 速い', RED)], f'{G}/c_res1.mp4', big='本当の地球の勝ち')
        res['res2'] = scene_card('res2', 'RESULT  決勝戦', [('真空の穴', f'約{TP1:.0f}分で反対側へ', GOLD), ('空気の入った穴', '中心まで 約46時間', PALE), ('そのあと', '中心で止まり、出られない', RED)], f'{G}/c_res2.mp4', big='優勝は真空の穴')
    elif which == 'fix':
        res = json.load(open(f'{G}/scene_static.json')); res['title'] = scene_title(); res['reveal'] = scene_reveal(); res['outro'] = scene_outro(); which = 'static'
    elif which == 'r1':
        end = vt1(TU1) + D['r1f'] + 1.2
        res['r1'] = scene_battle(('uni', 'prem'), '1回戦　教科書の地球 vs 本当の地球', R1_PRE, st1, [(0.2, 'r1a'), (vt1(0.3), 'r1b'), (vt1(12.73), 'r1c'), (vt1(19.09), 'r1d'), (vt1(TP1), 'r1e'), (vt1(TU1), 'r1f')], f'{G}/c_r1.mp4', end)
    elif which == 'r2':
        tC = vt2(AIR_C); end = tC + D["r2e"] + 0.8
        res['r2'] = scene_battle(('vac', 'air'), '決勝戦　真空の穴 vs 空気の入った穴', R2_PRE, st2, [(0.2, 'r2a'), (R2_PRE + 0.3, 'r2b'), (vt2(TP1), 'r2c'), (vt2(TP1) + D['r2c'] + 0.3, 'r2d'), (tC, 'r2e')], f'{G}/c_r2.mp4', end, ffrom=R2_HOLD)
    elif which == 'still':
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        for vt in (5, 12, 20, 30, 38): battle_frame(('uni', 'prem'), st1(vt), '1回戦　教科書の地球 vs 本当の地球', 'テスト', GOLD, vt).save(f'{G}/stills/r1_{vt}.jpg')
        for vt in (12, 25, 33, 38, 40): battle_frame(('vac', 'air'), st2(vt), '決勝戦', None, PALE, vt, vt >= R2_HOLD).save(f'{G}/stills/r2_{vt}.jpg')
        raise SystemExit
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
