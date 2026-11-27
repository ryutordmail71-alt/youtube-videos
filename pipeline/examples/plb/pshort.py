"""縦型ショート（最初の1秒＝問いの文字：E1-A、9時枠）"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, GREY, CYAN, ICE, ctext, ease, fade, kb, fog, vignette, cabinet, alpha_text
import pcont as C
W, H = 1080, 1920; G = '/home/claude/plb'; D = json.load(open(f'{G}/dur.json'))
PL = f'{G}/ph/p_d1a8.jpg'
def at(key, sub, t0): s = C.NAR[key]; return t0 + D[key] * s.index(sub) / len(s)
S1 = 3.4; S2 = S1 + D['v1'] + 0.35; S3 = S2 + D['v2'] + 0.35; END0 = S3 + D['v3'] + 0.4
TC = END0 + 0.3; TH = TC + D['vcta'] + 0.3; dur = TH + 2.2
CUES = [(0.15, 'vhook'), (S1, 'v1'), (S2, 'v2'), (S3, 'v3'), (TC, 'vcta')]
def ap(t, t0, d=0.4): return ease((t - t0) / d)
def fin(im, t, k=0.2, tag=False):
    fog(im, t, k); vignette(im, 0.7); d = ImageDraw.Draw(im, 'RGBA')
    if tag: R.tag_image(d, W, H, 30)
    R.note(d, W, H, 26); return im
def frame(t):
    if t < 0.3:   # 結果のチラ見せ
        im = R.darkbg(W, H, (30, 40, 60)).copy(); cabinet(im, 540, 1500, 900, t, 1.0, 0.45); ctext(ImageDraw.Draw(im), (540, 420), '…消えた', Mi(110), PALE, sw=5); return fin(im, t)
    if t < S1:
        im = kb('06.jpg', W, H, t / S1, bright=0.8, z0=1.0, z1=1.08, cx0=0.62, cx1=0.62); cabinet(im, 540, 1560, 980, t, 1.0)
        alpha_text(im, (540, 260), '遊ぶと', Mi(120), PALE, 1.0); alpha_text(im, (540, 420), 'おかしくなる', Mi(140), GOLD, 1.0); alpha_text(im, (540, 570), 'ゲームがあった？', Mi(110), PALE, 1.0)
        return fin(im, t, 0.15, True)
    if t < S2:
        q = t - S1; tc = at('v1', 'ゲームセンター', S1)
        if t < tc:
            im = kb(PL, W, H, q / (tc - S1), bright=0.85, z0=1.0, z1=1.12, cx0=0.4, cx1=0.5)
            alpha_text(im, (540, 300), '1981年', Mi(130), GOLD, ap(t, S1)); alpha_text(im, (540, 460), 'アメリカ・ポートランド', Mi(84), PALE, ap(t, at('v1', 'ポート', S1)))
            alpha_text(im, (540, 1650), '（写真：いまのポートランド）', Fo(36), GREY, 1.0, sw=0)
            return fin(im, t, 0.12)
        im = kb('06.jpg', W, H, (t - tc) / (S2 - tc), bright=0.5, z0=1.1, z1=1.2, cx0=0.5, cx1=0.6); cabinet(im, 540, 1600, 900, t, ap(t, tc + 0.4, 1.0), ap(t, tc, 0.8))
        alpha_text(im, (540, 330), 'ゲームセンターに', Mi(84), PALE, ap(t, tc)); alpha_text(im, (540, 480), '名前のない 黒いゲーム機', Mi(84), GOLD, ap(t, at('v1', '名前', S1)))
        return fin(im, t, 0.2, True)
    if t < S3:
        im = kb('02.jpg', W, H, (t - S2) / (S3 - S2), bright=0.55, z0=1.0, z1=1.12, cx0=0.55, cx1=0.45)
        alpha_text(im, (540, 300), '遊んだ子どもたちは…', Mi(76), PALE, ap(t, S2))
        alpha_text(im, (540, 700), 'こわい夢', Mi(150), ICE, ap(t, at('v2', 'こわい', S2))); alpha_text(im, (540, 920), '眠れない', Mi(150), ICE, ap(t, at('v2', '眠れ', S2)))
        return fin(im, t, 0.2, True)
    if t < END0:
        tg = at('v3', 'そして', S3)
        if t < tg:
            im = kb('04.jpg', W, H, (t - S3) / (tg - S3), bright=0.6, z0=1.0, z1=1.25, cx0=0.45, cx1=0.55)
            R.glow(im, W * (0.5 + 0.3 * math.sin(t * 0.9)), H * 0.55, 300, (230, 220, 180), 70)
            alpha_text(im, (540, 300), '夜になると…', Mi(80), GREY, ap(t, S3)); alpha_text(im, (540, 450), '黒い服の男たち', Mi(110), PALE, ap(t, at('v3', '黒い', S3)))
            alpha_text(im, (540, 1300), '何かの「記録」だけを', Mi(80), GOLD, ap(t, at('v3', '何かの', S3))); alpha_text(im, (540, 1430), '持ち帰った', Mi(80), GOLD, ap(t, at('v3', '持ち', S3)))
            return fin(im, t, 0.2, True)
        im = R.darkbg(W, H, (16, 22, 36)).copy(); cabinet(im, 540, 1500, 900, t, 0.9, 1 - ease((t - tg - 0.8) / 2.0))
        alpha_text(im, (540, 330), '数週間後', Mi(100), GREY, ap(t, tg)); alpha_text(im, (540, 480), 'ゲーム機は 消えた', Mi(110), PALE, ap(t, at('v3', 'ゲーム機', S3)))
        return fin(im, t, 0.3)
    # エンドカード
    im = R.darkbg(W, H, (20, 28, 44)).copy(); cabinet(im, 540, 1250, 560, t, 0.5, 0.35)
    q = t - END0
    alpha_text(im, (540, 330), 'このゲームは', Mi(100), PALE, ap(q, 0)); alpha_text(im, (540, 480), '本当にあったのか？', Mi(110), GOLD, ap(q, 0.2))
    d = ImageDraw.Draw(im, 'RGBA')
    for i, o in enumerate(['あった', 'なかった']):
        a = ap(q, 0.8 + i * 0.3)
        if a > 0:
            x = 540 + (i - 0.5) * 420; d.rounded_rectangle((x - 180, 640, x + 180, 760), 22, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x, 700), o, Mi(60), PALE + (int(255 * a),))
    if t < TH:
        alpha_text(im, (540, 1450), '答えは 画面の下の', Fo(64), PALE, ap(t, at('vcta', '答え', TC))); alpha_text(im, (540, 1560), '関連動画で ↓', Fo(76), GOLD, ap(t, at('vcta', '答え', TC) + 0.2))
    else:   # 本編の横サムネを小さく
        th = Image.open(f'{G}/plb_thumb.jpg').resize((680, 383)); a = ap(t, TH, 0.3)
        d.rounded_rectangle((540 - 350, 1120 - 8, 540 + 350, 1120 + 383 + 8), 14, fill=(255, 210, 80, int(255 * a)))
        im.paste(th, (200, 1120)); alpha_text(im, (540, 1600), '↓ 続きは本編で', Mi(80), GOLD, a)
    return fin(im, t, 0.2)
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for tt in [0.1, 1.5, 4, 9, 13, 17, 21, 25, TH + 1]: frame(tt).resize((540, 960)).save(f'{G}/still/s_{tt:.1f}.jpg')
        print(dur); sys.exit()
    json.dump({'dur': dur, 'cues': CUES, 'S': [S1, S2, S3, END0, TC, TH]}, open(f'{G}/s_meta.json', 'w'))
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for i in range(int(round(dur * 30))): p.stdin.write(frame(i / 30).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('short', dur)
