"""縦型ショート：流す人数をふやすと（最初の1秒＝いちばん衝撃的な数字：E1-B）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import trender as R
from trender import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, ORANGE, WATER, WATER2, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/tlt'; D = json.load(open(f'{G}/dur.json'))
STEPS = [(6.8, 'v1', '1人なら', '8L', 'バケツ1杯くらい'), (10.4, 'v2', '東京23区（約950万人）なら', '7.6万トン', '25mプール 約200杯'), (15.6, 'v3', '日本中（約1億2,400万人）なら', '100万トン', '東京ドーム 約0.8杯')]
END0 = 22.8; dur = END0 + 0.4 + D['vcta'] + 3.2; n = int(dur * FPS)
CUES = [(0.15, 'vhook')] + [(s[0], s[1]) for s in STEPS] + [(END0 + 0.4, 'vcta')]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
BG = R.night_bg(W, H, 7)
def bucket(d, cx, yb, s, lev):
    pts = [(cx - s * 0.5, yb - s), (cx + s * 0.5, yb - s), (cx + s * 0.38, yb), (cx - s * 0.38, yb)]
    if lev > 0:
        yl = yb - s * lev; k = (yb - yl) / s; hw = s * (0.38 + 0.12 * k)
        d.polygon([(cx - hw, yl), (cx + hw, yl), (cx + s * 0.38, yb), (cx - s * 0.38, yb)], fill=WATER)
    d.line(pts + [pts[0]], fill=PALE, width=8); d.arc((cx - s * 0.5, yb - s * 1.45, cx + s * 0.5, yb - s * 0.55), 200, 340, fill=PALE, width=6)
def pools(d, cx, cy, u):
    k = int(200 * u); cols = 10
    for i in range(k):
        x = cx - 5 * 84 + (i % cols) * 84; y = cy - 10 * 26 + (i // cols) * 26
        d.rectangle((x, y, x + 72, y + 18), fill=WATER, outline=WATER2)
def frame(vt):
    im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
    if vt < STEPS[0][0]:
        u = ease(vt / 0.25); im = R.glow(im.convert('RGBA'), 540, 1300, 300, (60, 140, 255)).convert('RGB'); d = ImageDraw.Draw(im, 'RGBA')
        ctext(d, (540, 660), '100万トン', Mi(int(180 * (1.15 - 0.15 * u))), GOLD, sw=8)
        if vt > 0.5: ctext(d, (540, 300), '日本中で 同時に', Mi(84), PALE, sw=5); ctext(d, (540, 410), 'トイレを流すと…', Mi(84), PALE, sw=5)
        R.toilet(d, 560, 1560, 520, (240, 244, 250), (24, 32, 52)); R.swirl(d, 482, 1300, 110, vt)
    else:
        st = max(s for s in STEPS if s[0] <= vt); t0, key, lab, val, cmp = st; i = STEPS.index(st); u = ease((vt - t0) / 0.35)
        d.rectangle((0, 0, W, 170), fill=(6, 9, 16, 235)); ctext(d, (540, 85), '流す人数をふやすと…', Fo(56), GOLD)
        ctext(d, (540, 290), lab, Fo(58), PALE, sw=4)
        ctext(d, (540, 470), val, Mi(int(170 * (1.25 - 0.25 * u))), GOLD, sw=7)
        if i == 0: bucket(d, 540, 1300, 380, 0.8 * ease((vt - t0 - 0.3) / 1.2))
        elif i == 1: pools(d, 540, 1100, fade((vt - t0 - 0.2) / 2.5)); d.text((540 - 5 * 84, 1400), '■＝25mプール1杯（約375トン）', font=Fb(30), fill=GREY, anchor='lm')
        else: R.dome(d, 540, 1350, 860, 460, 0.61 * ease((vt - t0 - 0.4) / 2.0)); ctext(d, (540, 820), '東京ドーム（約124万トン）', Fo(40), PALE, sw=3)
        ctext(d, (540, 1520), cmp, Fo(64), WATER2, sw=4)
        for k, s in enumerate(STEPS):
            col = GOLD if k == i else (90, 95, 110); d.ellipse((450 + k * 90 - 14, 1680 - 14, 450 + k * 90 + 14, 1680 + 14), fill=col)
    d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    return im
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05).filter(ImageFilter.GaussianBlur(14))).enhance(0.35)
    im = END_BG.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 430), '100万トンで', Mi(int(100 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 580), '下水道は あふれる？', Mi(96), GOLD, sw=6)
    for i, o in enumerate(['びくともしない', 'マンホールから ふき出す', '町が 水びたし']):
        if q > 0.8 + i * 0.4:
            y = 800 + i * 150; d.rounded_rectangle((W / 2 - 360, y - 55, W / 2 + 360, y + 55), 20, fill=(10, 12, 18, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(52), PALE)
    if q > 2.4:
        d.rounded_rectangle((90, 1400, W - 90, 1580), 24, fill=(10, 12, 18, 225), outline=GOLD, width=5)
        ctext(d, (W / 2, 1460), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1530), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im
if __name__ == '__main__':
    if len(sys.argv) > 1:
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        for vt in map(float, sys.argv[1:]): (frame(vt) if vt < END0 else endcard(vt - END0)).resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n):
        vt = f / FPS; im = frame(vt) if vt < END0 else endcard(vt - END0); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, end0=END0, steps=[s[0] for s in STEPS]), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
