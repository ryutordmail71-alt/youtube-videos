"""東京の地下の秘密の通路：本編の場面（python3 tscn.py main [still [key]] / main 0|1）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, CYAN, ICE, ctext, ease, fade, kb, fog, vignette, alpha_text
import sdraw as S
import tdraw as T
import pcont as C
G = '/home/claude/tkc'; D = json.load(open(f'{G}/dur.json')); W, H = 1920, 1080
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
def base(name, t, Tt, dark=0.62, **kw): return kb(name, W, H, t / max(Tt, 1), bright=dark, **kw).copy()
def cap(im, s): ImageDraw.Draw(im, 'RGBA').text((W - 24, 40), s, font=Fb(26), fill=(225, 228, 235), anchor='rm', stroke_width=2, stroke_fill=(0, 0, 0))
def finish(im, gt, fogk=0.2, caption=None, src=None):
    fog(im, gt, fogk); vignette(im, 0.8); d = ImageDraw.Draw(im, 'RGBA')
    if caption: cap(im, caption)
    if src: d.text((24, 1040), src, font=Fb(22), fill=(180, 185, 195), anchor='ls')
    R.note(d, W, H); return im
CAP = {'diet2.jpg': '写真：国会議事堂（東京・永田町）っ／Wikimedia Commons', 'diet_day.jpg': '写真：夜の永田町と国会議事堂 Daderot',
       'esc.jpg': '写真：永田町駅の長いエスカレーター 本屋', 'kplat.jpg': '写真：国会議事堂前駅 千代田線のホーム LERK', 'kplat2.jpg': '写真：国会議事堂前駅 丸ノ内線のホーム MaedaAkihiko',
       'maru_night.jpg': '写真：夜の丸の内と皇居のお堀 Nryate', 'moat.jpg': '写真：皇居のお堀 itoshin87', 'passage1.jpg': '写真：地下通路（イメージ：神田駅）Kirin7739',
       'passage2.jpg': '写真：虎ノ門駅と虎ノ門ヒルズ駅をつなぐ通路 Real Estate Japan', 'passage1.jpg': '写真：地下通路（イメージ：西新宿）Guilhem Vellut',
       'sakurada.jpg': '写真：桜田門と霞が関の通り Aimaimyi', 'wall.jpg': '写真：皇居の石垣 Wikimedia Commons'}
DOORIMG = '扉の絵：イメージ　'
MAPSRC = '略図：駅・建物の位置はおよそ。路線は簡単にしたもの'
TOKYO = (35.68, 139.76)
# ---------- 各場面 ----------
def s_hook(t, Tt, gt, pre):
    if t < 0.3:   # 結果のチラ見せ：少しだけ開いた扉
        im = base('passage1.jpg', 2, 3, 0.35, blue=0.5, z0=1.2, z1=1.2); T.door(im, W / 2, 1000, 760, 0.6)
        ctext(ImageDraw.Draw(im), (W / 2, 150), '扉の先は？', Mi(110), GOLD, sw=5); return finish(im, gt, 0.1)
    tc = at('hook', 'その地下', pre); ts = at('hook', 'そんな', pre)
    if t < tc:
        im = base('diet2.jpg', t, tc, 0.85, blue=0.25, z0=1.0, z1=1.12, cy0=0.45, cy1=0.4)
        alpha_text(im, (110, 200), '東京のど真ん中', Mi(80), PALE, appear(t, 0.3, 0.3), anchor='lm')
        alpha_text(im, (110, 330), '国会議事堂', Mi(120), GOLD, appear(t, at('hook', '国会', pre), 0.3), anchor='lm')
        return finish(im, gt, 0.1, caption=CAP['diet2.jpg'])
    im = base('kplat.jpg', t - tc, Tt - tc, 0.5, blue=0.5, z0=1.05, z1=1.25)
    P = lambda la, lo: (0, 0)
    alpha_text(im, (W / 2, 150), 'その地下には…', Mi(80), PALE, appear(t, tc))
    alpha_text(im, (W / 2, 460), '地図にのっていない', Mi(96), PALE, appear(t, at('hook', '地図', pre)))
    alpha_text(im, (W / 2, 620), '秘密の通路', Mi(170), GOLD, appear(t, at('hook', '秘密', pre), 0.4))
    alpha_text(im, (W / 2, 880), 'そんなうわさを 聞いたことは？', Mi(64), ICE, appear(t, ts))
    return finish(im, gt, 0.2, caption=CAP['kplat.jpg'])
def band(im, name, y, h, t, Tt, a=1.0, cy=0.45):
    src = R.photo(name, W, h, bright=0.8, blue=0.35, over=1.0); u = t / max(Tt, 1)
    x0 = (src.width - W) * (0.2 + 0.6 * u); yy = int((src.height - h) * cy)
    part = src.crop((int(x0), yy, int(x0) + W, yy + h)).copy()
    if a < 1: part = Image.blend(im.crop((0, y, W, y + h)), part, a)
    im.paste(part, (0, y))
    d = ImageDraw.Draw(im, 'RGBA'); d.line((0, y, W, y), fill=GOLD + (int(160 * a),), width=2); d.line((0, y + h, W, y + h), fill=GOLD + (int(160 * a),), width=2)
def s_title(t, Tt, gt, pre):
    im = R.darkbg(W, H, (16, 22, 36)).copy(); band(im, 'passage1.jpg', 560, 330, t, Tt, appear(t, 0.0, 1.0), cy=0.6)
    alpha_text(im, (W / 2, 140), '都市伝説', Mi(64), GREY, appear(t, 0.1), sw=0)
    alpha_text(im, (W / 2, 300), '東京の地下に眠る 秘密の通路', Mi(104), PALE, appear(t, 0.3, 0.8))
    alpha_text(im, (W / 2, 450), 'SECRET TUNNELS UNDER TOKYO', BE(84), GOLD, appear(t, 0.8, 0.8), sw=0)
    alpha_text(im, (W / 2, 960), '地図にない地下道のうわさ', Mi(66), PALE, appear(t, at('title', '「秘密', pre), 0.6))
    return finish(im, gt, 0.18, caption=CAP['passage1.jpg'])
def s_where(t, Tt, gt, pre):
    tn = at('where', '国会議事堂や', pre); tk = at('where', 'すぐ北', pre); ts = at('where', 'そして', pre); tl = at('where', '東京の地下鉄は', pre)
    if t < tn:
        im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / max(tn - 0.3, 1))
        sc = 14 + 260 * u ** 2; la = 37 + (35.68 - 37) * u; lo = 137.5 + (139.76 - 137.5) * u
        P = S.worldmap(im, W * 0.5, H * 0.55, sc, la, lo, hi=('Japan',))
        alpha_text(im, (W / 2, 80), '舞台は 東京都 千代田区', Mi(60), PALE, appear(t, 0.2), sw=0)
        S.pin(im, P, *TOKYO, '永田町', gt, appear(t, at('where', '永田町', pre)), side='r', size=80)
        return finish(im, gt, 0.06, src='地図：Natural Earth')
    if t < ts:
        im = R.darkbg(W, H, (14, 20, 34)).copy()
        P = T.areamap(im, appear(t, tn - 0.2, 0.6), lines_a=0.0, cy=H * 0.52)
        alpha_text(im, (W / 2, 90), '日本の政治の中心', Mi(66), GOLD, appear(t, at('where', '日本の', pre)))
        if t > tk:
            x, y = P(*T.PL['皇居']); r = 260 + 10 * math.sin(gt * 3); d = ImageDraw.Draw(im, 'RGBA')
            d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), outline=GOLD + (int(255 * appear(t, tk)),), width=5)
        return finish(im, gt, 0.04, src=MAPSRC)
    if t < tl:
        im = R.darkbg(W, H, (14, 20, 34)).copy()
        T.areamap(im, 0.75, lines_a=appear(t, ts + 0.3, 1.5), cy=H * 0.52)
        alpha_text(im, (W / 2, 90), '地下を 何本もの地下鉄が走る', Mi(66), PALE, appear(t, ts))
        return finish(im, gt, 0.04, src=MAPSRC)
    im = base('maru_night.jpg', t - tl, Tt - tl, 0.75, blue=0.3, z0=1.0, z1=1.15, cx0=0.5, cx1=0.6)
    alpha_text(im, (110, 220), '東京の地下鉄', Mi(64), PALE, appear(t, tl), anchor='lm')
    alpha_text(im, (110, 360), 'ぜんぶで およそ300km', Mi(96), GOLD, appear(t, at('where', '三百', pre)), anchor='lm')
    bullet(im, 110, 880, 'だれも知らない道が かくれている…？', t, at('where', 'そのどこか', pre), Mi(66), ICE)
    return finish(im, gt, 0.12, caption=CAP['maru_night.jpg'], src='300km：東京メトロ＋都営地下鉄の営業キロの合計（目安）')
def s_l1(t, Tt, gt, pre):
    tc = at('l1', '国会議事堂、', pre); tb = at('l1', 'でも', pre)
    if t < tc:
        im = base('sakurada.jpg', t, tc, 0.5, blue=0.45, z0=1.0, z1=1.12)
        header(im, 1, '地図にない地下道', t)
        bullet(im, 110, 330, '戦争の前から 戦争中にかけて', t, at('l1', '戦争の前', pre), Mi(62), PALE)
        bullet(im, 110, 470, '地下鉄とは別の 秘密の地下道が', t, at('l1', '地下鉄とは', pre), Mi(66), PALE)
        bullet(im, 110, 610, '掘られた…と言われている', t, at('l1', '掘られた', pre), Mi(80), GOLD)
        return finish(im, gt, 0.15, caption=CAP['sakurada.jpg'])
    im = R.darkbg(W, H, (14, 20, 34)).copy(); P = T.areamap(im, 0.8, lines_a=0.35, cy=H * 0.55, line_names=False)
    T.secretnet(im, P, (t - tc) / 3.5, gt, 1.0)
    header(im, 1, '地図にない地下道', t)
    if t > tb:
        d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, tb)
        d.rounded_rectangle((1020, 860, 1890, 1000), 24, fill=(8, 10, 18, int(220 * a)), outline=GOLD + (int(255 * a),), width=4)
        alpha_text(im, (1455, 930), 'どの地図にも 1本ものっていない', Mi(56), GOLD, a)
    alpha_text(im, (W - 60, 200), '金の点線：うわさの道（イメージ）', Fb(32), GOLD, appear(t, tc + 0.5), anchor='rm', sw=2)
    return finish(im, gt, 0.05, src=MAPSRC + '。点線は実在の道ではありません')
def s_l1b(t, Tt, gt, pre):
    tq = at('l1b', '本当に', pre)
    if t < tq:
        im = R.darkbg(W, H, (20, 22, 30)).copy()
        alpha_text(im, (W / 2, 90), '2000年代には こんな本まで', Mi(64), PALE, appear(t, 0.1))
        T.mapcard(im, 140, 220, 620, 470, '昔の地図', 'old', (t - 0.6) / 2.0, gt, appear(t, 0.5))
        T.mapcard(im, 1160, 220, 620, 470, 'いまの地図', 'new', (t - at('l1b', 'いまの地図', pre)) / 2.0, gt, appear(t, at('l1b', 'いまの地図', pre)))
        alpha_text(im, (W / 2, 450), '⇔', Fo(100), GOLD, appear(t, at('l1b', 'くらべて', pre)))
        a = appear(t, at('l1b', '「線路', pre))
        if a > 0:
            d = ImageDraw.Draw(im, 'RGBA'); d.rounded_rectangle((260, 850, 1660, 1000), 24, fill=(8, 10, 18, int(220 * a)), outline=GOLD + (int(255 * a),), width=4)
            alpha_text(im, (W / 2, 925), '「地図から消された道がある」', Mi(72), GOLD, appear(t, at('l1b', '「地図', pre)) * 0.7 + a * 0.3)
        T.book(im, W / 2, 460, 300, appear(t, at('l1b', '書いた本', pre)), ang=-4)
        return finish(im, gt, 0.04, src='地図・本の絵：内容を伏せたイメージ（参考：2000年代に出版された東京の地下についての本）')
    im = base('moat.jpg', t - tq, Tt - tq, 0.55, blue=0.4, z0=1.0, z1=1.15)
    bullet(im, 110, 420, '本当に 地図から', t, tq, Mi(80), PALE)
    bullet(im, 110, 580, '消された道は あるのか？', t, tq + 0.6, Mi(96), GOLD)
    return finish(im, gt, 0.2, caption=CAP['moat.jpg'])
def s_rh(t, Tt, gt, pre):
    im = base('passage1.jpg', t, Tt, 0.4, z0=1.15, z1=1.35, blur=5)
    alpha_text(im, (W / 2, 420), 'でも、このうわさには', Mi(90), PALE, appear(t, 0.1, 0.5))
    alpha_text(im, (W / 2, 620), '気になる「しるし」がある', Mi(120), GOLD, appear(t, at('rh', '気になる', pre), 0.5))
    return finish(im, gt, 0.35, caption=CAP['passage1.jpg'])
def s_l2(t, Tt, gt, pre):
    tc = at('l2', '千代田線', pre); tb = at('l2', 'ビルなら', pre); tu = at('l2', 'うわさでは', pre)
    if t < tc:
        im = base('kplat.jpg', t, tc, 0.6, blue=0.4, z0=1.0, z1=1.12)
        header(im, 2, '深すぎる駅', t)
        bullet(im, 110, 330, '国会議事堂のすぐそば', t, at('l2', '国会議事堂の', pre), Mi(62), PALE)
        bullet(im, 110, 470, '地下鉄の 国会議事堂前駅', t, at('l2', '地下鉄の', pre), Mi(80), GOLD)
        return finish(im, gt, 0.1, caption=CAP['kplat.jpg'])
    if t < tu:
        im = Image.new('RGB', (W, H)); u = (t - tc) / 2.5
        T.section(im, 40, 230, 17.5, gt, show=('chiyoda', 'bldg'), chi_u=u, labels=True)
        header(im, 2, '深すぎる駅', t)
        alpha_text(im, (1350, 330), '千代田線のホーム', Mi(54), PALE, appear(t, tc), sw=2)
        alpha_text(im, (1350, 450), '地下 およそ38m', Mi(100), GOLD, appear(t, at('l2', '三十八', pre)), sw=3)
        alpha_text(im, (1350, 580), 'ビル12階ぶんくらい', Mi(56), ICE, appear(t, tb), sw=2)
        if t > at('l2', '東京メトロ', pre):
            d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, at('l2', '東京メトロ', pre))
            d.rounded_rectangle((900, 940, 1800, 1030), 20, fill=(8, 10, 18, int(230 * a)), outline=GOLD + (int(255 * a),), width=4)
            alpha_text(im, (1350, 985), '東京メトロで いちばん深いホーム', Mi(50), GOLD, a, sw=0)
        return finish(im, gt, 0.0, src='深さ 37.9m（千代田線ホーム）。ビルの階数は1階 約3.1mとした目安')
    im = base('esc.jpg', t - tu, Tt - tu, 0.55, blue=0.45, z0=1.0, z1=1.2, cy0=0.6, cy1=0.75)
    bullet(im, 110, 300, 'こんなに深いのは…', t, tu, Mi(70), PALE)
    bullet(im, 110, 460, 'いざというときの', t, at('l2', 'いざ', pre), Mi(70), PALE)
    bullet(im, 110, 620, 'シェルターだから？', t, at('l2', 'シェルター', pre), Mi(120), GOLD)
    return finish(im, gt, 0.15, caption=CAP['esc.jpg'] + '（となりの駅）')
def s_l2b(t, Tt, gt, pre):
    tk = at('l2b', '近くの駅', pre); tg = at('l2b', '議員の事務所が入るビルには', pre)
    if t < tk:
        im = base('kplat2.jpg', t, tk, 0.6, blue=0.4, z0=1.0, z1=1.15, cx0=0.4, cx1=0.5)
        bullet(im, 110, 260, 'しかも 丸ノ内線のホームは', t, 0.2, Mi(62), PALE)
        bullet(im, 110, 400, '国会議事堂の敷地の 真下', t, at('l2b', '国会議事堂の', pre), Mi(84), GOLD)
        return finish(im, gt, 0.1, caption=CAP['kplat2.jpg'], src='参考：旅行ライター向けサイト tabi-mag.jp ほか')
    if t < tg:
        im = R.darkbg(W, H, (14, 20, 34)).copy(); P = T.areamap(im, 0.75, lines_a=0.25, S=75000, center=(35.6752, 139.7440), cy=H * 0.5 - 40, labels=('国会議事堂', '総理大臣官邸', '議員会館'), line_names=False)
        # 駅（丸）と、それをつなぐ地下の線
        nodes = ['国会議事堂前駅', '国会議事堂', '総理大臣官邸', '議員会館', '永田町駅']; d = ImageDraw.Draw(im, 'RGBA')
        for nm in ('国会議事堂前駅', '永田町駅'):
            x, y = P(*T.PL[nm]); d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(20, 20, 30, 255), outline=ICE + (255,), width=5); alpha_text(im, (x + 36, y), nm, Fb(34), ICE, 1.0, anchor='lm', sw=2)
        u = (t - tk) / 3.0; pairs = [('国会議事堂前駅', '国会議事堂'), ('国会議事堂前駅', '議員会館'), ('国会議事堂前駅', '総理大臣官邸'), ('永田町駅', '国会議事堂')]
        g = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for i, (p, q) in enumerate(pairs):
            k = fade(u * len(pairs) - i)
            if k <= 0: continue
            (x0, y0), (x1, y1) = P(*T.PL[p]), P(*T.PL[q]); T.dashed(gd, [(x0, y0), (x0 + (x1 - x0) * k, y0 + (y1 - y0) * k)], ICE + (255,), 7, ph=gt)
        im.paste(g.convert('RGB'), (0, 0), g)
        alpha_text(im, (W / 2, 980), '地下の通路で つながっている…とも', Mi(70), GOLD, appear(t, tk + 0.5))
        return finish(im, gt, 0.04, src=MAPSRC + '。点線は「つながっている」と言われる様子のイメージ')
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im, 'RGBA'); yg = 520; fh = 72
    T.section(im, -2000, yg, 1, gt, show=(), labels=False)
    bx = 700; bw = 520; a = appear(t, tg, 0.6)
    for f in range(12):
        y = yg - (f + 1) * 34; d.rectangle((bx, y, bx + bw, y + 32), fill=(36, 44, 64, int(255 * a)), outline=(80, 95, 125, int(255 * a)))
    for f in range(5):
        k = appear(t, tg + 0.8 + f * 0.35, 0.3)
        if k <= 0: continue
        y = yg + f * fh; d.rectangle((bx, y + 4, bx + bw, y + fh), fill=(60, 40, 30, int(255 * k)), outline=GOLD + (int(255 * k),), width=3)
        alpha_text(im, (bx + bw / 2, y + fh / 2 + 2), f'地下{f + 1}階', Fb(36), GOLD, k, sw=0)
    alpha_text(im, (W / 2, 70), '議員の事務所が入るビル', Mi(64), PALE, a)
    alpha_text(im, (1500, 700), '地下5階まで', Mi(100), GOLD, appear(t, at('l2b', '地下五階', pre)))
    return finish(im, gt, 0.0, src='衆議院第一議員会館：地上12階・地下5階（国土交通省）。図は簡単にしたもの')
def doorscene(t, Tt, gt, open_u=0.0, bright=0.6, name='passage2.jpg', z=(1.0, 1.12)):
    im = base(name, t, Tt, bright, blue=0.45, z0=z[0], z1=z[1], cx0=0.45, cx1=0.5)
    T.door(im, W * 0.42, H * 0.86, 620, open_u); return im
def s_l3(t, Tt, gt, pre):
    ti = at('l3', 'いつも', pre); tu = at('l3', 'うわさでは', pre)
    im = doorscene(t, Tt, gt, 0.0 if t < tu else 0.15 * appear(t, at('l3', '続いて', pre), 1.5), 0.55)
    header(im, 3, '開かずの扉', t)
    bullet(im, 80, 280, '通路や ホームのはしの', t, 0.8, Mi(50), PALE)
    bullet(im, 80, 360, '「関係者以外 立入禁止」', t, at('l3', '「関係者', pre), Mi(54), GOLD)
    bullet(im, 1320, 330, 'いつも 閉まったまま', t, ti, Mi(56), ICE)
    if t > tu:
        d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, tu)
        d.rounded_rectangle((W / 2 - 700, 880, W / 2 + 700, 1010), 24, fill=(8, 10, 18, int(220 * a)), outline=GOLD + (int(255 * a),), width=4)
        alpha_text(im, (W / 2, 945), 'その先は 秘密の通路へ…？', Mi(72), GOLD, a)
    return finish(im, gt, 0.15, caption=DOORIMG + CAP['passage2.jpg'])
def s_quiz(t, Tt, gt, pre):
    ts = at('quiz', '一、', pre)
    im = base('passage1.jpg', t, Tt, 0.4, blue=0.5, z0=1.1, z1=1.25, blur=3)
    alpha_text(im, (W / 2, 120), 'いちばん あやしいのは どれ？', Mi(84), GOLD, appear(t, at('quiz', '三つの', pre)))
    S.card(im, 260, 300, 1400, 150, 1, '地図にない地下道', appear(t, ts))
    S.card(im, 260, 500, 1400, 150, 2, '深すぎる駅（地下38m）', appear(t, at('quiz', '二、', pre)))
    S.card(im, 260, 700, 1400, 150, 3, '開かずの扉', appear(t, at('quiz', '三、', pre)))
    if t < ts: alpha_text(im, (W / 2, 560), 'あなたも 考えてみて', Mi(96), PALE, appear(t, 0.1) * (1 - appear(t, ts - 0.4, 0.4)))
    return finish(im, gt, 0.15, caption=CAP['passage1.jpg'])
def s_why(t, Tt, gt, pre):
    tm = at('why', '東京メトロは', pre); tma = at('why', '国会議事堂前駅の', pre); tch = at('why', '千代田線は', pre); ta = at('why', 'あとから', pre)
    if t < tm:
        im = base('diet_day.jpg', t, tm, 0.6, blue=0.35, z0=1.0, z1=1.12)
        alpha_text(im, (W / 2, 330), '本当に 秘密の通路はあるの？', Mi(84), PALE, appear(t, 0.1))
        alpha_text(im, (W / 2, 520), '駅が深いのには', Mi(70), PALE, appear(t, at('why', '駅が深い', pre)))
        alpha_text(im, (W / 2, 650), 'はっきりした理由がある', Mi(96), GOLD, appear(t, at('why', 'はっきり', pre)))
        return finish(im, gt, 0.1, caption=CAP['diet_day.jpg'])
    if t < tma:
        im = base('kplat.jpg', t - tm, tma - tm, 0.45, blue=0.45, z0=1.12, z1=1.2, blur=2)
        d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, tm)
        d.rounded_rectangle((260, 380, 1660, 700), 28, fill=(8, 10, 18, int(220 * a)), outline=GOLD + (int(255 * a),), width=4)
        alpha_text(im, (W / 2, 470), '東京メトロの説明', Fb(46), GREY, a, sw=0)
        alpha_text(im, (W / 2, 590), '深さは あくまで「つくり」の問題', Mi(76), GOLD, appear(t, at('why', '深さは', pre)))
        return finish(im, gt, 0.08, caption=CAP['kplat.jpg'], src='参考：tabi-mag.jp「東京の地下鉄は核シェルター？」（東京メトロのコメントとして紹介）')
    im = Image.new('RGB', (W, H))
    show = ['maru']
    if t > tch: show.append('chiyoda')
    if t > at('why', '水道', pre): show.append('pipes')
    T.section(im, 40, 230, 17.5, gt, show=tuple(show), chi_u=(t - tch) / 2.0, maru_u=(t - tma) / 1.5)
    alpha_text(im, (W / 2, 80), '先にできた線の下を 通るしかない', Mi(60), PALE, appear(t, ta))
    if t > ta:
        d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, at('why', 'よけて', pre))
        ax = 1500; d.line((ax, 330, ax, 820), fill=GOLD + (int(255 * a),), width=10); d.polygon([(ax - 34, 800), (ax + 34, 800), (ax, 860)], fill=GOLD + (int(255 * a),))
        alpha_text(im, (ax - 60, 600), 'よけて もっと深く', Mi(56), GOLD, a, anchor='rm', sw=3)
    return finish(im, gt, 0.0, src='断面は簡単にした図。丸ノ内線の深さは目安。管の深さも目安')
def s_why2(t, Tt, gt, pre):
    tn = at('why2', '新しい線', pre); td = at('why2', '深い駅は', pre)
    if t < tn:
        im = R.darkbg(W, H, (14, 20, 34)).copy()
        alpha_text(im, (W / 2, 90), 'いま 東京でいちばん深い駅は？', Mi(66), PALE, appear(t, 0.1))
        T.bars(im, 560, 220, [('千代田線 国会議事堂前', 37.9, (60, 190, 110)), ('大江戸線 六本木', 42.3, (220, 80, 170))], (t - at('why2', '二〇〇〇', pre)) / 2.0, ppm=12, bw=260, gap=300)
        alpha_text(im, (1250, 990), '2000年にできた 大江戸線', Mi(46), ICE, appear(t, at('why2', '二〇〇〇', pre)))
        return finish(im, gt, 0.0, src='深さ：千代田線 国会議事堂前駅 37.9m／大江戸線 六本木駅 42.3m（tabi-mag.jp、Wikipedia）')
    if t < td:
        im = Image.new('RGB', (W, H)); T.section(im, 40, 230, 15.5, gt, show=('maru', 'chiyoda', 'pipes'), roppongi=(t - tn) / 1.5)
        alpha_text(im, (W / 2, 80), '新しい線ほど 深くなる', Mi(80), GOLD, appear(t, tn))
        return finish(im, gt, 0.0, src='断面は簡単にした図（駅の場所はそれぞれちがいます）')
    im = base('esc.jpg', t - td, Tt - td, 0.5, blue=0.45, z0=1.2, z1=1.05)
    bullet(im, 110, 300, '深い駅は 秘密のしるしではなく', t, td, Mi(62), PALE)
    bullet(im, 110, 450, '地下が こみ合っているしるし', t, at('why2', '東京の地下が', pre), Mi(84), GOLD)
    return finish(im, gt, 0.1, caption=CAP['esc.jpg'])
def s_now1(t, Tt, gt, pre):
    tw = at('now1', '国会議事堂前駅と', pre); td = at('now1', '開かずの', pre)
    if t < tw:
        im = base('diet2.jpg', t, tw, 0.7, blue=0.2, z0=1.12, z1=1.0)
        alpha_text(im, (W / 2, 140), 'いま、この場所は？', Mi(80), PALE, appear(t, 0.1)); return finish(im, gt, 0.05, caption=CAP['diet2.jpg'])
    if t < td:
        im = base('passage2.jpg', t - tw, td - tw, 0.7, blue=0.2, z0=1.0, z1=1.1)
        S.card(im, 160, 640, 1600, 170, 1, '国会議事堂前駅 ⇔ 溜池山王駅', appear(t, tw), sub='1997年から 地下の通路でつながる')
        bullet(im, 160, 900, 'だれでも 歩ける', t, at('now1', 'だれでも', pre), Mi(66), GOLD)
        return finish(im, gt, 0.04, caption='写真：地下鉄の駅をつなぐ通路（イメージ：虎ノ門）Real Estate Japan', src='参考：Wikipedia「Kokkai-gijidō-mae Station」')
    im = doorscene(t - td, Tt - td, gt, 0.0, 0.5, z=(1.12, 1.2))
    alpha_text(im, (W / 2, 120), '開かずの扉の多くは…', Mi(70), PALE, appear(t, td))
    for i, (s, key) in enumerate((('電気の設備', '電気'), ('空気を入れかえる設備', '空気'), ('非常のときの通路', '非常'))):
        a = appear(t, at('now1', key, pre))
        if a <= 0: continue
        x = 140 if i != 1 else 1300; y = 360 + (i % 2) * 260 if i != 2 else 820
        if i == 2: x = 140
        d = ImageDraw.Draw(im, 'RGBA'); d.rounded_rectangle((x, y - 60, x + 520, y + 60), 20, fill=(8, 10, 18, int(220 * a)), outline=GOLD + (int(255 * a),), width=4)
        alpha_text(im, (x + 260, y), s, Mi(46), PALE, a, sw=0)
    return finish(im, gt, 0.1, caption=DOORIMG + CAP['passage2.jpg'])
def s_now2(t, Tt, gt, pre):
    tb = at('now2', 'でも', pre); tn = at('now2', 'それでも', pre)
    if t < tb:
        im = base('diet2.jpg', t, tb, 0.85, blue=0.1, z0=1.0, z1=1.1)
        S.card(im, 160, 700, 1600, 170, 1, '国会議事堂は 見学できる', appear(t, 0.2), sub='中を案内してもらえる')
        return finish(im, gt, 0.02, caption=CAP['diet2.jpg'])
    if t < tn:
        im = R.darkbg(W, H, (14, 20, 34)).copy(); P = T.areamap(im, 0.6, lines_a=0.5, cy=H * 0.55, line_names=False)
        T.secretnet(im, P, 1.0, gt, 0.35 * (1 - appear(t, tb + 1.0, 1.5)))
        d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, tb)
        d.rounded_rectangle((W / 2 - 640, 80, W / 2 + 640, 220), 24, fill=(8, 10, 18, int(230 * a)), outline=GOLD + (int(255 * a),), width=4)
        alpha_text(im, (W / 2, 150), '地図にない地下道は 見つかっていない', Mi(66), GOLD, a)
        return finish(im, gt, 0.04, src=MAPSRC)
    im = base('passage1.jpg', t - tn, Tt - tn, 0.55, blue=0.45, z0=1.0, z1=1.3)
    bullet(im, 110, 300, 'それでも 東京の地下では', t, tn, Mi(66), PALE)
    bullet(im, 110, 450, 'いまも 新しいトンネルが…', t, at('now2', '新しい', pre), Mi(84), GOLD)
    return finish(im, gt, 0.15, caption=CAP['passage1.jpg'])
def s_outro(t, Tt, gt, pre):
    tm = at('outro', 'でも', pre); tq = at('outro', 'では', pre)
    if t < tm:
        im = base('passage1.jpg', t, tm, 0.5, blue=0.45, z0=1.0, z1=1.15)
        bullet(im, 110, 260, '正体は 深い駅と 迷路のような地下通路が', t, at('outro', 'その正体', pre), Mi(58), PALE)
        bullet(im, 110, 380, '生んだ うわさ…なのかもしれない', t, at('outro', '生んだ', pre), Mi(58), PALE)
        return finish(im, gt, 0.15, caption=CAP['passage1.jpg'])
    if t < tq:
        im = doorscene(t - tm, tq - tm, gt, 0.35 * appear(t, at('outro', '少しだけ', pre), 1.5), 0.45, z=(1.0, 1.1))
        bullet(im, 110, 200, 'もし いつも閉まっている扉が', t, tm, Mi(60), PALE)
        bullet(im, 110, 320, '少しだけ 開いていたら…', t, at('outro', '少しだけ', pre), Mi(70), GOLD)
        return finish(im, gt, 0.2, caption=DOORIMG + CAP['passage2.jpg'])
    im = doorscene(t - tq, Tt - tq, gt, 0.35, 0.3, z=(1.1, 1.15)); im = im.filter(ImageFilter.GaussianBlur(3))
    alpha_text(im, (W / 2, 110), '最後に、あなたに質問', Mi(60), PALE, appear(t, tq))
    ta = at('outro', 'あなたは', pre)
    alpha_text(im, (110, 330), 'その扉の先へ', Mi(80), PALE, appear(t, ta), anchor='lm'); alpha_text(im, (110, 500), '行ってみたい？', Mi(120), GOLD, appear(t, ta + 0.4), anchor='lm')
    d = ImageDraw.Draw(im, 'RGBA')
    for i, s in enumerate(['行ってみたい', '行かない']):
        a = appear(t, ta + 1.0 + i * 0.3)
        if a > 0:
            x = 110 + i * 420; d.rounded_rectangle((x, 700, x + 380, 800), 20, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x + 190, 750), s, Mi(50), PALE + (int(255 * a),))
    bullet(im, 110, 900, 'コメントで教えてください', t, at('outro', 'コメント', pre), Fo(44), PALE)
    return finish(im, gt, 0.2, caption=DOORIMG + CAP['passage2.jpg'])
def s_end(t, Tt, gt, pre):
    im = base('maru_night.jpg', t, Tt, 0.35, z0=1.2, z1=1.25, blur=8); im = vignette(im, 0.6)
    S.endscreen(im, gt, appear(t, 0.0, 0.6)); return im
ORDER = [('hook', s_hook, 0.15, 0.6), ('title', s_title, 0.4, 0.8), ('where', s_where, 0.4, 0.8), ('l1', s_l1, 0.6, 0.6), ('l1b', s_l1b, 0.3, 1.0),
         ('rh', s_rh, 0.3, 0.6), ('l2', s_l2, 0.6, 0.6), ('l2b', s_l2b, 0.3, 1.0), ('l3', s_l3, 0.6, 1.0), ('quiz', s_quiz, 0.4, 2.0), ('why', s_why, 0.5, 0.5),
         ('why2', s_why2, 0.3, 1.0), ('now1', s_now1, 0.5, 0.6), ('now2', s_now2, 0.3, 1.0), ('outro', s_outro, 0.4, 1.2)]
ENDT = 12.0
def plan():
    out = []; off = 0.0
    for k, fn, pre, post in ORDER:
        Tt = pre + D[k] + post; out.append((k, fn, pre, off, Tt)); off += Tt
    out.append(('end', s_end, 0.5, off, ENDT)); off += ENDT
    return out, off
if __name__ == '__main__':
    P, total = plan()
    if len(sys.argv) > 2 and sys.argv[2] == 'still':
        only = sys.argv[3] if len(sys.argv) > 3 else None
        for k, fn, pre, off, Tt in P:
            if only and k != only: continue
            for j, u in enumerate((0.2, 0.45, 0.7, 0.95)):
                fn(Tt * u, Tt, off + Tt * u, pre).convert('RGB').resize((960, 540)).save(f'{G}/still/{k}_{j}.jpg', quality=85)
        print('stills', total); sys.exit()
    part = int(sys.argv[2]) if len(sys.argv) > 2 else None
    json.dump({'scenes': [(k, off, Tt, pre) for k, fn, pre, off, Tt in P], 'total': total}, open(f'{G}/main_plan.json', 'w'))
    n = int(round(total * 30)); rng_ = range(n) if part is None else (range(0, n // 2) if part == 0 else range(n // 2, n))
    p = R.writer(f'{G}/main_video{"" if part is None else part}.mp4', W, H); idx = 0
    for i in rng_:
        gt = i / 30
        while idx + 1 < len(P) and gt >= P[idx + 1][3]: idx += 1
        k, fn, pre, off, Tt = P[idx]
        p.stdin.write(fn(gt - off, Tt, gt, pre).convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('main video', total)
