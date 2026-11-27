"""ポリビアス：本編の場面（python3 pscn.py main [only_scene] [still]）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, CYAN, ICE, ctext, ease, fade, kb, fog, vignette, cabinet, alpha_text, shadow_text
import pcont as C
G = '/home/claude/plb'; D = json.load(open(f'{G}/dur.json')); W, H = 1920, 1080
PL = f'{G}/ph/p_d1a8.jpg'; PS = f'{G}/ph/p_46c1.jpg'
def at(key, sub, pre):
    s = C.NAR[key]; i = s.index(sub); return pre + D[key] * i / len(s)
def appear(t, t0, d=0.5): return ease((t - t0) / d)
# ---------- 場面の部品 ----------
def header(im, no, title, t):
    a = appear(t, 0.0, 0.6); d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 0, W, 150), fill=(0, 0, 0, int(150 * a)))
    alpha_text(im, (70, 58), f'言い伝え その{no}', Fb(40), GOLD, a, anchor='lm', sw=0)
    alpha_text(im, (70, 112), title, Mi(54), PALE, a, anchor='lm', sw=0)
def bullet(im, x, y, txt, t, t0, f=None, col=PALE, anchor='lm'):
    a = appear(t, t0, 0.6)
    if a <= 0: return
    alpha_text(im, (x + (1 - a) * 30, y), txt, f or Mi(58), col, a, anchor=anchor)
def base_photo(name, t, T, dark=0.62, **kw):
    im = kb(name, W, H, t / max(T, 1), bright=dark, **kw).copy(); return im
def finish(im, gt, fogk=0.22, image_tag=False):
    fog(im, gt, fogk); vignette(im, 0.8); d = ImageDraw.Draw(im, 'RGBA')
    if image_tag: R.tag_image(d, W, H)
    R.note(d, W, H); return im
# ---------- 各場面 ----------
def s_hook(t, T, gt, pre):
    if t < 0.3:   # 結果のチラ見せ：消えていくゲーム機
        im = R.darkbg(W, H, (30, 40, 60)).copy(); cabinet(im, W * 0.5, 980, 820, gt, 1.0, 0.5); ctext(ImageDraw.Draw(im), (W / 2, 130), '…消えた', Mi(90), PALE, sw=4)
        return finish(im, gt, 0.25)
    im = base_photo('06.jpg', t, T, 0.75, z0=1.0, z1=1.15, cx0=0.5, cx1=0.55)
    a_gone = fade((t - at('hook', '数週間後', pre) - 0.6) / 2.0)
    cabinet(im, 1450, 1000, 760, gt, 1.0, 1 - a_gone)
    alpha_text(im, (110, 220), '1981年　アメリカ', Mi(70), PALE, appear(t, 0.35, 0.3), anchor='lm')
    f = appear(t, 0.35, 0.3)
    alpha_text(im, (110, 400), '遊ぶと', Mi(110), PALE, f, anchor='lm'); alpha_text(im, (110, 560), 'おかしくなる', Mi(150), GOLD, f, anchor='lm')
    alpha_text(im, (110, 720), 'ゲームがあった', Mi(110), PALE, f, anchor='lm')
    bullet(im, 110, 880, '数週間後、あとかたもなく消えた', t, at('hook', '数週間後', pre), Mi(62), ICE)
    return finish(im, gt, 0.18, True)
def s_title(t, T, gt, pre):
    im = R.darkbg(W, H, (16, 26, 44)).copy(); cabinet(im, 1380, 1010, 860, gt, ease(t / 1.2))
    alpha_text(im, (520, 300), '都市伝説', Mi(70), GREY, appear(t, 0.1), sw=0)
    alpha_text(im, (520, 500), 'ポリビアス', Mi(190), PALE, appear(t, 0.3, 0.8))
    alpha_text(im, (520, 680), 'P  O  L  Y  B  I  U  S', BE(110), GOLD, appear(t, 0.8, 0.8), sw=0)
    alpha_text(im, (520, 820), '40年以上 語りつがれる 黒いゲーム機', Mi(48), PALE, appear(t, at('title', '四十年', pre), 0.6))
    return finish(im, gt, 0.25)
PORT = (45.52, -122.68)
def s_where(t, T, gt, pre):
    tsw = at('where', 'うわさでは', pre)
    if t < tsw + 0.6:
        im = R.darkbg(W, H, (12, 22, 40)).copy(); u = ease(t / (tsw - 0.2))
        sc = 24 + 26 * u; c0 = math.cos(math.radians(38))
        # ポートランドを画面の中心へ寄せる
        cxm = W * 0.5 - (PORT[1] + 96) * sc * c0 * u + 0 * (1 - u); cym = H * 0.55 + (PORT[0] - 38) * sc * u
        P = R.usmap(im, cxm, cym, sc, hi=PORT); d = ImageDraw.Draw(im, 'RGBA')
        x, y = P(*PORT)
        a1 = appear(t, at('where', 'アメリカ', pre)); ctext(d, (W / 2, 120), 'アメリカ合衆国', Mi(64), PALE + (int(255 * a1),), sw=0)
        a2 = appear(t, at('where', 'カナダ', pre))
        if a2 > 0:
            cx, cy = P(49.6, -110); ctext(d, (cx, max(60, cy - 40)), '↑ カナダ', Fo(44), GREY + (int(255 * a2),))
        a3 = appear(t, at('where', 'オレゴン', pre))
        if a3 > 0:
            r = 18 + 10 * math.sin(gt * 3); d.ellipse((x - r, y - r, x + r, y + r), outline=GOLD + (int(255 * a3),), width=5); d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=GOLD + (int(255 * a3),))
            alpha_text(im, (x + 60, y - 30), 'オレゴン州', Fo(50), PALE, a3, anchor='lm'); alpha_text(im, (x + 60, y + 40), 'ポートランド', Mi(80), GOLD, appear(t, at('where', 'ポートランド', pre)), anchor='lm')
        im = finish(im, gt, 0.12)
        if t > tsw:
            ph = finish(base_photo(PL, t - tsw, T - tsw, 0.8, z0=1.05, z1=1.18), gt, 0.15)
            im = Image.blend(im, ph, ease((t - tsw) / 0.6))
        return im
    im = base_photo(PL, t - tsw, T - tsw, 0.8, z0=1.05, z1=1.18); d = ImageDraw.Draw(im, 'RGBA')
    alpha_text(im, (110, 200), 'オレゴン州 ポートランド（いまの夜景）', Fo(46), PALE, 1.0, anchor='lm')
    bullet(im, 110, 880, 'うわさ：この町の郊外の ゲームセンター', t, tsw + 0.6, Mi(66), GOLD)
    return finish(im, gt, 0.15)
def s_era(t, T, gt, pre):
    tc = at('era', '子どもたち', pre)
    if t < tc:
        im = base_photo('02.jpg', t, tc, 0.78, z0=1.0, z1=1.1)
        bullet(im, 110, 230, '1981年', t, 0.2, Mi(90), GOLD); bullet(im, 110, 360, 'ゲームセンターの 黄金時代', t, at('era', '黄金', pre), Mi(76))
        bullet(im, 110, 470, '町のあちこちに ゲームセンター', t, at('era', '街の', pre), Mi(56), ICE)
    else:
        im = base_photo('00.jpg', t - tc, T - tc, 0.8, z0=1.0, z1=1.18, cy0=0.35, cy1=0.4)
        bullet(im, 1000, 820, 'コインをにぎりしめて', t, tc + 0.2, Mi(70)); bullet(im, 1000, 930, '新しいゲームに むらがった', t, at('era', '新しい', pre), Mi(60), GOLD)
    return finish(im, gt, 0.15, True)
def s_l1(t, T, gt, pre):
    im = base_photo('06.jpg', t, T, 0.36, z0=1.15, z1=1.25, blur=6)
    a = appear(t, at('l1', '見たことのない', pre) - 0.2, 1.0)
    cabinet(im, 520, 1010, 800 + 30 * ease(t / T), gt, appear(t, at('l1', '画面には', pre), 0.8), a)
    header(im, 1, '見たことのない 黒いゲーム機', t)
    bullet(im, 980, 330, '飾りのない 真っ黒な箱', t, at('l1', '飾り', pre), Mi(62))
    bullet(im, 980, 470, '画面には 光る図形が回る', t, at('l1', '画面には', pre), Mi(62), CYAN)
    bullet(im, 980, 630, '作った会社：Sinneslöschen', t, at('l1', '作った', pre), Fo(50), PALE)
    bullet(im, 980, 700, '（シンネスレッシェン）', t, at('l1', 'シンネス', pre), Fo(40), GREY)
    bullet(im, 980, 830, '意味は「感覚を消す」？', t, at('l1', '意味は', pre), Mi(72), GOLD)
    return finish(im, gt, 0.2, True)
def s_l2(t, T, gt, pre):
    im = base_photo('02.jpg', t, T, 0.55, z0=1.1, z1=1.25, cx0=0.6, cx1=0.45)
    header(im, 2, '遊んだ子どもたちの 異変', t)
    bullet(im, 110, 290, '一度遊ぶと やめられない', t, at('l2', 'このゲームは', pre), Mi(60))
    bullet(im, 110, 400, '毎日 長い行列、けんかまで', t, at('l2', '毎日', pre), Mi(60))
    for i, (s, k) in enumerate([('こわい夢', 'こわい夢'), ('眠れない', '夜、'), ('記憶がとぶ', '記憶')]):
        bullet(im, 110 + i * 560, 600, s, t, at('l2', k, pre), Mi(96), ICE)
    bullet(im, 110, 800, 'やがて、ゲームそのものを こわがるように', t, at('l2', 'やがて', pre), Mi(62), GOLD)
    return finish(im, gt, 0.2, True)
def s_l2b(t, T, gt, pre):
    im = base_photo('07.jpg', t, T, 0.35, z0=1.0, z1=1.12)
    cabinet(im, 1450, 1000, 620, gt * 0.5, ease((t - at('l2b', '画面だけ', pre)) / 2.5), 0.9)
    bullet(im, 110, 300, '電源を入れていないのに…', t, at('l2b', '電源', pre), Mi(70))
    bullet(im, 110, 450, '真夜中、誰もいないお店で', t, at('l2b', '真夜中', pre), Mi(62), GREY)
    bullet(im, 110, 640, '画面だけが ぼんやり光っていた', t, at('l2b', '画面だけ', pre), Mi(70), CYAN)
    return finish(im, gt, 0.28, True)
def s_rh(t, T, gt, pre):
    im = R.darkbg(W, H, (20, 26, 40)).copy()
    alpha_text(im, (W / 2, 380), 'でも…', Mi(90), GREY, appear(t, 0.1))
    alpha_text(im, (W / 2, 580), '本当にぞっとするのは', Mi(110), PALE, appear(t, 0.6, 0.6)); alpha_text(im, (W / 2, 740), 'ここから', Mi(140), GOLD, appear(t, 1.4, 0.6))
    return finish(im, gt, 0.35)
def s_l3(t, T, gt, pre):
    tg = at('l3', '数週間後', pre)
    if t < tg:
        im = base_photo('04.jpg', t, tg, 0.6, z0=1.0, z1=1.3, cx0=0.4, cy0=0.5, cx1=0.55, cy1=0.6)
        # 懐中電灯の光がゆっくり動く
        lx = W * (0.35 + 0.25 * math.sin(gt * 0.6)); ly = H * (0.55 + 0.1 * math.cos(gt * 0.8)); R.glow(im, lx, ly, 260, (230, 220, 180), 70)
        header(im, 3, '黒い服の男たち', t)
        bullet(im, 110, 300, 'お店が閉まったあと…', t, at('l3', 'お店', pre), Mi(64), GREY)
        bullet(im, 110, 420, '黒いスーツの男たちが ふたを開けた', t, at('l3', '黒いスーツ', pre), Mi(64))
        bullet(im, 110, 600, 'コインには 手をつけない', t, at('l3', 'でも', pre), Mi(70), ICE)
        bullet(im, 110, 740, '何かの「記録」だけを 持ち帰った', t, at('l3', '何かの', pre), Mi(76), GOLD)
        return finish(im, gt, 0.2, True)
    im = R.darkbg(W, H, (16, 22, 36)).copy(); q = t - tg
    for i in range(5):
        a = 1 - ease((q - 1.2 - i * 0.9) / 1.2); cabinet(im, 330 + i * 315, 960, 470, gt + i, 0.9, a)
    alpha_text(im, (W / 2, 170), '数週間後', Mi(80), GREY, appear(t, tg))
    alpha_text(im, (W / 2, 300), '町じゅうのゲームセンターから 消えた', Mi(76), PALE, appear(t, at('l3', 'ゲーム機は', pre)))
    return finish(im, gt, 0.25)
def timeline(im, t, pts, y=560):
    d = ImageDraw.Draw(im, 'RGBA'); x0, x1 = 180, 1740; years = (1975, 2020)
    X = lambda yr: x0 + (yr - years[0]) / (years[1] - years[0]) * (x1 - x0)
    d.line((x0, y, x1, y), fill=(200, 205, 220, 200), width=4)
    for yr in range(1980, 2021, 10): d.line((X(yr), y - 10, X(yr), y + 10), fill=(200, 205, 220, 200), width=3); ctext(d, (X(yr), y + 40), str(yr), Fb(30), GREY)
    for k, (yr, lab, sub, t0, col) in enumerate(pts):
        a = appear(t, t0, 0.6)
        if a <= 0: continue
        x = X(yr); up = k % 2 == 0; yy = y - 150 if up else y + 170
        d.line((x, y, x, yy + (40 if up else -40)), fill=col + (int(220 * a),), width=3); d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=col + (int(255 * a),))
        alpha_text(im, (x, yy - 30), lab, Mi(50), col, a, sw=0); alpha_text(im, (x, yy + 25), sub, Fo(32), PALE, a, sw=0)
def s_now1(t, T, gt, pre):
    im = base_photo('00.jpg', t, T, 0.28, z0=1.2, z1=1.35, blur=8)
    alpha_text(im, (W / 2, 110), 'いま、このうわさは？', Mi(72), PALE, appear(t, 0.1))
    tp = at('now1', 'じつは', pre); th = at('now1', 'うわさが', pre)
    if t < th + 0.3:
        a = appear(t, tp); alpha_text(im, (W / 2, 420), '黒いゲーム機の写真', Mi(80), PALE, a); alpha_text(im, (W / 2, 640), '0枚', Mi(240), GOLD, appear(t, at('now1', '一枚も', pre)))
        alpha_text(im, (W / 2, 820), '一枚も 見つかっていない', Mi(56), ICE, appear(t, at('now1', '一枚も', pre) + 0.4))
    else:
        timeline(im, t, [(1981, '1981年', 'うわさの舞台', th, GREY), (2000, '2000年ごろ', 'ゲーム機のサイトに 初めて登場', at('now1', '二〇〇〇年', pre), GOLD)])
        bullet(im, W / 2, 900, '「このゲームを 知っている人は？」', t, at('now1', '「この', pre), Mi(60), PALE, anchor='mm')
    return finish(im, gt, 0.15, True)
def s_spread(t, T, gt, pre):
    ts = at('spread', 'そこから', pre)
    if t < ts:
        im = base_photo('06.jpg', t, T, 0.28, z0=1.25, z1=1.35, blur=8)
        alpha_text(im, (W / 2, 110), 'うわさは 世界中へ', Mi(72), PALE, 1.0)
        timeline(im, t, [(1981, '1981年', 'うわさの舞台', -1, GREY), (2000, '2000年ごろ', 'サイトに初登場', -1, GREY),
                         (2003, '2003年', 'アメリカのゲーム雑誌', at('spread', '二〇〇三年', pre), GOLD)])
        bullet(im, W / 2, 900, '「本当にあったかどうかは、わからない」', t, at('spread', '「本当', pre), Mi(58), GOLD, anchor='mm')
        return finish(im, gt, 0.15, True)
    q = t - ts; im = R.darkbg(W, H, (12, 22, 40)).copy(); sc = 30 - 12 * ease(q / 6)
    c0 = math.cos(math.radians(38)); cx = W * 0.62 + 26.68 * sc * c0 * 0.6; cy = H * 0.55 + 7.5 * sc * 0.6
    P = R.usmap(im, cx, cy, sc, hi=PORT, a=0.8); x, y = P(*PORT); d = ImageDraw.Draw(im, 'RGBA')
    for k in range(6):   # ポートランドから広がる輪
        r = ((q * 160 + k * 220) % 1300); a = max(0, 1 - r / 1300)
        d.ellipse((x - r, y - r, x + r, y + r), outline=GOLD + (int(200 * a),), width=4)
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=GOLD)
    for i, (lab, key) in enumerate([('アニメ', 'アニメ'), ('ドラマ', 'ドラマ'), ('音楽の映像', '音楽')]):
        bullet(im, 110, 300 + i * 150, lab, t, at('spread', key, pre), Mi(90), ICE)
    bullet(im, 110, 820, 'うわさは 世界中に広がった', t, at('spread', '世界中', pre), Mi(72), GOLD)
    return finish(im, gt, 0.12)
def s_now2(t, T, gt, pre):
    im = base_photo(PS, t, T, 0.5, z0=1.05, z1=1.2); d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((60, 170, 1860, 1010), fill=(0, 0, 0, 120))
    alpha_text(im, (W / 2, 100), '1981年のポートランドで 本当にあったニュース', Mi(62), GOLD, appear(t, 0.1))
    bullet(im, 120, 250, '同じ日に、ゲームセンターで 若者2人の具合が悪くなった', t, at('now2', '同じ日', pre), Mi(52))
    bullet(im, 180, 360, '1人：ひどい頭痛', t, at('now2', '一人は', pre), Mi(52), ICE)
    bullet(im, 180, 450, '1人：28時間 遊び続けて おなかが痛く', t, at('now2', 'もう一人', pre), Mi(52), ICE)
    bullet(im, 120, 590, '約10日後　警察とFBIが ゲームセンターを一斉に調べた', t, at('now2', 'その十日', pre), Mi(52))
    bullet(im, 180, 700, '理由：ゲーム機を使った 違法なかけごと', t, at('now2', '理由', pre), Mi(52), ICE)
    bullet(im, W / 2, 870, '黒い服の男たちの正体は…これ？', t, at('now2', '黒い服', pre), Mi(76), GOLD, anchor='mm')
    d = ImageDraw.Draw(im, 'RGBA'); d.text((80, 1040), '出典：Eugene Register-Guard（1981年11月29日）、Skeptoid #362 ほか　写真：夜の路面電車（イメージ）', font=Fb(22), fill=(200, 200, 210), anchor='ls')
    return finish(im, gt, 0.12)
def s_now3(t, T, gt, pre):
    t17 = at('now3', 'そして', pre)
    if t < t17:
        im = R.darkbg(W, H, (22, 26, 36)).copy(); d = ImageDraw.Draw(im, 'RGBA')
        alpha_text(im, (W / 2, 110), '名前の由来：古代ギリシャの歴史家', Mi(62), PALE, appear(t, 0.1))
        alpha_text(im, (W / 2, 200), 'ポリュビオス（約2200年前）', Mi(56), GOLD, appear(t, at('now3', '二千年', pre)))
        L = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'; tg = at('now3', '文字を', pre); s = 120; x0 = W / 2 - 2.5 * s + 60; y0 = 330
        for i in range(5):
            ctext(d, (x0 - 70, y0 + i * s + s / 2), str(i + 1), BE(70), GOLD + (int(255 * appear(t, tg)),)); ctext(d, (x0 + i * s + s / 2, y0 - 40), str(i + 1), BE(70), GOLD + (int(255 * appear(t, tg)),))
        for k, ch in enumerate(L):
            a = appear(t, tg + k * 0.12, 0.3)
            if a <= 0: continue
            r, c = divmod(k, 5); x, y = x0 + c * s, y0 + r * s
            d.rectangle((x + 4, y + 4, x + s - 4, y + s - 4), outline=(150, 160, 190, int(200 * a)), width=3); ctext(d, (x + s / 2, y + s / 2), ch, BE(80), PALE + (int(255 * a),))
        if t > at('now3', '数字に', pre):
            a = appear(t, at('now3', '数字に', pre)); d.rectangle((x0 + 1 * s + 4, y0 + 3 * s + 4, x0 + 2 * s - 4, y0 + 4 * s - 4), outline=GOLD + (int(255 * a),), width=6)
            alpha_text(im, (x0 + 5 * s + 260, y0 + 3.5 * s), 'R ＝ 42', Fo(100), GOLD, a, sw=0)
        im = finish(im, gt, 0.15)
        return im
    im = base_photo('02.jpg', t - t17, T - t17, 0.5, z0=1.15, z1=1.3, cx0=0.4, cx1=0.6)
    alpha_text(im, (W / 2, 330), '2017年', Mi(110), GOLD, appear(t, t17 + 0.3))
    alpha_text(im, (W / 2, 520), '同じ名前の 本物のゲームが発売', Mi(80), PALE, appear(t, at('now3', 'うわさのゲーム', pre)))
    alpha_text(im, (W / 2, 700), 'うわさが、本物になった', Mi(90), ICE, appear(t, at('now3', 'うわさが、本物', pre)))
    return finish(im, gt, 0.18, True)
def s_outro(t, T, gt, pre):
    tm = at('outro', 'もし', pre)
    if t < tm: im = R.darkbg(W, H, (18, 26, 42)).copy()
    else: im = base_photo('02.jpg', t - tm, T - tm, 0.42, z0=1.05, z1=1.3, cx0=0.7, cx1=0.75)
    cabinet(im, 1450, 1010, 820 + 60 * ease((t - tm) / (T - tm)) * (t > tm), gt, 0.6 + 0.4 * ease(t / 3))
    bullet(im, 110, 200, '写真も 記録も ない', t, 0.2, Mi(66), GREY)
    bullet(im, 110, 310, 'それでも 40年以上 語りつがれる', t, at('outro', 'それでも', pre), Mi(60))
    ta = at('outro', 'あなたは', pre)
    alpha_text(im, (110, 520), 'あなたは', Mi(90), PALE, appear(t, ta), anchor='lm'); alpha_text(im, (110, 660), '遊んでみたい？', Mi(120), GOLD, appear(t, ta + 0.3), anchor='lm')
    d = ImageDraw.Draw(im, 'RGBA')
    for i, s in enumerate(['遊ぶ', '遊ばない']):
        a = appear(t, ta + 0.9 + i * 0.3)
        if a > 0:
            x = 110 + i * 360; d.rounded_rectangle((x, 780, x + 320, 880), 20, fill=(10, 12, 20, int(220 * a)), outline=GOLD + (int(255 * a),), width=4); ctext(d, (x + 160, 830), s, Mi(54), PALE + (int(255 * a),))
    bullet(im, 110, 960, 'コメントで教えてください', t, at('outro', 'コメント', pre), Fo(44), PALE)
    if t > tm: alpha_text(im, (110, 420), 'もし、近くのゲームセンターに 名前のない黒いゲーム機があったら…', Fo(40), GREY, appear(t, tm), anchor='lm', sw=0)
    return finish(im, gt, 0.3, t > tm)
ORDER = [('hook', s_hook, 0.15, 0.6), ('title', s_title, 0.5, 0.8), ('where', s_where, 0.4, 0.8), ('era', s_era, 0.3, 0.7), ('l1', s_l1, 0.6, 0.8),
         ('l2', s_l2, 0.6, 0.6), ('l2b', s_l2b, 0.3, 0.8), ('rh', s_rh, 0.3, 0.6), ('l3', s_l3, 0.6, 1.6), ('now1', s_now1, 0.5, 0.6), ('spread', s_spread, 0.3, 0.8),
         ('now2', s_now2, 0.5, 0.9), ('now3', s_now3, 0.4, 0.9), ('outro', s_outro, 0.4, 2.4)]
def plan():
    out = []; off = 0.0
    for k, fn, pre, post in ORDER:
        T = pre + D[k] + post; out.append((k, fn, pre, off, T)); off += T
    return out, off
if __name__ == '__main__':
    P, total = plan()
    if len(sys.argv) > 2 and sys.argv[2] == 'still':   # 静止画チェック
        for k, fn, pre, off, T in P:
            for j, u in enumerate((0.25, 0.6, 0.95)):
                fn(T * u, T, off + T * u, pre).resize((960, 540)).save(f'{G}/still/{k}_{j}.jpg', quality=85)
        print('stills'); sys.exit()
    json.dump({'scenes': [(k, off, T, pre) for k, fn, pre, off, T in P], 'total': total}, open(f'{G}/main_plan.json', 'w'))
    p = R.writer(f'{G}/main_video.mp4', W, H); n = int(round(total * 30))
    idx = 0
    for i in range(n):
        gt = i / 30
        while idx + 1 < len(P) and gt >= P[idx + 1][3]: idx += 1
        k, fn, pre, off, T = P[idx]
        im = fn(gt - off, T, gt, pre)
        # 場面のつなぎ：0.35秒のクロスフェード（暗転は短く）
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('main video', total)
