"""縦型ショート：心臓1個 vs 心臓10個"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import hrender as R, hmodel as HM
from hrender import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/h10'; D = json.load(open(f'{G}/dur.json'))
PRE = 0.3; END0 = 21.5; dur = 31.5; n = int(dur * FPS)
CAPS = [(3.6, 6.4, '血の量は10倍！でも…', GOLD), (6.6, 8.9, '血が赤くならない！', RED), (9.0, 12.5, '肺の血管も\nもたない！', RED), (17.6, END0, 'ふつうの人にも\n抜かれた！', RED)]
CUES = [(0.2, 'vhook'), (3.6, 'v1'), (6.6, 'v2'), (9.0, 'v3'), (17.7, 'v4'), (22.3, 'vcta')]
B = R.Battle(1, 10, 40); tubes = [R.Tube(), R.Tube()]
def bg():
    im = R.sky(W, H).convert('RGBA'); d = ImageDraw.Draw(im); rng = np.random.default_rng(2)
    for k in range(400):
        x = rng.uniform(0, W); y = rng.uniform(450, 520); c = tuple(int(v) for v in rng.integers(60, 200, 3)); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=c)
    d.rectangle((0, 525, W, 538), fill=(240, 240, 240)); d.rectangle((0, 538, W, 1110), fill=(178, 72, 52))
    for yy in (538, 824, 1106): d.rectangle((0, yy - 3, W, yy + 3), fill=(245, 240, 235))
    return im
BG = bg()
def frame(vt, f):
    st = vt - PRE; stt = max(0.0, st); im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
    dA, dB = B.dist(B.A, stt), B.dist(B.B, stt); mid = (dA + dB) / 2; k = 7.0
    for m in range(int(mid - 100), int(mid + 100)):
        if m % 10: continue
        x = W / 2 + (m - mid) * k
        if -50 < x < W + 50:
            d.line((x, 540, x, 1104), fill=(230, 210, 200, 90), width=3)
            if m >= 0: d.text((x + 6, 1096), f'{m}m', font=Fb(22), fill=(250, 235, 225), anchor='ld')
    for i, (Rr, dd, ly, col) in enumerate(((B.A, dA, 810, (60, 110, 200)), (B.B, dB, 1076, (210, 90, 60)))):
        x = W / 2 + (dd - mid) * k; slump = min(1.0, Rr.at(stt, 6) * 1.6)
        c = R.runner(d, x, ly, 250, dd * 1.7, col, slump); R.hearts_row(d, c[0], c[1], Rr.N, 9 if Rr.N > 3 else 13, stt, 160, per=5)
        lab = '心臓1個' if Rr.N == 1 else '心臓10個'; tw = Fo(40).getlength(lab); lx = max(tw / 2 + 20, x - 170 - tw / 2)
        d.rounded_rectangle((lx - tw / 2 - 16, ly - 150, lx + tw / 2 + 16, ly - 90), 14, fill=(10, 12, 18, 210)); ctext(d, (lx, ly - 120), lab, Fo(40), PALE)
    d.rectangle((0, 0, W, 440), fill=(8, 10, 16, 235))
    ctext(d, (W / 2, 70), 'ふつうの人  vs  心臓10個', Fo(56), GOLD)
    v = f'{stt:4.1f}'; d.text((W / 2 - 12, 160), v, font=BE(80), fill=PALE, anchor='rm'); d.text((W / 2 - 4, 170), '秒', font=Fo(40), fill=GREY, anchor='lm')
    # 下のパネル
    d.rectangle((0, 1120, W, H), fill=(10, 12, 20, 240))
    for i, Rr in enumerate((B.A, B.B)):
        y0 = 1150 + i * 330; tt = Rr.at(stt, 2); dmg = Rr.at(stt, 6); sat = Rr.at(stt, 3); o2 = Rr.at(stt, 4); pc = Rr.at(stt, 5)
        d.text((40, y0 + 20), 'ふつうの人（心臓1個）' if i == 0 else '心臓10個の人', font=Fo(40), fill=(150, 190, 255) if i == 0 else (255, 160, 120), anchor='lm')
        d.text((W - 40, y0 + 20), f'肺を通る {R.f2(tt)}秒', font=Fb(34), fill=GREY, anchor='rm')
        tubes[i].step(max(tt, 0.02), 1 / FPS); tubes[i].draw(d, 110, y0 + 105, 700, 40, max(tt, 0.02), dmg, st, label=True, fs=26, below=True)
        for j, (lab, v, u, c) in enumerate([('酸素', f'{o2:.1f}', 'L/分', PALE), ('満タン度', f'{sat:.0f}', '%', R.mix(R.bcol((sat - 20) / 78), (255, 255, 255), 0.25)), ('肺の圧力', f'{pc:.0f}', '', RED if pc > HM.LIM else GREEN)]):
            cx = 180 + j * 360; d.text((cx, y0 + 190), lab, font=Fb(30), fill=GREY, anchor='mm')
            tw = BE(84).getlength(v); uw = Fb(30).getlength(u); x0 = cx - (tw + uw + 6) / 2
            d.text((x0, y0 + 262), v, font=BE(84), fill=c, anchor='lm'); d.text((x0 + tw + 6, y0 + 278), u, font=Fb(30), fill=GREY, anchor='lm')
    d.text((W / 2, H - 50), '危険ライン：肺の圧力50（仮定）', font=Fb(28), fill=GOLD, anchor='mm')
    d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    if vt < 3.4:
        u = ease(vt / 0.35); ctext(d, (W / 2, 270), '心臓が10個あったら', Mi(int(84 * (1.4 - 0.4 * u))), PALE, sw=4); ctext(d, (W / 2, 380), '最強？', Mi(110), GOLD, sw=5)
    cap = next(((c, col) for a0, a1, c, col in CAPS if a0 <= vt < a1), None)
    if cap:
        lines = cap[0].split('\n'); fnt = Fo(76); y0 = 330 - 45 * (len(lines) - 1)
        for q, l in enumerate(lines): ctext(d, (W / 2, y0 + q * 95), l, fnt, cap[1], sw=2)
    elif vt >= 3.4: ctext(d, (W / 2, 320), '全力で走る！ 取りこむ酸素が多いほど前へ', Fb(36), GREY)
    return im
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05, 0).convert('RGB').filter(ImageFilter.GaussianBlur(14))).enhance(0.35).convert('RGBA')
    im = END_BG.copy(); d = ImageDraw.Draw(im); u = ease(q / 0.4)
    ctext(d, (W / 2, 470), '心臓は、何個が', Mi(int(100 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 620), '最強なのか？', Mi(120), GOLD, sw=6)
    opts = ['1個？', '2個？', '3個？', '10個？']
    for i, o in enumerate(opts):
        if q > 0.8 + i * 0.35:
            x = W / 2 + (i - 1.5) * 240; d.rounded_rectangle((x - 105, 800, x + 105, 920), 20, fill=(10, 12, 18, 220), outline=GOLD, width=4); ctext(d, (x, 860), o, Fo(56), PALE)
    if q > 2.4:
        d.rounded_rectangle((90, 1400, W - 90, 1580), 24, fill=(10, 12, 18, 225), outline=GOLD, width=5)
        ctext(d, (W / 2, 1460), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1530), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for vt in map(float, sys.argv[1:]): (frame(vt, 0) if vt < END0 else endcard(vt - END0)).convert('RGB').resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n):
        vt = f / FPS; im = frame(vt, f) if vt < END0 else endcard(vt - END0); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, pre=PRE, end0=END0), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
