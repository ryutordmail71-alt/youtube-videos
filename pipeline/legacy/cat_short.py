import math, random, subprocess, wave, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, S = 1080, 1920, 2          # output size, supersample factor
FPS, DUR = 30, 8.0
NF = int(FPS * DUR)
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'

def s(v): return int(round(v * S))
def box(x0, y0, x1, y1): return (s(x0), s(y0), s(x1), s(y1))
def pts(lst): return [(s(x), s(y)) for x, y in lst]

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))

# palette
OUT = (92, 52, 28)
ORANGE = (243, 166, 88)
DARK = (214, 124, 52)
WHITE = (255, 247, 236)
PINK = (247, 160, 170)
NOSE = (236, 118, 132)
SKIN = (246, 205, 170)
SKIN_OUT = (190, 128, 96)
SLEEVE = (70, 92, 140)
SLEEVE_D = (52, 70, 112)

# ---------------- background ----------------
def make_bg():
    bg = Image.new('RGB', (W * S, H * S))
    a = np.linspace(0, 1, H * S)[:, None]
    top, bot = np.array([250, 238, 220]), np.array([240, 220, 192])
    col = (top * (1 - a) + bot * a).astype(np.uint8)
    arr = np.repeat(col[:, None, :], W * S, axis=1)
    bg = Image.fromarray(arr.reshape(H * S, W * S, 3))
    d = ImageDraw.Draw(bg, 'RGBA')
    # window
    d.rounded_rectangle(box(70, 470, 440, 960), radius=s(18), fill=(255, 255, 255))
    for i in range(4):
        y0 = 495 + i * 112
        d.rectangle(box(95, y0, 415, y0 + 100), fill=mix((178, 220, 245), (222, 240, 250), i / 3))
    d.rectangle(box(250, 490, 262, 940), fill=(255, 255, 255))
    d.rectangle(box(95, 600, 415, 607), fill=(255, 255, 255))
    d.rectangle(box(95, 712, 415, 719), fill=(255, 255, 255))
    d.rectangle(box(95, 824, 415, 831), fill=(255, 255, 255))
    d.rectangle(box(50, 955, 460, 985), fill=(238, 228, 214))
    # sunlight beams
    d.polygon(pts([(440, 480), (440, 960), (1080, 1700), (1080, 1100)]), fill=(255, 245, 210, 45))
    # floor
    d.rectangle(box(0, 1380, 1080, 1920), fill=(214, 166, 118))
    for i, y in enumerate(range(1380, 1920, 70)):
        d.line(pts([(0, y), (1080, y)]), fill=(194, 146, 100), width=s(3))
        off = (i * 260) % 520
        for x in range(off, 1080, 520):
            d.line(pts([(x, y), (x, y + 70)]), fill=(194, 146, 100), width=s(3))
    d.rectangle(box(0, 1370, 1080, 1386), fill=(236, 222, 200))
    # rug
    d.ellipse(box(150, 1420, 930, 1700), fill=(226, 190, 186))
    d.ellipse(box(180, 1440, 900, 1680), fill=(238, 208, 202))
    # plant
    d.polygon(pts([(880, 1250), (1010, 1250), (990, 1390), (900, 1390)]), fill=(206, 120, 86))
    d.rectangle(box(870, 1235, 1020, 1262), fill=(190, 104, 72))
    for ang, ln in [(-60, 230), (-80, 300), (-100, 280), (-120, 220), (-40, 180), (-140, 170)]:
        r = math.radians(ang)
        cx, cy = 945 + math.cos(r) * ln * 0.6, 1235 + math.sin(r) * ln * 0.6
        bx = (cx - 45, cy - 80, cx + 45, cy + 80)
        leaf = Image.new('RGBA', (s(120), s(200)), (0, 0, 0, 0))
        ImageDraw.Draw(leaf).ellipse(box(15, 20, 105, 180), fill=(96, 158, 104))
        ImageDraw.Draw(leaf).line(pts([(60, 30), (60, 170)]), fill=(76, 132, 86), width=s(4))
        leaf = leaf.rotate(-(ang + 90), resample=Image.BICUBIC, expand=True)
        bg.paste(leaf, (s(cx) - leaf.width // 2, s(cy) - leaf.height // 2), leaf)
    # picture frame
    d.rounded_rectangle(box(640, 520, 900, 720), radius=s(8), fill=(176, 130, 92))
    d.rectangle(box(660, 540, 880, 700), fill=(250, 232, 200))
    d.ellipse(box(720, 570, 820, 670), fill=(246, 190, 120))
    # cat shadow
    d.ellipse(box(320, 1480, 800, 1590), fill=(180, 130, 130, 110))
    return bg

def caption(bg):
    d = ImageDraw.Draw(bg, 'RGBA')
    f = ImageFont.truetype(FONT, s(76), index=0)
    txt = '在宅勤務が終わらない理由'
    tw = d.textlength(txt, font=f) / S
    x0 = (W - tw) / 2
    d.rounded_rectangle(box(x0 - 40, 228, x0 + tw + 40, 360), radius=s(30), fill=(0, 0, 0, 40))
    d.rounded_rectangle(box(x0 - 44, 216, x0 + tw + 36, 348), radius=s(30), fill=(255, 255, 255))
    d.text((s(x0 - 4), s(232)), txt, font=f, fill=(60, 40, 30))
    f2 = ImageFont.truetype(FONT, s(40), index=0)
    sub = '🐾 うちの猫、甘えすぎ問題'
    sub = 'うちの猫、甘えすぎ問題'
    tw2 = d.textlength(sub, font=f2) / S
    d.text((s((W - tw2) / 2), s(380)), sub, font=f2, fill=(120, 80, 50),
           stroke_width=s(6), stroke_fill=(255, 255, 255))

# ---------------- cat ----------------
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])

def draw_tail(d, sway):
    P = [(690, 1500), (900, 1540), (940 + sway * 0.6, 1360), (850 + sway * 1.4, 1215)]
    N = 60
    cs = [bez(*P, i / (N - 1)) for i in range(N)]
    rad = [lerp(36, 27, i / (N - 1)) for i in range(N)]
    for (x, y), r in zip(cs, rad):
        d.ellipse(box(x - r - 6, y - r - 6, x + r + 6, y + r + 6), fill=OUT)
    for i, ((x, y), r) in enumerate(zip(cs, rad)):
        k = i / (N - 1)
        c = DARK if (0.35 < k < 0.45 or 0.6 < k < 0.7 or k > 0.85) else ORANGE
        d.ellipse(box(x - r, y - r, x + r, y + r), fill=c)

def draw_body(d, breath):
    by = 1530
    def e(x0, y0, x1, y1, fill, ow=6):
        # scale vertically around bottom for breathing
        y0 = by - (by - y0) * breath; y1 = by - (by - y1) * breath
        if ow: d.ellipse(box(x0 - ow, y0 - ow, x1 + ow, y1 + ow), fill=OUT)
        d.ellipse(box(x0, y0, x1, y1), fill=fill)
    # outlines first
    for b in [(330, 1050, 750, 1530), (295, 1340, 470, 1545), (610, 1340, 785, 1545)]:
        e(*b, OUT, ow=6)
    for b in [(330, 1050, 750, 1530), (295, 1340, 470, 1545), (610, 1340, 785, 1545)]:
        e(*b, ORANGE, ow=0)
    # stripes on body sides
    for i, yy in enumerate([1170, 1250, 1330]):
        y = by - (by - yy) * breath
        d.arc(box(340, y - 40, 470, y + 60), 160, 230, fill=DARK, width=s(16))
        d.arc(box(610, y - 40, 740, y + 60), -50, 20, fill=DARK, width=s(16))
    e(310, 1400, 380, 1440, DARK, ow=0)
    e(700, 1400, 770, 1440, DARK, ow=0)
    # chest
    e(430, 1080, 650, 1400, WHITE, ow=0)
    # front paws
    for x0 in (432, 550):
        e(x0, 1462, x0 + 98, 1548, WHITE, ow=6)
        d.line(pts([(x0 + 33, 1520), (x0 + 33, 1545)]), fill=OUT, width=s(4))
        d.line(pts([(x0 + 65, 1520), (x0 + 65, 1545)]), fill=OUT, width=s(4))

HC = 700  # head canvas (unscaled)
def draw_head(eye_open, happy, look, blush):
    im = Image.new('RGBA', (s(HC), s(HC)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ears = [[(185, 275), (222, 118), (305, 215)], [(515, 275), (478, 118), (395, 215)]]
    inner = [[(207, 252), (228, 160), (285, 222)], [(493, 252), (472, 160), (415, 222)]]
    shapes = [(140, 200, 560, 520), (118, 320, 268, 505), (432, 320, 582, 505)]
    ow = 7
    for ear in ears:
        d.polygon(pts(ear), fill=OUT, outline=OUT, width=s(ow * 2))
    for b in shapes:
        d.ellipse(box(b[0] - ow, b[1] - ow, b[2] + ow, b[3] + ow), fill=OUT)
    for ear, inn in zip(ears, inner):
        d.polygon(pts(ear), fill=ORANGE)
        d.polygon(pts(inn), fill=PINK)
    for b in shapes:
        d.ellipse(box(*b), fill=ORANGE)
    # forehead stripes
    for x, h in [(318, 50), (350, 66), (382, 50)]:
        d.polygon(pts([(x - 12, 206), (x + 12, 206), (x, 206 + h)]), fill=DARK)
    d.polygon(pts([(140, 330), (195, 345), (142, 360)]), fill=DARK)
    d.polygon(pts([(560, 330), (505, 345), (558, 360)]), fill=DARK)
    # muzzle
    d.ellipse(box(282, 382, 358, 458), fill=WHITE)
    d.ellipse(box(342, 382, 418, 458), fill=WHITE)
    # blush
    if blush > 0.01:
        bc = mix(ORANGE, (250, 140, 140), blush)
        d.ellipse(box(195, 395, 262, 432), fill=bc)
        d.ellipse(box(438, 395, 505, 432), fill=bc)
    # eyes
    for ex in (262, 438):
        ex += look
        ey = 335
        if happy > 0.5:
            d.line(pts([(ex - 36, ey + 14), (ex, ey - 12), (ex + 36, ey + 14)]), fill=OUT, width=s(10), joint='curve')
        elif eye_open < 0.15:
            d.arc(box(ex - 36, ey - 30, ex + 36, ey + 14), 20, 160, fill=OUT, width=s(9))
        else:
            ry = 46 * eye_open
            d.ellipse(box(ex - 40, ey - ry, ex + 40, ey + ry), fill=(48, 30, 20))
            d.ellipse(box(ex - 33, ey - ry * 0.85, ex + 33, ey + ry * 0.85), fill=(70, 120, 60))
            d.ellipse(box(ex - 24, ey - ry * 0.75, ex + 24, ey + ry * 0.75), fill=(30, 20, 14))
            if eye_open > 0.4:
                d.ellipse(box(ex - 20 + look * .3, ey - ry * 0.6, ex + 2 + look * .3, ey - ry * 0.6 + 22), fill=(255, 255, 255))
                d.ellipse(box(ex + 8, ey + ry * 0.2, ex + 18, ey + ry * 0.2 + 10), fill=(255, 255, 255))
    # nose & mouth
    d.polygon(pts([(334, 384), (366, 384), (350, 402)]), fill=NOSE)
    d.line(pts([(350, 400), (350, 414)]), fill=OUT, width=s(5))
    d.arc(box(318, 396, 352, 428), 10, 170, fill=OUT, width=s(5))
    d.arc(box(348, 396, 382, 428), 10, 170, fill=OUT, width=s(5))
    # whiskers
    for (a, b) in [((240, 405), (100, 385)), ((240, 418), (95, 420)), ((242, 431), (105, 458))]:
        d.line(pts([a, b]), fill=OUT, width=s(3))
        d.line(pts([(700 - a[0], a[1]), (700 - b[0], b[1])]), fill=OUT, width=s(3))
    return im

PIV_L = (350, 505)      # pivot inside head canvas
PIV_S = (540, 1112)     # pivot in scene

def paste_rot(frame, layer, piv_local, piv_scene, ang):
    # rotate layer around piv_local by ang (deg, ccw), placing piv at piv_scene
    lw, lh = layer.size
    cx, cy = s(piv_local[0]), s(piv_local[1])
    # pad so pivot is center
    pw = 2 * max(cx, lw - cx); ph = 2 * max(cy, lh - cy)
    pad = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    pad.paste(layer, (pw // 2 - cx, ph // 2 - cy))
    r = pad.rotate(ang, resample=Image.BICUBIC, expand=False)
    frame.paste(r, (s(piv_scene[0]) - pw // 2, s(piv_scene[1]) - ph // 2), r)

# ---------------- hand ----------------
def make_hand():
    im = Image.new('RGBA', (s(420), s(320)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    parts = [(150, 90, 340, 230), (55, 100, 200, 142), (40, 136, 200, 176),
             (52, 172, 200, 210), (82, 204, 200, 238), (200, 58, 300, 112)]
    for b in parts:
        d.ellipse(box(b[0] - 6, b[1] - 6, b[2] + 6, b[3] + 6), fill=SKIN_OUT)
    for b in parts:
        d.ellipse(box(*b), fill=SKIN)
    for y in (140, 174, 208):
        d.line(pts([(150, y), (196, y)]), fill=SKIN_OUT, width=s(3))
    d.rectangle(box(320, 110, 420, 212), fill=SKIN)
    d.line(pts([(320, 104), (420, 104)]), fill=SKIN_OUT, width=s(6))
    d.line(pts([(320, 217), (420, 217)]), fill=SKIN_OUT, width=s(6))
    return im

HAND = make_hand()
HAND_PIV = (230, 160)

def draw_arm(frame, hx, hy, dx, dy):
    d = ImageDraw.Draw(frame)
    nx, ny = -dy, dx
    w0 = (hx + dx * 170, hy + dy * 170)
    far = (hx + dx * 1500, hy + dy * 1500)
    def quad(a, b, wa, wb, c, ow=6):
        p = [(a[0] + nx * (wa + ow), a[1] + ny * (wa + ow)), (b[0] + nx * (wb + ow), b[1] + ny * (wb + ow)),
             (b[0] - nx * (wb + ow), b[1] - ny * (wb + ow)), (a[0] - nx * (wa + ow), a[1] - ny * (wa + ow))]
        d.polygon(pts(p), fill=c)
    quad(w0, far, 92, 110, (40, 52, 84))
    quad(w0, far, 86, 104, SLEEVE, ow=0)
    c1 = w0; c2 = (w0[0] + dx * 50, w0[1] + dy * 50)
    quad(c1, c2, 86, 88, SLEEVE_D, ow=0)
    for k in range(3, 14):
        a = (w0[0] + dx * k * 50, w0[1] + dy * k * 50)
        b = (a[0] + dx * 10, a[1] + dy * 10)
        quad(a, b, 96, 96, (62, 82, 128), ow=0)
    th = math.degrees(math.atan2(-dy, -dx))
    paste_rot(frame, HAND, HAND_PIV, (hx, hy), 180 - th)

# ---------------- effects ----------------
def heart_patch(size, alpha):
    n = int(size * 1.3)
    im = Image.new('RGBA', (s(n), s(n)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        p.append((n / 2 + x * size / 36, n / 2 - y * size / 36))
    d.polygon(pts(p), fill=(255, 255, 255))
    p2 = [(n / 2 + (x - n / 2) * 0.82, n / 2 + (y - n / 2) * 0.82) for x, y in p]
    d.polygon(pts(p2), fill=(255, 92, 128))
    d.ellipse(box(n * 0.3, n * 0.3, n * 0.42, n * 0.4), fill=(255, 190, 205))
    a = im.getchannel('A').point(lambda v: int(v * alpha))
    im.putalpha(a)
    return im

def text_patch(txt, size, color, alpha, bubble=False):
    f = ImageFont.truetype(FONT, s(size), index=0)
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), txt, font=f, stroke_width=s(8))
    pad = s(40) if bubble else s(10)
    im = Image.new('RGBA', (r - l + 2 * pad, b - t + 2 * pad + (s(40) if bubble else 0)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if bubble:
        bw, bh = r - l + 2 * pad, b - t + 2 * pad
        d.rounded_rectangle((s(3), s(3), bw - s(3), bh - s(3)), radius=s(40), fill=(255, 255, 255), outline=OUT, width=s(5))
        d.polygon([(bw * 0.62, bh - s(6)), (bw * 0.80, bh - s(6)), (bw * 0.82, bh + s(34))], fill=(255, 255, 255))
        d.line([(bw * 0.62, bh - s(3)), (bw * 0.82, bh + s(34)), (bw * 0.80, bh - s(3))], fill=OUT, width=s(5))
        d.text((pad - l, pad - t), txt, font=f, fill=color)
    else:
        d.text((pad - l, pad - t), txt, font=f, fill=color, stroke_width=s(8), stroke_fill=(255, 255, 255))
    im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    return im

def paste_center(frame, patch, cx, cy, scale=1.0, ang=0):
    if scale != 1.0:
        patch = patch.resize((max(1, int(patch.width * scale)), max(1, int(patch.height * scale))), Image.BICUBIC)
    if ang:
        patch = patch.rotate(ang, resample=Image.BICUBIC, expand=True)
    frame.paste(patch, (s(cx) - patch.width // 2, s(cy) - patch.height // 2), patch)

random.seed(7)
HEARTS = []
t0 = 2.4
while t0 < 5.7:
    HEARTS.append(dict(t=t0, x=random.uniform(560, 760), size=random.uniform(42, 66),
                       ph=random.uniform(0, 6.28), drift=random.uniform(-40, 60)))
    t0 += random.uniform(0.3, 0.45)

# ---------------- timeline ----------------
TARGET = (745, 845)
DIR = (0.78, -0.62)
nrm = math.hypot(*DIR); DIR = (DIR[0] / nrm, DIR[1] / nrm)

def state(t):
    st = {}
    # hand offset along arm direction (0 = resting on head)
    if t < 1.0: off = 1000
    elif t < 2.0: off = lerp(1000, 0, 1 - (1 - ease(t - 1.0)) ** 2)
    elif t < 6.0: off = 0
    elif t < 6.9: off = lerp(0, 1000, ease((t - 6.0) / 0.9) ** 1.5)
    else: off = 1000
    rub = ease((t - 2.0) / 0.4) * (1 - ease((t - 5.8) / 0.4))
    osc = math.sin(2 * math.pi * 1.1 * (t - 2.0))
    st['head_ang'] = -rub * (14 + 9 * osc)
    st['head_dx'] = rub * (14 + 8 * osc)
    st['hand'] = (TARGET[0] + DIR[0] * off + rub * (10 + 12 * osc),
                  TARGET[1] + DIR[1] * off + rub * (14 + 10 * osc))
    st['happy'] = 1.0 if 2.3 <= t < 6.0 else 0.0
    st['blush'] = ease((t - 2.3) / 0.5) * (1 - ease((t - 6.0) / 0.6))
    # eyes
    eo = 1.0
    for bt, bd in [(0.45, 0.28), (7.15, 0.7)]:
        if bt <= t < bt + bd:
            k = (t - bt) / bd
            eo = 1 - 0.95 * math.sin(math.pi * k)
    st['eye'] = eo
    look = 0
    if 1.0 <= t < 2.3: look = 12 * ease((t - 1.0) / 0.5)
    elif 6.0 <= t < 7.0: look = 12 * (1 - ease((t - 6.5) / 0.4))
    st['look'] = look
    st['tail'] = 40 * math.sin(2 * math.pi * (0.5 + 0.6 * rub) * t) * (0.5 + 0.5 * rub)
    st['tail'] = 40 * math.sin(2 * math.pi * t * 0.5 / 1) if rub < 0.01 else st['tail']
    st['breath'] = 1 + 0.008 * math.sin(2 * math.pi * t / 1.6) * (1 + rub)
    return st

def render(bg, i):
    t = i / FPS
    st = state(t)
    fr = bg.copy()
    d = ImageDraw.Draw(fr)
    draw_tail(d, st['tail'])
    draw_body(d, st['breath'])
    head = draw_head(st['eye'], st['happy'], st['look'], st['blush'])
    paste_rot(fr, head, PIV_L, (PIV_S[0] + st['head_dx'], PIV_S[1]), st['head_ang'])
    hx, hy = st['hand']
    if hx < 1300:
        draw_arm(fr, hx, hy, *DIR)
    # hearts
    for h in HEARTS:
        age = t - h['t']
        if 0 <= age < 1.7:
            a = min(1, age / 0.2) * (1 - ease((age - 1.2) / 0.5))
            y = 820 - age * 230
            x = h['x'] + h['drift'] * age + 18 * math.sin(h['ph'] + age * 5)
            sc = 0.6 + 0.4 * ease(age / 0.25)
            paste_center(fr, heart_patch(h['size'] * sc, a), x, y)
    # purr text
    if 2.3 <= t < 6.2:
        a = ease((t - 2.3) / 0.3) * (1 - ease((t - 5.9) / 0.3))
        pulse = 1 + 0.06 * math.sin(2 * math.pi * 3 * t)
        paste_center(fr, text_patch('ゴロゴロ…', 70, (150, 88, 40), a), 215, 760, pulse, 8)
    # speech bubble
    if 6.3 <= t < 7.9:
        a = ease((t - 6.3) / 0.15) * (1 - ease((t - 7.55) / 0.3))
        pop = 0.7 + 0.3 * ease((t - 6.3) / 0.2) + 0.06 * math.sin(math.pi * min(1, (t - 6.3) / 0.35))
        paste_center(fr, text_patch('もっとなでて…', 56, OUT, a, bubble=True), 330, 680, pop)
    return fr.resize((W, H), Image.LANCZOS)

def make_audio(path):
    sr = 44100
    n = int(sr * DUR)
    t = np.arange(n) / sr
    rng = np.random.default_rng(3)
    noise = rng.standard_normal(n)
    sp = np.fft.rfft(noise)
    fq = np.fft.rfftfreq(n, 1 / sr)
    sp *= np.exp(-(fq / 380) ** 2) * (fq > 30)
    lp = np.fft.irfft(sp, n)
    lp /= np.abs(lp).max()
    pulses = (0.5 + 0.5 * np.cos(2 * np.pi * 25 * t)) ** 6
    breath_ph = (t - 2.1) / 1.25
    breath = 0.55 + 0.45 * np.abs(np.sin(np.pi * breath_ph))
    tone = 0.25 * np.sin(2 * np.pi * 50 * t) + 0.15 * np.sin(2 * np.pi * 100 * t)
    purr = (lp + tone) * pulses * breath
    env = np.clip((t - 2.1) / 0.35, 0, 1) * np.clip((6.2 - t) / 0.4, 0, 1)
    sig = purr * env
    # soft room tone
    room = rng.standard_normal(n)
    sr_sp = np.fft.rfft(room) * np.exp(-(fq / 900) ** 2)
    room = np.fft.irfft(sr_sp, n); room /= np.abs(room).max()
    sig = sig / max(1e-9, np.abs(sig).max()) * 0.6 + room * 0.015
    pcm = (np.clip(sig, -1, 1) * 32000).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())

if __name__ == '__main__':
    out = sys.argv[1]
    bg = make_bg(); caption(bg)
    if len(sys.argv) > 2 and sys.argv[2] == 'preview':
        for tt in [0.5, 1.6, 3.0, 6.7, 7.4]:
            render(bg, int(tt * FPS)).save(f'{out}_{tt}.png')
        sys.exit()
    wav = out + '.wav'
    make_audio(wav)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out],
                         stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(render(bg, i).tobytes())
    p.stdin.close(); p.wait()
    print('done', p.returncode)
