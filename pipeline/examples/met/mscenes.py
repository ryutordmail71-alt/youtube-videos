"""東京に隕石が落ちたら（本編の場面）  python3 mscenes.py key1 key2 ..."""
import json, math, sys
sys.path.insert(0, '/home/claude/met')
from mbase import *
D = json.load(open(f'{G}/dur.json'))
CX, CY = W / 2 + 150, H / 2 + 20
def basemap(im, ppk, cx=CX, cy=CY, dim=1.0):
    ppk = round(ppk / 0.02) * 0.02; im.alpha_composite(map_img(ppk, cx=cx, cy=cy))
def label_cities(d, ppk, names, cx=CX, cy=CY, fs=30):
    for n in names: city(d, n, round(ppk / 0.02) * 0.02, cx, cy, fs=fs)
def tokyo_px(ppk, cx=CX, cy=CY): return cx, cy
def title_box(d, txt, sub=None):
    d.rounded_rectangle((60, 40, 60 + Fo(46).getlength(txt) + 60, 120), 20, fill=(0, 0, 0, 200)); d.text((90, 80), txt, font=Fo(46), fill=GOLD, anchor='lm')
    if sub: d.text((92, 150), sub, font=Fb(32), fill=PALE, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
def streak(im, d, u, x1, y1, r, col=(255, 200, 120)):
    """u：0〜1 で右上から (x1,y1) へ"""
    x0, y0 = x1 + 900, y1 - 700; x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u
    for k in range(18):
        q = k / 18; xx = x + (x0 - x1) * 0.25 * q; yy = y + (y0 - y1) * 0.25 * q
        d.line((x, y, xx, yy), fill=(255, int(200 - 120 * q), 80, int(200 * (1 - q))), width=max(2, int(r * (1 - q))))
    glow(im, x, y, r * 2.5, (255, 220, 150), 200); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 220))
def flash(im, a):
    if a <= 0: return
    im.alpha_composite(Image.new('RGBA', im.size, (255, 245, 225, int(255 * min(1, a)))))
def alt_gauge(d, alt, x=120, y0=260, y1=900, top=100):
    d.line((x, y0, x, y1), fill=GRAY, width=3)
    for a in (0, 20, 40, 60, 80, 100):
        yy = y1 - (y1 - y0) * a / top; d.line((x - 10, yy, x + 10, yy), fill=GRAY, width=2); d.text((x + 20, yy), f'{a}km', font=Fb(26), fill=GRAY, anchor='lm')
    yy = y1 - (y1 - y0) * min(top, alt) / top; d.ellipse((x - 14, yy - 14, x + 14, yy + 14), fill=ORANGE)
    d.text((x, y0 - 40), '高さ', font=Fo(32), fill=PALE, anchor='mm')

def s_title():
    dur = 0.6 + D['intro'] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.8); basemap(im, 3.0, cx=1400, cy=560); label_cities(d, 3.0, ['東京駅'], 1400, 560, 34)
        p = (t * 0.25) % 1.0; streak(im, d, 0.35 + 0.6 * p, 1400, 560, 10)
        d.rounded_rectangle((90, 110, 560, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (325, 140), '実データでシミュレーション', Fb(32), GOLD)
        s = 1.15 - 0.15 * u
        ctext(d, (90, 320), '東京に隕石が', Mi(int(104 * s)), PALE, 'lm', 5)
        ctext(d, (90, 460), '落ちたら？', Mi(int(104 * s)), PALE, 'lm', 5)
        ctext(d, (90, 620), '10m・100m・1km', Mi(int(96 * s)), GOLD, 'lm', 5)
        ctext(d, (96, 730), 'WHAT IF AN ASTEROID HIT TOKYO?', Fb(30), GRAY, 'lm')
    return scene('title', dur, dr, [(0.6, 'intro')])

def s_data():
    dd = D['data']; dur = 0.5 + dd + 0.8
    def card(d, x, y, w, h, head, rows, a, col):
        d.rounded_rectangle((x, y, x + w, y + h), 22, fill=(16, 18, 30, int(235 * a)), outline=col + (int(255 * a),), width=4)
        d.text((x + 36, y + 60), head, font=Fo(48), fill=col, anchor='lm')
        for i, (k, v) in enumerate(rows):
            yy = y + 150 + i * 78; d.text((x + 40, yy), k, font=Fb(34), fill=GRAY, anchor='lm'); d.text((x + w - 40, yy), v, font=Fo(42), fill=PALE, anchor='rm')
    def dr(im, d, t):
        u = (t - 0.5) / dd
        a1 = fade(t / 0.5); card(d, 80, 120, 860, 620, 'チェリャビンスク隕石（2013年）', [('直径', '約18m'), ('速さ', '秒速 約19km'), ('爆発した高さ', '上空 約30km'), ('エネルギー', '広島型原爆 約30発分'), ('けが人', '約1,500人（おもにガラス）')], a1, GOLD)
        if u > 0.62:
            a2 = fade((u - 0.62) / 0.05); card(d, 1000, 120, 840, 470, 'ツングースカ大爆発（1908年）', [('場所', 'ロシア・シベリア'), ('なぎ倒された森', '約2,000km²'), ('', '＝東京都とほぼ同じ広さ')], a2, ORANGE)
        rock(d, 1420, 820, 90, 3)
    return scene('data', dur, dr, [(0.5, 'data')])

def s_rule():
    dd = D['rule']; dur = 0.5 + dd + 0.8
    def dr(im, d, t):
        u = (t - 0.5) / dd; basemap(im, 4.0); label_cities(d, 4.0, ['東京駅', '横浜', 'さいたま', '千葉'])
        title_box(d, 'ルール', '石の隕石が 秒速20km で 東京駅の真上に落ちる')
        if u > 0.35:
            for i, (s, r) in enumerate([('10m', 14), ('100m', 26), ('1km', 46)]):
                a = fade((u - 0.35 - i * 0.06) / 0.05); x = 260 + i * 200
                if a > 0: rock(d, x, 420, r, i + 2); d.text((x, 500), s, font=Fo(44), fill=GOLD, anchor='mm')
        if u > 0.62:
            d.rounded_rectangle((90, 620, 760, 820), 20, fill=(0, 0, 0, 200))
            ring(im, 150, 680, 26, RED, 90, 255); d.text((200, 680), '建物が大きくこわれる範囲', font=Fb(34), fill=PALE, anchor='lm')
            ring(im, 150, 765, 26, BLUE, 50, 255); d.text((200, 765), '窓ガラスが割れる範囲', font=Fb(34), fill=PALE, anchor='lm')
    return scene('rule', dur, dr, [(0.5, 'rule')])

def r_scene(key, size, tj_extra, alt_burst, drawer_after, cues_keys, extra_tail=1.0):
    """落下 → 爆発。cues_keys=[a, b, c]"""
    ka, kb, kc = cues_keys; t_a = 0.4; tj = t_a + D[ka] + 0.3; fall = 2.2; tb = tj + fall
    tc = tb + max(D[kb], 1.8) + 0.3; dur = tc + D[kc] + extra_tail
    st = dict(t_jump=tj, t_burst=tb, dur=dur); json.dump(st, open(f'{G}/c_{key}_st.json', 'w'))
    return tj, tb, tc, dur, [(t_a, ka), (tb, kb), (tc, kc)]
def s_r1():
    tj, tb, tc, dur, cues = r_scene('r1', 10, 0, 40, None, ['r1a', 'r1b', 'r1c'])
    def dr(im, d, t):
        basemap(im, 4.0); label_cities(d, 4.0, ['東京駅', '横浜', 'さいたま', '千葉'])
        title_box(d, '1回戦　直径10m', 'エネルギー：広島型原爆 約5発分')
        alt = 100 if t < tj else max(40, 100 - 60 * (t - tj) / (tb - tj)); alt_gauge(d, alt)
        if tj <= t < tb: streak(im, d, ease((t - tj) / (tb - tj)) * 0.85, CX, CY, 9)
        if t >= tb:
            q = t - tb; flash(im, 0.85 * math.exp(-q * 3)); glow(im, CX + 40, CY - 120, 60 * math.exp(-q * 0.8) + 8, (255, 220, 160), 200 * math.exp(-q * 0.6))
            if q > 0.3: caption(d, '上空 約40kmで爆発！（目安）', GOLD)
        if t >= tc: d.rounded_rectangle((1200, 140, 1860, 260), 20, fill=(0, 0, 0, 210)); d.text((1530, 200), '地上の被害：ほぼなし', font=Fo(48), fill=PALE, anchor='mm')
    return scene('r1', dur, dr, cues)
def s_res1():
    dd = D['res1']; dur = 0.4 + dd + 0.8
    def dr(im, d, t):
        basemap(im, 4.0); label_cities(d, 4.0, ['東京駅', '横浜', 'さいたま', '千葉'])
        d.rounded_rectangle((300, 300, 1620, 760), 30, fill=(10, 10, 18, 235), outline=GOLD, width=5)
        ctext(d, (960, 400), '1回戦の結果', Fo(50), GRAY); ctext(d, (960, 530), '東京は ほぼ無事', Mi(110), GOLD, sw=4)
        ctext(d, (960, 670), '空の上でバラバラに（大きな音・窓ガラスが割れることも）', Fb(36), PALE)
    return scene('res1', dur, dr, [(0.4, 'res1')])

R2_IN, R2_WIN = 40, 250
def s_r2():
    tj, tb, tc, dur, cues = r_scene('r2', 100, 0, 5, None, ['r2a', 'r2b', 'r2c'], 1.2)
    def dr(im, d, t):
        basemap(im, 4.0); label_cities(d, 4.0, ['東京駅', '横浜', 'さいたま', '千葉'])
        title_box(d, '2回戦　直径100m', 'エネルギー：広島型原爆 約5,000発分')
        alt = 100 if t < tj else max(5, 100 - 95 * (t - tj) / (tb - tj)); alt_gauge(d, alt)
        if tj <= t < tb: streak(im, d, ease((t - tj) / (tb - tj)) * 0.97, CX, CY, 16)
        if t >= tb:
            q = t - tb; flash(im, math.exp(-q * 2.2)); r = R2_IN * 4.0 * ease(q / 1.6)
            ring(im, CX, CY, r, RED, 90, 255, 5)
            if q > 1.6: d.text((CX + r * 0.72 + 10, CY - r * 0.72 - 10), '半径 約40km（目安）', font=Fo(40), fill=(255, 140, 130), anchor='lb', stroke_width=4, stroke_fill=(0, 0, 0))
            label_cities(d, 4.0, ['東京駅', '横浜', 'さいたま', '千葉'])
        if t >= tc: caption(d, '東京23区も 横浜も さいたまも 千葉も すっぽり', GOLD)
    return scene('r2', dur, dr, cues)
def s_res2():
    dd = D['res2']; dur = 0.4 + dd + 1.0
    def dr(im, d, t):
        z = ease((t - 0.4) / 3.0); ppk = 4.0 + (1.25 - 4.0) * z
        basemap(im, ppk); label_cities(d, ppk, ['東京駅'] + (['静岡', '福島', '宇都宮', '甲府', '名古屋'] if z > 0.6 else ['横浜', 'さいたま', '千葉']))
        rw = R2_WIN * ppk * ease((t - 2.0) / 2.0) if t > 2.0 else 0
        if rw > 0: ring(im, CX, CY, rw, BLUE, 40, 230, 4)
        ring(im, CX, CY, R2_IN * ppk, RED, 90, 255, 4)
        if t > 4.0: d.text((CX + rw * 0.7, CY + rw * 0.72 + 10), '窓ガラスが割れる範囲　半径 約250km（目安）', font=Fo(36), fill=BLUE, anchor='mt', stroke_width=4, stroke_fill=(0, 0, 0))
        d.rounded_rectangle((60, 60, 760, 330), 24, fill=(0, 0, 0, 215))
        ctext(d, (410, 130), '大きさ 10倍', Mi(64), PALE); ctext(d, (410, 250), 'エネルギー 1000倍', Mi(72), GOLD)
    return scene('res2', dur, dr, [(0.4, 'res2')])
def s_secret():
    dd = D['secret']; dur = 0.4 + dd + 0.8
    def dr(im, d, t):
        u = (t - 0.4) / dd; title_box(d, '種明かし', '重さは「大きさの3乗」で増える')
        for i, (s, r, m) in enumerate([('大きさ 1', 30, '重さ 1'), ('大きさ 10', 90, '重さ 1,000'), ('大きさ 100（イメージ）', 230, '重さ 1,000,000')]):
            a = fade((u - 0.15 - i * 0.12) / 0.06)
            if a <= 0: continue
            x = [300, 760, 1400][i]; rock(d, x, 560, r, i + 5)
            d.text((x, 560 + r + 50), s, font=Fb(36), fill=GRAY, anchor='mm'); d.text((x, 560 + r + 110), m, font=Fo(50), fill=GOLD, anchor='mm')
        if u > 0.55: caption(d, '10 × 10 × 10 ＝ 1000倍', GOLD, y=200, fs=60)
    return scene('secret', dur, dr, [(0.4, 'secret')])
R3_IN = 200
def s_r3():
    tj, tb, tc, dur, cues = r_scene('r3', 1000, 0, 0, None, ['r3a', 'r3b', 'r3c'], 1.4)
    def dr(im, d, t):
        z = ease((t - tc) / 2.5) if t > tc else 0; ppk = 4.0 + (1.35 - 4.0) * z
        basemap(im, ppk); names = ['東京駅', '横浜', 'さいたま', '千葉'] if z < 0.5 else ['東京駅', '宇都宮', '水戸', '前橋', '甲府', '静岡', '福島']
        title_box(d, '決勝戦　直径1km', 'エネルギー：広島型原爆 約500万発分')
        alt = 100 if t < tj else max(0, 100 - 100 * (t - tj) / (tb - tj)); alt_gauge(d, alt)
        if tj <= t < tb: streak(im, d, ease((t - tj) / (tb - tj)), CX, CY, 28)
        if t >= tb:
            q = t - tb; flash(im, 1.2 * math.exp(-q * 1.4))
            cr = 7.5 * ppk; glow(im, CX, CY, cr * 2.2, (255, 120, 40), 160 * math.exp(-q * 0.3) + 40)
            d.ellipse((CX - cr, CY - cr, CX + cr, CY + cr), fill=(20, 12, 10), outline=(255, 150, 70), width=3)
            if t < tc: d.text((CX + cr + 20, CY + 10), 'クレーター 直径 約15km（目安）', font=Fo(40), fill=ORANGE, anchor='lm', stroke_width=4, stroke_fill=(0, 0, 0))
        if t >= tc:
            r = R3_IN * ppk * ease((t - tc - 0.6) / 2.0); ring(im, CX, CY, r, RED, 80, 255, 5)
            if t > tc + 2.6: d.text((CX - r * 0.7, CY + r * 0.72 + 10), '建物が大きくこわれる範囲　半径 約200km（目安）', font=Fo(38), fill=(255, 140, 130), anchor='mt', stroke_width=4, stroke_fill=(0, 0, 0))
        label_cities(d, ppk, names)
    return scene('r3', dur, dr, cues)
def s_res3():
    dd = D['res3']; dur = 0.4 + dd + 1.0
    def dr(im, d, t):
        z = ease(t / 2.5); ppk = 1.35 + (0.55 - 1.35) * z; basemap(im, ppk, cx=CX + 150 * z, cy=CY - 80 * z)
        a = fade((t - 1.0) / (dur - 2)); ov = Image.new('RGBA', im.size, (70, 55, 45, int(170 * a))); im.alpha_composite(ov)
        d.rounded_rectangle((300, 330, 1620, 750), 30, fill=(10, 10, 18, 235), outline=GOLD, width=5)
        ctext(d, (960, 420), '決勝戦の結果', Fo(50), GRAY); ctext(d, (960, 545), '関東のほぼ全部', Mi(110), GOLD, sw=4)
        ctext(d, (960, 670), 'まい上がったチリで 世界の気温が下がるとも（目安）', Fb(38), PALE)
    return scene('res3', dur, dr, [(0.4, 'res3')])
def s_odds():
    dd = D['odds']; dur = 0.4 + dd + 1.0
    def dr(im, d, t):
        u = (t - 0.4) / dd; title_box(d, '本当に東京に落ちる？', '平均すると何年に1回？（目安）')
        rows = [('100m級', '地球のどこか', '約1,000年に1回', 0.12), ('1km級', '地球のどこか', '約10万年に1回', 0.25), ('100m級', '東京23区', '約8億年に1回', 0.55), ('1km級', '東京23区', '約800億年に1回', 0.68)]
        for i, (s, where, v, at) in enumerate(rows):
            a = fade((u - at) / 0.04)
            if a <= 0: continue
            y = 290 + i * 135; hot = i >= 2
            d.rounded_rectangle((120, y - 55, 1800, y + 55), 18, fill=(30, 22, 16, 230) if hot else (18, 20, 32, 230), outline=GOLD if hot else (90, 95, 120), width=3)
            d.text((170, y), s, font=Fo(50), fill=PALE, anchor='lm'); d.text((480, y), where, font=Fb(44), fill=GRAY, anchor='lm'); d.text((1760, y), v, font=Mi(60), fill=GOLD if hot else PALE, anchor='rm')
        if u > 0.38 and u < 0.55: caption(d, '東京23区 ＝ 地球の表面の 約81万分の1', PALE, y=900)
        if u > 0.82: caption(d, '宇宙の年齢（約138億年）より ずっと長い', GOLD, y=900)
    return scene('odds', dur, dr, [(0.4, 'odds')])
def s_outro():
    dd = D['outro']; dur = 0.4 + dd + 2.5
    def dr(im, d, t):
        u = (t - 0.4) / dd
        ctext(d, (960, 250), '大きさ 10倍 → 被害 1000倍', Mi(96), GOLD, sw=4)
        if u > 0.2: ctext(d, (960, 420), 'でも 大きい隕石ほど めったに落ちてこない', Fo(52), PALE)
        if u > 0.38: ctext(d, (960, 540), '世界中の望遠鏡が いまも見張っている', Fo(52), BLUE)
        for i, r in enumerate([14, 26, 46]): rock(d, 760 + i * 200, 720, r, i + 2)
        if u > 0.75:
            d.rounded_rectangle((360, 860, 1560, 980), 24, fill=(12, 10, 16, 235), outline=GOLD, width=4)
            ctext(d, (960, 920), 'いちばん怖いのはどの大きさ？ コメントで教えてね', Fo(48), PALE)
    return scene('outro', dur, dr, [(0.4, 'outro')])

ALL = dict(title=s_title, data=s_data, rule=s_rule, r1=s_r1, res1=s_res1, r2=s_r2, res2=s_res2, secret=s_secret, r3=s_r3, res3=s_res3, odds=s_odds, outro=s_outro)
if __name__ == '__main__':
    keys = sys.argv[1:]; out = {}
    for k in keys: out[k] = ALL[k](); print(k, round(out[k][0], 1), flush=True)
    json.dump(out, open(f'{G}/scenes_{"_".join(keys)}.json', 'w'))
