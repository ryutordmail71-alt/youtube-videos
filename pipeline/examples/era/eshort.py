"""縦型ショート：決勝（20℃の湖、息止め vs 巨大なエラ）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import erender as R, emodel as EM
from erender import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, CYAN, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/era'; D = json.load(open(f'{G}/dur.json'))
PRE = 0.3; RATE = 0.52; Bt = R.Battle(None, 60, 20, 2.2, 14.0); END0 = PRE + Bt.endB / RATE + 1.6; dur = END0 + 0.4 + D['vcta'] + 3.6; n = int(dur * FPS)
def vt_of(st): return PRE + st / RATE
CUES = [(0.2, 'vhook'), (3.1, 'v1'), (5.0, 'v3'), (vt_of(4.0) + 0.15, 'v2'), (vt_of(Bt.endB), 'v4'), (END0 + 0.4, 'vcta')]
CAPS = [(3.1, 4.9, '酸素は たっぷり！', GREEN), (5.0, vt_of(4.0), 'でも 体温が\n下がっていく！', RED), (vt_of(4.0) + 0.15, vt_of(4.0) + 3.0, '息止めの人\n4分で限界！', RED), (vt_of(Bt.endB), END0, '28℃！\nエラの人も限界！', RED)]
for (a, k1), (b, k2) in zip(sorted(CUES), sorted(CUES)[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
BG = R.water_bg('lake', W, 680).convert('RGB')
def frame(vt):
    st = max(0.0, (vt - PRE) * RATE); im = Image.new('RGB', (W, H), (10, 12, 20)); im.paste(BG, (0, 440)); d = ImageDraw.Draw(im, 'RGBA')
    R.bubbles(d, vt, 0, W, 450, 1110, 18, 4)
    for i, (Rr, end, ly) in enumerate(((Bt.A, Bt.endA, 640), (Bt.B, Bt.endB, 940))):
        o, T, up, gone = R.person_state(Bt, Rr, end, st); rise = 0 if gone is None else ease(gone / (RATE * 1.6)) * 420
        if ly - rise > 380:
            R.swimmer(d, 560, ly - rise, 520, vt, 'hold' if i == 0 else 'gill', fade((37 - T) / 9), 2.2, (60, 110, 200) if i == 0 else (210, 90, 60), flow=0 if (i == 0 or gone is not None) else 1.0, dim=0 if gone is None else 0.6)
        if rise < 60:
            lab = '息止めの人' if i == 0 else '巨大なエラの人'; tw = Fo(38).getlength(lab)
            d.rounded_rectangle((30, ly - 150, 30 + tw + 30, ly - 92), 14, fill=(10, 12, 18, 210)); d.text((45, ly - 121), lab, font=Fo(38), fill=PALE, anchor='lm')
    d.rectangle((0, 0, W, 440), fill=(8, 10, 16, 255)); d.rectangle((0, 1110, W, H), fill=(10, 12, 20, 255))
    d.text((40, 60), '水温 20℃', font=Fo(44), fill=CYAN, anchor='lm')
    v = R.mmss(st); d.text((W - 260, 62), v, font=BE(84), fill=PALE, anchor='rm'); d.text((W - 248, 70), '経過', font=Fo(36), fill=GREY, anchor='lm')
    d.text((W - 40, 120), '（早送り）', font=Fb(26), fill=GREY, anchor='rm')
    for i, (Rr, end) in enumerate(((Bt.A, Bt.endA), (Bt.B, Bt.endB))):
        o, T, up, gone = R.person_state(Bt, Rr, end, st); y0 = 1150 + i * 340
        d.text((40, y0 + 20), '息止めの人' if i == 0 else '巨大なエラの人（毎分60Lの水）', font=Fo(40), fill=(150, 190, 255) if i == 0 else (255, 160, 120), anchor='lm')
        if gone is not None: d.rounded_rectangle((W - 290, y0 - 6, W - 40, y0 + 46), 12, fill=(160, 30, 40)); ctext(d, (W - 165, y0 + 20), f'限界 {R.mmss(end)}', Fo(34), PALE)
        oc = GREEN if o > 0.5 else (GOLD if o > 0.2 else RED)
        d.text((40, y0 + 100), '酸素の残り', font=Fb(32), fill=GREY, anchor='lm'); R.bar(d, 260, y0 + 100, 820, o, oc, 36); d.text((W - 40, y0 + 100), f'{o * 100:.0f}%', font=BE(72), fill=oc, anchor='rm')
        d.text((40, y0 + 210), '体温', font=Fb(32), fill=GREY, anchor='lm'); tv = f'{T:.1f}'
        d.text((150, y0 + 210), tv, font=BE(110), fill=R.tcol(T), anchor='lm'); d.text((150 + BE(110).getlength(tv) + 8, y0 + 222), '℃', font=Fo(48), fill=R.tcol(T), anchor='lm')
        R.bar(d, 470, y0 + 215, W - 40, (T - 26) / 11, R.tcol(T), 24)
        for th in (35, 32, 28):
            lx = 470 + (W - 510) * (th - 26) / 11; d.line((lx, y0 + 195, lx, y0 + 235), fill=GOLD, width=3); d.text((lx, y0 + 242), f'{th}' + ('限界' if th == 28 else ''), font=Fb(24), fill=GOLD, anchor='mt')
    d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    if vt < 3.0:
        u = ease(vt / 0.3); ctext(d, (W / 2, 250), 'エラがあれば', Mi(int(90 * (1.4 - 0.4 * u))), PALE, sw=4); ctext(d, (W / 2, 370), '水中で暮らせる？', Mi(100), GOLD, sw=5)
    cap = next(((c, col) for a0, a1, c, col in CAPS if a0 <= vt < a1), None)
    if cap:
        lines = cap[0].split('\n'); y0 = 300 - 50 * (len(lines) - 1)
        for q, l in enumerate(lines): ctext(d, (W / 2, y0 + q * 100), l, Fo(80), cap[1], sw=2)
    elif vt >= 3.0: ctext(d, (W / 2, 300), '息止め vs 巨大なエラ', Fo(60), GOLD)
    return im
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05).filter(ImageFilter.GaussianBlur(14))).enhance(0.35)
    im = END_BG.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 450), 'エラ人間が暮らせるのは', Mi(int(84 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 610), '何℃の水？', Mi(130), GOLD, sw=6)
    for i, o in enumerate(['10℃？', '20℃？', '26℃？', '36℃？']):
        if q > 0.8 + i * 0.35:
            x = W / 2 + (i - 1.5) * 245; d.rounded_rectangle((x - 112, 800, x + 112, 920), 20, fill=(10, 12, 18, 220), outline=GOLD, width=4); ctext(d, (x, 860), o, Fo(52), PALE)
    if q > 2.4:
        d.rounded_rectangle((90, 1400, W - 90, 1580), 24, fill=(10, 12, 18, 225), outline=GOLD, width=5)
        ctext(d, (W / 2, 1460), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1530), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for vt in map(float, sys.argv[1:]): (frame(vt) if vt < END0 else endcard(vt - END0)).resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n):
        vt = f / FPS; im = frame(vt) if vt < END0 else endcard(vt - END0); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, pre=PRE, rate=RATE, end0=END0, ends=[Bt.endA, Bt.endB]), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
