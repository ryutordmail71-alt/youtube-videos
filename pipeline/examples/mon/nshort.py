"""縦型ショート：月が半分の距離に近づいたら（最初の1秒＝衝撃の数字「8倍」：E1-B）"""
import json, math, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/air')
import arnd as R, nscn as S, ncont as C
from arnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, GREEN, CYAN, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/mon'; D = json.load(open(f'{G}/dur.json'))
def fr_(k, p): return C.NAR[k].index(p) / len(C.NAR[k])
T1 = 0.15 + D['vhook'] + 0.35; T2 = T1 + D['v1'] + 0.7; T3 = T2 + D['v2'] + 0.7; END0 = T3 + D['v3'] + 0.8
CTA = END0 + 0.3; ENDC = CTA + D['vcta'] + 0.9; dur = ENDC + 2.2
n = int(dur * FPS)
STEPS = [(T1, 'v1', 'うわさ1', '空が月でいっぱい', 'ウソ', GREEN), (T2, 'v2', 'うわさ2', '潮が8倍', 'ホント', GOLD), (T3, 'v3', 'うわさ3', '月がこわれる', 'ウソ', GREEN)]
CUES = [(0.15, 'vhook')] + [(s[0], s[1]) for s in STEPS] + [(CTA, 'vcta')]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
PH = None
def photo_v(t):
    global PH
    if PH is None:
        p = Image.open(f'{G}/dl/iss072e618284.jpg').convert('RGB'); s = H / p.height * 1.25
        PH = ImageEnhance.Brightness(p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)).enhance(1.05)
    x = int((PH.width - W) * (0.5 + 0.015 * t)); y = int((PH.height - H) * 0.42); return PH.crop((x, y, x + W, y + H))
def sky_v(warm=0.0): return S.sky(W, H, warm)
def frame(vt):
    if vt < T1:
        if vt < 0.3:   # 結果のチラ見せ：8倍の数字
            im = sky_v(0.1).copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
            S.draw_moon(im, 540, 700, 440, glow_a=90); d = ImageDraw.Draw(im, 'RGBA')
            ctext(d, (540, 1250), '潮の満ち引き', Fo(70), PALE, sw=5); ctext(d, (540, 1430), '8倍', Mi(240), GOLD, sw=10)
        else:
            im = photo_v(vt).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, 760), fill=(0, 0, 0, 130))
            u = ease((vt - 0.3) / 0.25)
            ctext(d, (540, 190), '月が今の半分の', Mi(int(92 * (1.2 - 0.2 * u))), PALE, sw=6)
            ctext(d, (540, 330), '距離に近づいたら', Mi(int(104 * (1.2 - 0.2 * u))), CYAN, sw=7)
            ctext(d, (540, 510), 'どうなる？', Mi(int(150 * (1.25 - 0.25 * u))), GOLD, sw=9)
            if vt > 0.9:
                d.rounded_rectangle((150, 1600, 930, 1700), 24, fill=(4, 8, 16, 215), outline=GOLD, width=4)
                ctext(d, (540, 1650), '実データでシミュレーション', Fo(46), PALE)
            d.text((W - 16, H - 60), '写真：NASA（iss072e618284）', font=Fb(22), fill=(225, 225, 230), anchor='rs')
    else:
        st = max(s for s in STEPS if s[0] <= vt); t0, key, no, lab, ans, col = st; i = STEPS.index(st); q = vt - t0; u = ease(q / 0.35)
        if i == 0:
            prog = min(1, q / max(0.8, D['v1'] * 0.95)); dist = S.D0 - (S.D0 / 2) * prog
            im = sky_v().copy().convert('RGBA'); S.draw_moon(im, 540, 780, 150 * (S.D0 / dist) * 1.5, glow_a=70)
            d = ImageDraw.Draw(im, 'RGBA')
            ctext(d, (540, 1210), f'距離 {dist / 10000:,.1f}万km', Fo(60), PALE, sw=4)
            for j, (nm, val) in enumerate((('見かけの幅', f'{S.D0 / dist:.2f}倍'), ('見かけの面積', f'{(S.D0 / dist) ** 2:.2f}倍'))):
                y = 1330 + j * 110; d.rounded_rectangle((110, y - 48, 970, y + 48), 18, fill=(4, 8, 16, 225))
                d.text((150, y), nm, font=Fb(36), fill=GREY, anchor='lm'); d.text((930, y), val, font=Fo(50), fill=GOLD, anchor='rm')
        elif i == 1:
            prog = min(1, q / max(0.8, D['v2'] * 0.92)); dist = S.D0 - (S.D0 / 2) * prog; mult = S.tide(dist)
            im = sky_v(0.12).copy().convert('RGBA'); S.draw_moon(im, 800, 560, 110 * (S.D0 / dist), glow_a=70)
            d = ImageDraw.Draw(im, 'RGBA')
            base = 1330; hh = min(420, 36 * mult)
            wave = [(x, base - hh * (0.55 + 0.45 * math.cos(x / W * math.pi * 2 + vt * 0.9))) for x in range(90, 991, 10)]
            d.polygon([(90, base + 60)] + wave + [(990, base + 60)], fill=(40, 110, 200)); d.line(wave, fill=(150, 215, 255), width=5)
            d.rectangle((90, base + 60, 990, base + 120), fill=(50, 44, 38))
            d.line((90, base, 990, base), fill=(120, 130, 150, 200), width=2)
            ctext(d, (540, 1520), f'距離 {dist / 10000:,.1f}万km', Fo(56), PALE, sw=4)
            d.rounded_rectangle((230, 1590, 850, 1690), 20, fill=(4, 8, 16, 230), outline=GOLD, width=4)
            ctext(d, (540, 1640), f'潮を起こす力 ×{mult:,.1f}', Fo(52), GOLD)
        else:
            prog = min(1, q / max(0.8, D['v3'] * 0.92)); dist = S.D0 / 2 - (S.D0 / 2 - S.ROCHE) * prog
            im = sky_v().copy().convert('RGBA')
            px = min(560, 150 * (S.D0 / dist)); sq = 1.0 if dist > 60000 else 1.0 + 0.3 * (60000 - dist) / 42000
            S.draw_moon(im, 540, 760, px, glow_a=70, squash=sq); d = ImageDraw.Draw(im, 'RGBA')
            ctext(d, (540, 1230), f'距離 {dist / 10000:,.1f}万km', Fo(60), PALE, sw=4)
            d.rounded_rectangle((110, 1310, 970, 1410), 18, fill=(4, 8, 16, 225))
            d.text((150, 1360), 'ロッシュ限界', font=Fb(36), fill=GREY, anchor='lm'); d.text((930, 1360), '約1万8,000km', font=Fo(46), fill=RED, anchor='rm')
            d.rounded_rectangle((110, 1430, 970, 1530), 18, fill=(4, 8, 16, 225))
            d.text((150, 1480), '半分の距離は', font=Fb(36), fill=GREY, anchor='lm'); d.text((930, 1480), 'その10倍以上 外側', font=Fo(44), fill=GREEN, anchor='rm')
        d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, 170), fill=(2, 6, 14, 235)); ctext(d, (540, 85), '月が半分の距離に近づいたら', Fo(50), GOLD)
        ctext(d, (540, 260), no, Fo(56), CYAN, sw=4); ctext(d, (540, 380), lab, Mi(int(100 * (1.2 - 0.2 * u))), PALE, sw=6)
        if q > D[key] * 0.42:
            uu = ease((q - D[key] * 0.42) / 0.2); sz = int(140 * (1.4 - 0.4 * uu))
            d.rounded_rectangle((540 - 230, 1770 - 80, 540 + 230, 1770 + 80), 28, fill=(4, 8, 16, 235), outline=col, width=8)
            ctext(d, (540, 1770), ans, Mi(sz), col, sw=4)
        for k in range(3):
            c = GOLD if k == i else (90, 95, 110); d.ellipse((450 + k * 90 - 13, 1660 - 13, 450 + k * 90 + 13, 1660 + 13), fill=c)
    d = ImageDraw.Draw(im, 'RGBA'); d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    return im.convert('RGB')
TH = None
def endcard(q):
    """最後：答えを伏せた問い＋最後の約2秒は本編サムネを見せる（手法32）"""
    global TH
    im = S.sky(W, H, 0.05).copy().convert('RGBA')
    S.draw_moon(im, 540, 430, 320, glow_a=80); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 760), 'じゃあ ひと月の長さは', Mi(int(84 * (1.3 - 0.3 * u))), PALE, sw=5)
    ctext(d, (W / 2, 890), 'どうなる？', Mi(118), GOLD, sw=6)
    for i, o in enumerate(['長くなる', '短くなる']):
        if q > 0.5 + i * 0.35:
            y = 1040 + i * 150; d.rounded_rectangle((W / 2 - 300, y - 58, W / 2 + 300, y + 58), 20, fill=(4, 8, 16, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(56), PALE)
    if q > 1.3:
        k = int((q - 1.3) / 0.6) % 2; y = 1040 + k * 150
        d.rounded_rectangle((W / 2 - 312, y - 70, W / 2 + 312, y + 70), 24, outline=(255, 240, 160), width=6)
    if ENDC - END0 - 2.0 < q:   # 最後の約2秒：本編のサムネを小さく見せる
        if TH is None: TH = Image.open(f'{G}/mon_thumb.jpg').resize((680, 383), Image.LANCZOS)
        a = ease((q - (ENDC - END0 - 2.0)) / 0.3)
        box = Image.new('RGBA', (700, 403), (255, 210, 80, int(230 * a))); box.alpha_composite(TH.convert('RGBA'), (10, 10))
        im.alpha_composite(box, (190, 1330))
        d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (W / 2, 1300), '↓ 続きは本編で', Fo(52), GOLD, sw=4)
    elif q > 1.0:
        by = 1620 + 16 * abs(math.sin(q * 4)); d.polygon([(W / 2 - 38, by), (W / 2 + 38, by), (W / 2, by + 48)], fill=GOLD)
        d.rounded_rectangle((90, 1380, W - 90, 1560), 24, fill=(4, 8, 16, 225), outline=GOLD, width=5)
        ctext(d, (W / 2, 1440), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1510), '画面の下の関連動画で ↓', Fo(54), GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im.convert('RGB')
def get(vt): return frame(vt) if vt < END0 else endcard(vt - END0)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        os.makedirs(f'{G}/stills', exist_ok=True)
        for vt in map(float, sys.argv[1:]): get(vt).resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n): p.stdin.write(get(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    json.dump(dict(dur=dur, cues=CUES, end0=END0, cta=CTA, endc=ENDC, steps=[s[0] for s in STEPS]), open(f'{G}/s_meta.json', 'w')); print('done short', round(dur, 2))
