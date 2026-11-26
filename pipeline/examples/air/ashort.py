"""縦型ショート：AIの3つの攻撃（最初の1秒＝問いの文字：E1-A）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, ascn as S
from arnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, GREEN, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/air'; D = json.load(open(f'{G}/dur.json')); AIR = S.AIR
STEPS = [(3.9, 'v1', 'その1', '日本中を 停電させる', '295万戸'), (12.2, 'v2', 'その2', 'スマホを 乗っ取る（架空）', '2億台'), (17.9, 'v3', 'その3', 'ロボット軍団で 攻める', '500万台')]
END0 = 23.2; dur = END0 + 0.4 + D['vcta'] + 3.2; n = int(dur * FPS)
CUES = [(0.15, 'vhook')] + [(s[0], s[1]) for s in STEPS] + [(END0 + 0.4, 'vcta')]
for (a, k1), (b, k2) in zip(CUES, CUES[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
BG = S.dark_bg(W, H)
def bright_bg():
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.55) / H) ** 2)
    t = np.clip(r / 0.7, 0, 1)[..., None]; c = np.array((150, 40, 50), float) * (1 - t) + np.array((30, 10, 16), float) * t
    return Image.fromarray(c.astype(np.uint8))
BB = bright_bg()
def phones_grid(d, k, n=60, x0=110, y0=640, cols=10):
    for i in range(n):
        S.phone(d, x0 + (i % cols) * 96, y0 + (i // cols) * 130, 100, 1.0 if i < k else 0.0)
def frame(vt):
    if vt < STEPS[0][0]:
        im = BB.copy().convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
        if vt < 0.3:   # 結果のチラ見せ：真っ赤になったスマホの壁
            phones_grid(d, 60)
        else:
            S.ai_eye(im, 540, 1150, 330, vt); d = ImageDraw.Draw(im, 'RGBA')
        u = ease(vt / 0.25)
        ctext(d, (540, 300), 'AIが反乱したら', Mi(int(104 * (1.15 - 0.15 * u))), PALE, sw=7)
        ctext(d, (540, 470), '人類は何日もつ？', Mi(int(112 * (1.15 - 0.15 * u))), GOLD, sw=8)
        if vt > 0.8: ctext(d, (540, 1620), '実データでシミュレーション', Fo(48), PALE, sw=4)
    else:
        im = BG.copy().convert('RGBA'); st = max(s for s in STEPS if s[0] <= vt); t0, key, no, lab, val = st; i = STEPS.index(st); q = vt - t0; u = ease(q / 0.35)
        d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, 170), fill=(6, 6, 12, 235)); ctext(d, (540, 85), 'AIの攻撃', Fo(56), GOLD)
        ctext(d, (540, 270), f'{no}　{lab}', Fo(60), PALE, sw=4)
        ctext(d, (540, 440), val, Mi(int(170 * (1.25 - 0.25 * u))), AIR, sw=7)
        if i == 0:
            lit = 1.0 if q < 1.2 else max(0.0, 1 - (q - 1.2) / 0.4)
            S.city(d, 60, 1020, 1300, lit, seed=5); d.rectangle((40, 1300, 1040, 1310), fill=(80, 80, 90))
            if q > 3.0: ctext(d, (540, 1450), '北海道の大停電（2018年）', Fo(48), PALE, sw=3); ctext(d, (540, 1530), '約295万戸が 真っ暗に', Fo(56), GOLD, sw=3)
        elif i == 1:
            k = int(60 * fade((q - 0.5) / 3.5) ** 3); phones_grid(d, k)
            ctext(d, (540, 1520), '1時間ごとに 2倍に広がる（架空）', Fo(46), PALE, sw=3)
        else:
            for j in range(8): S.robot_arm(d, 150 + (j % 4) * 260, 900 + (j // 4) * 330, 170, vt, ph=j)
            ctext(d, (540, 1540), '世界の工場のロボット', Fo(52), PALE, sw=3)
        for k, s in enumerate(STEPS):
            col = GOLD if k == i else (90, 95, 110); d.ellipse((450 + k * 90 - 14, 1700 - 14, 450 + k * 90 + 14, 1700 + 14), fill=col)
    d = ImageDraw.Draw(im, 'RGBA'); d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    return im.convert('RGB')
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05).filter(ImageFilter.GaussianBlur(14))).enhance(0.35)
    im = END_BG.copy().convert('RGBA'); S.ai_eye(im, 540, 330, 120, q); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 560), '人類は', Mi(int(100 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 700), '何日もつ？', Mi(120), GOLD, sw=6)
    for i, o in enumerate(['1日で 負ける', '1年で 負ける', 'ずっと 負けない']):
        if q > 0.8 + i * 0.4:
            y = 900 + i * 150; d.rounded_rectangle((W / 2 - 360, y - 55, W / 2 + 360, y + 55), 20, fill=(10, 12, 18, 220), outline=GOLD, width=4); ctext(d, (W / 2, y), o, Fo(52), PALE)
    if q > 2.4:
        d.rounded_rectangle((90, 1400, W - 90, 1580), 24, fill=(10, 12, 18, 225), outline=GOLD, width=5)
        ctext(d, (W / 2, 1460), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1530), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im.convert('RGB')
if __name__ == '__main__':
    if len(sys.argv) > 1:
        import os; os.makedirs(f'{G}/stills', exist_ok=True)
        for vt in map(float, sys.argv[1:]): (frame(vt) if vt < END0 else endcard(vt - END0)).resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n):
        vt = f / FPS; im = frame(vt) if vt < END0 else endcard(vt - END0); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, end0=END0, steps=[s[0] for s in STEPS]), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
