"""渋谷にゾンビが1人現れたら（本編の場面）"""
import json, math, sys
sys.path.insert(0, '/home/claude/zmb')
from zbase import *
import zsim
D = json.load(open(f'{G}/dur.json'))
SIM = np.load(f'{G}/sim.npz'); SN = SIM['snaps']; ST = SIM['stats']; TI = SIM['t_inf']
TIL = TI[LAND]
N0 = POP0.sum()
def snap(day):
    f = day * 4; i = int(min(len(SN) - 2, f)); a = f - i
    s = SN[i].astype(np.float32) * (1 - a) + SN[i + 1].astype(np.float32) * a
    hr = day * 24; fr = np.where(TIL <= hr, np.clip(1 - (hr - TIL) / 60.0, 0, 1), 0.0)
    return s[0], s[1], fr
def human_left(day):
    f = day * 4; i = int(min(len(ST) - 2, f)); a = f - i
    return (ST[i, 1] * (1 - a) + ST[i + 1, 1] * a) / N0
def reach_day(name):
    y, x = zsim.cell(*CITIES[name]); return TI[y, x] / 24
MK = 3.4; MOX, MOY = 900, 30
def draw_map(im, d, day=None, k=MK, ox=MOX, oy=MOY, inset=(1700, 880), arr=None):
    if day is None: lay = map_layer(k=k)
    else:
        h, z, fr = snap(day); lay = map_layer(h, z, k, front=fr)
    im.alpha_composite(lay, (int(ox), int(oy)))
    if inset: okinawa_inset(im, d, inset[0], inset[1], k)

def s_title():
    dur = 0.6 + D['intro'] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.8)
        draw_map(im, d, 0, k=3.2, ox=1000, oy=60, inset=None)
        x, y = lonlat_px(*SHIBUYA, 1000, 60, 3.2); p = 0.5 + 0.5 * math.sin(t * 3)
        glow(im, x, y, 26 + 14 * p, (255, 50, 40), 200); d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 90, 80))
        d.line((x, y, x - 120, y + 160), fill=(255, 90, 80), width=3); d.text((x - 125, y + 170), '渋谷', font=Fo(40), fill=(255, 110, 100), anchor='mt')
        d.rounded_rectangle((90, 110, 560, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (325, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (90, 310), '渋谷にゾンビが', Mi(int(96 * (1.15 - 0.15 * u))), PALE, 'lm', 4)
        ctext(d, (90, 440), '1人現れたら', Mi(int(96 * (1.15 - 0.15 * u))), PALE, 'lm', 4)
        ctext(d, (90, 600), '日本は何日で全滅？', Mi(int(104 * (1.15 - 0.15 * u))), GOLD, 'lm', 5)
        ctext(d, (96, 710), 'ONE ZOMBIE IN SHIBUYA. HOW LONG WOULD JAPAN LAST?', Fb(28), GRAY, 'lm')
        if t > 2.0: zombie(d, 300 + (t - 2) * 8, 1000, 240, phase=t * 2.2)
    return scene('title', dur, dr, [(0.6, 'intro')])

def s_data():
    dur = 0.5 + D['data'] + 0.8; dd = D['data']
    cards = [(0.0, 'ゾンビ', ZC, [('歩く速さ', '秒速 約30cm'), ('', '（時速 約1km）'), ('人間の歩く速さの', '約1/4'), ('かみつく強さ', '倒す強さの 約1.25倍')], '1対1で9回戦うと 5勝4敗'),
             (0.58, '日本の人口', HC, [('全体', '約1億2600万人'), ('', '（2020年 国勢調査）'), ('', ''), ('', '')], ''),
             (0.72, '人の多さ（1km²あたり）', GOLD, [('東京都', '約6,400人'), ('北海道', '約60人'), ('', ''), ('', '')], 'ちがいは 約100倍')]
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 80), 'データ', Mi(70), PALE, sw=3)
        for i, (tr, name, col, rows, big) in enumerate(cards):
            if u < tr: continue
            x0 = 80 + i * 600; a = ease((u - tr) * dd / 0.6)
            d.rounded_rectangle((x0, 160, x0 + 560, 960), 22, fill=(12, 8, 14, int(230 * a)), outline=col, width=4)
            ctext(d, (x0 + 280, 215), name, Fo(46 if len(name) < 8 else 38), col)
            if i == 0: zombie(d, x0 + 230, 470, 220, phase=t * 2)
            elif i == 1:
                for k in range(7): person(d, x0 + 90 + k * 65, 460, 150, phase=t * 3 + k)
            else:
                for (yy, n, cc) in [(300, 40, PALE), (420, 3, PALE)]:
                    d.rectangle((x0 + 330, yy - 50, x0 + 430, yy + 50), outline=(120, 120, 130), width=2)
                    rng = np.random.default_rng(n)
                    for _ in range(n): px, py = rng.uniform(5, 95, 2); d.ellipse((x0 + 330 + px - 4, yy - 50 + py - 4, x0 + 330 + px + 4, yy - 50 + py + 4), fill=cc)
                ctext(d, (x0 + 180, 300), '東京都', Fo(36), PALE); ctext(d, (x0 + 180, 420), '北海道', Fo(36), PALE)
            for r, (k, v) in enumerate(rows):
                if not (k or v): continue
                y = 540 + r * 72
                d.text((x0 + 28, y), k, font=Fb(28), fill=GRAY, anchor='lm'); d.text((x0 + 535, y), v, font=Fo(36 if len(v) < 10 else 30), fill=PALE, anchor='rm')
            if big: ctext(d, (x0 + 280, 890), big, Mi(40 if len(big) > 10 else 50), GOLD, sw=2)
        d.text((24, H - 50), '出典：Alemi ほか 2015（Phys. Rev. E 92, 052801：ゾンビ映画にあてはめた数字）、令和2年国勢調査、都道府県の面積（国土地理院）', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('data', dur, dr, [(0.5, 'data')])

def s_rule():
    dur = 0.5 + D['rule'] + 0.8; dd = D['rule']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 90), 'ルール', Mi(80), PALE, sw=3)
        draw_map(im, d, 0, k=2.6, ox=80, oy=200, inset=None)
        x, y = lonlat_px(*SHIBUYA, 80, 200, 2.6); p = 0.5 + 0.5 * math.sin(t * 3)
        glow(im, x, y, 20 + 10 * p, (255, 50, 40), 200); d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 90, 80))
        d.text((x + 20, y + 10), '渋谷に1人', font=Fo(32), fill=(255, 110, 100), anchor='lt', stroke_width=2, stroke_fill=(0, 0, 0))
        rows = [(0.05, '渋谷に、ゾンビが1人'), (0.25, '近くにいる人を見つけて、おそいかかる'), (0.55, 'かまれた人は、ゾンビになる'), (0.75, '日本中の人がゾンビになったら「全滅」')]
        for i, (tr, txt) in enumerate(rows):
            if u < tr: continue
            y = 220 + i * 165
            d.rounded_rectangle((860, y, W - 80, y + 125), 18, fill=(12, 8, 14, 230), outline=GOLD if i == 3 else None, width=4 if i == 3 else 0)
            d.text((900, y + 62), txt, font=Fo(42), fill=PALE, anchor='lm')
    return scene('rule', dur, dr, [(0.5, 'rule')])

# 1回戦：倍々計算。渋谷から近い順に人口をうめる
_dist = None
def naive_mask(nz):
    global _dist
    if _dist is None:
        yy, xx = np.mgrid[0:NY, 0:NX]; sy, sx = zsim.cell(*SHIBUYA); dist = np.hypot(yy - sy, xx - sx); dist[~LAND] = 1e9
        order = np.argsort(dist, axis=None); cum = np.cumsum(POP0.ravel()[order]); _dist = (order, cum)
    order, cum = _dist; n = np.searchsorted(cum, nz); m = np.zeros(NY * NX, bool); m[order[:n + 1]] = True
    return m.reshape(NY, NX)[LAND]
R1T = 9.0
def s_r1():
    cues = [(0.2, 'r1a')]; tj = 0.2 + D['r1a'] - 0.2
    cues += [(tj + 3.2, 'r1b'), (tj + 9.05, 'r1c')]
    dur = cues[-1][0] + D['r1c'] + 1.5; n = int(dur * FPS); p = writer(f'{G}/c_r1.mp4')
    for f in range(n):
        t = f / FPS; im = bg(); d = ImageDraw.Draw(im); q = t - tj
        hr = 0 if q < 0 else min(27.0, 27 * q / R1T); nz = 2 ** hr
        m = naive_mask(nz) if nz > 2 else np.zeros(LAND.sum(), bool)
        h = np.where(m, 0.0, 1.0); z = np.where(m, 0.18, 0.0)
        im.alpha_composite(map_layer(h, z, MK), (MOX, MOY)); okinawa_inset(im, d, 1700, 880, MK, label=False,
                                                                       arr=cells_rgba(h, z) if hr >= 27 else None)
        x, y = lonlat_px(*SHIBUYA, MOX, MOY, MK); glow(im, x, y, 22, (255, 50, 40), 180)
        d.rectangle((0, 0, W, 120), fill=(8, 6, 10, 220))
        ctext(d, (W / 2, 40), '1回戦　よく聞く計算「1時間に1人かむ → 倍々で増える」', Fo(40), GOLD); ctext(d, (W / 2, 92), '1時間ごとに ゾンビが2倍', Fb(30), PALE)
        ctext(d, (450, 300), f'{int(hr)}時間後', Mi(96), PALE, sw=4)
        zs = int(round(nz)) if hr < 27 else 2 ** 27
        lab = f'{zs:,}人' if zs < 10000 else (f'約{zs / 1e4:,.0f}万人' if zs < 1e8 else f'約{zs / 1e8:.2f}億人')
        ctext(d, (450, 450), 'ゾンビ ' + lab, Fo(64), RED, sw=3)
        ctext(d, (450, 560), '日本の人口 約1億2600万人', Fb(36), GRAY)
        bw = 700 * min(1, nz / 1.26e8); d.rounded_rectangle((100, 620, 800, 670), 25, fill=(50, 50, 60)); d.rounded_rectangle((100, 620, 100 + max(50, bw), 670), 25, fill=(200, 40, 40))
        if t >= cues[2][0]: caption(d, '27時間で 日本の人口をこえた！', GOLD, y=820, w=900, fs=48)
        elif t >= cues[1][0]: caption(d, '10時間で 約1000人 → 20時間で 約100万人', PALE, y=820, w=900, fs=40)
        disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(t_jump=tj), open(f'{G}/c_r1_st.json', 'w')); return dur, cues

def card(key, title, big, bigcol, lines, bs=120):
    dur = 0.6 + D[key] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.4)
        ctext(d, (W / 2, 200), title, Fb(38), (215, 215, 220))
        ctext(d, (W / 2, 350), big, Mi(int(bs * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 540 + r * 115
            d.rounded_rectangle((W / 2 - 660, y - 48, W / 2 + 660, y + 48), 16, fill=(12, 8, 14, 225))
            d.text((W / 2 - 620, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 620, y), val, font=Fo(48), fill=col, anchor='rm')
    return scene(key, dur, dr, [(0.6, key)])

def s_secret():
    dur = 0.5 + D['secret'] + 1.0; dd = D['secret']; S1, S2 = 0.46, 0.72
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 80), '種明かし　ぬけていた3つのこと', Mi(64), GOLD, sw=3)
        for i, (lab, tr) in enumerate([('① 人間も反撃する', 0.03), ('② 出会わないと、かめない', S1), ('③ 歩くのが、とても遅い', S2)]):
            if u < tr: continue
            on = (i == 0 and u < S1) or (i == 1 and S1 <= u < S2) or (i == 2 and u >= S2)
            d.rounded_rectangle((60 + i * 610, 160, 650 + i * 610, 240), 16, fill=(12, 8, 14, 230), outline=GOLD if on else None, width=3)
            ctext(d, (355 + i * 610, 200), lab, Fo(36), GOLD if on else GRAY)
        if u < S1:
            zombie(d, 170, 640, 320, phase=t * 2); person(d, 1760, 640, 320, phase=t * 3)
            ctext(d, (W / 2, 330), '1対1で9回戦うと', Fo(44), PALE)
            for k in range(9):
                x = W / 2 - 4 * 90 + k * 90; c = (190, 40, 40) if k < 5 else (80, 140, 230)
                if u > 0.06 + k * 0.012: d.rounded_rectangle((x - 38, 380, x + 38, 450), 12, fill=c); ctext(d, (x, 415), 'ゾ' if k < 5 else '人', Fo(36), PALE)
            ctext(d, (W / 2, 500), 'ゾンビ 5勝 ： 人間 4勝', Fo(48), PALE)
            if u > 0.2:
                d.rounded_rectangle((260, 700, W - 260, 900), 22, fill=(12, 8, 14, 235), outline=GOLD, width=4)
                ctext(d, (W / 2, 760), '最初の1人のゾンビは', Fo(46), PALE)
                ctext(d, (W / 2, 840), '80%の確率で すぐ倒されて おしまい', Mi(60), GOLD, sw=2)
        elif u < S2:
            for (cx, n, lab, sub) in [(560, 260, '人が多い場所', 'すぐ出会う → 増える'), (1360, 8, '人が少ない場所', 'なかなか出会えない')]:
                d.rectangle((cx - 300, 290, cx + 300, 790), outline=(120, 120, 130), width=3)
                rng = np.random.default_rng(n)
                for _ in range(n):
                    px, py = rng.uniform(15, 585), rng.uniform(15, 485); d.ellipse((cx - 300 + px - 6, 290 + py - 6, cx - 300 + px + 6, 290 + py + 6), fill=HC)
                rr = 80 + 10 * math.sin(t * 3); d.ellipse((cx - rr, 540 - rr, cx + rr, 540 + rr), outline=(255, 80, 70), width=4)
                d.ellipse((cx - 14, 526, cx + 14, 554), fill=(200, 40, 40))
                ctext(d, (cx, 840), lab, Fo(48), PALE); ctext(d, (cx, 910), sub, Fb(36), GOLD)
        else:
            q = (u - S2) * dd
            d.rectangle((0, 920, W, 950), fill=(50, 46, 56))
            zx = 200 + q * 25; zombie(d, zx, 920, 240, phase=t * 2.2)
            person(d, 200 + q * 95 + 500, 920, 240, phase=t * 6)
            ctext(d, (W / 2, 330), 'ゾンビ：時速 約1km　　人間：時速 約4km', Fo(50), PALE)
            if u > S2 + 0.08:
                d.rounded_rectangle((300, 420, W - 300, 600), 22, fill=(12, 8, 14, 235), outline=GOLD, width=4)
                ctext(d, (W / 2, 470), '電車が止まれば、休まず歩いても', Fo(44), PALE)
                ctext(d, (W / 2, 550), '1日に 約26km しか進めない', Mi(62), GOLD, sw=2)
        d.text((24, H - 50), '「最初の1人が倒されて終わる確率 ＝ 0.8」：Alemi ほか 2015 のモデル（かむ：倒す ＝ 1.25：1 のとき）', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('secret', dur, dr, [(0.5, 'secret')])

TBL = [('渋谷のような都会の真ん中', '約1万5000人', 1.6, '約1.6時間'), ('住宅地', '約1000人', 1.8, '約1.8時間'), ('北海道の平均くらい', '約60人', 5.0, '約5時間'), ('山の中など', '約5人', 43.0, '約43時間')]
def s_table():
    dur = 0.5 + D['table'] + 1.2; dd = D['table']; rv = [0.2, 0.36, 0.52, 0.72]
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 90), 'ゾンビの数が2倍になるまでの時間', Mi(64), PALE, sw=3)
        d.text((130, 200), '場所', font=Fb(30), fill=GRAY, anchor='lm'); d.text((760, 200), '人の多さ（1km²）', font=Fb(30), fill=GRAY, anchor='mm'); d.text((1360, 200), '2倍になるまで', font=Fb(30), fill=GRAY, anchor='mm')
        for i, (a, b, hrs, lab) in enumerate(TBL):
            if u < rv[i]: continue
            y = 240 + i * 160; aa = ease((u - rv[i]) * dd / 1.0)
            d.rounded_rectangle((100, y, W - 100, y + 130), 18, fill=(12, 8, 14, 230))
            d.text((130, y + 65), a, font=Fo(40), fill=PALE, anchor='lm'); d.text((760, y + 65), b, font=Fo(40), fill=GRAY, anchor='mm')
            bw = 560 * math.log10(1 + hrs) / math.log10(44) * aa
            d.rounded_rectangle((1000, y + 40, 1000 + max(40, bw), y + 90), 25, fill=(200, 45, 40) if hrs < 3 else (130, 60, 60))
            d.text((W - 130, y + 65), lab, font=Fo(46), fill=GOLD if i == 3 else PALE, anchor='rm')
        if u > 0.85:
            d.rounded_rectangle((360, 900, W - 360, 990), 22, fill=(12, 8, 14, 235), outline=GOLD, width=4); ctext(d, (W / 2, 945), '人が少ないほど、ゾンビは増えにくい', Mi(50), GOLD)
        d.text((24, H - 50), '計算：出会う範囲 1時間に約0.03km²（Alemi ほか 2015 の値から換算）、1回の戦いは約15分、5勝4敗とした目安', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('table', dur, dr, [(0.5, 'table')])

def dmap(q):
    """決勝のアニメ：経過秒 → 日数"""
    if q < 0: return 0.0
    if q < 10: return 6.0 * q
    return min(150.0, 60 + 10 * (q - 10))
EV = [('東京', '東京'), ('名古屋', '名古屋'), ('大阪', '大阪'), ('仙台', '仙台'), ('青森', '青森'), ('札幌', '札幌'), ('福岡', '福岡'), ('鹿児島', '鹿児島')]
def s_r3():
    cues = [(0.2, 'r3a')]; tj = 0.2 + D['r3a'] - 0.3
    cues += [(tj + 0.3, 'r3b'), (tj + 0.3 + D['r3b'] + 0.4, 'r3c')]
    dur = max(cues[-1][0] + D['r3c'] + 1.5, tj + 19 + 2.5); n = int(dur * FPS); p = writer(f'{G}/c_r3.mp4')
    RD = {k: reach_day(v) for k, v in EV}
    for f in range(n):
        t = f / FPS; im = bg(); d = ImageDraw.Draw(im); day = dmap(t - tj)
        draw_map(im, d, day)
        x, y = lonlat_px(*SHIBUYA, MOX, MOY, MK)
        if day < 1: glow(im, x, y, 22 + 8 * math.sin(t * 3), (255, 50, 40), 200)
        for name, _ in EV:
            cx, cy = lonlat_px(*CITIES[name], MOX, MOY, MK); rd = RD[name]
            hit = day >= rd; col = (255, 120, 100) if hit else PALE
            d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=col)
            lab = f'{name} {rd:.0f}日' if hit else name
            d.text((cx - 12, cy), lab, font=Fo(28), fill=col, anchor='rm', stroke_width=3, stroke_fill=(0, 0, 0))
        d.rectangle((0, 0, 860, 140), fill=(8, 6, 10, 0))
        ctext(d, (60, 70), '決勝戦　日本地図でシミュレーション', Fo(44), GOLD, 'lm')
        ctext(d, (60, 130), '最初の1人が倒されなかった場合／電車や車はすぐ止まる', Fb(28), PALE, 'lm')
        ctext(d, (60, 290), f'{day:.0f}日目', Mi(130), PALE, 'lm', 5)
        hl = human_left(day)
        ctext(d, (60, 450), f'人間の残り　{hl * 100:.0f}%', Fo(56), BLUE, 'lm', 3)
        d.rounded_rectangle((60, 500, 760, 550), 25, fill=(50, 50, 60)); d.rounded_rectangle((60, 500, 60 + max(50, 700 * hl), 550), 25, fill=(90, 150, 230))
        for i, (c, lab) in enumerate([((255, 205, 120), '人のいる明かり'), ((255, 70, 40), 'ゾンビの先頭'), ((150, 22, 28), 'ゾンビが広がった所')]):
            d.rectangle((60, 620 + i * 60, 100, 650 + i * 60), fill=c); d.text((120, 635 + i * 60), lab, font=Fb(30), fill=GRAY, anchor='lm')
        hk = TI[CODE == 1].min() / 24
        if day >= hk:
            hx, hy = lonlat_px(140.73, 41.77, MOX, MOY, MK); d.text((hx - 14, hy + 10), f'北海道に上陸 {hk:.0f}日', font=Fo(28), fill=(255, 120, 100), anchor='rm', stroke_width=3, stroke_fill=(0, 0, 0))
        if 0 < t - tj < 19: d.text((60, 820), '早送り', font=Fo(34), fill=GOLD, anchor='lm')
        if t >= cues[2][0]:
            caption(d, '沖縄と多くの島には、歩いてはたどり着けない', GOLD, y=930, w=880, fs=34)
        disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(t_jump=tj, RD=RD), open(f'{G}/c_r3_st.json', 'w'), ensure_ascii=False); return dur, cues

TR = np.load(f'{G}/sim_train.npz')
def s_outro():
    dur = 0.5 + D['outro'] + 2.0; dd = D['outro']
    SNT = TR['snaps']; i10 = 40
    def dr(im, d, t):
        u = (t - 0.5) / dd
        if u < 0.78:
            ctext(d, (W / 2, 90), '広がる速さを決めるのは「人の多さ」と「移動の速さ」', Mi(56), GOLD, sw=3)
            if u > 0.04:
                for j, (sn, lab, hl) in enumerate([(SN[i10], '電車が止まった', ST[i10, 1] / N0), (SNT[i10], '電車が半日動いた', TR['stats'][i10, 1] / N0)]):
                    ox = 260 + j * 820; k = 2.2
                    s = sn.astype(np.float32); hr = 240; fr = np.where((TR['t_inf'] if j else TI)[LAND] <= hr, np.clip(1 - (hr - (TR['t_inf'] if j else TI)[LAND]) / 60, 0, 1), 0)
                    im.alpha_composite(map_layer(s[0], s[1], k, front=fr), (ox, 140))
                    ctext(d, (ox + 300, 820), f'{lab}：10日目', Fo(40), PALE); ctext(d, (ox + 300, 872), f'人間の残り 約{hl * 100:.0f}%', Fo(40), BLUE if j == 0 else RED)
                if 0.36 < u < 0.6:
                    d.rounded_rectangle((300, 920, W - 300, 1010), 22, fill=(12, 8, 14, 235), outline=GOLD, width=4)
                    ctext(d, (W / 2, 965), '人間が2割に減るまで　46日 → たったの10日', Mi(48), GOLD)
                if u >= 0.6:
                    d.rounded_rectangle((300, 920, W - 300, 1010), 22, fill=(12, 8, 14, 240)); ctext(d, (W / 2, 965), '本物の感染症の研究でも使われる考え方（SIRモデル）', Fo(40), PALE)
        else:
            ctext(d, (W / 2, 220), '研究チームのアドバイス：', Fo(44), GRAY)
            ctext(d, (W / 2, 330), 'なるべく、人の少ない場所へ', Mi(76), GOLD, sw=3)
            ctext(d, (W / 2, 520), 'あなたなら、どこへ逃げる？', Mi(80), PALE, sw=4)
            ctext(d, (W / 2, 630), 'コメントで教えてください', Mi(54), GOLD, sw=3)
            if u > 0.9:
                d.rounded_rectangle((W / 2 - 520, 720, W / 2 + 520, 880), 24, fill=(12, 8, 14, 225), outline=GOLD, width=4)
                ctext(d, (W / 2, 770), '次に見たい「怖い雑学」は？', Fo(48), PALE); ctext(d, (W / 2, 840), 'リクエスト募集中！', Fo(42), GOLD)
    return scene('outro', dur, dr, [(0.5, 'outro')])

ORDER = ['title', 'data', 'rule', 'r1', 'res1', 'secret', 'table', 'r3', 'res3', 'outro']
def build(k):
    if k == 'title': return s_title()
    if k == 'data': return s_data()
    if k == 'rule': return s_rule()
    if k == 'r1': return s_r1()
    if k == 'res1': return card('res1', 'RESULT　1回戦　倍々で計算すると', '全滅まで 27時間', GOLD, [('1時間ごとにゾンビが2倍', '2の27乗 ＝ 約1億3400万人', PALE), ('日本の人口', '約1億2600万人', PALE), ('でも、この計算には…', '大事なことが3つぬけている', RED)], bs=110)
    if k == 'secret': return s_secret()
    if k == 'table': return s_table()
    if k == 'r3': return s_r3()
    if k == 'res3': return card('res3', 'RESULT　決勝戦　ゾンビがすみずみまで たどり着いた日（歩いて行けない島はのぞく）', '日本は 全滅しなかった', GOLD, [('本州', '約66日', PALE), ('九州', '約84日', PALE), ('北海道', '約147日（約5か月）', PALE), ('最後まで残った人（沖縄・島など）', '約2%', BLUE)], bs=100)
    if k == 'outro': return s_outro()
if __name__ == '__main__':
    which = sys.argv[1:] or ORDER; res = {}
    for k in which: res[k] = build(k); print('done', k, round(res[k][0], 1), flush=True)
    json.dump(res, open(f'{G}/scenes_{"_".join(which)}.json', 'w'))
