"""縦型ショート：世界記録の選手が全員で100m競争したら（最初の1秒＝問いの文字：E1-A）"""
import json, math, sys
sys.path.insert(0, '/home/claude/air')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, wscn as S, wcont as C
from arnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, GREEN, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/wrr'; D = json.load(open(f'{G}/dur.json'))
def fr_(k, p): return C.NAR[k].index(p) / len(C.NAR[k])
LANES = [S.BIKE, S.HRS, S.SKATE, S.RUN, S.SWIM]
T1 = 0.15 + D['vhook'] + 0.3; T2 = T1 + D['v1'] + 1.0; T3 = T2 + D['v2'] + 1.0; END0 = T3 + D['v3'] + 1.0
STEPS = [(T1, 'v1', 4, '最下位'), (T2, 'v2', 3, '4位'), (T3, 'v3', 2, '3位')]
CTA = END0 + 0.4; ENDC = CTA + D['vcta'] + 1.0; dur = ENDC + 2.5; n = int(dur * FPS)
CUES = [(0.15, 'vhook')] + [(s[0], s[1]) for s in STEPS] + [(CTA, 'vcta')]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
BG = S.stadium_bg(W, H)
LX0, LX1 = 270, 900
def lanes_img(vt, pos, shown, hide_top=True, hl=None):
    """pos[i]：0〜100m。shown：結果を出す選手。hide_top：上の2人を？にする"""
    im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA'); y0 = 840; lh = 166
    d.line((LX1, y0 - 20, LX1, y0 + lh * 5 + 10), fill=PALE, width=6); d.line((LX0, y0 - 20, LX0, y0 + lh * 5 + 10), fill=GREY, width=3)
    d.text((LX0, y0 - 30), 'スタート', font=Fb(28), fill=GREY, anchor='ms'); d.text((LX1, y0 - 30), '100m', font=Fb(28), fill=PALE, anchor='ms')
    for i, sp in enumerate(LANES):
        y = y0 + lh * (i + 0.5); d.rounded_rectangle((40, y - lh / 2 + 10, W - 40, y + lh / 2 - 10), 16, fill=(255, 255, 255, 16), outline=GOLD if hl == i else None, width=4 if hl == i else 0)
        x = LX0 + (LX1 - LX0) * pos[i] / 100
        if hide_top and i < 2:
            d.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(12, 16, 28), outline=(150, 150, 165), width=6); ctext(d, (x, y + 2), '？', Fo(52), PALE)
            continue
        if pos[i] > 0: d.rounded_rectangle((max(LX0, x - 220), y - 10, x, y + 10), 10, fill=sp[2] + (150,))
        S.badge(d, x, y + S.bob(vt, i), 46, sp); d.text((60, y), sp[0], font=Fo(34), fill=sp[2], anchor='lm')
        if i in shown: d.text((W - 50, y - 56), f'{100 / sp[1]:.2f}秒', font=Fo(36), fill=PALE, anchor='rm')
    return im
def frame(vt):
    if vt < T1:
        if vt < 0.3:   # 結果のチラ見せ：ゴール直前のレース
            im = lanes_img(vt, [97, 85, 64, 45, 9], set(), hide_top=True); im = ImageEnhance.Brightness(im).enhance(1.15); d = ImageDraw.Draw(im, 'RGBA')
            ctext(d, (540, 450), '1位は…', Mi(140), GOLD, sw=8)
        else:
            im = lanes_img(vt, [0] * 5, set(), hide_top=False); d = ImageDraw.Draw(im, 'RGBA'); u = ease((vt - 0.3) / 0.25)
            ctext(d, (540, 170), '世界記録の選手が', Mi(int(84 * (1.2 - 0.2 * u))), PALE, sw=6)
            ctext(d, (540, 320), '全員で100m競争', Mi(int(96 * (1.2 - 0.2 * u))), PALE, sw=7)
            ctext(d, (540, 520), '1位は？', Mi(int(170 * (1.25 - 0.25 * u))), GOLD, sw=9)
            if vt > 1.0: ctext(d, (540, 1780), '実データでシミュレーション', Fo(48), PALE, sw=4)
            ev = ['自転車 助走つき200m', '競走馬 最高速度', 'スケート 500m', '陸上 100m', '水泳 100m自由形']
            for j in range(5):
                tj = 1.1 + j * 0.65
                if vt > tj:
                    uu = ease((vt - tj) / 0.25); y = 840 + 166 * (j + 0.5); x1 = W - 50
                    d.rounded_rectangle((x1 - 400 * uu, y - 34, x1, y + 34), 14, fill=(4, 8, 16, 235), outline=LANES[j][2], width=3)
                    if uu > 0.9: d.text((x1 - 20, y), ev[j], font=Fo(32), fill=PALE, anchor='rm')
    else:
        st = max(s for s in STEPS if s[0] <= vt); t0, key, lane, rk = st; k = STEPS.index(st); q = vt - t0
        done = {s[2] for s in STEPS[:k]}; sp = LANES[lane]; T = 100 / sp[1]; run = min(1.0, q / 1.6); simt = T * run
        pos = [100 if i in done else 0 for i in range(5)]; pos[lane] = 100 * run
        im = lanes_img(vt, pos, done | ({lane} if run >= 1 else set()), hl=lane); d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle((0, 0, W, 150), fill=(2, 6, 14, 235)); ctext(d, (540, 75), '世界記録の選手が 全員で100m競争', Fo(46), GOLD)
        u = ease(q / 0.3); ctext(d, (540, 270), sp[0], Mi(int(120 * (1.2 - 0.2 * u))), sp[2], sw=6); ctext(d, (540, 380), sp[4], Fo(40), PALE, sw=3)
        d.rounded_rectangle((540 - 230, 470, 540 + 230, 600), 24, fill=(4, 8, 16, 235), outline=sp[2], width=5)
        d.text((540 + 60, 560), f'{simt:.2f}', font=BE(110), fill=PALE, anchor='rs'); d.text((540 + 80, 556), '秒', font=Fo(48), fill=PALE, anchor='ls')
        if run >= 1:
            uu = ease((q - 1.6) / 0.2); ctext(d, (540, 632), rk, Mi(int(72 * (1.3 - 0.3 * uu))), RED if rk == '最下位' else GOLD, sw=5)
        if q < 1.6 and q > 0.1: ctext(d, (840, 535), '早送り' if lane == 4 else '', Fo(30), GOLD)
        fact = ['陸上の 約5倍の時間がかかる', '時速 約38km　人間の足で最速', '時速 約54km　陸上の約1.4倍'][k]
        if q > 2.3:
            uu = ease((q - 2.3) / 0.3); d.rounded_rectangle((540 - 430 * uu, 712, 540 + 430 * uu, 776), 18, fill=(4, 8, 16, 240), outline=sp[2], width=3)
            if uu > 0.9: ctext(d, (540, 744), fact, Fo(38), PALE)
        if q > 3.0:
            p = 0.5 + 0.5 * math.sin((q - 3.0) * 8); y = 840 + 166 * 1.0
            d.rounded_rectangle((W - 330, y - 40, W - 40, y + 40), 18, fill=(60, 50, 10, int(160 + 80 * p)), outline=GOLD, width=3); ctext(d, (W - 185, y), '残り2人は？', Fo(36), GOLD)
    d = ImageDraw.Draw(im, 'RGBA'); d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    return im
TH = None
def endcard(q, vt):
    global TH
    im = S.stadium_bg(W, H).copy(); d = ImageDraw.Draw(im, 'RGBA')
    if vt < ENDC:
        for i, sp in enumerate(LANES[:2]):
            x = 540 + (i * 2 - 1) * 230; y = 610 + 12 * math.sin(q * 3 + i)
            d.ellipse((x - 120, y - 120, x + 120, y + 120), fill=(12, 16, 28), outline=(150, 150, 165), width=8); ctext(d, (x, y + 4), '？', Mi(130), PALE)
        u = ease(q / 0.4); ctext(d, (540, 170), 'じゃあ', Mi(80), PALE, sw=5); ctext(d, (540, 320), '1位は？', Mi(int(150 * (1.3 - 0.3 * u))), GOLD, sw=8)
        for i, o in enumerate(['自転車？', '競走馬？']):
            if q > 0.8 + i * 0.5:
                y = 800 + i * 160; d.rounded_rectangle((W / 2 - 280, y - 60, W / 2 + 280, y + 60), 20, fill=(4, 8, 16, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(60), PALE)
        if q > 2.0:
            k = int((q - 2.0) / 0.5) % 2; y = 800 + k * 160; d.rounded_rectangle((W / 2 - 292, y - 72, W / 2 + 292, y + 72), 24, outline=(255, 240, 160), width=6)
        if q > 3.0:
            by = 1660 + 18 * abs(math.sin(q * 4)); d.polygon([(W / 2 - 40, by), (W / 2 + 40, by), (W / 2, by + 50)], fill=GOLD)
            d.rounded_rectangle((90, 1400, W - 90, 1580), 24, fill=(4, 8, 16, 225), outline=GOLD, width=5)
            ctext(d, (W / 2, 1460), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1530), '画面の下の関連動画で ↓', Fo(56), GOLD)
    else:   # 最後の約2秒：本編のサムネを小さく
        if TH is None: TH = Image.open(f'{G}/wrr_thumb.jpg').resize((680, 383), Image.LANCZOS)
        qq = vt - ENDC; u = ease(qq / 0.35)
        ctext(d, (540, 420), 'じゃあ 1位は？', Mi(100), GOLD, sw=6)
        d.rounded_rectangle((540 - 352, 1000 - 203, 540 + 352, 1000 + 203), 18, fill=GOLD); im.paste(TH, (200, int(1000 - 192 + 40 * (1 - u))))
        d = ImageDraw.Draw(im, 'RGBA'); ctext(d, (540, 1300), '↓ 続きは本編で', Mi(84), PALE, sw=5)
        by = 1430 + 18 * abs(math.sin(qq * 5)); d.polygon([(W / 2 - 44, by), (W / 2 + 44, by), (W / 2, by + 56)], fill=GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im
def get(vt): return frame(vt) if vt < END0 else endcard(vt - END0, vt)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        for vt in map(float, sys.argv[1:]): get(vt).resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n): p.stdin.write(get(f / FPS).tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, end0=END0, cta=CTA, endc=ENDC, steps=[s[0] for s in STEPS]), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
