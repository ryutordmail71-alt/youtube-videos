"""縦型ショート（15時枠：E1-B＝最初の1秒に衝撃の数字「人口34万人」）"""
import json, math, sys
from PIL import Image, ImageDraw
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, GREY, CYAN, ICE, RED, ctext, ease, fade, kb, fog, vignette, alpha_text
import bdraw as B
import pcont as C
W, H = 1080, 1920; G = '/home/claude/bie'; D = json.load(open(f'{G}/dur.json'))
def at(key, sub, t0): s = C.NAR[key]; return t0 + D[key] * s.index(sub) / len(s)
S1 = 3.4; S2 = S1 + D['v1'] + 0.35; S3 = S2 + D['v2'] + 0.35; END0 = S3 + D['v3'] + 0.4
TC = END0 + 0.3; TH = TC + D['vcta'] + 0.3; dur = TH + 2.2
CUES = [(0.15, 'vhook'), (S1, 'v1'), (S2, 'v2'), (S3, 'v3'), (TC, 'vcta')]
def ap(t, t0, d=0.4): return ease((t - t0) / d)
def cap(im, s): ImageDraw.Draw(im).text((W - 24, 40), s, font=Fb(26), fill=(225, 228, 235), anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
def fin(im, t, k=0.2, tag=False, caption=None):
    fog(im, t, k); vignette(im, 0.7); d = ImageDraw.Draw(im, 'RGBA')
    if tag: R.tag_image(d, W, H, 30)
    elif caption: cap(im, caption)
    R.note(d, W, H, 26); return im
def frame(t):
    if t < 0.3:   # 結果のチラ見せ
        im = R.darkbg(W, H, (40, 36, 20)).copy(); d = ImageDraw.Draw(im)
        ctext(d, (540, 820), '賞金', Mi(110), PALE, sw=4); ctext(d, (540, 1000), '100万ユーロ', Mi(150), GOLD, sw=5); return fin(im, t)
    if t < S1:   # 最初の1秒：衝撃の数字
        im = kb('09.jpg', W, H, t / S1, bright=1.0, blue=0.2, z0=1.0, z1=1.08, cx0=0.45, cx1=0.45)
        alpha_text(im, (540, 250), 'ドイツの', Mi(80), PALE, 1.0); alpha_text(im, (540, 420), '人口34万人', Mi(150), GOLD, 1.0)
        alpha_text(im, (540, 580), 'の町が', Mi(100), PALE, 1.0); alpha_text(im, (540, 1450), '存在しない？', Mi(150), PALE, ap(t, 0.9, 0.3))
        return fin(im, t, 0.1, caption='写真：ビーレフェルトの城')
    if t < S2:
        tn = at('v1', '一九九四年', S1)
        if t < tn:
            im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease((t - S1) / (tn - S1))
            P = B.europe(im, 540, 900, 90 + 160 * u, lat0=51.5 + 0.5 * u, lon0=10.0 - 1.4 * u); x, y = P(*B.BIE); d = ImageDraw.Draw(im, 'RGBA')
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=GOLD + (255,)); alpha_text(im, (x, y - 90), 'ビーレフェルト', Mi(90), GOLD, 1.0)
            alpha_text(im, (540, 300), 'ドイツの町', Mi(90), PALE, ap(t, S1))
            ImageDraw.Draw(im).text((24, 1830), '地図：Natural Earth', font=Fb(24), fill=(180, 185, 195))
            return fin(im, t, 0.1)
        im = kb('02.jpg', W, H, (t - tn) / (S2 - tn), bright=0.4, blue=0.4, z0=1.1, z1=1.2, blur=3)
        alpha_text(im, (540, 330), '1994年', Mi(150), GOLD, ap(t, tn))
        a = ap(t, at('v1', 'ネット', S1)); B.terminal(im, 90, 620, 900, 520, ['de.talk.bizarre', '16 May 1994', 'Subject: Bielefeld'], t, at('v1', 'ネット', S1), cps=24, a=a)
        alpha_text(im, (540, 1300), 'ネットに現れた 書きこみ', Mi(76), PALE, a)
        return fin(im, t, 0.15, caption='写真：昔のビーレフェルトの通り')
    if t < S3:
        im = kb('06.jpg', W, H, (t - S2) / (S3 - S2), bright=0.4, z0=1.0, z1=1.12, blur=3)
        Q = [('知っている？', 'ビーレフェルトの人を', 'ビーレフェルトの人'), ('行ったことがある？', 'ビーレフェルトに', '行ったこと'), ('行った人を知ってる？', 'ビーレフェルトに', '三つとも')]
        for i, (q, sub, k) in enumerate(Q):
            a = ap(t, at('v2', k, S2) - (0.6 if i == 2 else 0))
            if a > 0:
                y = 300 + i * 260; d = ImageDraw.Draw(im, 'RGBA'); d.rounded_rectangle((70, y, 1010, y + 220), 24, fill=(8, 12, 22, int(215 * a)), outline=GOLD + (int(255 * a),), width=4)
                alpha_text(im, (110, y + 65), f'{i + 1}. {sub}', Mi(46), GREY, a, anchor='lm', sw=0); alpha_text(im, (110, y + 150), q, Mi(70), PALE, a, anchor='lm')
        ti = at('v2', '三つとも', S2)
        alpha_text(im, (540, 1180), '3つとも「いいえ」なら', Mi(76), ICE, ap(t, ti)); alpha_text(im, (540, 1360), '存在しない', Mi(140), GOLD, ap(t, at('v2', 'この町', S2)))
        return fin(im, t, 0.15, caption='写真：ビーレフェルトの公園')
    if t < END0:
        im = kb('04.jpg', W, H, (t - S3) / (END0 - S3), bright=0.55, blue=0.3, z0=1.0, z1=1.15, cx0=0.48, cx1=0.48)
        alpha_text(im, (540, 300), '25年後', Mi(110), GREY, ap(t, S3))
        tm = at('v3', '賞金', S3); a = ap(t, tm, 0.3)
        if a > 0:
            v = int(1_000_000 * ease((t - tm) / 1.4)); alpha_text(im, (540, 520), '賞金', Mi(90), PALE, a); alpha_text(im, (540, 690), f'{v:,}ユーロ', Mi(120), GOLD, a)
        alpha_text(im, (540, 1350), '「存在しないと', Mi(96), PALE, ap(t, at('v3', '存在', S3))); alpha_text(im, (540, 1500), '証明してみろ」', Mi(96), PALE, ap(t, at('v3', '証明', S3)))
        return fin(im, t, 0.15, caption='写真：ビーレフェルトの城')
    im = R.darkbg(W, H, (20, 28, 44)).copy(); q = t - END0
    alpha_text(im, (540, 330), '証明できた人は', Mi(100), PALE, ap(q, 0)); alpha_text(im, (540, 480), 'いたのか？', Mi(130), GOLD, ap(q, 0.2))
    d = ImageDraw.Draw(im, 'RGBA')
    for i, o in enumerate(['いた', 'いなかった']):
        a = ap(q, 0.8 + i * 0.3)
        if a > 0:
            x = 540 + (i - 0.5) * 440; d.rounded_rectangle((x - 190, 640, x + 190, 760), 22, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x, 700), o, Mi(60), PALE + (int(255 * a),))
    if t < TH:
        B.eyes(im, t, 8, 1.0, seed=3)
        alpha_text(im, (540, 1450), '答えは 画面の下の', Fo(64), PALE, ap(t, at('vcta', '答え', TC))); alpha_text(im, (540, 1560), '関連動画で ↓', Fo(76), GOLD, ap(t, at('vcta', '答え', TC) + 0.2))
    else:   # 本編の横サムネを小さく
        th = Image.open(f'{G}/bie_thumb.jpg').resize((680, 383)); a = ap(t, TH, 0.3)
        d.rounded_rectangle((540 - 350, 1120 - 8, 540 + 350, 1120 + 383 + 8), 14, fill=(255, 210, 80, int(255 * a)))
        im.paste(th, (200, 1120)); alpha_text(im, (540, 1600), '↓ 続きは本編で', Mi(80), GOLD, a)
    return fin(im, t, 0.2)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for tt in [0.1, 1.5, 4, 7, 11, 15, 19, 23, 27, TH + 1]: frame(tt).resize((540, 960)).save(f'{G}/still/s_{tt:05.1f}.jpg')
        print(dur); sys.exit()
    json.dump({'dur': dur, 'cues': CUES, 'S': [S1, S2, S3, END0, TC, TH]}, open(f'{G}/s_meta.json', 'w'))
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for i in range(int(round(dur * 30))): p.stdin.write(frame(i / 30).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('short', dur)
