"""縦型ショート（20時枠：E1-A＝最初の1秒に結論を伏せた問いの文字）"""
import json, math, sys
from PIL import Image, ImageDraw
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, GREY, CYAN, ICE, RED, ctext, ease, fade, kb, fog, vignette, alpha_text
import mdraw as M
import pcont as C
W, H = 1080, 1920; G = '/home/claude/mbe'; D = json.load(open(f'{G}/dur.json'))
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
def frame(t):
    if t < 0.3:   # 結果のチラ見せ
        im = M.window(W, H, t + 2, '16.jpg', 0.45); ctext(ImageDraw.Draw(im), (540, 960), '幻の駅', Mi(190), GOLD, sw=5); return fin(im, t, 0.1)
    if t < S1:   # 最初の1秒：問いの文字
        im = M.window(W, H, t, '16.jpg', (t - 0.1) / 3.6)
        alpha_text(im, (540, 330), '地下鉄の窓に', Mi(90), PALE, 1.0); alpha_text(im, (540, 480), '一瞬だけ見える', Mi(90), PALE, 1.0)
        alpha_text(im, (540, 1380), 'だれもいない', Mi(120), GOLD, 1.0); alpha_text(im, (540, 1540), 'ホームの正体は？', Mi(110), GOLD, 1.0)
        return fin(im, t, 0.1, '絵：電車の窓（イメージ）写真：東京ではありません')
    if t < S2:
        im = kb('02c.jpg', W, H, (t - S1) / (S2 - S1), bright=0.5, blue=0.45, z0=1.0, z1=1.1, blur=2)
        alpha_text(im, (540, 300), '東京の 銀座線', Mi(90), PALE, ap(t, S1))
        alpha_text(im, (540, 450), '神田〜末広町のあいだ', Mi(76), ICE, ap(t, at('v1', '神田', S1)))
        alpha_text(im, (540, 1150), '2年たらずで消えた', Mi(90), PALE, ap(t, at('v1', '二年', S1)))
        alpha_text(im, (540, 1320), '万世橋駅', Mi(150), GOLD, ap(t, at('v1', '万世橋', S1)))
        alpha_text(im, (540, 1470), '1930年1月〜1931年11月', Fo(56), ICE, ap(t, at('v1', '万世橋', S1) + 0.3))
        return fin(im, t, 0.15, '写真：日本の駅のホーム（イメージ）')
    if t < S3:
        im = kb('05.jpg', W, H, (t - S2) / (S3 - S2), bright=0.5, blue=0.4, z0=1.0, z1=1.12)
        alpha_text(im, (540, 300), '新橋の地下には', Mi(90), PALE, ap(t, S2)); alpha_text(im, (540, 450), 'もう一つの新橋駅', Mi(96), ICE, ap(t, S2 + 0.5))
        tm = at('v2', '使われた', S2); a = ap(t, tm)
        if a > 0: M.months(im, 60, 1000, 960, (t - tm) / 1.6, a)
        alpha_text(im, (540, 1320), 'わずか 8か月', Mi(140), GOLD, ap(t, at('v2', 'わずか', S2), 0.3))
        alpha_text(im, (540, 1460), '1939年1月15日〜9月15日', Fo(52), PALE, ap(t, at('v2', 'わずか', S2) + 0.3))
        return fin(im, t, 0.15, '写真：地下鉄のトンネル（イメージ）')
    if t < END0:
        im = kb('21c.jpg', W, H, (t - S3) / (END0 - S3), bright=0.5, blue=0.4, z0=1.0, z1=1.15)
        alpha_text(im, (540, 330), '上野の地下にも', Mi(100), PALE, ap(t, S3))
        alpha_text(im, (540, 1250), '電車が止まらなくなった', Mi(84), ICE, ap(t, at('v3', '電車', S3)))
        alpha_text(im, (540, 1400), '駅が眠っている', Mi(110), GOLD, ap(t, at('v3', '眠って', S3)))
        return fin(im, t, 0.15, '写真：使われなくなった地下の駅（イメージ：東京ではありません）')
    im = R.darkbg(W, H, (20, 28, 44)).copy(); q = t - END0
    alpha_text(im, (540, 330), 'その駅は いま', Mi(100), PALE, ap(q, 0)); alpha_text(im, (540, 480), 'どうなっている？', Mi(120), GOLD, ap(q, 0.2))
    if t < TH:
        alpha_text(im, (540, 1450), '答えは 画面の下の', Fo(64), PALE, ap(t, at('vcta', '答え', TC))); alpha_text(im, (540, 1560), '関連動画で ↓', Fo(76), GOLD, ap(t, at('vcta', '答え', TC) + 0.2))
        M.line_map(im, t, -900, 2200, 900, a=ap(q, 0.3), labels=False, ghosts=[('shinbashi', 1.0), ('mansei', 1.0)])
    else:
        th = Image.open(f'{G}/mbe_thumb.jpg').resize((680, 383)); a = ap(t, TH, 0.3); d = ImageDraw.Draw(im, 'RGBA')
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
