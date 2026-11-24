import math, sys
sys.path.insert(0, '/home/claude/hack'); sys.path.insert(0, '/home/claude/hack2')
import anim
from anim import Pen, seg, lerp, mix, ease, INK, ORANGE, BLUE, RED, GREEN, S
from PIL import Image, ImageDraw
from h2content import EN_LABELS
anim.EN.update(EN_LABELS)
WATER = (170, 215, 245)

def glass(p, cx, top=260, bot=640, w=150):
    p.poly([(cx - w, top), (cx + w, top), (cx + w * 0.8, bot), (cx - w * 0.8, bot)], fill=(235, 245, 252))
    p.poly([(cx - w * 0.95, top + 80), (cx + w * 0.95, top + 80), (cx + w * 0.8 - 4, bot - 4), (cx - w * 0.8 + 4, bot - 4)], fill=WATER, outline=None)

def egg(u):
    p = Pen()
    glass(p, 230, w=140); glass(p, 610, w=140)
    d = seg(u, 0.15, 0.4)
    # fresh: lies on bottom
    y1 = lerp(150, 570, d); p.ell((230 - 80, y1 - 50, 230 + 80, y1 + 50), fill=(245, 225, 190))
    # old: stands / floats
    y2 = lerp(150, 420, d)
    p.ell((610 - 50, y2 - 80, 610 + 50, y2 + 80), fill=(235, 210, 170))
    if d > 0.9: p.ell((610 - 35, y2 - 75, 610 + 35, y2 - 30), fill=(255, 255, 255), outline=(180, 180, 180), w=3)
    if u < 0.4: p.text((420, 80), '水に入れる', 50, fill=BLUE, stroke=8)
    if u > 0.45:
        p.badge((230, 700), '新しい', GREEN, 50); p.badge((610, 700), '古い', RED, 50)
    if u > 0.75: p.text((420, 80), '浮いたら食べない', 46, fill=RED, stroke=8)
    return p.out()

def garlic(u):
    p = Pen()
    shake = seg(u, 0.2, 0.7); dx = 30 * math.sin(u * 60) * (1 if 0.2 < u < 0.7 else 0)
    cx = 420 + dx
    p.rect((cx - 170, 200, cx + 170, 560), fill=(235, 245, 252), r=30)
    p.rect((cx - 180, 170, cx + 180, 215), fill=(240, 120, 90), r=14)
    peeled = u > 0.65
    for k, (ox, oy) in enumerate([(-70, 470), (40, 480), (-20, 380), (80, 390), (-90, 300)]):
        x, y = cx + ox + (12 * math.sin(u * 50 + k) if 0.2 < u < 0.7 else 0), oy
        col = (250, 248, 240) if peeled else (235, 220, 200)
        p.poly([(x - 35, y + 30), (x, y - 40), (x + 35, y + 30)], fill=col)
    if peeled:
        for k in range(6): p.line([(cx - 130 + k * 50, 540), (cx - 110 + k * 50, 525)], fill=(200, 180, 150), w=5)
        p.badge((420, 680), '皮がむけた！', GREEN, 54)
    elif u > 0.2:
        p.text((420, 680), 'シャカシャカ振る', 50, fill=ORANGE, stroke=8)
    return p.out()

def boil(u):
    p = Pen()
    p.rect((180, 330, 660, 620), fill=(170, 175, 190), r=20)
    p.rect((180, 340, 660, 400), fill=WATER, outline=None)
    spoon = seg(u, 0.35, 0.5)
    rise = seg(u, 0.05, 0.35) * (1 - seg(u, 0.5, 0.75))
    for k in range(9):
        x = 210 + k * 52; r = 26 + 6 * math.sin(u * 30 + k)
        y = 340 - 80 * rise - 20 * math.sin(u * 20 + k * 2) * rise
        p.ell((x - r, y - r, x + r, y + r), fill=(255, 255, 255), outline=(200, 210, 220), w=3)
    if spoon > 0:
        sx = lerp(900, 140, spoon)
        p.rect((sx, 300, sx + 560, 324), fill=(200, 150, 90), r=10)
        p.ell((sx + 520, 288, sx + 620, 336), fill=(200, 150, 90))
    if u < 0.35: p.badge((420, 140), '吹きこぼれそう…', RED, 50)
    elif u < 0.6: p.text((420, 140), '木べらをわたす', 50, fill=ORANGE, stroke=8)
    else: p.badge((420, 140), '泡がこわれる！', GREEN, 52)
    return p.out()

def rice(u):
    p = Pen()
    flat = seg(u, 0.15, 0.45)
    h = lerp(220, 50, flat); w = lerp(220, 420, flat)
    p.rect((420 - w / 2, 480 - h, 420 + w / 2, 480), fill=(252, 252, 248), r=20)
    for k in range(int(10 + 10 * flat)):
        x = 420 - w / 2 + 20 + (k * 37) % (w - 40); y = 480 - h + 15 + (k * 23) % max(10, h - 30)
        p.ell((x - 7, y - 4, x + 7, y + 4), fill=(235, 235, 225), outline=None)
    if flat > 0.9:
        p.rect((420 - w / 2 - 10, 470 - h, 420 + w / 2 + 10, 490), fill=None, outline=(170, 210, 240), w=4, r=24)
        fr = seg(u, 0.55, 0.8)
        for k in range(5):
            x = 260 + k * 80; p.line([(x, 360), (x, 360 - 40 * fr)], fill=BLUE, w=6)
        p.text((420, 250), '薄く平らに', 50, fill=ORANGE, stroke=8)
    if u > 0.8: p.badge((420, 640), '早く凍る！', GREEN, 54)
    return p.out()

def tomato(u):
    p = Pen()
    a = seg(u, 0.25, 0.4); b = seg(u, 0.5, 0.62); peel = seg(u, 0.75, 0.9)
    tx = lerp(lerp(420, 230, a), 610, b); ty = lerp(300, 430, max(a, b) if u < 0.7 else 1)
    if u > 0.25:
        p.rect((100, 380, 360, 600), fill=(240, 120, 90), r=24); p.rect((110, 400, 350, 590), fill=(255, 210, 180), outline=None, r=18)
        p.text((230, 640), '熱湯 10秒', 40, fill=RED, stroke=6)
        p.rect((480, 380, 740, 600), fill=(150, 190, 230), r=24); p.rect((490, 400, 730, 590), fill=WATER, outline=None, r=18)
        p.text((610, 640), '冷水へ', 40, fill=BLUE, stroke=6)
    p.ell((tx - 90, ty - 85, tx + 90, ty + 85), fill=mix((230, 60, 50), (255, 120, 100), peel))
    p.poly([(tx - 30, ty - 85), (tx, ty - 110), (tx + 30, ty - 85)], fill=GREEN)
    p.line([(tx - 25, ty + 40), (tx + 25, ty + 80)], fill=(120, 20, 20), w=5); p.line([(tx + 25, ty + 40), (tx - 25, ty + 80)], fill=(120, 20, 20), w=5)
    if peel > 0:
        p.poly([(tx + 40, ty + 60), (tx + 40 + 110 * peel, ty + 40 - 20 * peel), (tx + 90, ty + 90)], fill=(220, 50, 40))
        p.badge((420, 140), 'つるんとむける！', GREEN, 52)
    elif u < 0.25: p.text((420, 140), '十字の切れ目', 50, fill=ORANGE, stroke=8)
    return p.out()

def chill(u):
    p = Pen()
    p.rect((470, 140, 760, 620), fill=(230, 240, 250), r=20)
    for a in (0, 60, 120):
        r_ = math.radians(a); p.line([(615 - 40 * math.cos(r_), 230 - 40 * math.sin(r_)), (615 + 40 * math.cos(r_), 230 + 40 * math.sin(r_))], fill=BLUE, w=7)
    wrap = seg(u, 0.1, 0.3); inn = seg(u, 0.35, 0.5)
    cx = lerp(220, 615, inn); cy = lerp(430, 450, inn)
    p.rect((cx - 60, cy - 120, cx + 60, cy + 120), fill=(220, 80, 70), r=20)
    if wrap > 0:
        p.rect((cx - 66, cy - 100, cx - 66 + 132 * wrap, cy + 100), fill=(240, 245, 255), outline=(150, 190, 230), w=4, r=12)
    if u < 0.35 and wrap > 0.3: p.text((220, 200), 'ぬれたペーパー', 42, fill=BLUE, stroke=8)
    if u > 0.55:
        k = seg(u, 0.55, 0.9)
        p.rect((80, 260, 330, 300), fill=(230, 230, 235), r=20)
        p.rect((80, 260, 80 + 250 * k, 300), fill=BLUE, outline=None, r=20)
        p.text((205, 340), '冷え具合', 30, fill=INK)
    if u > 0.85: p.badge((300, 640), '早く冷える！', GREEN, 54)
    return p.out()

def micro(u):
    p = Pen()
    p.rect((90, 150, 750, 600), fill=(225, 228, 235), r=24); p.rect((120, 180, 560, 570), fill=(250, 250, 245), r=12)
    p.rect((590, 200, 720, 300), fill=(60, 70, 90), r=10)
    for k in range(6):
        x, y = 160 + (k * 67) % 380, 200 + (k * 53) % 330
        if u < 0.7: p.ell((x - 18, y - 12, x + 18, y + 12), fill=mix((190, 120, 70), (240, 220, 200), seg(u, 0.4, 0.7)), outline=None)
    p.poly([(270, 470), (410, 470), (390, 560), (290, 560)], fill=(235, 245, 255))
    p.rect((280, 480, 400, 520), fill=WATER, outline=None)
    if 0.15 < u < 0.7:
        for k in range(4):
            ph = ((u - 0.15) * 2 + k / 4) % 1
            x = 300 + k * 30; y = lerp(460, 220, ph)
            p.line([(x + 10 * math.sin(y / 20 + j), y - j * 18) for j in range(4)], fill=(210, 215, 225), w=6)
        p.text((655, 380), '水を入れて\n温める', 34, fill=BLUE, stroke=6)
    if 0.4 < u < 0.75: p.badge((340, 110), '汚れが浮く！', ORANGE, 50)
    if u > 0.7:
        sx = lerp(150, 520, seg(u, 0.7, 0.9))
        p.rect((sx - 50, 260, sx + 50, 330), fill=(255, 210, 120), r=12)
        p.badge((420, 680), 'さっとふける！', GREEN, 52)
    return p.out()

def drain(u):
    p = Pen()
    p.ell((180, 220, 660, 660), fill=(200, 205, 215), w=6); p.ell((250, 290, 590, 590), fill=(150, 155, 165), w=5)
    for k in range(8):
        a = math.radians(k * 45); p.line([(420 + 70 * math.cos(a), 440 + 70 * math.sin(a)), (420 + 160 * math.cos(a), 440 + 160 * math.sin(a))], fill=(120, 125, 135), w=8)
    clean = seg(u, 0.5, 0.85)
    if clean < 1:
        for k in range(7):
            a = math.radians(k * 51 + 10); x, y = 420 + 120 * math.cos(a), 440 + 120 * math.sin(a)
            r = 22 * (1 - clean); p.ell((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(150, 170, 110), outline=None)
    drop = seg(u, 0.15, 0.35)
    for k, (bx, by) in enumerate([(360, 400), (470, 410), (420, 490)]):
        y = lerp(120, by, drop)
        p.ell((bx - 32, y - 32, bx + 32, y + 32), fill=(215, 220, 230), outline=(140, 145, 160), w=4)
        p.line([(bx - 15, y - 10), (bx + 10, y + 12)], fill=(250, 250, 255), w=4)
    if u < 0.45: p.text((420, 110), '丸めたアルミホイル', 44, fill=INK, stroke=8)
    if u > 0.8: p.badge((420, 720), 'ぬめりにくい！', GREEN, 52)
    return p.out()

def sticker(u):
    p = Pen()
    p.rect((120, 250, 720, 620), fill=(170, 210, 240), r=30)
    peel = seg(u, 0.55, 0.85)
    sx0 = 260
    p.rect((sx0, 330, sx0 + 320 * (1 - peel), 530), fill=(255, 255, 255), w=4, r=8)
    if peel > 0:
        p.poly([(sx0 + 320 * (1 - peel), 330), (sx0 + 320 * (1 - peel) + 120 * peel, 280), (sx0 + 320 * (1 - peel) + 160 * peel, 480), (sx0 + 320 * (1 - peel), 530)], fill=(240, 240, 240))
    if peel < 0.3: p.text((sx0 + 160, 430), 'SALE', 70, fill=RED)
    if 0.15 < u < 0.55:
        for k in range(4):
            ph = ((u - 0.15) * 3 + k / 4) % 1
            x = lerp(780, 600, ph); p.arrow((x + 50, 360 + k * 40), (x, 360 + k * 40), fill=(255, 150, 60), w=8, head=20)
        p.text((420, 170), '温風を当てる', 50, fill=ORANGE, stroke=8)
    if peel > 0.6: p.badge((420, 700), 'するっとはがれる！', GREEN, 52)
    return p.out()

def sneaker(u):
    p = Pen()
    p.poly([(130, 470), (170, 330), (330, 300), (430, 380), (650, 420), (720, 480), (130, 480)], fill=(250, 250, 250))
    p.rect((120, 470, 730, 540), fill=(255, 255, 255), r=20)
    clean = seg(u, 0.35, 0.8)
    for k in range(9):
        x = 170 + k * 60
        if x > lerp(140, 760, clean): p.ell((x - 18, 488, x + 18, 520), fill=(110, 105, 100), outline=None)
    if 0.2 < u < 0.85:
        sx = lerp(140, 700, clean); p.rect((sx - 60, 560, sx + 60, 640), fill=(255, 255, 255), outline=(150, 190, 230), w=5, r=10)
        p.text((420, 200), 'ぬらしてこする', 50, fill=BLUE, stroke=8)
    if u > 0.8: p.badge((420, 200), '白さ復活！', GREEN, 56)
    return p.out()

def hanger(u):
    p = Pen()
    for side, cx in enumerate((230, 610)):
        p.line([(cx, 140), (cx, 180)], w=6); p.d.arc([((cx - 25) * S), (120 * S), ((cx + 25) * S), (170 * S)], 180, 360, fill=INK, width=10)
        p.line([(cx - 170, 260), (cx, 180), (cx + 170, 260)], w=10)
        drop = seg(u, 0.4, 0.65) if side == 0 else 0
        rot = -25 * drop; dy = 160 * drop
        p.poly([(cx - 160, 262 + dy), (cx + 160, 262 + dy * 0.2), (cx + 140, 560 + dy * 0.6), (cx - 140, 560 + dy)], fill=(240, 160, 190) if side == 0 else (240, 160, 190))
        if side == 1 and u > 0.15:
            for x in (cx - 140, cx + 140): p.rect((x - 14, 240, x + 14, 275), fill=(210, 170, 110), w=3, r=6)
    if u > 0.15: p.text((610, 90), '輪ゴムを巻く', 40, fill=ORANGE, stroke=8)
    if u > 0.5: p.badge((230, 700), 'ずり落ちる…', RED, 44); p.badge((610, 700), '落ちない！', GREEN, 48)
    return p.out()

def soda(u):
    p = Pen()
    p.rect((140, 100, 700, 680), fill=(235, 242, 250), r=24)
    for y in (300, 480): p.line([(150, y), (690, y)], fill=(190, 200, 215), w=5)
    p.rect((200, 200, 300, 295), fill=(120, 190, 100), r=10); p.rect((520, 380, 640, 475), fill=(240, 150, 80), r=10)
    cl = seg(u, 0.4, 0.8)
    if cl < 1:
        for k in range(4):
            ph = (u * 2 + k / 4) % 1
            x = 250 + k * 110; y = 600 - 120 * ph
            p.line([(x + 15 * math.sin((y + j * 20) / 25), y - j * 25) for j in range(4)], fill=mix((150, 170, 90), (235, 242, 250), cl), w=7)
    bx = 330; p.rect((bx, 560, bx + 180, 660), fill=(255, 255, 255), w=5, r=14)
    p.rect((bx + 10, 580, bx + 170, 650), fill=(245, 245, 240), outline=None, r=10)
    p.text((bx + 90, 615), '重曹', 32, fill=INK)
    if cl > 0.6: p.badge((420, 160), 'においを吸う！', GREEN, 52)
    return p.out()

def keys_combo(p, keys, u, a=0.3, y=650):
    n = len(keys); span = 230
    for k, kk in enumerate(keys):
        pr = seg(u, a + k * 0.07, a + 0.05 + k * 0.07)
        x = 420 - span * (n - 1) / 2 + k * span; yy = y + 8 * pr
        p.rect((x - 95, yy - 48, x + 95, yy + 48), fill=mix((240, 240, 245), (255, 200, 120), pr), w=5, r=16)
        p.text((x, yy), kk, 40, fill=INK)
        if k < n - 1: p.text((x + span / 2, y), '＋', 40, fill=INK)

def snip(u):
    p = Pen()
    p.rect((80, 110, 760, 540), fill=(255, 255, 255), r=16)
    for k in range(5): p.rect((120, 160 + k * 70, 120 + (k * 97) % 400 + 200, 200 + k * 70), fill=(225, 230, 240), outline=None, r=8)
    keys_combo(p, ['Win', 'Shift', 'S'], u, 0.1)
    sel = seg(u, 0.4, 0.65)
    if sel > 0:
        x0, y0 = 250, 220; x1, y1 = lerp(250, 620, sel), lerp(220, 440, sel)
        dim = Image.new('RGBA', p.im.size, (0, 0, 0, 0)); ImageDraw.Draw(dim).rectangle([80 * S, 110 * S, 760 * S, 540 * S], fill=(0, 0, 0, 70))
        ImageDraw.Draw(dim).rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=(0, 0, 0, 0))
        p.im.alpha_composite(dim)
        p.rect((x0, y0, x1, y1), fill=None, outline=ORANGE, w=5)
        if u < 0.7: p.text((420, 80), '範囲を選ぶ', 44, fill=ORANGE, stroke=8)
    if u > 0.72: p.badge((420, 80), '切り取れた！', GREEN, 50)
    return p.out()

def lock(u):
    p = Pen()
    p.rect((120, 110, 720, 520), fill=(60, 70, 100) if u > 0.5 else (255, 255, 255), r=16)
    if u <= 0.5:
        for k in range(5): p.rect((160, 160 + k * 65, 160 + (k * 83) % 350 + 180, 195 + k * 65), fill=(225, 230, 240), outline=None, r=8)
    else:
        p.rect((360, 280, 480, 380), fill=(255, 210, 90), r=12); p.d.arc([(375 * S), (220 * S), (465 * S), (310 * S)], 180, 360, fill=(255, 210, 90), width=18)
        p.badge((420, 450), 'ロック完了！', GREEN, 50)
    keys_combo(p, ['Win', 'L'], u, 0.3)
    if u < 0.3: p.text((420, 70), '席を立つ前に', 44, fill=INK, stroke=8)
    return p.out()

def cursor(u):
    p = Pen()
    p.rect((220, 60, 620, 740), fill=(40, 45, 60), r=40); p.rect((240, 110, 600, 690), fill=(250, 250, 255), outline=None, r=18)
    p.text((260, 180), 'あしたのかいぎは3じです', 26, fill=INK, anchor='lm')
    hold = u > 0.3
    mv = seg(u, 0.45, 0.8)
    cx = lerp(560, 330, mv)
    p.line([(cx, 160), (cx, 200)], fill=BLUE, w=5)
    kb = (210, 215, 225) if hold else (225, 228, 235)
    p.rect((240, 420, 600, 690), fill=kb, outline=None, r=12)
    if not hold:
        for r_ in range(3):
            for c in range(7): p.rect((255 + c * 49, 440 + r_ * 60, 295 + c * 49, 485 + r_ * 60), fill=(255, 255, 255), outline=None, r=6)
    p.rect((320, 620, 520, 665), fill=(255, 255, 255) if not hold else (200, 205, 215), outline=None, r=8)
    fx = lerp(420, 300, mv) if hold else 420
    p.ell((fx - 30, 610, fx + 30, 670), fill=(255, 200, 160, 200), outline=None)
    if 0.3 < u < 0.45: p.text((420, 330), '長押し', 48, fill=ORANGE, stroke=8)
    if u > 0.6: p.badge((420, 330), 'カーソルが動く！', GREEN, 48)
    return p.out()

def cables(u):
    p = Pen()
    cols = [(60, 60, 70), (60, 60, 70), (60, 60, 70)]
    labs = ['充電器', 'モニター', 'スピーカー']
    tag = seg(u, 0.35, 0.7)
    for k in range(3):
        x = 220 + k * 200
        p.line([(x, 120), (x + 30 * math.sin(k), 300), (x - 20, 480), (x, 680)], fill=cols[k], w=14)
        if tag > k / 3:
            p.rect((x - 70, 380, x + 70, 440), fill=(255, 230, 120), w=4, r=8)
            p.text((x, 410), labs[k], 26, fill=INK)
    if u < 0.35: p.badge((420, 560), 'どれがどれ？', RED, 52)
    if u > 0.75: p.badge((420, 560), '一目でわかる！', GREEN, 52)
    return p.out()

def pack(u):
    p = Pen()
    for side, cx in enumerate((230, 610)):
        good = side == 1
        p.ell((cx - 120 - 60 * (1 - good) * seg(u, 0.4, 0.6) * 0, 150, cx - 40, 230), fill=(240, 200, 170))
        p.rect((cx - 140, 230, cx - 30, 560), fill=(120, 160, 220), r=30)
        tilt = (1 - good) * seg(u, 0.4, 0.65) * 12
        bag = Image.new('RGBA', p.im.size, (0, 0, 0, 0)); bp = ImageDraw.Draw(bag)
        bp.rounded_rectangle([(cx - 30) * S, 230 * S, (cx + 130) * S, 520 * S], 30 * S, fill=(240, 150, 70), outline=INK, width=10)
        hy = 290 if good else 440; hx = cx - 10 if good else cx + 60
        bp.rounded_rectangle([(hx - 10) * S, hy * S, (hx + 60) * S, (hy + 70) * S], 10 * S, fill=(90, 90, 100))
        bag = bag.rotate(-tilt, center=((cx - 30) * S, 240 * S), resample=Image.BICUBIC)
        p.im.alpha_composite(bag)
    if u > 0.3: p.text((420, 90), '背中側に重いもの', 44, fill=ORANGE, stroke=8)
    if u > 0.6: p.badge((230, 680), '後ろに引っぱられる…', RED, 36); p.badge((610, 680), '軽く感じる！', GREEN, 46)
    return p.out()

def blister(u):
    p = Pen()
    p.poly([(150, 600), (200, 300), (360, 260), (420, 420), (700, 520), (720, 600)], fill=(245, 205, 175))
    a = seg(u, 0.2, 0.45)
    if a > 0:
        p.rect((175, 380 - 80 * (1 - a), 275, 470 - 80 * (1 - a)), fill=(240, 210, 170), outline=(200, 160, 120), w=4, r=14)
        p.rect((205, 400 - 80 * (1 - a), 245, 450 - 80 * (1 - a)), fill=(250, 235, 210), outline=None, r=6)
    if 0.2 < u < 0.55: p.text((420, 150), '先に貼る', 52, fill=ORANGE, stroke=8)
    sh = seg(u, 0.55, 0.75)
    if sh > 0:
        p.poly([(120, 640), (140, 420 + 60 * (1 - sh)), (320, 400 + 60 * (1 - sh)), (420, 500), (740, 560), (740, 650)], fill=(70, 80, 120))
    if u > 0.8: p.badge((420, 150), '靴ずれ知らず！', GREEN, 54)
    return p.out()

def parking(u):
    p = Pen()
    for k in range(4):
        x = 120 + k * 200
        p.rect((x, 160, x + 60, 640), fill=(200, 200, 205), w=4)
        p.text((x + 30, 230), f'B{k + 3}', 30, fill=INK)
    p.rect((300, 450, 520, 590), fill=(220, 80, 70), r=30); p.ell((320, 560, 380, 620), fill=INK); p.ell((440, 560, 500, 620), fill=INK)
    ph = seg(u, 0.2, 0.4)
    if ph > 0:
        p.rect((560, 260, 760, 600), fill=(40, 45, 60), r=24); p.rect((575, 290, 745, 570), fill=(230, 235, 245), outline=None, r=10)
        p.rect((620, 330, 700, 520), fill=(200, 200, 205), outline=None); p.text((660, 400), 'B4', 40, fill=INK)
        if 0.38 < u < 0.48:
            fl = Image.new('RGBA', p.im.size, (255, 255, 255, 140)); p.im.alpha_composite(fl)
        if u < 0.6: p.text((660, 200), 'パシャッ', 44, fill=ORANGE, stroke=8)
    if u > 0.7: p.badge((420, 710), 'すぐ戻れる！', GREEN, 52)
    return p.out()

def keyspot(u):
    p = Pen()
    p.rect((80, 120, 760, 640), fill=(250, 240, 220), r=24)
    p.rect((480, 420, 720, 470), fill=(170, 120, 80), r=10)          # shelf
    p.rect((520, 380, 680, 420), fill=(235, 235, 240), w=4, r=10)    # tray
    good = u > 0.5
    kx, ky = (600, 370) if good else (200 + 40 * math.sin(u * 20), 540)
    p.ell((kx - 30, ky - 30, kx + 30, ky + 30), fill=None, outline=(220, 180, 60), w=10)
    p.rect((kx + 25, ky - 8, kx + 95, ky + 8), fill=(220, 180, 60), outline=None)
    if not good:
        p.badge((420, 220), 'どこ…？', RED, 56)
        for k in range(3): p.text((150 + k * 180, 400 + 40 * (k % 2)), '?', 60, fill=RED, stroke=6)
    else:
        p.arrow((420, 260), (560, 350), fill=GREEN, w=10)
        p.badge((420, 220), 'いつもここ！', GREEN, 56)
    return p.out()

FUNCS = [egg, garlic, boil, rice, tomato, chill, micro, drain, sticker, sneaker, hanger, soda, snip, lock, cursor, cables, pack, blister, parking, keyspot]
