import json, math, sys
sys.path.insert(0, '/home/claude/nfj')
from nbase import *
import nbase as B
from PIL import ImageDraw
D = json.load(open(f'{G}/dur.json'))
W2, H2 = 1080, 1920
T = {'vhook': 0.2, 'v1': 4.5, 'v2': 8.5, 'v3': 15.5, 'vcta': 22.0}; TJ = 9.3; TR = 3.4
HOPS = [0.4, 1.6, 2.8, 5.2, 6.6]
dur = T['vcta'] + D['vcta'] + 6.0; n = int(dur * FPS)
p = writer(f'{G}/s_video.mp4', W2, H2); GR = 1500
def hop(t):
    for h0 in HOPS:
        q = t - h0
        if 0 <= q < 0.6: return math.sin(q / 0.6 * math.pi), 0
        if -0.25 <= q < 0: return 0, 1 + q / 0.25
    return 0, 0
for f in range(n):
    t = f / FPS; im = bg(W2, H2); d = ImageDraw.Draw(im)
    if t < T['vcta'] - 0.2:
        d.rectangle((0, GR, W2, H2), fill=(52, 58, 76))
        if t < T['v2']:
            s = 1500.0                                   # 1mあたりのpx（ノミ拡大）
            a, cr = hop(t); hh = 0.18 * a
            ruler_m(d, 170, GR, s, 330)
            if t >= T['v1']: d.line((230, GR - 0.18 * s, 900, GR - 0.18 * s), fill=GOLD, width=4); d.text((900, GR - 0.18 * s - 12), '約18cm', font=Fo(56), fill=GOLD, anchor='rs')
            flea(d, 600, GR - hh * s, 230, crouch=cr)
            if t >= T['v1']: ctext(d, (600, GR + 110), 'ノミは拡大して表示（体長 約1.8mm）', Fb(40), GRAY)
        elif t < T['v3']:
            q = t - TJ; h = 0 if q < 0 else 170 * (1 - (1 - min(1, q / TR)) ** 2); s = min(240.0, 950 / (h + 2.2))
            building(d, 640, GR, 35, 170, s, floors=50)
            ruler_m(d, 150, GR, s, GR - 500)
            yf = GR - h * s; figure(d, 450, yf, s / 100, crouch=fade((t - TJ + 0.8) / 0.5) if q < 0 else 0, col=FLEA_C)
            if s < 30:
                d.ellipse((450 - 18, yf - 1.7 * s - 18, 450 + 18, yf - 1.7 * s + 18), outline=GOLD, width=5)
                d.text((490, yf - 1.7 * s), f'{h:.0f}m', font=Fo(60), fill=GOLD, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
        else:
            q = t - T['v3']
            for x, name, col in [(220, 'ノミ人間', FLEA_C), (540, 'ふつうの人間', HUM_C), (860, 'アワフキムシ人間', HOP_C)]:
                figure(d, x - 40, GR, 2.0, crouch=0.5 + 0.5 * math.sin(q * 3), col=col); ctext(d, (x, GR + 60), name, Fo(40), col)
            if q > 2.0: ctext(d, (220, GR - 470), '？？？cm', Fo(64), GOLD, sw=4)
        d.rectangle((0, 0, W2, 460), fill=(8, 10, 16, 220))
        if t < T['v1']: lines = ['人間が', 'ノミの跳躍力を持ったら？']
        elif t < T['v2']: lines = ['ノミは跳べる高さ約18cm', '＝ 体長の約100倍！']
        elif t < T['v3']: lines = ['人間なら身長の100倍', '170m！？']
        else: lines = ['でも、踏み切りの速さで', '正しく計算し直すと…']
        ctext(d, (W2 / 2, 150), lines[0], Mi(74), PALE, sw=4); ctext(d, (W2 / 2, 300), lines[1], Mi(96 if len(lines[1]) < 8 else 76), GOLD, sw=4)
    else:
        q = t - T['vcta']
        ctext(d, (W2 / 2, 420), 'ノミ人間の記録', Mi(100), PALE, sw=5)
        ctext(d, (W2 / 2, 640), '？？？cm', Mi(int(150 * (1.2 - 0.2 * ease(q / 0.4)))), GOLD, sw=6)
        if q > 1.0: ctext(d, (W2 / 2, 880), '170mのはずが…まさかの結果に', Fo(60), RED, sw=4)
        if q > 2.2:
            d.rounded_rectangle((90, 1420, W2 - 90, 1600), 24, fill=(10, 12, 20, 225), outline=GOLD, width=5)
            ctext(d, (W2 / 2, 1480), '答えは', Fo(48), PALE); ctext(d, (W2 / 2, 1550), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W2 / 2, H2 - 50), DISC, font=Fb(24), fill=(215, 215, 220), anchor='mm')
    p.stdin.write(im.convert('RGB').tobytes())
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=[(v, k) for k, v in T.items()], hops=HOPS, tj=TJ), open(f'{G}/s_meta.json', 'w')); print('short', round(dur, 1))
