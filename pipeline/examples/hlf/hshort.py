import json, math, sys
sys.path.insert(0, '/home/claude/hlf')
import hscenes as S
from PIL import ImageDraw
W, H, FPS = 1080, 1920, 30
D = S.D
T = {'vhook': 0.2}; T['v1'] = T['vhook'] + D['vhook'] + 0.4; T['v2'] = T['v1'] + D['v1'] + 1.6; T['v3'] = T['v2'] + D['v2'] + 0.6; T['vcta'] = T['v3'] + D['v3'] + 1.6
dur = T['vcta'] + D['vcta'] + 1.2; n = int(dur * FPS)
p = S.writer(f'{S.G}/s_video.mp4', W, H)
for f in range(n):
    t = f / FPS; im = S.bg(W, H); d = ImageDraw.Draw(im)
    if t < T['v2'] - 0.2:
        S.ctext(d, (W / 2, 260), 'あなたの心臓は', S.Mi(92), S.PALE, sw=4); S.ctext(d, (W / 2, 390), '一生で何回動く？', S.Mi(100), S.GOLD, sw=5)
        beat = math.exp(-((t * 70 / 60) % 1) * 10); S.heart(d, W / 2, 820, 260, (220, 50, 60), beat)
        S.ctext(d, (W / 2, 1150), '1分間に 約70回', S.Fo(56), S.PALE)
        if t > T['v1']:
            u = S.ease((t - T['v1']) / 1.2); v = S.HB * u
            S.ctext(d, (W / 2, 1380), '約31億回' if u >= 0.995 else f'約{S.jnum(v)}回', S.Fo(130), S.GOLD, sw=5)
    elif t < T['vcta'] - 0.2:
        S.ctext(d, (W / 2, 260), 'まばたきで', S.Mi(92), S.PALE, sw=4); S.ctext(d, (W / 2, 390), '目を閉じている時間は？', S.Mi(84), S.GOLD, sw=5)
        S.eye(d, W / 2, 820, 260, 0.0 if (t * 0.8) % 1 < 0.12 else 1.0)
        S.ctext(d, (W / 2, 1150), '1回 約0.1秒 × 一生ぶん', S.Fo(56), S.PALE)
        if t > T['v3']: S.ctext(d, (W / 2, 1380), '1年半近く！', S.Fo(140), S.GOLD, sw=5)
    else:
        q = t - T['vcta']
        S.ctext(d, (W / 2, 300), 'あなたの一生（84年）', S.Mi(80), S.PALE, sw=4)
        for i, lab in enumerate(['眠る時間', '食べる量', '歩く距離']):
            y = 520 + i * 220; u = S.ease((q - i * 0.5) / 0.4)
            d.rounded_rectangle((120, y, W - 120, y + 170), 24, fill=(10, 12, 20, int(225 * u)), outline=S.GOLD, width=4)
            d.text((170, y + 85), lab, font=S.Fo(60), fill=S.PALE, anchor='lm'); d.text((W - 170, y + 85), '？？？', font=S.Fo(70), fill=S.GOLD, anchor='rm')
        if q > 2.0: S.ctext(d, (W / 2, 1300), 'あなたは人生の何％？', S.Fo(76), S.RED, sw=4)
        if q > 3.2:
            d.rounded_rectangle((90, 1440, W - 90, 1620), 24, fill=(10, 12, 18, 225), outline=S.GOLD, width=5)
            S.ctext(d, (W / 2, 1500), '答えは', S.Fo(48), S.PALE); S.ctext(d, (W / 2, 1570), '画面の下の関連動画で ↓', S.Fo(56), S.GOLD)
    d.text((W / 2, H - 50), S.DISC, font=S.Fb(26), fill=(215, 215, 220), anchor='mm')
    p.stdin.write(im.convert('RGB').tobytes())
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=[(v, k) for k, v in T.items()]), open(f'{S.G}/s_meta.json', 'w')); print('short', round(dur, 1))
