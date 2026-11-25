import json, math, sys
sys.path.insert(0, '/home/claude/mlm')
import mscenes as M
from PIL import ImageDraw
W, H, FPS = 1080, 1920, 30; HS = M.HS
FL = 1500
T = {'vhook': 0.2, 'v1': 4.2, 'v2': 9.4, 'v3': 14.6, 'vcta': 19.0}; JUMP = {'v1': (5.0, 1.0), 'v2': (10.2, 1 / 0.9)}
dur = T['vcta'] + M.D['vcta'] + 3.0; n = int(dur * FPS)
p = HS.writer(f'{M.G}/s_video.mp4', W, H); st_log = []
M.FLOOR = FL; M.CM = 2.4
for f in range(n):
    t = f / FPS; im = HS.bg(W, H, (18, 22, 36)); d = ImageDraw.Draw(im)
    if t < T['vcta'] - 0.2:
        d.rectangle((0, FL, W, H), fill=(52, 58, 76)); M.ruler(d, 260)
        seg = 'v2' if t >= T['v2'] else 'v1'; tj, k = JUMP[seg]
        if t < T['v1']: hcm, cr, s = 0, 0.5 + 0.5 * math.sin(t * 2.5), 0
        elif t >= T['v3']: hcm, cr, s = 0, min(1, (t - T['v3']) / 1.5), 0
        else:
            hcm, cr, s, brk, fall = M.jump_state(t - tj, k)
        M.figure(d, 560, FL - hcm * M.CM, crouch=max(0, cr) * 0.9)
        if T['v1'] <= t < T['v3']:
            best = M.jump_h(k) * 100 if t - tj > 0.6 else 0
            if best: d.line((280, FL - best * M.CM, 900, FL - best * M.CM), fill=HS.GOLD, width=4); d.text((900, FL - best * M.CM - 10), f'{best:.0f}cm', font=HS.Fo(56), fill=HS.GOLD, anchor='rs')
        d.rectangle((0, 0, W, 420), fill=(8, 10, 16, 220))
        if t < T['v1']: lines = ['リミッターを外したら', '人はどこまで跳べる？']
        elif t < T['v2']: lines = ['ふつうの全力', '（筋肉の約90%）']
        elif t < T['v3']: lines = ['リミッター解除', '（筋肉の100%）']
        else: lines = ['じゃあ', '筋肉の力が3倍なら？']
        HS.ctext(d, (W / 2, 140), lines[0], HS.Mi(80), HS.PALE, sw=4); HS.ctext(d, (W / 2, 280), lines[1], HS.Mi(84), HS.GOLD, sw=4)
    else:
        q = t - T['vcta']
        HS.ctext(d, (W / 2, 420), '筋肉の力 3倍', HS.Mi(110), HS.PALE, sw=5)
        HS.ctext(d, (W / 2, 650), '記録 ？？？cm', HS.Mi(int(120 * (1.2 - 0.2 * HS.ease(q / 0.4)))), HS.GOLD, sw=6)
        if q > 1.0: HS.ctext(d, (W / 2, 880), '計算では2m以上のはずが…', HS.Fo(64), HS.RED, sw=4)
        if q > 2.2:
            d.rounded_rectangle((90, 1420, W - 90, 1600), 24, fill=(10, 12, 18, 225), outline=HS.GOLD, width=5)
            HS.ctext(d, (W / 2, 1480), '答えは', HS.Fo(48), HS.PALE); HS.ctext(d, (W / 2, 1550), '画面の下の関連動画で ↓', HS.Fo(56), HS.GOLD)
    d.text((W / 2, H - 50), M.DISC, font=HS.Fb(26), fill=(215, 215, 220), anchor='mm')
    p.stdin.write(im.convert('RGB').tobytes())
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=[(v, k) for k, v in T.items()]), open(f'{M.G}/s_meta.json', 'w')); print('short', round(dur, 1))
