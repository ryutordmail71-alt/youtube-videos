import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, shift as nd_shift
from cine_thumbs import fractal, pal, FIRE, ICE, WATER, BEAM, jet_field, smoke, particles, base_bg, composite, W, H, XX, YY
from cine_thumbs_v3 import ridged, god_rays, bokeh, streaks, finish, post, layout2

# ---------------- silhouette ----------------
def figure_mask(foot, h, facing, arm_ang, coat=True):
    """side-view firing stance; returns (mask HxW float, hand_xy)"""
    S = 2
    im = Image.new('L', (W * S, H * S), 0); d = ImageDraw.Draw(im)
    fx, fy = foot
    def P(x, y):  # local units (facing right, y up negative) -> pixels
        return ((fx + x * h * facing) * S, (fy + y * h) * S)
    def limb(pts, w):
        pp = [P(*p) for p in pts]
        d.line(pp, fill=255, width=int(w * h * S), joint='curve')
        for p in pp: r = w * h * S / 2; d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=255)
    # legs (back leg straight & braced, front leg bent)
    limb([(0.00, -0.50), (-0.14, -0.26), (-0.27, -0.02)], 0.085)
    limb([(0.06, -0.50), (0.21, -0.29), (0.22, -0.02)], 0.09)
    d.polygon([P(-0.33, 0), P(-0.20, 0), P(-0.22, -0.05), P(-0.31, -0.05)], fill=255)
    d.polygon([P(0.17, 0), P(0.33, 0), P(0.30, -0.05), P(0.18, -0.06)], fill=255)
    # torso leaning forward
    d.polygon([P(-0.06, -0.47), P(0.11, -0.47), P(0.19, -0.80), P(0.00, -0.82)], fill=255)
    limb([(0.02, -0.50), (0.08, -0.62), (0.10, -0.78)], 0.15)
    # coat tail flowing back
    if coat:
        d.polygon([P(-0.05, -0.62), P(0.08, -0.55), P(-0.10, -0.30), P(-0.30, -0.24), P(-0.20, -0.42)], fill=255)
    # neck + head (hood)
    limb([(0.10, -0.80), (0.13, -0.86)], 0.07)
    hx, hy = P(0.15, -0.93); r = 0.072 * h * S
    d.ellipse((hx - r, hy - r * 1.1, hx + r, hy + r * 1.05), fill=255)
    d.polygon([P(0.06, -0.97), P(0.12, -1.02), P(0.02, -0.88)], fill=255)  # hood peak back
    # arms: both pointing along arm_ang (screen angle, radians), from shoulder
    sx, sy = 0.13, -0.79
    ca, sa = math.cos(arm_ang), math.sin(arm_ang)
    dx, dy = ca * facing, sa      # local-direction (facing-normalised)
    L1, L2 = 0.20, 0.19
    for off, wid in ((0.0, 0.065), (0.025, 0.06)):
        e = (sx + dx * L1, sy + dy * L1 + off)
        hnd = (e[0] + dx * L2, e[1] + dy * L2 + off * 0.5)
        limb([(sx, sy + off), e, hnd], wid)
    hand = (fx + hnd[0] * h * facing, fy + hnd[1] * h)
    m = np.asarray(im.filter(ImageFilter.GaussianBlur(1)).resize((W, H), Image.LANCZOS), np.float32) / 255
    return m, hand

def apply_silhouette(img, m, light_xy, rim_col, rim=1.6):
    # dark body, rim light on the side facing the light
    cy, cx = np.nonzero(m > 0.5); mx, my = cx.mean(), cy.mean()
    lx, ly = light_xy[0] - mx, light_xy[1] - my; n = math.hypot(lx, ly) + 1e-6
    sh = nd_shift(m, (-ly / n * 7, -lx / n * 7), order=1)
    edge = np.clip(m - sh, 0, 1)
    edge = gaussian_filter(edge, 1.5)
    body = np.array([7, 7, 9], np.float32)
    img = img * (1 - m[..., None]) + body * m[..., None]
    img += edge[..., None] * np.array(rim_col, np.float32) * rim
    img += gaussian_filter(edge, 8)[..., None] * np.array(rim_col, np.float32) * 0.5
    return img

def hand_flash(img, hand, col, r=90, k=1.6):
    g = np.exp(-(((XX - hand[0]) ** 2 + (YY - hand[1]) ** 2) / r ** 2))
    return img + g[..., None] * np.array(col, np.float32) * k

FOOT_Y = 1010

# ======================= moves =======================
def kaen(path):
    ang = math.radians(-30)
    m, hand = figure_mask((170, FOOT_Y), 600, 1, ang)
    bg = base_bg((16, 6, 3), (6, 3, 3))
    v, u, vv, wd = jet_field(hand[0], hand[1], ang, 1050, 30, 700, 11, turb=0.7, warp=1.5)
    v = v * (0.45 + 1.0 * ridged(61, 8)) + 0.25 * v * ridged(62, 20)
    sm, s = smoke(13, np.exp(-(vv / (wd * 1.7)) ** 2) * np.clip((u - 150) / 400, 0, 1) * (1 - np.exp(-(vv / (wd * 0.8)) ** 2)), (55, 44, 40), 1.0)
    bg = bg * (1 - s[..., None] * 0.5) + sm
    img = composite(bg, np.clip(v * 1.05, 0, 1.1), FIRE, 1.0)
    img += gaussian_filter(v, 110)[..., None] * np.array([255, 90, 20]) * 0.45
    img = apply_silhouette(img, m, hand, (255, 150, 60))
    img = hand_flash(img, hand, (255, 200, 120), 70, 1.4)
    img = god_rays(img, hand[0], hand[1], (255, 150, 60), thr=160, k=0.7)
    img = post(img, (12, 4, 0), seed=1, vign=0.6, expo=0.75)
    img = bokeh(img, 8, 3, (255, 140, 50), (0, 0, W, 1300), 6, 22, 0.05, 0.18)
    im = finish(img, None)
    particles(im, 380, 4, (255, 190, 90), (hand[0], 100, 1080, 1000), (1, 3.4), streak=(34, -22))
    layout2(im, 1, '', 'かえんほうしゃ', '推定温度', '？？？？', '℃', (255, 140, 40), path)

def bakuhatsu(path):
    m, hand = figure_mask((140, FOOT_Y), 470, 1, math.radians(-8))
    bg = base_bg((12, 6, 4), (3, 2, 2))
    cx, cy = 650, 640
    r = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    g = np.random.default_rng(5)
    Dn = np.zeros((H, W), np.float32)
    for i in range(110):
        a = g.uniform(0, 2 * np.pi); rr = 480 * g.random() ** 0.6
        bx, by = cx + rr * np.cos(a), cy + rr * np.sin(a) * 0.85
        br = g.uniform(90, 240) * (1.15 - rr / 800)
        Dn += np.exp(-(((XX - bx) ** 2 + (YY - by) ** 2) / br ** 2) * 2.2)
    nf = fractal(21, 8, 6)
    Dn = np.clip(Dn, 0, 3) * (0.7 + 0.6 * nf)
    T = np.clip(Dn / 3.0, 0, 1) ** 0.75 * np.exp(-(r / 600) ** 2) * (0.45 + 0.7 * nf ** 1.4) * (0.55 + 0.8 * ridged(63, 12))
    sm, s_ = smoke(23, np.clip(Dn / 1.5, 0, 1) * np.clip(r / 500, 0, 1), (60, 46, 40), 1.0)
    bg = bg * (1 - s_[..., None] * 0.7) + sm
    img = composite(bg, np.clip(T, 0, 1.15), FIRE, 1.05)
    ring = np.exp(-((r - 690) / 9) ** 2) * (0.35 + 0.65 * nf)
    img += gaussian_filter(ring, 4)[..., None] * np.array([255, 220, 190]) * 1.2
    img += gaussian_filter(ring, 30)[..., None] * np.array([255, 140, 60]) * 2.0
    img += gaussian_filter(T, 140)[..., None] * np.array([255, 100, 30]) * 0.5
    hz = np.exp(-((YY - FOOT_Y) / 26) ** 2) * np.exp(-((XX - cx) / 700) ** 2)
    img += hz[..., None] * np.array([255, 160, 80]) * 1.2
    dust, ds = smoke(24, np.exp(-((YY - FOOT_Y + 20) / 70) ** 2), (120, 80, 50), 1.0)
    img = img + dust * 0.8
    img = streaks(img, cx, cy, 160, 7, (255, 190, 120), 500, 700, width=(1, 4))
    img = apply_silhouette(img, m, (cx, cy), (255, 170, 90), rim=2.0)
    img = god_rays(img, cx, cy, (255, 170, 90), thr=160, k=0.7, step=0.045)
    img = post(img, (10, 4, 2), seed=2, vign=0.55, expo=0.7)
    img = bokeh(img, 10, 5, (255, 150, 70), (0, 0, W, 1150), 6, 22, 0.05, 0.18)
    im = finish(img, None)
    particles(im, 300, 6, (255, 190, 110), (0, 50, 1080, 1000), (1, 2.6))
    layout2(im, 2, '', 'だいばくはつ', '推定被害半径', '？？？', 'km', (255, 120, 50), path)

def fubuki(path):
    ang = math.radians(-18)
    m, hand = figure_mask((170, FOOT_Y), 580, 1, ang)
    bg = base_bg((14, 26, 40), (3, 7, 13))
    cx, cy = hand[0] + 40, hand[1] - 10
    big = fractal(31, 8, 3, w=W * 3, h=H)
    im_n = Image.fromarray((big * 255).astype(np.uint8)).rotate(-32, resample=Image.BICUBIC)
    n = np.asarray(im_n.crop((W, 0, 2 * W, H)), np.float32) / 255
    n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    # cone of blizzard from the hand toward upper-right
    ca, sa = math.cos(ang), math.sin(ang)
    u = (XX - cx) * ca + (YY - cy) * sa; vv = -(XX - cx) * sa + (YY - cy) * ca
    cone = np.exp(-(vv / (60 + 0.55 * np.clip(u, 0, None))) ** 2) * (u > -40) * np.exp(-np.clip(u, 0, None) / 1400)
    r = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    light = np.exp(-(r / 420) ** 2)
    fog = np.clip((n - 0.25) * 1.6, 0, 1) * (0.25 + 0.9 * cone) + cone * 0.45
    img = composite(bg, np.clip(fog, 0, 1.1), ICE, 1.0)
    img += light[..., None] * np.array([140, 200, 255]) * 0.7
    img = streaks(img, cx, cy, 420, 9, (200, 230, 255), 90, 900, width=(1, 3), alpha=(0.15, 0.7))
    img = apply_silhouette(img, m, (cx, cy), (170, 220, 255))
    img = hand_flash(img, hand, (220, 240, 255), 80, 1.6)
    img = god_rays(img, cx, cy, (170, 220, 255), thr=150, k=0.7, step=0.04)
    img = post(img, (0, 6, 16), bloom_thr=165, seed=3, vign=0.6)
    img = bokeh(img, 11, 11, (200, 230, 255), (0, 0, W, 1400), 6, 22, 0.05, 0.18)
    im = finish(img, None)
    particles(im, 1100, 8, (200, 225, 245), (-300, -100, 1080, 1750), (0.8, 2.2), streak=(70, -24), alpha=(40, 170))
    particles(im, 260, 9, (220, 238, 255), (-100, 0, 1080, 1750), (2, 6), streak=(170, -55), alpha=(20, 80))
    layout2(im, 3, '', 'ふぶき', '到達気温', '？？？', '℃', (140, 210, 255), path, prefix='−')

def hydro(path):
    ang = math.radians(-155)
    m, hand = figure_mask((900, FOOT_Y), 580, -1, ang)
    bg = base_bg((4, 12, 24), (2, 5, 10))
    v, u, vv, wd = jet_field(hand[0], hand[1], ang, 950, 30, 300, 41, turb=0.5, warp=1.0)
    v2, *_ = jet_field(hand[0], hand[1], ang, 950, 12, 80, 43, turb=0.2, warp=0.4)
    mist_mask = np.exp(-(vv / (wd * 2.6)) ** 2) * np.clip((u - 150) / 400, 0, 1)
    sm, s = smoke(44, mist_mask, (90, 150, 190), 0.8)
    bg = bg + sm
    img = composite(bg, np.clip(v + v2 * 0.8, 0, 1.2), WATER, 1.1)
    tx, ty = hand[0] + 950 * math.cos(ang), hand[1] + 950 * math.sin(ang)
    tx = max(tx, 90)
    rr = np.sqrt((XX - tx) ** 2 + (YY - ty) ** 2)
    sp = np.clip(1 - rr / 340, 0, 1) ** 1.5 * (0.5 + 0.8 * fractal(45, 8, 8))
    img += pal(np.clip(sp, 0, 1), WATER) * 0.9
    img += gaussian_filter(v, 90)[..., None] * np.array([40, 150, 255]) * 0.8
    img = streaks(img, tx, ty, 200, 12, (190, 235, 255), 110, 450, width=(1, 4))
    img = apply_silhouette(img, m, (tx, ty), (120, 200, 255))
    img = hand_flash(img, hand, (180, 230, 255), 70, 1.4)
    img = god_rays(img, tx, ty, (120, 200, 255), thr=160, k=0.7)
    img = post(img, (0, 4, 12), seed=4, vign=0.6)
    img = bokeh(img, 13, 13, (150, 210, 255), (0, 0, W, 1300), 6, 22, 0.05, 0.18)
    im = finish(img, None)
    particles(im, 520, 14, (210, 240, 255), (0, 150, 600, 800), (1, 4))
    particles(im, 220, 15, (190, 230, 255), (0, 150, 900, 1000), (1, 2.4), streak=(-60, -28))
    layout2(im, 4, '', 'ハイドロポンプ', '推定噴射圧', '？？？', '気圧', (80, 190, 255), path)

def hakai(path):
    ang = math.radians(-9)
    m, hand = figure_mask((140, FOOT_Y), 600, 1, ang)
    bg = base_bg((14, 7, 3), (4, 2, 3))
    v, u, vv, wd = jet_field(hand[0] - 20, hand[1], ang, 1200, 50, 230, 51, turb=0.25, warp=0.3)
    img = composite(bg, np.clip(v * 1.25, 0, 1.2), BEAM, 1.2)
    sheath = np.exp(-(vv / (wd * 2.2)) ** 2) * (0.5 + 0.5 * fractal(52, 7, 4)) * np.clip(u / 200, 0, 1)
    img += sheath[..., None] * np.array([255, 110, 20]) * 0.5
    fl = np.exp(-((YY - (hand[1] + (XX - hand[0]) * math.tan(ang))) / 5) ** 2) * np.clip((XX - hand[0]) / 100, 0, 1)
    img += fl[..., None] * np.array([255, 200, 140]) * 0.9
    img += gaussian_filter(v, 130)[..., None] * np.array([255, 120, 30]) * 0.9
    img = streaks(img, hand[0], hand[1], 200, 18, (255, 200, 120), 140, 700, width=(1, 3), alpha=(0.2, 0.8))
    img = apply_silhouette(img, m, hand, (255, 170, 80))
    img = hand_flash(img, hand, (255, 230, 170), 110, 1.8)
    img = god_rays(img, hand[0], hand[1], (255, 170, 80), thr=165, k=0.7, step=0.05)
    img = post(img, (10, 4, 0), seed=5, vign=0.55)
    img = bokeh(img, 10, 17, (255, 170, 80), (0, 0, W, 1300), 6, 22, 0.05, 0.18)
    im = finish(img, None)
    particles(im, 320, 17, (255, 220, 150), (hand[0], 300, 1080, 1000), (1, 2.6), streak=(90, -15))
    layout2(im, 5, '', 'はかいこうせん', '使用者への反動', '？？？', '', (255, 150, 50), path)

if __name__ == '__main__':
    out = '/home/claude/shorts_thumbs_v4'; os.makedirs(out, exist_ok=True)
    which = sys.argv[1:] or ['1', '2', '3', '4', '5']
    fns = {'1': (kaen, '1_kaenhousha'), '2': (bakuhatsu, '2_daibakuhatsu'), '3': (fubuki, '3_fubuki'),
           '4': (hydro, '4_hydropump'), '5': (hakai, '5_hakaikousen')}
    for w in which:
        f, n = fns[w]; f(f'{out}/{n}.png')
