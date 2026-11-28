"""ビーレフェルト：本編の場面（python3 bscn.py main [still]）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, CYAN, ICE, ctext, ease, fade, kb, fog, vignette, alpha_text
import bdraw as B
import pcont as C
G = '/home/claude/bie'; D = json.load(open(f'{G}/dur.json')); W, H = 1920, 1080
def at(key, sub, pre):
    s = C.NAR[key]; i = s.index(sub); return pre + D[key] * i / len(s)
def appear(t, t0, d=0.5): return ease((t - t0) / d)
def header(im, no, title, t):
    a = appear(t, 0.0, 0.6); d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 0, W, 150), fill=(0, 0, 0, int(150 * a)))
    alpha_text(im, (70, 58), f'言い伝え その{no}', Fb(40), GOLD, a, anchor='lm', sw=0)
    alpha_text(im, (70, 112), title, Mi(54), PALE, a, anchor='lm', sw=0)
def bullet(im, x, y, txt, t, t0, f=None, col=PALE, anchor='lm'):
    a = appear(t, t0, 0.6)
    if a <= 0: return
    alpha_text(im, (x + (1 - a) * 30, y), txt, f or Mi(58), col, a, anchor=anchor)
def base_photo(name, t, T, dark=0.62, **kw): return kb(name, W, H, t / max(T, 1), bright=dark, **kw).copy()
def cap(im, s):
    d = ImageDraw.Draw(im, 'RGBA'); d.text((W - 24, 40), s, font=Fb(26), fill=(225, 228, 235), anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
def finish(im, gt, fogk=0.22, image_tag=False, caption=None):
    fog(im, gt, fogk); vignette(im, 0.8); d = ImageDraw.Draw(im, 'RGBA')
    if image_tag: R.tag_image(d, W, H)
    elif caption: cap(im, caption)
    R.note(d, W, H); return im
PB = '写真：ビーレフェルトの町'
def band(im, name, y, h, t, T, a=1.0):
    """横長の写真を帯で見せる（パノラマ）"""
    src = R.photo(name, W, h, bright=0.8, blue=0.25, over=1.0); u = t / max(T, 1)
    x0 = (src.width - W) * (0.2 + 0.6 * u)
    part = src.crop((int(x0), int((src.height - h) / 2), int(x0) + W, int((src.height - h) / 2) + h))
    if a < 1: im.paste(Image.blend(im.crop((0, y, W, y + h)), part, a), (0, y))
    else: im.paste(part, (0, y))
    d = ImageDraw.Draw(im, 'RGBA'); d.line((0, y, W, y), fill=GOLD + (int(160 * a),), width=2); d.line((0, y + h, W, y + h), fill=GOLD + (int(160 * a),), width=2)
# ---------- 各場面 ----------
def s_hook(t, T, gt, pre):
    if t < 0.3:   # 結果のチラ見せ
        im = R.darkbg(W, H, (40, 36, 20)).copy(); ctext(ImageDraw.Draw(im), (W / 2, 480), '賞金 100万ユーロ', Mi(150), GOLD, sw=4); ctext(ImageDraw.Draw(im), (W / 2, 680), '「存在しないと 証明せよ」', Mi(80), PALE, sw=3)
        return finish(im, gt, 0.2)
    im = base_photo('09.jpg', t, T, 1.0, blue=0.2, z0=1.0, z1=1.15, cx0=0.55, cx1=0.6)
    alpha_text(im, (110, 200), 'ドイツ', Mi(70), PALE, appear(t, 0.3, 0.3), anchor='lm')
    alpha_text(im, (110, 360), '人口 約34万人', Mi(140), GOLD, appear(t, 0.35, 0.3), anchor='lm')
    alpha_text(im, (110, 520), 'の大きな町が', Mi(90), PALE, appear(t, 0.35, 0.3), anchor='lm')
    alpha_text(im, (110, 680), '存在しない？', Mi(150), PALE, appear(t, at('hook', 'でも', pre), 0.4), anchor='lm')
    bullet(im, 110, 830, '言われ続けて 25年', t, at('hook', '二十五年', pre), Mi(66), ICE)
    bullet(im, 110, 940, 'ついに町が 賞金を出した', t, at('hook', 'ついに', pre), Mi(66), GOLD)
    return finish(im, gt, 0.12, caption='写真：ビーレフェルトのスパーレンブルク城')
def s_title(t, T, gt, pre):
    im = R.darkbg(W, H, (16, 26, 44)).copy(); band(im, '00.jpg', 560, 330, t, T, appear(t, 0.0, 1.0))
    alpha_text(im, (W / 2, 140), '都市伝説', Mi(64), GREY, appear(t, 0.1), sw=0)
    alpha_text(im, (W / 2, 300), 'ビーレフェルト', Mi(170), PALE, appear(t, 0.3, 0.8))
    alpha_text(im, (W / 2, 460), 'B I E L E F E L D', BE(100), GOLD, appear(t, 0.8, 0.8), sw=0)
    alpha_text(im, (W / 2, 960), 'ドイツでいちばん有名な「存在しない町」', Mi(58), PALE, appear(t, at('title', 'ドイツ', pre), 0.6))
    return finish(im, gt, 0.18, caption='写真：ビーレフェルトの町なみ')
def s_where(t, T, gt, pre):
    im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / 6.0)
    sc = 60 + 170 * u; lat0 = 51.0 + (51.9 - 51.0) * u; lon0 = 10.0 + (9.0 - 10.0) * u
    P = B.europe(im, W * 0.55, H * 0.55, sc, lat0=lat0, lon0=lon0); d = ImageDraw.Draw(im, 'RGBA')
    gx, gy = P(51.2, 10.6); alpha_text(im, (gx, gy), 'ドイツ', Mi(70 + 20 * u), PALE, appear(t, 0.3) * (1 - 0.6 * u), sw=0)
    nx, ny = P(51.85, 5.0); alpha_text(im, (nx, ny), 'オランダ', Fo(48), GREY, appear(t, at('where', 'オランダ', pre)))
    x, y = P(*B.BIE)
    a1 = appear(t, at('where', '東へ', pre))
    if a1 > 0:   # 国境からの矢印（約100km）
        bx, by = P(52.02, 7.05); d.line((bx, by, bx + (x - bx) * a1, y), fill=ICE + (230,), width=6)
        alpha_text(im, ((bx + x) / 2, by + 50), '約100km', Fo(46), ICE, a1)
    for nm, (la, lo) in B.CITIES.items():
        a = appear(t, at('where', nm if nm != 'ベルリン' else 'ハノーファー', pre))
        cx, cy = P(la, lo)
        if a > 0 and -50 < cx < W + 50:
            d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=GREY + (int(255 * a),))
            if nm == 'ハノーファー': alpha_text(im, (cx + 24, cy), nm, Fo(38), GREY, a, anchor='lm')
            else: alpha_text(im, (cx, cy + 45), nm, Fo(38), GREY, a)
    a3 = appear(t, 0.5)
    r = 20 + 10 * math.sin(gt * 3); d.ellipse((x - r, y - r, x + r, y + r), outline=GOLD + (int(255 * a3),), width=5); d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=GOLD + (int(255 * a3),))
    alpha_text(im, (x - 25, y - 60), 'ビーレフェルト', Mi(70), GOLD, a3, anchor='rm')
    tp = at('where', '人口は', pre); a4 = appear(t, tp)
    if a4 > 0:
        d.rounded_rectangle((70, 650, 700, 1000), 24, fill=(0, 0, 0, int(170 * a4)), outline=GOLD + (int(200 * a4),), width=3)
        alpha_text(im, (110, 720), '人口', Mi(50), PALE, a4, anchor='lm'); alpha_text(im, (110, 820), '約34万人', Mi(110), GOLD, a4, anchor='lm')
        bullet(im, 110, 940, 'ドイツで上から20番目くらい', t, at('where', 'ドイツでは', pre), Mi(44), ICE)
    alpha_text(im, (W / 2, 70), 'ドイツの北西部', Mi(60), PALE, appear(t, 0.3), sw=0)
    im = finish(im, gt, 0.1); ImageDraw.Draw(im).text((24, 1040), '地図：Natural Earth', font=Fb(22), fill=(180, 185, 195), anchor='ls'); return im
def s_castle(t, T, gt, pre):
    th = at('castle', '高さ', pre)
    if t < th:
        im = base_photo('04.jpg', t, th, 0.75, blue=0.25, z0=1.0, z1=1.12, cy0=0.5, cy1=0.42)
        bullet(im, 110, 220, '町を見下ろす丘の上', t, 0.3, Mi(60), PALE)
        bullet(im, 110, 340, '750年以上前に建てられた', t, at('castle', '七百', pre), Mi(66), ICE)
        bullet(im, 110, 470, 'スパーレンブルク城', t, at('castle', 'スパー', pre), Mi(96), GOLD)
        return finish(im, gt, 0.12, caption='写真：スパーレンブルク城（ビーレフェルト）')
    q = t - th; im = base_photo('05.jpg', q, T - th, 0.75, blue=0.25, z0=1.0, z1=1.1, cy0=0.3, cy1=0.35)
    d = ImageDraw.Draw(im, 'RGBA'); a = appear(q, 0.2, 0.8); x = 1180
    d.line((x, 980, x, 980 - 860 * a), fill=GOLD + (255,), width=6); d.line((x - 30, 980, x + 30, 980), fill=GOLD + (255,), width=6)
    if a > 0.95: d.line((x - 30, 120, x + 30, 120), fill=GOLD + (255,), width=6)
    alpha_text(im, (x + 60, 520), '高さ 37m', Mi(110), GOLD, appear(q, 0.6), anchor='lm')
    bullet(im, 1240, 700, 'の塔', t, th + 0.8, Mi(70), PALE)
    bullet(im, 110, 940, '町の人たちの 自まんの場所', t, at('castle', '町の人', pre), Mi(64), PALE)
    return finish(im, gt, 0.12, caption='写真：スパーレンブルク城の塔')
def s_origin(t, T, gt, pre):
    im = base_photo('02.jpg', t, T, 0.4, blue=0.4, z0=1.15, z1=1.25, blur=4)
    bullet(im, 110, 150, '1994年', t, 0.2, Mi(110), GOLD)
    bullet(im, 560, 150, 'インターネットが まだ ごく一部の人のもの', t, at('origin', 'インター', pre), Mi(48), ICE)
    tb = at('origin', 'ネットの掲示板', pre); a = appear(t, tb)
    if a > 0:
        B.terminal(im, 260, 320, 1400, 560, ['Newsgroups: de.talk.bizarre', 'Date: 16 May 1994', 'Subject: Bielefeld', '', 'Bielefeld ...?'], t, tb + 0.3, cps=22, a=a)
        bullet(im, 260, 950, 'ある大学生が、ネットの掲示板に書きこんだ', t, at('origin', 'ある大学生', pre), Mi(54), PALE)
    return finish(im, gt, 0.15, caption='写真：昔のビーレフェルトの通り（古い写真）')
def s_l1(t, T, gt, pre):
    im = base_photo('06.jpg', t, T, 0.4, z0=1.1, z1=1.25, blur=3)
    header(im, 1, '3つの質問', t)
    Q = [('ビーレフェルトの人を 知っている？', 'あなたは'), ('ビーレフェルトに 行ったことがある？', 'ビーレフェルトに、行った'), ('行ったことがある人を 知っている？', 'ビーレフェルトに行ったことがある')]
    ta = at('l1', '三つとも', pre)
    for i, (q, k) in enumerate(Q):
        B.qcard(im, 110, 200 + i * 150, 1300, 120, i + 1, q, appear(t, at('l1', k, pre)), (t - ta - i * 0.35) / 0.3 if t > ta else 0)
    tn = at('l1', 'ビーレフェルトは、存在', pre)
    bullet(im, 110, 720, '→ ビーレフェルトは 存在しない', t, tn, Mi(84), GOLD)
    th = at('l1', 'もし', pre)
    bullet(im, 110, 860, '「はい」と答える人は…', t, th, Mi(56), PALE)
    bullet(im, 760, 860, 'だまされている？', t, at('l1', 'だまされ', pre), Mi(64), ICE)
    bullet(im, 1300, 860, 'それとも 仲間？', t, at('l1', '仲間', pre), Mi(64), RED)
    return finish(im, gt, 0.2, caption='写真：ビーレフェルトの公園')
def s_l2(t, T, gt, pre):
    tm = at('l2', 'やつらは', pre)
    im = R.darkbg(W, H, (18, 20, 32)).copy()
    B.eyes(im, gt, 16, ease(t / 6.0) * (1 - 0.6 * appear(t, tm)))
    if t < tm + 0.3:
        header(im, 2, '「やつら」のしわざ', t)
        bullet(im, W / 2, 330, '町を あるように見せかけている', t, at('l2', 'この町', pre), Mi(64), PALE, 'mm')
        bullet(im, W / 2, 470, '正体不明の「やつら」', t, at('l2', '正体', pre), Mi(90), ICE, 'mm')
        a = appear(t, at('l2', 'ドイツ語', pre))
        alpha_text(im, (W / 2, 700), 'SIE', BE(260), RED, a); alpha_text(im, (W / 2, 880), 'ドイツ語で「やつら」（ズィー）', Mi(52), PALE, a)
        return finish(im, gt, 0.25)
    q = t - tm
    P = B.europe(im, 520, 640, 150, lat0=52.0, lon0=8.8, a=0.9 * appear(q, 0, 0.6)); x, y = P(*B.BIE); d = ImageDraw.Draw(im, 'RGBA')
    d.ellipse((x - 10, y - 10, x + 10, y + 10), outline=GOLD + (255,), width=4); alpha_text(im, (x, y - 60), 'Bielefeld', Fb(54), GOLD, appear(q, 0.2))
    header(im, 2, '「やつら」のしわざ', t)
    bullet(im, 110, 250, '地図にも', t, tm + 0.3, Mi(56), PALE)
    B.exit_sign(im, 1400, 470, 230, 0, appear(t, at('l2', '高速道路', pre)))
    bullet(im, 1050, 250, '高速道路の標識にも', t, at('l2', '高速道路', pre), Mi(56), PALE)
    bullet(im, 900, 820, '名前はよく見るのに…', t, at('l2', 'だから', pre), Mi(62), PALE)
    bullet(im, 900, 940, '本物の町には たどり着けない？', t, at('l2', '本物の', pre), Mi(66), GOLD)
    im = finish(im, gt, 0.15); ImageDraw.Draw(im).text((24, 1040), '地図：Natural Earth　標識の絵はイメージ', font=Fb(22), fill=(180, 185, 195), anchor='ls'); return im
def road(im, t, speed=1.0):
    d = ImageDraw.Draw(im, 'RGBA'); hz = 470; vx = W / 2
    d.polygon([(vx - 30, hz), (vx + 30, hz), (W * 0.95, H), (W * 0.05, H)], fill=(24, 26, 32, 255))
    for k in range(14):
        z = ((k / 14) + t * 0.12 * speed) % 1.0; z2 = z + 0.025
        f = lambda zz: hz + (H - hz) * zz ** 2.2
        y1, y2 = f(z), f(min(1, z2)); w1, w2 = 3 + 14 * z ** 2.2, 3 + 14 * min(1, z2) ** 2.2
        d.polygon([(vx - w1, y1), (vx + w1, y1), (vx + w2, y2), (vx - w2, y2)], fill=(220, 220, 200, int(200 * z)))
    R.glow(im, vx, hz, 200, (120, 140, 190), 50)
def s_l2b(t, T, gt, pre):
    im = R.darkbg(W, H, (14, 18, 30)).copy(); road(im, gt)
    tc = at('l2b', '町へ下りる', pre)
    sc = 140 + 120 * ease(t / T); B.exit_sign(im, 1450, 360, sc, (t - at('l2b', '閉まって', pre)) / 0.6 if t > at('l2b', '閉まって', pre) else 0, appear(t, tc - 1.5, 1.0))
    bullet(im, 110, 200, 'うわさを書いた大学生が 話した きっかけ', t, 0.3, Mi(50), GREY)
    bullet(im, 110, 330, '車で ビーレフェルトの近くを通ったら…', t, at('l2b', '車で', pre), Mi(58), PALE)
    bullet(im, 110, 880, '町へ下りる出口が 閉まっていた', t, at('l2b', '閉まって', pre) - 0.3, Mi(78), GOLD)
    return finish(im, gt, 0.3, True)
def s_rh(t, T, gt, pre):
    im = R.darkbg(W, H, (20, 26, 40)).copy(); B.eyes(im, gt, 10, 1.0, seed=8)
    alpha_text(im, (W / 2, 420), 'でも、本当にあやしいのは', Mi(100), PALE, appear(t, 0.1, 0.5)); alpha_text(im, (W / 2, 620), 'ここから', Mi(150), GOLD, appear(t, 0.9, 0.5))
    return finish(im, gt, 0.35)
def s_l3(t, T, gt, pre):
    im = base_photo('01.jpg', t, T, 0.55, z0=1.0, z1=1.25, cx0=0.4, cy0=0.45, cx1=0.55, cy1=0.4)
    tu = at('l3', 'それとも', pre)
    B.ufo(im, 1350 + 60 * math.sin(gt * 0.5), 300 + 20 * math.sin(gt * 0.9), 210, gt, appear(t, tu, 1.5))
    header(im, 3, '大学に隠された 宇宙船', t)
    bullet(im, 110, 280, 'やつらの正体は…', t, at('l3', 'やつらの', pre), Mi(58), GREY)
    bullet(im, 110, 400, '外国のスパイ組織？', t, at('l3', '外国', pre), Mi(76), PALE)
    bullet(im, 110, 530, 'それとも 宇宙人？', t, tu, Mi(84), CYAN)
    bullet(im, 110, 780, '大学の巨大な建物は', t, at('l3', '町の大学', pre), Mi(60), PALE)
    bullet(im, 110, 900, '宇宙船を隠す「カバー」？', t, at('l3', 'じつは', pre), Mi(80), GOLD)
    im = finish(im, gt, 0.2, caption='写真：ビーレフェルト大学の駐車場（UFOの絵はイメージ）'); return im
def timeline(im, t, pts, y=600, years=(1990, 2022)):
    d = ImageDraw.Draw(im, 'RGBA'); x0, x1 = 160, 1760
    X = lambda yr: x0 + (yr - years[0]) / (years[1] - years[0]) * (x1 - x0)
    d.line((x0, y, x1, y), fill=(200, 205, 220, 200), width=4)
    for yr in range(1990, 2021, 5): d.line((X(yr), y - 10, X(yr), y + 10), fill=(200, 205, 220, 200), width=3); ctext(d, (X(yr), y + 40), str(yr), Fb(30), GREY)
    for k, (yr, lab, sub, t0, col) in enumerate(pts):
        a = appear(t, t0, 0.6)
        if a <= 0: continue
        x = X(yr); up = k % 2 == 0; yy = y - 190 if up else y + 200
        d.line((x, y, x, yy + (60 if up else -60)), fill=col + (int(220 * a),), width=3); d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=col + (int(255 * a),))
        alpha_text(im, (x, yy - 30), lab, Mi(50), col, a, sw=0); alpha_text(im, (x, yy + 30), sub, Fo(34), PALE, a, sw=0)
def s_now1(t, T, gt, pre):
    im = base_photo('07.jpg', t, T, 0.3, z0=1.2, z1=1.35, blur=8)
    alpha_text(im, (W / 2, 110), 'いま、この町は？', Mi(72), PALE, appear(t, 0.1))
    bullet(im, W / 2, 230, '町は、このうわさを 何度もネタにしてきた', t, at('now1', 'じつは', pre), Mi(56), GOLD, 'mm')
    timeline(im, t, [(1994, '1994年', 'うわさが生まれる', at('now1', 'じつは', pre) + 1.0, GREY),
                     (1999, '1999年4月1日', '市「ビーレフェルトは、あります！」', at('now1', '一九九九', pre), ICE),
                     (2014, '2014年（町の800歳）', '合言葉「そんなの、あるわけない」', at('now1', '二〇一四', pre), GOLD)])
    return finish(im, gt, 0.15, caption=PB)
def s_spread(t, T, gt, pre):
    im = base_photo('09.jpg', t, T, 0.3, z0=1.2, z1=1.3, blur=6)
    bullet(im, W / 2, 140, 'うわさが生まれて 25年目', t, 0.3, Mi(60), GREY, 'mm')
    bullet(im, W / 2, 260, '2019年　市の発表', t, at('spread', '二〇一九', pre), Mi(80), PALE, 'mm')
    tp = at('spread', 'ビーレフェルトが', pre)
    bullet(im, W / 2, 420, '「存在しないと 証明できたら」', t, tp, Mi(70), PALE, 'mm')
    tm = at('spread', '賞金', pre); a = appear(t, tm, 0.3)
    if a > 0:
        v = int(1_000_000 * ease((t - tm) / 1.6)); alpha_text(im, (W / 2, 620), f'賞金 {v:,}ユーロ', Mi(130), GOLD, a)
    bullet(im, W / 2, 820, '当時の日本円で 約1億2千万円', t, at('spread', '当時', pre), Mi(66), ICE, 'mm')
    return finish(im, gt, 0.12, caption=PB)
def s_now2(t, T, gt, pre):
    tr = at('now2', '結果の', pre)
    if t < tr:
        im = R.darkbg(W, H, (16, 22, 36)).copy(); d = ImageDraw.Draw(im, 'RGBA')
        ts = at('now2', 'およそ二千人', pre); n = int(2000 * ease((t - ts) / 2.5)) if t > ts else 0
        alpha_text(im, (110, 110), '締め切りまで わずか2週間', Mi(56), PALE, appear(t, 0.2), anchor='lm')
        for k in range(n // 10):   # 1つの点＝10人
            r, c = divmod(k, 20); x = 1080 + c * 38; y = 80 + r * 38; d.ellipse((x, y, x + 26, y + 26), fill=GOLD + (220,))
        alpha_text(im, (110, 260), f'応募 約{n:,}人', Mi(100), GOLD, appear(t, ts), anchor='lm')
        alpha_text(im, (1080, 1010), '● 1つ＝10人', Fb(28), GREY, appear(t, ts), anchor='lm', sw=0)
        bullet(im, 110, 470, 'ポエム・イラスト・動画', t, at('now2', 'ポエム', pre), Mi(60), PALE)
        bullet(im, 110, 600, '物理学や数学の 何ページもの「証明」', t, at('now2', '物理学', pre), Mi(52), ICE)
        bullet(im, 110, 760, '大学の研究者と 一つずつ確認', t, at('now2', '市は', pre), Mi(58), PALE)
        return finish(im, gt, 0.15)
    q = t - tr; im = base_photo('04.jpg', q, T - tr, 0.7, blue=0.2, z0=1.0, z1=1.12)
    alpha_text(im, (W / 2, 180), '結果の発表　2019年9月17日', Mi(64), PALE, appear(q, 0.0))
    alpha_text(im, (W / 2, 440), '「ビーレフェルトは、ある」', Mi(130), GOLD, appear(t, at('now2', '「ビーレ', pre), 0.4))
    bullet(im, W / 2, 700, '賞金を手にした人　0人', t, at('now2', '賞金を', pre), Mi(90), PALE, 'mm')
    return finish(im, gt, 0.1, caption='写真：スパーレンブルク城（ビーレフェルト）')
def s_now3(t, T, gt, pre):
    im = base_photo('07.jpg', t, T, 0.5, z0=1.0, z1=1.12, cy0=0.6, cy1=0.6)
    B.stone(im, 1480, 980, 330, appear(t, 0.3, 1.0))
    bullet(im, 110, 200, '町の古い教会のそばの公園', t, 0.2, Mi(54), PALE)
    bullet(im, 110, 320, '重さ 600kg の石', t, at('now3', '重さ', pre), Mi(90), GOLD)
    bullet(im, 110, 470, '「ビーレフェルト陰謀論の 終わり」', t, at('now3', 'きざまれた', pre), Mi(56), ICE)
    tb = at('now3', '発表の日', pre)
    bullet(im, 110, 640, '発表の日、25年前に書いた本人も', t, tb, Mi(52), PALE)
    bullet(im, 110, 740, 'うわさの終わりを 見届けた', t, at('now3', 'うわさの終わり', pre), Mi(62), GOLD)
    return finish(im, gt, 0.15, True)
def s_outro(t, T, gt, pre):
    tq = at('outro', 'では', pre)
    if t < tq:
        im = base_photo('09.jpg', t, tq, 0.85, blue=0.2, z0=1.0, z1=1.1)
        bullet(im, 110, 300, '存在しない、と言われ続けた町は', t, 0.2, Mi(66), PALE)
        bullet(im, 110, 440, 'いまも ちゃんと そこにある', t, at('outro', 'いまも', pre), Mi(90), GOLD)
        return finish(im, gt, 0.1, caption=PB)
    im = base_photo('06.jpg', t - tq, T - tq, 0.4, z0=1.05, z1=1.3, cx0=0.6, cx1=0.7)
    alpha_text(im, (W / 2, 90), '最後に、あなたに質問', Mi(60), PALE, appear(t, tq))
    ks = [('ビーレフェルトの人を 知っている？', 'あなたは、ビーレ'), ('ビーレフェルトに 行ったことがある？', '行ったことは')]
    for i, (q, k) in enumerate(ks): B.qcard(im, 110, 180 + i * 140, 1250, 110, i + 1, q, appear(t, at('outro', k, pre)))
    ta = at('outro', 'あなたは、この', pre)
    alpha_text(im, (110, 560), 'あなたは この町に', Mi(80), PALE, appear(t, ta), anchor='lm'); alpha_text(im, (110, 700), '行ってみたい？', Mi(130), GOLD, appear(t, ta + 0.3), anchor='lm')
    d = ImageDraw.Draw(im, 'RGBA')
    for i, s in enumerate(['行きたい', '行かない']):
        a = appear(t, ta + 0.9 + i * 0.3)
        if a > 0:
            x = 110 + i * 380; d.rounded_rectangle((x, 810, x + 340, 910), 20, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x + 170, 860), s, Mi(54), PALE + (int(255 * a),))
    bullet(im, 900, 860, 'コメントで教えてください', t, at('outro', 'コメント', pre), Fo(44), PALE)
    return finish(im, gt, 0.25, caption='写真：ビーレフェルトの公園')
ORDER = [('hook', s_hook, 0.15, 0.6), ('title', s_title, 0.4, 0.8), ('where', s_where, 0.4, 0.8), ('castle', s_castle, 0.3, 0.7), ('origin', s_origin, 0.4, 1.2),
         ('l1', s_l1, 0.6, 1.0), ('l2', s_l2, 0.6, 0.8), ('l2b', s_l2b, 0.3, 1.0), ('rh', s_rh, 0.3, 0.6), ('l3', s_l3, 0.6, 1.0), ('now1', s_now1, 0.5, 1.0),
         ('spread', s_spread, 0.3, 1.0), ('now2', s_now2, 0.4, 1.2), ('now3', s_now3, 0.4, 1.0), ('outro', s_outro, 0.4, 2.4)]
def plan():
    out = []; off = 0.0
    for k, fn, pre, post in ORDER:
        T = pre + D[k] + post; out.append((k, fn, pre, off, T)); off += T
    return out, off
if __name__ == '__main__':
    P, total = plan()
    if len(sys.argv) > 2 and sys.argv[2] == 'still':
        only = sys.argv[3] if len(sys.argv) > 3 else None
        for k, fn, pre, off, T in P:
            if only and k != only: continue
            for j, u in enumerate((0.25, 0.6, 0.95)):
                fn(T * u, T, off + T * u, pre).resize((960, 540)).save(f'{G}/still/{k}_{j}.jpg', quality=85)
        print('stills', total); sys.exit()
    json.dump({'scenes': [(k, off, T, pre) for k, fn, pre, off, T in P], 'total': total}, open(f'{G}/main_plan.json', 'w'))
    p = R.writer(f'{G}/main_video.mp4', W, H); n = int(round(total * 30)); idx = 0
    for i in range(n):
        gt = i / 30
        while idx + 1 < len(P) and gt >= P[idx + 1][3]: idx += 1
        k, fn, pre, off, T = P[idx]
        p.stdin.write(fn(gt - off, T, gt, pre).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('main video', total)
