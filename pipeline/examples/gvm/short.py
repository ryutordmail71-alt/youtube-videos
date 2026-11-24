"""縦型ショート（1080x1920, 約30秒）"""
import json, sys
sys.path.insert(0, '/home/claude/gvm')
import grender as GR
GR.W, GR.H = 1080, 1920
import gmodel as GM
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import scenes as S
W, H, FPS = 1080, 1920, 30
D = S.D
M = GM.Model(1e8, can_bite=False)
SEGS = [(300, 311, 1.0), (311, 4090, 600.0), (4090, 4152, 12.0)]
CAM0 = [(0, (0, 42, 52.0)), (3.6, (0, 30, 24.0)), (7.5, (0, 36, 34.0)), (10.5, (0, 30, 22.0)), (18.0, (0, 32, 24.0))]
CAM = S._cam(CAM0)
CUES = [(0.2, 'vhook'), (4.4, 'v1'), (8.0, 'v2'), (18.6, 'v3')]
CAPS = [(0.0, 4.2, '身長50mの巨人\nvs 蚊1億匹', S.GOLD), (4.4, 7.8, '蚊が巨人を包み込む！', S.PALE), (8.0, 11.0, 'でも…針が届かない！', S.GOLD),
        (11.0, 18.4, '早送り…', S.PALE), (18.6, 23.0, '巨人の完全勝利\n吸われた血 0L', S.GOLD)]
sm, bdur = S.seg_map(SEGS)
END = 7.6; dur = bdur + END; n = int(dur * FPS)
p = S.writer('/home/claude/gvm/s_video.mp4', W, H); cs = None; sts = []
last = None
for f in range(n):
    vt = f / FPS
    if vt < bdur:
        st, sp = S.v2s(vt, sm)
        for (va, ma, za), (vb, mb, zb) in zip(CAM, CAM[1:]):
            if va <= vt < vb: break
        else: va, ma, za = CAM[-1]; vb, mb, zb = va + 1, ma, za
        u = (lambda x: x * x * (3 - 2 * x))(min(1, max(0, (vt - va) / max(0.01, min(2.5, vb - va)))))
        tx, ty = ma[0] + (mb[0] - ma[0]) * u, ma[1] + (mb[1] - ma[1]) * u
        if cs is None: cs = [tx, ty]
        cs[0] += (tx - cs[0]) * 0.15; cs[1] += (ty - cs[1]) * 0.15; ppm = za + (zb - za) * u
        cap = next(((c, col) for a0, a1, c, col in CAPS if a0 <= vt < a1), (None, None))
        im = GR.render(M, st, (cs[0], cs[1], ppm), dict(title='蚊1億匹 vs 巨人', speed=sp, cap=cap[0], capcol=cap[1], ruler=1.5 < vt < 4.3), f=f, speed=sp)
        last = im; sts.append(round(st, 3))
    else:
        if vt - bdur < 1 / FPS * 0.5 or not hasattr(S, '_sbg'):
            S._sbg = ImageEnhance.Brightness(GR.render(GM.Model(2e10), 200000, (0, 32, 22), dict(off=True), f=0).filter(ImageFilter.GaussianBlur(14))).enhance(0.38).convert('RGBA')
        q = vt - bdur; im = S._sbg.copy(); d = ImageDraw.Draw(im); u = S.fade(q / 0.4)
        S.ctext(d, (W / 2, 520), 'もし巨人の皮膚が', S.Mi(76), S.PALE, sw=4)
        S.ctext(d, (W / 2, 620), '人と同じ薄さだったら？', S.Mi(76), S.PALE, sw=4)
        S.ctext(d, (W / 2, 860), '蚊 ???匹', S.Mi(int(170 * (1.3 - 0.3 * u))), S.GOLD, sw=6)
        S.ctext(d, (W / 2, 1010), 'vs 巨人', S.Mi(90), S.GIANT_C, sw=5)
        if q > 1.2: S.ctext(d, (W / 2, 1200), '何匹いたら危ない？', S.Fo(80), (255, 110, 110), sw=5)
        if q > 2.6:
            d.rounded_rectangle((90, 1420, W - 90, 1600), 24, fill=(10, 12, 18, 225), outline=S.GOLD, width=5)
            S.ctext(d, (W / 2, 1480), '答えは', S.Fo(48), S.PALE); S.ctext(d, (W / 2, 1550), '画面の下の関連動画で ↓', S.Fo(56), S.GOLD)
        im = im.convert('RGB'); sts.append(-1)
    p.stdin.write(im.tobytes())
    if f % 150 == 0: print(f, n, flush=True)
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=CUES + [(bdur + 0.3, 'vcta')], st=sts), open('/home/claude/gvm/s_meta.json', 'w'))
print('done short', dur)
