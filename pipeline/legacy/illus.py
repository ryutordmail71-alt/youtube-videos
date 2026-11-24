import math, os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
S = 2
CW, CH = 1600, 900
BG = (246, 244, 238)
FD = '/usr/share/fonts/opentype/noto/'
def F(sz, w='Black'): return ImageFont.truetype(FD + f'NotoSansCJK-{w}.ttc', sz * S, index=0)

def canvas(bg=BG):
    im = Image.new('RGB', (CW * S, CH * S), bg); return im, ImageDraw.Draw(im)
def fin(im): return im.resize((CW, CH), Image.LANCZOS)
def L(d, pts, fill=(20, 20, 20), w=8):
    d.line([(x * S, y * S) for x, y in pts], fill=fill, width=w * S, joint='curve')
def C(d, cx, cy, r, fill=None, outline=None, w=0):
    d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=fill, outline=outline, width=w * S)
def R(d, x0, y0, x1, y1, fill=None, outline=None, w=0):
    d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill, outline=outline, width=w * S)
def T(d, x, y, t, sz=40, fill=(200, 30, 30), w='Black', anchor='mm'):
    d.text((x * S, y * S), t, font=F(sz, w), fill=fill, anchor=anchor)
RED = (215, 40, 40); BLUE = (40, 90, 200)

def muller():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        for y, inward in ((300, True), (620, False)):
            x0, x1 = 450, 1150
            L(d, [(x0, y), (x1, y)], w=10)
            if not ans:
                for x, s in ((x0, 1), (x1, -1)):
                    dx = 70 * s * (1 if inward else -1)
                    L(d, [(x, y), (x + dx, y - 60)], w=10); L(d, [(x, y), (x + dx, y + 60)], w=10)
            else:
                for x, s in ((x0, 1), (x1, -1)):
                    dx = 70 * s * (1 if inward else -1)
                    L(d, [(x, y), (x + dx, y - 60)], fill=(200, 200, 200), w=10); L(d, [(x, y), (x + dx, y + 60)], fill=(200, 200, 200), w=10)
        T(d, 300, 300, 'A', 70, (60, 60, 60)); T(d, 300, 620, 'B', 70, (60, 60, 60))
        if ans:
            for x in (450, 1150): L(d, [(x, 150), (x, 760)], fill=RED, w=5)
            T(d, 800, 830, '同じ長さ / Same length', 52)
        out.append(fin(im))
    return out

def ebbing():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        OR = (240, 140, 30)
        C(d, 450, 450, 55, OR)
        C(d, 1150, 450, 55, OR)
        if not ans:
            for k in range(6):
                a = k * math.pi / 3; C(d, 450 + 210 * math.cos(a), 450 + 210 * math.sin(a), 95, (110, 130, 200))
            for k in range(8):
                a = k * math.pi / 4; C(d, 1150 + 95 * math.cos(a), 450 + 95 * math.sin(a), 24, (110, 130, 200))
        else:
            L(d, [(395, 395), (1205, 395)], fill=RED, w=4); L(d, [(395, 505), (1205, 505)], fill=RED, w=4)
            T(d, 800, 760, '同じ大きさ / Same size', 52)
        out.append(fin(im))
    return out

def ponzo():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        if not ans:
            L(d, [(620, 60), (180, 880)], fill=(60, 60, 60), w=10); L(d, [(980, 60), (1420, 880)], fill=(60, 60, 60), w=10)
            for y in range(120, 900, 70): L(d, [(800 - (y * 0.47 + 140), y), (800 + (y * 0.47 + 140), y)], fill=(170, 150, 120), w=6)
        Y = (230, 40, 40) if False else (235, 190, 30)
        R(d, 650, 230, 950, 270, Y); R(d, 650, 650, 950, 690, Y)
        if ans:
            L(d, [(650, 150), (650, 780)], fill=RED, w=4); L(d, [(950, 150), (950, 780)], fill=RED, w=4)
            T(d, 800, 830, '同じ長さ / Same length', 52)
        out.append(fin(im))
    return out

def cafe():
    out = []
    for ans in (0, 1):
        im, d = canvas((255, 255, 255))
        sq = 80; off = [0, 25, 50, 25]
        for r in range(10):
            y = 50 + r * (sq + 4)
            o = off[r % 4]
            for c in range(-1, 21):
                x = 40 + c * sq * 2 + o
                R(d, x, y, x + sq, y + sq, (0, 0, 0))
            R(d, 0, y + sq, CW, y + sq + 4, (128, 128, 128))
        if ans:
            for r in range(10):
                y = 50 + r * (sq + 4) + sq + 2; L(d, [(0, y), (CW, y)], fill=RED, w=3)
            R(d, 400, 380, 1200, 470, (255, 255, 255)); T(d, 800, 425, '全部まっすぐ・平行 / All parallel', 46)
        out.append(fin(im))
    return out

def zollner():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        for k in range(6):
            x0 = 150 + k * 230
            L(d, [(x0, 60), (x0 + 400, 840)], w=7)
            if not ans:
                for t in range(1, 16):
                    px = x0 + 400 * t / 16; py = 60 + 780 * t / 16
                    if k % 2: L(d, [(px - 35, py), (px + 35, py)], w=5)
                    else: L(d, [(px, py - 35), (px, py + 35)], w=5)
        if ans: T(d, 800, 850, '全部平行 / All parallel', 50)
        out.append(fin(im))
    return out

def hering():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        if not ans:
            for k in range(36):
                a = k * math.pi / 36
                L(d, [(800 - 1200 * math.cos(a), 450 - 1200 * math.sin(a)), (800 + 1200 * math.cos(a), 450 + 1200 * math.sin(a))], fill=(40, 40, 40), w=3)
        L(d, [(620, 40), (620, 860)], fill=RED, w=10); L(d, [(980, 40), (980, 860)], fill=RED, w=10)
        if ans: T(d, 800, 450, 'まっすぐ / Straight', 56, (30, 30, 30))
        out.append(fin(im))
    return out

def contrast():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        for x in range(CW * S):
            v = int(30 + 200 * x / (CW * S)); d.line((x, 0, x, CH * S), fill=(v, v, v))
        g = (128, 128, 128)
        R(d, 260, 330, 500, 570, g); R(d, 1100, 330, 1340, 570, g)
        if ans:
            R(d, 500, 430, 1100, 470, g); T(d, 800, 760, '同じ灰色 / Same gray', 56, (230, 40, 40))
        out.append(fin(im))
    return out

def gradbar():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        if not ans:
            for x in range(CW * S):
                v = int(20 + 215 * x / (CW * S)); d.line((x, 0, x, CH * S), fill=(v, v, v))
        else:
            R(d, 0, 0, CW, CH, (200, 200, 200))
        R(d, 150, 400, 1450, 500, (128, 128, 128))
        T(d, 160, 360, '左 Left', 34, (240, 200, 60), anchor='lm'); T(d, 1440, 360, '右 Right', 34, (240, 200, 60) if not ans else (40, 40, 40), anchor='rm')
        if ans: T(d, 800, 700, 'ずっと同じ色 / One single color', 56)
        out.append(fin(im))
    return out

def kanizsa():
    out = []
    for ans in (0, 1):
        im, d = canvas((255, 255, 255))
        cx, cy, r = 800, 480, 300
        pts = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)]
        inv = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in (math.pi / 2, -math.pi / 6, 7 * math.pi / 6)]
        for i, (x, y) in enumerate(pts):
            C(d, x, y, 75, (0, 0, 0))
        d.polygon([(x * S, y * S) for x, y in pts], fill=(255, 255, 255))
        if not ans:
            d.polygon([(x * S, y * S) for x, y in inv], outline=(0, 0, 0), width=7 * S)
        else:
            d.polygon([(x * S, y * S) for x, y in inv], outline=(0, 0, 0), width=7 * S)
            d.polygon([(x * S, y * S) for x, y in pts], outline=RED, width=4 * S)
            T(d, 800, 860, '白い三角形は描かれていない / No white triangle is drawn', 40)
        out.append(fin(im))
    return out

def hermann(scint=False):
    out = []
    for ans in (0, 1):
        im, d = canvas((0, 0, 0) if not scint else (0, 0, 0))
        sq, gap = 110, 26
        n = 8
        x0 = (CW - (n * sq + (n - 1) * gap)) // 2; y0 = (CH - (6 * sq + 5 * gap)) // 2
        if scint:
            R(d, 0, 0, CW, CH, (0, 0, 0))
            for i in range(n + 1):
                x = x0 + i * (sq + gap) - gap
                R(d, x, 0, x + gap, CH, (128, 128, 128))
            for j in range(7):
                y = y0 + j * (sq + gap) - gap
                R(d, 0, y, CW, y + gap, (128, 128, 128))
            for i in range(n + 1):
                for j in range(7):
                    C(d, x0 + i * (sq + gap) - gap / 2, y0 + j * (sq + gap) - gap / 2, 17, (255, 255, 255))
        else:
            R(d, 0, 0, CW, CH, (255, 255, 255))
            for i in range(n):
                for j in range(6):
                    x = x0 + i * (sq + gap); y = y0 + j * (sq + gap)
                    R(d, x, y, x + sq, y + sq, (0, 0, 0))
        if ans:
            cx = x0 + 4 * (sq + gap) - gap / 2; cy = y0 + 3 * (sq + gap) - gap / 2
            C(d, cx, cy, 70, None, RED, 6)
            R(d, 300, CH - 110, 1300, CH - 30, (255, 255, 255))
            T(d, 800, CH - 70, ('黒い点は0個 / Zero black dots' if scint else '灰色の点は存在しない / No gray dots exist'), 44)
        out.append(fin(im))
    return out

def rubin():
    out = []
    for ans in (0, 1):
        im, d = canvas((0, 0, 0))
        # face profile (left), mirrored for right; vase is the white space between
        prof = [(0, 0), (60, 0), (70, 80), (55, 150), (90, 210), (70, 250), (100, 300), (75, 330), (85, 370), (60, 420), (40, 500), (40, 600), (110, 680), (120, 760), (0, 760)]
        def poly(side):
            pts = []
            for x, y in prof:
                X = 520 + x if side < 0 else 1080 - x
                pts.append((X * S, (70 + y) * S))
            pts += [((520 if side < 0 else 1080) * S - side * 0, 830 * S)]
            return pts
        d.rectangle((520 * S, 70 * S, 1080 * S, 830 * S), fill=(255, 255, 255))
        fc = (0, 0, 0) if not ans else (60, 110, 200)
        d.polygon(poly(-1) + [(0, 830 * S), (0, 70 * S)], fill=fc)
        d.polygon(poly(1) + [(CW * S, 830 * S), (CW * S, 70 * S)], fill=fc)
        d.rectangle((0, 0, 520 * S, CH * S), fill=fc); d.rectangle((1080 * S, 0, CW * S, CH * S), fill=fc)
        d.polygon(poly(-1) + [(520 * S, 830 * S)], fill=fc); d.polygon(poly(1) + [(1080 * S, 830 * S)], fill=fc)
        if ans:
            T(d, 260, 450, '顔 Face', 60, (255, 255, 255)); T(d, 1340, 450, '顔 Face', 60, (255, 255, 255)); T(d, 800, 470, '壺 Vase', 60, (215, 40, 40))
        out.append(fin(im))
    return out

def photo_qa(path, labels):
    src = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    out = []
    for ans in (0, 1):
        im = Image.new('RGB', (CW, CH), (255, 255, 255))
        s = min(CW / src.width, CH / src.height) * 0.95
        p = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
        im.paste(p, ((CW - p.width) // 2, (CH - p.height) // 2))
        if ans:
            d = ImageDraw.Draw(im)
            for (x, y, t, col) in labels:
                d.rounded_rectangle((x - 180, y - 40, x + 180, y + 40), 20, fill=col)
                d.text((x, y), t, font=ImageFont.truetype(FD + 'NotoSansCJK-Black.ttc', 40, index=0), fill=(255, 255, 255), anchor='mm')
        out.append(im)
    return out

def necker():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        def cube(ox, oy, s, shade=None):
            a = [(ox, oy), (ox + s, oy), (ox + s, oy + s), (ox, oy + s)]
            b = [(x + s * 0.45, y - s * 0.45) for x, y in a]
            if shade == 'front': d.polygon([(x * S, y * S) for x, y in a], fill=(150, 190, 240))
            if shade == 'back': d.polygon([(x * S, y * S) for x, y in b], fill=(240, 170, 140))
            for P in (a, b): L(d, P + [P[0]], w=7)
            for p, q in zip(a, b): L(d, [p, q], w=7)
        if not ans: cube(600, 300, 380)
        else:
            cube(220, 330, 320, 'front'); cube(970, 330, 320, 'back')
            T(d, 400, 800, '見方A', 46, (40, 90, 200)); T(d, 1150, 800, '見方B', 46, (215, 40, 40))
        out.append(fin(im))
    return out

def penrose():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        cx, cy, R0, w = 800, 500, 380, 95
        V = [(cx + R0 * math.cos(a), cy + R0 * math.sin(a)) for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)]
        cols = [(90, 140, 210), (150, 190, 240), (40, 80, 160)]
        def lerp(p, q, t): return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        def shrink(P, k):
            return [lerp(p, (cx, cy), k) for p in P]
        In1 = shrink(V, w / R0 * 1.0); In2 = shrink(V, w / R0 * 2.0)
        # three L-shaped bars (classic construction)
        for i in range(3):
            a, b, c = V[i], V[(i + 1) % 3], V[(i + 2) % 3]
            ia, ib = In1[i], In1[(i + 1) % 3]
            ja, jb, jc = In2[i], In2[(i + 1) % 3], In2[(i + 2) % 3]
            poly = [a, lerp(a, b, 0.0), b, ib, lerp(jb, jc, 0), ja]
            poly = [a, b, ib, jb, jc, lerp(ia, c, 0.0)]
            d.polygon([(x * S, y * S) for x, y in [a, b, ib, ja]], fill=cols[i], outline=(20, 20, 20), width=4 * S)
        if ans: T(d, 800, 860, '3次元では作れない形 / Impossible in 3D', 46)
        out.append(fin(im))
    return out

def jastrow():
    out = []
    def shape(cx, cy, col):
        r1, r2 = 520, 340; a0, a1 = math.radians(-125), math.radians(-55)
        pts = [(cx + r1 * math.cos(a0 + (a1 - a0) * t / 40), cy + r1 * math.sin(a0 + (a1 - a0) * t / 40)) for t in range(41)]
        pts += [(cx + r2 * math.cos(a1 - (a1 - a0) * t / 40), cy + r2 * math.sin(a1 - (a1 - a0) * t / 40)) for t in range(41)]
        return [(x * S, y * S) for x, y in pts], col
    for ans in (0, 1):
        im, d = canvas()
        if not ans:
            p, c = shape(800, 720, (230, 90, 90)); d.polygon(p, fill=c)
            p, c = shape(800, 920, (90, 120, 220)); d.polygon(p, fill=c)
            T(d, 1180, 340, 'A', 60, (60, 60, 60)); T(d, 1180, 560, 'B', 60, (60, 60, 60))
        else:
            p, c = shape(560, 820, (230, 90, 90)); d.polygon(p, fill=c)
            p, c = shape(1060, 820, (90, 120, 220)); d.polygon(p, fill=c)
            T(d, 800, 830, '同じ大きさ / Same size', 52)
        out.append(fin(im))
    return out

def poggendorff():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        k = 0.55
        def yat(x): return 120 + (x - 150) * k
        L(d, [(150, yat(150)), (650, yat(650))], fill=RED, w=8)
        tgt = yat(1450)
        for lab, dy in (('A', -110), ('B', 0), ('C', 110)):
            L(d, [(950, yat(950) + dy), (1450, tgt + dy)], fill=(30, 30, 30) if lab != 'B' or not ans else RED, w=8)
            T(d, 1500, tgt + dy, lab, 54, (60, 60, 60))
        if not ans: R(d, 650, 40, 950, 860, (120, 150, 200))
        else:
            R(d, 650, 40, 950, 860, (120, 150, 200, 80))
            im2 = im.copy(); dd = ImageDraw.Draw(im2); L(dd, [(150, yat(150)), (1450, tgt)], fill=RED, w=6); im = Image.blend(im, im2, 0.7); d = ImageDraw.Draw(im)
            T(d, 800, 860, '正解はB / The answer is B', 50, (255, 255, 255))
        out.append(fin(im))
    return out

def delboeuf():
    out = []
    for ans in (0, 1):
        im, d = canvas()
        C(d, 480, 450, 90, (20, 20, 20)); C(d, 1120, 450, 90, (20, 20, 20))
        if not ans:
            C(d, 480, 450, 110, None, (20, 20, 20), 6); C(d, 1120, 450, 230, None, (20, 20, 20), 6)
        else:
            L(d, [(390, 360), (1210, 360)], fill=RED, w=4); L(d, [(390, 540), (1210, 540)], fill=RED, w=4)
            T(d, 800, 760, '同じ大きさ / Same size', 52)
        out.append(fin(im))
    return out

def afterimage():
    im, d = canvas((0, 0, 0))
    C(d, 800, 450, 270, (0, 230, 230))
    C(d, 800, 450, 8, (0, 0, 0)); C(d, 800, 450, 6, (255, 255, 255))
    q = fin(im)
    im2, d2 = canvas((255, 255, 255)); C(d2, 800, 450, 6, (0, 0, 0))
    return [q, fin(im2)]
