"""スカイフィッシュ：描画部品（地図・スカイフィッシュの絵・ビデオの枠・縦穴の断面・ぶれのシミュレーション・終了画面）"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, ICE, CYAN, ctext, alpha_text, ease, fade
# ---- 地図（Natural Earth / world-atlas 50m）----
_T = json.load(open('/home/claude/sky/wa/package/countries-50m.json'))
_SC, _TR = _T['transform']['scale'], _T['transform']['translate']
_ARCS = []
for a in _T['arcs']:
    x = y = 0; pts = []
    for dx, dy in a: x += dx; y += dy; pts.append((x * _SC[0] + _TR[0], y * _SC[1] + _TR[1]))
    _ARCS.append(pts)
def _arc(i): return _ARCS[i] if i >= 0 else _ARCS[~i][::-1]
def _ring(r):
    out = []
    for i in r: p = _arc(i); out.extend(p if not out else p[1:])
    return out
COUNTRIES = []
for g in _T['objects']['countries']['geometries']:
    nm = g['properties']['name']; polys = g['arcs'] if g['type'] == 'MultiPolygon' else ([g['arcs']] if g['type'] == 'Polygon' else [])
    for p in polys:
        r = _ring(p[0]); xs = [q[0] for q in r]; ys = [q[1] for q in r]
        COUNTRIES.append((nm, np.array(r), (min(xs), max(xs), min(ys), max(ys))))
def worldmap(im, cx, cy, scale, lat0, lon0, a=1.0, hi=(), hi_col=(70, 90, 130)):
    """経度1度=scale px。hi に入れた国を明るく"""
    c0 = math.cos(math.radians(lat0)); d = ImageDraw.Draw(im, 'RGBA'); W, H = im.size
    P = lambda la, lo: (cx + (lo - lon0) * scale * c0, cy - (la - lat0) * scale)
    for nm, r, (x0, x1, y0, y1) in COUNTRIES:
        px0, py1 = P(y0, x0); px1, py0 = P(y1, x1)
        if px1 < -50 or px0 > W + 50 or py1 < -50 or py0 > H + 50: continue
        xs = cx + (r[:, 0] - lon0) * scale * c0; ys = cy - (r[:, 1] - lat0) * scale
        pts = list(zip(xs.tolist(), ys.tolist()))
        if len(pts) > 400 and scale < 30: pts = pts[::3]
        if nm in hi: d.polygon(pts, fill=hi_col + (int(235 * a),), outline=(230, 220, 170, int(255 * a)))
        else: d.polygon(pts, fill=(34, 42, 62, int(230 * a)), outline=(95, 110, 140, int(200 * a)))
    return P
def pin(im, P, la, lo, label, t, a, col=GOLD, side='r', size=64):
    if a <= 0.01: return
    d = ImageDraw.Draw(im, 'RGBA'); x, y = P(la, lo); r = 20 + 8 * math.sin(t * 3)
    d.ellipse((x - r, y - r, x + r, y + r), outline=col + (int(255 * a),), width=5); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col + (int(255 * a),))
    if side == 'r': alpha_text(im, (x + 40, y), label, Mi(size), col, a, anchor='lm')
    elif side == 'l': alpha_text(im, (x - 40, y), label, Mi(size), col, a, anchor='rm')
    else: alpha_text(im, (x, y - 60), label, Mi(size), col, a, anchor='mm')
# ---- スカイフィッシュ（うわさの姿のイメージ）----
def skyfish(im, x, y, ang, L, t, a=1.0, glow=True, col=(235, 240, 255)):
    """中心(x,y)、向きang(rad)、長さL(px)。両側のヒレが波打つ。半透明・少しぼかして「写ってしまったもの」らしく"""
    if a <= 0.01: return im
    m = int(L * 0.7) + 40; bx, by = int(x - m), int(y - m); S = 2 * m
    lay = Image.new('L', (S, S), 0); d = ImageDraw.Draw(lay)
    ca, sa = math.cos(ang), math.sin(ang); N = 14; wbody = max(3, L * 0.035)
    def p(u, v): return (m + ca * u - sa * v, m + sa * u + ca * v)
    d.line([p(-L / 2, 0), p(L / 2, 0)], fill=255, width=int(wbody))
    for i in range(N):
        u0 = -L / 2 + L * (i + 0.15) / N; u1 = -L / 2 + L * (i + 0.85) / N
        taper = math.sin(math.pi * (i + 0.5) / N) ** 0.6
        for sgn in (1, -1):
            fw = L * 0.085 * taper * (0.65 + 0.35 * math.sin(t * 14 - i * 0.9 + (0 if sgn > 0 else 1.6)))
            d.polygon([p(u0, 0), p((u0 + u1) / 2 + L * 0.01, sgn * fw), p(u1, 0)], fill=170)
    lay = lay.filter(ImageFilter.GaussianBlur(max(1.5, L * 0.008)))
    if glow:
        gl = lay.filter(ImageFilter.GaussianBlur(L * 0.04)).point(lambda v: int(v * 0.8 * a))
        im.paste((150, 190, 255), (bx, by), gl)
    im.paste(col, (bx, by), lay.point(lambda v: int(v * 0.85 * a))); return im
# ---- ビデオカメラの画面（REC・コマ番号）----
def camui(im, t, frame_no=None, a=1.0, paused=False):
    d = ImageDraw.Draw(im, 'RGBA'); W, H = im.size; c = (240, 240, 240, int(230 * a)); L = 70
    for (x, y, sx, sy) in ((60, 60, 1, 1), (W - 60, 60, -1, 1), (60, H - 90, 1, -1), (W - 60, H - 90, -1, -1)):
        d.line((x, y, x + sx * L, y), fill=c, width=5); d.line((x, y, x, y + sy * L), fill=c, width=5)
    if paused: alpha_text(im, (110, 110), '❚❚ 一時停止', Fb(40), PALE, a, anchor='lm', sw=0)
    elif int(t * 2) % 2 == 0: d.ellipse((100, 92, 136, 128), fill=(230, 50, 50, int(255 * a))); alpha_text(im, (150, 110), 'REC', BE(56), PALE, a, anchor='lm', sw=0)
    if frame_no is not None: alpha_text(im, (W - 110, 110), f'コマ {frame_no:04d}', Fb(40), PALE, a, anchor='rm', sw=0)
# ---- フィルムのコマ（並べて見せる）----
def filmstrip(im, src, x0, y0, n, fw, fh, gap, t, rod_u=None, a=1.0, hi=None):
    """src：背景の写真（Image）。rod_u：棒が横切るコマの位置 0〜1（コマごとにずれていく）"""
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((x0 - 30, y0 - 50, x0 + n * (fw + gap) - gap + 30, y0 + fh + 50), fill=(8, 8, 10, int(235 * a)))
    for k in range(int((n * (fw + gap)) / 40) + 1):
        xx = x0 - 20 + k * 40; d.rounded_rectangle((xx, y0 - 38, xx + 18, y0 - 18), 3, fill=(60, 60, 66, int(255 * a))); d.rounded_rectangle((xx, y0 + fh + 18, xx + 18, y0 + fh + 38), 3, fill=(60, 60, 66, int(255 * a)))
    for i in range(n):
        x = x0 + i * (fw + gap); fr = src.resize((fw, fh)).copy()
        if rod_u is not None:
            u = rod_u + i * 0.22
            if -0.2 < u < 1.2: skyfish(fr, fw * u, fh * (0.62 - 0.25 * u), -0.35, fw * 0.32, t + i, 0.95, glow=True)
        if a < 1: fr = Image.blend(im.crop((x, y0, x + fw, y0 + fh)).convert('RGB'), fr, a)
        im.paste(fr, (x, y0))
        if hi == i: d.rectangle((x - 5, y0 - 5, x + fw + 5, y0 + fh + 5), outline=GOLD + (int(255 * a),), width=6)
# ---- 大きさの目盛り（数cm〜30m）----
def sizebar(im, x0, y, w, u, a=1.0):
    d = ImageDraw.Draw(im, 'RGBA'); d.line((x0, y, x0 + w, y), fill=(200, 205, 220, int(200 * a)), width=4)
    for v, lab in ((0.0, '数cm'), (0.5, '約15m'), (1.0, '30m')):
        xx = x0 + w * v; d.line((xx, y - 16, xx, y + 16), fill=(200, 205, 220, int(220 * a)), width=4); alpha_text(im, (xx, y + 50), lab, Fb(36), PALE, a, sw=0)
    k = ease(u); L = 20 + (w - 20) * k
    if k > 0: skyfish(im, x0 + L / 2, y - 80, 0.0, L, k * 6, a * 0.95)
# ---- 縦穴の断面（ツバメの洞窟）と東京タワー ----
def pit(im, cx, ytop, ppm, u, t, a=1.0, rev=None):
    """ppm：1mあたりのpx。u：0→1 で深さの線をのばす。口 49〜62m、深さ 333〜370m、底の広間 約303m"""
    W, H = im.size; d = ImageDraw.Draw(im, 'RGBA'); rock = (54, 46, 40, int(255 * a)); air = (6, 8, 14, int(255 * a))
    d.rectangle((0, ytop, W, H), fill=rock)
    for k in range(70):   # 岩のすじ（決まった乱数）
        rr = np.random.default_rng(k); x = rr.uniform(0, W); y = rr.uniform(ytop + 10, H); d.line((x, y, x + rr.uniform(40, 160), y + rr.uniform(-8, 8)), fill=(70, 60, 52, int(200 * a)), width=3)
    top_hw = 31 * ppm; bot_hw = 151 * ppm; dl = 333 * ppm; dr = 370 * ppm
    pts = [(cx - top_hw, ytop), (cx + top_hw, ytop)]
    for s in np.linspace(0, 1, 24): pts.append((cx + top_hw + (bot_hw - top_hw) * s ** 1.8, ytop + (dr - 10 * ppm) * s))
    pts += [(cx + bot_hw, ytop + dr), (cx - bot_hw, ytop + dl)]
    for s in np.linspace(1, 0, 24): pts.append((cx - top_hw - (bot_hw - top_hw) * s ** 1.8, ytop + dl * s))
    d.polygon(pts, fill=air)
    if rev is not None:   # 深さの線に合わせて、穴が上から開いていく
        yr = ytop + 8 * ppm + (dr - 8 * ppm) * ease(rev)
        d.rectangle((cx - bot_hw - 2, yr, cx + bot_hw + 2, ytop + dr + 2), fill=rock)
    d.rectangle((0, ytop - 6, cx - top_hw, ytop), fill=(70, 110, 60, int(255 * a))); d.rectangle((cx + top_hw, ytop - 6, W, ytop), fill=(70, 110, 60, int(255 * a)))
    k = ease(u)
    if k > 0:
        xs = cx - bot_hw - 70; d.line((xs, ytop, xs, ytop + dl * k), fill=GOLD + (int(255 * a),), width=6)
        d.line((xs - 20, ytop, xs + 20, ytop), fill=GOLD + (int(255 * a),), width=5)
        if k > 0.98: d.line((xs - 20, ytop + dl, xs + 20, ytop + dl), fill=GOLD + (int(255 * a),), width=5)
    return (cx - bot_hw - 70, ytop + dl)
def tower(im, x, yb, hpx, a=1.0, col=(235, 120, 70)):
    """東京タワーの形を単純にした鉄塔のシルエット（333m）"""
    if a <= 0.01: return
    d = ImageDraw.Draw(im, 'RGBA'); c = col + (int(235 * a),); w = hpx * 0.28
    lv = [(0, w / 2), (0.36, w * 0.16), (0.7, w * 0.06), (0.9, w * 0.025), (1.0, 2)]
    for (h0, w0), (h1, w1) in zip(lv, lv[1:]):
        y0 = yb - hpx * h0; y1 = yb - hpx * h1
        d.line((x - w0, y0, x - w1, y1), fill=c, width=5); d.line((x + w0, y0, x + w1, y1), fill=c, width=5)
        n = 6
        for j in range(n):
            s0, s1 = j / n, (j + 1) / n
            xa0 = w0 + (w1 - w0) * s0; xa1 = w0 + (w1 - w0) * s1; ya = y0 + (y1 - y0) * s0; yb_ = y0 + (y1 - y0) * s1
            d.line((x - xa0, ya, x + xa1, yb_), fill=c, width=2); d.line((x + xa0, ya, x - xa1, yb_), fill=c, width=2)
    for h in (0.36, 0.62):
        y = yb - hpx * h; ww = w * (0.18 if h < 0.5 else 0.09); d.rectangle((x - ww, y - 10, x + ww, y + 6), fill=c)
# ---- ぶれのシミュレーション：1コマのあいだに虫が進み、羽ばたく ----
_BS = {}
def blur_sim(W2, H2, speed=1.0, fbeat=5.0, K=90):
    """1コマ（露光）のあいだの虫の位置と羽の角度を K 回に分けて計算し、重ねた明るさ（0〜1）を返す。
    speed：露光のあいだに進む長さ（画面幅の割合）、fbeat：露光のあいだの羽ばたきの回数"""
    key = (W2, H2, speed, fbeat, K)
    if key in _BS: return _BS[key]
    acc = np.zeros((K + 1, H2, W2), np.float32); cy = H2 / 2
    for k in range(K):
        s = k / (K - 1); x = W2 * 0.12 + W2 * 0.76 * speed * s; th = math.sin(2 * math.pi * fbeat * s) * 1.0   # 羽の角度（-1〜1 rad）
        L = Image.new('L', (W2, H2), 0); d = ImageDraw.Draw(L); bl = H2 * 0.11
        d.ellipse((x - bl, cy - bl * 0.38, x + bl, cy + bl * 0.38), fill=255)
        wl = H2 * 0.28
        for sgn in (1, -1):
            ang = sgn * (math.pi / 2) - sgn * th * 0.9
            ex, ey = x + wl * 0.25 * math.cos(ang), cy - wl * math.sin(abs(ang)) * sgn * (1 if sgn > 0 else 1)
            ey = cy - sgn * wl * abs(math.cos(th * 0.9 - 0.0)) * (0.35 + 0.65 * abs(math.sin(math.pi / 2 - th * 0.9)))
            ey = cy - sgn * wl * (0.2 + 0.8 * (0.5 + 0.5 * math.sin(2 * math.pi * fbeat * s)))
            d.polygon([(x - bl * 0.3, cy), (x + bl * 0.3, cy), (ex + bl * 0.2, ey), (ex - bl * 0.4, ey)], fill=150)
        acc[k + 1] = acc[k] + np.asarray(L, np.float32) / 255.0
    _BS[key] = acc / K * 6.0; return _BS[key]
def insect_at(W2, H2, s, speed=1.0, fbeat=5.0):
    """ある一瞬の虫（くっきり）"""
    L = Image.new('L', (W2, H2), 0); d = ImageDraw.Draw(L); cy = H2 / 2; x = W2 * 0.12 + W2 * 0.76 * speed * s; bl = H2 * 0.11; wl = H2 * 0.28
    d.ellipse((x - bl, cy - bl * 0.38, x + bl, cy + bl * 0.38), fill=255)
    for sgn in (1, -1):
        ey = cy - sgn * wl * (0.2 + 0.8 * (0.5 + 0.5 * math.sin(2 * math.pi * fbeat * s)))
        d.polygon([(x - bl * 0.3, cy), (x + bl * 0.3, cy), (x + bl * 0.45, ey), (x - bl * 0.2, ey)], fill=170)
    return L
def paste_mask(im, x, y, arr, col, a=1.0):
    m = Image.fromarray((np.clip(arr, 0, 1) * 255 * a).astype(np.uint8)); im.paste(col, (int(x), int(y)), m)
# ---- 番号つきカード（幻の駅と同じ形）----
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
# ---- 網（中国の実験のイメージ）----
def net(im, x0, y0, w, h, a=1.0, sag=0.0):
    d = ImageDraw.Draw(im, 'RGBA'); c = (210, 215, 225, int(200 * a))
    d.line((x0, y0 - 40, x0, y0 + h + 40), fill=(150, 150, 160, int(255 * a)), width=8); d.line((x0 + w, y0 - 40, x0 + w, y0 + h + 40), fill=(150, 150, 160, int(255 * a)), width=8)
    n = 14
    for i in range(n + 1):
        x = x0 + w * i / n; off = sag * math.sin(math.pi * i / n)
        d.line((x, y0 + off * 0.3, x, y0 + h + off), fill=c, width=2)
    for j in range(9):
        y = y0 + h * j / 8; pts = [(x0 + w * i / n, y + sag * math.sin(math.pi * i / n) * (0.3 + 0.7 * j / 8)) for i in range(n + 1)]
        d.line(pts, fill=c, width=2)
def moth(im, x, y, s, a=1.0, ang=0.0):
    """ガのシルエット（小さく）"""
    d = ImageDraw.Draw(im, 'RGBA'); c = (120, 100, 80, int(255 * a)); c2 = (160, 140, 110, int(255 * a))
    d.polygon([(x, y), (x - s, y - s * 0.8), (x - s * 1.1, y + s * 0.2)], fill=c2); d.polygon([(x, y), (x + s, y - s * 0.8), (x + s * 1.1, y + s * 0.2)], fill=c2)
    d.ellipse((x - s * 0.18, y - s * 0.5, x + s * 0.18, y + s * 0.6), fill=c)
# ---- 終了画面（最後の12秒）----
def endscreen(im, t, a=1.0):
    """左：16:9の枠（幅約45%）＋「次に見るならコレ ▶」、右：丸い枠（直径＝高さの25%）＋「チャンネル登録」"""
    W, H = im.size; d = ImageDraw.Draw(im, 'RGBA')
    fw = int(W * 0.45); fh = int(fw * 9 / 16); fx = int(W * 0.08); fy = int((H - fh) / 2)
    d.rounded_rectangle((fx - 4, fy - 4, fx + fw + 4, fy + fh + 4), 16, outline=GOLD + (int(255 * a),), width=6)
    d.rounded_rectangle((fx, fy, fx + fw, fy + fh), 12, fill=(0, 0, 0, int(110 * a)))
    alpha_text(im, (fx, fy - 60), '次に見るならコレ ▶', Mi(64), PALE, a, anchor='lm')
    r = int(H * 0.25 / 2); ccx = int(W * 0.76); ccy = int(H / 2)
    rr = r + 6 + 4 * math.sin(t * 2.5)
    d.ellipse((ccx - rr, ccy - rr, ccx + rr, ccy + rr), outline=GOLD + (int(255 * a),), width=6); d.ellipse((ccx - r, ccy - r, ccx + r, ccy + r), fill=(0, 0, 0, int(110 * a)))
    alpha_text(im, (ccx, ccy + r + 70), 'チャンネル登録', Mi(60), PALE, a)
    alpha_text(im, (W / 2, H - 70), 'ご視聴ありがとうございました', Fb(34), GREY, a, sw=0)
