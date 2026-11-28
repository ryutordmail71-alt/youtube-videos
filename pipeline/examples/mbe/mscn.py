"""幻の駅：本編の場面（python3 mscn.py main [still [key]]）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, CYAN, ICE, ctext, ease, fade, kb, fog, vignette, alpha_text
import mdraw as M
import pcont as C
G = '/home/claude/mbe'; D = json.load(open(f'{G}/dur.json')); W, H = 1920, 1080
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
def finish(im, gt, fogk=0.22, caption=None, src=None):
    fog(im, gt, fogk); vignette(im, 0.8); d = ImageDraw.Draw(im, 'RGBA')
    if caption: cap(im, caption)
    if src: d.text((24, 1040), src, font=Fb(22), fill=(180, 185, 195), anchor='ls')
    R.note(d, W, H); return im
CAP = {'05.jpg': '写真：地下鉄のトンネル（イメージ）', '03.jpg': '写真：東京駅のホーム（イメージ）', '16.jpg': '写真：使われなくなった地下鉄の駅（イメージ：東京ではありません）',
       '18.jpg': '写真：地下鉄のトンネル（イメージ：東京ではありません）', '21c.jpg': '写真：使われなくなった地下の駅（イメージ：東京ではありません）',
       '28.jpg': '写真：地下のトンネル工事（イメージ：東京ではありません）', '02c.jpg': '写真：日本の駅のホーム（イメージ）'}
WIN = '絵：電車の窓（イメージ）　'
def win(t, gt, photo, p0, p1):
    u = (t - p0) / (p1 - p0) if p1 > p0 else None
    return M.window(W, H, gt, photo, u)
# ---------- 各場面 ----------
def s_hook(t, T, gt, pre):
    if t < 0.3:   # 結果のチラ見せ：窓の外の幻のホーム
        im = M.window(W, H, gt, '16.jpg', 0.45); ctext(ImageDraw.Draw(im), (W / 2, 540), '幻の駅', Mi(190), GOLD, sw=5); return finish(im, gt, 0.15)
    im = win(t, gt, '16.jpg', 0.25, at('hook', '明かり', pre) + 3.0)
    alpha_text(im, (110, 200), '東京の地下鉄', Mi(70), PALE, appear(t, 0.3, 0.3), anchor='lm')
    alpha_text(im, (110, 330), '窓に 一瞬だけ見える', Mi(90), PALE, appear(t, 0.35, 0.3), anchor='lm')
    alpha_text(im, (110, 470), '明かりの消えたホーム', Mi(110), GOLD, appear(t, 0.35, 0.3), anchor='lm')
    bullet(im, 110, 780, 'だれも乗り降りしない駅', t, at('hook', 'そこは', pre), Mi(70), ICE)
    alpha_text(im, (W - 110, 900), '「幻の駅」', Mi(140), GOLD, appear(t, at('hook', '「幻', pre), 0.4), anchor='rm')
    return finish(im, gt, 0.12, caption=WIN + CAP['16.jpg'])
def band(im, name, y, h, t, T, a=1.0):
    src = R.photo(name, W, h, bright=0.8, blue=0.3, over=1.0); u = t / max(T, 1)
    x0 = (src.width - W) * (0.2 + 0.6 * u)
    part = src.crop((int(x0), int((src.height - h) / 2), int(x0) + W, int((src.height - h) / 2) + h))
    if a < 1: im.paste(Image.blend(im.crop((0, y, W, y + h)), part, a), (0, y))
    else: im.paste(part, (0, y))
    d = ImageDraw.Draw(im, 'RGBA'); d.line((0, y, W, y), fill=GOLD + (int(160 * a),), width=2); d.line((0, y + h, W, y + h), fill=GOLD + (int(160 * a),), width=2)
def s_title(t, T, gt, pre):
    im = R.darkbg(W, H, (16, 26, 44)).copy(); band(im, '03.jpg', 560, 330, t, T, appear(t, 0.0, 1.0))
    alpha_text(im, (W / 2, 140), '都市伝説', Mi(64), GREY, appear(t, 0.1), sw=0)
    alpha_text(im, (W / 2, 300), '東京の地下鉄の「幻の駅」', Mi(120), PALE, appear(t, 0.3, 0.8))
    alpha_text(im, (W / 2, 450), 'GHOST STATIONS OF TOKYO', BE(90), GOLD, appear(t, 0.8, 0.8), sw=0)
    alpha_text(im, (W / 2, 960), 'いまも地下に眠っている駅', Mi(58), PALE, appear(t, at('title', 'いまも', pre), 0.6))
    return finish(im, gt, 0.18, caption=CAP['03.jpg'])
def s_where(t, T, gt, pre):
    tl = at('where', '浅草から', pre)
    im = R.darkbg(W, H, (12, 22, 40)).copy()
    if t < tl:
        u = ease(t / max(tl - 0.3, 1)); sc = 40 + 260 * u; lat0 = 36.5 + (35.7 - 36.5) * u; lon0 = 137.5 + (139.6 - 137.5) * u
        P = M.asia(im, W * 0.58, H * 0.52, sc, lat0=lat0, lon0=lon0); d = ImageDraw.Draw(im, 'RGBA')
        jx, jy = P(37.5, 139.0); alpha_text(im, (jx + 60, jy - 40), '日本', Mi(80), PALE, appear(t, 0.3) * (1 - u), sw=0)
        x, y = P(*M.TOKYO); r = 20 + 10 * math.sin(gt * 3); a3 = appear(t, at('where', '東京', pre))
        d.ellipse((x - r, y - r, x + r, y + r), outline=GOLD + (int(255 * a3),), width=5); d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=GOLD + (int(255 * a3),))
        alpha_text(im, (x - 30, y - 60), '東京', Mi(80), GOLD, a3, anchor='rm')
        alpha_text(im, (W / 2, 80), '舞台は 日本の首都・東京', Mi(60), PALE, appear(t, 0.3), sw=0)
        bullet(im, 110, 940, '真ん中を走る 地下鉄「銀座線」', t, at('where', 'その真ん中', pre), Mi(60), ICE)
        return finish(im, gt, 0.1, src='地図：Natural Earth')
    q = t - tl
    M.line_map(im, gt, 160, 1760, 470, a=appear(q, 0, 0.4), show=q / 2.0, ghosts=[(k, appear(t, at('where', 'この線には', pre) + i * 0.4)) for i, k in enumerate(('omote', 'shinbashi', 'mansei'))])
    alpha_text(im, (W / 2, 120), '銀座線　約14km', Mi(80), ORANGE_T, appear(q, 0.3))
    bullet(im, 110, 760, '1927年 上野〜浅草で開業', t, at('where', '一九二七', pre), Mi(60), PALE)
    bullet(im, 110, 870, 'アジアで最初の地下鉄', t, at('where', 'アジア', pre), Mi(76), GOLD)
    bullet(im, 1000, 870, '使われなくなった駅が いくつも', t, at('where', 'この線には', pre), Mi(52), ICE)
    return finish(im, gt, 0.08, src='簡略化した路線図（駅の間かくは実際とちがいます）')
ORANGE_T = (250, 175, 60)
def s_l1(t, T, gt, pre):
    tw = at('l1', 'うわさでは', pre)
    if t < tw:
        im = R.darkbg(W, H, (14, 20, 34)).copy(); u = ease(t / 2.5)
        x0 = 160 + (-2512 - 160) * u; x1 = 1760 + (2488 - 1760) * u   # 神田〜末広町に寄る
        M.line_map(im, gt, x0, x1, 560, ghosts=[('mansei', appear(t, at('l1', '昔', pre)))], focus=True)
        header(im, 1, '神田と末広町のあいだの 消えたホーム', t)
        bullet(im, 110, 250, '秋葉原の近く・万世橋のあたり', t, at('l1', '秋葉原', pre), Mi(54), PALE)
        bullet(im, 110, 820, '1930年1月 〜 1931年11月', t, at('l1', '一九三〇', pre), Mi(66), ICE)
        bullet(im, 110, 930, '神田駅ができるまでの「仮の駅」　使われたのは 2年たらず', t, at('l1', '神田駅が', pre), Mi(54), GOLD)
        return finish(im, gt, 0.1, src='簡略化した路線図（駅の間かくは実際とちがいます）')
    im = win(t, gt, '18.jpg', at('l1', '暗やみ', pre) - 0.5, at('l1', '暗やみ', pre) + 4.0)
    header(im, 1, '神田と末広町のあいだの 消えたホーム', t)
    bullet(im, 110, 300, 'うわさでは…', t, tw + 0.1, Mi(60), GREY)
    bullet(im, 110, 430, '窓に顔を近づけていると', t, at('l1', 'この区間', pre), Mi(66), PALE)
    bullet(im, 110, 800, '暗やみに 古いホームのような影が', t, at('l1', '暗やみ', pre), Mi(76), GOLD)
    return finish(im, gt, 0.15, caption=WIN + CAP['18.jpg'])
def s_l2(t, T, gt, pre):
    im = base_photo('05.jpg', t, T, 0.45, z0=1.0, z1=1.2, blur=2)
    header(im, 2, '8か月だけの駅', t)
    bullet(im, 110, 240, '新橋駅の地下の もう一つの新橋駅', t, at('l2', '新橋駅の地下', pre), Mi(62), PALE)
    bullet(im, 110, 360, '1939年　別の鉄道会社の終点として', t, at('l2', '一九三九', pre), Mi(56), ICE)
    tm = at('l2', '使われたのは', pre); a = appear(t, tm)
    if a > 0:
        M.months(im, 160, 520, 1600, (t - at('l2', '一月', pre)) / max(0.1, at('l2', 'わずか', pre) - at('l2', '一月', pre)), a)
        alpha_text(im, (160 + 1600 / 24, 470), '1/15', Fb(34), GOLD, a); alpha_text(im, (160 + 1600 * 8.5 / 12, 470), '9/15', Fb(34), GOLD, appear(t, at('l2', '九月', pre)))
    alpha_text(im, (W / 2, 790), 'わずか 8か月', Mi(120), GOLD, appear(t, at('l2', 'わずか', pre), 0.3))
    bullet(im, 110, 940, '2つの会社の電車が直通 → ホームは役目を終えた', t, at('l2', '二つの', pre), Mi(54), PALE)
    return finish(im, gt, 0.12, caption=CAP['05.jpg'])
def s_l2b(t, T, gt, pre):
    im = base_photo('16.jpg', t, T, 0.5, z0=1.05, z1=1.2, cx0=0.4, cx1=0.55)
    tl = at('l2b', 'だれもいない', pre); a = appear(t, tl, 1.5) * (0.75 + 0.25 * math.sin(gt * 2.2))
    if a > 0: R.glow(im, 1400, 420, 260, (255, 225, 160), 90 * a)
    header(im, 2, '8か月だけの駅', t)
    bullet(im, 110, 260, 'ホームは こわされずに 地下に残った', t, 0.3, Mi(60), PALE)
    bullet(im, 110, 400, '戦争中、一度だけ', t, at('l2b', '戦争中', pre), Mi(76), ICE)
    bullet(im, 110, 520, 'ふたたび営業に使われたと伝えられる', t, at('l2b', 'ふたたび', pre), Mi(56), PALE)
    bullet(im, 110, 800, 'だれもいないはずのホームに', t, tl, Mi(66), PALE)
    bullet(im, 110, 920, '明かりがついていた…？（うわさ）', t, at('l2b', '明かりが', pre), Mi(76), GOLD)
    return finish(im, gt, 0.2, caption=CAP['16.jpg'])
def s_rh(t, T, gt, pre):
    im = base_photo('18.jpg', t, T, 0.3, z0=1.25, z1=1.45, blur=6)
    alpha_text(im, (W / 2, 420), 'でも、幻の駅は', Mi(110), PALE, appear(t, 0.1, 0.5)); alpha_text(im, (W / 2, 620), 'ここだけではない', Mi(150), GOLD, appear(t, 1.0, 0.5))
    return finish(im, gt, 0.35, caption=CAP['18.jpg'])
def s_l3(t, T, gt, pre):
    tn = at('l3', '夜の電車', pre)
    if t < at('l3', '開業は', pre):
        im = R.darkbg(W, H, (14, 20, 34)).copy()
        M.line_map(im, gt, -2183, 1517, 760, show=1.0, labels=True, keisei=appear(t, at('l3', '上野公園', pre), 0.8), focus=True)
        header(im, 3, '動物園の下の駅', t)
        bullet(im, 110, 260, '上野公園の地下', t, at('l3', '上野公園', pre), Mi(60), PALE)
        bullet(im, 110, 380, '京成線「博物館動物園駅」', t, at('l3', '「博物館', pre), Mi(70), GOLD)
        return finish(im, gt, 0.1, src='簡略化した路線図（駅の間かくは実際とちがいます）')
    if t < tn:
        im = base_photo('21c.jpg', t, tn, 0.5, z0=1.0, z1=1.15)
        header(im, 3, '動物園の下の駅', t)
        Y = [('1933年', '開業', '開業は'), ('1997年', 'ホームが短く、電車が止まらなくなる', '一九九七'), ('2004年', '正式に廃止', '二〇〇四')]
        for i, (y, s, k) in enumerate(Y):
            a = appear(t, at('l3', k, pre))
            alpha_text(im, (130, 300 + i * 200), y, Mi(90), GOLD, a, anchor='lm'); alpha_text(im, (520, 300 + i * 200), s, Mi(58), PALE, a, anchor='lm')
        return finish(im, gt, 0.15, caption=CAP['21c.jpg'])
    im = win(t, gt, '21c.jpg', tn - 0.2, tn + 3.5)
    header(im, 3, '動物園の下の駅', t)
    bullet(im, 110, 760, '夜の電車の窓から', t, tn, Mi(60), PALE)
    bullet(im, 110, 880, '白くぼんやり光るホームが…？', t, at('l3', '白く', pre), Mi(76), GOLD)
    return finish(im, gt, 0.15, caption=WIN + CAP['21c.jpg'])
def s_now1(t, T, gt, pre):
    im = base_photo('28.jpg', t, T, 0.35, z0=1.1, z1=1.25, blur=4)
    alpha_text(im, (W / 2, 100), 'いま、これらの駅は？', Mi(72), PALE, appear(t, 0.1))
    M.card(im, 110, 220, 1700, 170, 1, '2008年「選奨土木遺産」に選ばれた', appear(t, at('now1', '万世橋', pre)), sub='万世橋駅のあたりの アーチ型のトンネル')
    M.card(im, 110, 440, 1700, 170, 2, '倉庫や会議室に', appear(t, at('now1', '新橋', pre)), sub='幻の新橋駅のホーム')
    M.card(im, 110, 660, 1700, 170, 3, '電車を止めておく場所に', appear(t, at('now1', 'となりの', pre)), sub='となりの線路')
    bullet(im, W / 2, 950, 'ふだんは 一般の人は入れない', t, at('now1', 'ふだんは', pre), Mi(62), GOLD, 'mm')
    return finish(im, gt, 0.12, caption=CAP['28.jpg'])
def s_now2(t, T, gt, pre):
    th = at('now2', 'そして', pre)
    if t < th:
        im = R.darkbg(W, H, (14, 20, 34)).copy(); d = ImageDraw.Draw(im, 'RGBA'); a = appear(t, 0.3)
        y = 560; d.line((200, y, 1720, y), fill=ORANGE_T + (int(255 * a),), width=16)
        xn, xo = 1400, 640; d.ellipse((xn - 22, y - 22, xn + 22, y + 22), fill=(245, 245, 245, int(255 * a)), outline=(60, 40, 10, 255), width=4)
        alpha_text(im, (xn, y + 80), 'いまの表参道駅', Mi(56), PALE, a)
        ao = appear(t, at('now2', '一九七八', pre)); rr = 24 + 6 * math.sin(gt * 3)
        d.ellipse((xo - rr, y - rr, xo + rr, y + rr), outline=GOLD + (int(255 * ao),), width=5); alpha_text(im, (xo, y + 80), '旧ホーム（1978年まで）', Mi(56), GOLD, ao)
        alpha_text(im, (200, y - 70), '← 渋谷', Fo(40), GREY, a, anchor='lm')
        am = appear(t, at('now2', 'およそ', pre))
        if am > 0:
            d.line((xo, y - 90, xo + (xn - xo) * am, y - 90), fill=ICE + (255,), width=5); alpha_text(im, ((xo + xn) / 2, y - 150), '約180m', Mi(80), ICE, am)
        alpha_text(im, (W / 2, 140), '銀座線 表参道駅にも 幻のホーム', Mi(70), PALE, appear(t, 0.1))
        bullet(im, W / 2, 900, 'いまは 資材置き場', t, at('now2', '資材', pre), Mi(76), GOLD, 'mm')
        return finish(im, gt, 0.1, src='簡略化した図（距離は目安）')
    im = base_photo('21c.jpg', t - th, T - th, 0.6, z0=1.25, z1=1.4, cx0=0.3, cx1=0.4, cy0=0.45, cy1=0.4)
    bullet(im, 110, 260, '博物館動物園駅', t, th, Mi(90), GOLD)
    bullet(im, 110, 420, '2018年　駅の建物を修理', t, at('now2', '二〇一八', pre), Mi(66), PALE)
    bullet(im, 110, 540, '見学のイベントなどで 公開されるように', t, at('now2', '見学', pre), Mi(60), ICE)
    return finish(im, gt, 0.12, caption=CAP['21c.jpg'])
def s_why(t, T, gt, pre):
    im = R.darkbg(W, H, (16, 22, 36)).copy(); im = M.window(W, H, gt * 0.4, None, None, 0.35)
    d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((0, 0, W, H), fill=(5, 8, 15, 170))
    alpha_text(im, (W / 2, 120), 'なぜ、駅は「幻」になる？', Mi(80), PALE, appear(t, 0.1))
    M.card(im, 160, 260, 1600, 160, 1, '線をのばすまでの「つなぎ」の駅', appear(t, at('why', '一つ目', pre)), sub='万世橋駅')
    M.card(im, 160, 470, 1600, 160, 2, '別々の会社の線が 1本につながった', appear(t, at('why', '二つ目', pre)), sub='幻の新橋駅')
    M.card(im, 160, 680, 1600, 160, 3, 'ホームが短く 長い電車が止まれない', appear(t, at('why', '三つ目', pre)), sub='博物館動物園駅')
    bullet(im, W / 2, 950, '表参道：新しい路線ができたときに 場所を移した', t, at('why', '表参道', pre), Mi(52), ICE, 'mm')
    return finish(im, gt, 0.12, caption='絵：電車の窓（イメージ）')
def s_outro(t, T, gt, pre):
    tq = at('outro', 'では', pre)
    if t < tq:
        im = base_photo('05.jpg', t, tq, 0.55, z0=1.0, z1=1.18)
        bullet(im, 110, 300, '幻の駅の正体は 幽霊ではなく', t, 0.2, Mi(66), PALE)
        bullet(im, 110, 440, '町が変わってきた 歴史のあと', t, at('outro', '町が', pre), Mi(84), GOLD)
        bullet(im, 110, 800, 'でも 一瞬だけ見えるホームは…', t, at('outro', 'でも', pre), Mi(60), ICE)
        bullet(im, 110, 920, '少しだけ、こわい', t, at('outro', '少しだけ', pre), Mi(76), PALE)
        return finish(im, gt, 0.15, caption=CAP['05.jpg'])
    im = base_photo('16.jpg', t - tq, T - tq, 0.4, z0=1.05, z1=1.3, cx0=0.6, cx1=0.65)
    alpha_text(im, (W / 2, 110), '最後に、あなたに質問', Mi(60), PALE, appear(t, tq))
    bullet(im, 110, 300, 'もし 見学できる日が来たら', t, at('outro', 'もし', pre), Mi(66), PALE)
    ta = at('outro', 'あなたは、幻', pre)
    alpha_text(im, (110, 470), 'あなたは 幻の駅に', Mi(80), PALE, appear(t, ta), anchor='lm'); alpha_text(im, (110, 620), '行ってみたい？', Mi(130), GOLD, appear(t, ta + 0.3), anchor='lm')
    d = ImageDraw.Draw(im, 'RGBA')
    for i, s in enumerate(['行きたい', '行かない']):
        a = appear(t, ta + 0.9 + i * 0.3)
        if a > 0:
            x = 110 + i * 380; d.rounded_rectangle((x, 780, x + 340, 880), 20, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x + 170, 830), s, Mi(54), PALE + (int(255 * a),))
    bullet(im, 900, 830, 'コメントで教えてください', t, at('outro', 'コメント', pre), Fo(44), PALE)
    return finish(im, gt, 0.25, caption=CAP['16.jpg'])
ORDER = [('hook', s_hook, 0.15, 0.6), ('title', s_title, 0.4, 0.8), ('where', s_where, 0.4, 0.8), ('l1', s_l1, 0.6, 1.0), ('l2', s_l2, 0.6, 0.8), ('l2b', s_l2b, 0.3, 1.0),
         ('rh', s_rh, 0.3, 0.6), ('l3', s_l3, 0.6, 1.0), ('now1', s_now1, 0.5, 1.0), ('now2', s_now2, 0.4, 1.0), ('why', s_why, 0.4, 1.0), ('outro', s_outro, 0.4, 2.4)]
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
