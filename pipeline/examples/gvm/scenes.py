import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/gvm')
import gmodel as GM, grender as GR, bcontent as C
W, H, FPS = 1920, 1080, 30
D = json.load(open('/home/claude/gvm/dur.json'))
Fo, Fb, Mi, BE = GR.Fo, GR.Fb, GR.Mi, GR.BE
PALE, GOLD, MOS_C, BLOOD_C, GIANT_C = GR.PALE, GR.GOLD, GR.MOS_C, GR.BLOOD_C, GR.GIANT_C
def IMG(k):
    p = f'/home/claude/gvm/img/{k}.jpg'
    return p if os.path.exists(p) and os.path.getsize(p) > 1000 else None

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
def cover(path, *a, **k): return cover_im(Image.open(path), *a, **k)
def ctext(d, xy, t, f, fill, anchor='mm', sw=0):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
def fade(u): return max(0.0, min(1.0, u))

M1 = GM.Model(1e8, can_bite=False)
M2 = GM.Model(2e10)
def giant_shot(cam, M=None, t=0, ruler=False):
    return GR.render(M, t, cam, dict(ruler=ruler, off=True), f=0)
def swarm_shot():
    return GR.render(M2, 40000, (0, 34, 15), dict(off=True), f=0)

def draw_mosquito(size):
    """写真が使えないとき用の、簡単な蚊のイラスト"""
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = size / 100
    c = (40, 36, 34, 255)
    d.ellipse((38 * s, 40 * s, 62 * s, 62 * s), fill=c); d.ellipse((55 * s, 44 * s, 90 * s, 56 * s), fill=c); d.ellipse((24 * s, 43 * s, 40 * s, 57 * s), fill=c)
    d.line((26 * s, 50 * s, 2 * s, 52 * s), fill=c, width=max(1, int(1.5 * s)))
    for k in range(3):
        x = 42 + k * 7
        d.line((x * s, 58 * s, (x - 10) * s, 85 * s), fill=c, width=max(1, int(1.2 * s))); d.line(((x - 10) * s, 85 * s, (x - 16) * s, 98 * s), fill=c, width=max(1, int(1 * s)))
        d.line((x * s, 44 * s, (x + 6) * s, 18 * s), fill=c, width=max(1, int(1.2 * s)))
    d.ellipse((40 * s, 18 * s, 78 * s, 40 * s), fill=(200, 210, 220, 140)); d.ellipse((44 * s, 22 * s, 82 * s, 42 * s), outline=(120, 130, 140, 200), width=1)
    return im
def mosquito_panel(w, h):
    p = IMG('aedes') or IMG('macro')
    if p: return cover(p, w, h)
    bg = Image.new('RGB', (w, h), (236, 222, 205)); m = draw_mosquito(min(w, h) - 20); bg.paste(m, ((w - m.width) // 2, (h - m.height) // 2), m); return bg

def scene_title():
    dur = 0.6 + D['intro'] + 1.0; n = int(dur * FPS)
    sw = swarm_shot(); gs = giant_shot((-8, 26, 13), ruler=True)
    L = cover(IMG('macro'), W // 2 + 120, H, dark=0.62) if IMG('macro') else cover_im(sw, W // 2 + 120, H, dark=0.75)
    R = cover_im(gs, W // 2 + 120, H, fx=0.5, dark=0.8)
    base = Image.new('RGB', (W, H)); base.paste(L, (-120, 0))
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([(W // 2 + 90, 0), (W, 0), (W, H), (W // 2 - 90, H)], fill=255)
    Rf = Image.new('RGB', (W, H)); Rf.paste(R, (W // 2 - 120, 0)); base = Image.composite(Rf, base, m)
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H): gd.line((0, y, W, y), fill=(0, 0, 0, int(170 * max(0, (y - H * 0.35) / (H * 0.65)))))
    base = base.convert('RGBA'); base.alpha_composite(g)
    ImageDraw.Draw(base).line((W // 2 + 90, 0, W // 2 - 90, H), fill=(255, 255, 255), width=6)
    p = writer('/home/claude/gvm/c_title.mp4')
    for f in range(n):
        t = f / FPS; im = base.copy(); d = ImageDraw.Draw(im)
        u = fade(t / 0.5); s = 1.6 - 0.6 * u
        ctext(d, (W / 2, H / 2 - 80), 'VS', Mi(int(220 * s)), (255, 255, 255), sw=8)
        if t > 0.4:
            d.rounded_rectangle((W / 2 - 220, 640, W / 2 + 220, 690), 25, fill=(0, 0, 0, 170)); ctext(d, (W / 2, 665), '実データでシミュレーション', Fb(28), GOLD)
            ctext(d, (W / 2, 775), '巨人  vs  蚊の大群', Mi(110), PALE, sw=4)
            ctext(d, (W / 2, 890), '身長50mの巨人は、何匹の蚊まで耐えられる？', Mi(52), GOLD, sw=3)
            ctext(d, (W / 2, 960), 'A 50-METER GIANT  vs  A SWARM OF MOSQUITOES', Fb(26), (220, 220, 225))
        ctext(d, (330, 120), '蚊', Mi(64), MOS_C, sw=4); ctext(d, (W - 330, 120), '巨人', Mi(64), GIANT_C, sw=4)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, 'intro')]

GROWS = [('身長', '50m', '人の約29倍'), ('体重', '約1,600t', '約2万3000倍'), ('血液', '約12万L', '約2万3000倍')]
MROWS = [('体長', '約5mm', ''), ('1回に吸う血', '約0.005mL', ''), ('針の長さ', '約2mm', '')]
def scene_stats():
    t1 = 0.5; t2 = t1 + D['stats1'] + 0.4; dur = t2 + D['stats2'] + 1.0; n = int(dur * FPS)
    bg = cover_im(giant_shot((0, 30, 12)), W, H, blur=30, dark=0.3).convert('RGBA')
    pw, ph = 760, 330
    gp = cover_im(giant_shot((-6, 25, 9), ruler=True), pw, ph, fx=0.5, fy=0.35); mp = mosquito_panel(pw, ph)
    p = writer('/home/claude/gvm/c_stats.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im)
        ctext(d, (W / 2, 70), 'データ比較', Mi(60), PALE); ctext(d, (W / 2, 120), 'DATA', Fb(24), (200, 200, 205))
        for side, (x0, photo, name, col, ts, rows, key) in enumerate([(130, gp, '巨人', GIANT_C, t1, GROWS, 'stats1'), (W - 130 - pw, mp, '蚊', MOS_C, t2, MROWS, 'stats2')]):
            if t < ts: continue
            im.paste(photo, (x0, 170)); d.rectangle((x0, 170, x0 + pw, 170 + ph), outline=col, width=5)
            ctext(d, (x0 + pw / 2, 545), name, Mi(56), col)
            for r, row in enumerate(rows):
                if t < ts + 1.0 + r * (D[key] - 1.5) / 3: continue
                y = 640 + r * 125
                d.rounded_rectangle((x0, y, x0 + pw, y + 105), 14, fill=(10, 12, 18, 215))
                d.text((x0 + 30, y + 52), row[0], font=Fb(28), fill=(200, 200, 205), anchor='lm')
                d.text((x0 + 250, y + 52), row[1], font=Fo(46), fill=PALE, anchor='lm')
                if row[2]: d.text((x0 + pw - 30, y + 52), row[2], font=Fb(26), fill=col, anchor='rm')
        if t1 + D['stats1'] * 0.35 < t < t2:
            d.rounded_rectangle((W / 2 + 60, 300, W - 160, 520), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
            ctext(d, (W * 0.73, 360), '大きさが29倍になると', Fo(40), PALE)
            ctext(d, (W * 0.73, 450), '29×29×29 = 約2万3000倍', Fo(52), GOLD)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t1, 'stats1'), (t2, 'stats2')]

def scene_skin():
    t1 = 0.5; t2 = t1 + D['skin'] + 0.8; dur = t2 + D['rule'] + 1.0; n = int(dur * FPS)
    bg = Image.new('RGBA', (W, H), (16, 18, 26, 255))
    bg2 = cover_im(giant_shot((0, 30, 12), M1, 300), W, H, dark=0.35).convert('RGBA')
    mos = draw_mosquito(120)
    RULES = [('蚊', '巨人の体にとまって、血を吸おうとする', 0.05), ('巨人', '手でたたいて、蚊を倒す', 0.30), ('蚊', '吸った血が全体の3割に届いたら勝ち', 0.50), ('巨人', '蚊がいなくなるまで耐えたら勝ち', 0.72)]
    p = writer('/home/claude/gvm/c_skin.mp4')
    for f in range(n):
        t = f / FPS
        if t < t2 - 0.3:
            im = bg.copy(); d = ImageDraw.Draw(im); u = (t - t1) / D['skin']
            ctext(d, (W / 2, 80), '蚊の針は、血管まで届く？', Mi(64), GOLD, sw=3)
            # 左：ふつうの人
            x0, x1 = 160, 900; ytop = 340
            ctext(d, ((x0 + x1) / 2, 170), 'ふつうの人', Fo(48), PALE)
            sk = 150                                         # 1〜2mm → 150px（1mmあたり 約100px）
            d.rectangle((x0, ytop, x1, ytop + sk), fill=(232, 190, 160)); d.text((x0 + 16, ytop + sk / 2), '皮膚 1〜2mm', font=Fo(34), fill=(80, 40, 30), anchor='lm')
            d.rectangle((x0, ytop + sk, x1, H - 160), fill=(200, 120, 110))
            d.rounded_rectangle((x0 + 60, ytop + sk + 20, x1 - 60, ytop + sk + 56), 18, fill=(190, 30, 40)); d.text((x1 - 70, ytop + sk + 38), '血管', font=Fo(28), fill=(255, 255, 255), anchor='rm')
            nx = (x0 + x1) / 2; nl = 200 * min(1, max(0, u * 3))
            d.line((nx, ytop - 60, nx, ytop - 60 + 60 + nl), fill=(30, 30, 30), width=6); im.alpha_composite(mos, (int(nx - 112), int(ytop - 125)))
            d.text((nx + 20, ytop - 40), '針 約2mm', font=Fo(34), fill=PALE, anchor='lm')
            if u > 0.33: ctext(d, ((x0 + x1) / 2, H - 110), '届く！', Fo(64), (120, 230, 120), sw=3)
            # 右：巨人
            x0, x1 = W - 900, W - 160
            if u > 0.42:
                ctext(d, ((x0 + x1) / 2, 170), '巨人（29倍）', Fo(48), GIANT_C)
                d.rectangle((x0, ytop, x1, H - 160), fill=(232, 190, 160))
                d.text((x0 + 16, ytop + 60), '皮膚 3〜6cm', font=Fo(40), fill=(80, 40, 30), anchor='lm')
                d.text((x0 + 16, ytop + 120), '（人の約29倍の厚さ）', font=Fb(28), fill=(110, 60, 40), anchor='lm')
                ctext(d, ((x0 + x1) / 2, H - 200), '↓ 血管は、ずっと下', Fo(34), (140, 60, 50))
                nx = (x0 + x1) / 2 + 120; nl = 200 * min(1, max(0, (u - 0.5) * 4))
                d.line((nx, ytop - 60, nx, ytop - 60 + 60 + nl * 0.2), fill=(30, 30, 30), width=6); im.alpha_composite(mos, (int(nx - 112), int(ytop - 125)))
                d.text((nx + 20, ytop - 40), '針 約2mm', font=Fo(34), fill=PALE, anchor='lm')
                if u > 0.75: ctext(d, ((x0 + x1) / 2, H - 110), '届かない！', Fo(64), (255, 90, 90), sw=3)
            d.text((W - 24, H - 18), '※厚さ・長さは目安。皮膚の厚さは場所によって違います', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        else:
            im = bg2.copy(); d = ImageDraw.Draw(im)
            ctext(d, (W / 2, 150), 'ルール', Mi(80), PALE, sw=3); ctext(d, (W / 2, 220), 'RULES', Fb(26), (210, 210, 215))
            for r, (who, txt, fr) in enumerate(RULES):
                if t < t2 + D['rule'] * fr: continue
                y = 310 + r * 150; col = MOS_C if who == '蚊' else GIANT_C
                d.rounded_rectangle((200, y, W - 200, y + 120), 18, fill=(10, 12, 18, 225), outline=GOLD if r >= 2 else None, width=4 if r >= 2 else 0)
                d.rounded_rectangle((230, y + 25, 390, y + 95), 14, fill=col); ctext(d, (310, y + 60), who, Fo(40), (20, 20, 24))
                d.text((430, y + 60), txt, font=Fo(46), fill=PALE, anchor='lm')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t1, 'skin'), (t2, 'rule')]

def seg_map(segs):
    out = []; v = 0.0
    for s0, s1, sp in segs: out.append((v, v + (s1 - s0) / sp, s0, sp)); v += (s1 - s0) / sp
    return out, v
def v2s(vt, sm):
    for v0, v1, s0, sp in sm:
        if vt < v1: return s0 + (vt - v0) * sp, sp
    v0, v1, s0, sp = sm[-1]; return s0 + (v1 - v0) * sp, sp
def scene_battle(M, title, segs, camk, cues, out, ruler_until=0):
    sm, dur = seg_map(segs); n = int(dur * FPS)
    caps = [(vt, vt + D[k] + 0.6, C.CAP[k]) for vt, k in cues if k in C.CAP]
    cs = None; sts = []; p = writer(out)
    for f in range(n):
        vt = f / FPS; st, sp = v2s(vt, sm)
        for (va, ma, za), (vb, mb, zb) in zip(camk, camk[1:]):
            if va <= vt < vb: break
        else: va, ma, za = camk[-1]; vb, mb, zb = va + 1, ma, za
        u = (lambda x: x * x * (3 - 2 * x))(min(1, max(0, (vt - va) / max(0.01, min(2.5, vb - va)))))
        tx, ty = ma[0] + (mb[0] - ma[0]) * u, ma[1] + (mb[1] - ma[1]) * u
        if cs is None: cs = [tx, ty]
        cs[0] += (tx - cs[0]) * 0.1; cs[1] += (ty - cs[1]) * 0.1
        ppm = za + (zb - za) * u
        cap = next((c for a0, a1, c in caps if a0 <= vt < a1), None)
        capcol = GOLD if cap and ('勝利' in cap or '届かない' in cap) else PALE
        im = GR.render(M, st, (cs[0], cs[1], ppm), dict(round=title, speed=sp, cap=cap, capcol=capcol, ruler=vt < ruler_until), f=f, speed=sp)
        sts.append(round(st, 3)); p.stdin.write(im.tobytes())
        if f % 300 == 0: print(out, f, n, flush=True)
    p.stdin.close(); p.wait()
    json.dump(dict(st=sts), open(out.replace('.mp4', '_st.json'), 'w'))
    return dur, cues

R1_SEGS = [(0, 10, 1.0), (10, 22, 1.0), (22, 30, 1.0), (30, 36, 1.0), (36, 4086, 300.0), (4086, 4146, 12.0), (4146, 4152, 1.0)]
R1_CAM = [(0, (-8, 25, 13.0)), (9.0, (0, 32, 15.0)), (21.0, (0, 40, 38.0)), (30.0, (0, 38, 30.0)), (36.0, (0, 32, 15.0)), (54.5, (0, 33, 17.0))]
R1_CUES = [(0.3, 'r1a'), (10.3, 'r1b'), (22.3, 'r1c'), (30.2, 'r1d'), (36.3, 'r1e'), (39.0, 'r1f'), (54.7, 'r1g')]
R2_SEGS = [(0, 10, 1.0), (10, 22, 1.0), (22, 30, 1.0), (30, 3630, 300.0), (3630, 280000, 25000.0), (280000, 285700, 500.0), (285700, 285736, 4.0)]
R2_CAM = [(0, (0, 30, 12.0)), (9.0, (0, 32, 15.0)), (21.0, (0, 40, 38.0)), (30.0, (0, 32, 15.0)), (53.0, (0, 36, 24.0)), (64.4, (0, 34, 20.0))]
R2_CUES = [(0.3, 'r2a'), (10.3, 'r2b'), (22.3, 'r2c'), (30.3, 'r2d'), (45.3, 'r2e'), (53.0, 'r2f'), (72.6, 'r2g')]
def _cam(lst): return [(v, (c[0], c[1]), c[2]) for v, c in lst]

def scene_card(key, title, lines, bg, out, big=None, sub=None):
    dur = 0.6 + D[key] + 0.8; n = int(dur * FPS); p = writer(out)
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im); u = fade(t / 0.4)
        ctext(d, (W / 2, 250), title, Fb(38), (220, 220, 225))
        if big: ctext(d, (W / 2, 390), big, Mi(int(140 * (1.3 - 0.3 * u))), GOLD, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 580 + r * 120
            d.rounded_rectangle((W / 2 - 560, y - 48, W / 2 + 560, y + 48), 16, fill=(10, 12, 18, 220))
            d.text((W / 2 - 520, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm')
            d.text((W / 2 + 520, y), val, font=Fo(52), fill=col, anchor='rm')
        if sub: d.text((W - 24, H - 18), sub, font=Fb(20), fill=(200, 200, 205), anchor='rs')
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.6, key)]
def blur_bg(M, t, cam):
    return ImageEnhance.Brightness(GR.render(M, t, cam, dict(off=True), f=0).filter(ImageFilter.GaussianBlur(12))).enhance(0.4).convert('RGBA')

TABLE = [('10億匹', '2%', PALE), ('50億匹', '10%', PALE), ('100億匹', '20%  まだセーフ', PALE), ('約150億匹', '30%  危険ライン', GOLD)]
def scene_sweep():
    t0 = 0.5; dd = D['sweep']; dur = t0 + dd + 1.5; n = int(dur * FPS)
    bg = blur_bg(M2, 30000, (0, 32, 14))
    reveal = [t0 + dd * x for x in (0.42, 0.55, 0.66, 0.84)]
    p = writer('/home/claude/gvm/c_sweep.mp4')
    for f in range(n):
        t = f / FPS; im = bg.copy(); d = ImageDraw.Draw(im)
        ctext(d, (W / 2, 120), 'もし、巨人の皮膚が人と同じ薄さだったら？', Mi(64), GOLD, sw=3)
        ctext(d, (W / 2, 190), '蚊の数と、吸われる血の割合（全体 約12万L）', Fb(30), (220, 220, 225))
        for r, (ns, res, col) in enumerate(TABLE):
            if t < reveal[r]: continue
            y = 300 + r * 150; last = r == 3
            d.rounded_rectangle((260, y, W - 260, y + 120), 18, fill=(10, 12, 18, 225), outline=GOLD if last else None, width=5 if last else 0)
            d.text((310, y + 60), f'蚊 {ns}', font=Fo(56), fill=MOS_C, anchor='lm')
            d.text((W - 310, y + 60), res, font=Fo(60), fill=col, anchor='rm')
        if t > reveal[3] + 0.5: ctext(d, (W / 2, 990), '※1回0.005mL、体にとまれる数やたたく速さは目安で計算', Fb(28), (225, 225, 230))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(t0, 'sweep')]

def scene_outro():
    dur = 0.5 + D['outro'] + 2.0; n = int(dur * FPS)
    base = cover_im(giant_shot((-8, 25, 13)), W, H, dark=0.45).convert('RGBA')
    p = writer('/home/claude/gvm/c_outro.mp4')
    for f in range(n):
        t = f / FPS; im = base.copy(); d = ImageDraw.Draw(im); u = (t - 0.5) / D['outro']
        if u < 0.62:
            ctext(d, (W / 2, 200), '本当の巨人の、もっと大きな問題', Mi(64), PALE, sw=4)
            if u > 0.12:
                d.rounded_rectangle((260, 330, W / 2 - 40, 620), 24, fill=(10, 12, 18, 225)); ctext(d, (W / 4 + 110, 400), '重さ', Fo(48), PALE); ctext(d, (W / 4 + 110, 520), '× 2万3000', Fo(80), (255, 110, 110))
            if u > 0.24:
                d.rounded_rectangle((W / 2 + 40, 330, W - 260, 620), 24, fill=(10, 12, 18, 225)); ctext(d, (3 * W / 4 - 110, 400), '骨の強さ', Fo(48), PALE); ctext(d, (3 * W / 4 - 110, 520), '× 約800', Fo(80), (120, 200, 255))
            if u > 0.38: ctext(d, (W / 2, 760), '→ 自分の重さで、骨が折れてしまうかも！', Mi(56), GOLD, sw=4)
            d.text((W - 24, H - 18), '※「二乗三乗の法則」。強さは骨の断面積（29×29）に比例すると考えた場合', font=Fb(20), fill=(200, 200, 205), anchor='rs')
        else:
            ctext(d, (W / 2, 380), '巨人と蚊、どっちが勝つと思った？', Mi(80), PALE, sw=4)
            ctext(d, (W / 2, 490), 'コメントで教えてください', Mi(54), GOLD, sw=3)
            if u > 0.82:
                d.rounded_rectangle((W / 2 - 520, 620, W / 2 + 520, 800), 24, fill=(10, 12, 18, 225), outline=GOLD, width=4)
                ctext(d, (W / 2, 670), '次の対決は？', Fo(52), PALE); ctext(d, (W / 2, 750), 'リクエスト募集中！', Fo(44), GOLD)
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, [(0.5, 'outro')]

if __name__ == '__main__':
    which = sys.argv[1]; res = {}
    if which == 'static':
        res['title'] = scene_title(); res['stats'] = scene_stats(); res['skin'] = scene_skin(); res['sweep'] = scene_sweep(); res['outro'] = scene_outro()
        res['res1'] = scene_card('res1', 'RESULT  蚊1億匹', [('吸われた血', '0L', BLOOD_C), ('たたいて倒した蚊', '約2200万匹', GIANT_C), ('あきらめた蚊', '約7800万匹', MOS_C)], blur_bg(M1, 600, (0, 32, 15)), '/home/claude/gvm/c_res1.mp4', big='巨人の完全勝利')
        res['res2'] = scene_card('res2', 'RESULT  皮膚の薄い巨人 vs 蚊200億匹', [('危険ラインまで', '約79時間', BLOOD_C), ('吸われた血', '約3万5000L', PALE), ('刺された回数', '約70億回', MOS_C)], blur_bg(M2, 200000, (0, 32, 15)), '/home/claude/gvm/c_res2.mp4', big='蚊の勝利')
    elif which == 'r1':
        res['r1'] = scene_battle(M1, '1回戦  蚊1億匹 vs 巨人', R1_SEGS, _cam(R1_CAM), R1_CUES, '/home/claude/gvm/c_r1.mp4', ruler_until=8.5)
    elif which == 'r2':
        res['r2'] = scene_battle(M2, '決勝戦  蚊200億匹 vs 皮膚の薄い巨人', R2_SEGS, _cam(R2_CAM), R2_CUES, '/home/claude/gvm/c_r2.mp4')
    json.dump(res, open(f'/home/claude/gvm/scene_{which}.json', 'w'))
    print('done', which)
