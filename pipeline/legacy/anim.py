"""Animated explainer panels for each life hack. Panel is 840x780 (drawn at 2x)."""
import math
from PIL import Image, ImageDraw, ImageFont
PW, PH, S = 840, 780, 2
FD = '/usr/share/fonts/opentype/noto/'
def F(sz): return ImageFont.truetype(FD + 'NotoSansCJK-Black.ttc', int(sz * S), index=0)
INK = (45, 45, 60); ORANGE = (255, 140, 40); BLUE = (70, 150, 235); RED = (230, 70, 70); GREEN = (60, 175, 100)

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def seg(u, a, b): return ease((u - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))

class Pen:
    def __init__(self):
        self.im = Image.new('RGBA', (PW * S, PH * S), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def P(self, pts): return [(x * S, y * S) for x, y in pts]
    def rect(self, b, fill=None, outline=INK, w=5, r=0):
        b = [v * S for v in b]
        if r: self.d.rounded_rectangle(b, r * S, fill=fill, outline=outline, width=int(w * S))
        else: self.d.rectangle(b, fill=fill, outline=outline, width=int(w * S))
    def ell(self, b, fill=None, outline=INK, w=5):
        self.d.ellipse([v * S for v in b], fill=fill, outline=outline, width=int(w * S))
    def line(self, pts, fill=INK, w=5): self.d.line(self.P(pts), fill=fill, width=int(w * S), joint='curve')
    def poly(self, pts, fill=None, outline=INK, w=5):
        self.d.polygon(self.P(pts), fill=fill)
        if outline: self.d.line(self.P(pts + [pts[0]]), fill=outline, width=int(w * S), joint='curve')
    def text(self, xy, s, sz, fill=INK, anchor='mm', stroke=0, sf=(255, 255, 255)):
        self.d.text((xy[0] * S, xy[1] * S), s, font=F(sz), fill=fill, anchor=anchor, stroke_width=int(stroke * S), stroke_fill=sf)
    def arrow(self, a, b, fill=ORANGE, w=10, head=26):
        self.line([a, b], fill, w)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        p1 = (b[0] - head * math.cos(ang - 0.5), b[1] - head * math.sin(ang - 0.5))
        p2 = (b[0] - head * math.cos(ang + 0.5), b[1] - head * math.sin(ang + 0.5))
        self.poly([b, p1, p2], fill=fill, outline=None)
    def arc_arrow(self, c, r, a0, a1, fill=ORANGE, w=10):
        pts = [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * k / 24 for k in range(25)]]
        self.line(pts, fill, w)
        self.arrow(pts[-3], pts[-1], fill, w, 28)
    def badge(self, xy, s, col, sz=44):
        self.text(xy, s, sz, fill=col, stroke=10)
    def out(self): return self.im.resize((PW, PH), Image.LANCZOS)

# ---------------------------------------------------------------- 1 jar
def jar(u):
    p = Pen()
    lift = seg(u, 0.78, 0.9); tilt = lift * 18
    # jar
    p.rect((290, 360, 550, 680), fill=(205, 232, 245), r=40)
    p.rect((320, 470, 520, 620), fill=(240, 120, 70), outline=None, r=20)     # jam
    p.text((420, 545), 'JAM', 40, fill=(255, 255, 255))
    # lid
    ly = 360 - 46 - lift * 90
    lx = 420 + lift * 40
    band = seg(u, 0.12, 0.35)
    rot = (u - 0.4) * 40 if u > 0.4 else 0
    lid = Pen()
    lid.rect((270, 0, 570, 70), fill=RED, r=12)
    for k in range(9):
        x = 290 + ((k * 32 + rot * 30) % 270)
        lid.line([(x, 8), (x, 62)], fill=(180, 40, 40), w=4)
    if band > 0:
        lid.rect((270, 22, 270 + 300 * band, 50), fill=(210, 170, 110), outline=INK, w=3)
    li = lid.out().crop((0, 0, PW, 80)).rotate(tilt, resample=Image.BICUBIC, expand=True)
    p.im.alpha_composite(li.resize((li.width * S, li.height * S)), (int((lx - li.width / 2) * S), int(ly * S)))
    if 0.4 < u < 0.8:
        p.arc_arrow((420, ly + 35), 210, 200, 200 + 120 * seg(u, 0.4, 0.6))
        p.text((690, 200), 'ひねる！', 46, fill=ORANGE, stroke=8)
    if 0.12 < u < 0.4:
        p.text((420, 180), '輪ゴムを巻く', 50, fill=INK, stroke=8)
    if lift > 0.5: p.badge((420, 120), 'パカッ！開いた！', GREEN, 56)
    return p.out()

# ---------------------------------------------------------------- 2 egg
def egg(u):
    p = Pen()
    p.poly([(190, 500), (650, 500), (600, 700), (240, 700)], fill=(225, 240, 250))
    p.rect((200, 540, 640, 560), fill=(150, 205, 245), outline=None)
    p.poly([(210, 545), (630, 545), (598, 690), (242, 690)], fill=(150, 205, 245), outline=None)
    if u > 0.3:
        for k in range(4):   # ice cubes
            x = 260 + k * 90; p.rect((x, 560, x + 50, 610), fill=(235, 250, 255), outline=(120, 170, 210), w=3, r=8)
    drop = seg(u, 0.15, 0.32)
    ey = lerp(160, 520, drop); ex = 420
    gap = seg(u, 0.45, 0.7) * 16
    open_ = seg(u, 0.78, 0.92)
    w, h = 110, 145
    if open_ > 0:
        # white peeled egg + shell halves moving apart
        p.ell((ex - w + 10, ey - h + 10, ex + w - 10, ey + h - 10), fill=(255, 255, 255))
        p.d.pieslice([(ex - w - 120 * open_) * S, (ey - h) * S, (ex + w - 120 * open_) * S, (ey + h) * S], 90, 270, fill=(235, 200, 150), outline=INK, width=8)
        p.d.pieslice([(ex - w + 120 * open_) * S, (ey - h) * S, (ex + w + 120 * open_) * S, (ey + h) * S], 270, 90, fill=(235, 200, 150), outline=INK, width=8)
        p.badge((420, 130), 'つるんとむける！', GREEN, 56)
    else:
        p.ell((ex - w, ey - h, ex + w, ey + h), fill=(240, 205, 160))
        if gap > 0.5:
            p.ell((ex - w + gap, ey - h + gap, ex + w - gap, ey + h - gap), fill=(255, 255, 255), outline=(200, 200, 200), w=3)
            p.text((620, 300), 'すき間が\nできる', 40, fill=BLUE, stroke=8)
    if 0.3 < u < 0.78: p.text((420, 100), '急に冷やす', 52, fill=BLUE, stroke=8)
    return p.out()

# ---------------------------------------------------------------- 3 arch drying
def arch(u):
    p = Pen()
    p.line([(80, 170), (760, 170)], fill=(120, 120, 130), w=12)
    xs = [130 + k * 72.5 for k in range(9)]
    lens = [430, 360, 290, 230, 200, 230, 290, 360, 430]
    cols = [(120, 170, 230), (250, 190, 90), (240, 120, 120), (120, 200, 150), (200, 160, 230), (120, 200, 150), (240, 120, 120), (250, 190, 90), (120, 170, 230)]
    for k, (x, L, c) in enumerate(zip(xs, lens, cols)):
        a = seg(u, 0.03 * k, 0.03 * k + 0.12)
        if a <= 0: continue
        p.line([(x, 170), (x, 195)], fill=(90, 90, 100), w=5)
        p.rect((x - 28, 195, x + 28, 195 + L * a), fill=c, w=4, r=6)
    if u > 0.42:
        for k in range(5):
            ph = ((u - 0.42) * 2.2 + k / 5) % 1
            y = lerp(720, 420, ph); x = 420 + 70 * math.sin(ph * 6 + k)
            p.arrow((x, y + 60), (x, y), fill=(120, 190, 255), w=8, head=22)
        p.text((420, 700), '風が通る！', 52, fill=BLUE, stroke=8)
    if u < 0.42:
        p.text((650, 90), '長い→外側', 40, fill=INK, stroke=8)
        p.text((230, 90), '短い→内側', 40, fill=INK, stroke=8)
    if u > 0.8: p.badge((420, 90), '早く乾く！', GREEN, 56)
    return p.out()

# ---------------------------------------------------------------- 4 microwave donut
def donut(u):
    p = Pen()
    p.ell((130, 120, 710, 700), fill=(245, 245, 250), w=6)
    p.ell((200, 190, 640, 630), fill=None, outline=(200, 200, 210), w=4)
    move = seg(u, 0.3, 0.55)
    heat = seg(u, 0.55, 0.9)
    n = 8; rot = (u * 90) if u > 0.55 else 0
    for k in range(n):
        a0 = math.radians(k * 360 / n)
        cx0 = 420 + 60 * math.cos(a0 * 1.7); cy0 = 410 + 60 * math.sin(a0 * 1.3)
        a1 = math.radians(k * 360 / n + rot)
        cx1 = 420 + 190 * math.cos(a1); cy1 = 410 + 190 * math.sin(a1)
        cx, cy = lerp(cx0, cx1, move), lerp(cy0, cy1, move)
        col = mix((120, 170, 240), (255, 150, 60), heat)
        p.rect((cx - 38, cy - 30, cx + 38, cy + 30), fill=col, w=4, r=14)
    if u < 0.3:
        p.badge((420, 410), '真ん中が冷たい…', BLUE, 44)
    elif u < 0.55:
        p.text((420, 410), 'まん中をあける', 42, fill=ORANGE, stroke=8)
    if heat > 0.2:
        for k in range(6):
            a = math.radians(k * 60 + u * 200); r = 300
            x, y = 420 + r * math.cos(a), 410 + r * math.sin(a)
            p.line([(x, y), (x + 10 * math.cos(a), y + 10 * math.sin(a) - 20)], fill=(255, 150, 60), w=6)
    if u > 0.8: p.badge((420, 410), 'ムラなく温まる！', GREEN, 50)
    return p.out()

# ---------------------------------------------------------------- 5 metal tray thaw
def tray(u):
    p = Pen()
    p.poly([(120, 560), (720, 560), (690, 620), (150, 620)], fill=(190, 195, 205))
    p.line([(130, 575), (710, 575)], fill=(235, 235, 240), w=4)
    thaw = seg(u, 0.4, 0.85)
    col = mix((220, 235, 250), (230, 110, 110), thaw)
    p.rect((260, 410, 580, 560), fill=col, r=30)
    if thaw < 0.6:
        for k in range(10):
            x = 280 + k * 30; p.line([(x, 420), (x + 12, 440)], fill=(255, 255, 255), w=4)
    if u > 0.3:
        for k in range(6):
            ph = ((u - 0.3) * 1.6 + k / 6) % 1
            x = 160 + k * 100
            p.arrow((x, 700 - 60 * ph), (x, 640 - 60 * ph), fill=(255, 150, 60), w=8, head=20)
        p.text((420, 720), '金属が熱をどんどん伝える', 40, fill=ORANGE, stroke=8)
    p.text((420, 200), 'アルミ・金属のトレー', 46, fill=INK, stroke=8)
    if u > 0.85: p.badge((420, 300), '早く解ける！', GREEN, 56)
    return p.out()

# ---------------------------------------------------------------- 6 sticky note
def sticky(u):
    p = Pen()
    p.line([(420, 140), (420, 700)], fill=(210, 210, 215), w=4)
    # left: peel from bottom -> curls
    a = seg(u, 0.1, 0.35)
    p.rect((80, 260, 360, 300), fill=(255, 230, 120), w=4)
    if a < 1:
        p.poly([(80, 300), (360, 300), (360, lerp(560, 330, a)), (80, lerp(560, 330, a))], fill=(255, 225, 90))
    else:
        p.rect((100, 380, 340, 600), fill=(255, 225, 90), w=4)
        p.d.arc([(100 * S), (560 * S), (340 * S), (650 * S)], 180, 360, fill=INK, width=8)
        p.poly([(100, 600), (340, 600), (340, 560), (100, 560)], fill=(240, 205, 70))
    p.arrow((380, 600), (380, 380), fill=RED, w=8, head=20)
    p.badge((220, 680), '× 丸まる', RED, 48)
    # right: peel sideways -> flat
    b = seg(u, 0.45, 0.7)
    p.rect((480, 260, 760, 300), fill=(255, 230, 120), w=4)
    x0 = lerp(480, 520, b); x1 = lerp(760, 800, b)
    p.rect((x0 + 20 * b, 300 + 80 * b, x1 - 40 * b, 560 + 40 * b), fill=(255, 225, 90), w=4)
    p.arrow((500, 640), (740, 640), fill=GREEN, w=8, head=20)
    if u > 0.7: p.badge((620, 700), '〇 ピタッ', GREEN, 48)
    return p.out()

# ---------------------------------------------------------------- 7 tape tab
def tape(u):
    p = Pen()
    p.ell((230, 230, 610, 610), fill=(215, 175, 115), w=6)
    p.ell((340, 340, 500, 500), fill=(250, 244, 232), w=5)
    fold = seg(u, 0.4, 0.6)
    p.line([(560, 300), (600, 270)], fill=(180, 140, 85), w=6)
    if fold > 0:
        p.poly([(585, 285), (585 + 55 * fold, 285 - 60 * fold), (630, 300)], fill=(240, 205, 140))
    if u < 0.4:
        p.badge((420, 150), '端はどこ…？', RED, 52)
        p.text((640, 330), '?', 80, fill=RED, stroke=8)
    if fold > 0.9:
        p.arrow((720, 160), (650, 245), fill=GREEN, w=10)
        p.badge((420, 700), 'すぐつまめる！', GREEN, 56)
    if 0.4 <= u < 0.75: p.text((420, 700), '端を少し折る', 50, fill=ORANGE, stroke=8)
    return p.out()

# ---------------------------------------------------------------- 8 shoe + newspaper
def shoe(u):
    p = Pen()
    p.poly([(120, 560), (160, 380), (330, 380), (380, 470), (650, 520), (720, 600), (700, 640), (130, 640)], fill=(120, 95, 80))
    p.ell((180, 365, 330, 405), fill=(70, 55, 45), w=4)
    dry = seg(u, 0.5, 0.85)
    if dry < 1:
        for k, (x, y) in enumerate([(200, 300), (300, 260), (480, 430), (600, 470), (250, 450), (400, 330)]):
            r = 20 * (1 - dry)
            if r > 1: p.poly([(x, y - r * 1.6), (x + r, y), (x - r, y)], fill=BLUE, outline=None); p.ell((x - r, y - r * 0.6, x + r, y + r * 1.1), fill=BLUE, outline=None)
    ball = seg(u, 0.2, 0.45)
    bx, by = lerp(650, 255, ball), lerp(180, 360, ball)
    if u > 0.12:
        p.ell((bx - 70, by - 60, bx + 70, by + 60), fill=(225, 225, 220), w=4)
        for k in range(5): p.line([(bx - 50 + k * 22, by - 30), (bx - 40 + k * 22, by + 30)], fill=(150, 150, 150), w=3)
    if 0.12 < u < 0.5: p.text((600, 120), '丸めた新聞紙', 46, fill=INK, stroke=8)
    if 0.5 < u < 0.85: p.text((420, 720), '水分を吸い取る', 48, fill=BLUE, stroke=8)
    if u > 0.85: p.badge((420, 720), 'カラッと乾く！', GREEN, 56)
    return p.out()

# ---------------------------------------------------------------- 9 airplane mode
def phone(u):
    p = Pen()
    p.rect((260, 90, 580, 700), fill=(40, 45, 60), r=40)
    p.rect((280, 140, 560, 650), fill=(245, 248, 255), outline=None, r=18)
    on = u > 0.3
    # toggle
    p.text((330, 200), '✈', 50, fill=INK)
    p.text((385, 200), '機内モード', 34, fill=INK, anchor='lm')
    tx = 500
    p.rect((tx - 40, 180, tx + 40, 220), fill=GREEN if on else (200, 200, 210), outline=None, r=20)
    kx = tx + (20 if on else -20)
    p.ell((kx - 17, 183, kx + 17, 217), fill=(255, 255, 255), outline=None)
    # signal bars fade
    for k in range(4):
        h = 14 + k * 10; x = 300 + k * 16
        p.rect((x, 270 - h, x + 10, 270), fill=(180, 180, 190) if on else INK, outline=None)
    # battery
    rate = 0.35 * u if u < 0.3 else 0.105 + 0.85 * (u - 0.3) / 0.7 * 1.0
    lvl = min(0.95, rate)
    p.rect((330, 330, 500, 560), fill=None, w=8, r=16); p.rect((385, 310, 445, 330), fill=INK, outline=None)
    hh = 210 * lvl
    p.rect((345, 545 - hh, 485, 545), fill=GREEN, outline=None, r=8)
    p.text((415, 600), f'{int(lvl * 100)}%', 40, fill=INK)
    if on: p.badge((420, 750 - 30), '少し早く充電！', GREEN, 48)
    return p.out()

# ---------------------------------------------------------------- 10 reopen tab
def tabs(u):
    p = Pen()
    p.rect((80, 160, 760, 560), fill=(255, 255, 255), r=16)
    p.rect((80, 160, 760, 220), fill=(225, 228, 235), outline=None, r=16)
    gone = seg(u, 0.15, 0.25); back = seg(u, 0.65, 0.78)
    names = ['ニュース', 'レシピ', '地図']
    for k, nm in enumerate(names):
        x = 100 + k * 210
        if k == 1:
            vis = 1 - gone + back
            if vis <= 0.01: continue
            sc = min(1, vis)
            p.rect((x, 172, x + 190 * sc, 220), fill=(255, 255, 255) if back > 0 else (245, 247, 250), w=3, r=10)
            if sc > 0.7: p.text((x + 85, 196), nm, 28, fill=INK)
        else:
            p.rect((x, 172, x + 190, 220), fill=(245, 247, 250), w=3, r=10); p.text((x + 85, 196), nm, 28, fill=INK)
    if u < 0.25: p.badge((420, 390), 'うっかり閉じた！', RED, 52)
    keys = ['Ctrl', 'Shift', 'T']
    for k, kk in enumerate(keys):
        pr = seg(u, 0.35 + k * 0.08, 0.4 + k * 0.08)
        if pr <= 0: continue
        x = 190 + k * 230; y = 650 + 10 * pr
        p.rect((x - 90, y - 50, x + 90, y + 50), fill=mix((240, 240, 245), (255, 200, 120), pr), w=5, r=16)
        p.text((x, y), kk, 46, fill=INK)
        if k < 2: p.text((x + 115, 650), '＋', 44, fill=INK)
    if back > 0.5: p.badge((420, 390), '元に戻った！', GREEN, 56)
    return p.out()

FUNCS = [jar, egg, arch, donut, tray, sticky, tape, shoe, phone, tabs]
