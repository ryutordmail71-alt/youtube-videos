"""縦型ショート：宇宙に生身で（最初の1秒＝衝撃の数字：E1-B）"""
import json, math, sys
sys.path.insert(0, '/home/claude/air')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, sscn as S, scont as C
from arnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, GREEN, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/spc'; D = json.load(open(f'{G}/dur.json')); ICE = S.ICE
def fr_(k, p): return C.NAR[k].index(p) / len(C.NAR[k])
T1 = 4.2; T2 = T1 + D['v1'] + 0.3; T3 = T2 + D['v2'] + 0.3; END0 = T3 + D['v3'] + 0.4
STEPS = [(T1, 'v1', 'うわさ1', '体が 破裂する', 'ウソ', GREEN, '答えは'), (T2, 'v2', 'うわさ2', '一瞬で 凍る', 'ウソ', GREEN, 'これも'), (T3, 'v3', 'うわさ3', '息が もたない', '本当', RED, 'これは')]
dur = END0 + 0.4 + D['vcta'] + 2.6; n = int(dur * FPS)
CUES = [(0.15, 'vhook')] + [(s[0], s[1]) for s in STEPS] + [(END0 + 0.4, 'vcta')]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
BG = S.space_bg(W, H)
PH = None
def photo_v(t):
    global PH
    if PH is None:
        p = Image.open(f'{G}/dl/iss044e045215.jpg').convert('RGB'); s = H / p.height * 1.05; PH = ImageEnhance.Brightness(p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)).enhance(1.0)
    x = int((PH.width - W) * (0.45 + 0.03 * t)); return PH.crop((x, 0, x + W, H))
def frame(vt):
    if vt < STEPS[0][0]:
        if vt < 0.3:   # 結果のチラ見せ：暗くなる視界とタイマー
            im = photo_v(0).convert('RGBA'); S.figure(im, 540, 1000, 330, 30)
            a = Image.new('RGBA', (W, H), (40, 0, 0, 90)); im.alpha_composite(a); d = ImageDraw.Draw(im, 'RGBA'); ctext(d, (500, 1000), '15.0', BE(300), RED, sw=8); ctext(d, (830, 1040), '秒', Fo(110), RED, sw=6)
        else:
            im = photo_v(vt).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, 760), fill=(0, 0, 0, 120))
            S.figure(im, 540, 1250, 300, -15 + vt * 6); d = ImageDraw.Draw(im, 'RGBA')
            u = ease((vt - 0.3) / 0.25)
            ctext(d, (540, 170), '宇宙に放り出されたら', Mi(84), PALE, sw=6)
            ctext(d, (540, 300), '意識がもつのは', Mi(70), PALE, sw=5)
            ctext(d, (540, 520), '15秒', Mi(int(260 * (1.25 - 0.25 * u))), GOLD, sw=10)
            if vt > 1.2: ctext(d, (540, 1660), '実データでシミュレーション', Fo(48), PALE, sw=4)
            d.text((W - 16, H - 60), '写真：NASA（iss044e045215）', font=Fb(22), fill=(210, 210, 215), anchor='rs')
    else:
        im = BG.copy().convert('RGBA'); st = max(s for s in STEPS if s[0] <= vt); t0, key, no, lab, ans, col, ph = st; i = STEPS.index(st); q = vt - t0; u = ease(q / 0.35)
        cx, cy = 540, 1050
        if i == 0:
            sw = 1 + 0.2 * ease((q - 1.0) / 3); dd = ImageDraw.Draw(im, 'RGBA'); S.bubbles(dd, cx, cy, 320, vt); S.figure(im, cx, cy, 380, q * 8, sw)
        elif i == 1:
            S.figure(im, 380, cy, 320, q * 6); dd = ImageDraw.Draw(im, 'RGBA'); ss = min(60, q / (D['v2'] - 0.3) * 60); temp = 37 - 0.22 * ss / 60
            S.thermo(dd, 800, 1380, 480, temp, 30, 40); ctext(dd, (740, 770), f'{temp:.2f}℃', Fo(80), ICE if temp < 36.95 else PALE, sw=4)
            for k in range(10):
                a = k * math.pi / 5 + 0.2; uu = (vt * 0.6 + k * 0.17) % 1; r0 = 200 + 260 * uu
                pts = [(380 + (r0 + j * 7) * math.cos(a) - 12 * math.sin(j * 0.9) * math.sin(a), cy + (r0 + j * 7) * math.sin(a) + 12 * math.sin(j * 0.9) * math.cos(a)) for j in range(14)]
                dd.line(pts, fill=(255, 140, 90, int(220 * (1 - uu))), width=6)
            if q > D['v2'] * fr_('v2', '一分で'): ctext(dd, (540, 1500), '1分で 約0.2℃だけ', Mi(70), GOLD, sw=4)
            elif q > 0.6: ctext(dd, (540, 1500), f'{ss:.0f}秒たっても…', Fo(52), PALE, sw=3)
            if q > D['v2'] * fr_('v2', '真空'): dd.rounded_rectangle((90, 1560, 990, 1650), 20, fill=(4, 8, 16, 230), outline=ICE, width=3); ctext(dd, (540, 1605), '真空 ＝ 魔法瓶と同じ（熱が逃げにくい）', Fo(40), ICE)
        else:
            dd = ImageDraw.Draw(im, 'RGBA'); S.lungs(dd, 540, 1080, 300)
            for k in range(7):
                uu = (vt * 0.8 + k / 7) % 1; x = 540 + (k - 3) * 60; y = 860 - 300 * uu; dd.ellipse((x - 18, y - 18, x + 18, y + 18), outline=ICE + (int(255 * (1 - uu)),), width=4)
            if q > D['v3'] * fr_('v3', '息を止める'): ctext(dd, (540, 1480), '息を止めると 肺が傷つく', Fo(54), RED, sw=3)
            dd.rounded_rectangle((330, 1550, 750, 1640), 18, fill=(4, 10, 22, 235), outline=ICE, width=3); ctext(dd, (540, 1595), f'経過 {q:4.1f}秒', Fo(48), PALE)
        d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, 170), fill=(2, 6, 14, 235)); ctext(d, (540, 85), '宇宙に生身で 放り出されたら', Fo(52), GOLD)
        ctext(d, (540, 270), no, Fo(58), ICE, sw=4); ctext(d, (540, 400), lab, Mi(int(110 * (1.2 - 0.2 * u))), PALE, sw=6)
        tv = t0 + D[key] * fr_(key, ph)
        if vt >= tv:
            uu = ease((vt - tv) / 0.2); s = int(150 * (1.4 - 0.4 * uu))
            d.rounded_rectangle((540 - 200, 560 - 95, 540 + 200, 560 + 95), 28, fill=(4, 8, 16, 230), outline=col, width=8); ctext(d, (540, 560), ans, Mi(s), col, sw=4)
        for k, s_ in enumerate(STEPS):
            c = GOLD if k == i else (90, 95, 110); d.ellipse((450 + k * 90 - 14, 1700 - 14, 450 + k * 90 + 14, 1700 + 14), fill=c)
    d = ImageDraw.Draw(im, 'RGBA'); d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    return im.convert('RGB')
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05).filter(ImageFilter.GaussianBlur(14))).enhance(0.35)
    im = END_BG.copy().convert('RGBA'); S.figure(im, 540, 330, 200, q * 10); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 580), '何秒以内に戻れば', Mi(int(90 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 720), '助かる？', Mi(130), GOLD, sw=6)
    for i, o in enumerate(['15秒', '90秒', '5分']):
        if q > 0.8 + i * 0.4:
            y = 920 + i * 150; d.rounded_rectangle((W / 2 - 300, y - 55, W / 2 + 300, y + 55), 20, fill=(4, 8, 16, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(56), PALE)
    if q > 1.6:
        k = int((q - 1.6) / 0.6) % 3; y = 920 + k * 150; d.rounded_rectangle((W / 2 - 312, y - 67, W / 2 + 312, y + 67), 24, outline=(255, 240, 160), width=6)
    if q > 4.2: ctext(d, (W / 2, 1320), 'コメントで 予想してね', Fo(46), PALE, sw=3)
    if q > 2.4:
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
