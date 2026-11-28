"""東京の地下の秘密の通路：描画部品（永田町の略図・うわさの道・地下の断面・開かずの扉・地図くらべ）"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, ICE, CYAN, alpha_text, ease, fade
# ---- 永田町まわりの略図（緯度・経度はおよその位置）----
LAT0, LON0 = 35.6795, 139.7545
PL = {'国会議事堂': (35.6759, 139.7448), '総理大臣官邸': (35.6731, 139.7413), '霞が関': (35.6745, 139.7520), '皇居': (35.6840, 139.7535), '東京駅': (35.6812, 139.7671),
      '国会議事堂前駅': (35.6738, 139.7455), '溜池山王駅': (35.6722, 139.7408), '永田町駅': (35.6786, 139.7403), '議員会館': (35.6728, 139.7470)}
LINES = {'丸ノ内線': ((235, 70, 60), [(35.6770, 139.7370), (35.6738, 139.7455), (35.6732, 139.7510), (35.6717, 139.7640), (35.6812, 139.7660)]),
         '千代田線': ((60, 190, 110), [(35.6700, 139.7350), (35.6738, 139.7455), (35.6732, 139.7510), (35.6740, 139.7600), (35.6810, 139.7615), (35.6880, 139.7645)]),
         '有楽町線': ((215, 175, 70), [(35.6820, 139.7330), (35.6786, 139.7403), (35.6772, 139.7515), (35.6750, 139.7630)]),
         '半蔵門線': ((150, 110, 200), [(35.6740, 139.7330), (35.6786, 139.7403), (35.6856, 139.7413), (35.6955, 139.7509)]),
         '南北線': ((60, 170, 180), [(35.6656, 139.7380), (35.6722, 139.7408), (35.6786, 139.7403), (35.6880, 139.7350)])}
def proj(W, H, S=50000, cx=None, cy=None, center=None):
    cx = W / 2 if cx is None else cx; cy = H / 2 if cy is None else cy; c0 = math.cos(math.radians(LAT0))
    if center: cx = cx - (center[1] - LON0) * S * c0; cy = cy + (center[0] - LAT0) * S
    return lambda la, lo: (cx + (lo - LON0) * S * c0, cy - (la - LAT0) * S)
def areamap(im, a=1.0, lines_a=1.0, S=50000, cx=None, cy=None, center=None, labels=('国会議事堂', '総理大臣官邸', '霞が関', '皇居', '東京駅'), line_names=True):
    W, H = im.size; P = proj(W, H, S, cx, cy, center); d = ImageDraw.Draw(im, 'RGBA')
    # 皇居（緑とお堀）
    x, y = P(*PL['皇居']); rx, ry = 0.0068 * S * 0.81, 0.0058 * S
    d.ellipse((x - rx - 18, y - ry - 18, x + rx + 18, y + ry + 18), fill=(40, 70, 110, int(200 * a)))
    d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(36, 70, 48, int(235 * a)), outline=(90, 140, 100, int(255 * a)), width=3)
    # 道路の格子（うすく）
    for k in range(-12, 13):
        d.line((x + k * 90 - 600, 0, x + k * 90 + 300, H), fill=(60, 70, 95, int(60 * a)), width=2)
    if lines_a > 0:
        for nm, (col, pts) in LINES.items():
            q = [P(*p) for p in pts]; d.line(q, fill=col + (int(230 * a * lines_a),), width=9, joint='curve')
            if line_names:
                lx, ly = q[0]; alpha_text(im, (lx, ly - 28), nm, Fb(28), col, a * lines_a, anchor='mm', sw=2)
    for nm in labels:
        x, y = P(*PL[nm])
        if nm == '皇居': alpha_text(im, (x, y), '皇居', Mi(60), (190, 230, 190), a); continue
        d.rectangle((x - 16, y - 16, x + 16, y + 16), fill=PALE + (int(240 * a),), outline=(20, 20, 30, int(255 * a)), width=3)
        alpha_text(im, (x, y + 46), nm, Mi(38), PALE, a)
    return P
def dashed(d, pts, col, w=6, dash=26, gap=16, ph=0.0):
    """折れ線を点線で（ph で流れる）"""
    seg = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); s = -((ph * (dash + gap)) % (dash + gap))
        while s < L:
            a0 = max(0, s); a1 = min(L, s + dash)
            if a1 > a0: d.line((x0 + (x1 - x0) * a0 / L, y0 + (y1 - y0) * a0 / L, x0 + (x1 - x0) * a1 / L, y0 + (y1 - y0) * a1 / L), fill=col, width=w)
            s += dash + gap
SECRET = [('国会議事堂', '皇居'), ('総理大臣官邸', '国会議事堂'), ('皇居', '霞が関'), ('霞が関', '国会議事堂'), ('皇居', '東京駅')]
def secretnet(im, P, u, t, a=1.0):
    """うわさの道（イメージ）：u=0→1 で1本ずつのびる。金色の点線が流れる"""
    if a <= 0.01 or u <= 0: return
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    n = len(SECRET)
    for i, (p, q) in enumerate(SECRET):
        k = fade(u * n - i)
        if k <= 0: continue
        (x0, y0), (x1, y1) = P(*PL[p]), P(*PL[q]); mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 60
        pts = []
        for s in np.linspace(0, k, 24):
            pts.append(((1 - s) ** 2 * x0 + 2 * (1 - s) * s * mx + s * s * x1, (1 - s) ** 2 * y0 + 2 * (1 - s) * s * my + s * s * y1))
        dashed(d, pts, GOLD + (int(255 * a),), 7, ph=t * 1.2)
    gl = g.filter(ImageFilter.GaussianBlur(8)); im.paste((255, 200, 90), (0, 0), gl.getchannel('A').point(lambda v: int(v * 0.8)))
    im.paste(g.convert('RGB'), (0, 0), g)
# ---- 地下の断面（深さの比較）----
def section(im, x0, y_ground, ppm, t, show=('pipes', 'maru', 'chiyoda', 'bldg'), a=1.0, roppongi=0.0, chi_u=1.0, maru_u=1.0, labels=True):
    """ppm：1mあたりのpx。地面 y_ground。丸ノ内線（浅い）・千代田線 37.9m・六本木 42.3m・ビル12階ぶん"""
    W, H = im.size; d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((0, 0, W, y_ground), fill=(10, 14, 26, int(255 * a)))
    for i in range(int((H - y_ground) / 30) + 1):   # 土の層
        yy = y_ground + i * 30; c = 46 - min(20, i) * 0.6
        d.rectangle((0, yy, W, yy + 30), fill=(int(c + 14), int(c + 6), int(c), int(255 * a)))
    rr = np.random.default_rng(5)
    for k in range(60):
        x = rr.uniform(0, W); y = rr.uniform(y_ground + 20, H); d.line((x, y, x + rr.uniform(40, 140), y + rr.uniform(-6, 6)), fill=(80, 68, 56, int(160 * a)), width=3)
    d.rectangle((0, y_ground - 6, W, y_ground), fill=(120, 125, 135, int(255 * a)))
    # 地上のビル（うすい影）
    for bx, bw, bh in ((x0 + 820, 160, 300), (x0 + 1040, 120, 220), (x0 + 1210, 200, 380), (x0 + 1460, 140, 260)):
        d.rectangle((bx, y_ground - bh, bx + bw, y_ground), fill=(26, 32, 48, int(255 * a)), outline=(60, 70, 95, int(255 * a)))
        for wy in range(int(y_ground - bh + 20), int(y_ground - 10), 34):
            for wx in range(int(bx + 14), int(bx + bw - 14), 30): d.rectangle((wx, wy, wx + 12, wy + 14), fill=(200, 180, 120, int(110 * a)))
    if 'pipes' in show:   # 水道・電気・ガスの管（地下 1〜5m あたり）
        for col, dep, nm in (((90, 150, 220), 2.0, '水道'), ((230, 190, 80), 3.4, '電気'), ((220, 120, 80), 4.8, 'ガス')):
            y = y_ground + dep * ppm; d.line((x0 + 300, y, W, y), fill=col + (int(230 * a),), width=max(4, int(ppm * 0.6)))
            if labels: alpha_text(im, (W - 40, y - 4), nm, Fb(30), col, a, anchor='rm', sw=2)
    def tube(dep, col, u, nm, yr):
        if u <= 0: return
        y = y_ground + dep * ppm; L = (W - x0 - 340) * ease(u); r = 3.2 * ppm
        d.rounded_rectangle((x0 + 300, y - r, x0 + 300 + L, y + r), int(r), fill=(14, 16, 22, int(255 * a)), outline=col + (int(255 * a),), width=5)
        if u > 0.3 and labels: alpha_text(im, (x0 + 330, y), f'{nm}（{yr}）', Fb(34), col, a * fade((u - 0.3) * 3), anchor='lm', sw=2)
    if 'maru' in show: tube(8.0, (235, 70, 60), maru_u, '丸ノ内線', '1959年')
    if 'chiyoda' in show: tube(37.9, (60, 190, 110), chi_u, '千代田線', '1972年')
    if roppongi > 0: tube(42.3, (220, 80, 170), roppongi, '大江戸線 六本木駅', '2000年')
    # 深さの目盛り
    d.line((x0 + 150, y_ground, x0 + 150, y_ground + 45 * ppm), fill=(200, 205, 220, int(200 * a)), width=3)
    for m in (0, 10, 20, 30, 40):
        y = y_ground + m * ppm; d.line((x0 + 135, y, x0 + 165, y), fill=(200, 205, 220, int(220 * a)), width=3)
        alpha_text(im, (x0 + 120, y), f'{m}m', Fb(30), PALE, a, anchor='rm', sw=2)
    if 'bldg' in show and chi_u > 0.5:   # ビル12階ぶん（1階 約3.1m の目安）を逆さに
        k = ease((chi_u - 0.5) * 2); bx = x0 + 200
        for f in range(12):
            if f / 12 > k: break
            y = y_ground + f * 3.16 * ppm; d.rectangle((bx, y + 2, bx + 70, y + 3.16 * ppm - 2), outline=(150, 170, 210, int(200 * a)), width=2)
    return lambda m: y_ground + m * ppm
# ---- 開かずの扉（金属の扉・注意書き）----
def door(im, cx, by, h, open_u=0.0, a=1.0, sign=True, light=(255, 230, 170)):
    if a <= 0.01: return
    w = h * 0.46; x0, y0, x1, y1 = cx - w / 2, by - h, cx + w / 2, by
    L = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((x0 - 14, y0 - 14, x1 + 14, y1), fill=(70, 74, 82, 255))
    if open_u > 0:   # 開いたすき間の光
        gw = w * 0.25 * open_u; d.rectangle((x1 - gw, y0, x1, y1), fill=light + (255,))
        gl = Image.new('L', im.size, 0); ImageDraw.Draw(gl).polygon([(x1 - gw, y0), (x1, y0), (x1 + h * 0.5 * open_u, y1 + h * 0.15), (x1 - gw - h * 0.2 * open_u, y1 + h * 0.15)], fill=int(120 * open_u))
        im.paste(light, (0, 0), gl.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * a)))
    dw = w - w * 0.25 * open_u
    d.rectangle((x0, y0, x0 + dw, y1), fill=(118, 124, 134, 255), outline=(40, 42, 48, 255), width=3)
    d.rectangle((x0 + dw * 0.12, y0 + h * 0.08, x0 + dw * 0.88, y0 + h * 0.44), outline=(90, 95, 104, 255), width=3)
    d.rectangle((x0 + dw * 0.12, y0 + h * 0.52, x0 + dw * 0.88, y0 + h * 0.92), outline=(90, 95, 104, 255), width=3)
    d.rounded_rectangle((x0 + dw - w * 0.16, y0 + h * 0.48, x0 + dw - w * 0.05, y0 + h * 0.53), 4, fill=(190, 195, 200, 255))
    if sign:
        sx0, sy0 = x0 + dw * 0.1, y0 + h * 0.15; sw_, sh_ = dw * 0.8, h * 0.17
        d.rectangle((sx0, sy0, sx0 + sw_, sy0 + sh_), fill=(240, 236, 220, 255), outline=(200, 40, 40, 255), width=4)
        d.text((sx0 + sw_ / 2, sy0 + sh_ * 0.32), '関係者以外', font=Fb(int(sh_ * 0.27)), fill=(200, 30, 30, 255), anchor='mm')
        d.text((sx0 + sw_ / 2, sy0 + sh_ * 0.7), '立入禁止', font=Fb(int(sh_ * 0.32)), fill=(200, 30, 30, 255), anchor='mm')
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (0, 0), L)
# ---- 地図くらべ（昔の地図・いまの地図。線は簡単にしたイメージ）----
def mapcard(im, x, y, w, h, title, kind, u, t, a=1.0):
    if a <= 0.01: return
    d = ImageDraw.Draw(im, 'RGBA')
    bg = (70, 60, 44) if kind == 'old' else (24, 30, 46)
    d.rounded_rectangle((x, y, x + w, y + h), 16, fill=bg + (int(240 * a),), outline=(200, 190, 160, int(220 * a)), width=4)
    rr = np.random.default_rng(11)
    for k in range(14):   # 道
        yy = y + 40 + k * (h - 80) / 13; d.line((x + 20, yy, x + w - 20, yy + rr.uniform(-20, 20)), fill=(150, 140, 120, int(120 * a)) if kind == 'old' else (70, 80, 110, int(140 * a)), width=2)
    col = (230, 90, 70)
    base = [(x + w * 0.1, y + h * 0.7), (x + w * 0.35, y + h * 0.55), (x + w * 0.55, y + h * 0.58), (x + w * 0.9, y + h * 0.3)]
    if kind == 'old': pts = [(x + w * 0.1, y + h * 0.7), (x + w * 0.38, y + h * 0.6), (x + w * 0.62, y + h * 0.5), (x + w * 0.9, y + h * 0.3)]
    else: pts = base
    k = ease(u); n = max(2, int(2 + k * 30)); q = []
    for s in np.linspace(0, k, n):
        seg = min(2, int(s * 3)); ss = s * 3 - seg; (ax, ay), (bx, by_) = pts[seg], pts[seg + 1]; q.append((ax + (bx - ax) * ss, ay + (by_ - ay) * ss))
    if len(q) > 1: d.line(q, fill=col + (int(255 * a),), width=8, joint='curve')
    if kind == 'new' and u > 0.8:   # 「なぜここで曲がる？」
        mx, my = pts[1]; r = 50 + 6 * math.sin(t * 4)
        d.ellipse((mx - r, my - r, mx + r, my + r), outline=GOLD + (int(255 * a),), width=5)
        alpha_text(im, (mx, my - 90), 'なぜ ここで曲がる？', Fb(36), GOLD, a * fade((u - 0.8) * 5), sw=2)
    alpha_text(im, (x + w / 2, y + h + 50), title, Mi(46), PALE, a, sw=0)
def book(im, cx, cy, h, a=1.0, ang=-6):
    if a <= 0.01: return
    w = h * 0.7; L = Image.new('RGBA', (int(w) + 60, int(h) + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((30, 30, 30 + w, 30 + h), fill=(20, 18, 22, 255), outline=(150, 130, 90, 255), width=4)
    d.rectangle((30, 30, 52, 30 + h), fill=(60, 50, 40, 255))
    d.text((30 + w / 2 + 10, 30 + h * 0.3), '東京の', font=Mi(int(h * 0.1)), fill=(230, 220, 200, 255), anchor='mm')
    d.text((30 + w / 2 + 10, 30 + h * 0.45), '地下の', font=Mi(int(h * 0.1)), fill=(230, 220, 200, 255), anchor='mm')
    d.text((30 + w / 2 + 10, 30 + h * 0.62), '秘密', font=Mi(int(h * 0.14)), fill=GOLD + (255,), anchor='mm')
    d.text((30 + w / 2 + 10, 30 + h * 0.86), '（イメージ）', font=Fb(int(h * 0.05)), fill=(170, 170, 175, 255), anchor='mm')
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC)
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (int(cx - L.width / 2), int(cy - L.height / 2)), L)
def bars(im, x, y, items, u, a=1.0, ppm=14, bw=150, gap=110):
    """深さの棒（下向き）items=[(名前, m, 色)]"""
    d = ImageDraw.Draw(im, 'RGBA')
    for i, (nm, m, col) in enumerate(items):
        k = ease(fade(u * len(items) - i * 0.7)); bx = x + i * (bw + gap)
        if k <= 0: continue
        d.rectangle((bx, y, bx + bw, y + m * ppm * k), fill=col + (int(235 * a),))
        alpha_text(im, (bx + bw / 2, y + m * ppm * k + 50), f'{m * k:.1f}m', Mi(60), PALE, a)
        alpha_text(im, (bx + bw / 2, y - 50), nm, Mi(40), col, a)
