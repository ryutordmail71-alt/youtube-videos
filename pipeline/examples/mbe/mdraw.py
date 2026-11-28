"""幻の駅：描画部品（日本地図・銀座線の簡略図・電車の窓・カード）"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, ICE, ctext, alpha_text, ease, fade
ORANGE = (243, 151, 0); KBLUE = (90, 140, 230)
# ---- 地図（Natural Earth / world-atlas 50m）----
_T = json.load(open('/home/claude/mbe/wa/package/countries-50m.json'))
_SC, _TR = _T['transform']['scale'], _T['transform']['translate']
def _arc(i):
    a = _T['arcs'][i if i >= 0 else ~i]; x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * _SC[0] + _TR[0], y * _SC[1] + _TR[1]))
    return pts if i >= 0 else pts[::-1]
def _ring(r):
    out = []
    for i in r:
        p = _arc(i); out.extend(p if not out else p[1:])
    return out
COUNTRIES = {}
for g in _T['objects']['countries']['geometries']:
    nm = g['properties']['name']; polys = g['arcs'] if g['type'] == 'MultiPolygon' else ([g['arcs']] if g['type'] == 'Polygon' else [])
    rings = [_ring(p[0]) for p in polys]
    if any(115 < lo < 150 and 20 < la < 50 for r in rings for lo, la in r[::5] + r[:1]): COUNTRIES[nm] = rings
TOKYO = (35.68, 139.77)
def asia(im, cx, cy, scale, lat0=36.0, lon0=138.0, a=1.0, hi='Japan'):
    c0 = math.cos(math.radians(lat0)); d = ImageDraw.Draw(im, 'RGBA')
    P = lambda la, lo: (cx + (lo - lon0) * scale * c0, cy - (la - lat0) * scale)
    for nm, rings in COUNTRIES.items():
        for r in rings:
            pts = [P(la, lo) for lo, la in r]
            if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > im.width + 50: continue
            if max(p[1] for p in pts) < -50 or min(p[1] for p in pts) > im.height + 50: continue
            if nm == hi: d.polygon(pts, fill=(70, 90, 130, int(235 * a)), outline=(230, 220, 170, int(255 * a)))
            else: d.polygon(pts, fill=(34, 42, 62, int(230 * a)), outline=(95, 110, 140, int(200 * a)))
    return P
# ---- 銀座線の簡略図 ----
ST = ['渋谷', '表参道', '外苑前', '青山一丁目', '赤坂見附', '溜池山王', '虎ノ門', '新橋', '銀座', '京橋', '日本橋', '三越前', '神田', '末広町', '上野広小路', '上野', '稲荷町', '田原町', '浅草']
def line_map(im, t, x0, x1, y, a=1.0, ghosts=(), focus=None, show=1.0, labels=True, keisei=0.0):
    """ghosts: 表示する幻の駅 'omote','shinbashi','mansei','hakudo' と出す強さ"""
    if a <= 0.01: return
    d = ImageDraw.Draw(im, 'RGBA'); n = len(ST); X = lambda i: x0 + (x1 - x0) * i / (n - 1)
    xe = x0 + (x1 - x0) * ease(show)
    d.line((x0, y, xe, y), fill=ORANGE + (int(255 * a),), width=16)
    for i, s in enumerate(ST):
        x = X(i)
        if x > xe + 1: break
        big = s in ('渋谷', '新橋', '神田', '上野', '浅草', '表参道', '末広町')
        r = 13 if big else 9; d.ellipse((x - r, y - r, x + r, y + r), fill=(245, 245, 245, int(255 * a)), outline=(60, 40, 10, int(255 * a)), width=3)
        if labels and (big or focus):
            up = i % 2 == 0
            alpha_text(im, (x, y + (-58 if up else 58)), s, Fo(34 if big else 26), PALE if big else GREY, a, sw=1, blur=6)
    G = {'omote': (1.35, '旧表参道ホーム'), 'shinbashi': (7, '幻の新橋駅'), 'mansei': (12.5, '万世橋駅')}
    for k, v in ghosts:
        if k in G and v > 0.01:
            i, lab = G[k]; x = X(i); yy = y + (0 if k != 'shinbashi' else 0); rr = 22 + 6 * math.sin(t * 3)
            d.ellipse((x - rr, yy - rr, x + rr, yy + rr), outline=GOLD + (int(255 * v * a),), width=5)
            alpha_text(im, (x, yy + 120 * (1 if k != 'mansei' else -1) * (1 if k == 'omote' else 1)), lab, Mi(46), GOLD, v * a, sw=2)
            d.line((x, yy + (rr if k != 'mansei' else -rr), x, yy + (90 if k != 'mansei' else -90)), fill=GOLD + (int(200 * v * a),), width=3)
    if keisei > 0.01:   # 京成線（日暮里〜京成上野）の一部
        xu = X(15); k = keisei * a
        d.line((xu + 30, y - 330, xu + 30, y - 120), fill=KBLUE + (int(255 * k),), width=12)
        for yy, lab in ((y - 330, '日暮里'), (y - 120, '京成上野')):
            d.ellipse((xu + 18, yy - 12, xu + 42, yy + 12), fill=(245, 245, 245, int(255 * k)), outline=(20, 40, 80, int(255 * k)), width=3)
            alpha_text(im, (xu + 60, yy), lab, Fo(30), PALE, k, anchor='lm', sw=1, blur=6)
        yy = y - 225; rr = 20 + 5 * math.sin(t * 3); d.ellipse((xu + 30 - rr, yy - rr, xu + 30 + rr, yy + rr), outline=GOLD + (int(255 * k),), width=5)
        alpha_text(im, (xu + 70, yy), '博物館動物園駅', Mi(42), GOLD, k, anchor='lm', sw=2)
        alpha_text(im, (xu + 70, y - 395), '京成線', Fo(30), KBLUE, k, anchor='lm', sw=1)
    return X
# ---- 電車の窓から見た暗いトンネル。pass_u（0→1）で写真のホームが横切る ----
def window(W, H, t, photo=None, pass_u=None, a_light=1.0):
    im = Image.new('RGB', (W, H), (4, 5, 8)); d = ImageDraw.Draw(im, 'RGBA')
    # 窓の外：流れる照明
    for k in range(7):
        x = W - ((t * 1500 + k * W / 6.5) % (W * 1.15)); y = H * 0.32
        d.rectangle((x, y, x + 120, y + 10), fill=(255, 235, 190, int(200 * a_light)))
        d.line((x - 300, y + 5, x, y + 5), fill=(255, 220, 160, int(40 * a_light)), width=6)
    for k in range(18):   # 壁のケーブル・継ぎ目
        x = W - ((t * 1500 + k * W / 17) % (W * 1.1)); d.line((x, H * 0.18, x, H * 0.82), fill=(30, 32, 38, 255), width=4)
    d.line((0, H * 0.55, W, H * 0.55), fill=(40, 42, 50, 255), width=5); d.line((0, H * 0.6, W, H * 0.6), fill=(28, 30, 36, 255), width=3)
    if photo is not None and pass_u is not None and 0 < pass_u < 1:
        src = R.photo(photo, int(W * 1.3), H, bright=0.55, blue=0.45, over=1.0)
        x = int(W - pass_u * (W + src.width)); m = Image.new('L', src.size, 0); md = ImageDraw.Draw(m)
        md.rectangle((0, 0, src.width, src.height), fill=255); m = m.filter(ImageFilter.GaussianBlur(40))
        blur = src.filter(ImageFilter.BoxBlur(6))   # 動いているので横にぶれる
        im.paste(blur, (x, 0), m)
    im = im.filter(ImageFilter.GaussianBlur(1.5))
    # 窓わく（電車の中）
    d = ImageDraw.Draw(im, 'RGBA'); fr = (22, 24, 30, 255)
    d.rectangle((0, 0, W, H * 0.1), fill=fr); d.rectangle((0, H * 0.9, W, H), fill=fr)
    for x in (0, W * 0.5 - 18, W - 36): d.rectangle((x, 0, x + 36, H), fill=fr)
    d.rounded_rectangle((36, H * 0.1, W * 0.5 - 18, H * 0.9), 26, outline=(60, 64, 74, 255), width=6)
    d.rounded_rectangle((W * 0.5 + 18, H * 0.1, W - 36, H * 0.9), 26, outline=(60, 64, 74, 255), width=6)
    # ガラスの反射
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).polygon([(W * 0.12, H * 0.1), (W * 0.2, H * 0.1), (W * 0.08, H * 0.9), (0, H * 0.9)], fill=26)
    im.paste((200, 210, 230), (0, 0), g.filter(ImageFilter.GaussianBlur(20)))
    return im
# ---- 番号つきカード ----
def card(im, x, y, w, h, no, txt, a, sub=None, col=GOLD):
    if a <= 0.01: return
    L = Image.new('RGBA', (int(w) + 40, int(h) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((20, 20, w + 20, h + 20), 22, fill=(8, 12, 22, 215), outline=col + (255,), width=4)
    d.ellipse((44, 20 + h / 2 - 40, 124, 20 + h / 2 + 40), fill=col + (255,)); d.text((84, 20 + h / 2), str(no), font=BE(72), fill=(20, 20, 20, 255), anchor='mm')
    if sub:
        d.text((156, 20 + h * 0.34), sub, font=Fb(int(h * 0.2)), fill=GREY + (255,), anchor='lm'); d.text((156, 20 + h * 0.68), txt, font=Mi(int(h * 0.32)), fill=PALE + (255,), anchor='lm')
    else: d.text((156, 20 + h / 2), txt, font=Mi(int(h * 0.34)), fill=PALE + (255,), anchor='lm')
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (int(x - 20 + (1 - a) * 40), int(y - 20)), L)
# ---- 12か月の帯（8か月だけ光る）----
def months(im, x0, y, w, u, a=1.0):
    """1月15日〜9月15日（8か月）を、12か月の帯の上に光らせる"""
    d = ImageDraw.Draw(im, 'RGBA'); cw = w / 12
    d.rounded_rectangle((x0, y, x0 + w, y + 70), 12, fill=(40, 44, 56, int(220 * a)))
    for m in range(1, 12): d.line((x0 + m * cw, y + 6, x0 + m * cw, y + 64), fill=(80, 86, 100, int(255 * a)), width=2)
    k = ease(u)
    if k > 0: d.rounded_rectangle((x0 + 0.5 * cw, y + 6, x0 + (0.5 + 8 * k) * cw, y + 64), 10, fill=GOLD + (int(240 * a),))
    for m in range(12): ctext(d, (x0 + (m + 0.5) * cw, y + 105), f'{m + 1}月', Fb(28), GREY + (int(255 * a),))
