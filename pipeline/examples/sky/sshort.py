"""縦型ショート（0時枠：E1-A＝最初の1秒に結論を伏せた問いの文字）"""
import json, math, sys
from PIL import Image, ImageDraw
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, GREY, CYAN, ICE, RED, ctext, ease, fade, kb, fog, vignette, alpha_text
import sdraw as S
import pcont as C
W, H = 1080, 1920; G = '/home/claude/sky'; D = json.load(open(f'{G}/dur.json'))
def at(key, sub, t0): s = C.NAR[key]; return t0 + D[key] * s.index(sub) / len(s)
S1 = D['vhook'] + 0.5; S2 = S1 + D['v1'] + 0.35; S3 = S2 + D['v2'] + 0.35; END0 = S3 + D['v3'] + 0.4
TC = END0 + 0.3; TH = TC + D['vcta'] + 0.3; dur = TH + 2.2
CUES = [(0.15, 'vhook'), (S1, 'v1'), (S2, 'v2'), (S3, 'v3'), (TC, 'vcta')]
def ap(t, t0, d=0.4): return ease((t - t0) / d)
def cap(im, s): ImageDraw.Draw(im).text((W - 24, 40), s, font=Fb(24), fill=(225, 228, 235), anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
def fin(im, t, k=0.2, caption=None):
    fog(im, t, k); vignette(im, 0.7); d = ImageDraw.Draw(im, 'RGBA')
    if caption: cap(im, caption)
    R.note(d, W, H, 26); return im
CS = '絵：うわさの姿のイメージ 写真：夕方の空（イメージ）NASA'
def frame(t):
    if t < 0.3:   # 結果のチラ見せ：画面いっぱいのスカイフィッシュ
        im = kb('sky.jpg', W, H, 0.5, bright=0.75, blue=0.3, z0=1.0, z1=1.0); S.skyfish(im, 540, 960, -0.9, 1300, t * 10, 1.0); return fin(im, t, 0.05)
    if t < S1:   # 最初の1秒：問いの文字（最初から明るく）
        im = kb('sky.jpg', W, H, (t) / 4, bright=0.8, blue=0.3, z0=1.0, z1=1.08)
        u = (t - 0.3) / 0.5
        if 0 <= u <= 1: S.skyfish(im, -300 + 1700 * u, 1050 - 300 * u, -0.25, 600, t, 0.7)
        S.camui(im, t, 1000 + int(t * 30))
        alpha_text(im, (540, 380), '目には見えないのに', Mi(86), PALE, 1.0); alpha_text(im, (540, 520), 'カメラにだけ写る', Mi(96), PALE, 1.0)
        alpha_text(im, (540, 1400), '生き物がいる？', Mi(130), GOLD, 1.0)
        return fin(im, t, 0.08, CS)
    if t < S2:
        im = kb('sky.jpg', W, H, (t - S1) / (S2 - S1), bright=0.6, blue=0.4, z0=1.1, z1=1.2, cx0=0.3, cx1=0.6)
        alpha_text(im, (540, 280), '1994年', Mi(110), GOLD, ap(t, S1)); alpha_text(im, (540, 420), 'アメリカ・ニューメキシコ州', Mi(68), PALE, ap(t, S1 + 0.4))
        tf = at('v1', '一コマ', S1); src = R.photo('sky.jpg', 300, 190, bright=0.7, over=1.0)
        if t > tf - 0.5:
            fr = Image.new('RGB', (W, 600), (8, 8, 10)); S.filmstrip(fr, src, 60, 100, 3, 300, 190, 30, t, rod_u=-0.6 + (t - tf) * 0.45, a=1.0, hi=int((t - tf) * 3) % 3)
            im.paste(fr.crop((0, 40, W, 360)), (0, 700))
        alpha_text(im, (540, 1200), '一コマずつ見ると…', Mi(76), PALE, ap(t, tf))
        alpha_text(im, (540, 1380), '細長い「なにか」', Mi(110), GOLD, ap(t, at('v1', '細長い', S1)))
        return fin(im, t, 0.1, '絵：フィルムのコマのイメージ 写真：夕方の空（イメージ）NASA')
    if t < S3:
        im = kb('sky.jpg', W, H, (t - S2) / (S3 - S2), bright=0.45, blue=0.4, z0=1.2, z1=1.3, blur=3)
        S.skyfish(im, 540, 820, -0.5, 900, t * 0.7, ap(t, S2, 0.6))
        alpha_text(im, (540, 280), '体の両側に ゆれるヒレ', Mi(80), PALE, ap(t, S2))
        alpha_text(im, (540, 1300), '速すぎて 目では見えない', Mi(76), ICE, ap(t, at('v2', '速すぎて', S2)))
        alpha_text(im, (540, 1470), 'スカイフィッシュ', Mi(130), GOLD, ap(t, at('v2', 'その名', S2), 0.3))
        return fin(im, t, 0.12, CS)
    if t < END0:
        im = R.darkbg(W, H, (40, 52, 74)).copy(); ppm = 1.55
        xs, yb = S.pit(im, 700, 560, ppm, (t - S3 - 0.3) / 1.8, t, rev=(t - S3 - 0.3) / 1.8)
        for i in range(2):
            ph = (t - S3) * 0.4 + i * 0.5; ph -= math.floor(ph); S.skyfish(im, 640 - 150 + ph * 300, 560 + 260 + i * 160, 0.15, 130, t + i, 0.7)
        alpha_text(im, (540, 230), 'メキシコの縦穴', Mi(100), PALE, ap(t, S3))
        alpha_text(im, (xs - 20, 560 + 333 * ppm / 2), '333m', Mi(76), GOLD, ap(t, at('v3', '三百', S3) + 0.5), anchor='rm')
        at_ = ap(t, at('v3', '三百', S3) + 1.2, 0.6); S.tower(im, 190, 560 + 333 * ppm, 333 * ppm * 0.98, at_)
        alpha_text(im, (190, 560 + 333 * ppm + 45), '東京タワー', Fb(38), (235, 150, 110), at_)
        alpha_text(im, (540, 380), 'ここでも写った…？', Mi(80), GOLD, ap(t, at('v3', '写った', S3)))
        return fin(im, t, 0.06, '断面図は単純にした目安')
    im = R.darkbg(W, H, (20, 28, 44)).copy(); q = t - END0
    alpha_text(im, (540, 330), 'その正体は？', Mi(130), GOLD, ap(q, 0))
    if t < TH:
        for i in range(3):
            ph = (q * 0.5 + i * 0.33) % 1.0; S.skyfish(im, -200 + 1500 * ph, 700 + i * 160, -0.1, 360, t + i, 0.6)
        alpha_text(im, (540, 1450), '答えは 画面の下の', Fo(64), PALE, ap(t, at('vcta', '答え', TC))); alpha_text(im, (540, 1560), '関連動画で ↓', Fo(76), GOLD, ap(t, at('vcta', '答え', TC) + 0.2))
    else:
        th = Image.open(f'{G}/sky_thumb.jpg').resize((680, 383)); a = ap(t, TH, 0.3); d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((540 - 350, 1120 - 8, 540 + 350, 1120 + 383 + 8), 14, fill=(255, 210, 80, int(255 * a)))
        im.paste(th, (200, 1120)); alpha_text(im, (540, 1600), '↓ 続きは本編で', Mi(80), GOLD, a)
    return fin(im, t, 0.2)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for tt in [0.1, 1.5, 5, 9, 13, 17, 21, 24, 27, TH + 1]: frame(tt).resize((540, 960)).save(f'{G}/still/s_{tt:05.1f}.jpg')
        print(dur); sys.exit()
    json.dump({'dur': dur, 'cues': CUES, 'S': [S1, S2, S3, END0, TC, TH]}, open(f'{G}/s_meta.json', 'w'))
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for i in range(int(round(dur * 30))): p.stdin.write(frame(i / 30).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('short', dur)
