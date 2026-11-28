"""縦型ショート（9時枠：E1-A＝最初の1秒に結論を伏せた問いの文字）"""
import json, math, sys
from PIL import Image, ImageDraw
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, GREY, CYAN, ICE, RED, ctext, ease, fade, kb, fog, vignette, alpha_text
import tdraw as T
import pcont as C
W, H = 1080, 1920; G = '/home/claude/tkc'; D = json.load(open(f'{G}/dur.json'))
def at(key, sub, t0): s = C.NAR[key]; return t0 + D[key] * s.index(sub) / len(s)
S1 = D['vhook'] + 0.45; S2 = S1 + D['v1'] + 0.6; S3 = S2 + D['v2'] + 0.6; END0 = S3 + D['v3'] + 0.7
TC = END0 + 0.2; TH = TC + D['vcta'] + 0.3; dur = TH + 2.5
CUES = [(0.15, 'vhook'), (S1, 'v1'), (S2, 'v2'), (S3, 'v3'), (TC, 'vcta')]
def ap(t, t0, d=0.4): return ease((t - t0) / d)
def cap(im, s): ImageDraw.Draw(im).text((W - 24, 40), s, font=Fb(24), fill=(225, 228, 235), anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
def fin(im, t, k=0.2, caption=None):
    fog(im, t, k); vignette(im, 0.7); d = ImageDraw.Draw(im, 'RGBA')
    if caption: cap(im, caption)
    R.note(d, W, H, 26); return im
def doorv(t, u, open_u, bright=0.55):
    im = kb('passage2.jpg', W, H, u, bright=bright, blue=0.45, z0=1.0, z1=1.1, cx0=0.4, cx1=0.42)
    T.door(im, 540, 1450, 820, open_u); return im
def frame(t):
    if t < 0.3:   # 結果のチラ見せ：少し開いた扉
        im = doorv(t, 0.5, 0.6, 0.5); return fin(im, t, 0.05)
    if t < S1:   # 最初の1秒：問いの文字（明るく）
        im = kb('diet2.jpg', W, H, t / 6, bright=1.0, blue=0.15, z0=1.0, z1=1.06, cx0=0.5, cx1=0.5)
        alpha_text(im, (540, 300), '国会議事堂の地下に', Mi(92), PALE, 1.0)
        alpha_text(im, (540, 1350), '地図にない', Mi(110), PALE, 1.0)
        alpha_text(im, (540, 1510), '秘密の通路がある？', Mi(104), GOLD, 1.0)
        return fin(im, t, 0.05, '写真：国会議事堂 っ／Wikimedia Commons')
    if t < S2:
        tp = at('v1', '国会議事堂前駅', S1); td = at('v1', '三十八', S1); tm = at('v1', '東京メトロ', S1)
        if t < tp:
            im = kb('diet_day.jpg', W, H, (t - S1) / 4, bright=0.75, blue=0.3, z0=1.0, z1=1.1, cx0=0.4, cx1=0.42)
            alpha_text(im, (540, 300), '東京・永田町', Mi(110), GOLD, ap(t, S1)); return fin(im, t, 0.08, '写真：夜の永田町と国会議事堂 Daderot')
        if t < td:
            im = kb('kplat.jpg', W, H, (t - tp) / 3, bright=0.6, blue=0.4, z0=1.0, z1=1.1, cx0=0.55, cx1=0.6)
            alpha_text(im, (540, 300), '国会議事堂前駅', Mi(104), PALE, ap(t, tp)); alpha_text(im, (540, 440), '千代田線のホーム', Mi(76), ICE, ap(t, tp + 0.3))
            return fin(im, t, 0.1, '写真：国会議事堂前駅 千代田線ホーム LERK')
        im = Image.new('RGB', (W, H)); T.section(im, -60, 520, 26, t, show=('chiyoda', 'bldg'), chi_u=(t - td) / 1.5, labels=False)
        alpha_text(im, (540, 200), '地下 およそ', Mi(80), PALE, ap(t, td)); alpha_text(im, (540, 370), '38m', Mi(200), GOLD, ap(t, td + 0.2))
        alpha_text(im, (540, 1700), '東京メトロで いちばん深い', Mi(68), GOLD, ap(t, tm))
        return fin(im, t, 0.0, '図：簡単にした断面（ビル12階ぶんの目安つき）')
    if t < S3:
        im = kb('esc.jpg', W, H, (t - S2) / 4.5, bright=0.55, blue=0.45, z0=1.2, z1=1.3, cx0=0.5, cx1=0.5, cy0=0.8, cy1=0.85)
        alpha_text(im, (540, 380), 'こんなに深いのは', Mi(84), PALE, ap(t, S2)); alpha_text(im, (540, 1300), 'いざというときの', Mi(84), PALE, ap(t, at('v2', 'いざ', S2)))
        alpha_text(im, (540, 1460), 'シェルターだから？', Mi(100), GOLD, ap(t, at('v2', 'シェルター', S2), 0.3))
        return fin(im, t, 0.12, '写真：永田町駅のエスカレーター 本屋')
    if t < END0:
        im = doorv(t, (t - S3) / 4, 0.0)
        alpha_text(im, (540, 300), '駅のはしには', Mi(90), PALE, ap(t, S3)); alpha_text(im, (540, 440), 'いつも閉まったままの扉', Mi(80), GOLD, ap(t, at('v3', 'いつも', S3)))
        return fin(im, t, 0.12, '扉の絵：イメージ 写真：虎ノ門の地下通路 Real Estate Japan')
    q = t - END0
    im = doorv(t, 0.8, 0.25 * ap(q, 0, 1.5), 0.35)
    alpha_text(im, (540, 300), 'その扉の先には', Mi(96), PALE, ap(q, 0)); alpha_text(im, (540, 450), '何がある？', Mi(130), GOLD, ap(q, 0.2))
    if t < TH:
        d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 1480, W, 1720), fill=(0, 0, 0, 150))
        alpha_text(im, (540, 1550), '答えは 画面の下の', Fo(64), PALE, ap(t, at('vcta', '答え', TC))); alpha_text(im, (540, 1650), '関連動画で ↓', Fo(76), GOLD, ap(t, at('vcta', '答え', TC) + 0.2))
    else:
        th = Image.open(f'{G}/tkc_thumb.jpg').resize((680, 383)); a = ap(t, TH, 0.3); d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle((0, 1080, W, 1720), fill=(0, 0, 0, int(160 * a)))
        d.rounded_rectangle((540 - 350, 1120 - 8, 540 + 350, 1120 + 383 + 8), 14, fill=(255, 210, 80, int(255 * a)))
        im.paste(th, (200, 1120)); alpha_text(im, (540, 1600), '↓ 続きは本編で', Mi(80), GOLD, a)
    return fin(im, t, 0.15, '扉の絵：イメージ 写真：虎ノ門の地下通路 Real Estate Japan')
if __name__ == '__main__':
    if len(sys.argv) > 1:
        from PIL import Image as I
        ts = [0.1, 1.0, S1 + 1, S1 + 4, S1 + 7.5, S2 + 1, S2 + 3.5, S3 + 2, END0 + 1.5, TC + 3, TH + 1.5, dur - 0.1]
        sh = I.new('RGB', (6 * 360, 2 * 640))
        for i, tt in enumerate(ts): sh.paste(frame(tt).convert('RGB').resize((360, 640)), ((i % 6) * 360, (i // 6) * 640))
        sh.save(f'{G}/still/short.jpg', quality=85); print(dur); sys.exit()
    json.dump({'dur': dur, 'cues': CUES, 'S': [S1, S2, S3, END0, TC, TH]}, open(f'{G}/s_meta.json', 'w'))
    p = R.writer(f'{G}/s_video.mp4', W, H)
    for i in range(int(round(dur * 30))): p.stdin.write(frame(i / 30).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('short', dur)
