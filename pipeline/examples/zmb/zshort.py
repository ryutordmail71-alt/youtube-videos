import json, math, sys
sys.path.insert(0, '/home/claude/zmb')
from zbase import *
import zscenes as Z
D = json.load(open(f'{G}/dur.json'))
W2, H2 = 1080, 1920
T = {'vhook': 0.2, 'v1': 4.8, 'v2': 8.2, 'v3': 12.0, 'vcta': 20.5}
TJ = 5.0; TR1 = 6.0; TM = 12.6
dur = 32.5; n = int(dur * FPS)
p = writer(f'{G}/s_video.mp4', W2, H2)
K = 3.5; OX, OY = 60, 560
for f in range(n):
    t = f / FPS; im = bg(W2, H2); d = ImageDraw.Draw(im)
    if t < T['vcta'] - 0.2:
        if t < T['v3']:
            q = t - TJ; hr = 0 if q < 0 else min(27.0, 27 * q / TR1); nz = 2 ** hr
            m = Z.naive_mask(nz) if nz > 2 else np.zeros(LAND.sum(), bool)
            h = np.where(m, 0.0, 1.0); z = np.where(m, 0.18, 0.0)
            im.alpha_composite(map_layer(h, z, K), (OX, OY))
            x, y = lonlat_px(*SHIBUYA, OX, OY, K); glow(im, x, y, 26 + 10 * math.sin(t * 4), (255, 50, 40), 210)
            d.text((x - 20, y + 20), '渋谷', font=Fo(44), fill=(255, 110, 100), anchor='rt', stroke_width=3, stroke_fill=(0, 0, 0))
            if t >= T['v1']:
                ctext(d, (W2 / 2, 1650), f'{int(hr)}時間後', Mi(90), PALE, sw=4)
                zs = int(round(nz)) if hr < 27 else 2 ** 27
                lab = f'{zs:,}人' if zs < 10000 else (f'約{zs / 1e4:,.0f}万人' if zs < 1e8 else f'約{zs / 1e8:.2f}億人')
                ctext(d, (W2 / 2, 1780), 'ゾンビ ' + lab, Fo(64), RED, sw=3)
        else:
            q = t - TM; day = 0 if q < 0 else min(150, q * 18)
            Z.draw_map(im, d, day, k=K, ox=OX, oy=OY, inset=None)
            ctext(d, (W2 / 2, 1650), '？？日目', Mi(100), PALE, sw=4)
            ctext(d, (W2 / 2, 1790), '本当にシミュレーション中…', Fo(50), GOLD, sw=3)
        d.rectangle((0, 0, W2, 500), fill=(8, 6, 10, 225))
        if t < T['v1']: lines = ['渋谷にゾンビが1人', '日本は何日で全滅？']
        elif t < T['v2']: lines = ['1時間に1人かむと', 'ゾンビは倍々に増える']
        elif t < T['v3']: lines = ['たった27時間で', '日本の人口をこえる！？']
        else: lines = ['でも、日本地図で', '本当に計算すると…']
        ctext(d, (W2 / 2, 170), lines[0], Mi(80), PALE, sw=4); ctext(d, (W2 / 2, 330), lines[1], Mi(86), GOLD, sw=4)
    else:
        q = t - T['vcta']
        Z.draw_map(im, d, 0, k=K, ox=OX, oy=OY + 100, inset=None)
        d.rectangle((0, 0, W2, H2), fill=(0, 0, 0, 0)); ov = Image.new('RGBA', (W2, H2), (8, 6, 10, 170)); im.alpha_composite(ov); d = ImageDraw.Draw(im)
        ctext(d, (W2 / 2, 420), '日本全滅まで', Mi(100), PALE, sw=5)
        ctext(d, (W2 / 2, 640), '？？？日', Mi(int(160 * (1.2 - 0.2 * ease(q / 0.4)))), GOLD, sw=6)
        if q > 1.0: ctext(d, (W2 / 2, 880), '27時間のはずが…まさかの結果に', Fo(56), RED, sw=4)
        zombie(d, W2 / 2 - 90, 1370, 400, phase=t * 2)
        if q > 2.2:
            d.rounded_rectangle((90, 1420, W2 - 90, 1600), 24, fill=(12, 8, 14, 235), outline=GOLD, width=5)
            ctext(d, (W2 / 2, 1480), '答えは', Fo(48), PALE); ctext(d, (W2 / 2, 1550), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W2 / 2, H2 - 80), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(26), fill=(205, 205, 210), anchor='mm'); d.text((W2 / 2, H2 - 44), '（数値は目安・仮定を含みます）', font=Fb(24), fill=(205, 205, 210), anchor='mm')
    p.stdin.write(im.convert('RGB').tobytes())
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=[(v, k) for k, v in T.items()], tj=TJ, tm=TM), open(f'{G}/s_meta.json', 'w')); print('short', round(dur, 1))
