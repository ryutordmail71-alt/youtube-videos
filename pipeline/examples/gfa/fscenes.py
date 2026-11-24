import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/gfa'); sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/gvm')
import frender as R, fmodel as FM, fcontent as C
GR = R.GR
W, H, FPS = 1920, 1080, 30
G = '/home/claude/gfa'
D = json.load(open(f'{G}/dur.json'))
Fo, Fb, Mi, BE = R.Fo, R.Fb, R.Mi, R.BE
PALE, GOLD, GIANT_C, HUM_C, BLOOD, RED = R.PALE, R.GOLD, R.GIANT_C, R.HUM_C, R.BLOOD, R.RED
GIR_C = (240, 190, 90)
sys.path.insert(0, '/home/claude/gva')
from ascenes import writer, cover_im, ctext, fade

MH = FM.Model(giant=False, pmax=120); MG = FM.Model(pmax=120); MS = FM.Model(pmax=900)
def shot(M, t, cam, **hud): return R.render(M, t, cam, dict(off=True, **hud), f=0)
def blur_bg(M, t, cam): return ImageEnhance.Brightness(shot(M, t, cam).filter(ImageFilter.GaussianBlur(12))).enhance(0.4).convert('RGBA')
MSL = FM.Model(pmax=900, t_up=960, tmax=3000, dt=0.1)     # 16分かけて立つ巨人（立ったままの絵に使う）
STAND = 1500.0
def giant_standing(cam, **k): return shot(MSL, STAND, cam, **k)

def scene_title():
    dur = 0.6 + D['intro'] + 1.0; n = int(dur * FPS)
    base = shot(MG, 6.0, (-8, 28, 13)).convert('RGBA')
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H): gd.line((0, y, W, y), fill=(0, 0, 0, int(190 * max(0, (y - H * 0.3) / (H * 0.7)))))
    base.alpha_composite(g); p = writer(f'{G}/c_title.mp4')
    for f in range(n):
        t = f / FPS; im = base.copy(); d = ImageDraw.Draw(im); u = fade(t / 0.5); s = 1.5 - 0.5 * u
        ctext(d, (W / 2, 330), '立ち上がったら…気絶？', Mi(int(130 * s)), (255, 255, 255), sw=7)
        if t > 0.4:
            d.rounded_rectangle((W / 2 - 220, 600, W / 2 + 220, 650), 25, fill=(0, 0, 0, 170)); ctext(d, (W / 2, 625), '実データでシミュレーション', Fb(28), GOLD)
            ctext(d, (W / 2, 745), '巨人  vs  重力', Mi(116), PALE, sw=4)
            ctext(d, (W / 2, 865), '身長50mの巨人の、血圧の問題', Mi(52), GOLD, sw=3)
            ctext(d, (W / 2, 935), 'CAN A 50-METER GIANT STAND UP WITHOUT FAINTING?', Fb(26), (220, 220, 225))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, 'intro')]

def giraffe(d, x, y, s):
    """足元中央 (x,y)、高さ s px のキリン。戻り値：心臓と頭の位置"""
    c = (226, 170, 80); dk = (150, 96, 40)
    bx0, bx1, by0, by1 = x - s * 0.28, x + s * 0.22, y - s * 0.62, y - s * 0.4
    for lx in (bx0 + s * 0.04, bx0 + s * 0.12, bx1 - s * 0.12, bx1 - s * 0.04):
        d.rectangle((lx - s * 0.02, by1 - s * 0.02, lx + s * 0.02, y), fill=c)
    d.ellipse((bx0, by0, bx1, by1 + s * 0.04), fill=c)
    nx0, ny0 = bx1 - s * 0.06, by0 + s * 0.06; nx1, ny1 = bx1 + s * 0.12, y - s * 0.95
    d.line((nx0, ny0, nx1, ny1), fill=c, width=int(s * 0.07))
    d.ellipse((nx1 - s * 0.03, ny1 - s * 0.05, nx1 + s * 0.12, ny1 + s * 0.03), fill=c)
    d.line((nx1, ny1 - s * 0.03, nx1 - s * 0.01, ny1 - s * 0.08), fill=dk, width=max(2, int(s * 0.012)))
    rng = np.random.default_rng(3)
    for i in range(26):
        u, v = rng.uniform(0.1, 0.9), rng.uniform(0.15, 0.85); px = bx0 + (bx1 - bx0) * u; py = by0 + (by1 - by0) * v
        r = s * 0.018; d.ellipse((px - r, py - r, px + r, py + r), fill=dk)
    return (bx1 - s * 0.08, by0 + s * 0.12), (nx1 + s * 0.03, ny1 - s * 0.01)

def scene_heart():
    t1 = 0.5; t2 = t1 + D['heart'] + 0.5; t3 = t2 + D['giraffe'] + 0.5; dur = t3 + D['giant'] + 1.0; n = int(dur * FPS)
    bg = Image.new('RGBA', (W, H), (16, 18, 26, 255))
    gimg = giant_standing((-2, 36, 17), marks=True).convert('RGBA')
    hum = R.stand_person(720)
    p = writer(f'{G}/c_heart.mp4')
    for f in range(n):
        t = f / FPS; d = None
        if t < t3 - 0.25:
            im = bg.copy(); d = ImageDraw.Draw(im)
            if t < t2 - 0.25:
                u = (t - t1) / D['heart']
                ctext(d, (W / 2, 80), '血圧と、高さの関係', Mi(62), GOLD, sw=3)
                x0 = 560; y0 = 960; im.alpha_composite(hum, (int(x0 - hum.width / 2), int(y0 - hum.height))); d = ImageDraw.Draw(im)
                hy = y0 - 720 * 1.27 / 1.75; by = y0 - 720 * 1.62 / 1.75
                R.heart_icon(d, x0, hy, 26, BLOOD, R.beat_at(t, 70))
                if u > 0.25:
                    d.rounded_rectangle((900, hy - 60, 1700, hy + 60), 18, fill=(10, 12, 18, 230), outline=BLOOD, width=4)
                    d.text((940, hy), '心臓の血圧', font=Fo(40), fill=PALE, anchor='lm'); d.text((1660, hy), '約90', font=Fo(60), fill=BLOOD, anchor='rm')
                    d.line((x0 + 40, hy, 900, hy), fill=BLOOD, width=4)
                if u > 0.55:
                    d.line((x0, hy, x0, by), fill=(240, 160, 60), width=8); d.ellipse((x0 - 18, by - 18, x0 + 18, by + 18), fill=(240, 160, 60), outline=(255, 255, 255), width=3)
                    d.line((x0 + 30, by, 900, by - 20), fill=(240, 160, 60), width=4)
                    d.rounded_rectangle((900, by - 80, 1700, by + 40), 18, fill=(10, 12, 18, 230), outline=(240, 160, 60), width=4)
                    d.text((940, by - 20), '脳（35cm上）', font=Fo(40), fill=PALE, anchor='lm'); d.text((1660, by - 20), '約90−27', font=Fo(56), fill=(240, 160, 60), anchor='rm')
                if u > 0.8: ctext(d, (1300, 700), '高さ1mごとに、約78ずつ下がる', Fo(44), PALE)
                d.text((W - 24, H - 18), '※血圧の単位は mmHg（平均血圧）。血の重さ：1mあたり 約78mmHg', font=Fb(20), fill=(200, 200, 205), anchor='rs')
            else:
                u = (t - t2) / D['giraffe']
                ctext(d, (W / 2, 80), 'キリンの場合', Mi(62), GIR_C, sw=3)
                (hx, hy), (gx, gy) = giraffe(d, 620, 1000, 820)
                R.heart_icon(d, hx, hy, 26, BLOOD, R.beat_at(t, 60))
                d.line((hx, hy, gx, gy), fill=(240, 160, 60), width=6); d.ellipse((gx - 16, gy - 16, gx + 16, gy + 16), fill=(240, 160, 60), outline=(255, 255, 255), width=3)
                if u > 0.2:
                    d.rounded_rectangle((1000, 520, 1760, 640), 18, fill=(10, 12, 18, 230), outline=BLOOD, width=4)
                    d.text((1040, 580), '心臓の血圧', font=Fo(40), fill=PALE, anchor='lm'); d.text((1720, 580), '約200', font=Fo(60), fill=BLOOD, anchor='rm')
                if u > 0.45:
                    d.rounded_rectangle((1000, 250, 1760, 370), 18, fill=(10, 12, 18, 230), outline=(240, 160, 60), width=4)
                    d.text((1040, 310), '頭', font=Fo(40), fill=PALE, anchor='lm'); d.text((1720, 310), '約100', font=Fo(60), fill=(240, 160, 60), anchor='rm')
                if u > 0.55: ctext(d, (1380, 780), '人の2倍以上の血圧！', Fo(54), GOLD, sw=2)
                d.text((W - 24, H - 18), '※Hasenkamp ほか（2021, Annual Review of Physiology）などの値', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        else:
            u = (t - t3) / D['giant']; im = gimg.copy(); d = ImageDraw.Draw(im)
            ctext(d, (W / 2, 80), '巨人の場合', Mi(62), GIANT_C, sw=3)
            rows = [(0.18, '心臓から脳まで', '約10m', PALE), (0.38, '持ち上げるだけで', '約780', RED), (0.6, '必要な心臓の血圧', '約850', GOLD), (0.8, '人の約9倍・キリンの約4倍', '', GOLD)]
            for r, (tr, lab, val, col) in enumerate(rows):
                if u < tr: continue
                y = 230 + r * 120
                d.rounded_rectangle((1060, y, 1860, y + 100), 16, fill=(10, 12, 18, 225), outline=GOLD if r >= 2 else None, width=4 if r >= 2 else 0)
                if val: d.text((1090, y + 50), lab, font=Fo(36), fill=(210, 210, 215), anchor='lm'); d.text((1830, y + 50), val, font=Fo(56), fill=col, anchor='rm')
                else: d.text((1460, y + 50), lab, font=Fo(44), fill=col, anchor='mm')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t1, 'heart'), (t2, 'giraffe'), (t3, 'giant')]

RULES = [('スタート', '寝ている状態から、立ち上がる', 0.1), ('気絶', '脳の血圧が30を下回る状態が、7秒続いたら', 0.3)]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; n = int(dur * FPS); bg = blur_bg(MSL, STAND, (-6, 30, 13)); p = writer(f'{G}/c_rule.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = (t - 0.5) / D['rule']
        ctext(d, (W / 2, 170), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 240), 'RULES', Fb(26), (210, 210, 215))
        for r, (who, txt, fr) in enumerate(RULES):
            if u < fr: continue
            y = 340 + r * 170
            d.rounded_rectangle((180, y, W - 180, y + 130), 18, fill=(10, 12, 18, 225), outline=GOLD if r else None, width=4 if r else 0)
            d.rounded_rectangle((210, y + 30, 410, y + 100), 14, fill=GIANT_C if r == 0 else RED); ctext(d, (310, y + 65), who, Fo(38), (20, 20, 24))
            d.text((450, y + 65), txt, font=Fo(48), fill=PALE, anchor='lm')
        if u > 0.6:
            d.rounded_rectangle((300, 720, W - 300, 860), 18, fill=(10, 12, 18, 225))
            ctext(d, (W / 2, 765), '実験では、脳への血が止まると', Fo(38), (210, 210, 215)); ctext(d, (W / 2, 820), '4〜10秒ほどで意識を失う', Fo(46), GOLD)
        d.text((W - 24, H - 18), '※Rossen ほか（1943）の実験など', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'rule')]

def scene_battle(M, title, pre, sim_len, camk, cues, out, W_=W, H_=H):
    dur = pre + sim_len; n = int(dur * FPS)
    caps = [(vt, vt + D[k] + 0.6, C.CAP[k]) for vt, k in cues if k in C.CAP]
    cs = None; p = writer(out, W_, H_); sts = []
    for f in range(n):
        vt = f / FPS; st = vt - pre
        for (va, ma, za), (vb, mb, zb) in zip(camk, camk[1:]):
            if va <= vt < vb: break
        else: va, ma, za = camk[-1]; vb, mb, zb = va + 1, ma, za
        u = (lambda x: x * x * (3 - 2 * x))(min(1, max(0, (vt - va) / max(0.01, min(2.5, vb - va)))))
        tx, ty = ma[0] + (mb[0] - ma[0]) * u, ma[1] + (mb[1] - ma[1]) * u
        if cs is None: cs = [tx, ty]
        cs[0] += (tx - cs[0]) * 0.12; cs[1] += (ty - cs[1]) * 0.12; ppm = za + (zb - za) * u
        cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None)
        capcol = RED if cap and '気絶' in cap else (GOLD if cap and '平気' in cap else PALE)
        im = R.render(M, st, (cs[0], cs[1], ppm), dict(round=title, title=title, cap=cap, capcol=capcol), f=f)
        sts.append(round(st, 3)); p.stdin.write(im.tobytes())
        if f % 300 == 0: print(out, f, n, flush=True)
    p.stdin.close(); p.wait(); json.dump(dict(st=sts), open(out.replace('.mp4', '_st.json'), 'w'))
    return dur, cues
def _cam(lst): return [(v, (c[0], c[1]), c[2]) for v, c in lst]
R1_CAM = [(0, (-0.3, 0.75, 300.0)), (4.0, (-0.2, 0.9, 330.0))]
R1_CUES = [(0.2, 'r1a'), (5.0, 'r1b'), (9.0, 'r1c')]
R2_CAM = [(0, (-14, 24, 12.5)), (7.0, (-10, 28, 14.0)), (11.0, (-4, 36, 18.0)), (17.0, (-4, 36, 18.0)), (18.5, (-24, 22, 11.0))]
R2_CUES = [(0.2, 'r2a'), (9.8, 'r2b'), (13.5, 'r2c'), (17.0, 'r2d')]
R3_CAM = [(0, (-14, 24, 12.5)), (4.0, (-10, 28, 14.0)), (8.0, (-4, 36, 18.0)), (14.0, (-4, 36, 18.0)), (15.5, (-24, 22, 11.0))]
R3_CUES = [(0.2, 'r3a'), (5.2, 'r3b'), (10.6, 'r3c'), (14.0, 'r3d')]

def scene_card(key, title, lines, bg, out, big=None, sub=None, bigcol=GOLD):
    dur = 0.6 + D[key] + 0.8; n = int(dur * FPS); p = writer(out)
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = fade(t / 0.4)
        ctext(d, (W / 2, 250), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 390), big, Mi(int(130 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 560, y - 48, W / 2 + 560, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 520, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm')
            d.text((W / 2 + 520, y), val, font=Fo(52), fill=col, anchor='rm')
        if sub: d.text((W - 24, H - 18), sub, font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, key)]

def scene_super():
    t1 = 0.5; t2 = t1 + D['super'] + 0.5; dur = t2 + D['hrate'] + 1.0; n = int(dur * FPS)
    bg = blur_bg(MSL, STAND, (-4, 34, 16)); bg2 = Image.new('RGBA', (W, H), (16, 18, 26, 255)); p = writer(f'{G}/c_super.mp4')
    for f in range(n):
        t = f / FPS
        if t < t2 - 0.25:
            im = bg.copy(); d = ImageDraw.Draw(im); u = (t - t1) / D['super']
            ctext(d, (W / 2, 160), 'スーパー心臓', Mi(100), GOLD, sw=5)
            R.heart_icon(d, W / 2, 330, 70, BLOOD, R.beat_at(t, 50))
            if u > 0.2:
                d.rounded_rectangle((W / 2 - 520, 450, W / 2 + 520, 570), 18, fill=(10, 12, 18, 230), outline=GOLD, width=4)
                d.text((W / 2 - 480, 510), '血圧を上げられる上限', font=Fo(40), fill=PALE, anchor='lm'); d.text((W / 2 + 480, 510), '900', font=Fo(64), fill=GOLD, anchor='rm')
            if u > 0.5:
                d.rounded_rectangle((W / 2 - 520, 620, W / 2 + 520, 800), 18, fill=(60, 14, 18, 230), outline=RED, width=4)
                ctext(d, (W / 2, 670), '寝ているときから900だと…', Fo(40), PALE); ctext(d, (W / 2, 745), '脳の血管が破れてしまう！', Fo(52), RED)
            if u > 0.78: ctext(d, (W / 2, 880), '→ 立ち上がるときに、血圧を上げる', Fo(48), GOLD, sw=2)
        else:
            im = bg2.copy(); d = ImageDraw.Draw(im); u = (t - t2) / D['hrate']; tt = t - t2
            ctext(d, (W / 2, 100), '心臓の速さ（1分間の心拍数）', Mi(62), GOLD, sw=3)
            items = [(0.22, '人', '約70回', 70, HUM_C), (0.45, '巨人（計算）', '約6回', 5.7, GIANT_C), (0.72, 'シロナガスクジラ（潜水中）', '最低2回', 2, (150, 200, 230))]
            for i, (tr, name, val, hr, col) in enumerate(items):
                if u < tr: continue
                x = W * (i + 0.5) / 3
                R.heart_icon(d, x, 400, 90, BLOOD, R.beat_at(tt - tr * D['hrate'], hr))
                ctext(d, (x, 610), name, Fo(44), col); ctext(d, (x, 720), val, Fo(80), PALE)
            if u > 0.5: ctext(d, (W / 2, 880), '体が大きいほど、心臓はゆっくり（体重の −1/4 乗に比例）', Fo(38), (220, 220, 225))
            d.text((W - 24, H - 18), '※クジラ：Goldbogen ほか（2019）。巨人の値は動物の体重と心拍数の関係からの計算', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t1, 'super'), (t2, 'hrate')]

TABLE = [('1分', '17秒で気絶', RED), ('5分', '約1分で気絶', RED), ('10分', '約3分で気絶', RED), ('約16分', '気絶しない！', HUM_C)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.5; n = int(dur * FPS)
    bg = blur_bg(MSL, STAND, (-6, 30, 13)); reveal = [t0 + dd * x for x in (0.2, 0.4, 0.6, 0.78)]
    p = writer(f'{G}/c_sweep.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im)
        ctext(d, (W / 2, 120), 'ゆっくり立ち上がったら？', Mi(68), GOLD, sw=3)
        ctext(d, (W / 2, 195), 'スーパー心臓（最大900）の巨人が、立ち上がるのにかける時間', Fb(30), (220, 220, 225))
        for r, (ns, res, col) in enumerate(TABLE):
            if t < reveal[r]: continue
            y = 290 + r * 150; hl = r == 3
            d.rounded_rectangle((300, y, W - 300, y + 120), 18, fill=(10, 12, 18, 225), outline=GOLD if hl else None, width=5 if hl else 0)
            d.text((350, y + 60), f'{ns}かけて立つ', font=Fo(54), fill=GIANT_C, anchor='lm')
            d.text((W - 350, y + 60), res, font=Fo(56), fill=col, anchor='rm')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t0, 'sweep')]

def scene_feet():
    t0 = 0.5; dd = D['feet']; dur = t0 + dd + 1.0; n = int(dur * FPS)
    bg = Image.new('RGBA', (W, H), (16, 18, 26, 255)); p = writer(f'{G}/c_feet.mp4')
    bars = [(0.42, '人', 195, HUM_C, '約190'), (0.55, 'キリン', 300, GIR_C, '約260〜300'), (0.62, '巨人', 3750, RED, '約3,700')]
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = (t - t0) / dd
        ctext(d, (W / 2, 90), '足の血管にかかる圧力', Mi(66), GOLD, sw=3)
        ctext(d, (W / 2, 165), '巨人の足は、心臓より約37m下', Fb(32), (220, 220, 225))
        x0, x1 = 420, W - 160; ymax = 3800
        for i, (tr, name, v, col, lab) in enumerate(bars):
            if u < tr: continue
            g = fade((u - tr) * dd / 1.2); y = 330 + i * 200; L = (x1 - x0) * v / ymax * g
            d.text((x0 - 30, y + 50), name, font=Fo(52), fill=col, anchor='rm')
            d.rectangle((x0, y, x0 + max(6, L), y + 100), fill=col)
            d.text((x0 + max(6, L) + 20, y + 50) if L < (x1 - x0) * 0.7 else (x0 + L - 20, y + 50), lab, font=Fo(50), fill=PALE if L < (x1 - x0) * 0.7 else (20, 20, 24), anchor='lm' if L < (x1 - x0) * 0.7 else 'rm')
        if u > 0.75: ctext(d, (W / 2, 960), '人の約19倍！ 足の血管がパンパンに…', Mi(56), RED, sw=3)
        d.text((W - 24, H - 18), '※立っているときの足の動脈の血圧（目安）。キリンは Hasenkamp ほか（2021）の値', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t0, 'feet')]

def scene_outro():
    dur = 0.5 + D['outro'] + 2.0; n = int(dur * FPS)
    base = cover_im(giant_standing((-8, 27, 13)), W, H, dark=0.42).convert('RGBA'); p = writer(f'{G}/c_outro.mp4')
    for f in range(n):
        t = f / FPS; im = base.copy(); d = ImageDraw.Draw(im); u = (t - 0.5) / D['outro']
        if u < 0.38:
            ctext(d, (W / 2, 260), '首の長い恐竜 バロサウルス', Mi(70), PALE, sw=4)
            if u > 0.12:
                d.rounded_rectangle((W / 2 - 560, 380, W / 2 + 560, 560), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (W / 2, 430), '頭を高く上げるのに必要な、心臓の血圧', Fo(40), (220, 220, 225)); ctext(d, (W / 2, 510), '約700（という研究も）', Fo(66), GOLD)
            d.text((W - 24, H - 18), '※Seymour & Lillywhite（2000）などの推定', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        elif u < 0.72:
            ctext(d, (W / 2, 330), '本物の巨人がいたら…', Mi(76), PALE, sw=4)
            if u > 0.46: ctext(d, (W / 2, 490), '16分かけて立ち上がる', Mi(104), GOLD, sw=5)
            if u > 0.56: ctext(d, (W / 2, 640), 'のんびり屋さん？', Mi(70), PALE, sw=4)
        else:
            ctext(d, (W / 2, 380), '巨人は気絶すると思った？', Mi(86), PALE, sw=4)
            ctext(d, (W / 2, 490), 'コメントで教えてください', Mi(54), GOLD, sw=3)
            if u > 0.86:
                d.rounded_rectangle((W / 2 - 520, 620, W / 2 + 520, 800), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (W / 2, 670), '次に見たい巨人の謎は？', Fo(50), PALE); ctext(d, (W / 2, 750), 'リクエスト募集中！', Fo(44), GOLD)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'outro')]

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['heart'] = scene_heart(); res['rule'] = scene_rule(); res['super'] = scene_super(); res['sweep'] = scene_sweep(); res['feet'] = scene_feet(); res['outro'] = scene_outro()
        res['res1'] = scene_card('res1', 'RESULT  1回戦　ふつうの人', [('脳の血圧（いちばん低いとき）', '約50', PALE), ('元に戻るまで', '数秒', HUM_C)], blur_bg(MH, 12, (-0.2, 0.9, 330)), f'{G}/c_res1.mp4', big='人は平気！', bigcol=HUM_C)
        res['res2'] = scene_card('res2', 'RESULT  2回戦　巨人（人と同じ心臓）', [('気絶するまで', '約9秒', RED), ('脳の血圧（いちばん低いとき）', '約−640', RED), ('心臓から脳まで', '約10m', PALE)], blur_bg(MG, MG.t_end, (-24, 22, 11)), f'{G}/c_res2.mp4', big='巨人、気絶', bigcol=RED)
        res['res3'] = scene_card('res3', 'RESULT  決勝戦　巨人（スーパー心臓）', [('気絶するまで', '約9秒', RED), ('心拍', '1分に約6回', GIANT_C), ('血圧を上げるのが', '間に合わない', GOLD)], blur_bg(MS, MS.t_end if MS.faint_t else 30, (-24, 22, 11)), f'{G}/c_res3.mp4', big='それでも気絶', bigcol=RED)
    elif which == 'r1':
        res['r1'] = scene_battle(MH, '1回戦　ふつうの人が立ち上がる', 3.0, 10.5, _cam(R1_CAM), R1_CUES, f'{G}/c_r1.mp4')
    elif which == 'r2':
        res['r2'] = scene_battle(MG, '2回戦　巨人（人と同じ心臓）', 6.8, MG.t_end, _cam(R2_CAM), R2_CUES, f'{G}/c_r2.mp4')
    elif which == 'r3':
        res['r3'] = scene_battle(MS, '決勝戦　巨人（スーパー心臓）', 3.9, MS.t_end, _cam(R3_CAM), R3_CUES, f'{G}/c_r3.mp4')
    json.dump(res, open(f'{G}/scene_{which}.json', 'w'))
    print('done', which)
