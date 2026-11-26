import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import wrender as R, wmodel as M, wcontent as C
from wrender import W, H, FPS, Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, BLUE, CYAN, ORANGE, ctext, fade, ease, writer
G = '/home/claude/wng'; D = json.load(open(f'{G}/dur.json'))
def dark_bg(): return Image.new('RGB', (W, H), (12, 16, 30))
def sblur(dark=0.45, dusk=0.0): return ImageEnhance.Brightness(R.sky_bg(dusk=dusk).convert('RGB').filter(ImageFilter.GaussianBlur(8))).enhance(dark)
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
    dur = 0.6 + D['intro'] + 0.6; base = R.sky_bg().convert('RGB')
    def fr(t):
        im = base.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.5)
        R.winged(d, 1400, 470 + math.sin(t * 1.2) * 20, 900, t * 0.5, 0.8)
        d.rounded_rectangle((100, 110, 600, 170), 30, fill=(0, 0, 0, 190)); ctext(d, (350, 140), '実データでシミュレーション', Fb(32), GOLD)
        ctext(d, (110, 330), '翼があったら', Mi(int(110 * (1.3 - 0.3 * u))), PALE, 'lm', 6)
        if t > 0.4: ctext(d, (110, 520), '人間は飛べる？', Mi(150), GOLD, 'lm', 8)
        if t > 0.8: ctext(d, (116, 680), 'WHAT IF HUMANS HAD WINGS?', Fb(34), (245, 245, 250), 'lm', 3)
        if t > 1.0: ctext(d, (110, 790), '羽ばたいて、どこまでも…のはず？', Fo(46), PALE, 'lm', 3)
        d.text((W - 24, H - 16), R.NOTE, font=Fb(20), fill=(240, 240, 245), anchor='rs'); return im
    run(f'{G}/c_title.mp4', dur, fr); return dur, [(0.6, 'intro')]

def scene_data():
    t0 = 0.5; dd = D['data']; dur = t0 + dd + 0.8; bg = sblur(0.35)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '鳥と人間をくらべると', Mi(70), GOLD, sw=3)
        rows = [(0.08, '飛べる鳥でいちばん重い（アフリカオオノガン）', '約19kg', PALE, False), (0.33, 'いちばん翼が長い鳥（ワタリアホウドリ）', '最大 約3.6m', PALE, False),
                (0.55, '羽ばたく筋肉（鳥の平均）', '体重の約20%', GOLD, True), (0.78, '人間（この動画の設定）', '体重60kg ＝ 3倍以上', RED, True)]
        for r, (tr, lab, val, col, hl) in enumerate(rows):
            if u < tr: continue
            rowbox(d, 250 + r * 170, lab, val, col, 120, 1800, hl, lf=40, vf=58)
        foot(d, '※鳥の重さ・翼：ロンドン自然史博物館。筋肉：Biewener（2022, Current Biology）。胸の大きな筋肉が平均17%、ほかの羽ばたく筋肉を合わせて約20%')
        return im
    run(f'{G}/c_data.mp4', dur, fr); return dur, [(t0, 'data')]

def scene_power():
    t0 = 0.5; dd = D['power']; dur = t0 + dd + 0.8; bg = sblur(0.3)
    items = [(0.3, '数秒だけ（最大）', M.PEAK, RED), (0.5, '30秒の平均', M.MEAN30, ORANGE), (0.8, '長い時間続けられる（仮定）', M.CP, GREEN)]
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '人間が全身で出せるパワー（体重60kg）', Mi(64), GOLD, sw=3)
        if u > 0.12: ctext(d, (W / 2, 190), '自転車をこぐテストの値：体重1kgあたり 最大12.7W・30秒平均8.5W', Fo(38), PALE)
        for i, (tr, lab, v, col) in enumerate(items):
            if u < tr: continue
            y = 380 + i * 190; d.text((140, y), lab, font=Fo(46), fill=col, anchor='lm')
            R.bar(d, 820, y, 820 + 820 * v / 800 * ease((u - tr) / 0.08), 1, col, 70)
            d.text((1700, y), f'約{v:,.0f}W', font=Fo(56), fill=PALE, anchor='rm') if False else d.text((1780, y - 60), f'約{v:,.0f}W', font=Fo(52), fill=PALE, anchor='rm')
        foot(d, '※ふつうに運動する男性の値（Grant ほか 2014, BioMed Research International）を体重60kgにしたもの。長く続けられる力は1kgあたり3.5Wと仮定')
        return im
    run(f'{G}/c_power.mp4', dur, fr); return dur, [(t0, 'power')]

RULES = [('人', '体重60kgの人に、鳥と同じ形の翼を付ける', 0.04), ('翼', '翼の重さは 幅1mあたり1kg（仮定）', 0.27), ('力', '腕でも、脚と同じパワーが出せる（甘めの仮定）', 0.47),
         ('勝負', '高さ30mの丘から飛び、着地までの時間と距離', 0.68)]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; bg = sblur(0.4)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 170), 'RULES', Fb(26), GREY)
        for r, (who, txt, frr) in enumerate(RULES):
            if u < frr: continue
            y = 240 + r * 170; last = r == 3
            d.rounded_rectangle((140, y, W - 140, y + 130), 18, fill=(10, 12, 18, 225), outline=GOLD if last else None, width=4 if last else 0)
            d.rounded_rectangle((170, y + 30, 350, y + 100), 14, fill=RED if last else BLUE); ctext(d, (260, y + 65), who, Fo(38), (20, 20, 24))
            d.text((390, y + 65), txt, font=Fo(48), fill=PALE, anchor='lm')
        foot(d, '※翼の形は鳥にあわせて、速さ・パワーは空気の力の式（誘導抵抗＋形の抵抗）で計算した目安')
        return im
    run(f'{G}/c_rule.mp4', dur, fr); return dur, [(0.5, 'rule')]

def scene_card(key, title, lines, out, big=None, bigcol=GOLD, sub=None):
    dur = 0.6 + D[key] + 0.8; bg = sblur(0.3)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(t / 0.4)
        ctext(d, (W / 2, 230), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 380), big, Mi(int(120 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 660, y - 48, W / 2 + 660, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 620, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 620, y), val, font=Fo(50), fill=col, anchor='rm')
        if sub: foot(d, sub)
        return im
    run(out, dur, fr); return dur, [(0.6, key)]

def chest(d, cx, cy, s, frac, col):
    """胸の筋肉のふくらみ（正面）：frac = 体重に対する割合"""
    d.rounded_rectangle((cx - s * 0.32, cy - s * 0.1, cx + s * 0.32, cy + s * 0.75), int(s * 0.12), fill=(60, 110, 200))
    k = 0.15 + frac * 2.2
    d.ellipse((cx - s * 0.3 - s * k * 0.3, cy - s * 0.05, cx + s * 0.02, cy + s * 0.25 + s * k * 0.3), fill=col)
    d.ellipse((cx - s * 0.02, cy - s * 0.05, cx + s * 0.3 + s * k * 0.3, cy + s * 0.25 + s * k * 0.3), fill=col)
    d.ellipse((cx - s * 0.13, cy - s * 0.42, cx + s * 0.13, cy - s * 0.12), fill=(228, 182, 148))
def scene_reveal():
    t0 = 0.5; dd = D['reveal']; dur = t0 + dd + 1.0; F4 = M.Flight(4.0, 6)
    need = F4.preq; mus = need / 89
    def fr(t):
        im = dark_bg(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), 'なぜ、飛び続けられない？', Mi(70), GOLD, sw=3)
        if u < 0.5:
            ctext(d, (W / 2, 190), '幅4mの翼（体重60kg）で飛び続けるのに必要なパワー', Fo(42), PALE)
            for i, (lab, v, col) in enumerate([('必要なパワー', need, RED), ('数秒だけの全力', M.PEAK, ORANGE), ('長く続けられる力', M.CP, GREEN)]):
                if u < 0.08 + i * 0.12: continue
                y = 350 + i * 170; d.text((140, y), lab, font=Fo(46), fill=col, anchor='lm')
                R.bar(d, 640, y, 640 + 1000 * v / need * ease((u - 0.08 - i * 0.12) / 0.06), 1, col, 70)
                d.text((1800, y - 62), f'約{v:,.0f}W', font=Fo(46), fill=PALE, anchor='rm')
            if u > 0.32: ctext(d, (W / 2, 900), f'全力の約{need / M.PEAK:.1f}倍、続けられる力の約{need / M.CP:.0f}倍！', Mi(64), GOLD, sw=3)
        else:
            q = (u - 0.5) / 0.5
            ctext(d, (W / 2, 190), '鳥の胸の筋肉で飛ぶとしたら', Fo(44), PALE)
            if q > 0.05: rowbox(d, 330, '鳥の胸の筋肉が出すパワー', '1kgあたり 約89W', PALE, 760, 1840, lf=34, vf=46)
            if q > 0.3: rowbox(d, 480, '必要な羽ばたく筋肉', f'約{mus:.0f}kg', RED, 760, 1840, True, lf=34, vf=56)
            if q > 0.55: rowbox(d, 630, '体重の', '約3分の1！', RED, 760, 1840, True, lf=34, vf=56)
            chest(d, 380, 470, 380, min(0.34, 0.05 + 0.29 * ease((q - 0.3) / 0.5)), (225, 140, 120))
            if q > 0.72: ctext(d, (W / 2, 880), '鳥（平均 約20%）より、ずっと多い', Fo(50), CYAN, sw=2)
        foot(d, '※必要なパワーは計算の目安。鳥の胸の筋肉：ハトがふつうに飛ぶときの値（Biewener 2022）')
        return im
    run(f'{G}/c_reveal.mp4', dur, fr); return dur, [(t0, 'reveal')]

SW = [(4, 6), (8, 10), (12, 14), (20, 18), (30, 19.7)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.2; bg = sblur(0.3)
    reveal = [t0 + dd * x for x in (0.0, 0.15, 0.32, 0.47, 0.63)]; cx = [230, 600, 1000, 1360, 1690]
    rows = []
    for b, ar in SW:
        F = M.Flight(b, ar); rows.append((b, F.preq, F.v * 3.6, F.preq / 89, F.end))
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 80), '翼の幅を広げると？（ふつうの人）', Mi(66), GOLD, sw=3)
        for j, h in enumerate(['翼の幅', '必要なパワー', '飛ぶ速さ', '必要な胸の筋肉', '飛べる時間']): ctext(d, (cx[j], 190), h, Fo(32), GREY)
        for r, (b, p, v, mk, end) in enumerate(rows):
            if t < reveal[r]: continue
            y = 290 + r * 125; ok = p < M.CP
            d.rounded_rectangle((60, y - 54, W - 60, y + 54), 18, fill=(10, 12, 18, 230), outline=GOLD if b == 30 and u > 0.7 else None, width=6)
            ctext(d, (cx[0], y), f'{b}m', Fo(54), PALE); ctext(d, (cx[1], y), f'約{p:,.0f}W', Fo(50), RED if p > M.PEAK else (GOLD if p > M.CP else GREEN))
            ctext(d, (cx[2], y), f'時速{v:.0f}km', Fo(44), PALE); ctext(d, (cx[3], y), f'約{mk:.1f}kg', Fo(46), PALE)
            ctext(d, (cx[4], y), (f'約{end:.0f}秒' if end < 90 else f'約{end / 60:.0f}分') if end else 'ずっと', Fo(46), GREEN if ok else PALE)
        if u > 0.82: ctext(d, (W / 2, 940), '30mでも、続けられる210Wに あと少し届かない', Mi(56), GOLD, sw=3)
        foot(d, '※高さ30mから飛んだときの計算（目安）。翼が広いほど重くなる分も入れている。胸の筋肉は1kgあたり89Wとした')
        return im
    run(f'{G}/c_sweep.mp4', dur, fr); return dur, [(t0, 'sweep')]

def scene_law():
    t0 = 0.5; dd = D['law']; dur = t0 + dd + 1.0; bg = sblur(0.4, 0.5)
    def fr(t):
        im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = (t - t0) / dd
        ctext(d, (W / 2, 90), 'じつは、本当にあった話', Mi(70), GOLD, sw=3)
        R.winged(d, W / 2, 330, 1500, t, 0, kind='plane', suit=(60, 110, 200))
        if u > 0.12:
            for i, (lab, val) in enumerate([('年', '1979年'), ('翼の幅', '約30m（人力飛行機）'), ('飛んだ距離', '35.7km（イギリス〜フランスの海峡）'), ('かかった時間', '2時間49分'), ('必要なパワー', '約300W')]):
                if u < 0.12 + i * 0.1: continue
                y = 520 + i * 82; d.text((420, y), lab, font=Fb(36), fill=GREY, anchor='lm'); d.text((760, y), val, font=Fo(44), fill=PALE if i < 4 else GOLD, anchor='lm')
        if u > 0.72:
            d.rounded_rectangle((180, 935, W - 180, 1030), 20, fill=(10, 12, 18, 230), outline=GOLD, width=4)
            ctext(d, (W / 2, 982), '筋肉を増やすより、翼を大きく・軽く・ゆっくり', Fo(50), GOLD)
        foot(d, '※人力飛行機「ゴッサマー・アルバトロス」（Wikipedia）。重さは乗る人をふくめて約100kg')
        return im
    run(f'{G}/c_law.mp4', dur, fr); return dur, [(t0, 'law')]

def scene_outro():
    dur = 0.5 + D['outro'] + 1.5; bg = sblur(0.5)
    def fr(t):
        u = (t - 0.5) / D['outro']; im = bg.copy(); d = ImageDraw.Draw(im, 'RGBA')
        if u < 0.45:
            ctext(d, (W / 2, 110), '重い鳥ほど、飛ぶのはたいへん', Mi(72), GOLD, sw=3)
            rowbox(d, 330, '飛べる鳥の重さ', 'いちばん重くて 約19kg', PALE, 260, 1660, lf=40, vf=52)
        elif u < 0.78:
            ctext(d, (W / 2, 330), '鳥のように飛ぶには', Mi(70), PALE, sw=3); ctext(d, (W / 2, 500), '幅30mの翼 ＋ 鍛えた体', Mi(96), GOLD, sw=4)
        else:
            R.winged(d, 1450, 640, 700, t, 0.7)
            ctext(d, (700, 330), '何mの翼なら、ほしい？', Mi(76), PALE, sw=4); ctext(d, (700, 450), 'コメントで教えてください', Mi(56), GOLD, sw=3)
            if u > 0.92:
                d.rounded_rectangle((700 - 500, 580, 700 + 500, 760), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (700, 630), '次に見たい「もしも」は？', Fo(50), PALE); ctext(d, (700, 710), 'リクエスト募集中！', Fo(44), GOLD)
        return im
    run(f'{G}/c_outro.mp4', dur, fr); return dur, [(0.5, 'outro')]

def scene_battle(Bt, title, pre, knots, cues, out, tail=1.6):
    """knots：[(動画の秒(スタート後), シミュレーション秒)]。cues：(シミュレーション秒 or 準備中の秒, key, 'pre'/'s')"""
    kv = np.array([k[0] for k in knots]); ks = np.array([k[1] for k in knots])
    def st_of(vt): return float(np.interp(vt - pre, kv, ks)) if vt >= pre else -1
    def vt_of(st): return pre + float(np.interp(st, ks, kv))
    endall = Bt.endall(); dur = vt_of(endall) + tail; n = int(dur * FPS)
    vc = [(c if k == 'pre' else vt_of(c), key) for c, key, k in cues]
    for (a, k1), (b, k2) in zip(vc, vc[1:]): assert a + D[k1] < b + 0.05, (k1, a + D[k1], k2, b)
    caps = [(vt, vt + D[k] + 0.8, C.CAP[k]) for vt, k in vc if k in C.CAP]; p = writer(out); sts = []
    for f in range(n):
        vt = f / FPS; st = st_of(vt)
        cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None)
        col = RED if cap and any(w in cap for w in ('着地', '下がって', '尽きた')) else (GOLD if cap else PALE)
        im = R.battle_frame(Bt, st, title, cap, col, vt); p.stdin.write(im.tobytes()); sts.append(round(st, 3))
    p.stdin.close(); p.wait()
    json.dump(dict(st=sts, ends=Bt.ends, goal=(Bt.goal / Bt.F[1].v if Bt.goal else None), pre=pre), open(out.replace('.mp4', '_st.json'), 'w')); return dur, vc
def B1(): return R.Battle([(4.0, 6, M.CP), (8, 10, M.CP)], ('ノガン型の翼の人', '幅8mの翼の人'), 800, (150, 300))
def B2(): return R.Battle([(30, 19.7, M.CP), (30, 19.7, 300)], ('ふつうの人', '鍛えた人（長く300W）'), 40000, (420, 420), ('plane', 'plane'), 35700)

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['data'] = scene_data(); res['power'] = scene_power(); res['rule'] = scene_rule(); res['reveal'] = scene_reveal(); res['sweep'] = scene_sweep()
        res['law'] = scene_law(); res['outro'] = scene_outro()
        b = B1()
        res['res1'] = scene_card('res1', 'RESULT  1回戦', [('幅8mの翼', f'約{b.ends[1]:.0f}秒・約{b.F[1].a[-1, 2]:.0f}m', GOLD), ('幅4mの翼（ノガン型）', f'約{b.ends[0]:.0f}秒・約{b.F[0].a[-1, 2]:.0f}m', PALE), ('飛び続けられたのは', 'どちらも0秒', RED)], f'{G}/c_res1.mp4', big='幅8mの翼の勝ち')
        b = B2()
        res['res2'] = scene_card('res2', 'RESULT  決勝戦', [('鍛えた人', f'35.7kmを 約{int(35700 / b.F[1].v // 3600)}時間{int(35700 / b.F[1].v % 3600 // 60)}分', GOLD), ('ふつうの人', f'約{b.ends[0] / 60:.0f}分・約{b.F[0].a[-1, 2] / 1000:.0f}km', PALE), ('必要なパワー', f'約{b.F[0].preq:.0f}W', GREEN)], f'{G}/c_res2.mp4', big='優勝は鍛えた人')
    elif which == 'r1':
        pre = D['r1a'] + 0.4
        res['r1'] = scene_battle(B1(), '1回戦　幅4mの翼（ノガン型） vs 幅8mの翼', pre, [(0, 0), (22, 22), (29, 62)], [(0.2, 'r1a', 'pre'), (1.0, 'r1b', 's'), (6.0, 'r1c', 's'), (16.35, 'r1d', 's'), (20.85, 'r1e', 's'), (61.5, 'r1f', 's')], f'{G}/c_r1.mp4')
    elif which == 'r2':
        pre = D['r2a'] + 0.4
        res['r2'] = scene_battle(B2(), '決勝戦　幅30mの翼（足でこいでプロペラ）', pre, [(0, 0), (3, 30), (7.5, 281), (13, 1320), (16, 2400), (21, 6736)], [(0.2, 'r2a', 'pre'), (10, 'r2b', 's'), (281, 'r2c', 's'), (1320, 'r2d', 's'), (2400, 'r2e', 's'), (6736, 'r2f', 's')], f'{G}/c_r2.mp4')
    json.dump(res, open(f'{G}/scene_{which}.json', 'w')); print('done', which)
