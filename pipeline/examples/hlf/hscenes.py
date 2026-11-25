"""人間の一生を数字にすると？（本編の場面）"""
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 30
G = '/home/claude/hlf'
D = json.load(open(f'{G}/dur.json'))
NOTO = '/usr/share/fonts/opentype/noto/'
def Fo(s): return ImageFont.truetype(NOTO + 'NotoSansCJK-Black.ttc', s, index=0)
def Fb(s): return ImageFont.truetype(NOTO + 'NotoSansCJK-Bold.ttc', s, index=0)
def Mi(s): return ImageFont.truetype(NOTO + 'NotoSerifCJK-Black.ttc', s, index=0)
def BE(s): return ImageFont.truetype('/home/claude/fonts/BebasNeue-Regular.ttf', s)
PALE = (245, 240, 230); GOLD = (255, 210, 80); RED = (240, 90, 90); BLUE = (120, 190, 255); GREEN = (140, 220, 130); GRAY = (200, 200, 205)
DISC = '※実データをもとにした、単純化したシミュレーションです（数値は目安）'

def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))
def ease(u): u = fade(u); return 1 - (1 - u) ** 3
_BG = {}
def bg(w=W, h=H, tint=(16, 20, 34)):
    k = (w, h, tint)
    if k not in _BG:
        y = np.linspace(0, 1, h)[:, None, None]; c0 = np.array(tint, float); c1 = c0 * 0.45
        a = (c0 * (1 - y) + c1 * y) * np.ones((1, w, 1))
        rng = np.random.default_rng(3); im = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
        for _ in range(int(w * h / 9000)):
            x, yy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(0.6, 1.8); al = int(rng.uniform(30, 110))
            d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 255, 255, al))
        _BG[k] = im
    return _BG[k].copy()
def disc(d, w=W, h=H):
    d.text((w - 24, h - 20), DISC, font=Fb(20 if w > h else 24), fill=(215, 215, 220), anchor='rs')
def jnum(v):
    """大きな数を「31億」「4億4000万」のように"""
    if v >= 1e8:
        o = int(v // 1e8); m = int((v - o * 1e8) // 1e4)
        return f'{o}億' + (f'{m:,}万' if m >= 1 else '')
    if v >= 1e4: return f'{int(v // 1e4):,}万' + (f'{int(v % 1e4):,}' if v < 1e5 and v % 1e4 >= 1 else '')
    return f'{int(v):,}'

# 一生の数字（目安）
LIFE = 84.0; YEAR_S = 365.25 * 86400
HB = 70 * 60 * 24 * 365.25 * LIFE              # 心拍
BR = 15 * 60 * 24 * 365.25 * LIFE              # 呼吸
BL = 15 * 60 * 16 * 365.25 * LIFE              # まばたき（起きている16時間）
BLINK_Y = BL * 0.1 / YEAR_S                    # まばたきで目を閉じている年数
SLEEP_Y = 7.33 / 24 * LIFE                     # 睡眠
BLOOD_L = HB * 0.07                            # 心臓が送る血（L）
POOLS = BLOOD_L / 1000 / 375                   # 25mプール（375m³）
FOOD_T = 1.5 * 365.25 * LIFE / 1000            # 食べ物（t）
WALK_KM = 4.2 * 365.25 * (LIFE - 1)            # 1歳から歩く
HAIR_M = 0.01 * 12 * LIFE; NAIL_M = 0.003 * 12 * LIFE

def heart(d, x, y, r, col, beat=0.0):
    r = r * (1 + 0.18 * beat)
    d.ellipse((x - r, y - r * 0.6, x, y + r * 0.35), fill=col); d.ellipse((x, y - r * 0.6, x + r, y + r * 0.35), fill=col)
    d.polygon([(x - r * 0.97, y - r * 0.05), (x + r * 0.97, y - r * 0.05), (x, y + r * 1.05)], fill=col)
def person(d, x, y, h, col=(235, 225, 210), age=30):
    """足元 (x,y)、高さ h の人。年齢で体の比率を少し変える"""
    k = min(1.0, max(0.35, age / 18)) if age < 18 else 1.0
    hh = h * (0.55 + 0.45 * k); head = hh * (0.2 if age < 6 else 0.14)
    bend = max(0, (age - 65) / 20) * 0.12 * hh
    d.ellipse((x - head / 2 + bend, y - hh, x + head / 2 + bend, y - hh + head), fill=col)
    d.line((x + bend, y - hh + head, x, y - hh * 0.45), fill=col, width=max(3, int(hh * 0.1)))
    d.line((x, y - hh * 0.45, x - hh * 0.12, y), fill=col, width=max(3, int(hh * 0.08))); d.line((x, y - hh * 0.45, x + hh * 0.12, y), fill=col, width=max(3, int(hh * 0.08)))
    d.line((x + bend, y - hh * 0.75, x - hh * 0.16, y - hh * 0.5), fill=col, width=max(2, int(hh * 0.06))); d.line((x + bend, y - hh * 0.75, x + hh * 0.16, y - hh * 0.5), fill=col, width=max(2, int(hh * 0.06)))
    if age > 65: d.line((x + hh * 0.2, y - hh * 0.5, x + hh * 0.24, y), fill=(160, 120, 80), width=max(2, int(hh * 0.03)))
def truck(d, x, y, s, col=(230, 120, 60)):
    d.rectangle((x, y - s * 0.55, x + s * 0.72, y), fill=col); d.rectangle((x + s * 0.74, y - s * 0.4, x + s, y), fill=(200, 205, 215))
    d.rectangle((x + s * 0.8, y - s * 0.34, x + s * 0.95, y - s * 0.22), fill=(120, 170, 220))
    for wx in (x + s * 0.15, x + s * 0.55, x + s * 0.86): d.ellipse((wx - s * 0.08, y - s * 0.08, wx + s * 0.08, y + s * 0.08), fill=(30, 30, 34))
def pool(d, x, y, w, h):
    d.rectangle((x, y, x + w, y + h), fill=(60, 150, 220)); d.rectangle((x, y, x + w, y + h), outline=(220, 235, 245), width=max(1, int(w / 30)))

def scene(out, dur, draw, cues):
    n = int(dur * FPS); p = writer(f'{G}/{out}')
    for f in range(n):
        im = bg(); d = ImageDraw.Draw(im); draw(im, d, f / FPS); disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, cues

def s_title():
    dur = 0.6 + D['intro'] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.6)
        d.rounded_rectangle((W / 2 - 230, 150, W / 2 + 230, 205), 27, fill=(0, 0, 0, 170)); ctext(d, (W / 2, 178), '実データでシミュレーション', Fb(30), GOLD)
        ctext(d, (W / 2, 340), 'あなたの一生を', Mi(int(96 * (1.2 - 0.2 * u))), PALE, sw=4)
        ctext(d, (W / 2, 480), '数字にすると？', Mi(int(150 * (1.2 - 0.2 * u))), GOLD, sw=5)
        ctext(d, (W / 2, 590), 'YOUR LIFE IN NUMBERS', Fb(30), GRAY)
        if t > 1.2:
            for i, (lab, val) in enumerate([('心臓', '？回'), ('食べる量', '？トン'), ('歩く距離', '？km')]):
                x = W / 2 + (i - 1) * 460; uu = ease((t - 1.2 - i * 0.4) / 0.5)
                d.rounded_rectangle((x - 200, 700, x + 200, 900), 24, fill=(10, 12, 20, int(220 * uu)), outline=GOLD, width=3)
                ctext(d, (x, 760), lab, Fo(44), PALE); ctext(d, (x, 840), val, Fo(64), GOLD)
    return scene('c_title.mp4', dur, dr, [(0.6, 'intro')])

def s_rule():
    dur = 0.5 + D['rule'] + 0.6; dd = D['rule']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 150), '人生は何年？', Mi(76), PALE, sw=3)
        rows = [(0.05, '男性の平均寿命', '81.09年'), (0.2, '女性の平均寿命', '87.13年'), (0.42, 'この動画では', '84年')]
        for i, (tr, a, b) in enumerate(rows):
            if u < tr: continue
            y = 300 + i * 130; hl = i == 2
            d.rounded_rectangle((420, y, W - 420, y + 105), 18, fill=(10, 12, 20, 225), outline=GOLD if hl else None, width=4 if hl else 0)
            d.text((470, y + 52), a, font=Fo(42), fill=GRAY, anchor='lm'); d.text((W - 470, y + 52), b, font=Fo(60), fill=GOLD if hl else PALE, anchor='rm')
        if u > 0.62:
            v = 2.65e9 * ease((u - 0.62) / 0.25)
            ctext(d, (W / 2, 790), '84年 ＝', Fo(50), GRAY); ctext(d, (W / 2, 890), f'約{jnum(v)}秒' if v > 1e8 else f'{int(v):,}秒', Fo(96), GOLD, sw=3)
        d.text((24, H - 20), '平均寿命：厚生労働省「令和6年簡易生命表」', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('c_rule.mp4', dur, dr, [(0.5, 'rule')])

COUNTERS = [('心臓', HB, '回', RED), ('呼吸', BR, '回', BLUE), ('まばたき', BL, '回', GREEN), ('眠った時間', SLEEP_Y, '年', (190, 160, 255)), ('食べた量', FOOD_T, 'トン', (255, 160, 90)), ('歩いた距離', WALK_KM, 'km', GOLD)]
def fmt(v, unit):
    if unit == '回': return jnum(v) + '回'
    if unit == '年': return f'{v:.1f}年'
    if unit == 'トン': return f'{v:.1f}トン'
    return f'{v:,.0f}km'
def s_run():
    t1 = 0.4; t2 = t1 + D['run1'] + 0.3; t3 = t2 + D['run2'] + 0.3; dur = t3 + D['run3'] + 1.8
    T0, T1 = t1 + 0.5, t3 + D['run3'] - 0.6
    def age_at(t): return LIFE * (ease((t - T0) / (T1 - T0)) * 0.15 + 0.85 * fade((t - T0) / (T1 - T0)))
    def dr(im, d, t):
        a = age_at(t); fr = a / LIFE
        ctext(d, (W / 2, 80), '人生84年を早送り', Mi(56), PALE, sw=3)
        d.rounded_rectangle((120, 150, W - 120, 200), 25, fill=(255, 255, 255, 30))
        if fr > 0: d.rounded_rectangle((120, 150, 120 + (W - 240) * fr, 200), 25, fill=GOLD)
        for yy in range(0, 85, 10):
            x = 120 + (W - 240) * yy / LIFE; d.text((x, 215), f'{yy}', font=Fb(22), fill=GRAY, anchor='mt')
        ctext(d, (330, 520), f'{int(a)}歳', BE(150) if False else Fo(120), GOLD, sw=3)
        person(d, 330, 860, 300, age=a)
        for i, (lab, tot, unit, col) in enumerate(COUNTERS):
            x0 = 650 + (i % 2) * 610; y0 = 300 + (i // 2) * 230
            d.rounded_rectangle((x0, y0, x0 + 580, y0 + 200), 22, fill=(10, 12, 20, 220), outline=col, width=3)
            d.text((x0 + 30, y0 + 45), lab, font=Fo(40), fill=col, anchor='lm')
            d.text((x0 + 550, y0 + 135), fmt(tot * fr, unit), font=Fo(64), fill=PALE, anchor='rm')
        if a >= LIFE - 0.01 and t > T1 + 0.2: ctext(d, (330, 300), 'ゴール！', Fo(70), GOLD, sw=3)
    return scene('c_run.mp4', dur, dr, [(t1, 'run1'), (t2, 'run2'), (t3, 'run3')])

def s_heart():
    dur = 0.5 + D['heart'] + 0.8; dd = D['heart']
    def dr(im, d, t):
        u = (t - 0.5) / dd; ph = (t * 70 / 60) % 1; beat = math.exp(-ph * 10)
        ctext(d, (W / 2, 90), '① 心臓', Mi(70), RED, sw=3)
        heart(d, 420, 470, 190, (220, 50, 60), beat)
        ctext(d, (420, 760), '1分間に 約70回', Fo(46), PALE)
        v = HB * ease((u - 0.12) / 0.3) if u > 0.12 else 0
        ctext(d, (1250, 330), '一生で', Fo(44), GRAY); ctext(d, (1250, 440), ('約31億回' if v >= HB * 0.995 else f'約{jnum(v)}回') if v else '…', Fo(110), GOLD, sw=3)
        if u > 0.5:
            ctext(d, (1250, 590), '送り出す血（1回 約70mL）', Fo(40), GRAY)
            k = int(min(1, (u - 0.55) / 0.3) * 58)
            for i in range(k):
                x = 860 + (i % 12) * 66; y = 650 + (i // 12) * 52; pool(d, x, y, 58, 36)
            if u > 0.86: ctext(d, (1250, 950), '＝ 25mプール 約580杯ぶん', Fo(56), BLUE, sw=2)
            d.text((1640, 925), '（1マス＝10杯）', font=Fb(22), fill=GRAY, anchor='ls')
    return scene('c_heart.mp4', dur, dr, [(0.5, 'heart')])

def eye(d, x, y, r, open_=1.0):
    h = r * 0.55 * open_
    d.ellipse((x - r, y - max(2, h), x + r, y + max(2, h)), fill=(240, 240, 245))
    if open_ > 0.15: d.ellipse((x - r * 0.38, y - min(h, r * 0.38), x + r * 0.38, y + min(h, r * 0.38)), fill=(70, 120, 180)); d.ellipse((x - r * 0.15, y - min(h, r * 0.15), x + r * 0.15, y + min(h, r * 0.15)), fill=(10, 10, 14))
    d.line((x - r, y, x + r, y), fill=(30, 30, 36), width=3) if open_ <= 0.15 else None
def s_breath():
    t1 = 0.5; t2 = t1 + D['breath'] + 0.6; dur = t2 + D['blink'] + 0.8
    def dr(im, d, t):
        if t < t2 - 0.2:
            u = (t - t1) / D['breath']
            ctext(d, (W / 2, 90), '② 呼吸とまばたき', Mi(70), BLUE, sw=3)
            for i, (lab, tot, col, tr, ic) in enumerate([('呼吸（1分に約15回）', BR, BLUE, 0.0, 'lung'), ('まばたき（1分に約15回）', BL, GREEN, 0.45, 'eye')]):
                if u < tr: continue
                x = W / 4 + i * W / 2; v = tot * ease((u - tr) / 0.3)
                if ic == 'eye': eye(d, x, 380, 130, 1.0 if (t * 0.25) % 1 > 0.08 else 0.0)
                else:
                    s = 1 + 0.12 * math.sin(t * 2 * math.pi * 15 / 60)
                    d.ellipse((x - 150 * s, 270, x - 20, 500), fill=(240, 150, 160)); d.ellipse((x + 20, 270, x + 150 * s, 500), fill=(240, 150, 160)); d.line((x, 230, x, 330), fill=(240, 220, 225), width=14)
                ctext(d, (x, 610), lab, Fo(42), col); ctext(d, (x, 740), f'約{jnum(v)}回', Fo(96), PALE, sw=2)
                ctext(d, (x, 830), '一生で', Fo(36), GRAY)
        else:
            u = (t - t2) / D['blink']
            ctext(d, (W / 2, 90), 'まばたきで目を閉じている時間', Mi(64), GREEN, sw=3)
            eye(d, W / 2, 330, 160, 0.0 if (t * 0.8) % 1 < 0.12 else 1.0)
            if u > 0.2: ctext(d, (W / 2, 560), '1回 約0.1秒 × 約4億4000万回', Fo(50), GRAY)
            if u > 0.45:
                v = BLINK_Y * ease((u - 0.45) / 0.25)
                ctext(d, (W / 2, 720), f'＝ 約{v:.1f}年', Fo(140), GOLD, sw=4)
            if u > 0.75: ctext(d, (W / 2, 880), '人は、まばたきだけで1年半近くも目を閉じている！', Mi(54), PALE, sw=3)
    return scene('c_breath.mp4', dur, dr, [(t1, 'breath'), (t2, 'blink')])

def s_sleep():
    dur = 0.5 + D['sleep'] + 0.8; dd = D['sleep']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 90), '③ 眠っている時間', Mi(70), (190, 160, 255), sw=3)
        ctext(d, (W / 2, 220), '日本人の睡眠：1日 約7時間20分', Fo(44), GRAY)
        x0, x1, y = 160, W - 160, 420; L = (x1 - x0)
        d.rounded_rectangle((x0, y, x1, y + 140), 20, fill=(70, 80, 100))
        g = ease((u - 0.3) / 0.3); xs = x0 + L * SLEEP_Y / LIFE * g
        if g > 0: d.rounded_rectangle((x0, y, xs, y + 140), 20, fill=(150, 120, 240))
        d.text((x1, y + 180), '人生 84年', font=Fo(40), fill=GRAY, anchor='ra')
        if g > 0.3: d.text((x0 + 20, y + 70), f'眠り {SLEEP_Y * g:.0f}年', font=Fo(60), fill=(255, 255, 255), anchor='lm')
        if u > 0.65: ctext(d, (W / 2, 800), '人生の約3分の1は、眠っている！', Mi(66), GOLD, sw=3)
        d.text((24, H - 20), '睡眠時間：OECD「Gender data portal」などの日本の平均（目安）', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('c_sleep.mp4', dur, dr, [(0.5, 'sleep')])

def s_food():
    t1 = 0.5; t2 = t1 + D['food'] + 0.5; dur = t2 + D['walk'] + 0.8
    def dr(im, d, t):
        if t < t2 - 0.2:
            u = (t - t1) / D['food']
            ctext(d, (W / 2, 90), '④ 食べる量', Mi(70), (255, 160, 90), sw=3)
            ctext(d, (W / 2, 220), '食べ物：1日 約1.5kg', Fo(44), GRAY)
            v = FOOD_T * ease((u - 0.25) / 0.3) if u > 0.25 else 0
            ctext(d, (W / 2, 360), f'一生で 約{v:.0f}トン', Fo(100), GOLD, sw=3)
            k = int(min(5, max(0, (u - 0.55) / 0.35 * 5 + 0.5)))
            for i in range(k): truck(d, 200 + i * 320, 760, 280)
            if u > 0.85: ctext(d, (W / 2, 900), '10トントラック 約5台ぶん！', Mi(60), PALE, sw=3)
        else:
            u = (t - t2) / D['walk']
            ctext(d, (W / 2, 90), '⑤ 歩く距離', Mi(70), GOLD, sw=3)
            ctext(d, (W / 2, 210), '1日 約6000歩（約4.2km）', Fo(44), GRAY)
            cx, cy, r = 620, 640, 260
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 100, 170));
            for (a, b, w_, h_) in [(-120, -60, 150, 110), (40, -120, 120, 160), (-60, 80, 170, 90), (110, 60, 90, 120)]:
                d.ellipse((cx + a - w_ / 2, cy + b - h_ / 2, cx + a + w_ / 2, cy + b + h_ / 2), fill=(80, 160, 90))
            laps = WALK_KM / 40000 * ease((u - 0.3) / 0.45)
            for k in range(int(math.ceil(laps))):
                frac = min(1, laps - k); rr = r + 30 + k * 34
                d.arc((cx - rr, cy - rr, cx + rr, cy + rr), -90, -90 + 360 * frac, fill=GOLD, width=12)
            ctext(d, (1360, 520), f'約{WALK_KM * ease((u - 0.3) / 0.45) / 1e4:.1f}万km', Fo(100), PALE, sw=3)
            if u > 0.75: ctext(d, (1360, 690), '地球 約3周！', Mi(84), GOLD, sw=3)
    return scene('c_food.mp4', dur, dr, [(t1, 'food'), (t2, 'walk')])

def s_hair():
    dur = 0.5 + D['hair'] + 0.8; dd = D['hair']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 90), '⑥ 髪の毛と爪', Mi(70), PALE, sw=3)
        ctext(d, (W / 2, 210), '髪：1か月に約1cm　／　一度も切らなかったら？', Fo(42), GRAY)
        x0 = 160; ppm = 150; y = 560
        d.rounded_rectangle((x0, y - 170, x0 + 10.5 * ppm, y), 24, fill=(60, 140, 90));
        for i in range(8): d.rectangle((x0 + 60 + i * 180, y - 140, x0 + 180 + i * 180, y - 80), fill=(190, 220, 240))
        for wx in (x0 + 230, x0 + 10.5 * ppm - 230): d.ellipse((wx - 45, y - 40, wx + 45, y + 50), fill=(25, 25, 28))
        d.text((x0 + 10.5 * ppm / 2, y - 200), '路線バス（約10.5m）', font=Fo(36), fill=GRAY, anchor='ms')
        g = ease((u - 0.3) / 0.35); L = HAIR_M * ppm * g
        for k in range(5): d.line((x0, y + 90 + k * 6, x0 + L, y + 92 + k * 6 + 6 * math.sin(k + t)), fill=(60, 40, 30), width=4)
        if g > 0.2: d.text((x0 + L + 20, y + 100), f'髪 {HAIR_M * g:.1f}m', font=Fo(52), fill=GOLD, anchor='lm')
        if u > 0.75:
            d.line((x0, y + 230, x0 + NAIL_M * ppm, y + 230), fill=(240, 220, 210), width=22); d.text((x0 + NAIL_M * ppm + 20, y + 230), f'爪 約{NAIL_M:.0f}m', font=Fo(48), fill=PALE, anchor='lm')
    return scene('c_hair.mp4', dur, dr, [(0.5, 'hair')])

RANK = [('心臓が動く回数', '約31億回', RED), ('まばたき', '約4億4000万回', GREEN), ('眠る時間', '約26年', (190, 160, 255)), ('食べる量', 'トラック約5台（約46t）', (255, 160, 90)), ('歩く距離', '地球 約3周', GOLD)]
def s_rank():
    dur = 0.5 + D['rank'] + 0.8; dd = D['rank']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 100), 'あなたの一生（84年）まとめ', Mi(66), GOLD, sw=3)
        for i, (a, b, col) in enumerate(RANK):
            if u < 0.08 + i * 0.17: continue
            y = 210 + i * 150
            d.rounded_rectangle((260, y, W - 260, y + 120), 18, fill=(10, 12, 20, 225), outline=col, width=3)
            d.text((310, y + 60), a, font=Fo(48), fill=col, anchor='lm'); d.text((W - 310, y + 60), b, font=Fo(58), fill=PALE, anchor='rm')
    return scene('c_rank.mp4', dur, dr, [(0.5, 'rank')])

AGES = [10, 20, 30, 50]
def s_pct():
    dur = 0.5 + D['pct'] + 0.8; dd = D['pct']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 100), 'あなたは今、人生の何％？', Mi(76), PALE, sw=3)
        for i, a in enumerate(AGES):
            if u < [0.2, 0.33, 0.48, 0.62][i]: continue
            y = 260 + i * 160; g = ease((u - [0.2, 0.33, 0.48, 0.62][i]) * dd / 1.0); pct = a / LIFE * 100
            d.text((300, y + 55), f'{a}歳', font=Fo(60), fill=GOLD, anchor='rm')
            d.rounded_rectangle((340, y + 20, W - 380, y + 90), 35, fill=(255, 255, 255, 40))
            d.rounded_rectangle((340, y + 20, 340 + (W - 720) * pct / 100 * g, y + 90), 35, fill=GOLD)
            d.text((W - 350, y + 55), f'{pct * g:.0f}%', font=Fo(60), fill=PALE, anchor='lm')
        if u > 0.82: ctext(d, (W / 2, 960), '人生は、まだまだこれから！', Mi(60), GOLD, sw=3)
    return scene('c_pct.mp4', dur, dr, [(0.5, 'pct')])

def s_outro():
    dur = 0.5 + D['outro'] + 2.0
    def dr(im, d, t):
        ctext(d, (W / 2, 380), 'いちばん驚いた数字は？', Mi(90), PALE, sw=4)
        ctext(d, (W / 2, 500), 'あなたは人生の何％でしたか？', Mi(60), GOLD, sw=3)
        if t > 2.5:
            d.rounded_rectangle((W / 2 - 520, 620, W / 2 + 520, 800), 24, fill=(10, 12, 20, 225), outline=GOLD, width=4)
            ctext(d, (W / 2, 670), 'コメントで教えてください', Fo(52), PALE); ctext(d, (W / 2, 750), '次に見たい雑学も募集中！', Fo(44), GOLD)
    return scene('c_outro.mp4', dur, dr, [(0.5, 'outro')])

ORDER = ['title', 'rule', 'run', 'heart', 'breath', 'sleep', 'food', 'hair', 'rank', 'pct', 'outro']
if __name__ == '__main__':
    which = sys.argv[1:] or ORDER; res = {}
    for k in which: res[k] = globals()['s_' + k](); print('done', k, round(res[k][0], 1), flush=True)
    try: old = json.load(open(f'{G}/scenes.json'))
    except Exception: old = {}
    old.update(res); json.dump(old, open(f'{G}/scenes.json', 'w'))
