"""縦型ショート：マリアナ海溝の底に落ちたら（最初の1秒＝問いの文字：E1-A）"""
import json, math, sys
sys.path.insert(0, '/home/claude/air')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, mscn as S, mcont as C
from arnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, GREEN, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/mrt'; D = json.load(open(f'{G}/dur.json')); AQUA = S.AQUA
def fr_(k, p): return C.NAR[k].index(p) / len(C.NAR[k])
T1 = 3.6; T2 = T1 + D['v1'] + 0.3; T3 = T2 + D['v2'] + 0.3; END0 = T3 + D['v3'] + 0.4
STEPS = [(T1, 'v1', 'うわさ1', '底まで 一瞬', 'ウソ', GREEN, '答えは'), (T2, 'v2', 'うわさ2', '水圧で ぺちゃんこ', 'ウソ', GREEN, 'これも'), (T3, 'v3', 'うわさ3', '底は 真っ暗', '本当', RED, 'これは')]
dur = END0 + 0.4 + D['vcta'] + 2.4; n = int(dur * FPS)
CUES = [(0.15, 'vhook')] + [(s[0], s[1]) for s in STEPS] + [(END0 + 0.4, 'vcta')]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
PH = None
def photo_v(t):
    global PH
    if PH is None:
        p = Image.open(f'{G}/dl/PIA11019.jpg').convert('RGB'); s = H / p.height * 1.1; PH = ImageEnhance.Brightness(p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)).enhance(1.05)
    x = int((PH.width - W) * (0.25 + 0.02 * t)); y = int((PH.height - H) * 0.5); return PH.crop((x, y, x + W, y + H))
def frame(vt):
    if vt < STEPS[0][0]:
        if vt < 0.3:   # 結果のチラ見せ：底の水圧メーター
            im = ImageEnhance.Brightness(photo_v(0)).enhance(0.7).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); S.gauge(d, 540, 900, 330, 1070)
            ctext(d, (540, 1380), '約1,070気圧', Mi(120), RED, sw=6)
        else:
            im = photo_v(vt).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, 720), fill=(0, 0, 0, 120))
            S.figure(im, 540, 1150 + vt * 40, 300, 10 * math.sin(vt * 0.8)); d = ImageDraw.Draw(im, 'RGBA')
            u = ease((vt - 0.3) / 0.25)
            ctext(d, (540, 190), 'マリアナ海溝の', Mi(int(96 * (1.2 - 0.2 * u))), PALE, sw=6)
            ctext(d, (540, 340), '底に落ちたら', Mi(int(110 * (1.2 - 0.2 * u))), AQUA, sw=7)
            ctext(d, (540, 520), 'どうなる？', Mi(int(150 * (1.25 - 0.25 * u))), GOLD, sw=9)
            if vt > 1.0: ctext(d, (540, 1660), '実データでシミュレーション', Fo(48), PALE, sw=4)
            d.text((W - 16, H - 60), '写真：NASA（PIA11019）', font=Fb(22), fill=(225, 225, 230), anchor='rs')
    else:
        st = max(s for s in STEPS if s[0] <= vt); t0, key, no, lab, ans, col, ph = st; i = STEPS.index(st); q = vt - t0; u = ease(q / 0.35)
        cx, cy = 540, 1080
        if i == 0:
            depth = min(1, q / (D['v1'] - 0.3)) * BOT; im = S.sea_bg(depth * 0.25, W, H).copy().convert('RGBA'); dd = ImageDraw.Draw(im, 'RGBA'); S.snow(dd, vt, 3, W, H)
            S.figure(im, 400, cy, 300, 6 * math.sin(vt)); dd = ImageDraw.Draw(im, 'RGBA'); S.depth_bar(dd, 860, 760, 1420, depth)
            hrs = depth / 0.5 / 3600; ctext(dd, (540, 1520), f'水深 {depth:,.0f}m', Fo(60), PALE, sw=4)
            dd.rounded_rectangle((300, 1580, 780, 1660), 18, fill=(4, 10, 22, 235), outline=AQUA, width=3); ctext(dd, (540, 1620), f'経過 約{hrs:.1f}時間（早送り）', Fo(40), PALE)
        elif i == 1:
            depth = min(1, q / (D['v2'] * 0.5)) * BOT; P = S.atm(depth); bag = 1 / P
            im = S.sea_bg(depth, W, H).copy().convert('RGBA'); dd = ImageDraw.Draw(im, 'RGBA'); S.snow(dd, vt, 1, W, H)
            S.figure(im, 300, cy, 300, 0, bag=bag); dd = ImageDraw.Draw(im, 'RGBA')
            r = 190 * bag ** (1 / 3); dd.ellipse((780 - 190, 960 - 190, 780 + 190, 960 + 190), outline=(90, 100, 120), width=3)
            dd.ellipse((780 - r, 960 - r, 780 + r, 960 + r), fill=(170, 230, 255, 230), outline=PALE, width=3); ctext(dd, (780, 720), '肺の空気', Fo(44), PALE)
            ml = 6000 * bag; ctext(dd, (780, 1200), f'{ml / 1000:.1f}L' if ml >= 1000 else f'{ml:,.0f}mL', Fo(64), AQUA, sw=3)
            ctext(dd, (540, 1360), f'水圧 {P:,.0f}気圧', Fo(56), PALE, sw=3)
            if q > D['v2'] * fr_('v2', '体の水'): dd.rounded_rectangle((90, 1440, 990, 1530), 20, fill=(4, 8, 16, 230), outline=GREEN, width=3); ctext(dd, (540, 1485), '体の水は ほとんど縮まない（約5%）', Fo(40), GREEN)
            if q > D['v2'] * fr_('v2', 'でも'): ctext(dd, (540, 1600), '空気は 1,000分の1', Mi(76), RED, sw=4)
        else:
            depth = 100 + min(1, q / (D['v3'] * 0.7)) * 1000; im = S.sea_bg(depth, W, H).copy().convert('RGBA'); dd = ImageDraw.Draw(im, 'RGBA'); S.snow(dd, vt, 1.5, W, H)
            S.figure(im, 540, cy, 280, 8 * math.sin(vt), col=(80, 130, 170)); dd = ImageDraw.Draw(im, 'RGBA')
            L = S.light(depth); dd.text((140, 1440), '光', font=Fo(48), fill=PALE, anchor='lm'); dd.rectangle((240, 1410, 940, 1470), outline=GREY, width=3)
            dd.rectangle((246, 1416, 246 + 688 * L, 1464), fill=GOLD)
            ctext(dd, (540, 1560), f'水深 {depth:,.0f}m', Fo(60), PALE, sw=4)
            if depth > 990: ctext(dd, (540, 1660), '光は ほぼゼロ', Mi(76), RED, sw=4)
        d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, 170), fill=(2, 6, 14, 235)); ctext(d, (540, 85), 'マリアナ海溝の底に 落ちたら', Fo(52), GOLD)
        ctext(d, (540, 270), no, Fo(58), AQUA, sw=4); ctext(d, (540, 400), lab, Mi(int(104 * (1.2 - 0.2 * u))), PALE, sw=6)
        tv = t0 + D[key] * fr_(key, ph)
        if vt >= tv:
            uu = ease((vt - tv) / 0.2); s = int(150 * (1.4 - 0.4 * uu))
            d.rounded_rectangle((540 - 200, 560 - 95, 540 + 200, 560 + 95), 28, fill=(4, 8, 16, 230), outline=col, width=8); ctext(d, (540, 560), ans, Mi(s), col, sw=4)
        for k, s_ in enumerate(STEPS):
            c = GOLD if k == i else (90, 95, 110); d.ellipse((450 + k * 90 - 14, 1760 - 14, 450 + k * 90 + 14, 1760 + 14), fill=c)
    d = ImageDraw.Draw(im, 'RGBA'); d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    return im.convert('RGB')
BOT = S.BOTTOM
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(S.sea_bg(BOT, W, H).filter(ImageFilter.GaussianBlur(4))).enhance(1.0)
    im = END_BG.copy().convert('RGBA'); dd = ImageDraw.Draw(im, 'RGBA'); S.snow(dd, q, 0.4, W, H, a=0.6)
    l = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(l).ellipse((140, 140, 940, 560), fill=(200, 225, 255, 40)); im.alpha_composite(l.filter(ImageFilter.GaussianBlur(50)))
    S.figure(im, 540, 340, 170, 70 + 5 * math.sin(q), col=(80, 130, 170), lamp=True); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 600), '真っ暗な底に', Mi(int(90 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 740), '生き物はいる？', Mi(120), GOLD, sw=6)
    for i, o in enumerate(['いる', 'いない']):
        if q > 0.8 + i * 0.4:
            y = 940 + i * 160; d.rounded_rectangle((W / 2 - 280, y - 60, W / 2 + 280, y + 60), 20, fill=(4, 8, 16, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(60), PALE)
    if q > 1.6:
        k = int((q - 1.6) / 0.6) % 2; y = 940 + k * 160; d.rounded_rectangle((W / 2 - 292, y - 72, W / 2 + 292, y + 72), 24, outline=(255, 240, 160), width=6)
    if q > 3.5: ctext(d, (W / 2, 1290), 'コメントで 予想してね', Fo(46), PALE, sw=3)
    if q > 2.2:
        by = 1660 + 18 * abs(math.sin(q * 4)); d.polygon([(W / 2 - 40, by), (W / 2 + 40, by), (W / 2, by + 50)], fill=GOLD)
        d.rounded_rectangle((90, 1400, W - 90, 1580), 24, fill=(4, 8, 16, 225), outline=GOLD, width=5)
        ctext(d, (W / 2, 1460), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1530), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im.convert('RGB')
if __name__ == '__main__':
    if len(sys.argv) > 1:
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        for vt in map(float, sys.argv[1:]): (frame(vt) if vt < END0 else endcard(vt - END0)).resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n):
        vt = f / FPS; im = frame(vt) if vt < END0 else endcard(vt - END0); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, end0=END0, steps=[s[0] for s in STEPS]), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
