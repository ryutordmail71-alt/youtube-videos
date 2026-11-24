import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/claude/bvs')
import battle as B
B.W, B.H = 1080, 1920
import rbattle as RB
W, H, FPS = 1080, 1920, 30
Fo = B.Fo; BK, BD = B.BK, B.BD
PALE, BEAR_C, SAL_C, GOLD = RB.PALE, RB.BEAR_C, RB.SAL_C, RB.GOLD
BE = lambda s: ImageFont.truetype(B.BEBAS, s)

def vhud(im, R, i, st, hud):
    d = ImageDraw.Draw(im, 'RGBA'); ne, ng, full = R.counts(st)
    d.rectangle((0, 0, W, 340), fill=(8, 10, 16, 220))
    d.text((W / 2, 64), hud.get('title', ''), font=Fo(BK, 54), fill=PALE, anchor='mm')
    d.text((60, 150), '食べられた鮭', font=Fo(BK, 34), fill=BEAR_C, anchor='lm'); d.text((60, 225), f'{ne:,}', font=BE(96), fill=PALE, anchor='lm')
    d.text((W - 60, 150), '上流に着いた鮭', font=Fo(BK, 34), fill=SAL_C, anchor='rm'); d.text((W - 60, 225), f'{ng:,}', font=BE(96), fill=PALE, anchor='rm')
    x0, x1 = 60, W - 60; d.rounded_rectangle((x0, 280, x1, 306), 8, fill=(255, 255, 255, 40))
    if ne: d.rounded_rectangle((x0, 280, x0 + max(10, (x1 - x0) * ne / R.NS), 306), 8, fill=BEAR_C)
    if ng: d.rounded_rectangle((x1 - max(10, (x1 - x0) * ng / R.NS), 280, x1, 306), 8, fill=SAL_C)
    d.line((W / 2, 272, W / 2, 314), fill=(255, 255, 255), width=3)
    d.text((W / 2, 326), '50%以上が上流に着けば鮭の勝ち', font=Fo(BD, 24), fill=(220, 220, 225), anchor='mm')
    sp = hud.get('speed', 1.0)
    if sp != 1.0:
        tag = 'スロー' if sp < 1 else f'×{sp:.0f} 早送り'; d.rounded_rectangle((W / 2 - 110, 360, W / 2 + 110, 410), 10, fill=(200, 60, 60, 230)); d.text((W / 2, 385), tag, font=Fo(BK, 30), fill=(255, 255, 255), anchor='mm')
    cap = hud.get('cap')
    if cap:
        f = Fo(BK, 64); lines = cap.split('\n'); hh = 90 * len(lines); tw = max(f.getlength(l) for l in lines)
        d.rounded_rectangle((W / 2 - tw / 2 - 40, 1420, W / 2 + tw / 2 + 40, 1420 + hh + 40), 18, fill=(8, 10, 16, 215))
        for k, l in enumerate(lines): d.text((W / 2, 1420 + 20 + 45 + k * 90), l, font=f, fill=hud.get('capcol', PALE), anchor='mm')
    d.text((W / 2, H - 40), '※実データをもとにした、単純化したシミュレーションです', font=Fo(BD, 24), fill=(235, 235, 235, 210), anchor='mm')
RB.hud_draw = vhud

R1 = RB.RRound('r1'); R2 = RB.RRound('r2')
# (長さ, ラウンド, sim開始, 速度, カメラ開始, カメラ終了, キャプション, タイトル)
T1 = '熊1000体 vs 鮭1000匹'
SEG = [
 (4.6, R1, 4.0, 1.0, ((152, 100), 5.0), ((150, 100), 5.6), '熊1000体が待つ川を\n鮭は突破できる？', T1),
 (5.0, R1, 25.0, 1.0, ('f', 22.0), ('f', 24.0), '熊が鮭を捕まえた！', T1),
 (8.0, R1, 30.0, 8.0, ((128, 98), 9.0), ((125, 98), 8.0), '鮭が次々と食べられる…', T1),
 (3.6, R1, 94.0, 4.0, ((122, 98), 8.0), ((122, 98), 8.0), '結果は…全滅', T1),
 (7.6, R2, 3.0, 1.0, ((150, 100), 5.0), ((145, 100), 5.6), '鮭が何匹いれば\n熊に勝てる？', '熊1000体 vs 鮭 ?????匹'),
]
CUES = [(0.2, 'vhook'), (4.9, 'v1'), (9.8, 'v2'), (17.8, 'v3'), (21.4, 'vcta')]
def main():
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '/home/claude/bvs/s_video.mp4'], stdin=subprocess.PIPE)
    vt0 = 0; acts = []; cs = None
    for dur, R, s0, sp, ca, cb, cap, title in SEG:
        n = int(dur * FPS)
        for f in range(n):
            u = B.ease(f / max(1, n - 1)); st = s0 + f / FPS * sp
            def c(m): return RB.focus(R, st) if m == 'f' else m
            a, b = c(ca[0]), c(cb[0]); tx, ty = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
            if cs is None or f == 0: cs = [tx, ty]
            cs[0] += (tx - cs[0]) * 0.15; cs[1] += (ty - cs[1]) * 0.15
            ppm = ca[1] + (cb[1] - ca[1]) * u
            capcol = GOLD if cap and ('全滅' in cap or '何匹' in cap) else PALE
            hud = dict(title=title, speed=sp, cap=cap, capcol=capcol)
            if '?????' in title: RB.hud_draw = lambda im, R, i, st, h: vhud(im, R, i, st, h); R_ns = R.NS
            im = RB.render_frame(R, st, (cs[0], cs[1], ppm), hud)
            p.stdin.write(im.tobytes()); i = R.frame_idx(st); acts.append(int(((R.st[i] == 1) | (R.st[i] == 2)).sum()))
        vt0 += dur
    p.stdin.close(); p.wait()
    json.dump(dict(act=acts, cues=CUES, dur=vt0), open('/home/claude/bvs/s_meta.json', 'w')); print('short done', vt0)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        S = '/tmp/claude-0/-home-claude/3f2fb178-41da-56af-8da6-007907094230/scratchpad/'
        out = Image.new('RGB', (360 * 5, 640))
        for k, (dur, R, s0, sp, ca, cb, cap, title) in enumerate(SEG):
            st = s0 + 1.0; cc = RB.focus(R, st) if ca[0] == 'f' else ca[0]
            im = RB.render_frame(R, st, (cc[0], cc[1], ca[1]), dict(title=title, speed=sp, cap=cap)); out.paste(im.resize((360, 640)), (k * 360, 0))
        out.save(S + 'svt.jpg'); sys.exit()
    main()
