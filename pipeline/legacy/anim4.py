import math, sys
sys.path.insert(0, '/home/claude/hack'); sys.path.insert(0, '/home/claude/hack3')
import anim
from anim import Pen, seg, lerp, mix, INK, ORANGE, BLUE, RED, GREEN, S
from PIL import Image, ImageDraw
from h3content import EN_LABELS
anim.EN.update(EN_LABELS)

def phone_frame(p, x0=250, x1=590, y0=80, y1=720):
    p.rect((x0, y0, x1, y1), fill=(40, 45, 60), r=40); p.rect((x0 + 18, y0 + 45, x1 - 18, y1 - 45), fill=(250, 250, 255), outline=None, r=18)

def keys_combo(p, keys, u, a=0.3, y=650, span=230):
    n = len(keys)
    for k, kk in enumerate(keys):
        pr = seg(u, a + k * 0.07, a + 0.05 + k * 0.07)
        x = 420 - span * (n - 1) / 2 + k * span; yy = y + 8 * pr
        p.rect((x - 100, yy - 48, x + 100, yy + 48), fill=mix((240, 240, 245), (255, 200, 120), pr), w=5, r=16)
        p.text((x, yy), kk, 36, fill=INK)
        if k < n - 1: p.text((x + span / 2, y), '＋', 40, fill=INK)

def fuel(u):
    p = Pen()
    p.ell((170, 160, 670, 660), fill=(30, 35, 50), w=8)
    for k in range(9):
        a = math.radians(200 + k * 17.5); p.line([(420 + 200 * math.cos(a), 410 + 200 * math.sin(a)), (420 + 230 * math.cos(a), 410 + 230 * math.sin(a))], fill=(240, 240, 240), w=6)
    p.text((230, 470), 'E', 44, fill=(240, 240, 240)); p.text((610, 470), 'F', 44, fill=(240, 240, 240))
    a = math.radians(lerp(215, 250, seg(u, 0.1, 0.3)))
    p.line([(420, 410), (420 + 180 * math.cos(a), 410 + 180 * math.sin(a))], fill=(255, 90, 60), w=10)
    p.rect((370, 500, 450, 590), fill=(240, 240, 240), outline=None, r=8); p.rect((385, 515, 435, 545), fill=(30, 35, 50), outline=None)
    blink = u > 0.4 and int(u * 12) % 2 == 0
    p.poly([(470, 530), (500, 545), (470, 560)], fill=(255, 200, 60) if blink or u > 0.75 else (240, 240, 240), outline=None)
    if u < 0.4: p.badge((420, 100), '左右どっち？', RED, 50)
    if u > 0.45:
        p.arrow((560, 545), (740, 545), fill=ORANGE, w=12)
        p.badge((420, 720), '給油口はこっち！', GREEN, 50)
    return p.out()

def pulltab(u):
    p = Pen()
    p.rect((280, 250, 560, 700), fill=(200, 60, 60), r=30); p.ell((280, 220, 560, 290), fill=(200, 205, 215))
    spin = seg(u, 0.3, 0.5)
    tx = 420 + 0 * spin; ty = lerp(255, 245, spin)
    ang = lerp(0, 180, spin)
    p.ell((390, 230, 450, 265), fill=(60, 60, 70), outline=None)
    tab = Pen(); tab.ell((380, 225, 460, 285), fill=(190, 195, 205), w=4); tab.ell((400, 240, 440, 270), fill=(250, 244, 232), w=3)
    ti = tab.im.rotate(ang, center=(420 * S, 255 * S), resample=Image.BICUBIC); p.im.alpha_composite(ti)
    float_ = 0 if u > 0.55 else seg(u, 0.05, 0.25)
    sx = 420 if u > 0.55 else 430; sy = 120 - 60 * float_ * (0.5 + 0.5 * math.sin(u * 20))
    p.rect((sx - 12, sy, sx + 12, sy + 200), fill=(255, 255, 255), outline=(80, 160, 220), w=4, r=8)
    if u < 0.3: p.badge((640, 160), 'ぷかぷか…', RED, 40)
    elif u < 0.55: p.text((620, 160), 'プルタブを回す', 38, fill=ORANGE, stroke=8)
    else: p.badge((640, 160), '浮かない！', GREEN, 46)
    return p.out()

def hairpin(u):
    p = Pen()
    p.ell((150, 250, 690, 780), fill=(60, 45, 40), outline=None)
    for k in range(14): p.line([(180 + k * 36, 300 + (k % 3) * 10), (200 + k * 36, 600)], fill=(90, 70, 60), w=4)
    flip = seg(u, 0.2, 0.4)
    y = 380
    p.line([(250, y), (620, y)], fill=(40, 40, 40), w=10)
    pts = [(250 + k * 15, y + 28 + 10 * math.sin(k * 1.2) * (1 if flip > 0.5 else 0)) for k in range(25)]
    p.line(pts, fill=(40, 40, 40), w=10)
    p.d.arc([(600 * S), (y * S), (640 * S), ((y + 30) * S)], 270, 90, fill=(40, 40, 40), width=20)
    if flip > 0.5:
        p.text((420, 470), 'ギザギザを下に', 42, fill=ORANGE, stroke=8)
    if u > 0.7: p.badge((420, 160), 'ずれない！', GREEN, 56)
    return p.out()

def shell(u):
    p = Pen()
    p.ell((170, 300, 670, 640), fill=(255, 255, 255), w=6)
    p.ell((220, 330, 620, 610), fill=(250, 245, 230), outline=None)
    p.ell((340, 400, 500, 540), fill=(255, 190, 60), outline=None)
    take = seg(u, 0.4, 0.8)
    fx, fy = lerp(560, 640, take), lerp(470, 250, take)
    p.poly([(fx - 15, fy - 10), (fx + 15, fy - 15), (fx + 10, fy + 12), (fx - 12, fy + 10)], fill=(240, 220, 190))
    if u > 0.3:
        sx = lerp(760, fx + 30, seg(u, 0.3, 0.45)); sy = fy + 10
        p.d.pieslice([((sx - 80) * S), ((sy - 70) * S), ((sx + 80) * S), ((sy + 70) * S)], 20, 200, fill=(240, 215, 180), outline=INK, width=8)
    if u < 0.3: p.badge((420, 160), '殻が入った！', RED, 52)
    elif u < 0.8: p.text((420, 160), '殻ですくう', 52, fill=ORANGE, stroke=8)
    else: p.badge((420, 160), 'すっと取れる！', GREEN, 54)
    return p.out()

def thread(u):
    p = Pen()
    cut = seg(u, 0.4, 0.7)
    gap = 40 * seg(u, 0.72, 0.85)
    for side in (-1, 1):
        x = 420 + side * gap
        p.d.pieslice([((x - 140) * S), (300 * S), ((x + 140) * S), (620 * S)], 90 if side < 0 else 270, 270 if side < 0 else 90, fill=(255, 255, 255), outline=INK, width=10)
        if gap > 5:
            p.d.pieslice([((x - 70) * S), (390 * S), ((x + 70) * S), (530 * S)], 90 if side < 0 else 270, 270 if side < 0 else 90, fill=(255, 200, 60), outline=None)
    y = lerp(240, 470, cut)
    p.line([(170, y), (670, y)], fill=(80, 80, 90), w=4)
    p.ell((150, y - 20, 190, y + 20), fill=(240, 200, 170), outline=None); p.ell((650, y - 20, 690, y + 20), fill=(240, 200, 170), outline=None)
    if u < 0.4: p.text((420, 150), '糸をピンと張る', 48, fill=ORANGE, stroke=8)
    if u > 0.8: p.badge((420, 690), '断面きれい！', GREEN, 54)
    return p.out()

def wrap(u):
    p = Pen()
    p.rect((120, 320, 720, 520), fill=(220, 230, 240), r=90)
    p.ell((90, 320, 190, 520), fill=(200, 210, 225))
    lift = seg(u, 0.45, 0.65)
    tx = lerp(700, 450, seg(u, 0.2, 0.4))
    if u > 0.15:
        p.rect((tx - 50, 230 + 60 * math.sin(u * 30) * (0.2 < u < 0.45), tx + 50, 280), fill=(255, 245, 200), outline=(200, 180, 120), w=4, r=8)
    if lift > 0:
        p.poly([(380, 330), (520, 330), (500, 330 - 120 * lift), (400, 330 - 120 * lift)], fill=(240, 245, 250), outline=(170, 190, 210), w=4)
    if u < 0.2: p.badge((420, 150), '端はどこ…？', RED, 52)
    elif u < 0.6: p.text((420, 150), 'テープでトントン', 50, fill=ORANGE, stroke=8)
    else: p.badge((420, 650), '見つかった！', GREEN, 54)
    return p.out()

def snackbag(u):
    p = Pen()
    f1 = seg(u, 0.1, 0.3); f2 = seg(u, 0.35, 0.55); flip = seg(u, 0.6, 0.75)
    top = lerp(150, 320, f1)
    p.rect((230, top, 610, 680), fill=(250, 200, 60), r=10)
    p.text((420, 560), 'CHIPS', 64, fill=(200, 60, 40))
    if f1 > 0.9:
        for k in range(3): p.line([(240, top + 15 + k * 18), (600, top + 15 + k * 18)], fill=(200, 150, 30), w=4)
    if f2 > 0:
        c = 120 * f2
        p.poly([(230, top), (230 + c, top), (230, top + c)], fill=(230, 170, 40))
        p.poly([(610, top), (610 - c, top), (610, top + c)], fill=(230, 170, 40))
    if flip > 0.5:
        p.rect((230, top - 30, 610, top + 40), fill=(220, 160, 30), r=10)
    if u < 0.55 and u > 0.3: p.text((420, 150), '角を三角に折る', 46, fill=ORANGE, stroke=8)
    if 0.55 < u < 0.8: p.text((420, 150), 'くるっと裏返す', 46, fill=ORANGE, stroke=8)
    if u > 0.8: p.badge((420, 150), '開かない！', GREEN, 54)
    return p.out()

def chopsticks(u):
    p = Pen()
    sp = seg(u, 0.4, 0.65)
    for side in (-1, 1):
        y = 400 + side * 14 + side * 90 * sp
        p.rect((180, y - 14, 660, y + 14), fill=(235, 205, 150), r=6)
    if sp < 0.1: p.line([(180, 400), (560, 400)], fill=(180, 150, 100), w=3)
    p.arrow((420, 330 - 40 * sp), (420, 250 - 40 * sp), fill=ORANGE, w=10); p.arrow((420, 470 + 40 * sp), (420, 550 + 40 * sp), fill=ORANGE, w=10)
    if u < 0.4: p.text((420, 150), '横にして割る', 50, fill=ORANGE, stroke=8)
    if u > 0.7: p.badge((420, 690), 'きれいに割れた！', GREEN, 52)
    return p.out()

def hoodie(u):
    p = Pen()
    p.poly([(140, 260), (300, 200), (420, 280), (540, 200), (700, 260), (700, 660), (140, 660)], fill=(150, 180, 220))
    p.d.arc([(240 * S), (150 * S), (600 * S), (420 * S)], 0, 180, fill=(110, 140, 190), width=36)
    k = seg(u, 0.3, 0.85)
    pts = []
    for j in range(41):
        a = math.radians(180 - 180 * j / 40); pts.append((420 + 180 * math.cos(a), 285 + 135 * math.sin(a)))
    n = int(1 + 39 * k)
    p.line(pts[:n + 1], fill=(255, 255, 255), w=8)
    hx, hy = pts[n]
    p.ell((hx - 18, hy - 10, hx + 18, hy + 10), fill=(200, 200, 210), w=4)
    p.line([(130, 285), (pts[0][0], pts[0][1])], fill=(255, 255, 255), w=8)
    if u < 0.3: p.text((420, 110), '安全ピン', 50, fill=ORANGE, stroke=8)
    if u > 0.85: p.badge((420, 720), 'するする通る！', GREEN, 52)
    return p.out()

def staple(u):
    p = Pen()
    p.rect((160, 470, 680, 560), fill=(255, 255, 255), w=4); p.rect((170, 440, 670, 470), fill=(245, 245, 245), w=3)
    out = seg(u, 0.55, 0.75)
    p.rect((380, 455 - 60 * out, 470, 470 - 60 * out), fill=(170, 175, 185), outline=INK, w=3)
    ins = seg(u, 0.25, 0.5); rot = -15 * out
    st = Pen()
    x0 = lerp(760, 480, ins)
    st.rect((x0, 330, x0 + 360, 400), fill=(60, 70, 90), r=20)
    st.poly([(x0, 400), (x0 - 50, 455), (x0 + 30, 400)], fill=(150, 155, 165))
    si = st.im.rotate(rot, center=((x0 + 180) * S, 365 * S), resample=Image.BICUBIC); p.im.alpha_composite(si)
    if 0.2 < u < 0.6: p.text((420, 200), 'お尻を使う', 50, fill=ORANGE, stroke=8)
    if u > 0.75: p.badge((420, 200), 'すっとはずれる！', GREEN, 52)
    return p.out()

def gtimer(u):
    p = Pen()
    p.rect((90, 140, 750, 620), fill=(255, 255, 255), r=18)
    p.rect((130, 180, 710, 240), fill=(255, 255, 255), w=4, r=30)
    q = 'タイマー 3分'; n = int(len(q) * seg(u, 0.05, 0.3))
    p.text((160, 210), q[:n], 32, fill=INK, anchor='lm')
    if u > 0.35:
        left = 180 - int(170 * seg(u, 0.4, 1.0))
        p.text((420, 390), f'{left // 60}:{left % 60:02d}', 110, fill=INK)
        p.rect((180, 500, 660, 520), fill=(220, 225, 235), outline=None, r=10)
        p.rect((180, 500, 180 + 480 * left / 180, 520), fill=BLUE, outline=None, r=10)
        p.badge((420, 690), 'すぐ始まる！', GREEN, 52)
    return p.out()

def emoji(u):
    p = Pen()
    p.rect((80, 110, 760, 520), fill=(255, 255, 255), r=16)
    p.text((120, 170), 'おつかれさま', 34, fill=INK, anchor='lm')
    keys_combo(p, ['Win', '.'], u, 0.15)
    pop = seg(u, 0.35, 0.45)
    if pop > 0.1:
        p.rect((360, 200, 360 + 360 * pop, 200 + 280 * pop), fill=(245, 247, 252), w=4, r=14)
        if pop > 0.9:
            cols = [(255, 200, 60), (255, 120, 120), (120, 200, 120), (120, 170, 240), (240, 160, 220), (255, 170, 80)]
            for k in range(12):
                x = 400 + (k % 4) * 80; y = 250 + (k // 4) * 75
                p.ell((x - 25, y - 25, x + 25, y + 25), fill=cols[k % 6], w=3)
                p.ell((x - 10, y - 8, x - 4, y - 2), fill=INK, outline=None); p.ell((x + 4, y - 8, x + 10, y - 2), fill=INK, outline=None)
                p.d.arc([((x - 12) * S), ((y - 4) * S), ((x + 12) * S), ((y + 14) * S)], 20, 160, fill=INK, width=6)
            p.text((540, 175), '絵文字パネル', 30, fill=ORANGE, stroke=6)
    if u > 0.75:
        p.ell((345, 150, 395, 200), fill=(255, 200, 60), w=3)
        p.d.arc([(355 * S), (170 * S), (385 * S), (192 * S)], 20, 160, fill=INK, width=6)
    return p.out()

def ctrlbs(u):
    p = Pen()
    p.rect((80, 120, 760, 480), fill=(255, 255, 255), r=16)
    words = ['今日は', 'とても', 'いい', '天気です']
    gone = int(4 * seg(u, 0.45, 0.85))
    x = 120
    for k, w in enumerate(words[:4 - gone]):
        p.text((x, 300), w, 40, fill=INK, anchor='lm'); x += 40 * len(w) + 10
    p.line([(x, 270), (x, 330)], fill=BLUE, w=5)
    keys_combo(p, ['Ctrl', 'Backspace'], u, 0.2, span=300)
    if u > 0.55: p.badge((420, 180), '単語ごと消える！', GREEN, 50)
    return p.out()

def calc(u):
    p = Pen()
    phone_frame(p)
    num = '12345' if u < 0.5 else '1234'
    p.text((560, 240), num, 80, fill=INK, anchor='rm')
    sw = seg(u, 0.25, 0.5)
    if 0.2 < u < 0.55:
        fx = lerp(330, 540, sw); p.ell((fx - 30, 210, fx + 30, 270), fill=(255, 200, 160), outline=None)
        p.arrow((320, 300), (540, 300), fill=ORANGE, w=8)
        p.text((430, 340), 'スワイプ', 36, fill=ORANGE, stroke=6)
    for r_ in range(4):
        for c in range(4):
            x = 300 + c * 70; y = 400 + r_ * 70
            p.ell((x - 28, y - 28, x + 28, y + 28), fill=(255, 160, 40) if c == 3 else (210, 212, 220), outline=None)
    if u > 0.55: p.badge((420, 110), '1文字消えた！', GREEN, 50)
    return p.out()

def backtap(u):
    p = Pen()
    p.rect((260, 120, 580, 700), fill=(70, 75, 95), r=40)
    p.rect((300, 160, 400, 260), fill=(40, 45, 60), r=20)
    for k, t0 in enumerate((0.3, 0.42)):
        a = seg(u, t0, t0 + 0.08) * (1 - seg(u, t0 + 0.08, t0 + 0.12))
        if a > 0:
            p.ell((420 - 40, 420 - 40, 420 + 40, 420 + 40), fill=(255, 200, 160), outline=None)
            for j in range(6):
                ang = math.radians(j * 60); p.line([(420 + 55 * math.cos(ang), 420 + 55 * math.sin(ang)), (420 + 80 * math.cos(ang), 420 + 80 * math.sin(ang))], fill=ORANGE, w=6)
    if 0.25 < u < 0.6: p.text((420, 560), 'トントン', 50, fill=ORANGE, stroke=8)
    if u > 0.6:
        fl = Image.new('RGBA', p.im.size, (255, 255, 255, int(160 * (1 - seg(u, 0.6, 0.7))))); p.im.alpha_composite(fl)
        p.badge((420, 560), 'スクショ完了！', GREEN, 52)
    return p.out()

def camtext(u):
    p = Pen()
    p.rect((90, 300, 450, 700), fill=(255, 255, 255), w=4, r=8)
    for k, t in enumerate(['東京都千代田区', '丸の内1-1-1', '03-1234-5678']): p.text((110, 360 + k * 70), t, 30, fill=INK, anchor='lm')
    phone_frame(p, 440, 760, 140, 640)
    p.rect((470, 210, 730, 470), fill=(245, 245, 245), outline=None)
    for k, t in enumerate(['東京都千代田区', '丸の内1-1-1']): p.text((480, 270 + k * 60), t, 26, fill=INK, anchor='lm')
    sel = seg(u, 0.35, 0.55)
    if sel > 0:
        hl = Image.new('RGBA', p.im.size, (0, 0, 0, 0)); ImageDraw.Draw(hl).rectangle([475 * S, 245 * S, (475 + 250 * sel) * S, 355 * S], fill=(80, 150, 240, 90)); p.im.alpha_composite(hl)
    if 0.3 < u < 0.7: p.text((420, 120), '文字を選んでコピー', 44, fill=ORANGE, stroke=8)
    if u > 0.7: p.badge((420, 120), 'コピーできた！', GREEN, 52)
    return p.out()

def ring(u):
    p = Pen()
    phone_frame(p)
    p.ell((360, 220, 480, 340), fill=(200, 210, 230), outline=None); p.text((420, 400), '着信中', 40, fill=INK)
    ringing = u < 0.45
    if ringing:
        for k in range(3):
            r = 90 + k * 40 + 20 * math.sin(u * 40)
            p.d.arc([((420 - r) * S), ((280 - r) * S), ((420 + r) * S), ((280 + r) * S)], 300, 60, fill=ORANGE, width=8)
            p.d.arc([((420 - r) * S), ((280 - r) * S), ((420 + r) * S), ((280 + r) * S)], 120, 240, fill=ORANGE, width=8)
    pr = seg(u, 0.35, 0.45) * (1 - seg(u, 0.5, 0.55))
    p.rect((585 - 8 * pr, 220, 605 - 8 * pr, 320), fill=(255, 160, 60) if pr > 0.2 else (70, 75, 95), outline=None, r=6)
    if 0.25 < u < 0.55: p.text((660, 200), '1回押す', 36, fill=ORANGE, stroke=6)
    p.ell((310, 560, 390, 640), fill=RED, outline=None); p.ell((450, 560, 530, 640), fill=GREEN, outline=None)
    if not ringing: p.badge((420, 480), '音だけ止まる！', GREEN, 48)
    return p.out()

def elevator(u):
    p = Pen()
    p.rect((240, 100, 600, 720), fill=(200, 205, 215), r=24)
    lit = {3: u > 0.1, 5: u > 0.05}
    t1 = seg(u, 0.4, 0.47); t2 = seg(u, 0.52, 0.59)
    if u > 0.55: lit[3] = False
    for k in range(6):
        fl = 6 - k; y = 170 + k * 90
        on = lit.get(fl, False)
        press = (fl == 3) and (t1 * (1 - seg(u, 0.47, 0.5)) > 0 or t2 * (1 - seg(u, 0.59, 0.62)) > 0)
        p.ell((380, y, 460, y + 70), fill=(255, 190, 70) if on else (245, 245, 250), w=5)
        p.text((420, y + 35), str(fl), 34, fill=INK)
        if press: p.ell((450, y + 20, 500, y + 70), fill=(255, 200, 160), outline=None)
    if 0.1 < u < 0.4: p.badge((420, 60), '押し間違えた！', RED, 46)
    elif 0.4 <= u < 0.65: p.text((660, 360), '2回押す', 40, fill=ORANGE, stroke=8)
    elif u >= 0.65: p.badge((420, 60), '取り消し！', GREEN, 52)
    p.text((420, 750), '※一部の機種', 28, fill=(120, 115, 110))
    return p.out()

def roll(u):
    p = Pen()
    p.rect((120, 400, 720, 700), fill=(150, 110, 80), r=30); p.rect((140, 420, 700, 680), fill=(235, 220, 200), outline=None, r=20)
    cols = [(120, 170, 230), (240, 140, 140), (130, 200, 150), (240, 200, 100)]
    for k, c in enumerate(cols):
        a = seg(u, 0.15 + k * 0.15, 0.3 + k * 0.15)
        if a <= 0: continue
        x = 220 + k * 130
        if a < 1:
            w = lerp(220, 110, a); p.rect((x - w / 2, 250, x + w / 2, 250 + lerp(60, 110, a)), fill=c, r=20)
        else:
            p.ell((x - 60, 460, x + 60, 640), fill=c)
            p.d.arc([((x - 35) * S), (500 * S), ((x + 35) * S), (600 * S)], 0, 300, fill=INK, width=6)
    if u < 0.75: p.text((420, 150), 'くるくる巻く', 50, fill=ORANGE, stroke=8)
    else: p.badge((420, 150), 'すっきり収まる！', GREEN, 52)
    return p.out()

def remote(u):
    p = Pen()
    p.rect((90, 300, 330, 680), fill=(60, 65, 80), r=40)
    for k in range(6): p.ell((150 + (k % 2) * 80, 420 + (k // 2) * 70, 200 + (k % 2) * 80, 470 + (k // 2) * 70), fill=(150, 155, 170), outline=None)
    p.ell((180, 310, 240, 340), fill=(30, 30, 40), outline=None)
    press = u > 0.35 and int(u * 14) % 2 == 0
    if press: p.ell((140, 410, 210, 480), fill=(255, 200, 160), outline=None)
    if u < 0.35:
        p.badge((210, 220), '目には見えない…', INK, 40)
    phone_frame(p, 430, 760, 140, 680)
    if u > 0.3:
        p.rect((460, 210, 730, 610), fill=(50, 55, 70), outline=None)
        p.rect((540, 360, 650, 600), fill=(90, 95, 110), outline=None, r=10)
        if press:
            p.ell((570, 340, 620, 390), fill=(230, 180, 255), outline=None)
            gl = Image.new('RGBA', p.im.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse([555 * S, 325 * S, 635 * S, 405 * S], fill=(200, 140, 255, 90)); p.im.alpha_composite(gl)
    if u > 0.45: p.badge((595, 110), 'カメラだと光る！', GREEN, 40)
    return p.out()

FUNCS = [fuel, pulltab, hairpin, shell, thread, wrap, snackbag, chopsticks, hoodie, staple, gtimer, emoji, ctrlbs, calc, backtap, camtext, ring, elevator, roll, remote]
