import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/gva'); sys.path.insert(0, '/home/claude/gvm')
import arender as A, amodel as AM, acontent as C
GR = A.GR
W, H, FPS = 1920, 1080, 30
G = '/home/claude/gva'
D = json.load(open(f'{G}/dur.json'))
Fo, Fb, Mi, BE = A.Fo, A.Fb, A.Mi, A.BE
PALE, GOLD, GIANT_C, HUM_C = A.PALE, A.GOLD, A.GIANT_C, A.HUM_C
RED = (255, 110, 110)

def writer(path, w=W, h=H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
def cover_im(im, w, h, fx=0.5, fy=0.5, dark=1.0, blur=0):
    im = im.convert('RGB'); s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x = int((im.width - w) * fx); y = int((im.height - h) * fy); im = im.crop((x, y, x + w, y + h))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark != 1: im = ImageEnhance.Brightness(im).enhance(dark)
    return im
def ctext(d, xy, t, f, fill, anchor='mm', sw=0):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))

M1, M2, M3 = AM.Model(100), AM.Model(816), AM.Model(2000)
def shot(M, t, cam, **hud): return A.render(M, t, cam, dict(off=True, **hud), f=0)
def blur_bg(M, t, cam): return ImageEnhance.Brightness(shot(M, t, cam).filter(ImageFilter.GaussianBlur(12))).enhance(0.4).convert('RGBA')
def big_person(h):
    st, _ = A.person(h, 18, 0, 'pull'); return st

def scene_title():
    dur = 0.6 + D['intro'] + 1.0; n = int(dur * FPS)
    base = shot(M3, 12, (-30, 21, 13.5)).convert('RGBA')
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H): gd.line((0, y, W, y), fill=(0, 0, 0, int(190 * max(0, (y - H * 0.3) / (H * 0.7)))))
    base.alpha_composite(g)
    p = writer(f'{G}/c_title.mp4')
    for f in range(n):
        t = f / FPS; im = base.copy(); d = ImageDraw.Draw(im); u = fade(t / 0.5); s = 1.5 - 0.5 * u
        ctext(d, (W / 2, 360), '何人で勝てる？', Mi(int(150 * s)), (255, 255, 255), sw=7)
        if t > 0.4:
            d.rounded_rectangle((W / 2 - 220, 600, W / 2 + 220, 650), 25, fill=(0, 0, 0, 170)); ctext(d, (W / 2, 625), '実データでシミュレーション', Fb(28), GOLD)
            ctext(d, (W / 2, 745), '巨人  vs  人間の軍隊', Mi(110), PALE, sw=4)
            ctext(d, (W / 2, 865), '身長50mの巨人と、綱引きで勝負！', Mi(52), GOLD, sw=3)
            ctext(d, (W / 2, 935), 'A 50-METER GIANT  vs  A HUMAN ARMY  —  TUG OF WAR', Fb(26), (220, 220, 225))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, 'intro')]

GROWS = [('身長', '50m', '人の約29倍'), ('体重', '約1,600t', '約2万3000倍'), ('力', '約816倍', '29×29')]
HROWS = [('身長', '1.75m', ''), ('体重', '約70kg', ''), ('綱を引く力', '約63kg', '実験の値')]
def scene_stats():
    t1 = 0.5; t2 = t1 + D['stats1'] + 0.3; t3 = t2 + D['stats2'] + 0.4; dur = t3 + D['power'] + 1.0; n = int(dur * FPS)
    bg = cover_im(shot(M3, 12, (-20, 20, 12)), W, H, blur=30, dark=0.3).convert('RGBA')
    pw, ph = 760, 330
    gp = cover_im(shot(M3, -1, (-6, 28, 9), ruler=True), pw, ph, fx=0.6, fy=0.3)
    hp = cover_im(shot(M1, -1, (-22, 0.6, 110)), pw, ph, fx=0.5, fy=0.72)
    p = writer(f'{G}/c_stats.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im)
        if t < t3 - 0.2:
            ctext(d, (W / 2, 70), 'データ比較', Mi(60), PALE); ctext(d, (W / 2, 120), 'DATA', Fb(24), (200, 200, 205))
            for x0, photo, name, col, rows, ts in [(130, gp, '巨人', GIANT_C, GROWS, t1), (W - 130 - pw, hp, '人間（兵士1人）', HUM_C, HROWS, t1 + 1.0)]:
                im.paste(photo, (x0, 170)); d.rectangle((x0, 170, x0 + pw, 170 + ph), outline=col, width=5)
                ctext(d, (x0 + pw / 2, 545), name, Mi(52), col)
                for r, row in enumerate(rows):
                    tr = [t1 + 2.5, t1 + 6.0, t2 + 0.5][r]
                    if t < tr: continue
                    y = 640 + r * 125; hl = r == 2 and t > t2 + D['stats2'] * 0.55
                    d.rounded_rectangle((x0, y, x0 + pw, y + 105), 14, fill=(10, 12, 18, 215), outline=GOLD if hl else None, width=4 if hl else 0)
                    d.text((x0 + 30, y + 52), row[0], font=Fb(28), fill=(200, 200, 205), anchor='lm')
                    d.text((x0 + 250, y + 52), row[1], font=Fo(46), fill=GOLD if hl else PALE, anchor='lm')
                    if row[2]: d.text((x0 + pw - 30, y + 52), row[2], font=Fb(26), fill=col, anchor='rm')
            if t2 + 1 < t < t3:
                xr = W - 130 - pw
                d.rounded_rectangle((xr, 170, xr + pw, 170 + ph), 24, fill=(10, 12, 18, 245), outline=GOLD, width=4)
                ctext(d, (xr + pw / 2, 270), '筋肉の力は「太さ（断面積）」で決まる', Fo(34), PALE)
                ctext(d, (xr + pw / 2, 380), '29 × 29 = 約816倍', Fo(62), GOLD)
        else:
            u = (t - t3) / D['power']
            ctext(d, (W / 2, 170), '綱を引く力', Mi(70), PALE, sw=3)
            if u > 0.05:
                d.rounded_rectangle((260, 300, W / 2 - 60, 640), 24, fill=(10, 12, 18, 225)); ctext(d, (W / 4 + 100, 370), '人間 1人', Fo(46), HUM_C); ctext(d, (W / 4 + 100, 520), '約63kg', Fo(100), PALE)
            if u > 0.42:
                d.rounded_rectangle((W / 2 + 60, 300, W - 260, 640), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4); ctext(d, (3 * W / 4 - 100, 370), '巨人（×816）', Fo(46), GIANT_C)
                ctext(d, (3 * W / 4 - 100, 520), '約5万1000kg', Fo(84), GOLD)
            if u > 0.8: ctext(d, (W / 2, 760), '＝ 約51トン分の力！', Mi(64), GOLD, sw=3)
            d.text((W - 24, H - 18), '※1人の力は、リンゲルマンの綱引き実験（1913年ごろ）で1人で引いたときの値', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t1, 'stats1'), (t2, 'stats2'), (t3, 'power')]

RULES = [('人間', '巨人と綱で引っ張り合う', 0.08), ('人間', '巨人を10m引きずったら勝ち', 0.40), ('巨人', '人間を20m引きずったら勝ち', 0.70)]
def scene_rule():
    dur = 0.5 + D['rule'] + 1.0; n = int(dur * FPS); bg = blur_bg(M3, 12, (-30, 22, 12)); p = writer(f'{G}/c_rule.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im)
        ctext(d, (W / 2, 170), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 240), 'RULES', Fb(26), (210, 210, 215))
        for r, (who, txt, fr) in enumerate(RULES):
            if t < 0.5 + D['rule'] * fr: continue
            y = 340 + r * 170; col = HUM_C if who == '人間' else GIANT_C
            d.rounded_rectangle((220, y, W - 220, y + 130), 18, fill=(10, 12, 18, 225), outline=GOLD if r else None, width=4 if r else 0)
            d.rounded_rectangle((250, y + 30, 410, y + 100), 14, fill=col); ctext(d, (330, y + 65), who, Fo(40), (20, 20, 24))
            d.text((450, y + 65), txt, font=Fo(50), fill=PALE, anchor='lm')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'rule')]

def scene_battle(M, title, pre, post, camk, cues, out, ruler_until=0, W_=W, H_=H, extra=None):
    dur = pre + M.t_end + post; n = int(dur * FPS)
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
        if st < 0: cap = 'よーい…' if st < -1.2 else 'スタート！'
        capcol = GOLD if cap and ('勝' in cap or '倒れ' in cap or 'スタート' in cap) else PALE
        hud = dict(round=title, title=title, cap=cap, capcol=capcol, ruler=vt < ruler_until)
        if extra: hud.update(extra(vt))
        im = A.render(M, st, (cs[0], cs[1], ppm), hud, f=f)
        sts.append(round(st, 3)); p.stdin.write(im.tobytes())
        if f % 300 == 0: print(out, f, n, flush=True)
    p.stdin.close(); p.wait(); json.dump(dict(st=sts), open(out.replace('.mp4', '_st.json'), 'w'))
    return dur, cues
def _cam(lst): return [(v, (c[0], c[1]), c[2]) for v, c in lst]
R1_CAM = [(0, (-32, 24, 12.0)), (6.0, (-24, 22, 17.0)), (12.5, (-26, 14, 21.0)), (19.0, (-22, 18, 15.0))]
R1_CUES = [(0.2, 'r1a'), (7.6, 'r1b'), (13.2, 'r1c'), (23.1, 'r1d')]
R2_CAM = [(0, (-36, 24, 11.5)), (10.0, (-24, 22, 17.0)), (18.0, (-8, 30, 16.0)), (26.0, (-26, 14, 21.0)), (33.0, (-26, 20, 14.0))]
R2_CUES = [(0.2, 'r2a'), (18.0, 'r2b'), (25.5, 'r2c'), (37.6, 'r2d')]
R3_CAM = [(0, (-36, 24, 11.5)), (6.0, (-24, 22, 17.0)), (14.0, (-8, 30, 16.0)), (22.0, (-26, 14, 21.0)), (30.0, (-20, 15, 19.0)), (37.0, (-40, 22, 10.5))]
R3_CUES = [(0.2, 'r3a'), (7.6, 'r3b'), (14.6, 'r3c'), (25.0, 'r3d'), (6.6 + 32.3 + 3.0, 'r3e')]

def scene_card(key, title, lines, bg, out, big=None, sub=None, bigcol=GOLD):
    dur = 0.6 + D[key] + 0.8; n = int(dur * FPS); p = writer(out)
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = fade(t / 0.4)
        ctext(d, (W / 2, 250), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 390), big, Mi(int(140 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 560, y - 48, W / 2 + 560, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 520, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm')
            d.text((W / 2 + 520, y), val, font=Fo(52), fill=col, anchor='rm')
        if sub: d.text((W - 24, H - 18), sub, font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, key)]

RING = [(1, 1.00, '63kg'), (2, 0.93, ''), (3, 0.85, ''), (8, 0.49, '31kg')]
def scene_ringel():
    t1 = 0.5; t2 = t1 + D['ringel'] + 0.6; dur = t2 + D['ringel2'] + 1.0; n = int(dur * FPS)
    bg = Image.new('RGBA', (W, H), (16, 18, 26, 255)); p = writer(f'{G}/c_ringel.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = (t - t1) / D['ringel']
        ctext(d, (W / 2, 90), 'リンゲルマンの綱引き実験', Mi(66), GOLD, sw=3)
        ctext(d, (W / 2, 160), '大人数で引くと、1人あたりの力はどうなる？', Fb(32), (220, 220, 225))
        x0, x1, yb, yt = 380, W - 380, 900, 280
        d.line((x0 - 20, yb, x1 + 20, yb), fill=(200, 200, 205), width=3)
        d.text((x0 - 40, yt), '1人あたりの力', font=Fb(26), fill=(200, 200, 205), anchor='rm')
        for i, (k, v, lab) in enumerate(RING):
            ti = [0.45, 0.6, 0.66, 0.78][i]
            if u < ti: continue
            g = fade((u - ti) * D['ringel'] / 0.8); cxb = x0 + (i + 0.5) * (x1 - x0) / 4; bh = (yb - yt) * v * g
            col = HUM_C if i < 3 else RED
            d.rectangle((cxb - 110, yb - bh, cxb + 110, yb), fill=col)
            ctext(d, (cxb, yb - bh - 40), f'{int(v * 100)}%', Fo(50), PALE)
            if lab: ctext(d, (cxb, yb - bh + 40), lab, Fo(36), (20, 20, 24))
            ctext(d, (cxb, yb + 50), f'{k}人で引く', Fo(38), PALE)
        if t > t2:
            d.rounded_rectangle((W / 2 - 600, 340, W / 2 + 600, 560), 24, fill=(10, 12, 18, 240), outline=GOLD, width=5)
            ctext(d, (W / 2, 410), 'リンゲルマン効果（社会的手抜き）', Fo(52), GOLD)
            ctext(d, (W / 2, 495), '大勢になるほど、1人1人がつい力を抜いてしまう', Fo(38), PALE)
        d.text((W - 24, H - 18), '※Ringelmann（1913）の綱引き実験。大人数でも8人のときと同じ49%と仮定して計算', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t1, 'ringel'), (t2, 'ringel2')]

TABLE = [('1,000人', '巨人の60%　33秒で負け', PALE), ('1,500人', '巨人の90%　2分18秒で負け', PALE), ('約1,670人', '互角', GOLD), ('2,000人', '？？？', GOLD)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.5; n = int(dur * FPS)
    bg = blur_bg(M3, 12, (-25, 16, 18)); reveal = [t0 + dd * x for x in (0.28, 0.5, 0.82, 0.95)]
    p = writer(f'{G}/c_sweep.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im)
        ctext(d, (W / 2, 120), '手抜きも入れて、人数を増やすと？', Mi(64), GOLD, sw=3)
        ctext(d, (W / 2, 190), '1人あたり 約31kg（63kgの49%）で計算', Fb(30), (220, 220, 225))
        for r, (ns, res, col) in enumerate(TABLE):
            if t < reveal[r]: continue
            y = 290 + r * 150; hl = r >= 2
            d.rounded_rectangle((260, y, W - 260, y + 120), 18, fill=(10, 12, 18, 225), outline=GOLD if hl else None, width=5 if hl else 0)
            d.text((310, y + 60), f'人間 {ns}', font=Fo(54), fill=HUM_C, anchor='lm')
            d.text((W - 310, y + 60), res, font=Fo(54), fill=col, anchor='rm')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t0, 'sweep')]

def scene_outro():
    dur = 0.5 + D['outro'] + 2.0; n = int(dur * FPS)
    base = cover_im(shot(M3, 4, (-25, 22, 13)), W, H, dark=0.4).convert('RGBA'); p = writer(f'{G}/c_outro.mp4')
    for f in range(n):
        t = f / FPS; im = base.copy(); d = ImageDraw.Draw(im); u = (t - 0.5) / D['outro']
        if u < 0.33:
            ctext(d, (W / 2, 200), '倒れたとき、頭が地面にぶつかる速さ', Mi(62), PALE, sw=4)
            if u > 0.08:
                d.rounded_rectangle((260, 330, W / 2 - 40, 620), 24, fill=(10, 12, 18, 225)); ctext(d, (W / 4 + 110, 400), '人が転ぶ', Fo(48), HUM_C); ctext(d, (W / 4 + 110, 520), '時速 約26km', Fo(76), PALE)
            if u > 0.16:
                d.rounded_rectangle((W / 2 + 40, 330, W - 260, 620), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4); ctext(d, (3 * W / 4 - 110, 400), '巨人が倒れる', Fo(48), GIANT_C); ctext(d, (3 * W / 4 - 110, 520), '時速 約140km', Fo(76), RED)
            if u > 0.24: ctext(d, (W / 2, 760), '→ 5倍以上の速さ！', Mi(60), GOLD, sw=4)
            d.text((W - 24, H - 18), '※まっすぐな棒が倒れるとして計算（先端の速さ ＝ √(3 × 重力 × 高さ)）', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        elif u < 0.72:
            ctext(d, (W / 2, 330), '本物の巨人の、もっと大きな弱点', Mi(70), PALE, sw=4)
            if u > 0.5: ctext(d, (W / 2, 500), '立ち上がっただけで、気絶する？', Mi(96), GOLD, sw=5)
            if u > 0.6: ctext(d, (W / 2, 660), '→ 次の動画で', Fo(56), PALE, sw=3)
        else:
            ctext(d, (W / 2, 380), '何人で勝てると思った？', Mi(86), PALE, sw=4)
            ctext(d, (W / 2, 490), 'コメントで教えてください', Mi(54), GOLD, sw=3)
            if u > 0.86:
                d.rounded_rectangle((W / 2 - 520, 620, W / 2 + 520, 800), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (W / 2, 670), '次の対決は？', Fo(52), PALE); ctext(d, (W / 2, 750), 'リクエスト募集中！', Fo(44), GOLD)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'outro')]

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['stats'] = scene_stats(); res['rule'] = scene_rule(); res['ringel'] = scene_ringel(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
        res['res1'] = scene_card('res1', 'RESULT  1回戦　人間100人', [('引きずられるまで', '約16秒', PALE), ('人間チームの力', '約3,100kg', HUM_C), ('巨人の力', '約5万1000kg', GIANT_C)], blur_bg(M1, M1.t_end + 2, (-25, 16, 16)), f'{G}/c_res1.mp4', big='巨人の圧勝', bigcol=GIANT_C)
        res['res3'] = scene_card('res3', 'RESULT  決勝戦　人間2,000人', [('巨人を倒すまで', '約32秒', PALE), ('手抜きがなければ', '816人', HUM_C), ('実際に必要だったのは', '約1,670人以上', GOLD)], blur_bg(M3, M3.t_end + 8, (-35, 20, 12)), f'{G}/c_res3.mp4', big='人間チームの勝利', bigcol=HUM_C)
    elif which == 'r1':
        res['r1'] = scene_battle(M1, '1回戦　人間100人 vs 巨人', 6.6, 4.6, _cam(R1_CAM), R1_CUES, f'{G}/c_r1.mp4', ruler_until=5.5)
    elif which == 'r2':
        res['r2'] = scene_battle(M2, '2回戦　人間816人 vs 巨人', 10.8, 4.6, _cam(R2_CAM), R2_CUES, f'{G}/c_r2.mp4')
    elif which == 'r3':
        res['r3'] = scene_battle(M3, '決勝戦　人間2,000人 vs 巨人', 6.6, 9.0, _cam(R3_CAM), R3_CUES, f'{G}/c_r3.mp4')
    json.dump(res, open(f'{G}/scene_{which}.json', 'w'))
    print('done', which)
