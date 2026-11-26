"""縦型ショート：人数をふやしてジャンプ（最初の1秒＝結論を伏せた問いの文字：E1-A）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import hrender as R, jscenes as S
from hrender import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, ORANGE, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/jmp'; D = json.load(open(f'{G}/dur.json'))
STEPS = [(5.0, 'v1', 1, 1, 330, '1人', '−1.8', 0.12), (9.8, 'v2', 36, 3, 230, '7万人（スタジアム）', '1.5', 1.6), (16.4, 'v3', 96, 6, 160, '1.2億人（日本）', '3.6', 5.5)]
END0 = 20.6; dur = END0 + 0.4 + D['vcta'] + 3.2; n = int(dur * FPS)
CUES = [(0.15, 'vhook')] + [(s[0], s[1]) for s in STEPS] + [(END0 + 0.4, 'vcta')]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
JUMP = 0.6; SL = 2.0
def land_t(st): return st + JUMP + S.AIR * SL
BG = R.space_bg(W, H, 7)
def mscale(d, y, m, show):
    x0, x1 = 90, 990; X = lambda v: x0 + (x1 - x0) * (v + 2) / 11
    d.rounded_rectangle((50, y - 70, 1030, y + 110), 20, fill=(10, 12, 18, 225))
    d.line((x0, y + 20, x1, y + 20), fill=GREY, width=4)
    for v in range(-2, 10):
        d.line((X(v), y + 8, X(v), y + 32), fill=GREY, width=3); d.text((X(v), y + 46), str(v) if v >= 0 else f'−{-v}', font=Fb(28), fill=GREY, anchor='mt')
    d.text((x1, y - 40), 'マグニチュード相当', font=Fb(30), fill=PALE, anchor='rm')
    if show: xx = X(m); d.polygon([(xx, y + 14), (xx - 20, y - 24), (xx + 20, y - 24)], fill=GOLD)
def frame(vt):
    im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
    if vt < STEPS[0][0]:
        u = ease(vt / 0.25); S.draw_globe(im, 540, 1250, 400); d = ImageDraw.Draw(im, 'RGBA'); S.ring_people(d, 540, 1250, 400, vt, 22, 44)
        ctext(d, (540, 300), '82億人が同時に', Mi(int(96 * (1.12 - 0.12 * u))), PALE, sw=6)
        ctext(d, (540, 440), 'ジャンプしたら？', Mi(int(110 * (1.12 - 0.12 * u))), GOLD, sw=7)
        if vt > 0.6: ctext(d, (540, 590), '地震になる？', Fo(80), PALE, sw=4)
    else:
        st = max(s for s in STEPS if s[0] <= vt); t0, key, num, rows, sz, lab, m, amp = st; i = STEPS.index(st)
        d.rectangle((0, 0, W, 170), fill=(8, 10, 16, 235)); ctext(d, (540, 85), '人数をふやして、1か所で跳ぶと…', Fo(52), GOLD)
        ctext(d, (540, 270), lab, Mi(80), PALE, sw=5)
        tj = (vt - t0 - JUMP) / SL if vt >= t0 + JUMP else vt - t0 - JUMP
        d.rectangle((0, 980, W, 1090), fill=(70, 60, 50)); d.rectangle((0, 980, W, 992), fill=(110, 150, 80))
        lay = S.crowd_layout(num, 60 if num > 1 else 440, 1020 if num > 1 else 640, 980, rows, sz, seed=4 + i); S.draw_crowd(d, lay, tj, sz)
        if num > 1: d.text((30, 1060), '絵は一部', font=Fb(28), fill=PALE, anchor='lm')
        ev = [(land_t(t0), amp)] if True else []
        S.seismo(d, (40, 1120, 1040, 1400), vt, ev, '地震計', noise=0.35, span=5.0)
        shown = vt >= land_t(t0) + 0.1
        mscale(d, 1530, float(m.replace('−', '-')), shown)
        if shown: ctext(d, (540, 420), f'M {m}', BE(150), GOLD, sw=6)
    d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    return im
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05).filter(ImageFilter.GaussianBlur(14))).enhance(0.35)
    im = END_BG.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 430), '82億人', Mi(int(110 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 590), '全員なら？', Mi(110), GOLD, sw=6)
    for i, o in enumerate(['ゆれない', '小さな地震', '大地震']):
        if q > 0.8 + i * 0.4:
            y = 800 + i * 150; d.rounded_rectangle((W / 2 - 300, y - 55, W / 2 + 300, y + 55), 20, fill=(10, 12, 18, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(56), PALE)
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
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, end0=END0, lands=[land_t(s[0]) for s in STEPS], amps=[s[7] for s in STEPS]), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
