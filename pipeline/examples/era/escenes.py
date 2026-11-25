import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import erender as R, emodel as EM, econtent as C
from erender import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ctext, fade, ease, writer
G = '/home/claude/era'; D = json.load(open(f'{G}/dur.json'))
def dark_bg(): return Image.new('RGB', (W, H), (10, 18, 28))
def wblur(kind='lake', dark=0.5):
    return ImageEnhance.Brightness(R.water_bg(kind).convert('RGB').filter(ImageFilter.GaussianBlur(8))).enhance(dark)
def foot(d, s): d.text((W - 24, H - 16), s, font=Fb(20), fill=(200, 200, 205), anchor='rs')
def rowbox(d, y, lab, val, col, x0=W / 2 - 600, x1=W / 2 + 600, hl=False, lf=40, vf=60):
    d.rounded_rectangle((x0, y - 55, x1, y + 55), 18, fill=(10, 12, 18, 230), outline=GOLD if hl else None, width=4 if hl else 0)
    d.text((x0 + 40, y), lab, font=Fo(lf), fill=PALE, anchor='lm'); d.text((x1 - 40, y), val, font=Fo(vf), fill=col, anchor='rm')
def run(out, dur, fn):
    p = writer(out)
    for f in range(int(dur * FPS)):
        im = fn(f / FPS); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()

def scene_title():
    dur = 0.6 + D['intro'] + 0.6; base = R.water_bg('lake').convert('RGB')
    def fr(t):
        im = base.copy(); d = ImageDraw.Draw(im, 'RGBA'); R.bubbles(d, t, 0, W, 0, H, 40, 9)
        R.swimmer(d, 1350, 760, 900, t, 'gill', 0, 1.8, flow=0.8); u = ease(t / 0.5)
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (110, 330), 'エラがあったら', Mi(int(110 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (110, 520), '水中で暮らせる？', Mi(150), GOLD, 'lm', 8)
        if t > 0.8: ctext(d, (116, 680), 'WHAT IF HUMANS HAD GILLS?', Fb(34), (225, 225, 230), 'lm', 2)
        if t > 1.0: ctext(d, (110, 790), '息つぎなしで、ずっと水の中…のはず？', Fo(46), PALE, 'lm', 3)
        d.text((W - 24, H - 16), R.NOTE, font=Fb(20), fill=(220, 220, 225), anchor='rs'); return im
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]

def beaker(d, cx, by, w, h, n, col, t, seed, label, water=False):
    d.rectangle((cx - w / 2, by - h, cx + w / 2, by), fill=(60, 130, 190, 150) if water else (200, 220, 240, 40), outline=(230, 240, 250), width=5)
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = cx - w / 2 + 14 + rng.uniform(0, w - 28) + math.sin(t * 2 + k) * 4; y = by - 14 - rng.uniform(0, h - 28) + math.cos(t * 1.7 + k) * 4
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col)
    ctext(d, (cx, by + 50), label, Fo(44), PALE)
def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8
    def fr(t):
        im = dark_bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '空気と水をくらべると', Mi(70), GOLD, sw=3)
        beaker(d, 260, 640, 280, 380, 93, (255, 120, 120), t, 1, '空気 1L'); beaker(d, 620, 640, 280, 380, 3, (255, 120, 120), t, 2, '水 1L（20℃）', True)
        ctext(d, (440, 790), '● ＝ 酸素 約3mg', Fb(30), (255, 150, 150))
        rows = [(0.05, '1Lの中の酸素（空気）', '約280mg', PALE, False), (0.2, '1Lの中の酸素（20℃の水）', '約9mg', PALE, False), (0.36, '水の酸素は空気の', '約30分の1', RED, True),
                (0.55, '重さ（水 ÷ 空気）', '約800倍', GOLD, False), (0.72, '体を冷やす速さ（水 ÷ 空気）', '24倍以上', CYAN, True)]
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 240 + r * 150, lab, val, col, 900, 1860, hl, lf=36, vf=56)
        foot(d, '※空気の酸素は20℃・1気圧の計算値。水は淡水・飽和（USGS）。冷やす速さは Minnesota Sea Grant')
        return im
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]

def scene_fish():
    t0 = 0.5; dd = D['fish']; dur = t0 + dd + 0.8; bg = wblur('lake', 0.55)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), 'エラは、酸素を取りこむ名人', Mi(68), GOLD, sw=3)
        R.trout(d, 500, 470, 620, t, 0.5 + 0.5 * math.sin(t * 3))
        for k in range(10):   # 口からエラへ流れる水
            q = (t * 0.8 + k / 10) % 1.0; x = 920 - q * 320; y = 470 + math.sin(k * 1.7) * 60
            d.line((x, y, x + 30, y), fill=(210, 240, 255, int(220 * (1 - q))), width=4)
        ctext(d, (470, 760), 'ニジマス（マス）', Fo(40), PALE, sw=2)
        if u > 0.15: rowbox(d, 300, 'エラに通す水', '体重1kgあたり 毎分 約0.3L', PALE, 960, 1860, lf=32, vf=40)
        if u > 0.35: rowbox(d, 450, 'エラが取りこむ酸素の割合', '約67%', GOLD, 960, 1860, True, lf=34)
        if u > 0.62: rowbox(d, 600, '人の肺が取りこむ酸素の割合', '約4分の1', PALE, 960, 1860, lf=34)
        if u > 0.82: ctext(d, (1410, 760), '効率はエラのほうが、ずっと上！', Fo(48), GOLD, sw=3)
        foot(d, '※マスの値：Eom & Wood（2023, Fish Physiol Biochem）。肺は吸った空気の酸素21%のうち約5%分を取りこむ目安')
        return im
    run(f'{G}/c_fish.mp4', dur, fr); return dur, [(t0, 'fish')]

RULES = [('人', '体重70kgの人に、エラを付けて水にもぐる', 0.05), ('酸素', '休んでいても 毎分 約250mL 使う', 0.27), ('ため', '体にためておける酸素は 約1L（仮定）', 0.52),
         ('限界', '酸素がなくなる か 体温が28℃まで下がる', 0.75)]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; bg = wblur('pool', 0.4)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 170), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 240 + r * 170; last = r == 3
            d.rounded_rectangle((140, y, W - 140, y + 130), 18, fill=(10, 12, 18, 225), outline=GOLD if last else None, width=4 if last else 0)
            d.rounded_rectangle((170, y + 30, 350, y + 100), 14, fill=RED if last else BLUE); ctext(d, (260, y + 65), who, Fo(38), (20, 20, 24))
            d.text((390, y + 65), txt, font=Fo(48), fill=PALE, anchor='lm')
        foot(d, '※休んでいるときの酸素は約3.5mL/kg/分の目安。28℃以下は重い低体温症の目安')
        return im
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]

def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None, kind='pool'):
    dur = 0.6 + D[key] + 0.8; bg = wblur(kind, 0.35)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.4)
        ctext(d, (W / 2, 230), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 380), big, Mi(int(120 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 620, y - 48, W / 2 + 620, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 580, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 580, y), val, font=Fo(52), fill=col, anchor='rm')
        if sub: foot(d, sub)
        return im
    run(out, dur, fr); return dur, [(0.6, key)]

def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0
    temps = [10, 20, 30, 36]
    def fr(t):
        im = dark_bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), 'なぜ、マスと同じエラでは足りない？', Mi(66), GOLD, sw=3)
        if u < 0.42:
            ctext(d, (W / 2, 190), '体重1kgあたり、1分間に使う酸素', Fo(44), PALE)
            for i, (lab, v, col) in enumerate([('人（37℃の体）', 3.6, RED), ('マス（8℃の水）', 1.6, BLUE)]):
                y = 360 + i * 200; d.text((140, y), lab, font=Fo(46), fill=col, anchor='lm')
                R.bar(d, 620, y, 620 + 1000 * v / 3.6 * ease((u - 0.05 - i * 0.08) / 0.1), 1, col, 70)
                d.text((1680, y), f'約{v}mL', font=Fo(52), fill=PALE, anchor='lm')
            if u > 0.2: ctext(d, (W / 2, 800), '人は、マスの 約2倍！', Mi(76), GOLD, sw=3)
            if u > 0.3: ctext(d, (W / 2, 920), '体温37℃を保つため、燃料を燃やし続けている', Fo(42), PALE)
        else:
            ctext(d, (W / 2, 190), '水の温度と、とけている酸素（1Lあたり）', Fo(44), PALE)
            for i, tc in enumerate(temps):
                x = 300 + i * 260; v = EM.DO(tc); hh = v / 11.3 * 380 * ease((u - 0.45 - i * 0.03) / 0.08)
                d.rounded_rectangle((x - 70, 700 - hh, x + 70, 700), 12, fill=R.mix(BLUE, RED, (tc - 10) / 26))
                ctext(d, (x, 680 - hh - 30), f'{v:.1f}mg', Fo(40), PALE); ctext(d, (x, 750), f'{tc}℃', Fo(44), GREY)
            if u > 0.7:
                rowbox(d, 380, '必要な水（36℃）', '毎分 約78L', GOLD, 1150, 1880, True, lf=30, vf=46)
                rowbox(d, 530, 'マス並みのエラ', '毎分 約21L', PALE, 1150, 1880, lf=30, vf=46)
            if u > 0.86: ctext(d, (1545, 700), '約3.7倍 足りない！', Mi(64), RED, sw=3)
            ctext(d, (560, 850), '温かい水ほど、酸素は少ない', Fo(46), CYAN)
        foot(d, '※人：約250mL÷70kg。マス：Eom & Wood（2023）の安静時の値。水の酸素：淡水・飽和（USGS、Benson & Krause の式）')
        return im
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]

SW = [('休んでいる', 250, '約59L', '約30本', '約2.8倍'), ('歩くくらい', 1000, '約235L', '約118本', '約11倍'), ('全力で泳ぐ', 3000, '約700L', '約350本', '約34倍')]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; bg = wblur('lake', 0.3)
    reveal = [t0 + dd * x for x in (0.0, 0.42, 0.62)]; cx = [230, 620, 1000, 1360, 1700]
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '20℃の湖で、動くと？', Mi(70), GOLD, sw=3)
        for j, h in enumerate(['動き方', '使う酸素（毎分）', 'エラに通す水（毎分）', '2Lペットボトル', 'マス並みのエラの']):
            ctext(d, (cx[j], 200), h, Fo(32), GREY)
        for r, (lab, o2, wv, pb, tr) in enumerate(SW):
            if t < reveal[r]: continue
            y = 310 + r * 160
            d.rounded_rectangle((60, y - 65, W - 60, y + 65), 18, fill=(10, 12, 18, 230), outline=GOLD if r == 2 and u > 0.8 else None, width=6)
            ctext(d, (cx[0], y), lab, Fo(48), PALE); ctext(d, (cx[1], y), f'約{o2:,}mL', Fo(48), PALE); ctext(d, (cx[2], y), wv, Fo(60), GOLD if r == 0 else RED)
            ctext(d, (cx[3], y), pb, Fo(48), PALE); ctext(d, (cx[4], y), tr, Fo(48), RED)
        if u > 0.25: ctext(d, (W / 2, 820), '休むだけでも、毎分 自分の体重くらいの水', Fo(48), CYAN, sw=2)
        if u > 0.8: ctext(d, (W / 2, 940), '全力なら、毎分 お風呂 約3杯半！', Mi(64), GOLD, sw=3)
        foot(d, '※20℃の淡水、エラが酸素の67%を取りこむとした計算。使う酸素は目安。お風呂1杯＝200Lとした')
        return im
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]

def heater(d, x, y, s, glow):
    d.rounded_rectangle((x - s * 0.5, y - s * 0.7, x + s * 0.5, y + s * 0.7), 12, fill=(70, 70, 80), outline=(160, 160, 170), width=3)
    for k in range(3):
        yy = y - s * 0.4 + k * s * 0.4; d.rounded_rectangle((x - s * 0.38, yy - 7, x + s * 0.38, yy + 7), 7, fill=R.mix((120, 40, 20), (255, 150, 60), glow))
def scene_heat():
    t0 = 0.5; dd = D['heat']; dur = t0 + dd + 1.0
    def fr(t):
        im = dark_bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '犯人は、エラそのもの', Mi(72), GOLD, sw=3)
        if u < 0.5:
            # うすい膜をはさんで、血と水がすれちがう
            y0, y1 = 360, 620; x0, x1 = 260, 1660
            d.rectangle((x0, y0 - 120, x1, y0 - 10), fill=(40, 110, 170)); d.rectangle((x0, y0 + 10, x1, y0 + 120), fill=(120, 30, 40))
            d.rectangle((x0, y0 - 10, x1, y0 + 10), fill=(250, 200, 200))
            ctext(d, (x0 - 20, y0 - 65), '水', Fo(44), CYAN, 'rm'); ctext(d, (x0 - 20, y0 + 65), '血', Fo(44), RED, 'rm')
            for k in range(12):
                q = (t * 0.25 + k / 12) % 1.0
                xw = x1 - q * (x1 - x0); d.line((xw, y0 - 65, xw - 40, y0 - 65), fill=(220, 240, 255), width=4)
                xb = x0 + q * (x1 - x0); cb = R.mix((230, 60, 60), (120, 140, 220), q); d.ellipse((xb - 18, y0 + 47, xb + 18, y0 + 83), fill=cb)
            ctext(d, (W / 2, y0 + 170), '水の流れ ←　うすい膜　→ 血の流れ', Fo(38), GREY)
            if u > 0.18: ctext(d, (W / 2, 690), '酸素を受け取るしくみ ＝ 熱も逃がすしくみ', Fo(52), PALE, sw=2)
            if u > 0.33:
                d.rounded_rectangle((260, 790, 1660, 920), 20, fill=(10, 12, 18, 230), outline=GOLD, width=4)
                ctext(d, (W / 2, 855), 'エラを通った血は、水と同じ温度になる', Fo(54), GOLD)
        else:
            q = (u - 0.5) / 0.5
            for i, (lab, v, col) in enumerate([('体が作る熱（休んでいるとき）', '約84W', GREEN), ('20℃の水の中のエラから逃げる熱（最初）', '約5,400W', RED)]):
                if q < i * 0.25: continue
                rowbox(d, 260 + i * 150, lab, v, col, 160, 1760, i == 1, lf=40, vf=64)
            if q > 0.6:
                for k in range(5): heater(d, 560 + k * 200, 720, 140, 0.5 + 0.5 * math.sin(t * 4 + k))
                ctext(d, (W / 2, 900), '電気ストーブ 5台分以上！', Mi(72), RED, sw=3)
        foot(d, '※熱：心臓が送る血 毎分5L が37℃→20℃に冷えるとした計算（目安）。体が作る熱は酸素1Lあたり約20kJ。ストーブ1台＝1,000W')
        return im
    run(f'{G}/c_heat.mp4', dur, fr); return dur, [(t0, 'heat')]

TT = [(10, '約1分', '約5分'), (26, '約2分40秒', '約23分'), (30, '約4分30秒', '下がりきらない（約30℃に）'), (36, '下がらない', '下がらない')]
def scene_temp():
    t0 = 0.5; dd = D['temp']; dur = t0 + dd + 1.2; bg = wblur('lake', 0.3)
    reveal = [t0 + dd * x for x in (0.08, 0.27, 0.48, 0.66)]; cx = [250, 640, 1050, 1530]
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '水の温度を変えると？（巨大なエラ）', Mi(64), GOLD, sw=3)
        for j, h in enumerate(['水温', '必要な水（毎分）', '体温35℃まで', '体温28℃まで（限界）']): ctext(d, (cx[j], 190), h, Fo(32), GREY)
        for r, (tc, a, b) in enumerate(TT):
            if t < reveal[r]: continue
            y = 290 + r * 140; ok = tc == 36
            d.rounded_rectangle((60, y - 58, W - 60, y + 58), 18, fill=(10, 12, 18, 230), outline=GOLD if ok and u > 0.8 else None, width=6)
            ctext(d, (cx[0], y), f'{tc}℃', Fo(56), R.mix(BLUE, RED, (tc - 10) / 26)); ctext(d, (cx[1], y), f'約{EM.need_water(tc):.0f}L', Fo(48), PALE)
            ctext(d, (cx[2], y), a, Fo(46), GREEN if ok else PALE); ctext(d, (cx[3], y), b, Fo(46 if len(b) < 8 else 36), GREEN if ok else RED)
        if u > 0.82: ctext(d, (W / 2, 900), 'エラ人間が暮らせるのは、お風呂！', Mi(76), GOLD, sw=4)
        foot(d, '※20℃は決勝戦のとおり約10分。休んでいるときの計算（目安）。体温より熱いお湯では、逆に熱がこもる')
        return im
    run(f'{G}/c_temp.mp4', dur, fr); return dur, [(t0, 'temp')]

def whale(d, cx, cy, s, t):
    c = (70, 90, 120); body = [(cx + s * 0.5, cy), (cx + s * 0.3, cy - s * 0.18), (cx - s * 0.2, cy - s * 0.16), (cx - s * 0.55, cy - s * 0.02), (cx - s * 0.2, cy + s * 0.14), (cx + s * 0.35, cy + s * 0.13)]
    d.polygon(body, fill=c); w = math.sin(t * 1.5) * s * 0.08
    d.polygon([(cx - s * 0.52, cy), (cx - s * 0.75, cy - s * 0.15 + w), (cx - s * 0.68, cy + w * 0.3), (cx - s * 0.75, cy + s * 0.12 + w)], fill=c)
    d.ellipse((cx + s * 0.3, cy - s * 0.04, cx + s * 0.33, cy - s * 0.01), fill=(10, 10, 10))
    for k in range(4):
        q = (t * 0.6 + k / 4) % 1; d.ellipse((cx + s * 0.15 - 6, cy - s * 0.2 - q * s * 0.4 - 6, cx + s * 0.15 + 6, cy - s * 0.2 - q * s * 0.4 + 6), outline=(220, 240, 255), width=2)
def tuna(d, cx, cy, s, t, warm):
    body = [(cx + s * 0.5, cy), (cx + s * 0.2, cy - s * 0.2), (cx - s * 0.3, cy - s * 0.12), (cx - s * 0.5, cy), (cx - s * 0.3, cy + s * 0.12), (cx + s * 0.2, cy + s * 0.18)]
    d.polygon(body, fill=(50, 70, 110)); d.ellipse((cx - s * 0.22, cy - s * 0.08, cx + s * 0.22, cy + s * 0.08), fill=R.mix((120, 60, 60), (255, 110, 60), warm))
    w = math.sin(t * 5) * s * 0.06; d.polygon([(cx - s * 0.48, cy), (cx - s * 0.7, cy - s * 0.25 + w), (cx - s * 0.6, cy + w), (cx - s * 0.7, cy + s * 0.25 + w)], fill=(50, 70, 110))
    d.ellipse((cx + s * 0.32, cy - s * 0.04, cx + s * 0.37, cy + s * 0.01), fill=(240, 240, 240))
    d.arc((cx + s * 0.1, cy - s * 0.15, cx + s * 0.25, cy + s * 0.15), 110, 250, fill=(120, 170, 230), width=6)
def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; bg = wblur('lake', 0.45)
    def fr(t):
        u = (t - 0.5) / D['outro']; im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA')
        if u < 0.25:
            ctext(d, (W / 2, 100), 'クジラやイルカは、肺のまま', Mi(72), GOLD, sw=3); whale(d, 820, 560, 1000, t)
            if u > 0.12: ctext(d, (W / 2, 900), '海に戻ったほ乳類なのに、息つぎをしている', Fo(50), PALE, sw=2)
        elif u < 0.62:
            ctext(d, (W / 2, 100), 'マグロは、筋肉を温かく保てる', Mi(72), GOLD, sw=3); tuna(d, 760, 540, 900, t, 0.5 + 0.5 * math.sin(t * 2))
            if u > 0.33:
                d.rounded_rectangle((1220, 380, 1840, 560), 20, fill=(10, 12, 18, 230), outline=RED, width=4)
                ctext(d, (1530, 430), '泳ぐ筋肉は、まわりの水より', Fo(34), GREY); ctext(d, (1530, 505), '最大14℃も温かい', Fo(56), RED)
            if u > 0.45: ctext(d, (1530, 660), '熱を逃がさない特別な血管', Fo(40), PALE); ctext(d, (1530, 730), 'でも、エラの血は冷たいまま', Fo(40), CYAN)
            foot(d, '※冬に泳ぐマグロの例（Kimball の Biology Pages）')
        elif u < 0.8:
            ctext(d, (W / 2, 380), '体温の高い生き物にとって', Mi(70), PALE, sw=3); ctext(d, (W / 2, 540), 'エラは「体を冷やすラジエーター」', Mi(84), GOLD, sw=4)
        else:
            R.swimmer(d, 1400, 900, 600, t, 'gill', 0.2, 1.4, flow=0.6)
            ctext(d, (760, 330), 'エラと肺、どっちがほしい？', Mi(76), PALE, sw=4); ctext(d, (760, 450), 'コメントで教えてください', Mi(56), GOLD, sw=3)
            if u > 0.92:
                d.rounded_rectangle((760 - 520, 580, 760 + 520, 760), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (760, 630), '次に見たい「もしも」は？', Fo(50), PALE); ctext(d, (760, 710), 'リクエスト募集中！', Fo(44), GOLD)
        return im
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]

def scene_battle(qa, qb, tw, title, pre, rate, cues, out, gsize=1.0, gname='エラの人', tail=1.3):
    """cues：(シミュレーション分 or -1=準備中の秒, key)。rate：1秒あたりのシミュレーション分"""
    Bt = R.Battle(qa, qb, tw, gsize, 14.0); endall = max(Bt.endA, Bt.endB); dur = pre + endall / rate + tail; n = int(dur * FPS)
    vc = [(c if k == 'pre' else pre + c / rate, key) for c, key, k in cues]
    for (a, k1), (b, k2) in zip(vc, vc[1:]): assert a + D[k1] < b + 0.05, (k1, a + D[k1], k2, b)
    caps = [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in vc if k in C.CAP]; p = writer(out); sts = []
    for f in range(n):
        vt = f / FPS; st = (vt - pre) * rate if vt >= pre else -1
        cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None)
        col = RED if cap and any(w in cap for w in ('限界', '減って', '下がって', '切った')) else (GOLD if cap else PALE)
        im = R.battle_frame(Bt, st, title, cap, col, vt, rate, gname); p.stdin.write(im.tobytes()); sts.append(round(st, 4))
    p.stdin.close(); p.wait(); json.dump(dict(st=sts, ends=[Bt.endA, Bt.endB], pre=pre, rate=rate), open(out.replace('.mp4', '_st.json'), 'w')); return dur, vc

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['data'] = scene_data(); res['fish'] = scene_fish(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep()
        res['heat'] = scene_heat(); res['temp'] = scene_temp(); res['outro'] = scene_outro()
        up = EM.uptake(EM.TROUT, 36)
        res['res1'] = scene_card('res1', 'RESULT  1回戦', [('もった時間', '約5分半（息止めは4分）', GOLD), ('エラから取りこめた酸素', f'毎分 約{up:.0f}mL', PALE), ('必要な量（250mL）の', f'約{up / 250 * 100:.0f}%', RED)], f'{G}/c_res1.mp4', big='エラの人の勝ち', kind='pool')
        res['res2'] = scene_card('res2', 'RESULT  決勝戦', [('もった時間', '約10分（息止めは4分）', GOLD), ('酸素', '最後まで足りていた', GREEN), ('限界の理由', '体温が28℃まで下がった', RED)], f'{G}/c_res2.mp4', big='優勝は巨大なエラの人', kind='lake')
    elif which == 'fix':
        res = json.load(open(f'{G}/scene_static.json')); res['outro'] = scene_outro(); which = 'static'
    elif which == 'r1':
        pre = D['r1a'] + 0.4
        res['r1'] = scene_battle(None, EM.TROUT, 36, '1回戦　息止め vs マスと同じ割合のエラ', pre, 0.35, [(0.2, 'r1a', 'pre'), (0.25, 'r1b', 's'), (1.5, 'r1c', 's'), (4.0, 'r1d', 's')], f'{G}/c_r1.mp4')
    elif which == 'r2':
        pre = D['r2a'] + 0.4
        res['r2'] = scene_battle(None, 60, 20, '決勝戦　息止め vs 巨大なエラ', pre, 0.55, [(0.2, 'r2a', 'pre'), (0.25, 'r2b', 's'), (1.4, 'r2c', 's'), (4.55, 'r2d', 's'), (9.87, 'r2e', 's')], f'{G}/c_r2.mp4', 2.2, '巨大なエラの人')
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
