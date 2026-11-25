import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import hrender as R, hmodel as HM, hcontent as C
from hrender import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, BLOOD, ctext, fade, ease, writer
G = '/home/claude/h10'; D = json.load(open(f'{G}/dur.json'))
BG = (16, 18, 26, 255)
def dark_bg(): return Image.new('RGBA', (W, H), BG)
def track_blur(dark=0.45):
    im = R.track_bg().convert('RGB'); return ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(10))).enhance(dark).convert('RGBA')
def foot(d, s): d.text((W - 24, H - 16), s, font=Fb(20), fill=(200, 200, 205), anchor='rs')
def hero(im, x, y, h, n, t, ph=None):
    d = ImageDraw.Draw(im); c = R.runner(d, x, y, h, ph if ph is not None else t * 9, (210, 90, 60)); R.hearts_row(d, c[0], c[1], n, h * 0.03, t, 160, per=5)

def scene_title():
    dur = 0.6 + D['intro'] + 1.0; n = int(dur * FPS); base = track_blur(0.55); p = writer(f'{G}/c_title.mp4')
    for f in range(n):
        t = f / FPS; im = base.copy(); hero(im, 1450, 1000, 640, 10, t); d = ImageDraw.Draw(im); u = ease(t / 0.5)
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (110, 330), '心臓が10個あったら', Mi(int(110 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (110, 520), '最強？', Mi(190), GOLD, 'lm', 8)
        if t > 0.8: ctext(d, (116, 680), 'WHAT IF YOU HAD 10 HEARTS?', Fb(34), (225, 225, 230), 'lm', 2)
        if t > 1.0: ctext(d, (110, 790), 'ポンプ10倍 ＝ 酸素10倍…のはず？', Fo(46), PALE, 'lm', 3)
        d.text((W - 24, H - 16), R.NOTE, font=Fb(20), fill=(220, 220, 225), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, 'intro')]

def rowbox(d, y, lab, val, col, x0=W / 2 - 600, x1=W / 2 + 600, hl=False, lf=40, vf=60):
    d.rounded_rectangle((x0, y - 55, x1, y + 55), 18, fill=(10, 12, 18, 230), outline=GOLD if hl else None, width=4 if hl else 0)
    d.text((x0 + 40, y), lab, font=Fo(lf), fill=PALE, anchor='lm'); d.text((x1 - 40, y), val, font=Fo(vf), fill=col, anchor='rm')

def lungs(d, cx, cy, s, t):
    for sx in (-1, 1):
        d.ellipse((cx + sx * s * 0.55 - s * 0.38, cy - s * 0.7, cx + sx * s * 0.55 + s * 0.38, cy + s * 0.6), fill=(240, 150, 160), outline=(255, 210, 215), width=5)
        for k in range(5):
            a = -0.9 + k * 0.45; d.line((cx + sx * s * 0.25, cy - s * 0.2, cx + sx * (s * 0.55 + math.cos(a) * s * 0.3), cy + math.sin(a) * s * 0.45), fill=(200, 100, 115), width=6)
    d.line((cx, cy - s * 1.0, cx, cy - s * 0.2), fill=(220, 220, 230), width=14)
    R.heart_icon(d, cx + s * 0.12, cy + s * 0.55, s * 0.22, BLOOD, R.beat_at(t, 70))

def scene_heart_lung():
    t1 = 0.5; t2 = t1 + D['heart'] + 0.6; dur = t2 + D['lung'] + 1.0; n = int(dur * FPS); p = writer(f'{G}/c_heart.mp4'); tube = R.Tube(16, 3.0)
    for f in range(n):
        t = f / FPS; im = dark_bg(); d = ImageDraw.Draw(im)
        if t < t2 - 0.2:
            u = (t - t1) / D['heart']
            ctext(d, (W / 2, 90), 'ふつうの心臓', Mi(70), GOLD, sw=3)
            R.heart_icon(d, 330, 520, 150, BLOOD, R.beat_at(t, 60 if u < 0.62 else 170))
            ctext(d, (330, 780), '1個 約300g', Fo(40), GREY)
            if u > 0.12: rowbox(d, 330, '休んでいるとき（1分間）', '約5L', PALE, 640, 1840)
            if u > 0.42: rowbox(d, 480, '1日にすると', '約7,000L', PALE, 640, 1840)
            if u > 0.62: rowbox(d, 630, '全力の運動（よく鍛えた人・1分間）', '約25L', GOLD, 640, 1840, hl=True)
            foot(d, '※心臓が送り出す血の量（心拍出量）の目安。全力時は鍛え方で約20〜40L/分')
        else:
            u = (t - t2) / D['lung']
            ctext(d, (W / 2, 90), 'もう一つの主役：肺', Mi(70), GOLD, sw=3)
            lungs(d, 380, 520, 300, t)
            if u > 0.12: ctext(d, (1270, 220), '血は「すべて」肺を通って酸素を受け取る', Fo(40), PALE)
            if u > 0.35:
                tube.step(0.75, 1 / FPS); tube.draw(d, 880, 470, 860, 60, 0.75, label=True, fs=30)
                ctext(d, (1310, 320), '肺の細い血管（毛細血管）を通る血', Fb(32), GREY)
            if u > 0.5: rowbox(d, 650, '通り抜ける時間（休んでいるとき）', '約0.75秒', PALE, 800, 1840, lf=36)
            if u > 0.75: rowbox(d, 800, '酸素が満タンになるまで', '約0.25秒', GOLD, 800, 1840, hl=True, lf=36)
            foot(d, '※West の呼吸生理学の教科書などの値。チューブの中の血は、ゆっくり再生しています')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t1, 'heart'), (t2, 'lung')]

RULES = [('選手', '心臓の数だけがちがう', 0.05), ('勝ち', '取りこめた酸素が多いほど、前に進む', 0.18), ('心臓', 'どれも、ふつうの心臓と同じ強さ（全力で1個25L/分）', 0.36),
         ('肺', 'ふつうの肺が、ひと組だけ', 0.55), ('仮定', '肺の血管の圧力が50を超えると、血がにじむ', 0.7)]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.5; n = int(dur * FPS); bg = track_blur(0.4); p = writer(f'{G}/c_rule.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 170), 'RULES', Fb(26), GREY)
        for r, (who, txt, fr) in enumerate(RULES):
            if u < fr: continue
            y = 230 + r * 150; last = r == 4
            d.rounded_rectangle((140, y, W - 140, y + 120), 18, fill=(10, 12, 18, 225), outline=GOLD if last else None, width=4 if last else 0)
            d.rounded_rectangle((170, y + 25, 350, y + 95), 14, fill=RED if last else BLUE); ctext(d, (260, y + 60), who, Fo(38), (20, 20, 24))
            d.text((390, y + 60), txt, font=Fo(46), fill=PALE, anchor='lm')
        foot(d, '※肺の血管の圧力：肺の毛細血管の圧力の目安（mmHg）。危険ライン50はこの動画の仮定')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'rule')]

def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None):
    dur = 0.6 + D[key] + 0.8; n = int(dur * FPS); bg = track_blur(0.35); p = writer(out)
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = ease(t / 0.4)
        ctext(d, (W / 2, 230), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 380), big, Mi(int(130 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 600, y - 48, W / 2 + 600, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 560, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 560, y), val, font=Fo(52), fill=col, anchor='rm')
        if sub: foot(d, sub)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, key)]

def scene_reveal():
    dur = 0.5 + D['reveal'] + 1.5; n = int(dur * FPS); p = writer(f'{G}/c_reveal.mp4')
    rows = [(0.0, '休んでいるとき', 0.75, PALE), (0.2, '全力・心臓1個', 0.35, BLUE), (0.62, '全力・心臓2個', 0.175, (255, 160, 120))]
    tubes = [R.Tube(16, 4.0) for _ in rows]
    for f in range(n):
        t = f / FPS; im = dark_bg(); d = ImageDraw.Draw(im); u = (t - 0.5) / D['reveal']
        ctext(d, (W / 2, 90), 'なぜ2倍にならない？', Mi(76), GOLD, sw=3); ctext(d, (W / 2, 170), '肺の毛細血管を、血が通り抜ける時間', Fb(34), GREY)
        for i, (tr, lab, tt, col) in enumerate(rows):
            if u < tr: continue
            y = 330 + i * 230
            d.text((90, y - 70), lab, font=Fo(40), fill=col, anchor='lm'); d.text((1290, y - 70), f'通り抜ける時間 約{R.f2(tt)}秒', font=Fo(36), fill=PALE, anchor='rm')
            tubes[i].step(tt, 1 / FPS); tubes[i].draw(d, 190, y, 1100, 56, tt, label=True, fs=28, below=True)
            fx = 1 - math.exp(-tt / HM.TAU); sat = (HM.CV + (HM.CMAX - HM.CV) * fx) / HM.CMAX * 100
            d.text((1700, y - 40), '出口での満タン度', font=Fb(28), fill=GREY, anchor='mm'); d.text((1700, y + 20), f'{sat:.0f}%', font=Fo(64), fill=R.bcol(fx) if fx < 0.97 else (255, 120, 120), anchor='mm')
        if u > 0.85: ctext(d, (W / 2, 1000), '満タンになる前に、肺から出ていってしまう！', Mi(52), RED, sw=3)
        foot(d, '※チューブの中の血はスローで再生。満タン度は全力運動時の目安（戻ってくる血の酸素を仮定）')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'reveal')]

TAB = [1, 2, 3, 5, 10]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.8; n = int(dur * FPS); bg = track_blur(0.3); p = writer(f'{G}/c_sweep.mp4')
    reveal = [t0 + dd * x for x in (0.0, 0.05, 0.16, 0.3, 0.42)]; s1 = HM.steady(1)
    cx = [200, 600, 1040, 1520]
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '心臓の数を変えると？', Mi(70), GOLD, sw=3)
        for j, h in enumerate(['心臓の数', '肺を通る時間', '酸素（肺が無事なら）', '肺の血管の圧力']):
            ctext(d, (cx[j], 190), h, Fo(36), GREY)
        for r, N in enumerate(TAB):
            if t < reveal[r]: continue
            s = HM.steady(N); y = 280 + r * 140; hl = N == 2 and u > 0.85; bad = s['pc'] > HM.LIM
            d.rounded_rectangle((60, y - 58, W - 60, y + 58), 18, fill=(10, 12, 18, 230), outline=GOLD if hl else None, width=6 if hl else 0)
            ctext(d, (cx[0], y), f'{N}個', Fo(56), PALE)
            ctext(d, (cx[1], y), f'約{R.f2(s["tt"])}秒', Fo(50), RED if s['tt'] < 0.25 else GREEN)
            ctext(d, (cx[2], y), f'1個の 約{s["o2"] / s1["o2"]:.1f}倍', Fo(50), PALE)
            ctext(d, (cx[3], y), f'約{round(s["pc"], -1 if N == 10 else 0):.0f}' + ('  危険' if bad else '  OK'), Fo(50), RED if bad else GREEN)
        if u > 0.85: ctext(d, (W / 2, 1000), '安全なのは、2個まで！', Mi(60), GOLD, sw=3)
        foot(d, '※全力で走ったときの目安。酸素は肺が無事だとしたときの最大の量。圧力は肺の毛細血管（mmHg）の目安')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t0, 'sweep')]

def octopus(d, cx, cy, s, t):
    c = (200, 90, 110)
    for k in range(8):
        a = math.pi * (0.15 + 0.7 * k / 7); pts = []
        for j in range(14):
            q = j / 13; r = s * (0.3 + 0.9 * q); w = math.sin(t * 2 + k + q * 4) * 0.15 * q
            pts.append((cx + math.cos(a + w) * r, cy + s * 0.15 + math.sin(a + w) * r * 0.9))
        d.line(pts, fill=c, width=int(s * 0.09), joint='curve')
    d.ellipse((cx - s * 0.45, cy - s * 0.95, cx + s * 0.45, cy + s * 0.35), fill=c)
    for sx in (-1, 1):
        d.ellipse((cx + sx * s * 0.2 - s * 0.07, cy - s * 0.1, cx + sx * s * 0.2 + s * 0.07, cy + s * 0.04), fill=(250, 240, 220)); d.ellipse((cx + sx * s * 0.2 - s * 0.03, cy - s * 0.06, cx + sx * s * 0.2 + s * 0.03, cy + s * 0.0), fill=(20, 20, 20))
def scene_outro():
    dur = 0.5 + D['outro'] + 2.0; n = int(dur * FPS); p = writer(f'{G}/c_outro.mp4'); bg = track_blur(0.35)
    for f in range(n):
        t = f / FPS; u = (t - 0.5) / D['outro']
        if u < 0.46:
            im = dark_bg(); d = ImageDraw.Draw(im)
            ctext(d, (W / 2, 90), 'タコには、心臓が3つ', Mi(72), GOLD, sw=3)
            octopus(d, 560, 560, 330, t)
            if u > 0.12:
                for k, (lab, col) in enumerate([('エラ専用の心臓（右）', (150, 200, 255)), ('エラ専用の心臓（左）', (150, 200, 255)), ('全身に送る心臓', RED)]):
                    y = 330 + k * 150; d.rounded_rectangle((1060, y - 55, 1820, y + 55), 18, fill=(10, 12, 18, 230))
                    R.heart_icon(d, 1120, y, 26, col, R.beat_at(t + k * 0.2, 50)); d.text((1170, y), lab, font=Fo(44), fill=PALE, anchor='lm')
            if u > 0.36: ctext(d, (1440, 830), 'ポンプを増やすなら、', Fo(44), PALE); ctext(d, (1440, 900), '酸素を受け取る場所もいっしょに！', Fo(48), GOLD)
        elif u < 0.80:
            im = bg.copy(); d = ImageDraw.Draw(im)
            ctext(d, (W / 2, 200), '心臓がとても強い 競走馬', Mi(76), PALE, sw=4)
            d.rounded_rectangle((W / 2 - 700, 340, W / 2 + 700, 560), 24, fill=(10, 12, 18, 225), outline=RED, width=4)
            ctext(d, (W / 2, 400), 'トレーニングで全力で走ると', Fo(46), GREY); ctext(d, (W / 2, 490), '肺の血管から出血してしまう', Fo(66), RED)
            if u > 0.72: ctext(d, (W / 2, 720), '心臓は、多ければいいわけじゃない', Mi(70), GOLD, sw=4)
            foot(d, '※運動誘発性肺出血（EIPH）。Birks ほか（1997, J Appl Physiol）など')
        else:
            im = bg.copy(); d = ImageDraw.Draw(im); hero(im, 1500, 980, 420, 2, t); d = ImageDraw.Draw(im)
            ctext(d, (820, 380), '心臓は何個なら最強だと思った？', Mi(76), PALE, sw=4)
            ctext(d, (820, 500), 'コメントで教えてください', Mi(56), GOLD, sw=3)
            if u > 0.9:
                d.rounded_rectangle((820 - 520, 620, 820 + 520, 800), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (820, 670), '次に見たい「もしも」は？', Fo(50), PALE); ctext(d, (820, 750), 'リクエスト募集中！', Fo(44), GOLD)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'outro')]

def scene_battle(NA, NB, title, pre, sim_len, cues, out):
    B = R.Battle(NA, NB, sim_len + 1); dur = pre + sim_len; n = int(dur * FPS); tubes = [R.Tube(), R.Tube()]
    caps = [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in cues if k in C.CAP]; p = writer(out); sts = []
    for f in range(n):
        vt = f / FPS; st = vt - pre
        cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None)
        col = RED if cap and any(w in cap for w in ('超え', '赤くならない', '失速', 'にじ')) else (GOLD if cap else PALE)
        im = R.battle_frame(B, st, title, cap, col, tubes, f); p.stdin.write(im.tobytes()); sts.append(round(st, 3))
    p.stdin.close(); p.wait(); json.dump(dict(st=sts, NA=NA, NB=NB), open(out.replace('.mp4', '_st.json'), 'w')); return dur, cues

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['heart'] = scene_heart_lung(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
        s1, s2, s3, s10 = (HM.steady(k) for k in (1, 2, 3, 10))
        res['res1'] = scene_card('res1', 'RESULT  1回戦', [('取りこめた酸素（1分間）', f'約{s2["o2"]:.0f}L', GOLD), ('ふつうの人とくらべて', f'約{s2["o2"] / s1["o2"]:.1f}倍', PALE), ('でも…', '2倍には届かない', RED)], f'{G}/c_res1.mp4', big='心臓2個の勝ち', bigcol=GOLD)
        res['res2'] = scene_card('res2', 'RESULT  2回戦', [('心臓3個の肺の血管の圧力', f'約{s3["pc"]:.0f}', RED), ('危険ライン（仮定）', '50', GOLD), ('心臓を増やしたのに', '逆効果', RED)], f'{G}/c_res2.mp4', big='心臓2個の勝ち', bigcol=GOLD)
        res['res3'] = scene_card('res3', 'RESULT  決勝戦', [('心臓10個の肺の血管の圧力', '約200', RED), ('取りこめる酸素（肺が傷ついた後）', 'ふつうの人以下', RED), ('いちばん強いのは', '心臓2個', GOLD)], f'{G}/c_res3.mp4', big='優勝は心臓2個', bigcol=GOLD)
    elif which == 'r1':
        res['r1'] = scene_battle(1, 2, '1回戦　ふつうの人 vs 心臓2個', 5.4, 11.0, [(0.2, 'r1a'), (6.6, 'r1b'), (11.6, 'r1c')], f'{G}/c_r1.mp4')
    elif which == 'r2':
        res['r2'] = scene_battle(2, 3, '2回戦　心臓2個 vs 心臓3個', 4.0, 19.0, [(0.2, 'r2a'), (6.0, 'r2b'), (9.2, 'r2c'), (18.9, 'r2d')], f'{G}/c_r2.mp4')
    elif which == 'r3':
        res['r3'] = scene_battle(2, 10, '決勝戦　心臓2個 vs 心臓10個', 4.6, 16.6, [(0.2, 'r3a'), (8.0, 'r3b'), (13.4, 'r3c'), (16.8, 'r3d')], f'{G}/c_r3.mp4')
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
