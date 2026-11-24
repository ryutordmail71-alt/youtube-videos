import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/db'); import dbcontent as C, chara
VERT = len(sys.argv) > 1 and sys.argv[1] == 'short'
W, H = (1080, 1920) if VERT else (1920, 1080); FPS = 30
NF = '/usr/share/fonts/opentype/noto/'; FD = '/home/claude/fonts/'
def Fo(n, s): return ImageFont.truetype(NF + n, s, index=0)
def Fx(n, s): return ImageFont.truetype(FD + n, s)
BK, BD = 'NotoSansCJK-Black.ttc', 'NotoSansCJK-Bold.ttc'
PALE = (240, 236, 226); GREY = (180, 182, 192)
D = json.load(open('/home/claude/db/dur.json'))
PICK = json.load(open('/home/claude/db/dbpick.json'))

def lvcol(db):  # 青→緑→黄→橙→赤→白
    stops = [(0, (90, 170, 255)), (60, (110, 220, 150)), (100, (255, 210, 80)), (130, (255, 140, 60)), (170, (255, 70, 70)), (194, (255, 240, 240))]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if db <= b:
            u = (db - a) / (b - a); return tuple(int(ca[k] + (cb[k] - ca[k]) * u) for k in range(3))
    return stops[-1][1]
def fitf(t, name, size, maxw, fx=False):
    while size > 12:
        f = Fx(name, size) if fx else Fo(name, size)
        if f.getlength(t) <= maxw: return f
        size -= 2
    return f
def cover(path, w, h, blur=0, dark=1.0, fx=0.5, fy=0.5):
    im = Image.open(path).convert('RGB'); s = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * s + 0.5)), max(h, int(im.height * s + 0.5))), Image.LANCZOS)
    x = int((im.width - w) * fx); y = int((im.height - h) * fy); im = im.crop((x, y, x + w, y + h))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark != 1.0: im = ImageEnhance.Brightness(im).enhance(dark)
    return im
def contain(path, w, h):
    im = Image.open(path).convert('RGB'); s = min(w / im.width, h / im.height)
    fg = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    bg = cover(path, w, h, blur=24, dark=0.45); bg.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2)); return bg

# ---------- レイアウト ----------
if VERT:
    CARD = (60, 300, 960, 620); CHAR_C = (300, 1560); CHAR_S = 400; BUB = (520, 1210, 1040, 1420); NUM = (W // 2, 1060); METER = (80, 1840, 1000)
else:
    CARD = (1080, 160, 770, 470); CHAR_C = (330, 760); CHAR_S = 440; BUB = (600, 560, 1050, 780); NUM = (90, 170); METER = (620, 1040, 1830)

def topbar(im, title='声をどんどん大きくしたら？', en='What happens as the decibels keep rising?'):
    d = ImageDraw.Draw(im, 'RGBA')
    if VERT:
        d.rectangle((0, 0, W, 260), fill=(10, 12, 20, 235))
        d.text((W / 2, 70), '検証', font=Fo(BK, 40), fill=(255, 210, 80), anchor='mm')
        d.text((W / 2, 150), title, font=fitf(title, BK, 84, 1000), fill=PALE, anchor='mm')
        d.text((W / 2, 222), en, font=fitf(en, BD, 30, 1000), fill=GREY, anchor='mm')
    else:
        d.rectangle((0, 0, W, 110), fill=(10, 12, 20, 230))
        d.rounded_rectangle((40, 30, 140, 80), 10, fill=(255, 210, 80)); d.text((90, 55), '検証', font=Fo(BK, 34), fill=(20, 20, 30), anchor='mm')
        d.text((165, 52), title, font=Fo(BK, 52), fill=PALE, anchor='lm')
        d.text((W - 40, 40), en, font=Fo(BD, 26), fill=GREY, anchor='rm')
        d.text((W - 40, 80), '※音量は演出です（実際の大きさではありません）', font=Fo(BD, 22), fill=(200, 200, 205), anchor='rm')
    return im

def base_level(l, i, extra=None):
    db = l['db']; col = lvcol(db); p = PICK[l['photo']][0]
    im = cover(p['file'], W, H, blur=22, dark=0.32)
    tint = Image.new('RGB', (W, H), col); im = Image.blend(im, tint, 0.10)
    # 写真カード
    x, y, w, h = CARD
    card = contain(p['file'], w, h); im.paste(card, (x, y))
    d = ImageDraw.Draw(im, 'RGBA'); d.rectangle((x - 4, y - 4, x + w + 3, y + h + 3), outline=col + (255,), width=4)
    cr = f"Image: {p['artist']} / {p['lic']} / Wikimedia Commons"
    d.text((x + w, y + h + 18), cr, font=fitf(cr, BD, 18, w), fill=(190, 190, 195), anchor='rm')
    comp, comp_en = (extra or l)['comp'], (extra or l)['comp_en']
    if VERT:
        d.text((W / 2, y + h + 80), comp, font=fitf(comp, BK, 60, 980), fill=PALE, anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((W / 2, y + h + 140), comp_en, font=fitf(comp_en, BD, 30, 980), fill=GREY, anchor='mm')
    else:
        d.text((x, y + h + 70), '≒ ' + comp, font=fitf('≒ ' + comp, BK, 56, w), fill=PALE, anchor='lm', stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((x + 4, y + h + 122), comp_en, font=fitf(comp_en, BD, 28, w), fill=GREY, anchor='lm')
    return topbar(im)

def draw_num(im, val, col, eff=None, eff_en=None, label=None):
    d = ImageDraw.Draw(im, 'RGBA'); s = f'{val:.0f}'
    if VERT:
        f = Fx('BebasNeue-Regular.ttf', 230); wn = f.getlength(s); fu = Fx('BebasNeue-Regular.ttf', 110)
        x0 = W / 2 - (wn + 20 + fu.getlength('dB')) / 2; y = NUM[1]
        d.text((x0, y), s, font=f, fill=col, anchor='ls', stroke_width=6, stroke_fill=(0, 0, 0))
        d.text((x0 + wn + 20, y), 'dB', font=fu, fill=PALE, anchor='ls', stroke_width=4, stroke_fill=(0, 0, 0))
        if eff:
            d.text((W / 2, y + 60), eff, font=fitf(eff, BK, 58, 1000), fill=col, anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
            d.text((W / 2, y + 115), eff_en, font=fitf(eff_en, BD, 28, 1000), fill=PALE, anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0))
    else:
        x, y = NUM; f = Fx('BebasNeue-Regular.ttf', 270); wn = f.getlength(s)
        if label: d.text((x + 6, y - 10), label, font=Fo(BK, 30), fill=PALE, anchor='ls', stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((x, y + 240), s, font=f, fill=col, anchor='ls', stroke_width=7, stroke_fill=(0, 0, 0))
        d.text((x + wn + 18, y + 240), 'dB', font=Fx('BebasNeue-Regular.ttf', 120), fill=PALE, anchor='ls', stroke_width=4, stroke_fill=(0, 0, 0))
        if eff:
            d.text((x + 4, y + 300), eff, font=fitf(eff, BK, 54, 900), fill=col, anchor='lm', stroke_width=4, stroke_fill=(0, 0, 0))
            d.text((x + 6, y + 352), eff_en, font=fitf(eff_en, BD, 26, 900), fill=PALE, anchor='lm', stroke_width=2, stroke_fill=(0, 0, 0))

def meter(im, val):
    d = ImageDraw.Draw(im, 'RGBA'); x0, y, x1 = METER; h = 16
    d.rounded_rectangle((x0, y, x1, y + h), 8, fill=(255, 255, 255, 40))
    fx = x0 + (x1 - x0) * min(1, val / 200)
    for k in range(int(x0), int(fx), 6): d.rectangle((k, y, min(k + 5, fx), y + h), fill=lvcol((k - x0) / (x1 - x0) * 200))
    for t in range(0, 201, 20):
        tx = x0 + (x1 - x0) * t / 200; d.line((tx, y + h + 4, tx, y + h + 12), fill=(220, 220, 220), width=2)
        d.text((tx, y - 8), str(t), font=Fo(BD, 18 if not VERT else 22), fill=(220, 220, 225), anchor='mb')
    tx = x0 + (x1 - x0) * 194 / 200; d.line((tx, y - 4, tx, y + h + 4), fill=(255, 255, 255), width=3)

CH = {}
def char_img(mouth, eyes, sweat=False, ear=False, size=CHAR_S):
    k = (round(mouth, 1), eyes, sweat, ear, size)
    if k not in CH: CH[k] = chara.draw(size, mouth=round(mouth, 1), eyes=eyes, sweat=sweat, hands_ear=ear)
    return CH[k]
def put_char(im, c, dx=0, dy=0, scale=1.0):
    if scale != 1.0: c = c.resize((int(c.width * scale), int(c.height * scale)), Image.BILINEAR)
    cx, by = CHAR_C if not VERT else CHAR_C
    im.paste(c, (int(cx - c.width / 2 + dx), int(by - c.height * 0.55 + dy)), c)

def bubble(im, word, db, u):
    """吹き出し。u: 0→1 出現アニメ"""
    x0, y0, x1, y1 = BUB; col = lvcol(db)
    s = 0.6 + 0.4 * min(1, u * 3)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; w, h = (x1 - x0) * s, (y1 - y0) * s
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if db >= 110:  # ギザギザ吹き出し
        pts = []
        for k in range(28):
            a = 2 * math.pi * k / 28; r = 1.0 if k % 2 == 0 else 0.82
            pts.append((cx + w / 2 * r * math.cos(a), cy + h / 2 * r * math.sin(a)))
        d.polygon(pts, fill=(255, 255, 255), outline=(20, 20, 20))
    else:
        d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(40 * s), fill=(255, 255, 255), outline=(20, 20, 20), width=4)
    # しっぽ
    tx, ty = (CHAR_C[0] + 110, CHAR_C[1] - 60) if not VERT else (CHAR_C[0] + 120, CHAR_C[1] - 120)
    d.polygon([(cx - w * 0.3, cy + h * 0.28), (cx - w * 0.12, cy + h * 0.38), (tx, ty)], fill=(255, 255, 255))
    size = int((46 + 66 * min(1, db / 150)) * s); f = fitf(word, 'RocknRollOne-Regular.ttf', size, w * 0.8, fx=True)
    tc = (40, 40, 60) if db < 110 else (220, 40, 40)
    d.text((cx, cy), word, font=f, fill=tc, anchor='mm', stroke_width=2 if db >= 110 else 0, stroke_fill=(120, 0, 0))
    im.alpha_composite(lay) if im.mode == 'RGBA' else im.paste(lay, (0, 0), lay)

def lines(im, db, t):
    """叫び中の集中線・衝撃リング"""
    if db < 80: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy = CHAR_C[0], CHAR_C[1] - 40; n = int(10 + 30 * db / 194); rng = np.random.default_rng(int(t * 30))
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(250, 380); r1 = r0 + rng.uniform(120, 420)
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)), fill=(255, 255, 255, int(60 + 120 * db / 194)), width=int(2 + 4 * db / 194))
    if db >= 150:
        R = 200 + 1400 * ((t * 1.6) % 1.0)
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(255, 255, 255, int(200 * (1 - (t * 1.6) % 1.0))), width=10)
    im.paste(lay, (0, 0), lay)

def cracks(im, db, seed):
    if db < 150: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rng = np.random.default_rng(seed)
    n = 4 if db < 180 else 9
    for k in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H); pts = [(x, y)]
        for j in range(7): x += rng.uniform(-120, 120); y += rng.uniform(-120, 120); pts.append((x, y))
        d.line(pts, fill=(255, 255, 255, 170), width=3)
    im.paste(lay, (0, 0), lay)

# ---------- タイムライン ----------
EV = []  # (start, key) 音声配置
SEG = []  # (start, end, kind, data)
t = 0.0
def add(kind, dur, **kw):
    global t; SEG.append((t, t + dur, kind, kw)); t += dur
if VERT:
    SP = [3, 7, 9, 10, 11]  # 60,120,150,180,194 のインデックス
    VIDX = [3, 7, 9, 10, 11]
else:
    VIDX = list(range(len(C.L)))
# イントロ
EV.append((0.3, 'hook')); add('intro', (0.3 + D['hook'] + 0.4 + D['intro'] + 0.6) if not VERT else (0.3 + D['hook'] + 0.3 + D.get('vhook', 0) + 0.4))
if not VERT: EV.append((0.3 + D['hook'] + 0.4, 'intro'))
else: EV.append((0.3 + D['hook'] + 0.3, 'vhook'))
prev = 0
for i in VIDX:
    l = C.L[i]; s0 = t
    roll = 0.7
    EV.append((s0 + roll, f's{i}'))
    nk = f'n{i}' if not VERT else f'v{i}'
    EV.append((s0 + roll + D[f's{i}'] + 0.25, nk))
    add('level', roll + D[f's{i}'] + 0.25 + D[nk] + 0.5, i=i, prev=prev, roll=roll, sd=D[f's{i}'])
    prev = l['db']
# クラカタウ
kk = 'kraka' if not VERT else 'vcta'
EV.append((t + 0.6, kk)); add('kraka', 0.6 + D[kk] + 0.8)
if not VERT:
    EV.append((t + 0.3, 'end')); EV.append((t + 0.3 + D['end'] + 0.5, 'outro')); add('outro', 0.3 + D['end'] + 0.5 + D['outro'] + 1.0)
TOTAL = t
json.dump(EV, open('/home/claude/db/events_%s.json' % ('v' if VERT else 'h'), 'w'))

# ---------- 静的レイヤーのキャッシュ ----------
BASE = {}
def get_base(kind, i=None):
    k = (kind, i)
    if k in BASE: return BASE[k]
    if kind == 'level': b = base_level(C.L[i], i)
    elif kind == 'kraka': b = base_level(dict(C.KRAKA, db=194), 0, extra=C.KRAKA)
    else:
        p = PICK['11'][0] if kind == 'intro' else PICK['12'][0]
        b = cover(p['file'], W, H, blur=26, dark=0.3); b = topbar(b)
    BASE[k] = b.convert('RGBA'); return BASE[k]

def frame(tt):
    for s, e, kind, kw in SEG:
        if s <= tt < e: break
    lt = tt - s
    if kind == 'intro':
        im = get_base('intro').copy(); d = ImageDraw.Draw(im)
        if VERT:
            d.text((W / 2, 520), '声をどんどん', font=Fo(BK, 120), fill=PALE, anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0))
            d.text((W / 2, 680), '大きくしたら？', font=Fo(BK, 130), fill=(255, 210, 80), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0))
            d.text((W / 2, 800), '0dB → 194dB', font=Fx('BebasNeue-Regular.ttf', 110), fill=PALE, anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
        else:
            d.text((W / 2 + 200, 380), '声をどんどん', font=Fo(BK, 120), fill=PALE, anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0))
            d.text((W / 2 + 200, 540), '大きくしたら？', font=Fo(BK, 140), fill=(255, 210, 80), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0))
            d.text((W / 2 + 200, 690), '0dB → 194dB  どこまで耐えられる？', font=Fo(BK, 52), fill=PALE, anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
            d.text((W / 2 + 200, 760), 'What happens as the decibels keep rising?', font=Fo(BD, 30), fill=GREY, anchor='mm')
        sp = 0.3 <= lt < 0.3 + D['hook']
        c = char_img(0.25 if sp and int(lt * 8) % 2 == 0 else 0.0, 'closed' if sp else 'normal')
        put_char(im, c, dy=6 * math.sin(lt * 3))
        if sp or lt < 0.3 + D['hook'] + 1.0: bubble(im, C.HOOK_WORD, 10, min(1, (lt - 0.3) * 2))
        meter(im, 0)
        return im
    if kind == 'level':
        i = kw['i']; l = C.L[i]; db = l['db']; col = lvcol(db); roll, sd = kw['roll'], kw['sd']
        im = get_base('level', i).copy()
        u = min(1, lt / roll); val = kw['prev'] + (db - kw['prev']) * (1 - (1 - u) ** 3)
        shouting = roll <= lt < roll + sd
        after = lt >= roll + sd
        # 揺れ
        amp = 0 if not shouting else (db / 194) ** 2 * 38
        sx = amp * math.sin(lt * 71) ; sy = amp * math.cos(lt * 53)
        if shouting and db >= 100:
            fl = Image.new('RGBA', (W, H), col + (int(70 * (db - 90) / 104 * max(0, 1 - (lt - roll) * 2.5)),)); im.alpha_composite(fl)
            lines(im, db, lt)
        if after: cracks(im, db, i)
        draw_num(im, val, col if u >= 1 else lvcol(val), l['eff'] if after else None, l['eff_en'] if after else None)
        if shouting:
            ph = (lt - roll) / sd; m = (0.25 + 0.75 * min(1, db / 140)) * (0.85 + 0.15 * math.sin(lt * 40))
            if db < 40: m = 0.18 if int(lt * 10) % 2 == 0 else 0.08
            eyes = 'closed' if db < 60 else ('normal' if db < 100 else 'squint')
            c = char_img(m, eyes); put_char(im, c, sx, sy - 10, 1.0 + 0.12 * (db / 194))
        else:
            if db >= 150: c = char_img(0.15, 'dizzy', sweat=True)
            elif db >= 110: c = char_img(0.0, 'squint', sweat=True, ear=True)
            elif db >= 80: c = char_img(0.0, 'normal', sweat=True)
            else: c = char_img(0.0, 'normal')
            put_char(im, c, 0, 5 * math.sin(lt * 3))
        if lt >= roll: bubble(im, l['word'], db, (lt - roll))
        meter(im, val)
        return im.convert('RGB') if False else im
    if kind == 'kraka':
        im = get_base('kraka').copy(); col = (255, 120, 60)
        draw_num(im, 172, col, C.KRAKA['eff'], C.KRAKA['eff_en'], label='160km離れていても' if not VERT else None)
        c = char_img(0.3, 'wide', sweat=True); put_char(im, c, 0, 4 * math.sin(lt * 5), 0.9)
        meter(im, 172)
        return im
    if kind == 'outro':
        im = get_base('outro').copy(); d = ImageDraw.Draw(im)
        endd = 0.3 + D['end']
        if lt < endd + 0.5:
            c = char_img(0.15 if (0.3 < lt < endd and int(lt * 6) % 2 == 0) else 0.0, 'dizzy', sweat=True); put_char(im, c, 0, 0)
            bubble(im, C.END_WORD, 20, max(0, lt - 0.3))
        else:
            c = char_img(0.0, 'normal'); put_char(im, c, 0, 5 * math.sin(lt * 3))
            d.text((W / 2 + 230, 330), 'あなたは何dBまで出せる？', font=Fo(BK, 66), fill=PALE, anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0))
            d.text((W / 2 + 230, 410), 'コメントで教えてください', font=Fo(BK, 44), fill=(255, 210, 80), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
            d.rounded_rectangle((W / 2 - 160, 520, W / 2 + 620, 760), 24, fill=(10, 12, 20, 220), outline=(255, 210, 80), width=4)
            d.text((W / 2 + 230, 570), '次に見るなら', font=Fo(BD, 34), fill=GREY, anchor='mm')
            d.text((W / 2 + 230, 650), '地球史上ヤバすぎる', font=Fo(BK, 60), fill=PALE, anchor='mm')
            d.text((W / 2 + 230, 720), '大災害ランキング', font=Fo(BK, 60), fill=(255, 210, 80), anchor='mm')
        return im

def credits_lines():
    out = []
    for k in sorted(PICK, key=int):
        for p in PICK[k][:1]: out.append(f"{p['title']} — {p['artist']} / {p['lic']} / Wikimedia Commons")
    return out

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'test':
        S = '/tmp/claude-0/-home-claude/3f2fb178-41da-56af-8da6-007907094230/scratchpad/'
        ts = [float(x) for x in sys.argv[3].split(',')]
        for k, x in enumerate(ts): frame(x).convert('RGB').save(S + f'dbt{k}.jpg', quality=85)
        print('TOTAL', TOTAL); sys.exit()
    out = '/home/claude/db/%s_video.mp4' % ('v' if VERT else 'h')
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    n = int(TOTAL * FPS)
    for f in range(n):
        p.stdin.write(frame(f / FPS).convert('RGB').tobytes())
        if f % 300 == 0: print(f, n, flush=True)
    p.stdin.close(); p.wait(); print('total', TOTAL)
