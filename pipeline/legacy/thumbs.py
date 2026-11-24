import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter

W, H = 1280, 720
FB = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
def F(sz): return ImageFont.truetype(FB, sz, index=0)

def fractal(w, h, seed, oct=6):
    g = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        k = 3 * 2 ** o
        a = g.random((k, k)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        tot += amp; amp *= 0.55
    acc /= tot; return (acc - acc.min()) / (acc.max() - acc.min())

def pal(v, stops):
    xs = [s[0] for s in stops]
    return np.stack([np.interp(v, xs, [s[1][i] for s in stops]) for i in range(3)], -1)

FIRE = [(0, (0, 0, 0)), (0.3, (120, 10, 0)), (0.55, (240, 80, 0)), (0.75, (255, 170, 30)), (0.9, (255, 235, 140)), (1, (255, 255, 255))]
ELEC = [(0, (0, 0, 0)), (0.35, (10, 20, 120)), (0.6, (40, 120, 255)), (0.8, (140, 220, 255)), (1, (255, 255, 255))]
PSY = [(0, (0, 0, 0)), (0.35, (60, 0, 90)), (0.6, (200, 40, 220)), (0.8, (255, 140, 240)), (1, (255, 255, 255))]

def burst_bg(cx, cy, stops, seed, rays=46):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.sqrt(dx * dx + dy * dy); th = np.arctan2(dy, dx)
    n = fractal(W, H, seed)
    ray = (np.sin(th * rays + 3 * n) * 0.5 + 0.5) ** 6
    core = np.exp(-(r / 260) ** 1.4)
    v = np.clip(core * 1.15 + ray * 0.35 * np.exp(-r / 900) + (n - 0.5) * 0.35 * core + 0.05, 0, 1)
    img = pal(v, stops)
    vign = np.clip(1 - (np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 1.2) ** 2, 0.15, 1)
    return np.clip(img * vign[..., None], 0, 255)

def lightning(img, x0, y0, x1, y1, seed, col=(170, 230, 255), w=6, depth=6):
    g = random.Random(seed)
    def seg(a, b, d):
        if d == 0: return [a, b]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        mx += g.uniform(-0.22, 0.22) * L; my += g.uniform(-0.22, 0.22) * L
        return seg(a, (mx, my), d - 1)[:-1] + seg((mx, my), b, d - 1)
    pts = seg((x0, y0), (x1, y1), depth)
    glow = Image.new('RGB', img.size, (0, 0, 0)); d = ImageDraw.Draw(glow)
    d.line(pts, fill=col, width=w * 4)
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    img = Image.fromarray(np.clip(np.asarray(img, np.float32) + np.asarray(glow, np.float32) * 1.3, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img); d.line(pts, fill=col, width=w); d.line(pts, fill=(255, 255, 255), width=max(2, w // 2))
    return img

def text(img, s, x, y, size, fill=(255, 255, 255), inner=(0, 0, 0), outer=(255, 255, 255),
         i_w=10, o_w=20, rot=0, anchor='la', shadow=True, grad=None):
    f = F(size)
    d0 = ImageDraw.Draw(img)
    l, t, r, b = d0.textbbox((0, 0), s, font=f, stroke_width=o_w, anchor=anchor)
    pad = 30
    lay = Image.new('RGBA', (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay); o = (pad - l, pad - t)
    if outer: d.text(o, s, font=f, fill=outer, stroke_width=o_w, stroke_fill=outer, anchor=anchor)
    d.text(o, s, font=f, fill=inner, stroke_width=i_w, stroke_fill=inner, anchor=anchor)
    if grad:
        m = Image.new('L', lay.size, 0); ImageDraw.Draw(m).text(o, s, font=f, fill=255, anchor=anchor)
        gy = np.linspace(0, 1, lay.size[1])[:, None, None]
        top, bot = np.array(grad[0]), np.array(grad[1])
        gi = (top * (1 - gy) + bot * gy) * np.ones((1, lay.size[0], 1))
        gimg = Image.fromarray(gi.astype(np.uint8)).convert('RGBA'); gimg.putalpha(m)
        lay = Image.alpha_composite(lay, gimg)
    else:
        d.text(o, s, font=f, fill=fill, anchor=anchor)
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    px, py = int(x + l - pad), int(y + t - pad)
    if rot:
        px = int(x - lay.size[0] / 2); py = int(y - lay.size[1] / 2)
    if shadow:
        sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel('A').point(lambda a: int(a * 0.6)))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        img.paste(sh, (px + 8, py + 10), sh)
    img.paste(lay, (px, py), lay)

def arrow(img, x0, y0, x1, y1, col=(255, 30, 30), w=34):
    d = ImageDraw.Draw(img)
    ang = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0)
    def P(u, v): return (x0 + u * math.cos(ang) - v * math.sin(ang), y0 + u * math.sin(ang) + v * math.cos(ang))
    hl = 95
    poly = [P(0, -w / 2), P(L - hl, -w / 2), P(L - hl, -w * 1.7), P(L, 0), P(L - hl, w * 1.7), P(L - hl, w / 2), P(0, w / 2)]
    d.polygon(poly, fill=(255, 255, 255));
    poly2 = [P(8, -w / 2 + 8), P(L - hl + 4, -w / 2 + 8), P(L - hl + 4, -w * 1.7 + 14), P(L - 14, 0), P(L - hl + 4, w * 1.7 - 14), P(L - hl + 4, w / 2 - 8), P(8, w / 2 - 8)]
    d.polygon(poly2, fill=col)

def mystery_card(img, cx, cy, w, h, rot=0):
    lay = Image.new('RGBA', (w + 80, h + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    glow = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ImageDraw.Draw(glow).rounded_rectangle((20, 20, w + 60, h + 60), 30, fill=(255, 220, 60, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(16)); lay = Image.alpha_composite(lay, glow); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((40, 40, w + 40, h + 40), 24, fill=(255, 210, 40))
    d.rounded_rectangle((52, 52, w + 28, h + 28), 18, fill=(25, 10, 40))
    # silhouette blob (mysterious creature-free: just a glowing energy orb silhouette)
    n = fractal(w - 24, h - 24, 77, 4)
    yy, xx = np.mgrid[0:h - 24, 0:w - 24]
    r = np.sqrt(((xx - (w - 24) / 2) / (w * 0.4)) ** 2 + ((yy - (h - 24) * 0.55) / (h * 0.36)) ** 2)
    v = np.clip(1.2 - r - 0.25 * n, 0, 1) ** 1.3
    orb = pal(v, PSY).astype(np.uint8)
    o = Image.fromarray(orb).convert('RGBA'); o.putalpha(Image.fromarray((np.clip(v * 2, 0, 1) * 255).astype(np.uint8)))
    lay.paste(o, (52, 52), o)
    f = F(int(h * 0.62))
    d = ImageDraw.Draw(lay)
    d.text(((w + 80) / 2, (h + 80) / 2 + 6), '？', font=f, fill=(255, 255, 255), stroke_width=12, stroke_fill=(0, 0, 0), anchor='mm')
    d.rounded_rectangle((40, 18, 40 + 150, 74), 14, fill=(230, 20, 40))
    d.text((40 + 75, 46), '1位', font=F(38), fill=(255, 255, 255), anchor='mm')
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

def speedlines(img, cx, cy, n=90, seed=1, col=(255, 255, 255, 90)):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); g = random.Random(seed)
    for _ in range(n):
        a = g.uniform(0, 2 * math.pi); r0 = g.uniform(420, 600); r1 = 1600; w = g.uniform(0.006, 0.02)
        d.polygon([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)),
                   (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))], fill=col)
    img.paste(lay, (0, 0), lay)

# ================= A: ランキング + 隠された1位 =================
def thumb_a(path):
    bg = burst_bg(380, 380, FIRE, 3)
    img = Image.fromarray(bg.astype(np.uint8))
    speedlines(img, 380, 380, seed=2)
    for s, (a, b) in enumerate([((380, 380), (60, 40)), ((380, 380), (20, 600)), ((380, 380), (700, 700))]):
        img = lightning(img, *a, *b, seed=s + 10, col=(255, 230, 150), w=5)
    text(img, '最強の技', 34, 60, 150, inner=(0, 0, 0), outer=(255, 255, 255), i_w=14, o_w=26, grad=((255, 255, 255), (255, 230, 120)))
    text(img, 'TOP5', 40, 250, 230, inner=(120, 0, 0), outer=(255, 255, 255), i_w=14, o_w=26, grad=((255, 240, 60), (255, 120, 0)))
    # bottom banner
    d = ImageDraw.Draw(img)
    d.polygon([(0, 560), (760, 560), (720, 680), (0, 680)], fill=(0, 0, 0))
    d.polygon([(0, 572), (740, 572), (704, 668), (0, 668)], fill=(225, 20, 40))
    text(img, '1位はまさかの…', 40, 578, 76, inner=(0, 0, 0), outer=None, i_w=8, shadow=False)
    mystery_card(img, 1035, 380, 330, 420, rot=-6)
    arrow(img, 700, 470, 860, 400)
    img.save(path)

# ================= B: 一撃ダメージ =================
def hp_bar(img, x, y, w, frac, label='HP'):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x - 8, y - 8, x + w + 8, y + 62), 18, fill=(255, 255, 255))
    d.rounded_rectangle((x, y, x + w, y + 54), 12, fill=(30, 30, 40))
    d.text((x + 18, y + 27), label, font=F(36), fill=(255, 200, 40), anchor='lm')
    bx = x + 100; bw = w - 118
    d.rounded_rectangle((bx, y + 12, bx + bw, y + 42), 10, fill=(70, 70, 80))
    # ghost (just lost) part
    d.rounded_rectangle((bx, y + 12, bx + bw * 0.97, y + 42), 10, fill=(255, 210, 60))
    if frac > 0: d.rounded_rectangle((bx, y + 12, bx + max(14, bw * frac), y + 42), 10, fill=(230, 30, 30))
    d.rectangle((bx + bw * 0.02, y + 12, bx + bw * 0.97, y + 42), fill=(255, 210, 60, ))

def thumb_b(path):
    bg = burst_bg(840, 330, ELEC, 5, rays=60)
    img = Image.fromarray(bg.astype(np.uint8))
    speedlines(img, 840, 330, n=110, seed=4, col=(200, 240, 255, 80))
    for s, tgt in enumerate([(1280, 0), (1280, 720), (560, 0), (480, 720), (1280, 360)]):
        img = lightning(img, 840, 330, *tgt, seed=s + 30, w=6)
    # shattered HP bar
    hp_bar(img, 650, 560, 580, 0.02)
    text(img, '0', 1170, 520, 120, inner=(0, 0, 0), outer=(255, 255, 255), i_w=10, o_w=18, rot=10, fill=(255, 40, 40))
    text(img, '一撃で', 40, 40, 120, inner=(0, 0, 0), outer=(255, 255, 255), i_w=12, o_w=22, grad=((255, 255, 255), (200, 230, 255)))
    text(img, '全滅', 30, 175, 260, inner=(0, 0, 60), outer=(255, 255, 255), i_w=16, o_w=28, grad=((255, 250, 90), (255, 140, 0)))
    d = ImageDraw.Draw(img)
    d.polygon([(30, 500), (560, 500), (530, 610), (30, 610)], fill=(0, 0, 0))
    d.polygon([(38, 510), (545, 510), (518, 600), (38, 600)], fill=(20, 110, 255))
    text(img, 'ダメージ ？？？', 58, 510, 68, inner=(0, 0, 0), outer=None, i_w=8, shadow=False)
    img.save(path)

# ================= C: 禁止・警告 =================
def caution_tape(img, y, rot, txt):
    lay = Image.new('RGBA', (2000, 110), (255, 205, 0, 255)); d = ImageDraw.Draw(lay)
    for x in range(-200, 2000, 120):
        d.polygon([(x, 0), (x + 60, 0), (x - 50, 110), (x - 110, 110)], fill=(20, 20, 20))
    d.rectangle((0, 22, 2000, 88), fill=(255, 205, 0))
    for x in range(40, 2000, 520):
        d.text((x, 55), txt, font=F(52), fill=(20, 20, 20), anchor='lm')
    lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel('A').point(lambda a: int(a * .5)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img.paste(sh, (int(W / 2 - lay.size[0] / 2) + 6, int(y - lay.size[1] / 2) + 12), sh)
    img.paste(lay, (int(W / 2 - lay.size[0] / 2), int(y - lay.size[1] / 2)), lay)

def thumb_c(path):
    bg = burst_bg(900, 380, PSY, 8, rays=40)
    img = Image.fromarray(bg.astype(np.uint8))
    speedlines(img, 900, 380, n=80, seed=6, col=(255, 200, 255, 70))
    for s, tgt in enumerate([(1280, 100), (1100, 720), (600, 0)]):
        img = lightning(img, 900, 380, *tgt, seed=s + 50, col=(255, 160, 255), w=5)
    caution_tape(img, 80, 4, '危険  DANGER  使用注意')
    text(img, '絶対に', 50, 170, 110, inner=(0, 0, 0), outer=(255, 255, 255), i_w=12, o_w=22)
    text(img, '使うな', 40, 285, 240, inner=(90, 0, 0), outer=(255, 255, 255), i_w=16, o_w=28, grad=((255, 90, 90), (200, 0, 20)))
    d = ImageDraw.Draw(img)
    d.polygon([(30, 580), (620, 580), (590, 685), (30, 685)], fill=(0, 0, 0))
    d.polygon([(38, 590), (604, 590), (578, 675), (38, 675)], fill=(255, 205, 0))
    text(img, '使った瞬間に負ける技', 56, 594, 56, inner=(0, 0, 0), outer=None, i_w=0, fill=(20, 20, 20), shadow=False)
    # ban stamp
    lay = Image.new('RGBA', (360, 360), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.ellipse((20, 20, 340, 340), outline=(255, 255, 255), width=46)
    dl.ellipse((30, 30, 330, 330), outline=(230, 20, 40), width=30)
    dl.line((80, 280, 280, 80), fill=(255, 255, 255), width=56); dl.line((85, 275, 275, 85), fill=(230, 20, 40), width=32)
    lay = lay.rotate(-12, resample=Image.BICUBIC)
    img.paste(lay, (1280 - 400, 230), lay)
    img.save(path)

if __name__ == '__main__':
    thumb_a('/home/claude/thumb_A_ranking.png')
    thumb_b('/home/claude/thumb_B_ichigeki.png')
    thumb_c('/home/claude/thumb_C_kinshi.png')
