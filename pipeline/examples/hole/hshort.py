"""縦型ショート：真空の穴 vs 空気の入った穴（最初の1秒＝いちばん衝撃的な数字：E1-B）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import hrender as R, hmodel as HM, hscenes as S
from hrender import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, CYAN, ORANGE, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/hole'; D = json.load(open(f'{G}/dur.json'))
PRE = 0.3; RATE = 2.5
def st_of(vt): return max(0.0, (vt - PRE) * RATE)
def vt_of(st): return PRE + st / RATE
END0 = vt_of(S.TP1) + D['v2'] + 0.4 + D['v3'] + 0.6; dur = END0 + 0.4 + D['vcta'] + 3.4; n = int(dur * FPS)
CUES = [(0.15, 'vhook'), (vt_of(12.0), 'v1'), (vt_of(S.TP1), 'v2'), (vt_of(S.TP1) + D['v2'] + 0.4, 'v3'), (END0 + 0.4, 'vcta')]
CAPS = [(vt_of(12.0), vt_of(12.0) + 3.0, '重力は 深いほど\n強くなる！', ORANGE), (vt_of(S.TP1), vt_of(S.TP1) + D['v2'] + 0.4, '真空の人\n約38分で反対側へ！', GOLD),
        (vt_of(S.TP1) + D['v2'] + 0.4, END0, '空気の人は\n時速200kmのまま…', RED)]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
BG = R.space_bg(W, H, 7)
def frame(vt):
    st = st_of(vt); im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
    for i, who in enumerate(('vac', 'air')):
        cx, cy, rad = 280 + i * 520, 900, 235
        R.draw_earth(im, cx, cy, rad); d = ImageDraw.Draw(im, 'RGBA')
        x, v, g, arr = S.person(S.KIND[who], st)
        y = cy + rad + 22 if arr else cy - x / HM.R * rad
        R.faller(d, cx, y, 20, vt, S.COLS[who], glow=fade(v / 9000) * 0.8)
        ctext(d, (cx, cy - rad - 50), S.NAMES[who], Fo(42), S.COLS[who], sw=3)
        if arr: d.rounded_rectangle((cx - 150, cy + rad + 50, cx + 150, cy + rad + 110), 12, fill=(30, 110, 50)); ctext(d, (cx, cy + rad + 80), '到着 38:11', Fo(36), PALE)
        y0 = 1290; d.text((cx - 230, y0), '出口まで', font=Fb(30), fill=GREY, anchor='lm')
        left = 0 if arr else (x + HM.R) / 1000; d.text((cx - 230, y0 + 70), f'{left:,.0f}', font=BE(84), fill=PALE, anchor='lm'); d.text((cx - 230 + BE(84).getlength(f'{left:,.0f}') + 8, y0 + 82), 'km', font=Fo(34), fill=GREY, anchor='lm')
        d.text((cx - 230, y0 + 160), '速さ 時速', font=Fb(30), fill=GREY, anchor='lm'); sp = f'{R.kmh(v):,.0f}'
        d.text((cx - 230, y0 + 230), sp, font=BE(96), fill=GOLD if v > 7000 else PALE, anchor='lm'); d.text((cx - 230 + BE(96).getlength(sp) + 8, y0 + 244), 'km', font=Fo(34), fill=GREY, anchor='lm')
    d.rectangle((0, 0, W, 520), fill=(8, 10, 16, 235))
    d.text((W - 230, 60), R.hms(st), font=BE(84), fill=PALE, anchor='rm'); d.text((W - 218, 70), '経過', font=Fo(36), fill=GREY, anchor='lm')
    d.text((W - 40, 122), '（早送り）', font=Fb(26), fill=GREY, anchor='rm')
    d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    if vt < vt_of(12.0):
        u = ease(vt / 0.25)
        ctext(d, (W / 2, 220), '時速3万6000km', Mi(int(104 * (1.12 - 0.12 * u))), GOLD, sw=6)
        if vt > 0.5: ctext(d, (W / 2, 370), '地球をつらぬく穴に', Mi(68), PALE, sw=4); ctext(d, (W / 2, 460), '飛びこんだら？', Mi(68), PALE, sw=4)
    cap = next(((c, col) for a0, a1, c, col in CAPS if a0 <= vt < a1), None)
    if cap:
        lines = cap[0].split('\n'); y0 = 300 - 55 * (len(lines) - 1)
        for q, l in enumerate(lines): ctext(d, (W / 2, y0 + q * 110), l, Fo(82), cap[1], sw=2)
    elif vt >= vt_of(12.0): ctext(d, (W / 2, 300), '真空の穴 vs 空気の入った穴', Fo(60), GOLD)
    return im
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05).filter(ImageFilter.GaussianBlur(14))).enhance(0.35)
    im = END_BG.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 450), '空気の人は', Mi(int(90 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 610), '反対側に出られる？', Mi(96), GOLD, sw=6)
    for i, o in enumerate(['出られる', '戻ってくる', 'まさかの…']):
        if q > 0.8 + i * 0.4:
            y = 820 + i * 150; d.rounded_rectangle((W / 2 - 300, y - 55, W / 2 + 300, y + 55), 20, fill=(10, 12, 18, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(56), PALE)
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
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, end0=END0), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
