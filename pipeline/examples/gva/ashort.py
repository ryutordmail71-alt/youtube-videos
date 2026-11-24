"""縦型ショート（1080x1920）：816人なら互角のはず…が負ける"""
import json, sys
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/gvm')
import grender as GR
GR.W, GR.H = 1080, 1920
import arender as A, amodel as AM, ascenes as S
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W, H, FPS = 1080, 1920, 30
M = AM.Model(816)
PRE, SP = 11.0, 2.0
bdur = PRE + M.t_end / SP + 2.0; END = 7.2; dur = bdur + END; n = int(dur * FPS)
CAM = S._cam([(0, (-12, 30, 13.0)), (4.4, (-30, 18, 11.0)), (9.0, (-24, 6, 26.0)), (15.0, (-14, 24, 12.0)), (21.0, (-24, 8, 24.0))])
CAPS = [(0.0, 4.4, '身長50mの巨人と\n綱引き！', S.GOLD), (4.4, 10.6, '巨人の力は人の約816倍\n→ 816人なら互角のはず', S.PALE),
        (11.0, 18.5, 'スタート！', S.GOLD), (18.5, 24.5, 'ところが…', S.PALE)]
v3t = PRE + M.t_end / SP + 0.2
CAPS.append((v3t, bdur, '計算どおりの人数なのに\n負けた！', S.RED))
CUES = [(0.2, 'vhook'), (4.6, 'v1'), (18.5, 'v2'), (v3t, 'v3'), (bdur + 0.3, 'vcta')]
p = S.writer('/home/claude/gva/s_video.mp4', W, H); cs = None; sts = []; bg = None
for f in range(n):
    vt = f / FPS
    if vt < bdur:
        st = (vt - PRE) * (SP if vt > PRE else 1)
        for (va, ma, za), (vb, mb, zb) in zip(CAM, CAM[1:]):
            if va <= vt < vb: break
        else: va, ma, za = CAM[-1]; vb, mb, zb = va + 1, ma, za
        u = (lambda x: x * x * (3 - 2 * x))(min(1, max(0, (vt - va) / max(0.01, min(2.5, vb - va)))))
        tx, ty = ma[0] + (mb[0] - ma[0]) * u, ma[1] + (mb[1] - ma[1]) * u
        if cs is None: cs = [tx, ty]
        cs[0] += (tx - cs[0]) * 0.15; cs[1] += (ty - cs[1]) * 0.15; ppm = za + (zb - za) * u
        cap = next(((c, col) for a0, a1, c, col in CAPS if a0 <= vt < a1), (None, None))
        im = A.render(M, st, (cs[0], cs[1], ppm), dict(title='人間816人 vs 巨人', cap=cap[0], capcol=cap[1]), f=f)
        if vt > PRE: 
            d = ImageDraw.Draw(im); tag = '×2 早送り'; tw = S.Fo(30).getlength(tag) + 60
            d.rounded_rectangle((W / 2 - tw / 2, 400, W / 2 + tw / 2, 450), 10, fill=(200, 60, 60)); d.text((W / 2, 425), tag, font=S.Fo(30), fill=(255, 255, 255), anchor='mm')
        sts.append(round(st, 3))
    else:
        if bg is None: bg = ImageEnhance.Brightness(A.render(M, M.t_end + 2, (-20, 20, 12), dict(off=True), f=0).filter(ImageFilter.GaussianBlur(14))).enhance(0.38).convert('RGBA')
        q = vt - bdur; im = bg.copy(); d = ImageDraw.Draw(im); u = S.fade(q / 0.4)
        S.ctext(d, (W / 2, 470), 'なぜ負けた？', S.Mi(int(120 * (1.3 - 0.3 * u))), S.GOLD, sw=6)
        S.ctext(d, (W / 2, 700), '人間 ???人', S.Mi(140), S.HUM_C, sw=6); S.ctext(d, (W / 2, 850), 'vs 巨人', S.Mi(90), S.GIANT_C, sw=5)
        if q > 1.2: S.ctext(d, (W / 2, 1060), '何人いれば勝てる？', S.Fo(80), S.RED, sw=5)
        if q > 2.6:
            d.rounded_rectangle((90, 1420, W - 90, 1600), 24, fill=(10, 12, 18, 225), outline=S.GOLD, width=5)
            S.ctext(d, (W / 2, 1480), '答えは', S.Fo(48), S.PALE); S.ctext(d, (W / 2, 1550), '画面の下の関連動画で ↓', S.Fo(56), S.GOLD)
        im = im.convert('RGB'); sts.append(-99)
    p.stdin.write(im.tobytes())
    if f % 150 == 0: print(f, n, flush=True)
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=CUES, st=sts), open('/home/claude/gva/s_meta.json', 'w')); print('done short', dur)
