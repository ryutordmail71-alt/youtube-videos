"""ビーレフェルト：追加の描画部品（ヨーロッパ地図・標識・質問カード・UFOの光・記念の石）"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, ICE, ctext, alpha_text, ease, fade
# ---- 地図（Natural Earth / world-atlas 50m）----
_T = json.load(open('/home/claude/bie/wa/package/countries-50m.json'))
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
    if any(-12 < lo < 32 and 34 < la < 62 for r in rings for lo, la in r[::10] + r[:1]): COUNTRIES[nm] = rings
BIE = (52.02, 8.53); CITIES = {'ハノーファー': (52.37, 9.73), 'ドルトムント': (51.51, 7.47), 'ベルリン': (52.52, 13.40)}
def europe(im, cx, cy, scale, lat0=51.0, lon0=10.0, a=1.0, hi='Germany', label=True):
    """(lat0,lon0) を (cx,cy) に置く簡単な投影。scale：緯度1度あたりのpx"""
    c0 = math.cos(math.radians(lat0)); d = ImageDraw.Draw(im, 'RGBA')
    P = lambda la, lo: (cx + (lo - lon0) * scale * c0, cy - (la - lat0) * scale)
    for nm, rings in COUNTRIES.items():
        for r in rings:
            pts = [P(la, lo) for lo, la in r]
            if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > im.width + 50: continue
            if nm == hi: d.polygon(pts, fill=(70, 90, 130, int(235 * a)), outline=(230, 220, 170, int(255 * a)))
            else: d.polygon(pts, fill=(34, 42, 62, int(230 * a)), outline=(95, 110, 140, int(200 * a)))
    return P
# ---- 高速道路の出口の標識（ドイツ風の青い板。架空のデザイン）----
def exit_sign(im, x, y, s, closed=0.0, a=1.0):
    L = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    w, h = s * 2.2, s * 1.0
    d.rectangle((x - s * 0.04, y + h / 2, x + s * 0.04, y + h / 2 + s * 1.4), fill=(120, 125, 135, 255))
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), int(s * 0.06), fill=(20, 70, 160, 255), outline=(240, 240, 240, 255), width=max(3, int(s * 0.03)))
    d.text((x, y - h * 0.18), 'Bielefeld', font=Fb(int(s * 0.36)), fill=(250, 250, 250, 255), anchor='mm')
    d.text((x, y + h * 0.26), 'AUSFAHRT  →', font=Fb(int(s * 0.18)), fill=(230, 235, 245, 255), anchor='mm')
    if closed > 0:
        k = ease(closed); r = s * 0.9
        d.line((x - r * k, y - h * 0.5 * k, x + r * k, y + h * 0.5 * k), fill=(230, 60, 60, 255), width=int(s * 0.1))
        d.line((x - r * k, y + h * 0.5 * k, x + r * k, y - h * 0.5 * k), fill=(230, 60, 60, 255), width=int(s * 0.1))
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (0, 0), L); return im
# ---- 質問カード ----
def qcard(im, x, y, w, h, no, txt, a, ans=0.0):
    if a <= 0.01: return
    L = Image.new('RGBA', (int(w) + 40, int(h) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((20, 20, w + 20, h + 20), 22, fill=(8, 12, 22, 215), outline=GOLD + (255,), width=4)
    d.ellipse((44, 20 + h / 2 - 42, 128, 20 + h / 2 + 42), fill=GOLD + (255,)); d.text((86, 20 + h / 2), str(no), font=BE(76), fill=(20, 20, 20, 255), anchor='mm')
    d.text((160, 20 + h / 2), txt, font=Mi(int(h * 0.36)), fill=PALE + (255,), anchor='lm')
    if ans > 0:
        aa = int(255 * ease(ans)); d.rounded_rectangle((w - 230, 20 + h / 2 - 48, w - 10, 20 + h / 2 + 48), 16, fill=(150, 40, 40, aa)); d.text((w - 120, 20 + h / 2), 'いいえ', font=Mi(50), fill=(255, 255, 255, aa), anchor='mm')
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (int(x - 20 + (1 - a) * 40), int(y - 20)), L)
# ---- 「やつら」：たくさんの目（暗闇に光る点の対）----
def eyes(im, t, n, a=1.0, seed=5, col=(255, 210, 120)):
    rng = np.random.default_rng(seed); d = ImageDraw.Draw(im, 'RGBA')
    for i in range(n):
        x = rng.uniform(80, im.width - 80); y = rng.uniform(im.height * 0.2, im.height * 0.85); s = rng.uniform(6, 16); ph = rng.uniform(0, 6)
        k = fade((a * n - i) / 1.0) * (0.55 + 0.45 * math.sin(t * 0.8 + ph)) ** 2
        if math.sin(t * 0.37 + ph * 3) > 0.96: k *= 0.1   # まばたき
        for dx in (-s * 1.6, s * 1.6): d.ellipse((x + dx - s, y - s * 0.55, x + dx + s, y + s * 0.55), fill=col + (int(220 * k),))
# ---- UFO の光（ぼんやりした円盤の影と光の柱）----
def ufo(im, x, y, s, t, a=1.0):
    if a <= 0.01: return
    L = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.polygon([(x - s * 0.5, y + s * 0.15), (x + s * 0.5, y + s * 0.15), (x + s * 1.3, im.height), (x - s * 1.3, im.height)], fill=(170, 230, 255, int(60 * a)))
    L = L.filter(ImageFilter.GaussianBlur(s * 0.15)); d = ImageDraw.Draw(L)
    d.ellipse((x - s, y - s * 0.18, x + s, y + s * 0.22), fill=(30, 36, 50, int(240 * a)), outline=(140, 200, 230, int(200 * a)), width=3)
    d.ellipse((x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.1), fill=(60, 80, 110, int(230 * a)))
    for k in range(8):
        ang = t * 1.2 + k * math.pi / 4; px = x + math.cos(ang) * s * 0.8; on = (math.sin(ang) + 1) / 2
        d.ellipse((px - 9, y + s * 0.02 - 9, px + 9, y + s * 0.02 + 9), fill=(150, 240, 255, int(255 * a * (0.3 + 0.7 * on))))
    im.paste(L, (0, 0), L)
# ---- 記念の石（600kgの石：絵はイメージ）----
def stone(im, cx, by, s, a=1.0, txt=True):
    if a <= 0.01: return
    L = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rng = np.random.default_rng(11); pts = []
    for k in range(28):
        ang = math.pi + k / 27 * math.pi; r = s * (1 + 0.06 * rng.standard_normal())
        pts.append((cx + math.cos(ang) * r * 1.25, by + math.sin(ang) * r * 0.85))
    d.polygon(pts, fill=(118, 116, 110, 255), outline=(70, 68, 64, 255))
    for k in range(40):
        px = cx + rng.uniform(-1, 1) * s * 1.0; py = by - rng.uniform(0.05, 0.75) * s * 0.85; rr = rng.uniform(4, 14)
        d.ellipse((px - rr, py - rr * 0.6, px + rr, py + rr * 0.6), fill=(rng.integers(90, 150),) * 3 + (120,))
    if txt:
        d.rounded_rectangle((cx - s * 0.62, by - s * 0.55, cx + s * 0.62, by - s * 0.12), 8, fill=(40, 42, 46, 255), outline=(190, 170, 110, 255), width=3)
        d.text((cx, by - s * 0.44), 'Das Ende der', font=Fb(int(s * 0.11)), fill=(225, 205, 150, 255), anchor='mm')
        d.text((cx, by - s * 0.25), 'Bielefeld-Verschwörung', font=Fb(int(s * 0.11)), fill=(225, 205, 150, 255), anchor='mm')
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).ellipse((cx - s * 1.4, by - s * 0.08, cx + s * 1.4, by + s * 0.12), fill=int(160 * a))
    im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (0, 0), L)
# ---- 掲示板の画面（1994年の文字だけの画面）----
def terminal(im, x, y, w, h, lines, t, t0, cps=18, a=1.0):
    d = ImageDraw.Draw(im, 'RGBA'); d.rounded_rectangle((x, y, x + w, y + h), 18, fill=(6, 16, 10, int(235 * a)), outline=(80, 160, 110, int(255 * a)), width=4)
    n = int(max(0, t - t0) * cps); used = 0; lh = 58
    for i, ln in enumerate(lines):
        k = max(0, min(len(ln), n - used)); used += len(ln)
        if k <= 0 and ln: break
        d.text((x + 40, y + 40 + i * lh), ln[:k], font=Fb(40), fill=(120, 240, 160, int(255 * a)))
    d.text((x + w - 20, y + h - 16), '画面はイメージ', font=Fb(24), fill=(120, 180, 140, int(255 * a)), anchor='rs')
    if int(t * 2) % 2 == 0:
        i = min(len(lines) - 1, sum(1 for _ in lines)); cy = y + 40 + min(len(lines), max(1, sum(1 for j, l in enumerate(lines) if sum(len(q) for q in lines[:j]) < n))) * lh - lh
        d.rectangle((x + 40, cy + 50, x + 64, cy + 54), fill=(120, 240, 160, int(255 * a)))
