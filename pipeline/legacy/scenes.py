import math, random, os, sys
import numpy as np
from scipy.ndimage import gaussian_filter
from engine import *

HZ = 860  # horizon line

def clouds(seed, horizon, scale=0.0016, warp=180, thr=0.42, soft=0.25, stretch=2.2):
    d = fbm(seed, sx=scale * 1024 / stretch, sy=scale * 1024, warp=warp, octaves=8)
    d = ss(thr, thr + soft, d)
    d *= ss(horizon + 40, horizon - 200, YY)      # fade toward horizon
    return d

def lit_clouds(base, dens, light_map, cloud_dark, light_col, rim_from=None, k=1.0):
    shade = 0.6 + 0.4 * gaussian_filter(dens, 6)
    col = cloud_dark * shade[..., None] + light_col * (light_map[..., None] * (0.6 + 0.8 * dens[..., None])) * k
    return blend(base, col, dens * 0.95)

def ground(base, horizon, seed, col_a, col_b, scale=0.012):
    wx, z = ground_coords(horizon)
    T = tile(seed, octaves=8)
    t = sample(T, wx * scale * 60, z * scale * 25)
    fine = sample(tile(seed + 1, octaves=8, base=8), wx * scale * 260, z * scale * 120)
    tex = 0.6 * t + 0.4 * fine
    col = col_a * (1 - tex[..., None]) + col_b * tex[..., None]
    fog = np.exp(-np.clip(YY - horizon, 0, None) / 160)[..., None]
    below = (YY > horizon).astype(np.float32)
    aa = ss(horizon - 1, horizon + 2, YY)
    return blend(base, col, aa) , tex, z

def ember_layer(n, seed, area, rmin=0.6, rmax=2.4, inten=(0.5, 1.0)):
    g = random.Random(seed)
    return dots_layer([(g.uniform(area[0], area[2]), g.uniform(area[1], area[3]), g.uniform(rmin, rmax), g.uniform(*inten)) for _ in range(n)])

# =========================================================
def kaen():
    img = sky(lin((8, 5, 5)), lin((30, 16, 12)), lin((70, 32, 16)), HZ)
    # flame jet
    ox, oy, ang, Lj = -80, 870, math.radians(-17), 1300
    ca, sa = math.cos(ang), math.sin(ang)
    u = (XX - ox) * ca + (YY - oy) * sa; v = -(XX - ox) * sa + (YY - oy) * ca
    w = 34 + 0.30 * np.clip(u, 0, None)
    Tw = tile(11, octaves=8); Tf = tile(12, octaves=8, base=6)
    warpv = (sample(Tw, u * 0.004 * 1024 / 4, v * 0.01 * 1024 / 4 + 50) - 0.5) * w * 1.6
    vv = v + warpv
    lick = sample(Tf, u * 0.0035 * 256 - 0, vv * 0.016 * 256)
    lick2 = sample(Tf, u * 0.009 * 256 + 400, vv * 0.03 * 256)
    body = np.exp(-(vv / w) ** 2 * 1.4) * ss(-10, 60, u) * ss(Lj * 1.05, Lj * 0.6, u)
    dens = np.clip(body * (0.35 + 0.9 * lick ** 1.5 + 0.35 * ridge(lick2, 3)), 0, 1.4)
    core = np.exp(-(vv / (w * 0.35)) ** 2) * ss(-10, 40, u) * ss(Lj * 0.9, Lj * 0.2, u)
    T = np.clip(dens * (0.95 - 0.35 * np.clip(u / Lj, 0, 1)) + core * 0.35, 0, 1)
    flame = blackbody(T) * 1.15
    # smoke above / around the far end
    sm = fbm(13, sx=0.6, sy=0.8, warp=120, octaves=8)
    smoke_d = ss(0.35, 0.75, sm) * np.exp(-((vv + w * 0.9) / (w * 1.8)) ** 2) * ss(200, 900, u) * (YY < HZ + 40)
    light = gaussian_filter(T ** 2, 160) * 6 + gaussian_filter(T ** 2, 50) * 2
    # sky clouds lit
    cd = clouds(21, HZ, thr=0.45)
    img = lit_clouds(img, cd, np.clip(light, 0, 3), lin((25, 18, 16)), C(1.2, 0.45, 0.12), k=0.7)
    img = blend(img, lin((30, 22, 20)) + C(0.9, 0.35, 0.08) * np.clip(light, 0, 2)[..., None] * 0.4, smoke_d * 0.85)
    # ground: scorched earth lit by flame
    img, tex, z = ground(img, HZ, 31, lin((18, 12, 10)), lin((70, 48, 36)))
    gl = gaussian_filter(T ** 2, 220) * 9 * (YY > HZ)
    img += (img * gl[..., None] * C(2.4, 1.0, 0.35)) * (YY > HZ)[..., None]
    burn = ss(0.62, 0.8, sample(tile(33, octaves=8, base=8), (XX - 540) * z / 900 * 3, z * 2.5)) * (YY > HZ + 6) * ss(HZ, HZ + 260, YY)
    burn *= np.clip(gaussian_filter(T, 120) * 6, 0, 1)
    img += blackbody(0.45 + 0.25 * burn)[..., :] * burn[..., None] * 0.9
    # flame on top
    img = img * (1 - np.clip(dens, 0, 1)[..., None] * 0.7) + flame
    img += C(1.0, 0.4, 0.1) * light[..., None] * 0.06
    # embers
    e = ember_layer(700, 4, (200, 150, 1080, 980))
    img += gaussian_filter(e, 1.2)[..., None] * C(6, 2.2, 0.4) + gaussian_filter(e, 5)[..., None] * C(2, 0.6, 0.1)
    img = bloom(img, 1.2)
    out = grade(img, expo=0.9, shadow=(0.02, 0.0, -0.01), seed=1)
    compose_text(out, 'かえんほうしゃ', '推定温度', '？？？？', '℃', (255, 140, 50), OUT + '/1_kaenhousha.png')

# =========================================================
def bakuhatsu():
    img = sky(lin((10, 8, 10)), lin((40, 22, 18)), lin((110, 50, 24)), HZ)
    cx, cy = 540, HZ - 10
    r = np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.0) ** 2)
    g = np.random.default_rng(5)
    D = np.zeros((H, W), np.float32)
    for i in range(160):
        a = g.uniform(math.pi, 2 * math.pi)                 # upper hemisphere
        rr = 430 * g.random() ** 0.55
        bx, by = cx + rr * math.cos(a), cy + rr * math.sin(a) * 1.05
        br = g.uniform(70, 200) * (1.2 - rr / 700)
        D += np.exp(-(((XX - bx) ** 2 + (YY - by) ** 2) / br ** 2) * 2.0)
    det = fbm(21, sx=1.6, sy=1.6, warp=60, octaves=8)
    det2 = ridge(fbm(22, sx=3.0, sy=3.0, octaves=8), 2.5)
    D = np.clip(D, 0, 3) * (0.6 + 0.7 * det) * (YY < cy + 30)
    T = np.clip(D / 3, 0, 1) ** 0.8 * np.exp(-(r / 520) ** 2) * (0.55 + 0.6 * det2)
    T = np.clip(T * 1.25, 0, 1)
    # outer smoke shell
    shell = np.clip(D / 1.2, 0, 1) * ss(250, 520, r) * (0.6 + 0.6 * det)
    light = gaussian_filter(T ** 2, 220) * 10 + gaussian_filter(T ** 2, 70) * 2
    cd = clouds(41, HZ - 120, thr=0.48, scale=0.0013)
    img = lit_clouds(img, cd, np.clip(light, 0, 3), lin((26, 20, 22)), C(1.3, 0.5, 0.15), k=0.8)
    # condensation shock ring in the sky
    ring = np.exp(-(((np.sqrt(((XX - cx) / 1.0) ** 2 + ((YY - (cy - 120)) / 0.42) ** 2)) - 760) / 14) ** 2)
    ring *= (0.4 + 0.8 * fbm(43, sx=2, sy=2)) * (YY < HZ - 20)
    img += ring[..., None] * C(1.3, 1.1, 1.0) * 0.8
    # ground
    img, tex, z = ground(img, HZ, 31, lin((14, 11, 10)), lin((60, 44, 34)))
    gl = (gaussian_filter(T ** 2, 260) * 14) * (YY > HZ)
    img += img * gl[..., None] * C(2.6, 1.2, 0.45)
    # dust wall racing out along the horizon
    dw = fbm(45, sx=0.9, sy=2.4, warp=90, octaves=8)
    dust = ss(0.35, 0.7, dw) * np.exp(-((YY - HZ + 10) / 55) ** 2) * ss(1000, 200, np.abs(XX - cx))
    img = blend(img, lin((90, 60, 40)) + C(1.4, 0.6, 0.2) * np.clip(light, 0, 2)[..., None] * 0.6, dust * 0.9)
    # fireball
    img = blend(img, lin((24, 18, 16)) + C(1.6, 0.6, 0.15) * np.clip(light, 0, 2)[..., None] * 0.35, shell * 0.9)
    img = img * (1 - np.clip(T * 1.6, 0, 1)[..., None] * 0.8) + blackbody(T) * 1.4
    # debris
    gr = random.Random(8); segs = []
    for _ in range(140):
        a = gr.uniform(math.pi * 1.02, math.pi * 1.98); r0 = gr.uniform(380, 560); L = gr.uniform(60, 260)
        segs.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + (r0 + L) * math.cos(a), cy + (r0 + L) * math.sin(a), gr.uniform(0.3, 1), gr.uniform(1, 3)))
    st = lines_layer(segs, 1)
    img += gaussian_filter(st, 0.8)[..., None] * C(5, 2.2, 0.6) + gaussian_filter(st, 6)[..., None] * C(2, 0.7, 0.1)
    e = ember_layer(500, 6, (0, 100, 1080, 950))
    img += gaussian_filter(e, 1.0)[..., None] * C(5, 2.0, 0.5)
    img = bloom(img, 1.1)
    out = grade(img, expo=0.85, shadow=(0.02, 0.0, -0.01), seed=2)
    compose_text(out, 'だいばくはつ', '推定被害半径', '？？？', 'km', (255, 125, 50), OUT + '/2_daibakuhatsu.png')

# =========================================================
def fubuki():
    img = sky(lin((40, 52, 66)), lin((92, 110, 128)), lin((150, 168, 182)), HZ)
    sun = gauss(800, 330, 260) ; img += sun[..., None] * C(0.9, 1.0, 1.1) * 0.8
    cd = clouds(51, HZ, thr=0.4, scale=0.0012, warp=220)
    img = lit_clouds(img, cd, sun * 1.5, lin((70, 84, 100)), C(0.9, 1.0, 1.1), k=0.6)
    # distant hills
    hill = HZ - 60 - 90 * fbm(52, sx=0.25, sy=0.0001, octaves=6)
    img = blend(img, lin((120, 138, 155)), ss(hill, hill + 3, YY) * (YY < HZ + 2) * 0.85)
    img, tex, z = ground(img, HZ, 53, lin((150, 170, 190)), lin((235, 242, 250)), scale=0.008)
    sparkle = (sample(tile(54, octaves=2, base=512, n=1024), XX * 1.0, YY * 1.0) > 0.985) * (YY > HZ + 20)
    img += gaussian_filter(sparkle.astype(np.float32), 0.7)[..., None] * C(3, 3.3, 3.6)
    # blizzard blast: stretched snow mass from the left
    ox, oy, ang = -150, 760, math.radians(-8)
    ca, sa = math.cos(ang), math.sin(ang)
    u = (XX - ox) * ca + (YY - oy) * sa; v = -(XX - ox) * sa + (YY - oy) * ca
    w = 120 + 0.42 * np.clip(u, 0, None)
    T1 = tile(55, octaves=8)
    s1 = sample(T1, u * 0.0025 * 1024 / 4, v * 0.012 * 1024 / 4)
    s2 = sample(tile(56, octaves=8, base=8), u * 0.005 * 1024 / 4 + 200, v * 0.03 * 1024 / 4)
    vw = v + (s1 - 0.5) * w * 0.9
    mass = np.exp(-(vw / w) ** 2 * 1.2) * ss(-50, 150, u) * (0.3 + 0.9 * s2 ** 1.4)
    img = blend(img, C(1.6, 1.8, 2.0) * (0.6 + 0.6 * s2[..., None]), np.clip(mass * 1.1, 0, 0.95))
    img += np.exp(-(vw / (w * 0.4)) ** 2)[..., None] * ss(-50, 300, u)[..., None] * C(0.8, 1.0, 1.3) * 0.7
    # frost crust creeping on ground in front
    frost = ss(0.55, 0.75, sample(tile(57, octaves=8, base=8), XX * 1.2, YY * 1.2)) * ss(HZ + 50, H, YY)
    img = blend(img, C(1.3, 1.45, 1.6), frost * 0.4)
    # snow streaks, three depths
    for n, sd, ln, th, k, bl in ((1600, 61, (20, 60), (1, 1.6), 1.6, 0.6), (500, 62, (80, 180), (1.5, 3), 1.4, 1.5), (90, 63, (200, 420), (4, 8), 0.9, 5)):
        st = streak_field(n, sd, (-400, -50, 1080, 1000), ln, 10, thick=th, inten=(0.25, 1.0))
        img += gaussian_filter(st, bl)[..., None] * C(1.0, 1.1, 1.25) * k
    img = bloom(img, 1.4)
    out = grade(img, expo=0.72, shadow=(-0.01, 0.0, 0.03), sat=0.9, seed=3)
    compose_text(out, 'ふぶき', '到達気温', '？？？', '℃', (150, 210, 255), OUT + '/3_fubuki.png', prefix='−')

# =========================================================
def hydro():
    img = sky(lin((10, 18, 26)), lin((30, 48, 62)), lin((70, 92, 108)), HZ)
    cd = clouds(71, HZ, thr=0.4, scale=0.0013, warp=200)
    img = lit_clouds(img, cd, gauss(300, 500, 500) * 0.6, lin((26, 36, 46)), C(0.5, 0.75, 1.0), k=0.6)
    img, tex, z = ground(img, HZ, 72, lin((10, 14, 18)), lin((44, 52, 58)), scale=0.01)
    # water jet
    ox, oy = 1180, 560; ix, iy = 250, 900
    ang = math.atan2(iy - oy, ix - ox); Lj = math.hypot(ix - ox, iy - oy)
    ca, sa = math.cos(ang), math.sin(ang)
    u = (XX - ox) * ca + (YY - oy) * sa; v = -(XX - ox) * sa + (YY - oy) * ca
    w = 46 + 0.03 * np.clip(u, 0, None)
    Tn = tile(73, octaves=8, base=6)
    tur = sample(Tn, u * 0.008 * 256, v * 0.05 * 256)
    tur2 = sample(tile(74, octaves=8, base=8), u * 0.02 * 256, v * 0.08 * 256)
    vw = v + (tur - 0.5) * w * 0.6
    body = np.exp(-(vw / w) ** 4) * ss(-20, 40, u) * ss(Lj + 20, Lj - 40, u)
    spec = np.exp(-((vw + w * 0.35) / (w * 0.18)) ** 2) * body
    spray_edge = ss(0.5, 0.8, tur2) * np.exp(-(vw / (w * 2.2)) ** 2) * (1 - body) * ss(0, 300, u) * ss(Lj + 60, Lj - 100, u)
    water = C(0.25, 0.55, 0.85) * (0.6 + 0.6 * tur[..., None]) + C(2.5, 3.0, 3.4) * spec[..., None] * (0.5 + tur2[..., None])
    # impact splash plume
    rr = np.sqrt((XX - ix) ** 2 + ((YY - iy) * 1.0) ** 2); th = np.arctan2(YY - iy, XX - ix)
    fan = np.exp(-((th + math.pi / 2 + 0.15) / 0.75) ** 2)          # mostly upward
    pl = fbm(75, sx=2.2, sy=2.2, warp=80, octaves=8)
    plume = fan * ss(560, 60, rr) * (0.3 + 0.9 * pl) * (YY < iy + 20)
    plume += np.exp(-(rr / 140) ** 2) * 1.0
    mist = gaussian_filter(plume, 40) * 0.8 + fbm(76, sx=0.8, sy=0.8, warp=100) * ss(700, 150, rr) * 0.35
    img = blend(img, C(0.55, 0.7, 0.8), np.clip(mist, 0, 0.8))
    img = blend(img, water, body)
    img = blend(img, C(1.2, 1.5, 1.7), np.clip(spray_edge, 0, 1) * 0.7)
    img = blend(img, C(1.6, 1.9, 2.1) * (0.6 + 0.6 * pl[..., None]), np.clip(plume, 0, 1) * 0.9)
    img += np.exp(-(rr / 90) ** 2)[..., None] * C(2.0, 2.5, 3.0)
    # droplets on ballistic arcs
    g = random.Random(77); pts = []
    for _ in range(900):
        a = -math.pi / 2 + g.gauss(0, 0.7); sp = g.uniform(80, 620)
        x = ix + sp * math.cos(a) * g.uniform(0.6, 1.3); y = iy + sp * math.sin(a) * g.uniform(0.5, 1.0) + (sp / 620) ** 2 * 120
        pts.append((x, y, g.uniform(0.8, 3.2), g.uniform(0.4, 1.0)))
    dl = dots_layer(pts)
    img += gaussian_filter(dl, 0.7)[..., None] * C(1.6, 2.0, 2.3)
    # wet ground reflection of everything above the horizon
    refl = img[::-1][H - 2 * HZ:H - HZ] if 2 * HZ < H else None
    rows = np.arange(HZ, min(H, 2 * HZ))
    src = 2 * HZ - rows
    R = gaussian_filter(img[src], (6, 2, 0))
    wet = ss(0.35, 0.65, tex[rows]) * 0.55 + 0.15
    img[rows] = img[rows] + R * wet[..., None] * np.exp(-(rows - HZ) / 500)[:, None, None]
    img = bloom(img, 1.2)
    out = grade(img, expo=0.95, shadow=(-0.01, 0.01, 0.03), sat=1.0, seed=4)
    compose_text(out, 'ハイドロポンプ', '推定噴射圧', '？？？', '気圧', (90, 190, 255), OUT + '/4_hydropump.png')

# =========================================================
def hakai():
    img = sky(lin((8, 10, 24)), lin((40, 30, 50)), lin((140, 70, 40)), HZ)
    cd = clouds(81, HZ, thr=0.46, scale=0.0013)
    ox, oy = -160, 160; ix, iy = 760, 900
    ang = math.atan2(iy - oy, ix - ox); Lb = math.hypot(ix - ox, iy - oy)
    ca, sa = math.cos(ang), math.sin(ang)
    u = (XX - ox) * ca + (YY - oy) * sa; v = -(XX - ox) * sa + (YY - oy) * ca
    inb = ss(-10, 30, u) * ss(Lb + 30, Lb - 10, u)
    swirl = sample(tile(82, octaves=8, base=6), u * 0.004 * 256, v * 0.03 * 256)
    core = np.exp(-(v / 40) ** 2) * inb
    sheath = np.exp(-((v + (swirl - 0.5) * 60) / 110) ** 2) * inb
    halo = np.exp(-(v / 300) ** 2) * inb
    light = gaussian_filter(core, 200) * 30 + gauss(ix, iy, 300) * 3
    img = lit_clouds(img, cd, np.clip(light, 0, 3), lin((26, 20, 30)), C(1.4, 0.65, 0.25), k=0.8)
    img, tex, z = ground(img, HZ, 83, lin((16, 12, 12)), lin((66, 50, 42)))
    img += img * (gauss(ix, iy, 520, 260) * 10)[..., None] * C(2.4, 1.3, 0.6) * (YY > HZ)[..., None]
    # scorched trench from the impact toward camera
    tr = np.exp(-((XX - ix - (YY - iy) * 0.35) / (20 + (YY - iy) * 0.25)) ** 2) * (YY > iy)
    img += tr[..., None] * blackbody(np.clip(0.6 - (YY - iy) / 900, 0, 1))[..., :] * 0.8
    # beam
    img += halo[..., None] * C(0.9, 0.35, 0.08) * 0.6
    img += sheath[..., None] * C(3.5, 1.4, 0.25) * (0.6 + 0.6 * swirl[..., None])
    img += core[..., None] * C(10, 8.5, 6)
    # impact flash + dome
    rr = np.sqrt((XX - ix) ** 2 + ((YY - iy) * 1.4) ** 2)
    img += np.exp(-(rr / 120) ** 2)[..., None] * C(12, 9, 6) + np.exp(-(rr / 320) ** 2)[..., None] * C(3, 1.4, 0.4)
    dust = fbm(84, sx=1.4, sy=1.4, warp=90) * ss(520, 140, rr) * (YY < iy + 30)
    img = blend(img, lin((80, 56, 40)) + C(1.6, 0.8, 0.3) * gauss(ix, iy, 300)[..., None], ss(0.45, 0.8, dust) * 0.75)
    # debris
    gr = random.Random(85); segs = []
    for _ in range(220):
        a = gr.uniform(math.pi * 1.05, math.pi * 1.95); r0 = gr.uniform(60, 200); L = gr.uniform(60, 380)
        segs.append((ix + r0 * math.cos(a), iy + r0 * math.sin(a), ix + (r0 + L) * math.cos(a), iy + (r0 + L) * math.sin(a), gr.uniform(0.3, 1), gr.uniform(1, 3)))
    st = lines_layer(segs, 1)
    img += gaussian_filter(st, 0.8)[..., None] * C(6, 3, 1) + gaussian_filter(st, 5)[..., None] * C(2, 0.8, 0.2)
    # anamorphic flare
    fl = np.exp(-((YY - iy) / 4) ** 2) * np.exp(-((XX - ix) / 900) ** 2)
    img += fl[..., None] * C(2.5, 1.6, 1.0)
    img = bloom(img, 1.2)
    out = grade(img, expo=0.8, shadow=(0.0, 0.0, 0.03), seed=5)
    compose_text(out, 'はかいこうせん', '使用者への反動', '？？？', '', (255, 160, 60), OUT + '/5_hakaikousen.png')

# =========================================================
def volt():
    img = sky(lin((6, 6, 16)), lin((24, 22, 46)), lin((50, 46, 76)), HZ)
    cd = clouds(91, HZ - 150, thr=0.34, soft=0.3, scale=0.0012, warp=260)
    cd = np.maximum(cd, ss(500, 200, YY) * 0.85 * fbm(92, sx=0.9, sy=0.9, warp=200))
    bx0, by0, bx1, by1 = 470, 210, 560, HZ + 40
    light = gauss(bx0, by0 + 40, 380) * 2.5 + gauss(bx1, by1, 260) * 1.5
    img = lit_clouds(img, cd, np.clip(light, 0, 3), lin((18, 18, 32)), C(0.9, 0.85, 1.6), k=0.9)
    img, tex, z = ground(img, HZ, 93, lin((10, 10, 14)), lin((40, 40, 50)))
    img += img * (gauss(bx1, by1, 520, 220) * 8)[..., None] * C(1.4, 1.4, 2.4) * (YY > HZ)[..., None]
    # bolts
    segs = bolt(bx0, by0, bx1, by1, 3, depth=8, rough=0.18, branch=0.5)
    segs += [(a, b, c, d, i * 0.6, w_ * 0.6) for (a, b, c, d, i, w_) in bolt(830, 280, 900, HZ + 25, 7, depth=7, rough=0.2, branch=0.4)]
    segs += [(a, b, c, d, i * 0.45, w_ * 0.5) for (a, b, c, d, i, w_) in bolt(170, 330, 120, HZ + 15, 9, depth=7, rough=0.2, branch=0.4)]
    m = lines_layer(segs, 5)
    img += gaussian_filter(m, 0.8)[..., None] * C(14, 13, 9)
    img += gaussian_filter(m, 6)[..., None] * C(3.5, 3.0, 5.0)
    img += gaussian_filter(m, 30)[..., None] * C(1.5, 1.2, 3.0) * 3
    # arc network along the ground near impact
    arcs = []
    for k in range(10):
        a = random.Random(k).uniform(-0.5, 0.5) + (math.pi if k % 2 else 0)
        L = random.Random(k + 50).uniform(120, 340)
        arcs += bolt(bx1, by1 - 5, bx1 + L * math.cos(a), by1 - 5 + L * 0.25 * abs(math.sin(a)) + random.Random(k).uniform(0, 40), 100 + k, depth=5, rough=0.25, branch=0.2)
    am = lines_layer([(a, b, c, d, i * 0.7, w_ * 0.5) for (a, b, c, d, i, w_) in arcs], 3)
    img += gaussian_filter(am, 0.8)[..., None] * C(8, 8, 6) + gaussian_filter(am, 8)[..., None] * C(1.5, 1.5, 3)
    img += gauss(bx1, by1, 110)[..., None] * C(10, 9, 7) + gauss(bx1, by1, 300)[..., None] * C(1.2, 1.1, 2.4)
    # wet reflection
    rows = np.arange(HZ, min(H, 2 * HZ)); src = 2 * HZ - rows
    R = gaussian_filter(img[src], (8, 2, 0))
    img[rows] += R * (0.25 + 0.4 * tex[rows])[..., None] * np.exp(-(rows - HZ) / 400)[:, None, None]
    # rain
    st = streak_field(1400, 94, (-200, -100, 1100, 1700), (40, 110), 100, thick=(1, 1.6), inten=(0.1, 0.5), jitter=3)
    img += gaussian_filter(st, 0.6)[..., None] * C(0.5, 0.55, 0.8)
    img = bloom(img, 1.1)
    out = grade(img, expo=0.9, shadow=(0.0, 0.0, 0.04), sat=1.05, seed=6)
    compose_text(out, '10まんボルト', '推定電力', '？？？', '世帯分', (255, 215, 70), OUT + '/6_10manvolt.png')

OUT = '/home/claude/poster/out'
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fns = {'1': kaen, '2': bakuhatsu, '3': fubuki, '4': hydro, '5': hakai, '6': volt}
    for k in (sys.argv[1:] or list(fns)):
        fns[k]()
        print('done', k, flush=True)
