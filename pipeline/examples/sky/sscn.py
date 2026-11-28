"""スカイフィッシュ：本編の場面（python3 sscn.py main [still [key]]）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, CYAN, ICE, ctext, ease, fade, kb, fog, vignette, alpha_text
import sdraw as S
import pcont as C
G = '/home/claude/sky'; D = json.load(open(f'{G}/dur.json')); W, H = 1920, 1080
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
CAP = {'sky.jpg': '写真：夕方の空（イメージ：アメリカ・フロリダ州）NASA', 'ws.jpg': '写真：宇宙から見たニューメキシコ州・ホワイトサンズ（NASA）',
       'lc.jpg': '写真：宇宙から見たニューメキシコ州の町と山（NASA）', 'skim.jpg': '写真：飛ぶ鳥（イメージ：フロリダ州）NASA', 'birds.jpg': '写真：飛ぶ鳥（イメージ：フロリダ州）NASA',
       'egret.jpg': '写真：飛び立つ鳥（イメージ：フロリダ州）NASA', 'fly.jpg': '写真：ハエ（ショウジョウバエ）NASA'}
FISH = '絵：うわさの姿のイメージ　'
def fish_pass(im, t, t0, dur, y0=420, y1=300, L=460, a=1.0):
    """t0 から dur 秒かけて画面を横切る（うわさの姿）"""
    u = (t - t0) / dur
    if 0 <= u <= 1: S.skyfish(im, -300 + (W + 600) * u, y0 + (y1 - y0) * u, -0.12, L, t, a)
# ---------- 各場面 ----------
def s_hook(t, T, gt, pre):
    if t < 0.3:   # 結果のチラ見せ：網にかかった正体（ぼかし）
        im = base('fly.jpg', 0, 1, 0.55, blur=10); ctext(ImageDraw.Draw(im), (W / 2, 540), 'その正体は…', Mi(150), GOLD, sw=5); return finish(im, gt, 0.1)
    im = base('sky.jpg', t, T, 0.7, z0=1.0, z1=1.15, cy0=0.45, cy1=0.4)
    tc = at('hook', '一コマ', pre); paused = t > at('hook', '止めて', pre)
    if not paused: fish_pass(im, t, 0.35, 0.35, 500, 380, 520, 0.5)
    else:
        u = (t - at('hook', '止めて', pre)) * 0.025
        S.skyfish(im, 1180 + u * 300, 360, -0.25, 560, t, appear(t, at('hook', 'そこには', pre), 0.8))
    S.camui(im, gt, 1000 + int(t * 30) if not paused else 1000 + int(at('hook', '止めて', pre) * 30) + int((t - at('hook', '止めて', pre)) * 2), paused=paused)
    alpha_text(im, (110, 250), 'カメラにだけ写る', Mi(96), PALE, appear(t, 0.3, 0.3), anchor='lm')
    alpha_text(im, (110, 400), '生き物がいる？', Mi(120), GOLD, appear(t, 0.35, 0.3), anchor='lm')
    bullet(im, 110, 800, '目には見えない速さで飛ぶ 細長い「なにか」', t, at('hook', '目には', pre), Mi(56), ICE)
    alpha_text(im, (W - 110, 930), '「スカイフィッシュ」', Mi(120), GOLD, appear(t, at('hook', '「スカイ', pre), 0.4), anchor='rm')
    return finish(im, gt, 0.12, caption=FISH + CAP['sky.jpg'])
def band(im, name, y, h, t, T, a=1.0):
    src = R.photo(name, W, h, bright=0.85, blue=0.3, over=1.0); u = t / max(T, 1)
    x0 = (src.width - W) * (0.2 + 0.6 * u); yy = int((src.height - h) * 0.35)
    part = src.crop((int(x0), yy, int(x0) + W, yy + h))
    if a < 1: im.paste(Image.blend(im.crop((0, y, W, y + h)), part, a), (0, y))
    else: im.paste(part, (0, y))
    d = ImageDraw.Draw(im, 'RGBA'); d.line((0, y, W, y), fill=GOLD + (int(160 * a),), width=2); d.line((0, y + h, W, y + h), fill=GOLD + (int(160 * a),), width=2)
def s_title(t, T, gt, pre):
    im = R.darkbg(W, H, (16, 26, 44)).copy(); band(im, 'sky.jpg', 560, 330, t, T, appear(t, 0.0, 1.0))
    fish_pass(im, t, 1.2, 2.2, 720, 660, 300, 0.8)
    alpha_text(im, (W / 2, 140), '都市伝説', Mi(64), GREY, appear(t, 0.1), sw=0)
    alpha_text(im, (W / 2, 300), 'カメラにだけ写る「スカイフィッシュ」', Mi(104), PALE, appear(t, 0.3, 0.8))
    alpha_text(im, (W / 2, 450), 'SKYFISH  :  THE INVISIBLE FLYER', BE(84), GOLD, appear(t, 0.8, 0.8), sw=0)
    alpha_text(im, (W / 2, 960), '空飛ぶ 謎の生き物', Mi(58), PALE, appear(t, at('title', '空飛ぶ', pre), 0.6))
    return finish(im, gt, 0.18, caption=FISH + CAP['sky.jpg'])
NM = (34.4, -106.1); ROS = (33.39, -104.52); CAVE = (21.60, -99.10); ROKKO = (34.78, 135.26); TONGHUA = (41.73, 125.94)
def s_where(t, T, gt, pre):
    tw = at('where', '宇宙から', pre); tr = at('where', 'その東', pre)
    if t < tw:
        im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / max(tw - 0.5, 1))
        sc = 9 + 30 * u; lat0 = 38 + (34.3 - 38) * u; lon0 = -98 + (-105.5 + 98) * u
        P = S.worldmap(im, W * 0.55, H * 0.55, sc, lat0, lon0, hi=('United States of America',))
        alpha_text(im, (W / 2, 80), '舞台は アメリカの南西部', Mi(60), PALE, appear(t, 0.2), sw=0)
        S.pin(im, P, *NM, 'ニューメキシコ州', gt, appear(t, at('where', 'ニューメキシコ', pre)), side='r')
        bullet(im, 110, 950, 'かわいた砂漠と 山が広がる土地', t, at('where', 'かわいた', pre), Mi(58), ICE)
        return finish(im, gt, 0.08, src='地図：Natural Earth')
    if t < tr:
        im = base('ws.jpg', t - tw, tr - tw, 0.85, blue=0.15, z0=1.0, z1=1.18)
        bullet(im, 110, 880, '宇宙から見ると…', t, tw, Mi(58), PALE)
        bullet(im, 110, 980, '真っ白な砂の海（ホワイトサンズ）', t, at('where', '真っ白', pre), Mi(64), GOLD)
        return finish(im, gt, 0.06, caption=CAP['ws.jpg'])
    im = R.darkbg(W, H, (12, 22, 40)).copy(); P = S.worldmap(im, W * 0.5, H * 0.55, 39, 34.3, -105.5, hi=('United States of America',))
    S.pin(im, P, *ROS, 'ロズウェル', gt, appear(t, tr + 0.3), side='r', size=80)
    bullet(im, 110, 140, '昔から UFOのうわさで知られる町', t, at('where', '昔から', pre), Mi(62), ICE)
    return finish(im, gt, 0.08, src='地図：Natural Earth')
def s_l1(t, T, gt, pre):
    tf = at('l1', '撮った映像', pre); tb = at('l1', '空を横切る', pre); tn = at('l1', '撮っているとき', pre)
    im = base('sky.jpg', t, T, 0.6, z0=1.1, z1=1.2, cx0=0.4, cx1=0.6)
    header(im, 1, '1994年3月 ロズウェルの空', t)
    if t < tf:
        bullet(im, 110, 300, '空のUFOを撮ろうとしていた', t, at('l1', 'ロズウェルで', pre), Mi(62), PALE)
        bullet(im, 110, 420, 'ある映像作家', t, at('l1', 'ある映像', pre), Mi(76), GOLD)
        return finish(im, gt, 0.12, caption=CAP['sky.jpg'])
    d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 150, W, H), fill=(0, 0, 0, 120))
    src = R.photo('sky.jpg', 360, 220, bright=0.7, over=1.0)
    k = int((t - tf) * 3)   # 1コマずつ送る
    S.filmstrip(im, src, 150, 300, 4, 360, 220, 40, gt, rod_u=(-0.9 + (t - tf) * 0.25) if t > tb - 0.6 else None, a=appear(t, tf, 0.5), hi=k % 4)
    bullet(im, 110, 640, '一コマずつ ゆっくり見ていくと…', t, tf + 0.3, Mi(60), PALE)
    bullet(im, 110, 770, '空を横切る 細長い棒のようなもの', t, tb, Mi(72), GOLD)
    bullet(im, 110, 900, '撮っているときは 何も見えなかったのに', t, tn, Mi(58), ICE)
    return finish(im, gt, 0.1, caption='絵：フィルムのコマのイメージ　' + CAP['sky.jpg'])
def s_l2(t, T, gt, pre):
    im = base('sky.jpg', t, T, 0.42, z0=1.2, z1=1.3, blur=3)
    header(im, 2, 'うわさの姿', t)
    ts = at('l2', '大きさ', pre); tq = at('l2', '速すぎて', pre)
    if t < ts:
        a = appear(t, at('l2', 'その体', pre), 0.8); S.skyfish(im, W / 2 + 80, 520, 0.0, 1300, gt * 0.6, a)
        bullet(im, 110, 300, '体は 細長い棒', t, at('l2', 'その体', pre), Mi(66), PALE)
        bullet(im, 110, 780, '両側に 波のようにゆれる「ヒレ」', t, at('l2', '体の両側', pre), Mi(70), GOLD)
        return finish(im, gt, 0.12, caption=FISH + CAP['sky.jpg'])
    if t < tq:
        S.sizebar(im, 260, 640, 1400, (t - ts - 0.5) / 2.5, 1.0)
        bullet(im, 110, 300, '大きさは', t, ts, Mi(66), PALE)
        bullet(im, 450, 300, '数cm 〜 なんと 30m', t, at('l2', '数センチ', pre), Mi(90), GOLD)
        return finish(im, gt, 0.12, caption=FISH + CAP['sky.jpg'])
    fish_pass(im, t, tq, 0.25, 520, 420, 600, 0.6); fish_pass(im, t, tq + 2.0, 0.25, 760, 640, 400, 0.5)
    bullet(im, 110, 300, '速すぎて 人の目では見えない', t, tq, Mi(70), PALE)
    bullet(im, 110, 440, 'カメラにだけ 写る', t, at('l2', 'カメラにだけ', pre), Mi(96), GOLD)
    bullet(im, 110, 900, '水の中も泳げる…という話まで', t, at('l2', '空だけで', pre), Mi(60), ICE)
    return finish(im, gt, 0.12, caption=FISH + CAP['sky.jpg'])
def s_l2b(t, T, gt, pre):
    im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / max(at('l2b', '日本にも', pre) + 1.0, 1))
    lon0 = -150 + (137 + 150) * 0 if False else 137.0; sc = 10 + 26 * u
    P = S.worldmap(im, W * 0.5, H * 0.55, sc, 36.0 - 1.0 * u, 137.5 - 1.5 * u, hi=('Japan',))
    alpha_text(im, (W / 2, 100), '海をこえて 日本にも', Mi(70), PALE, appear(t, 0.2))
    bullet(im, 110, 230, '「スカイフィッシュ」の名前で知られるように', t, at('l2b', '「スカイ', pre), Mi(56), GOLD)
    S.pin(im, P, *ROKKO, '兵庫県 六甲山', gt, appear(t, at('l2b', '兵庫県', pre)), side='l', size=70)
    bullet(im, 110, 950, 'よく現れる場所…とうわさされる', t, at('l2b', 'よく現れる', pre), Mi(60), ICE)
    return finish(im, gt, 0.08, src='地図：Natural Earth')
def s_rh(t, T, gt, pre):
    im = base('birds.jpg', t, T, 0.35, z0=1.15, z1=1.35, blur=5)
    alpha_text(im, (W / 2, 420), 'でも、いちばん有名な映像は', Mi(96), PALE, appear(t, 0.1, 0.5))
    alpha_text(im, (W / 2, 620), 'もっと深い場所で', Mi(140), GOLD, appear(t, at('rh', 'もっと', pre), 0.5))
    return finish(im, gt, 0.35, caption=CAP['birds.jpg'])
def s_l3(t, T, gt, pre):
    tp = at('l3', '地面に', pre); tv = at('l3', 'この穴', pre)
    if t < tp:
        im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / max(tp - 0.3, 1))
        P = S.worldmap(im, W * 0.55, H * 0.55, 14 + 18 * u, 28 - 6 * u, -102 + 3 * u, hi=('Mexico',))
        header(im, 3, 'メキシコの「ツバメの洞窟」', t)
        S.pin(im, P, *CAVE, 'サンルイスポトシ州', gt, appear(t, at('l3', 'サンルイス', pre)), side='r', size=60)
        return finish(im, gt, 0.08, src='地図：Natural Earth')
    im = R.darkbg(W, H, (40, 52, 74)).copy(); ppm = 1.85; ytop = 200
    xs, yb = S.pit(im, 1220, ytop, ppm, (t - at('l3', 'まっすぐ', pre)) / 2.0, gt, rev=(t - at('l3', 'まっすぐ', pre)) / 2.0)
    if t > tv:   # 穴の中を飛ぶ影（うわさ）：1匹ずつ増える
        for i in range(4):
            ti = tv + i * 1.2
            if t < ti: continue
            yy = 360 + i * 85; sd = yy / (370 * ppm); hw = 31 * ppm + (120 * ppm) * sd ** 1.8; wdt = max(10, hw - 85)
            ph = (t - ti) * 0.45 + i * 0.27; ph -= math.floor(ph); x = 1220 - wdt + (1 - abs(2 * ph - 1)) * 2 * wdt
            S.skyfish(im, x, ytop + yy, 0.12 * (-1) ** i, 140, gt + i, 0.8 * appear(t, ti, 0.6))
    d = ImageDraw.Draw(im, 'RGBA'); am = appear(t, at('l3', '巨大な', pre))
    if am > 0:
        d.line((1220 - 31 * ppm, ytop - 14, 1220 + 31 * ppm, ytop - 14), fill=ICE + (int(255 * am),), width=4)
        alpha_text(im, (1220 + 31 * ppm + 24, ytop + 40), '口の幅 約49〜62m', Fb(40), ICE, am, anchor='lm', sw=0)
    ar = appear(t, at('l3', '東京タワー', pre) + 1.5)
    if ar > 0:
        xr = 1220 + 151 * ppm + 50; d.line((xr, ytop, xr, ytop + 370 * ppm * ar), fill=ICE + (int(255 * ar),), width=4)
        alpha_text(im, (xr + 20, ytop + 370 * ppm * 0.5), '高い側から 370m', Fb(38), ICE, ar, anchor='lm', sw=0)
    S.tower(im, 330, ytop + 333 * ppm, 333 * ppm, appear(t, at('l3', '東京タワー', pre), 0.6))
    a = appear(t, at('l3', 'まっすぐ', pre) + 1.8)
    alpha_text(im, (xs - 40, ytop + 333 * ppm / 2), '333m', Mi(84), GOLD, a, anchor='rm')
    alpha_text(im, (330, ytop + 333 * ppm + 50), '東京タワー（333m）', Fb(40), (235, 150, 110), appear(t, at('l3', '東京タワー', pre)))
    alpha_text(im, (1220, 100), '地面にあいた 巨大な縦穴', Mi(62), PALE, appear(t, tp))
    z = appear(t, tv + 0.2, 1.2)
    if z > 0:   # 穴の中へ寄って、写った影を大きく見せる
        bw = W / (1 + 0.35 * z); bh = bw * H / W; cx_ = W / 2 + (1220 - W / 2) * z; cy_ = H / 2 + (ytop + 420 - H / 2) * z
        x0 = min(max(0, cx_ - bw / 2), W - bw); y0 = min(max(0, cy_ - bh / 2), H - bh)
        im = im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + bw, y0 + bh))
        alpha_text(im, (1330, 1000), '穴の中の映像に 何匹も写っていた…？', Mi(52), ICE, 1.0)
    return finish(im, gt, 0.06, src='断面図は単純にした目安（口の幅 約49〜62m、まっすぐ落ちる深さ 333〜370m）')
def s_l3b(t, T, gt, pre):
    tb = at('l3b', '朝になると', pre); td = at('l3b', '暗い穴', pre)
    if t < tb:
        im = base('skim.jpg', t, tb, 0.6, z0=1.0, z1=1.12)
        bullet(im, 110, 260, '名前は「ツバメ」でも', t, 0.2, Mi(66), PALE)
        bullet(im, 110, 400, 'すむのは 主にアマツバメの仲間とインコ', t, at('l3b', '穴にすんで', pre), Mi(60), GOLD)
        return finish(im, gt, 0.1, caption=CAP['skim.jpg'])
    if t < td:
        im = base('egret.jpg', t - tb, td - tb, 0.55, z0=1.05, z1=1.2, cy0=0.55, cy1=0.4)
        bullet(im, 110, 260, '朝になると 輪をえがきながら', t, tb, Mi(64), PALE)
        bullet(im, 110, 400, '穴の外へ 飛び出していく', t, at('l3b', '穴の外', pre), Mi(76), GOLD)
        return finish(im, gt, 0.1, caption=CAP['egret.jpg'])
    im = base('birds.jpg', t - td, T - td, 0.4, z0=1.2, z1=1.35, blur=2)
    fish_pass(im, t, td + 1.6, 0.4, 300, 260, 380, 0.45)
    bullet(im, 110, 780, '暗い穴を飛び回る たくさんの影', t, td, Mi(66), PALE)
    bullet(im, 110, 910, 'そこに 何かがまじっていた…？', t, at('l3b', 'そこに', pre), Mi(76), GOLD)
    return finish(im, gt, 0.18, caption=CAP['birds.jpg'])
def s_quiz(t, T, gt, pre):
    im = base('sky.jpg', t, T, 0.35, z0=1.3, z1=1.4, blur=6)
    alpha_text(im, (W / 2, 140), 'あなたは どう思う？', Mi(70), PALE, appear(t, 0.1))
    alpha_text(im, (W / 2, 260), 'スカイフィッシュの正体は…', Mi(84), GOLD, appear(t, at('quiz', 'スカイ', pre)))
    S.card(im, 260, 380, 1400, 150, 1, 'まだ知られていない 新しい生き物', appear(t, at('quiz', '一、', pre)))
    S.card(im, 260, 580, 1400, 150, 2, '宇宙から来た 何か', appear(t, at('quiz', '二、', pre)))
    S.card(im, 260, 780, 1400, 150, 3, 'どこにでもいる ふつうのもの', appear(t, at('quiz', '三、', pre)))
    return finish(im, gt, 0.2, caption=CAP['sky.jpg'])
def s_now1(t, T, gt, pre):
    tn = at('now1', '製薬会社', pre); tt = at('now1', 'そこで', pre); tr = at('now1', 'ところが', pre)
    if t < tn:
        im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / max(tn - 0.3, 1))
        P = S.worldmap(im, W * 0.55, H * 0.55, 12 + 16 * u, 38 + 3 * u, 112 + 12 * u, hi=('China',))
        alpha_text(im, (W / 2, 100), '2005年 中国のテレビ局が伝えた 実験', Mi(64), PALE, appear(t, 0.2))
        S.pin(im, P, *TONGHUA, '吉林省', gt, appear(t, at('now1', '吉林省', pre)), side='l', size=70)
        return finish(im, gt, 0.08, src='地図：Natural Earth')
    im = R.darkbg(W, H, (22, 30, 46)).copy(); d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 820, W, H), fill=(30, 34, 40, 255))
    # 監視カメラ（左）
    d.rounded_rectangle((90, 300, 330, 400), 18, fill=(70, 76, 90, 255)); d.ellipse((300, 320, 360, 380), fill=(30, 30, 40, 255), outline=(150, 160, 180, 255), width=5)
    d.polygon([(360, 350), (1800, 140), (1800, 760)], fill=(200, 220, 255, 22))
    alpha_text(im, (210, 450), '監視カメラ', Fb(40), PALE, 1.0, sw=0)
    sag = 40 * appear(t, tr - 1.0, 1.5)
    if t > tt: S.net(im, 1250, 300, 420, 420, appear(t, tt, 0.6), sag)
    for i in range(3):   # カメラに写る「影」
        ph = ((t - tn) * 0.5 + i * 0.33) % 1.0
        x = 500 + ph * 900; y = 380 + i * 120 + 40 * math.sin(ph * 6)
        if t < tr and (t < tt or x < 1250): S.skyfish(im, x, y, -0.1, 220, gt + i, 0.8)
    if t > tr:
        for i, (mx, my) in enumerate([(1330, 620), (1460, 660), (1560, 600), (1400, 700)]): S.moth(im, mx, my + sag * 0.6, 26, appear(t, tr + 0.4 + i * 0.2))
    bullet(im, 110, 180, 'スカイフィッシュそっくりの影が 何度も写った', t, at('now1', '監視カメラ', pre), Mi(56), PALE)
    bullet(im, 1250, 240, '大きな網を張って 待ち構える', t, tt, Mi(48), ICE)
    if t > tr:
        alpha_text(im, (W / 2, 860), '網にかかっていたのは…', Mi(60), PALE, appear(t, tr))
        alpha_text(im, (W / 2, 960), 'ガなどの ふつうの虫だけ', Mi(84), GOLD, appear(t, at('now1', 'ガなど', pre), 0.3))
    return finish(im, gt, 0.05, src='絵：伝えられた実験のようすを単純にしたイメージ（出典：中国中央テレビの番組を伝えた記事）')
def s_why(t, T, gt, pre):
    tc = at('why', 'ビデオは', pre); te = at('why', '一枚を写す', pre); tw = at('why', 'そして', pre); tb = at('why', '速く飛ぶ', pre)
    if t < tc:
        im = base('fly.jpg', t, tc, 0.75, blue=0.1, z0=1.0, z1=1.1, cy0=0.5, cy1=0.45)
        bullet(im, 110, 300, 'なぜ 虫が', t, 0.2, Mi(80), PALE)
        bullet(im, 110, 440, 'スカイフィッシュに見える？', t, 0.5, Mi(80), GOLD)
        bullet(im, 110, 900, 'カギは カメラのしくみ', t, at('why', 'カギは', pre), Mi(70), ICE)
        return finish(im, gt, 0.05, caption=CAP['fly.jpg'])
    if t >= tb:
        im = base('skim.jpg', t - tb, T - tb, 0.6, z0=1.15, z1=1.3, blur=2)
        bullet(im, 110, 880, '速く飛ぶ鳥の羽も 同じように写ることがある', t, tb, Mi(60), GOLD)
        return finish(im, gt, 0.08, caption=CAP['skim.jpg'])
    im = R.darkbg(W, H, (18, 24, 38)).copy(); d = ImageDraw.Draw(im, 'RGBA')
    alpha_text(im, (W / 2, 90), 'ビデオ ＝ 1秒に 約30枚の絵', Mi(64), PALE, appear(t, tc))
    # 1枚ぶんの「シャッターが開いている時間」で計算
    PW, PH = 1500, 380; px, py = 210, 330
    if t >= te: d.rounded_rectangle((px - 20, py - 20, px + PW + 20, py + PH + 20), 18, outline=(120, 130, 150, 255), width=3, fill=(6, 8, 14, 255))
    alpha_text(im, (px, py - 50), '1枚を写すあいだ（約1/30秒）', Fb(40), ICE, appear(t, te), anchor='lm', sw=0)
    fb = 5.0 if t >= tw else 0.0
    if t < te:   # 1秒＝30枚のコマが並んでいく
        n = int(min(30, (t - tc) * 12)) + 1
        for i in range(n):
            x = 160 + (i % 15) * 107; y = 380 + (i // 15) * 140
            d.rounded_rectangle((x, y, x + 95, y + 70), 6, fill=(40, 48, 66, 255), outline=(150, 160, 180, 255), width=2); ctext(d, (x + 47, y + 35), str(i + 1), BE(40), PALE)
        alpha_text(im, (W / 2, 700), f'{min(30, n)}枚', Mi(90), GOLD, 1.0)
    acc = S.blur_sim(PW, PH, 1.0, 5.0 if t >= tw else 0.0001)
    if t >= te:
        s = min(1.0, (t - (tw if t >= tw else te)) / 3.5); k = int(s * (len(acc) - 1))
        S.paste_mask(im, px, py, acc[k], (235, 240, 255)); ins = S.insect_at(PW, PH, s, 1.0, fb if t >= tw else 0.0001)
        im.paste((255, 210, 80), (px, py), ins)
        # 進んだ距離の目盛り
        d.line((px + PW * 0.12, py + PH + 45, px + PW * (0.12 + 0.76 * s), py + PH + 45), fill=GOLD + (255,), width=5)
    bullet(im, 210, 860, '虫は前に進む → 横に引きのばされて「棒」に', t, at('why', 'だから', pre) - 0.3, Mi(54), PALE)
    bullet(im, 210, 970, '1枚のあいだに何回も羽ばたく → 波のような「ヒレ」に', t, tw, Mi(54), GOLD)
    return finish(im, gt, 0.04, src='しくみを説明するための単純な計算（羽ばたきの回数は目安）')
def s_now2(t, T, gt, pre):
    tc = at('now2', 'ツバメの洞窟は', pre)
    if t < tc:
        im = base('lc.jpg', t, tc, 0.75, blue=0.15, z0=1.0, z1=1.15)
        alpha_text(im, (W / 2, 110), 'いま、その場所は？', Mi(72), PALE, appear(t, 0.1))
        S.card(im, 160, 640, 1600, 150, 1, 'UFOの博物館', appear(t, at('now2', 'UFOの博物館', pre)), sub='ロズウェル')
        S.card(im, 160, 830, 1600, 150, 2, '毎年夏に UFOのお祭り', appear(t, at('now2', '毎年', pre)), sub='ロズウェル')
        return finish(im, gt, 0.06, caption=CAP['lc.jpg'] + '（イメージ）')
    im = base('birds.jpg', t - tc, T - tc, 0.6, z0=1.0, z1=1.15)
    bullet(im, 110, 260, 'ツバメの洞窟', t, tc, Mi(80), GOLD)
    bullet(im, 110, 400, '夕方 何千羽もの鳥が 群れで穴へもどる', t, at('now2', '夕方', pre), Mi(60), PALE)
    bullet(im, 110, 520, 'その姿を見に 多くの人が訪れる', t, at('now2', 'その姿', pre), Mi(60), ICE)
    return finish(im, gt, 0.1, caption=CAP['birds.jpg'])
def s_outro(t, T, gt, pre):
    tq = at('outro', 'では', pre)
    if t < tq:
        im = base('sky.jpg', t, tq, 0.6, z0=1.0, z1=1.18)
        fish_pass(im, t, at('outro', 'でも', pre) + 1.0, 3.5, 380, 300, 420, 0.4)
        bullet(im, 110, 300, '正体は カメラのしくみが作った', t, at('outro', 'その正体', pre), Mi(66), PALE)
        bullet(im, 110, 440, 'まぼろし…かもしれない', t, at('outro', 'まぼろし', pre), Mi(84), GOLD)
        bullet(im, 110, 800, 'でも まだだれも見たことのない生き物が', t, at('outro', 'でも', pre), Mi(56), ICE)
        bullet(im, 110, 920, '空のどこかを 飛んでいる…？', t, at('outro', '空のどこか', pre), Mi(70), PALE)
        return finish(im, gt, 0.15, caption=FISH + CAP['sky.jpg'])
    im = base('sky.jpg', t - tq, T - tq, 0.4, z0=1.15, z1=1.3, cx0=0.6, cx1=0.65)
    alpha_text(im, (W / 2, 110), '最後に、あなたに質問', Mi(60), PALE, appear(t, tq))
    ta = at('outro', 'あなたは、', pre)
    alpha_text(im, (110, 330), 'あなたは スカイフィッシュを', Mi(80), PALE, appear(t, ta), anchor='lm'); alpha_text(im, (110, 500), '探しに行ってみたい？', Mi(120), GOLD, appear(t, ta + 0.4), anchor='lm')
    d = ImageDraw.Draw(im, 'RGBA')
    for i, s in enumerate(['行きたい', '行かない']):
        a = appear(t, ta + 1.0 + i * 0.3)
        if a > 0:
            x = 110 + i * 380; d.rounded_rectangle((x, 700, x + 340, 800), 20, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x + 170, 750), s, Mi(54), PALE + (int(255 * a),))
    bullet(im, 900, 750, 'コメントで教えてください', t, at('outro', 'コメント', pre), Fo(44), PALE)
    return finish(im, gt, 0.2, caption=CAP['sky.jpg'])
def s_end(t, T, gt, pre):
    im = base('sky.jpg', t, T, 0.35, z0=1.2, z1=1.25, blur=8); im = vignette(im, 0.6)
    S.endscreen(im, gt, appear(t, 0.0, 0.6)); return im
ORDER = [('hook', s_hook, 0.15, 0.6), ('title', s_title, 0.4, 0.8), ('where', s_where, 0.4, 0.8), ('l1', s_l1, 0.6, 1.0), ('l2', s_l2, 0.6, 0.8), ('l2b', s_l2b, 0.3, 1.0),
         ('rh', s_rh, 0.3, 0.6), ('l3', s_l3, 0.6, 1.0), ('l3b', s_l3b, 0.3, 1.0), ('quiz', s_quiz, 0.4, 2.0), ('now1', s_now1, 0.5, 1.0), ('why', s_why, 0.4, 1.0),
         ('now2', s_now2, 0.4, 1.0), ('outro', s_outro, 0.4, 1.2)]
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
    part = int(sys.argv[2]) if len(sys.argv) > 2 else None   # 0/1 で半分ずつ
    json.dump({'scenes': [(k, off, T, pre) for k, fn, pre, off, T in P], 'total': total}, open(f'{G}/main_plan.json', 'w'))
    n = int(round(total * 30)); rng_ = range(n) if part is None else (range(0, n // 2) if part == 0 else range(n // 2, n))
    p = R.writer(f'{G}/main_video{"" if part is None else part}.mp4', W, H); idx = 0
    for i in rng_:
        gt = i / 30
        while idx + 1 < len(P) and gt >= P[idx + 1][3]: idx += 1
        k, fn, pre, off, T = P[idx]
        p.stdin.write(fn(gt - off, T, gt, pre).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('main video', total)
