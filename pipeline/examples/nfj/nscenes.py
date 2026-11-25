"""もし人間がノミの跳躍力を持っていたら（本編の場面）"""
import json, math, sys
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/nfj')
from nbase import *
D = json.load(open(f'{G}/dur.json'))
H170 = 170.0; H190 = 1.7 * 700 / 6.15    # 体長の何倍で拡大（m）

def s_title():
    dur = 0.6 + D['intro'] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.6)
        d.rounded_rectangle((W / 2 - 230, 90, W / 2 + 230, 145), 27, fill=(0, 0, 0, 170)); ctext(d, (W / 2, 118), '実データでシミュレーション', Fb(30), GOLD)
        ctext(d, (W / 2, 270), 'もし人間が', Mi(int(90 * (1.2 - 0.2 * u))), PALE, sw=4)
        ctext(d, (W / 2, 410), 'ノミの跳躍力を持っていたら', Mi(int(118 * (1.2 - 0.2 * u))), GOLD, sw=5)
        ctext(d, (W / 2, 515), 'WHAT IF HUMANS COULD JUMP LIKE FLEAS?', Fb(30), GRAY)
        FL = 950; d.rectangle((0, FL, W, H), fill=(52, 58, 76))
        ph = (t * 0.9) % 1.0; hop = max(0, math.sin(ph * math.pi)) if ph < 1 else 0
        flea(d, 640, FL - 260 * hop, 230, crouch=1 - hop if ph > 0.85 or ph < 0.05 else 0)
        figure(d, 1280, FL, 2.0, crouch=0.5 + 0.5 * math.sin(t * 2.2) if t > 0 else 0)
    return scene('title', dur, dr, [(0.6, 'intro')])

def s_data():
    dur = 0.5 + D['data'] + 0.8; dd = D['data']
    cards = [(0.0, 'ノミ', FLEA_C, [('体長', '約1.8mm'), ('踏み切りの速さ', '最高 秒速1.9m'), ('勢い', '重力の約160倍'), ('跳べる高さ', '約18cm')], '体長の 約100倍'),
             (0.5, 'アワフキムシ', HOP_C, [('体長', '約6mm'), ('跳べる高さ', '最高 約70cm'), ('', ''), ('', '')], '体長の 100倍以上'),
             (0.8, '人間', HUM_C, [('身長', '約170cm'), ('垂直跳び', '約50cm'), ('', '（20代前半男性）'), ('', '')], '身長の 約0.3倍')]
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 80), '選手のデータ', Mi(70), PALE, sw=3)
        for i, (tr, name, col, rows, big) in enumerate(cards):
            if u < tr: continue
            x0 = 90 + i * 600; a = ease((u - tr) * dd / 0.6)
            d.rounded_rectangle((x0, 160, x0 + 540, 960), 22, fill=(10, 12, 20, int(225 * a)), outline=col, width=4)
            ctext(d, (x0 + 270, 215), name, Fo(56), col)
            if i == 0: flea(d, x0 + 260, 430, 230)
            elif i == 1: hopper(d, x0 + 280, 420, 300)
            else: figure(d, x0 + 250, 460, 1.25)
            for r, (k, v) in enumerate(rows):
                if not (k or v): continue
                y = 520 + r * 75
                d.text((x0 + 30, y), k, font=Fb(30), fill=GRAY, anchor='lm'); d.text((x0 + 510, y), v, font=Fo(38), fill=PALE, anchor='rm')
            ctext(d, (x0 + 270, 890), big, Mi(52), GOLD if i < 2 else PALE, sw=2)
        d.text((24, H - 50), '出典：Sutton & Burrows 2011（J Exp Biol）、Burrows 2003（Nature）、Hoffmann ほか 2019（カナダ健康調査の垂直跳び）', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('data', dur, dr, [(0.5, 'data')])

def s_rule():
    dur = 0.5 + D['rule'] + 0.8; dd = D['rule']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3)
        FL = 950; d.rectangle((0, FL, W, H), fill=(52, 58, 76)); figure(d, 380, FL, 2.4, col=FLEA_C)
        flea(d, 600, FL - 360, 110)
        if u > 0.15: ctext(d, (600, FL - 470), 'ノミの跳躍力', Fo(36), FLEA_C)
        rows = [(0.05, '身長170cmの人間が、ノミの跳躍力を手に入れる'), (0.45, 'その場で、まっすぐ上にジャンプ'), (0.7, 'どこまで高く跳べるかを比べる')]
        for i, (tr, txt) in enumerate(rows):
            if u < tr: continue
            y = 250 + i * 160
            d.rounded_rectangle((760, y, W - 90, y + 120), 18, fill=(10, 12, 20, 225), outline=GOLD if i == 2 else None, width=4 if i == 2 else 0)
            d.text((800, y + 60), txt, font=Fo(42), fill=PALE, anchor='lm')
    return scene('rule', dur, dr, [(0.5, 'rule')])

def s_r1():
    cues = [(0.2, 'r1a')]; tj = 0.2 + D['r1a'] - 0.4; TR = 3.6
    cues += [(tj + TR - 0.2, 'r1b'), (tj + TR - 0.2 + D['r1b'] + 0.3, 'r1c')]
    dur = cues[-1][0] + D['r1c'] + 1.5; n = int(dur * FPS); p = writer(f'{G}/c_r1.mp4'); GR = 990
    for f in range(n):
        t = f / FPS; im = bg(); d = ImageDraw.Draw(im); q = t - tj
        h = 0.0 if q < 0 else H170 * (1 - (1 - min(1, q / TR)) ** 2)
        s = min(240.0, 820 / (h + 2.2))                       # 1mあたりのpx
        cr = fade((q + 0.9) / 0.5) if q < 0 else 0
        d.rectangle((0, GR, W, H), fill=(52, 58, 76))
        PX = 700; building(d, PX + 130 * s, GR, 35, 170, s, floors=50); building(d, PX + 14 * s, GR, 10, 7, s, col=(110, 90, 80), floors=2)
        if s * 170 > 60: pass
        if t > tj + TR - 0.4: d.text((PX + 130 * s - 20, GR - 140 * s), '50階建てのビル（約170m）', font=Fo(34), fill=PALE, anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
        ruler_m(d, 200, GR, s, GR - 150)
        yf = GR - h * s; figure(d, PX, yf, s / 100, crouch=cr, col=FLEA_C)
        if s < 30:
            d.ellipse((PX - 16, yf - 1.7 * s - 16, PX + 16, yf - 1.7 * s + 16), outline=GOLD, width=4)
            d.text((PX + 30, yf - 1.7 * s), f'ノミ人間　{h:.0f}m', font=Fo(44), fill=GOLD, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
            d.line((PX, yf + 6, PX, GR), fill=(255, 210, 80, 120), width=3)
        d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 215))
        ctext(d, (W / 2, 40), '1回戦　よく聞く計算「体長の100倍」', Fo(40), GOLD); ctext(d, (W / 2, 92), 'ノミ人間（身長170cm）× 100倍 ＝ ？', Fb(30), PALE)
        if t >= cues[1][0]: caption(d, '記録 170m！' if t < cues[2][0] else '約50階建てのビルの高さ', GOLD)
        disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(t_jump=tj, TR=TR), open(f'{G}/c_r1_st.json', 'w')); return dur, cues

def card(key, title, big, bigcol, lines, bs=120):
    dur = 0.6 + D[key] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.4)
        ctext(d, (W / 2, 220), title, Fb(38), (220, 220, 225))
        ctext(d, (W / 2, 370), big, Mi(int(bs * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 570 + r * 120
            d.rounded_rectangle((W / 2 - 620, y - 48, W / 2 + 620, y + 48), 16, fill=(10, 12, 20, 220))
            d.text((W / 2 - 580, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 580, y), val, font=Fo(50), fill=col, anchor='rm')
    return scene(key, dur, dr, [(0.6, key)])

def s_secret():
    dur = 0.5 + D['secret'] + 1.0; dd = D['secret']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 80), '種明かし', Mi(72), GOLD, sw=3)
        if u < 0.62:
            a = ease((u - 0.03) / 0.08); k = 1 + 9 * a
            c1 = 26; c2 = 26 * k; base = 700
            for (cx, sz, lab) in [(420, c1, '大きさ 1'), (1000, c2, f'大きさ {k:.0f}倍')]:
                dz = sz * 0.35
                d.polygon([(cx - sz / 2, base - sz), (cx - sz / 2 + dz, base - sz - dz), (cx + sz / 2 + dz, base - sz - dz), (cx + sz / 2, base - sz)], fill=(200, 140, 95))
                d.polygon([(cx + sz / 2, base), (cx + sz / 2, base - sz), (cx + sz / 2 + dz, base - sz - dz), (cx + sz / 2 + dz, base - dz)], fill=(120, 75, 45))
                d.rectangle((cx - sz / 2, base - sz, cx + sz / 2, base), fill=FLEA_C)
                ctext(d, (cx, base + 50), lab, Fo(40), PALE)
            rows = [(0.12, '体重', '10×10×10 ＝ 1000倍', PALE), (0.25, 'ジャンプのエネルギー（筋肉の量）', '1000倍', GREEN), (0.38, '同じ高さまで持ち上げるのに必要なエネルギー', '1000倍', RED)]
            for i, (tr, lab, val, col) in enumerate(rows):
                if u < tr: continue
                y = 250 + i * 110
                d.rounded_rectangle((1290, y - 45, W - 60, y + 45), 14, fill=(10, 12, 20, 225))
                d.text((1310, y - 18), lab, font=Fb(24), fill=GRAY, anchor='lm'); d.text((W - 80, y + 14), val, font=Fo(40), fill=col, anchor='rm')
            if u > 0.48: ctext(d, (1590, 650), '→ 跳べる高さは ほぼ同じ！', Mi(48), GOLD, sw=3)
        else:
            ctext(d, (W / 2, 260), '跳べる高さを決めるのは', Mi(64), PALE, sw=3)
            ctext(d, (W / 2, 380), '体の大きさ ではなく、踏み切りの速さ', Mi(70), GOLD, sw=3)
            d.rounded_rectangle((300, 480, W - 300, 640), 22, fill=(10, 12, 20, 225))
            ctext(d, (W / 2, 560), '高さ ＝ 速さ × 速さ ÷（2 × 重力 9.8）', Fo(56), PALE)
            if u > 0.8:
                ctext(d, (W / 2, 760), '秒速1.9m なら → 約18cm', Mi(80), GOLD, sw=4)
                if u > 0.88:
                    flea(d, 420, 960, 120); figure(d, 1500, 980, 0.9, col=(180, 180, 190))
                    ctext(d, (W / 2, 930), 'ノミでも、ゾウでも（同じ速さなら同じ高さ）', Fo(40), PALE)
        d.text((24, H - 50), '大きさと跳べる高さの関係：ボレリ（1680）、A.V.ヒル（1950）の考え方。空気抵抗は考えない', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('secret', dur, dr, [(0.5, 'secret')])

SCALE = [('ノミ', '約1.8mm', '約18cm'), ('ネズミの大きさ', '約15cm', '約15m'), ('人間の大きさ', '約170cm', '約170m'), ('ゾウの大きさ', '約3m', '約300m')]
def s_scale():
    dur = 0.5 + D['scale'] + 1.0; dd = D['scale']
    rv = [0.08, 0.2, 0.32, 0.42]
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 90), 'ノミをそのまま大きくしたら？', Mi(68), GOLD, sw=3)
        hy = 200
        d.text((250, hy), '大きさ', font=Fb(32), fill=GRAY, anchor='lm'); d.text((1050, hy), '「体長の100倍」計算', font=Fb(32), fill=GRAY, anchor='mm'); d.text((1560, hy), '踏み切りの速さで計算', font=Fb(32), fill=GRAY, anchor='mm')
        for i, (a, b, c) in enumerate(SCALE):
            if u < rv[i]: continue
            y = 250 + i * 150
            d.rounded_rectangle((200, y, W - 140, y + 125), 18, fill=(10, 12, 20, 225))
            d.text((250, y + 62), a, font=Fo(46), fill=PALE, anchor='lm'); d.text((700, y + 62), b, font=Fb(32), fill=GRAY, anchor='lm')
            d.text((1050, y + 62), c, font=Fo(54), fill=PALE, anchor='mm')
            if u > 0.62: d.text((1560, y + 62), '約18cm', font=Fo(54), fill=GOLD, anchor='mm')
        if u > 0.62: d.rounded_rectangle((1340, 240, 1780, 860), 20, outline=GOLD, width=5)
        if u > 0.82: ctext(d, (W / 2, 950), '大きくしても、高くは跳べない！', Mi(60), GOLD, sw=3)
    return scene('scale', dur, dr, [(0.5, 'scale')])

BARS = [('ノミ', '約0.5mg', 20, FLEA_C), ('コメツキムシ', '約40mg', 30, (190, 160, 110)), ('バッタ', '約3g', 60, GREEN), ('人間', '約70kg', 55, HUM_C)]
def s_table():
    dur = 0.5 + D['table'] + 1.2; dd = D['table']
    rv = [0.12, 0.25, 0.38, 0.52]
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 90), 'いろいろな生き物の、跳べる高さ', Mi(68), PALE, sw=3)
        for i, (name, kg, cm, col) in enumerate(BARS):
            if u < rv[i]: continue
            y = 230 + i * 160; a = ease((u - rv[i]) * dd / 1.0)
            d.text((430, y + 30), name, font=Fo(48), fill=col, anchor='rm'); d.text((430, y + 85), f'体重 {kg}', font=Fb(28), fill=GRAY, anchor='rm')
            d.rounded_rectangle((470, y + 20, 1470, y + 100), 40, fill=(58, 62, 78))
            d.rounded_rectangle((470, y + 20, 470 + 1000 * cm / 70 * a, y + 100), 40, fill=col)
            d.text((1500, y + 60), f'約{cm * a:.0f}cm' if i < 3 else ('約50〜60cm' if a > 0.99 else f'約{cm * a:.0f}cm'), font=Fo(50), fill=PALE, anchor='lm')
        if u > 0.75:
            d.rounded_rectangle((260, 880, W - 260, 990), 22, fill=(10, 12, 20, 230), outline=GOLD, width=4)
            ctext(d, (W / 2, 935), '体重は 約1億倍ちがうのに、高さは 約3倍しかちがわない', Fo(48), GOLD)
        d.text((24, H - 50), '出典：K. Schmidt-Nielsen『Scaling: Why is Animal Size So Important?』（1984）の値、MIT OCW 講義ノートより（体重・高さは目安）', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('table', dur, dr, [(0.5, 'table')])

LANES = [(430, 'ノミ人間', FLEA_C, V_FLEA, '秒速1.9m'), (960, 'ふつうの人間', HUM_C, V_HUM, '秒速3.1m'), (1490, 'アワフキムシ人間', HOP_C, V_HOP, '秒速4.0m')]
SLOW = 0.5
def s_r3():
    cues = [(0.2, 'r3a')]; tj = 0.2 + D['r3a'] - 0.3
    cues += [(tj + 2.2, 'r3b'), (tj + 2.2 + D['r3b'] + 0.2, 'r3c')]
    dur = cues[-1][0] + D['r3c'] + 1.5; n = int(dur * FPS); p = writer(f'{G}/c_r3.mp4'); GR = 890; CMp = 2.3
    for f in range(n):
        t = f / FPS; im = bg(); d = ImageDraw.Draw(im); q = (t - tj) * SLOW
        d.rectangle((0, GR, W, H), fill=(52, 58, 76))
        ruler_m(d, 130, GR, CMp * 100, 260)
        for x, name, col, v, vs in LANES:
            h = hv(v); tf = 2 * v / g
            if q < 0: hh = 0; cr = fade((t - tj + 0.9) / 0.5)
            elif q < tf: hh = v * q - 0.5 * g * q * q; cr = 0
            else: hh = 0; cr = max(0, 0.5 - (q - tf) * 3)
            if q > 0.05: d.line((x - 150, GR - h * 100 * CMp, x + 200, GR - h * 100 * CMp), fill=col, width=3)
            if q > tf * 0.5: d.text((x + 205, GR - h * 100 * CMp), f'{h * 100:.0f}cm', font=Fo(40), fill=col, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
            figure(d, x, GR - hh * 100 * CMp, CMp, crouch=cr, col=col)
            ctext(d, (x, GR + 38), name, Fo(38), col); ctext(d, (x, GR + 82), f'踏み切り {vs}', Fb(26), GRAY)
        d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 215))
        ctext(d, (W / 2, 40), '決勝戦　正しい計算（踏み切りの速さ）で3人同時にジャンプ', Fo(40), GOLD); ctext(d, (W / 2, 92), '体の大きさは3人とも身長170cm', Fb(30), PALE)
        if 0 < q < 1.2: d.text((W - 40, 160), 'スロー再生', font=Fo(34), fill=GOLD, anchor='rm')
        if t >= cues[2][0]: caption(d, 'ノミ人間は、たったの18cm！', RED, y=200)
        disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(t_jump=tj, slow=SLOW), open(f'{G}/c_r3_st.json', 'w')); return dur, cues

def s_outro():
    dur = 0.5 + D['outro'] + 2.0; dd = D['outro']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        if u < 0.72:
            ctext(d, (W / 2, 170), '虫がすごく見えるのは「体長の何倍」で比べるから', Mi(58), GOLD, sw=3)
            if u > 0.12:
                d.rounded_rectangle((200, 280, W - 200, 400), 20, fill=(10, 12, 20, 225))
                ctext(d, (W / 2, 340), '同じ18cmでも　ノミなら体長の100倍、人間なら身長の約0.1倍', Fo(42), PALE)
            if u > 0.3:
                d.rounded_rectangle((200, 450, W - 200, 650), 20, fill=(10, 12, 20, 225))
                ctext(d, (W / 2, 510), 'ノミの筋肉は小さすぎて、一瞬では縮みきれない', Fo(42), PALE)
                ctext(d, (W / 2, 590), '→「レシリン」というゴムのようなバネに力をためて一気に放つ', Fo(42), GOLD)
                flea(d, 200, 1000, 130)
            if u > 0.52: ctext(d, (W / 2, 790), 'バネがなくても50cm跳べる　人間の脚も優秀！', Mi(58), PALE, sw=3)
        else:
            ctext(d, (W / 2, 380), 'ノミ人間は何m跳べると思った？', Mi(80), PALE, sw=4)
            ctext(d, (W / 2, 500), 'コメントで教えてください', Mi(54), GOLD, sw=3)
            if u > 0.9:
                d.rounded_rectangle((W / 2 - 520, 620, W / 2 + 520, 800), 24, fill=(10, 12, 20, 225), outline=GOLD, width=4)
                ctext(d, (W / 2, 670), '次に見たい雑学は？', Fo(52), PALE); ctext(d, (W / 2, 750), 'リクエスト募集中！', Fo(44), GOLD)
    return scene('outro', dur, dr, [(0.5, 'outro')])

ORDER = ['title', 'data', 'rule', 'r1', 'res1', 'secret', 'scale', 'table', 'r3', 'res3', 'outro']
def build(k):
    if k == 'title': return s_title()
    if k == 'data': return s_data()
    if k == 'rule': return s_rule()
    if k == 'r1': return s_r1()
    if k == 'res1': return card('res1', 'RESULT　1回戦　「体長の100倍」で計算', '記録 約170m', GOLD, [('ノミ人間（体長の約100倍）', '約170m', PALE), ('アワフキムシ人間（体長の約114倍）', '約190m', PALE), ('でも、この計算は…', '大まちがい！', RED)])
    if k == 'secret': return s_secret()
    if k == 'scale': return s_scale()
    if k == 'table': return s_table()
    if k == 'r3': return s_r3()
    if k == 'res3': return card('res3', 'RESULT　決勝戦　正しい計算', '優勝 アワフキムシ人間', HOP_C, [('アワフキムシ人間', '約80cm', HOP_C), ('ふつうの人間', '約50cm', PALE), ('ノミ人間（最下位）', '約18cm', RED)], bs=96)
    if k == 'outro': return s_outro()
if __name__ == '__main__':
    which = sys.argv[1:] or ORDER; res = {}
    for k in which: res[k] = build(k); print('done', k, round(res[k][0], 1), flush=True)
    json.dump(res, open(f'{G}/scenes_{"_".join(which)}.json', 'w'))
