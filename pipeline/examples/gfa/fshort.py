"""縦型ショート：巨人が立ち上がると気絶"""
import json, sys
sys.path.insert(0, '/home/claude/gfa'); sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/gvm')
import grender as GR
GR.W, GR.H = 1080, 1920
import frender as R, fmodel as FM, fscenes as S
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W, H, FPS = 1080, 1920, 30
MG, MS = S.MG, S.MS
B1, B2 = 2.0, 16.0                      # それぞれのシミュレーションの 0 秒にあたる動画の時刻
SEG2 = 14.5; END0 = 29.5; dur = END0 + 7.0; n = int(dur * FPS)
CAPS = [(0.0, 4.4, '身長50mの巨人が\n立ち上がったら…', S.GOLD), (5.2, 9.0, '人と同じ心臓だと\n脳に血が届かない！', S.PALE), (11.9, SEG2, '巨人、気絶！', S.RED),
        (SEG2 + 0.4, 21.5, 'スーパー心臓\n（血圧 最大900）なら？', S.GOLD), (21.5, 25.9, '心臓がゆっくりしか\n動かない…', S.PALE), (25.9, END0, 'それでも気絶！', S.RED)]
CUES = [(0.2, 'vhook'), (5.2, 'v1'), (SEG2 + 0.6, 'v2'), (26.0, 'v3'), (END0 + 0.3, 'vcta')]
def cam(vt):
    if vt < SEG2: return (-10, 30, 15.0) if vt < 13 else (-18, 26, 12.0)
    return (-10, 30, 15.0) if vt < 27.5 else (-18, 26, 12.0)
p = S.writer('/home/claude/gfa/s_video.mp4', W, H); sts = []; bg = None; cs = None
for f in range(n):
    vt = f / FPS
    if vt < END0:
        M, st, tit = (MG, vt - B1, '巨人（人と同じ心臓）') if vt < SEG2 else (MS, vt - B2, '巨人（スーパー心臓）')
        c = cam(vt)
        if cs is None or abs(vt - SEG2) < 0.5 / FPS: cs = list(c)
        for i in range(3): cs[i] += (c[i] - cs[i]) * 0.06
        cap = next(((c_, col) for a0, a1, c_, col in CAPS if a0 <= vt < a1), (None, None))
        im = R.render(M, st, tuple(cs), dict(title=tit, cap=cap[0], capcol=cap[1]), f=f); sts.append([0 if vt < SEG2 else 1, round(st, 3)])
    else:
        if bg is None: bg = ImageEnhance.Brightness(S.shot(S.MSL, S.STAND, (-6, 30, 15)).filter(ImageFilter.GaussianBlur(14))).enhance(0.38).convert('RGBA')
        q = vt - END0; im = bg.copy(); d = ImageDraw.Draw(im); u = S.fade(q / 0.4)
        S.ctext(d, (W / 2, 520), '何分かければ', S.Mi(int(110 * (1.3 - 0.3 * u))), S.PALE, sw=6)
        S.ctext(d, (W / 2, 680), '気絶せずに立てる？', S.Mi(96), S.GOLD, sw=6)
        if q > 1.2: S.ctext(d, (W / 2, 900), '巨人の血圧の謎', S.Fo(70), S.RED, sw=4)
        if q > 2.6:
            d.rounded_rectangle((90, 1420, W - 90, 1600), 24, fill=(10, 12, 18, 225), outline=S.GOLD, width=5)
            S.ctext(d, (W / 2, 1480), '答えは', S.Fo(48), S.PALE); S.ctext(d, (W / 2, 1550), '画面の下の関連動画で ↓', S.Fo(56), S.GOLD)
        im = im.convert('RGB'); sts.append([-1, -99])
    p.stdin.write(im.tobytes())
    if f % 150 == 0: print(f, n, flush=True)
p.stdin.close(); p.wait()
json.dump(dict(dur=dur, cues=CUES, st=sts), open('/home/claude/gfa/s_meta.json', 'w')); print('done short', dur)
