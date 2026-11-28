"""ブラックアイド・キッズ：本編の場面（python3 bscn.py main [still [key]] / main 0|1）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, CYAN, ICE, ctext, ease, fade, kb, fog, vignette, alpha_text
import sdraw as S
import bdraw as B
import pcont as C
G = '/home/claude/bek'; D = json.load(open(f'{G}/dur.json')); W, H = 1920, 1080
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
def base(name, t, T, dark=0.62, **kw): return kb(name, W, H, t / max(T, 1), bright=dark, **kw).copy()
def cap(im, s): ImageDraw.Draw(im, 'RGBA').text((W - 24, 40), s, font=Fb(26), fill=(225, 228, 235), anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
def finish(im, gt, fogk=0.2, caption=None, src=None):
    fog(im, gt, fogk); vignette(im, 0.8); d = ImageDraw.Draw(im, 'RGBA')
    if caption: cap(im, caption)
    if src: d.text((24, 1040), src, font=Fb(22), fill=(180, 185, 195), anchor='ls')
    R.note(d, W, H); return im
CAP = {'door1.jpg': '写真：夜の玄関（イメージ：アメリカ・ユタ州）HABS／米国議会図書館', 'fogstreet.jpg': '写真：霧の夜の住宅街（イメージ）Spritegrape',
       'para1.jpg': '写真：アビリーンの映画館（話の映画館とは限りません）Billy Hathorn', 'park3.jpg': '写真：霧の夜の駐車場（イメージ）Bill Wren',
       'carwin.jpg': '写真：雨の夜の車の窓（イメージ）Ayodele Adeniji', 'peep2.jpg': '写真：のぞき穴から見た外（イメージ）AnemoneProjectors',
       'abi_sunset.jpg': '写真：夕方のアビリーン（テキサス州）Flofor15', 'portland.jpg': '写真：夜のポートランドの映画館（イメージ）Steve Morgan'}
KIDS = '影の絵：うわさの姿のイメージ　'
ABI = (32.45, -99.73); PDX = (45.52, -122.68)
_PV = {}
def peepview(name, t, T, kids_a=1.0, gt=0.0, r=430, cx=W / 2, cy=H / 2, zoom=(1.0, 1.08)):
    """のぞき穴から見た外（写真を魚眼っぽく）＋遠くに立つ二人の影"""
    src = kb(name, W, H, t / max(T, 1), bright=0.55, blue=0.4, z0=zoom[0], z1=zoom[1]).copy()
    if kids_a > 0: B.kids(src, W / 2, H * 0.78, 300, kids_a, gt)
    src = B.bulge(src, 0.35)
    return B.peephole(Image.new('RGB', (W, H)), src, cx, cy, r)
# ---------- 各場面 ----------
def s_hook(t, T, gt, pre):
    if t < 0.3:   # 結果のチラ見せ：うわさの目
        im = R.darkbg(W, H, (20, 26, 40)).copy(); B.eye(im, W / 2, 470, 760, 'black'); ctext(ImageDraw.Draw(im), (W / 2, 840), '白目が ない', Mi(130), GOLD, sw=5); return finish(im, gt, 0.1)
    tp = at('hook', 'のぞき穴', pre); td = at('hook', 'でも', pre)
    if t < tp:
        im = base('door1.jpg', t, tp, 0.8, blue=0.3, z0=1.0, z1=1.1, cy0=0.5, cy1=0.55)
        B.knock(im, W * 0.5, H * 0.55, t, at('hook', 'コン', pre))
        alpha_text(im, (110, 200), '夜、ドアをたたく音', Mi(96), PALE, appear(t, 0.3, 0.3), anchor='lm')
        return finish(im, gt, 0.12, caption=CAP['door1.jpg'])
    if t < td:
        im = peepview('fogstreet.jpg', t - tp, td - tp, appear(t, at('hook', '立って', pre), 0.8), gt)
        alpha_text(im, (110, 150), 'のぞき穴から見ると…', Mi(70), PALE, appear(t, tp), anchor='lm')
        alpha_text(im, (W - 110, 960), '二人の子ども', Mi(96), GOLD, appear(t, at('hook', '二人', pre)), anchor='rm')
        return finish(im, gt, 0.1, caption=KIDS + CAP['fogstreet.jpg'])
    im = R.darkbg(W, H, (18, 24, 38)).copy()
    B.eye(im, W / 2, 420, 900, 'black', appear(t, td + 0.2, 0.8))
    alpha_text(im, (W / 2, 140), 'その目には', Mi(76), PALE, appear(t, td))
    alpha_text(im, (W / 2, 820), '白いところが まったくなかった', Mi(104), GOLD, appear(t, at('hook', '白い', pre), 0.4))
    alpha_text(im, (W / 2, 960), '「ブラックアイド・キッズ」', Mi(70), ICE, appear(t, at('hook', 'まったく', pre) + 0.8))
    return finish(im, gt, 0.15, src='目の図：うわさをもとにしたイメージ')
def band(im, name, y, h, t, T, a=1.0, cy=0.45):
    src = R.photo(name, W, h, bright=0.8, blue=0.35, over=1.0); u = t / max(T, 1)
    x0 = (src.width - W) * (0.2 + 0.6 * u); yy = int((src.height - h) * cy)
    part = src.crop((int(x0), yy, int(x0) + W, yy + h)).copy()
    if a < 1: part = Image.blend(im.crop((0, y, W, y + h)), part, a)
    im.paste(part, (0, y))
    d = ImageDraw.Draw(im, 'RGBA'); d.line((0, y, W, y), fill=GOLD + (int(160 * a),), width=2); d.line((0, y + h, W, y + h), fill=GOLD + (int(160 * a),), width=2)
def s_title(t, T, gt, pre):
    im = R.darkbg(W, H, (16, 22, 36)).copy(); band(im, 'fogstreet.jpg', 560, 330, t, T, appear(t, 0.0, 1.0), cy=0.55)
    sub = im.crop((0, 560, W, 890)); B.kids(sub, W * 0.62 + t * 6, 320, 230, appear(t, 1.0, 1.2), gt); im.paste(sub, (0, 560))
    alpha_text(im, (W / 2, 140), '都市伝説', Mi(64), GREY, appear(t, 0.1), sw=0)
    alpha_text(im, (W / 2, 300), '夜にドアをたたく子どもたち', Mi(104), PALE, appear(t, 0.3, 0.8))
    alpha_text(im, (W / 2, 450), "BLACK-EYED KIDS  :  DON'T LET THEM IN", BE(84), GOLD, appear(t, 0.8, 0.8), sw=0)
    alpha_text(im, (W / 2, 960), '「ブラックアイド・キッズ」', Mi(66), PALE, appear(t, at('title', '「ブラック', pre), 0.6))
    return finish(im, gt, 0.18, caption=KIDS + CAP['fogstreet.jpg'])
def s_where(t, T, gt, pre):
    tp = at('where', '人口', pre)
    if t < tp:
        im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / max(tp - 0.5, 1))
        sc = 9 + 30 * u; lat0 = 38 + (32.0 - 38) * u; lon0 = -98 + (-99.5 + 98) * u
        P = S.worldmap(im, W * 0.55, H * 0.55, sc, lat0, lon0, hi=('United States of America',))
        alpha_text(im, (W / 2, 80), '舞台は アメリカ南部 テキサス州', Mi(60), PALE, appear(t, 0.2), sw=0)
        S.pin(im, P, *ABI, 'アビリーン', gt, appear(t, at('where', 'アビリーン', pre)), side='r', size=80)
        return finish(im, gt, 0.08, src='地図：Natural Earth')
    im = base('abi_sunset.jpg', t - tp, T - tp, 0.85, blue=0.12, z0=1.0, z1=1.15, cy0=0.6, cy1=0.55)
    bullet(im, 110, 250, '人口 およそ12万人', t, tp, Mi(80), GOLD)
    bullet(im, 110, 860, '夕方、ビルのかげが 赤い空にとけていく', t, at('where', '夕方', pre), Mi(58), PALE)
    bullet(im, 110, 970, '静かな町', t, at('where', '静かな', pre), Mi(64), ICE)
    return finish(im, gt, 0.05, caption=CAP['abi_sunset.jpg'])
def s_l1(t, T, gt, pre):
    tk = at('l1', '看板', pre); tc = at('l1', 'コン、コン', pre)
    if t < tk:
        im = base('para1.jpg', t, tk, 0.45, blue=0.55, z0=1.3, z1=1.4, cx0=0.3, cx1=0.45, cy0=0.25, cy1=0.3)
        header(im, 1, '始まりの夜（1990年代のなかごろ）', t)
        bullet(im, 110, 330, 'ある新聞記者', t, at('l1', 'ある新聞', pre), Mi(80), GOLD)
        bullet(im, 110, 470, '映画館の前の 駐車場に車をとめた', t, at('l1', '映画館', pre), Mi(62), PALE)
        return finish(im, gt, 0.12, caption=CAP['para1.jpg'])
    im = base('park3.jpg', t - tk, T - tk, 0.6, blue=0.4, z0=1.05, z1=1.2)
    if t > tc - 0.3: B.carwin(im, appear(t, tc - 0.3, 0.4)); B.knock(im, W * 0.45, H * 0.45, t, tc)
    header(im, 1, '始まりの夜（1990年代のなかごろ）', t)
    bullet(im, 110, 330, '看板の明かりで 書きものをしていると…', t, tk, Mi(60), PALE)
    bullet(im, 160, 930, '運転席の窓を だれかが たたいた', t, at('l1', '運転席', pre), Mi(66), GOLD)
    return finish(im, gt, 0.12, caption=CAP['park3.jpg'])
def s_l1b(t, T, gt, pre):
    tf = at('l1b', '話している', pre); te = at('l1b', 'そして', pre)
    if t < te:
        im = base('park3.jpg', t, te, 0.5, blue=0.45, z0=1.2, z1=1.3, blur=2)
        B.kids(im, W * 0.52, H * 0.8, 420, appear(t, 0.2, 1.0), gt); B.carwin(im)
        bullet(im, 160, 140, '10〜14歳くらいの 二人の男の子', t, 0.3, Mi(62), PALE)
        bullet(im, 160, 260, '「おじさん、家まで 乗せてくれない？」', t, at('l1b', '「おじさん', pre), Mi(66), GOLD)
        if t > tf: fog(im, gt, 0.25 * appear(t, tf, 2.0), (90, 100, 130))
        bullet(im, 160, 790, 'なぜか 体の奥から 怖さがわいてくる', t, tf, Mi(56), ICE)
        return finish(im, gt, 0.15, caption=KIDS + CAP['park3.jpg'])
    im = R.darkbg(W, H, (18, 24, 38)).copy()
    alpha_text(im, (W / 2, 120), '二人の目は…', Mi(70), PALE, appear(t, te))
    B.eye(im, 520, 450, 640, 'normal', appear(t, te + 0.4)); alpha_text(im, (520, 690), 'ふつうの目', Fb(44), GREY, appear(t, te + 0.4), sw=0)
    B.eye(im, 1400, 450, 640, 'black', appear(t, at('l1b', 'まぶた', pre))); alpha_text(im, (1400, 690), 'うわさの目', Fb(44), GOLD, appear(t, at('l1b', 'まぶた', pre)), sw=0)
    alpha_text(im, (W / 2, 830), 'まぶたからまぶたまで 真っ黒', Mi(84), GOLD, appear(t, at('l1b', 'まぶた', pre) + 0.5))
    alpha_text(im, (W / 2, 950), '白目も 黒目のふちも ない', Mi(62), ICE, appear(t, at('l1b', '白目', pre)))
    return finish(im, gt, 0.08, src='目の図：うわさをもとにしたイメージ')
def s_l1c(t, T, gt, pre):
    tr = at('l1c', '記者は', pre); tb = at('l1c', 'ふり返る', pre)
    if t < tr:
        im = base('park3.jpg', t, tr, 0.35, blue=0.5, z0=1.3, z1=1.4, blur=4); B.carwin(im)
        alpha_text(im, (W / 2, 330), '「ぼくたちは きみが', Mi(84), PALE, appear(t, at('l1c', '「ぼく', pre)))
        alpha_text(im, (W / 2, 480), 'いいよ と言わないと', Mi(84), PALE, appear(t, at('l1c', 'いいよ', pre)))
        alpha_text(im, (W / 2, 660), '入れないんだ」', Mi(130), GOLD, appear(t, at('l1c', '入れない', pre), 0.4))
        return finish(im, gt, 0.2, caption=CAP['park3.jpg'])
    if t < tb:
        im = base('carwin.jpg', t - tr, tb - tr, 0.7, blue=0.3, z0=1.0, z1=1.25, cx0=0.4, cx1=0.6)
        bullet(im, 110, 880, 'あわてて車を出し その場をはなれた', t, tr, Mi(66), PALE)
        return finish(im, gt, 0.08, caption=CAP['carwin.jpg'])
    im = base('park3.jpg', t - tb, T - tb, 0.55, blue=0.45, z0=1.2, z1=1.05)
    bullet(im, 110, 250, 'ふり返ると…', t, tb, Mi(70), PALE)
    bullet(im, 110, 400, '二人の姿は どこにもなかった', t, at('l1c', '二人の姿', pre), Mi(84), GOLD)
    return finish(im, gt, 0.25, caption=CAP['park3.jpg'])
def s_rh(t, T, gt, pre):
    im = base('fogstreet.jpg', t, T, 0.4, z0=1.15, z1=1.35, blur=5)
    alpha_text(im, (W / 2, 420), 'でも、話は', Mi(96), PALE, appear(t, 0.1, 0.5))
    alpha_text(im, (W / 2, 620), 'ここで終わらなかった', Mi(130), GOLD, appear(t, at('rh', 'ここで', pre), 0.5))
    return finish(im, gt, 0.35, caption=CAP['fogstreet.jpg'])
def screen_posts(im, t, t0, n_max=14):
    """ネットの書きこみが次々と増えていく画面（文字は灰色の線だけ）"""
    d = ImageDraw.Draw(im, 'RGBA'); x0, y0, w, h = 260, 220, 1400, 620
    d.rounded_rectangle((x0 - 20, y0 - 20, x0 + w + 20, y0 + h + 20), 22, fill=(20, 24, 32, 255), outline=(120, 130, 150, 255), width=4)
    d.rectangle((x0, y0, x0 + w, y0 + 50), fill=(40, 46, 60, 255)); d.text((x0 + 20, y0 + 25), 'こわい体験の掲示板（イメージ）', font=Fb(30), fill=(200, 205, 215), anchor='lm')
    n = int(min(n_max, max(0, (t - t0) * 1.5 + (1 if t >= t0 else 0))))
    for i in range(n):
        k = n - 1 - i; y = y0 + 70 + k * 62
        if y > y0 + h - 50: break
        d.rounded_rectangle((x0 + 20, y, x0 + w - 20, y + 52), 8, fill=(34, 40, 54, 255))
        d.ellipse((x0 + 34, y + 10, x0 + 66, y + 42), fill=(80, 90, 110, 255))
        rr = np.random.default_rng(i); ln = rr.uniform(0.4, 0.9)
        d.line((x0 + 90, y + 18, x0 + 90 + (w - 160) * ln, y + 18), fill=(150, 155, 170, 255), width=6)
        d.line((x0 + 90, y + 36, x0 + 90 + (w - 160) * ln * 0.6, y + 36), fill=(110, 115, 130, 255), width=6)
        if i == 0 and k == 0: d.text((x0 + w - 40, y + 26), 'NEW', font=BE(36), fill=GOLD, anchor='rm')
    return n
def s_l2(t, T, gt, pre):
    tn = at('l2', '記者が', pre); to = at('l2', '遠く', pre); tp = at('l2', 'そっくり', pre)
    if t < to:
        im = R.darkbg(W, H, (14, 20, 34)).copy(); header(im, 2, 'ドアの前の子どもたち', t)
        n = screen_posts(im, t, at('l2', '記者が', pre) + 0.6)
        bullet(im, 260, 950, 'ネットに書きこむと 同じような話が次々と', t, tn, Mi(56), PALE)
        if n: alpha_text(im, (1660, 950), f'{n}件', Mi(80), GOLD, 1.0, anchor='rm')
        return finish(im, gt, 0.05, src='画面：ネットの書きこみのイメージ（件数は演出）')
    if t < tp:
        im = R.darkbg(W, H, (12, 22, 40)).copy(); P = S.worldmap(im, W * 0.55, H * 0.55, 30, 39.5, -110, hi=('United States of America',))
        S.pin(im, P, *ABI, 'アビリーン', gt, 1.0, side='r', size=56)
        u = ease((t - to) / 1.5); (x0, y0), (x1, y1) = P(*ABI), P(*PDX); d = ImageDraw.Draw(im, 'RGBA')
        pts = [(x0 + (x1 - x0) * s, y0 + (y1 - y0) * s - 160 * math.sin(math.pi * s)) for s in np.linspace(0, u, 40)]
        if len(pts) > 1: d.line(pts, fill=GOLD + (230,), width=5)
        S.pin(im, P, *PDX, 'オレゴン州 ポートランド', gt, appear(t, to + 1.4), side='r', size=60)
        bullet(im, 110, 960, '遠くはなれた町でも…', t, to + 0.3, Mi(60), ICE)
        return finish(im, gt, 0.05, src='地図：Natural Earth')
    im = base('portland.jpg', t - tp, T - tp, 0.55, blue=0.4, z0=1.15, z1=1.3, cy0=0.25, cy1=0.3)
    bullet(im, 110, 300, 'そっくりな子どもに 会った人がいた', t, tp, Mi(66), GOLD)
    bullet(im, 110, 420, '…と言われている', t, at('l2', 'と言われて', pre), Mi(56), PALE)
    return finish(im, gt, 0.15, caption=CAP['portland.jpg'])
L2B = [('年', '6〜16歳くらい', '年は'), ('肌', '青白い', '肌は'), ('目', '真っ黒', '目は'), ('いつ', '夜おそく ドアや車の窓をたたく', '夜おそく'),
       ('言うこと', '「電話を貸して」「トイレを使わせて」', '「電話'), ('声', '大人のように落ち着いた 平らな話し方', '声は'), ('会った人', 'わけもなく 強い怖さを感じる', 'そして')]
def s_l2b(t, T, gt, pre):
    im = base('fogstreet.jpg', t, T, 0.45, blue=0.45, z0=1.1, z1=1.25, cx0=0.55, cx1=0.6)
    B.kids(im, 1580, 980, 430, appear(t, 0.3, 1.0), gt)
    alpha_text(im, (110, 90), 'うわさの姿', Mi(70), GOLD, appear(t, 0.1), anchor='lm')
    for i, (k, v, key) in enumerate(L2B):
        t0 = at('l2b', key, pre); a = appear(t, t0, 0.5)
        if a <= 0: continue
        y = 200 + i * 118; d = ImageDraw.Draw(im, 'RGBA')
        d.rounded_rectangle((90 + (1 - a) * 30, y - 46, 1240, y + 46), 14, fill=(8, 10, 18, int(190 * a)), outline=GOLD + (int(120 * a),), width=2)
        alpha_text(im, (130 + (1 - a) * 30, y), k, Fb(40), GOLD, a, anchor='lm', sw=0)
        alpha_text(im, (350 + (1 - a) * 30, y), v, Mi(50), PALE, a, anchor='lm', sw=0)
    return finish(im, gt, 0.15, caption=KIDS + CAP['fogstreet.jpg'])
def s_l3(t, T, gt, pre):
    tb = at('l3', 'だから', pre); te = at('l3', 'ヨーロッパ', pre)
    if t < te:
        im = base('door1.jpg', t, te, 0.6, blue=0.35, z0=1.0, z1=1.15, cy0=0.55, cy1=0.5)
        header(im, 3, 'いちばん大事な決まり', t)
        alpha_text(im, (W / 2, 330), '「どうぞ」と言わない限り', Mi(84), PALE, appear(t, at('l3', 'こちらが', pre)))
        alpha_text(im, (W / 2, 490), '中に 入ってこられない', Mi(110), GOLD, appear(t, at('l3', '中に', pre)))
        if t > tb:
            d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, tb)
            d.rounded_rectangle((W / 2 - 560, 790, W / 2 + 560, 950), 24, fill=(60, 10, 14, int(200 * a)), outline=RED + (int(255 * a),), width=4)
            alpha_text(im, (W / 2, 870), 'だから ドアを 開けてはいけない', Mi(76), PALE, a)
        return finish(im, gt, 0.12, caption=CAP['door1.jpg'])
    im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease((t - te) / 2.0)
    P = S.worldmap(im, W * 0.5, H * 0.55, 14 + 8 * u, 50, 12, hi=('Romania', 'Hungary', 'Serbia', 'Slovakia', 'Bulgaria'))
    alpha_text(im, (W / 2, 110), 'ヨーロッパの 古い吸血鬼の話', Mi(76), PALE, appear(t, te))
    d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, at('l3', '招かれない', pre))
    d.rounded_rectangle((W / 2 - 640, 800, W / 2 + 640, 980), 24, fill=(8, 12, 22, int(220 * a)), outline=GOLD + (int(255 * a),), width=4)
    alpha_text(im, (W / 2, 890), '招かれないと 家に入れない', Mi(84), GOLD, a)
    alpha_text(im, (W / 2, 220), '…よく似ている', Mi(60), ICE, appear(t, at('l3', 'それに', pre)))
    return finish(im, gt, 0.06, src='地図：Natural Earth（色をつけたのは、吸血鬼の言い伝えが多い東ヨーロッパの国々の一部）')
def s_quiz(t, T, gt, pre):
    ts = at('quiz', 'あなたなら', pre)
    if t < ts:
        im = peepview('peep2.jpg', t, ts, appear(t, at('quiz', 'のぞき穴', pre), 0.8), gt, zoom=(1.2, 1.3))
        alpha_text(im, (W / 2, 120), 'あなたも 考えてみて', Mi(70), PALE, appear(t, 0.1))
        alpha_text(im, (W / 2, 990), '夜おそく ドアがたたかれた…', Mi(66), GOLD, appear(t, at('quiz', '夜おそく', pre)))
        B.knock(im, W * 0.2, H * 0.5, t, at('quiz', 'たたかれた', pre) - 0.3, label=False)
        return finish(im, gt, 0.05, caption=KIDS + CAP['peep2.jpg'])
    im = peepview('peep2.jpg', t, T, 1.0, gt, r=300, cx=W * 0.8, cy=H * 0.55, zoom=(1.3, 1.35))
    alpha_text(im, (110, 150), 'あなたなら どうする？', Mi(84), GOLD, appear(t, ts), anchor='lm')
    S.card(im, 110, 300, 1180, 150, 1, 'ドアを開ける', appear(t, at('quiz', '一、', pre)))
    S.card(im, 110, 500, 1180, 150, 2, 'ドアごしに 話しかける', appear(t, at('quiz', '二、', pre)))
    S.card(im, 110, 700, 1180, 150, 3, '返事をしないで 朝を待つ', appear(t, at('quiz', '三、', pre)))
    return finish(im, gt, 0.08, caption=KIDS + CAP['peep2.jpg'])
def s_now1(t, T, gt, pre):
    im = R.darkbg(W, H, (14, 20, 34)).copy(); d = ImageDraw.Draw(im, 'RGBA')
    alpha_text(im, (W / 2, 100), '世界に広がった うわさ', Mi(72), PALE, appear(t, 0.1))
    y = 560; d.line((150, y, 1770, y), fill=(140, 150, 170, 255), width=4)
    pts = [(300, '1990年代', 'ネットの書きこみ', 0.3), (900, '2012年', 'テレビ番組・映画', at('now1', '二〇一二年', pre)), (1500, '2014年', 'イギリスの新聞', at('now1', '二〇一四年', pre))]
    for x, yr, lab, t0 in pts:
        a = appear(t, t0)
        if a <= 0: continue
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD + (int(255 * a),))
        alpha_text(im, (x, y + 70), yr, Mi(64), GOLD, a); alpha_text(im, (x, y + 150), lab, Mi(46), PALE, a)
    B.tv(im, 820, 340, 260, appear(t, at('now1', 'テレビ', pre)), gt); B.film(im, 1060, 350, 220, appear(t, at('now1', '映画', pre)), gt)
    tt = at('now1', '一週間', pre)
    for k in range(3):
        a = appear(t, tt + 0.5 + k * 0.45, 0.3); B.paper(im, 1400 + k * 110, 330 + (1 - a) * -60, 170, a, ang=(-8 + k * 8))
    alpha_text(im, (1500, 920), '1週間に 3回も 一面に', Mi(66), GOLD, appear(t, at('now1', '三回', pre)))
    return finish(im, gt, 0.04, src='新聞・テレビ・映画の絵は内容を伏せたイメージ（2014年は英国の大衆紙）')
def chain(im, t, t0, a=1.0):
    """「友だちの友だちから聞いた」：人の丸がつながって、元が「？」"""
    d = ImageDraw.Draw(im, 'RGBA'); xs = [1600, 1180, 760, 340]; y = 560; labs = ['あなた', '友だち', '友だちの友だち', '？']
    for i, x in enumerate(xs):
        aa = appear(t, t0 + i * 0.5) * a
        if aa <= 0: continue
        c = GOLD if i == 3 else PALE
        d.ellipse((x - 70, y - 70, x + 70, y + 70), fill=(20, 26, 40, int(240 * aa)), outline=c + (int(255 * aa),), width=5)
        if i == 3: alpha_text(im, (x, y), '？', Mi(90), GOLD, aa)
        else:
            d.ellipse((x - 22, y - 46, x + 22, y - 2), fill=c + (int(230 * aa),)); d.pieslice((x - 44, y + 4, x + 44, y + 80), 180, 360, fill=c + (int(230 * aa),))
        alpha_text(im, (x, y + 120), labs[i], Fb(40), c, aa, sw=0)
        if i > 0: d.line((xs[i - 1] - 80, y, x + 80, y), fill=(160, 170, 190, int(200 * aa)), width=4); d.polygon([(xs[i - 1] - 80, y), (xs[i - 1] - 100, y - 12), (xs[i - 1] - 100, y + 12)], fill=(160, 170, 190, int(200 * aa)))
def s_why(t, T, gt, pre):
    tf = at('why', '話の多く', pre); tn = at('why', 'だから', pre); tb = at('why', 'でも', pre)
    if t < tf:
        im = base('park3.jpg', t, tf, 0.45, blue=0.5, z0=1.0, z1=1.12)
        alpha_text(im, (W / 2, 130), '本当に いるの？', Mi(80), PALE, appear(t, 0.1))
        S.card(im, 260, 360, 1400, 170, 1, 'はっきりした写真 … 0枚', appear(t, at('why', 'はっきり', pre)))
        S.card(im, 260, 590, 1400, 170, 2, '警察の記録 … 見つかっていない', appear(t, at('why', '警察', pre)))
        return finish(im, gt, 0.15, caption=CAP['park3.jpg'])
    if t < tb:
        im = R.darkbg(W, H, (16, 22, 36)).copy()
        alpha_text(im, (W / 2, 140), '話の多くは「友だちの友だちから聞いた」', Mi(64), PALE, appear(t, tf))
        chain(im, t, tf + 0.3)
        alpha_text(im, (W / 2, 900), 'ネットで生まれて 広がった怖い話？', Mi(76), GOLD, appear(t, tn))
        return finish(im, gt, 0.05, src='図：うわさの伝わり方のイメージ（参考：Skeptoid、Snopes、Wikipedia）')
    im = base('fogstreet.jpg', t - tb, T - tb, 0.4, blue=0.5, z0=1.2, z1=1.35)
    B.kids(im, W * 0.7, H * 0.85, 400, appear(t, tb + 0.5, 1.2), gt)
    bullet(im, 110, 300, 'でも なぜ こんなに多くの人が', t, tb, Mi(66), PALE)
    bullet(im, 110, 440, '同じ子どもを 見たと言うのか…', t, at('why', '同じ子ども', pre), Mi(80), GOLD)
    return finish(im, gt, 0.25, caption=KIDS + CAP['fogstreet.jpg'])
def s_now2(t, T, gt, pre):
    tm = at('now2', '町には', pre); tl = at('now2', '夜の子ども', pre)
    if t < tm:
        im = base('abi_sunset.jpg', t, tm, 0.7, blue=0.1, z0=1.1, z1=1.2)
        alpha_text(im, (W / 2, 110), 'いま、始まりの町は？', Mi(72), PALE, appear(t, 0.1))
        S.card(im, 160, 600, 1600, 170, 1, '「テキサスの 絵本の都」', appear(t, at('now2', '「テキサス', pre)), sub='2015年 テキサス州の議会が選んだ')
        return finish(im, gt, 0.04, caption=CAP['abi_sunset.jpg'])
    if t < tl:
        im = base('abi_sunset.jpg', t - tm, tl - tm, 0.55, blue=0.1, z0=1.2, z1=1.3, cx0=0.6, cx1=0.4)
        S.card(im, 160, 330, 1600, 170, 2, '絵本の絵を集めた 美術館', appear(t, tm), sub='子どもの本のさし絵の美術館')
        S.card(im, 160, 560, 1600, 170, 3, '公園に 絵本の登場人物の像', appear(t, at('now2', '公園', pre)), sub='町を歩きながら見られる')
        return finish(im, gt, 0.04, caption=CAP['abi_sunset.jpg'])
    im = base('para1.jpg', t - tl, T - tl, 0.95, blue=0.0, z0=1.3, z1=1.4, cx0=0.35, cx1=0.4, cy0=0.2, cy1=0.25)
    bullet(im, 110, 760, '夜の怖いうわさが生まれた町は いま', t, tl, Mi(60), PALE)
    bullet(im, 110, 880, '昼間の子どもたちが 笑って歩く町に', t, at('now2', '昼間', pre), Mi(76), GOLD)
    return finish(im, gt, 0.0, caption='写真：アビリーンの映画館（昼）Billy Hathorn')
def s_outro(t, T, gt, pre):
    tq = at('outro', 'では', pre)
    if t < tq:
        im = base('door1.jpg', t, tq, 0.55, blue=0.4, z0=1.15, z1=1.0)
        bullet(im, 110, 260, '正体は だれかが作った怖い話…', t, at('outro', 'その正体', pre), Mi(66), PALE)
        bullet(im, 110, 380, 'なのかもしれない', t, at('outro', 'なのかも', pre), Mi(66), PALE)
        bullet(im, 110, 860, 'でも もし今夜 あなたの家のドアが…', t, at('outro', 'でも', pre), Mi(62), GOLD)
        B.knock(im, W * 0.55, H * 0.6, t, at('outro', 'コン、コン', pre))
        return finish(im, gt, 0.15, caption=CAP['door1.jpg'])
    im = base('door1.jpg', t - tq, T - tq, 0.35, z0=1.2, z1=1.3, blur=4)
    alpha_text(im, (W / 2, 110), '最後に、あなたに質問', Mi(60), PALE, appear(t, tq))
    ta = at('outro', 'あなたなら', pre)
    alpha_text(im, (110, 330), 'あなたなら そのドアを', Mi(80), PALE, appear(t, ta), anchor='lm'); alpha_text(im, (110, 500), '開けますか？', Mi(130), GOLD, appear(t, ta + 0.4), anchor='lm')
    d = ImageDraw.Draw(im, 'RGBA')
    for i, s in enumerate(['開ける', '開けない']):
        a = appear(t, ta + 1.0 + i * 0.3)
        if a > 0:
            x = 110 + i * 380; d.rounded_rectangle((x, 700, x + 340, 800), 20, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x + 170, 750), s, Mi(54), PALE + (int(255 * a),))
    bullet(im, 900, 750, 'コメントで教えてください', t, at('outro', 'コメント', pre), Fo(44), PALE)
    return finish(im, gt, 0.2, caption=CAP['door1.jpg'])
def s_end(t, T, gt, pre):
    im = base('fogstreet.jpg', t, T, 0.35, z0=1.2, z1=1.25, blur=8); im = vignette(im, 0.6)
    S.endscreen(im, gt, appear(t, 0.0, 0.6)); return im
ORDER = [('hook', s_hook, 0.15, 0.6), ('title', s_title, 0.4, 0.8), ('where', s_where, 0.4, 0.8), ('l1', s_l1, 0.6, 0.8), ('l1b', s_l1b, 0.3, 0.8), ('l1c', s_l1c, 0.3, 1.0),
         ('rh', s_rh, 0.3, 0.6), ('l2', s_l2, 0.6, 0.8), ('l2b', s_l2b, 0.3, 1.0), ('l3', s_l3, 0.6, 1.0), ('quiz', s_quiz, 0.4, 2.0), ('now1', s_now1, 0.5, 1.0),
         ('why', s_why, 0.4, 1.0), ('now2', s_now2, 0.4, 1.0), ('outro', s_outro, 0.4, 1.2)]
ENDT = 12.0
def plan():
    out = []; off = 0.0
    for k, fn, pre, post in ORDER:
        T = pre + D[k] + post; out.append((k, fn, pre, off, T)); off += T
    out.append(('end', s_end, 0.5, off, ENDT)); off += ENDT
    return out, off
if __name__ == '__main__':
    P, total = plan()
    if len(sys.argv) > 2 and sys.argv[2] == 'still':
        only = sys.argv[3] if len(sys.argv) > 3 else None
        for k, fn, pre, off, T in P:
            if only and k != only: continue
            for j, u in enumerate((0.25, 0.6, 0.95)):
                fn(T * u, T, off + T * u, pre).convert('RGB').resize((960, 540)).save(f'{G}/still/{k}_{j}.jpg', quality=85)
        print('stills', total); sys.exit()
    part = int(sys.argv[2]) if len(sys.argv) > 2 else None
    json.dump({'scenes': [(k, off, T, pre) for k, fn, pre, off, T in P], 'total': total}, open(f'{G}/main_plan.json', 'w'))
    n = int(round(total * 30)); rng_ = range(n) if part is None else (range(0, n // 2) if part == 0 else range(n // 2, n))
    p = R.writer(f'{G}/main_video{"" if part is None else part}.mp4', W, H); idx = 0
    for i in rng_:
        gt = i / 30
        while idx + 1 < len(P) and gt >= P[idx + 1][3]: idx += 1
        k, fn, pre, off, T = P[idx]
        p.stdin.write(fn(gt - off, T, gt, pre).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('main video', total)
