"""ブラックアイド・キッズ：描画部品（フードの子どもの影・のぞき穴・窓のノック・目の図・新聞・テレビ）
顔は描かない（後ろから光が当たった黒い影だけ）。"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import prnd as R
from prnd import Fo, Fb, Mi, BE, PALE, GOLD, RED, GREY, ICE, ctext, alpha_text, ease, fade
from sdraw import worldmap, pin, card, endscreen

def kid(im, x, by, h, a=1.0, sway=0.0, col=(6, 7, 10), rim=(150, 170, 210)):
    """フードをかぶった子どもの影（顔は見えない、霧の中の黒い影）。x：中心、by：足もと、h：背の高さ(px)"""
    if a <= 0.01: return im
    m = int(h * 0.3); S = (int(h * 0.7) + 2 * m, int(h) + 2 * m); L = Image.new('L', S, 0); d = ImageDraw.Draw(L)
    cx = S[0] / 2 + sway; b = S[1] - m; top = b - h
    def pt(u, v): return (cx + u * h, top + v * h)
    # 頭とフード（少しとがった形）
    hood = [pt(0.0, 0.0), pt(0.06, 0.012), pt(0.095, 0.05), pt(0.105, 0.1), pt(0.1, 0.15), pt(0.085, 0.185),
            pt(-0.085, 0.185), pt(-0.1, 0.15), pt(-0.105, 0.1), pt(-0.09, 0.045), pt(-0.05, 0.01)]
    d.polygon(hood, fill=255)
    # 上着（なで肩、すそが少し広い）
    body = [pt(-0.07, 0.17), pt(0.07, 0.17), pt(0.15, 0.22), pt(0.175, 0.28), pt(0.185, 0.5), pt(0.175, 0.56),
            pt(-0.175, 0.56), pt(-0.185, 0.5), pt(-0.175, 0.28), pt(-0.15, 0.22)]
    d.polygon(body, fill=255)
    # だらんと下げた腕
    for sg in (1, -1):
        d.polygon([pt(sg * 0.16, 0.24), pt(sg * 0.2, 0.3), pt(sg * 0.205, 0.55), pt(sg * 0.19, 0.6), pt(sg * 0.165, 0.6), pt(sg * 0.155, 0.4)], fill=255)
    # 足（細め）
    for sg in (1, -1):
        d.polygon([pt(sg * 0.015, 0.55), pt(sg * 0.13, 0.55), pt(sg * 0.11, 0.97), pt(sg * 0.125, 1.0), pt(sg * 0.035, 1.0), pt(sg * 0.03, 0.97)], fill=255)
    L = L.filter(ImageFilter.GaussianBlur(max(1.2, h * 0.007)))
    edge = L.filter(ImageFilter.GaussianBlur(h * 0.025)).point(lambda v: int(v * 0.45 * a))
    ox, oy = int(x - S[0] / 2), int(by - b)
    im.paste(rim, (ox, oy), edge)
    im.paste(col, (ox, oy), L.point(lambda v: int(v * 0.94 * a)))
    sh = Image.new('L', (int(h * 0.6), int(h * 0.06)), 0); ImageDraw.Draw(sh).ellipse((0, 0, sh.width, sh.height), fill=int(120 * a))
    sh = sh.filter(ImageFilter.GaussianBlur(h * 0.01)); im.paste((0, 0, 0), (int(x - sh.width / 2), int(by - sh.height / 2)), sh)
    return im

def kids(im, x, by, h, a=1.0, t=0.0, gap=None):
    gap = gap or h * 0.24
    kid(im, x - gap, by, h, a, sway=math.sin(t * 0.7) * h * 0.004)
    kid(im, x + gap, by + h * 0.01, h * 0.8, a, sway=math.sin(t * 0.6 + 1) * h * 0.004)
    return im

def peephole(im, src, cx, cy, r, a=1.0):
    """のぞき穴の丸い視界：src（同じ大きさの絵）を魚眼っぽく丸く切り抜いて重ね、外は真っ黒"""
    W, H = im.size
    dark = Image.new('RGB', (W, H), (2, 2, 4))
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(r * 0.06))
    # 円の内側も、ふちに向かって暗く
    yy, xx = np.mgrid[0:H, 0:W]; rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    v = Image.fromarray((np.clip((rr - 0.55) / 0.5, 0, 1) ** 1.5 * 220).astype(np.uint8))
    inner = src.copy(); inner.paste((0, 0, 0), (0, 0), v)
    out = Image.composite(inner, dark, m)
    if a < 1: out = Image.blend(im, out, a)
    return out

def bulge(src, k=0.35):
    """魚眼レンズのように真ん中をふくらませる"""
    W, H = src.size; a = np.asarray(src)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); cx, cy = W / 2, H / 2; R0 = min(W, H) / 2
    dx, dy = (xx - cx) / R0, (yy - cy) / R0; r = np.sqrt(dx * dx + dy * dy)
    f = np.where(r < 1, (1 - k) + k * r * r, 1.0)
    sx = np.clip(cx + dx * f * R0, 0, W - 1).astype(np.int32); sy = np.clip(cy + dy * f * R0, 0, H - 1).astype(np.int32)
    return Image.fromarray(a[sy, sx])

def knock(im, x, y, t, t0, a=1.0, col=(235, 240, 255), label=True, size=90):
    """コン、コン：t0 と t0+0.45 に広がる輪と文字"""
    d = ImageDraw.Draw(im, 'RGBA')
    for j, tt in enumerate((t0, t0 + 0.45)):
        u = t - tt
        if 0 <= u < 1.2:
            for k in range(2):
                uu = u - k * 0.12
                if uu < 0: continue
                rr = 20 + uu * 160; al = int(200 * (1 - uu / 1.2) * a)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col + (max(0, al),), width=5)
        if label and u >= 0:
            al = fade(1.6 - u) if u > 1.0 else 1.0
            alpha_text(im, (x + (-80 if j == 0 else 90), y - 130 - j * 30), 'コン', Mi(size), PALE, al * a)

def eye(im, cx, cy, w, kind, a=1.0):
    """目の図（ふつう／うわさの目）。kind='normal' or 'black'。人の顔は描かない"""
    if a <= 0.01: return
    h = w * 0.48; L = Image.new('RGBA', (int(w) + 40, int(h) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ox, oy = 20, 20; pts = []
    for i in range(41):
        u = i / 40; pts.append((ox + w * u, oy + h / 2 - h / 2 * math.sin(math.pi * u)))
    for i in range(41):
        u = 1 - i / 40; pts.append((ox + w * u, oy + h / 2 + h / 2 * math.sin(math.pi * u)))
    m = Image.new('L', L.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    fill = Image.new('RGBA', L.size, (0, 0, 0, 0)); fd = ImageDraw.Draw(fill)
    if kind == 'normal':
        fd.rectangle((0, 0, L.width, L.height), fill=(235, 232, 225, 255))
        r = h * 0.42; c = (ox + w / 2, oy + h / 2); fd.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=(110, 80, 50, 255))
        r2 = r * 0.45; fd.ellipse((c[0] - r2, c[1] - r2, c[0] + r2, c[1] + r2), fill=(10, 10, 10, 255))
        fd.ellipse((c[0] + r * 0.2, c[1] - r * 0.45, c[0] + r * 0.45, c[1] - r * 0.2), fill=(255, 255, 255, 230))
    else:
        fd.rectangle((0, 0, L.width, L.height), fill=(4, 4, 6, 255))
        fd.ellipse((ox + w * 0.58, oy + h * 0.18, ox + w * 0.66, oy + h * 0.32), fill=(120, 130, 150, 160))
    L.paste(fill, (0, 0), m)
    d = ImageDraw.Draw(L); d.line(pts[:41], fill=(200, 205, 215, 255), width=4); d.line(pts[41:], fill=(200, 205, 215, 160), width=3)
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (int(cx - L.width / 2), int(cy - L.height / 2)), L)

def carwin(im, a=1.0):
    """車の中から見た運転席の窓わく（左右・下を暗く）"""
    W, H = im.size; L = Image.new('L', (W, H), 0); d = ImageDraw.Draw(L)
    d.polygon([(0, 0), (W * 0.12, 0), (W * 0.06, H), (0, H)], fill=250)                  # 前の柱
    d.polygon([(W * 0.92, 0), (W, 0), (W, H), (W * 0.96, H)], fill=250)                    # 後ろの柱
    d.rectangle((0, H * 0.83, W, H), fill=250)                                              # ドアの下
    d.rectangle((0, 0, W, H * 0.06), fill=250)
    L = L.filter(ImageFilter.GaussianBlur(6))
    if a < 1: L = L.point(lambda v: int(v * a))
    im.paste((8, 9, 12), (0, 0), L)
    dd = ImageDraw.Draw(im, 'RGBA'); dd.line((W * 0.06, H * 0.83, W * 0.96, H * 0.83), fill=(70, 75, 90, int(200 * a)), width=5)

def paper(im, x, y, w, a=1.0, n=1, ang=0.0):
    """新聞（中身は灰色の線だけ）"""
    if a <= 0.01: return
    h = w * 1.3; L = Image.new('RGBA', (int(w) + 20, int(h) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((10, 10, w + 10, h + 10), fill=(232, 228, 214, 255), outline=(90, 90, 90, 255), width=2)
    d.rectangle((24, 24, w - 4, 24 + h * 0.07), fill=(40, 40, 40, 255))
    d.rectangle((24, 34 + h * 0.08, w - 4, 34 + h * 0.2), fill=(20, 20, 20, 255))
    d.rectangle((24, 44 + h * 0.21, w * 0.55, 44 + h * 0.5), fill=(70, 70, 75, 255))
    for k in range(14):
        yy = 44 + h * 0.21 + k * h * 0.035
        d.line((w * 0.6, yy, w - 4, yy), fill=(140, 140, 140, 255), width=3)
    for k in range(9):
        yy = 54 + h * 0.53 + k * h * 0.045; d.line((24, yy, w - 4, yy), fill=(140, 140, 140, 255), width=3)
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC)
    if a < 1: L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    im.paste(L, (int(x - L.width / 2), int(y - L.height / 2)), L)

def tv(im, x, y, w, a=1.0, t=0.0):
    if a <= 0.01: return
    h = w * 0.62; d = ImageDraw.Draw(im, 'RGBA')
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 18, fill=(30, 32, 40, int(255 * a)), outline=(160, 165, 180, int(255 * a)), width=4)
    d.rectangle((x - w / 2 + 20, y - h / 2 + 20, x + w / 2 - 20, y + h / 2 - 20), fill=(60, 80, 110, int(255 * a)))
    kids(im, x, y + h / 2 - 24, h * 0.55, a * 0.95, t)
    d.line((x - w * 0.15, y + h / 2, x - w * 0.25, y + h / 2 + 40), fill=(160, 165, 180, int(255 * a)), width=5)
    d.line((x + w * 0.15, y + h / 2, x + w * 0.25, y + h / 2 + 40), fill=(160, 165, 180, int(255 * a)), width=5)

def film(im, x, y, w, a=1.0, t=0.0):
    if a <= 0.01: return
    h = w * 0.62; d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=(8, 8, 10, int(255 * a)))
    for k in range(9):
        xx = x - w / 2 + 14 + k * (w - 28) / 8
        d.rectangle((xx - 9, y - h / 2 + 8, xx + 9, y - h / 2 + 26), fill=(80, 80, 88, int(255 * a))); d.rectangle((xx - 9, y + h / 2 - 26, xx + 9, y + h / 2 - 8), fill=(80, 80, 88, int(255 * a)))
    d.rectangle((x - w / 2 + 16, y - h / 2 + 36, x + w / 2 - 16, y + h / 2 - 36), fill=(90, 70, 50, int(255 * a)))
    kid(im, x, y + h / 2 - 40, h * 0.6, a)
