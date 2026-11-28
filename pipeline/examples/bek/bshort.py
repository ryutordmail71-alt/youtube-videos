"""縦型ショート（4時枠：E1-B＝最初の1秒にいちばん衝撃的な一言「白目がない」）"""
import json, math, sys
from PIL import Image, ImageDraw
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, GREY, CYAN, ICE, RED, ctext, ease, fade, kb, fog, vignette, alpha_text
import bdraw as B
import pcont as C
W, H = 1080, 1920; G = '/home/claude/bek'; D = json.load(open(f'{G}/dur.json'))
def at(key, sub, t0): s = C.NAR[key]; return t0 + D[key] * s.index(sub) / len(s)
S1 = D['vhook'] + 0.5; S2 = S1 + D['v1'] + 0.35; S3 = S2 + D['v2'] + 0.35; END0 = S3 + D['v3'] + 0.6
TC = END0 + 0.3; TH = TC + D['vcta'] + 0.3; dur = TH + 2.2
CUES = [(0.15, 'vhook'), (S1, 'v1'), (S2, 'v2'), (S3, 'v3'), (TC, 'vcta')]
def ap(t, t0, d=0.4): return ease((t - t0) / d)
def cap(im, s): ImageDraw.Draw(im).text((W - 24, 40), s, font=Fb(24), fill=(225, 228, 235), anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
def fin(im, t, k=0.2, caption=None):
    fog(im, t, k); vignette(im, 0.7); d = ImageDraw.Draw(im, 'RGBA')
    if caption: cap(im, caption)
    R.note(d, W, H, 26); return im
def frame(t):
    if t < 0.3:   # 結果のチラ見せ：うわさの目
        im = R.darkbg(W, H, (30, 36, 54)).copy(); B.eye(im, 540, 900, 900, 'black'); return fin(im, t, 0.05)
    if t < S1:   # 最初の1秒：いちばん衝撃的な一言（最初から明るく）
        im = kb('door1.jpg', W, H, t / 5, bright=0.95, blue=0.25, z0=1.0, z1=1.08)
        B.knock(im, 540, 900, t, 0.35, label=False)
        alpha_text(im, (540, 330), '夜、ドアをたたく', Mi(96), PALE, 1.0); alpha_text(im, (540, 470), '子どもの目に', Mi(96), PALE, 1.0)
        alpha_text(im, (540, 1360), '白目が ない', Mi(160), GOLD, 1.0)
        return fin(im, t, 0.06, '写真：夜の玄関（イメージ）HABS')
    if t < S2:
        tk = at('v1', 'コン', S1); tb = at('v1', '立って', S1)
        if t < tk:
            im = kb('para1.jpg', W, H, (t - S1) / (tk - S1 + 1), bright=0.5, blue=0.5, z0=1.0, z1=1.1, cx0=0.3, cx1=0.4)
            alpha_text(im, (540, 300), 'アメリカ・テキサス州', Mi(84), PALE, ap(t, S1)); alpha_text(im, (540, 1400), '映画館の駐車場', Mi(100), GOLD, ap(t, at('v1', '映画館', S1)))
            return fin(im, t, 0.1, '写真：アビリーンの映画館（話の映画館とは限りません）Billy Hathorn')
        im = kb('park3.jpg', W, H, (t - tk) / (S2 - tk), bright=0.6, blue=0.4, z0=1.0, z1=1.1)
        if t > tb: B.kids(im, 540, 1250, 520, ap(t, tb, 0.8), t)
        B.carwin(im); B.knock(im, 540, 800, t, tk, label=False)
        alpha_text(im, (540, 300), '車の窓が コン、コン', Mi(88), PALE, ap(t, tk)); alpha_text(im, (540, 1450), '二人の男の子', Mi(110), GOLD, ap(t, tb))
        return fin(im, t, 0.12, '影の絵：うわさの姿のイメージ 写真：霧の夜の駐車場（イメージ）')
    if t < S3:
        te = at('v2', 'その目', S2)
        if t < te:
            im = kb('park3.jpg', W, H, (t - S2) / 3, bright=0.45, blue=0.45, z0=1.15, z1=1.2, blur=2); B.kids(im, 540, 1250, 520, 1.0, t); B.carwin(im)
            alpha_text(im, (540, 380), '「家まで', Mi(110), PALE, ap(t, S2)); alpha_text(im, (540, 540), '乗せてくれない？」', Mi(100), GOLD, ap(t, S2 + 0.4))
            return fin(im, t, 0.15, '影の絵：うわさの姿のイメージ 写真：霧の夜の駐車場（イメージ）')
        im = R.darkbg(W, H, (18, 24, 38)).copy(); B.eye(im, 540, 800, 860, 'black', ap(t, te, 0.6))
        alpha_text(im, (540, 380), 'その目は', Mi(90), PALE, ap(t, te)); alpha_text(im, (540, 1200), 'まぶたから', Mi(100), PALE, ap(t, at('v2', 'まぶた', S2)))
        alpha_text(im, (540, 1350), 'まぶたまで 真っ黒', Mi(110), GOLD, ap(t, at('v2', '真っ黒', S2)))
        return fin(im, t, 0.08, '目の図：うわさをもとにしたイメージ')
    if t < END0:
        im = kb('door1.jpg', W, H, (t - S3) / 3, bright=0.55, blue=0.4, z0=1.1, z1=1.2)
        alpha_text(im, (540, 420), '「きみが', Mi(110), PALE, ap(t, S3)); alpha_text(im, (540, 580), 'いいよと言わないと', Mi(96), PALE, ap(t, at('v3', 'いいよ', S3)))
        alpha_text(im, (540, 1380), '入れないんだ」', Mi(118), GOLD, ap(t, at('v3', '入れない', S3), 0.3))
        return fin(im, t, 0.12, '写真：夜の玄関（イメージ）HABS')
    im = R.darkbg(W, H, (20, 28, 44)).copy(); q = t - END0
    alpha_text(im, (540, 330), 'このあと', Mi(110), PALE, ap(q, 0)); alpha_text(im, (540, 480), 'どうなった？', Mi(130), GOLD, ap(q, 0.2))
    if t < TH:
        B.kids(im, 540, 1250, 460, ap(q, 0.2, 0.8) * 0.9, t)
        alpha_text(im, (540, 1450), '答えは 画面の下の', Fo(64), PALE, ap(t, at('vcta', '答え', TC))); alpha_text(im, (540, 1560), '関連動画で ↓', Fo(76), GOLD, ap(t, at('vcta', '答え', TC) + 0.2))
    else:
        th = Image.open(f'{G}/bek_thumb.jpg').resize((680, 383)); a = ap(t, TH, 0.3); d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((540 - 350, 1120 - 8, 540 + 350, 1120 + 383 + 8), 14, fill=(255, 210, 80, int(255 * a)))
        im.paste(th, (200, 1120)); alpha_text(im, (540, 1600), '↓ 続きは本編で', Mi(80), GOLD, a)
    return fin(im, t, 0.2)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for tt in [0.1, 1.0, 3.5, 6, 9, 12, 15, 18, 21, 24, 27, TH + 1]: frame(tt).resize((540, 960)).save(f'{G}/still/s_{tt:05.1f}.jpg')
        print(dur); sys.exit()
    json.dump({'dur': dur, 'cues': CUES, 'S': [S1, S2, S3, END0, TC, TH]}, open(f'{G}/s_meta.json', 'w'))
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for i in range(int(round(dur * 30))): p.stdin.write(frame(i / 30).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('short', dur)
