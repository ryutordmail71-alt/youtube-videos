"""ポリビアス：描画部品（写真・霧・地図・黒いゲーム機）"""
import math, json, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
FPS = 30
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'; NOTOB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc'; BEBAS = '/home/claude/fonts/BebasNeue-Regular.ttf'
_F = {}
def font(p, s):
    s = max(8, int(s)); k = (p, s)
    if k not in _F: _F[k] = ImageFont.truetype(p, s, index=0) if p.endswith('.ttc') else ImageFont.truetype(p, s)
    return _F[k]
Fo = lambda s: font(NOTO, s); Fb = lambda s: font(NOTOB, s); Mi = lambda s: font(SERIF, s); BE = lambda s: font(BEBAS, s)
PALE = (236, 238, 245); GOLD = (255, 210, 80); RED = (230, 70, 70); GREY = (170, 175, 190); CYAN = (110, 230, 220); ICE = (150, 200, 255)
NOTE = '※言い伝え・うわさをもとにした紹介です。実在の場所の立ち入り禁止区域には入らないでください'
PH = '/home/claude/mbe/ph'
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return u * u * (3 - 2 * u)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0, sf=(0, 0, 0)): d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=sf)
def writer(path, w, h):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
# ---- 写真：暗め・青み、ゆっくり寄る ----
_P = {}
def photo(name, w, h, bright=0.62, blue=0.35, over=1.18, blur=0):
    k = (name, w, h, bright, blue, blur)
    if k in _P: return _P[k]
    im = Image.open(name if name.startswith('/') else f'{PH}/{name}').convert('RGB')
    s = max(w * over / im.width, h * over / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(0.55)).enhance(1.12); im = ImageEnhance.Brightness(im).enhance(bright)
    a = np.asarray(im).astype(np.float32); tint = np.array((40, 70, 120), np.float32)
    a = a * (1 - blue * 0.35) + tint * blue * 0.35 * (a.mean(2, keepdims=True) / 128 + 0.3)
    _P[k] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if blur: _P[k] = _P[k].filter(ImageFilter.GaussianBlur(blur * 1.2))
    return _P[k]
def kb(name, w, h, u, z0=1.0, z1=1.12, cx0=0.5, cy0=0.5, cx1=0.5, cy1=0.5, **kw):
    """Ken Burns：u=0→1 で z0→z1 に寄りながら中心を動かす"""
    src = photo(name, w, h, **kw); u = ease(u) * 0.5 + u * 0.5
    z = z0 + (z1 - z0) * u; cx = cx0 + (cx1 - cx0) * u; cy = cy0 + (cy1 - cy0) * u
    bw = min(src.width, src.height * w / h) / z; bh = bw * h / w
    x0 = min(max(0, src.width * cx - bw / 2), src.width - bw); y0 = min(max(0, src.height * cy - bh / 2), src.height - bh)
    return src.resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + bw, y0 + bh))
# ---- 霧 ----
_FOG = {}
def fog_tex(w, h):
    if (w, h) not in _FOG:
        rng = np.random.default_rng(3); n = rng.random((h // 8 + 2, w * 2 // 8 + 2)).astype(np.float32)
        im = Image.fromarray((n * 255).astype(np.uint8)).resize((w * 2, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
        a = np.asarray(im).astype(np.float32) / 255; a = (a - a.min()) / (a.max() - a.min() + 1e-6)
        _FOG[(w, h)] = Image.fromarray((a ** 1.6 * 255).astype(np.uint8))
    return _FOG[(w, h)]
def fog(im, t, k=0.28, col=(150, 170, 200)):
    w, h = im.size; kk = round(k, 2); key = (w, h, kk)
    if key not in _FOG: _FOG[key] = fog_tex(w, h).point(lambda v: int(v * kk))
    x = int((t * 22) % w); m = _FOG[key].crop((x, 0, x + w, h)); im.paste(Image.new('RGB', (w, h), col), (0, 0), m); return im
_VIG = {}
def vignette(im, k=0.75):
    w, h = im.size
    if (w, h, k) not in _VIG:
        yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        _VIG[(w, h, k)] = Image.fromarray((np.clip((r - 0.45) / 0.9, 0, 1) ** 1.3 * 255 * k).astype(np.uint8))
    im.paste(Image.new('RGB', (w, h), (0, 0, 0)), (0, 0), _VIG[(w, h, k)]); return im
_DB = {}
def darkbg(w, h, col=(14, 20, 34)):
    if (w, h, col) in _DB: return _DB[(w, h, col)]
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx - w / 2) / w) ** 2 + ((yy - h * 0.45) / h) ** 2)
    t = np.clip(r / 0.8, 0, 1)[..., None]; c = np.array(col, float) * (1 - t) + np.array((2, 3, 7), float) * t
    _DB[(w, h, col)] = Image.fromarray(c.astype(np.uint8)); return _DB[(w, h, col)]
def glow(im, x, y, r, col, a=120):
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((x - r, y - r, x + r, y + r), fill=col + (int(a),))
    im.paste(g.filter(ImageFilter.GaussianBlur(r * 0.45)), (0, 0), g.filter(ImageFilter.GaussianBlur(r * 0.45))); return im
def shadow_text(im, xy, t, f, fill, anchor='mm', blur=10, a=230, sw=2):
    l = Image.new('L', im.size, 0); ImageDraw.Draw(l).text((xy[0], xy[1] + 4), t, font=f, fill=a, anchor=anchor, stroke_width=sw + 8, stroke_fill=a)
    im.paste(Image.new('RGB', im.size, (0, 0, 0)), (0, 0), l.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
_SP = {}
def _sprite(t, f, fill, sw, blur):
    k = (t, id(f), fill, sw, blur)
    if k not in _SP:
        l, tp, r, b = f.getbbox(t, stroke_width=sw); m = blur * 3 + sw + 12
        w, h = int(r - l + 2 * m), int(b - tp + 2 * m + 4); ox, oy = -l + m, -tp + m
        sh = Image.new('L', (w, h), 0); ImageDraw.Draw(sh).text((ox, oy + 4), t, font=f, fill=220, stroke_width=sw + 8, stroke_fill=220)
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
        tx = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(tx).text((ox, oy), t, font=f, fill=fill + (255,), stroke_width=sw, stroke_fill=(0, 0, 0, 255))
        _SP[k] = (sh, tx, ox, oy)
    return _SP[k]
def alpha_text(im, xy, t, f, fill, a, anchor='mm', sw=2, blur=10):
    """a=0〜1 の不透明度で、影つき文字を描く（文字の絵はキャッシュ）"""
    if a <= 0.01: return
    sh, tx, ox, oy = _sprite(t, f, tuple(fill[:3]), sw, blur)
    l, tp, r, b = f.getbbox(t, anchor=anchor, stroke_width=sw)
    l0, tp0, _, _ = f.getbbox(t, stroke_width=sw)
    px = int(xy[0] + l - l0 - ox + (ox + l0) - l0 - (ox - (-l0 + (ox + l0)))) if False else int(xy[0] + (l - l0) - ox)
    py = int(xy[1] + (tp - tp0) - oy)
    if a < 0.99:
        shm = sh.point(lambda v: int(v * a)); tm = tx.getchannel('A').point(lambda v: int(v * a))
    else: shm = sh; tm = tx.getchannel('A')
    im.paste((0, 0, 0), (px, py, px + sh.width, py + sh.height), shm)
    im.paste(tx.convert('RGB'), (px, py), tm)
def tag_image(d, w, h, s=26):
    d.rounded_rectangle((w - 24 - s * 3.6, 24, w - 24, 24 + s * 1.7), 8, fill=(0, 0, 0, 150)); d.text((w - 24 - s * 1.8, 24 + s * 0.85), 'イメージ', font=Fb(s), fill=(230, 230, 235), anchor='mm')
def note(d, w, h, size=20):
    if w > h: d.text((w - 22, h - 10), NOTE, font=Fb(size), fill=(215, 218, 225), anchor='rs', stroke_width=2, stroke_fill=(0, 0, 0))
    else:
        d.text((w / 2, h - 52), '※言い伝え・うわさをもとにした紹介です', font=Fb(size), fill=(215, 218, 225), anchor='ms', stroke_width=2, stroke_fill=(0, 0, 0))
        d.text((w / 2, h - 18), '実在の場所の立ち入り禁止区域には入らないでください', font=Fb(size), fill=(215, 218, 225), anchor='ms', stroke_width=2, stroke_fill=(0, 0, 0))
# ---- 黒いゲーム機（架空。飾りのない黒い箱＋光る図形の画面）----
def cabinet(im, cx, by, s, t, lit=1.0, alpha=1.0):
    if alpha <= 0.01: return im
    LW, LH = int(s * 1.6), int(s * 1.3); ox, oy = int(cx - LW / 2), int(by - s * 1.15)
    loc = im.crop((ox, oy, ox + LW, oy + LH)); _cabinet(loc, cx - ox, by - oy, s, t, lit, alpha); im.paste(loc, (ox, oy)); return im
_GL = {}
def _cabinet(im, cx, by, s, t, lit=1.0, alpha=1.0):
    """cx：中心、by：床の位置、s：高さ(px)。画面の図形はゆっくり回る（点滅はしない）"""
    if alpha <= 0.01: return im
    w = s * 0.42; L = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    top = by - s; edge = (60, 66, 82, 255)
    body = [(cx - w / 2, top + s * 0.02), (cx + w / 2, top), (cx + w / 2, by), (cx - w / 2, by)]
    d.polygon(body, fill=(8, 9, 12, 255), outline=edge)
    d.polygon([(cx - w / 2 - s * 0.03, top + s * 0.50), (cx + w / 2 + s * 0.03, top + s * 0.50), (cx + w / 2 + s * 0.06, top + s * 0.60), (cx - w / 2 - s * 0.06, top + s * 0.60)], fill=(14, 15, 20, 255), outline=edge)
    d.rectangle((cx - w / 2, top, cx + w / 2, top + s * 0.09), fill=(5, 5, 8, 255), outline=edge)   # 名前のない看板
    sx0, sy0, sx1, sy1 = cx - w * 0.38, top + s * 0.14, cx + w * 0.38, top + s * 0.46
    d.rectangle((sx0 - 6, sy0 - 6, sx1 + 6, sy1 + 6), fill=(2, 2, 4, 255))
    for k in range(2):   # コイン投入口
        x = cx - w * 0.16 + k * w * 0.32; d.rectangle((x - s * 0.018, top + s * 0.70, x + s * 0.018, top + s * 0.76), fill=(30, 32, 40, 255), outline=(90, 30, 30, 255))
    d.ellipse((cx - s * 0.03, top + s * 0.525, cx + s * 0.03, top + s * 0.565), fill=(25, 25, 30, 255), outline=edge)
    if lit > 0.01:   # 画面の光る図形
        bx0, by0 = int(sx0 - 10), int(sy0 - 10); g = Image.new('RGBA', (int(sx1 - sx0) + 20, int(sy1 - sy0) + 20), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        scx, scy = (sx0 + sx1) / 2 - bx0, (sy0 + sy1) / 2 - by0; R = (sy1 - sy0) * 0.42
        for i in range(5):
            r = R * (1 - i * 0.17); n = 3 + i % 3; a0 = t * (0.5 + 0.18 * i) * (1 if i % 2 else -1)
            pts = [(scx + r * math.cos(a0 + 2 * math.pi * j / n), scy + r * 0.92 * math.sin(a0 + 2 * math.pi * j / n)) for j in range(n)]
            c = [(110, 230, 220), (160, 140, 255), (255, 210, 120), (110, 230, 220), (230, 120, 200)][i]
            gd.polygon(pts, outline=c + (int(230 * lit),), width=max(2, int(s * 0.006)))
        gd.ellipse((scx - 5, scy - 5, scx + 5, scy + 5), fill=(255, 255, 255, int(220 * lit)))
        L.alpha_composite(g.filter(ImageFilter.GaussianBlur(5)), (bx0, by0)); L.alpha_composite(g, (bx0, by0))
    if alpha < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * alpha)))
    gk = (im.size, int(cx), int(top), int(s), round(lit * alpha, 1))
    if gk not in _GL:
        gl = Image.new('L', im.size, 0); ImageDraw.Draw(gl).ellipse((cx - w, top + s * 0.05, cx + w, top + s * 0.55), fill=int(45 * lit * alpha)); _GL[gk] = gl.filter(ImageFilter.GaussianBlur(s * 0.12))
    im.paste((90, 200, 210), (0, 0), _GL[gk])
    im.paste(L, (0, 0), L); return im
# ---- 点で描いたアメリカの地図（空港の位置）----
_AP = None
def airports():
    global _AP
    if _AP is None:
        import csv
        rows = [(float(r['latitude']), float(r['longitude'])) for r in csv.DictReader(open('/home/claude/plb/airports.csv'))]
        _AP = [(la, lo) for la, lo in rows if 24 < la < 50 and -126 < lo < -66]
    return _AP
def usmap(im, cx, cy, scale, hi=None, a=1.0):
    """経度・緯度を簡単な投影で。scale：経度1度あたりのpx。hi=(lat,lon) のまわりを明るく"""
    d = ImageDraw.Draw(im, 'RGBA'); c0 = math.cos(math.radians(38))
    def P(la, lo): return cx + (lo + 96) * scale * c0, cy - (la - 38) * scale
    for la, lo in airports():
        x, y = P(la, lo)
        if -20 < x < im.width + 20 and -20 < y < im.height + 20:
            col = (120, 160, 220)
            if hi and abs(la - hi[0]) < 4.5 and abs(lo - hi[1]) < 6: col = (190, 210, 240)
            r = max(1.5, scale * 0.07); d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(170 * a),))
    return P
