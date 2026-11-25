import json, math, sys
sys.path.insert(0, '/home/claude/met')
from mbase import *
D = json.load(open(f'{G}/dur.json'))
W2, H2 = 1080, 1920
T = {'vhook': 0.15, 'v1': 3.0, 'v2': 10.5, 'v3': 18.5, 'vcta': 22.0}
TB1 = 6.6; TB2 = 13.6; dur = 31.0; n = int(dur * FPS)
CX, CY = 540, 1080
p = writer(f'{G}/s_video.mp4', W2, H2)
def streak(im, d, u, x1, y1, r):
    x0, y0 = x1 + 700, y1 - 900; x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u
    for k in range(18):
        q = k / 18; d.line((x, y, x + (x0 - x1) * 0.25 * q, y + (y0 - y1) * 0.25 * q), fill=(255, int(200 - 120 * q), 80, int(200 * (1 - q))), width=max(2, int(r * (1 - q))))
    glow(im, x, y, r * 2.5, (255, 220, 150), 200); d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 220))
for f in range(n):
    t = f / FPS; im = bg(W2, H2); d = ImageDraw.Draw(im)
    if t < T['vcta']:
        ppk = 3.2; im.alpha_composite(map_img(ppk, W2, H2, CX, CY))
        for c in ['東京駅', '横浜', 'さいたま', '千葉']: city(d, c, ppk, CX, CY, fs=34)
        if t < TB1: streak(im, d, 0.2 + 0.75 * ease(t / TB1), CX + 20, CY - 140, 10); size = '直径10m'
        elif t < T['v2']:
            q = t - TB1; im.alpha_composite(Image.new('RGBA', (W2, H2), (255, 245, 225, int(230 * math.exp(-q * 3)))))
            glow(im, CX + 20, CY - 140, 50 * math.exp(-q * 0.8) + 8, (255, 220, 160), 180); size = '直径10m'
            if q > 0.6: ctext(d, (W2 / 2, 1640), '地上はほぼ無事', Mi(90), GOLD, sw=5)
        elif t < T['v3']:
            size = '直径100m'
            if t < TB2: streak(im, d, ease((t - T['v2']) / (TB2 - T['v2'])), CX, CY, 16)
            else:
                q = t - TB2; im.alpha_composite(Image.new('RGBA', (W2, H2), (255, 245, 225, int(255 * math.exp(-q * 2.2)))))
                ring(im, CX, CY, 40 * ppk * ease(q / 1.5), RED, 90, 255, 5)
                for c in ['東京駅', '横浜', 'さいたま', '千葉']: city(d, c, ppk, CX, CY, fs=34)
                if q > 1.5: ctext(d, (W2 / 2, 1640), '半径 約40km', Mi(96), (255, 140, 130), sw=5)
        else:
            size = '直径1km'; streak(im, d, 0.5 * ease((t - T['v3']) / 3.5), CX, CY, 40)
            ctext(d, (W2 / 2, 1640), '？？？', Mi(120), GOLD, sw=5)
        d.rectangle((0, 0, W2, 520), fill=(8, 8, 14, 230))
        ctext(d, (W2 / 2, 120), '実データでシミュレーション', Fb(44), GOLD)
        if t < T['v1']: lines = ['東京に隕石が', '落ちたら？']
        elif t < T['v2']: lines = ['10mなら 空の上で', '爆発して ほぼ無事']
        elif t < T['v3']: lines = ['100mなら 東京も横浜も', 'すっぽり入る']
        else: lines = ['じゃあ', '1kmなら？']
        ctext(d, (W2 / 2, 260), lines[0], Mi(80), PALE, sw=4); ctext(d, (W2 / 2, 410), lines[1], Mi(88), GOLD, sw=4)
        d.rounded_rectangle((W2 / 2 - 190, 560, W2 / 2 + 190, 650), 20, fill=(0, 0, 0, 200)); ctext(d, (W2 / 2, 605), size, Fo(54), ORANGE)
    else:
        q = t - T['vcta']; im.alpha_composite(map_img(1.2, W2, H2, CX, CY + 100)); im.alpha_composite(Image.new('RGBA', (W2, H2), (8, 6, 10, 170))); d = ImageDraw.Draw(im)
        ctext(d, (W2 / 2, 420), '直径1kmの隕石', Mi(100), PALE, sw=5)
        ctext(d, (W2 / 2, 640), '被害は？', Mi(int(160 * (1.2 - 0.2 * ease(q / 0.4)))), GOLD, sw=6)
        if q > 1.0: ctext(d, (W2 / 2, 880), '大きさ10倍で…まさかの結果に', Fo(56), RED, sw=4)
        rock(d, W2 / 2, 1150, 150, 4)
        if q > 2.2:
            d.rounded_rectangle((90, 1420, W2 - 90, 1600), 24, fill=(12, 8, 14, 235), outline=GOLD, width=5)
            ctext(d, (W2 / 2, 1480), '答えは', Fo(48), PALE); ctext(d, (W2 / 2, 1550), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W2 / 2, H2 - 80), '※実データをもとにした、単純化した空想のシミュレーションです', font=Fb(26), fill=(205, 205, 210), anchor='mm'); d.text((W2 / 2, H2 - 44), '（数値は目安・仮定を含みます）', font=Fb(24), fill=(205, 205, 210), anchor='mm')
    p.stdin.write(im.convert('RGB').tobytes())
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=[(v, k) for k, v in T.items()], tb=[TB1, TB2]), open(f'{G}/s_meta.json', 'w')); print('short', dur)
