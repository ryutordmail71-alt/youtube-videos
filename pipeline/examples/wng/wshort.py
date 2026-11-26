"""縦型ショート：幅4mの翼（ノガン型）で高さ30mから"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import wrender as R, wmodel as M
from wrender import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREEN, GREY, CYAN, ORANGE, ctext, ease, fade
W, H, FPS = 1080, 1920, 30; G = '/home/claude/wng'; D = json.load(open(f'{G}/dur.json'))
F = M.Flight(4.0, 6); PRE = 3.2; RATE = 1.0; END0 = PRE + F.end / RATE + 1.4; dur = END0 + 0.4 + D['vcta'] + 3.4; n = int(dur * FPS)
WP_OUT = float(F.a[np.where(F.a[:, 4] <= 0)[0][0], 0])
def vt_of(st): return PRE + st / RATE
CUES = [(0.15, 'vhook'), (3.3, 'v1'), (6.4, 'v2'), (vt_of(WP_OUT), 'v3'), (vt_of(F.end), 'v4'), (END0 + 0.4, 'vcta')]
CAPS = [(3.3, 6.3, '幅4mの翼で\n全力で羽ばたく！', GOLD), (6.4, vt_of(WP_OUT), 'でも 高さが\n下がっていく！', RED), (vt_of(WP_OUT), vt_of(F.end), '体力が\n尽きた！', RED), (vt_of(F.end), END0, '約21秒で\n着地！', RED)]
for (a, k1), (b, k2) in zip(sorted(CUES), sorted(CUES)[1:]): assert a + D[k1] < b + 0.05, (k1, k2)
SKY = R.sky_bg(W, 700, 0.9).convert('RGB'); GY = 440 + 630; TOP = 520
def hy(h): return GY - (GY - TOP) * h / 35
def xx(x): return 170 + (W - 230) * x / 420
def frame(vt, nocap=False):
    st = max(0.0, (vt - PRE) * RATE); tt = min(st, F.end); im = Image.new('RGB', (W, H), (10, 12, 20)); im.paste(SKY, (0, 440)); d = ImageDraw.Draw(im, 'RGBA')
    d.polygon([(0, hy(30) - 4), (130, hy(30) - 4), (190, GY), (0, GY)], fill=(90, 135, 70))
    for h in (10, 20, 30): d.line((170, hy(h), W - 90, hy(h)), fill=(255, 255, 255, 60), width=2); d.text((W - 20, hy(h)), f'{h}m', font=Fb(30), fill=PALE, anchor='rm')
    h = F.at(tt, 1); x = F.at(tt, 2); p = F.at(tt, 3); w = F.at(tt, 4); landed = st >= F.end
    k = int(tt / F.dt); idx = np.linspace(0, max(1, k), 50).astype(int); pts = [(xx(F.a[j, 2]), hy(F.a[j, 1])) for j in idx]
    if vt >= PRE: d.line(pts, fill=(255, 170, 120, 220), width=6)
    R.winged(d, xx(x), hy(h) - 50, 230, vt, 0 if landed else 1.0, dim=0.5 if landed else 0)
    d.rectangle((0, 0, W, 440), fill=(8, 10, 16, 255)); d.rectangle((0, 1110, W, H), fill=(10, 12, 20, 255))
    d.text((40, 1170), '翼の幅 4m（いちばん重い鳥と同じ形）', font=Fo(40), fill=(255, 170, 120), anchor='lm')
    d.text((40, 1260), '高さ', font=Fb(34), fill=GREY, anchor='lm'); hv = f'{h:.1f}'; hc = GREEN if h >= 29.5 else (GOLD if h > 10 else RED)
    d.text((40, 1350), hv, font=BE(130), fill=hc, anchor='lm'); d.text((40 + BE(130).getlength(hv) + 8, 1370), 'm', font=Fo(50), fill=hc, anchor='lm')
    v = R.hms(st); d.text((W - 40, 1260), '経過', font=Fb(34), fill=GREY, anchor='rm'); d.text((W - 40, 1350), v, font=BE(130), fill=PALE, anchor='rm')
    pw = 0 if landed else p
    d.text((40, 1480), 'パワー', font=Fb(34), fill=GREY, anchor='lm'); d.text((W - 40, 1480), f'{pw:,.0f} / 必要 {F.preq:,.0f} W', font=Fo(40), fill=RED, anchor='rm')
    R.bar(d, 40, 1550, W - 40, pw / (F.preq * 1.05), ORANGE, 36); nx = 40 + (W - 80) / 1.05; d.line((nx, 1520, nx, 1580), fill=GOLD, width=5)
    d.text((40, 1650), '体力', font=Fb(34), fill=GREY, anchor='lm'); wc = GREEN if w > 0.5 else (GOLD if w > 0.2 else RED)
    R.bar(d, 180, 1650, W - 220, w, wc, 36); d.text((W - 40, 1650), f'{w * 100:.0f}%', font=BE(80), fill=wc, anchor='rm')
    d.text((W / 2, H - 14), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='ms')
    if vt < 3.2:
        u = ease(vt / 0.3); ctext(d, (W / 2, 190), '翼があれば', Mi(int(96 * (1.4 - 0.4 * u))), PALE, sw=4); ctext(d, (W / 2, 330), '人間は飛べる？', Mi(110), GOLD, sw=5)
    cap = None if nocap else next(((c, col) for a0, a1, c, col in CAPS if a0 <= vt < a1), None)
    if cap:
        lines = cap[0].split('\n'); y0 = 230 - 55 * (len(lines) - 1)
        for q, l in enumerate(lines): ctext(d, (W / 2, y0 + q * 110), l, Fo(84), cap[1], sw=2)
    elif vt >= 3.2 and not nocap: ctext(d, (W / 2, 230), '高さ30mの丘から', Fo(64), GOLD)
    return im
END_BG = None
def endcard(q):
    global END_BG
    if END_BG is None: END_BG = ImageEnhance.Brightness(frame(END0 - 0.05, True).filter(ImageFilter.GaussianBlur(14))).enhance(0.35)
    im = END_BG.copy(); d = ImageDraw.Draw(im, 'RGBA'); u = ease(q / 0.4)
    ctext(d, (W / 2, 430), 'ずっと飛ぶには', Mi(int(84 * (1.3 - 0.3 * u))), PALE, sw=5); ctext(d, (W / 2, 590), '翼の幅が何m必要？', Mi(104), GOLD, sw=6)
    for i, o in enumerate(['8m？', '12m？', '20m？', '30m？']):
        if q > 0.8 + i * 0.35:
            x = W / 2 + (i - 1.5) * 245; d.rounded_rectangle((x - 112, 780, x + 112, 900), 20, fill=(10, 12, 18, 220), outline=GOLD, width=4); ctext(d, (x, 840), o, Fo(52), PALE)
    if q > 2.4:
        d.rounded_rectangle((90, 1400, W - 90, 1580), 24, fill=(10, 12, 18, 225), outline=GOLD, width=5)
        ctext(d, (W / 2, 1460), '答えは', Fo(48), PALE); ctext(d, (W / 2, 1530), '画面の下の関連動画で ↓', Fo(56), GOLD)
    d.text((W / 2, H - 40), R.NOTE, font=Fb(24), fill=(225, 225, 230), anchor='mm')
    return im
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for vt in map(float, sys.argv[1:]): (frame(vt) if vt < END0 else endcard(vt - END0)).resize((540, 960)).save(f'{G}/stills/short_{vt:05.1f}.jpg')
        raise SystemExit
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for f in range(n):
        vt = f / FPS; im = frame(vt) if vt < END0 else endcard(vt - END0); p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); json.dump(dict(dur=dur, cues=CUES, pre=PRE, rate=RATE, end0=END0, ends=[F.end], wp=WP_OUT), open(f'{G}/s_meta.json', 'w')); print('done short', dur)
