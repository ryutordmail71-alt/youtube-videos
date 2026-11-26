import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
def bg_grad(c1, c2, cx=0.7, cy=0.5):
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx / W - cx) * 1.6) ** 2 + (yy / H - cy) ** 2)
    t = np.clip(r / 1.0, 0, 1)[..., None]; a = np.array(c1, float) * (1 - t) + np.array(c2, float) * t
    return Image.fromarray(a.astype(np.uint8)).convert('RGBA')
def glowline(im, pts, col, w=10, g=3):
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(l).line(pts, fill=col + (255,), width=w, joint='curve')
    for _ in range(g): im.alpha_composite(l.filter(ImageFilter.GaussianBlur(w * 2.5)))
    im.alpha_composite(l.filter(ImageFilter.GaussianBlur(w * 0.6))); im.alpha_composite(l)
def heart_pts(cx, cy, s, n=200):
    t = np.linspace(0, 2 * np.pi, n); x = 16 * np.sin(t) ** 3; y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    return [(cx + s * a / 17, cy - s * b / 17) for a, b in zip(x, y)]
def heart(im, cx, cy, s, col, a=255, glowa=150):
    l = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(l).polygon(heart_pts(cx, cy, s), fill=col + (a,))
    g = l.copy(); g.putalpha(g.getchannel('A').point(lambda v: v * glowa // 255))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(s * 0.5))); im.alpha_composite(l)
    hl = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(hl).ellipse((cx - s * 0.55, cy - s * 0.75, cx - s * 0.15, cy - s * 0.4), fill=(255, 255, 255, 70))
    im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(s * 0.12)))
def ecg(x0, x1, y, amp, beats, dip=0):
    pts = []; n = 600
    for i in range(n + 1):
        u = i / n; x = x0 + (x1 - x0) * u; ph = (u * beats) % 1; v = 0
        if 0.40 < ph < 0.44: v = -0.25 * math.sin((ph - 0.40) / 0.04 * math.pi)
        elif 0.46 < ph < 0.50: v = 1.0 * math.sin((ph - 0.46) / 0.04 * math.pi)
        elif 0.50 < ph < 0.53: v = -0.35 * math.sin((ph - 0.50) / 0.03 * math.pi)
        elif 0.62 < ph < 0.74: v = 0.22 * math.sin((ph - 0.62) / 0.12 * math.pi)
        damp = 1 - dip * u
        pts.append((x, y - v * amp * damp + dip * u * 160))
    return pts
# 1) 気絶
im = bg_grad((70, 12, 14), (4, 3, 6), 0.72, 0.5)
glowline(im, ecg(980, 1960, 700, 200, 2.6, dip=0.8), (255, 210, 80), 9)
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - 1400) / 900) ** 2 + ((yy - 540) / 620) ** 2)
a = np.clip((r - 0.55) / 0.35, 0, 1) * 0.92; im.paste(Image.new('RGBA', (W, H), (0, 0, 0, 255)), (0, 0), Image.fromarray((a * 255).astype(np.uint8)))
im = left_shade(im, 0.6, 0.45)
headline(im, '巨人が立ち上がると', '気絶する？', s1=116, s2=170, max_w=1000, english='Would a giant faint just by standing up?')
save(im, 'out/gfa_thumb.jpg')
# 2) 心臓10個
im = bg_grad((60, 10, 18), (3, 2, 6), 0.72, 0.5)
pos = [(1150 + (i % 4) * 180 + (90 if (i // 4) % 2 else 0), 300 + (i // 4) * 230) for i in range(10)]
for k, (x, y) in enumerate(pos): heart(im, x, y, 72, (255, 200, 70) if k == 5 else (215, 30, 45), 255, 170)
im = left_shade(im, 0.8, 0.5); im = vignette(im, 0.5)
headline(im, '心臓が10個なら', '最強？', s1=130, s2=200, english='What if you had 10 hearts?')
save(im, 'out/heart10_thumb.jpg')
# 3) 人間の一生
im = bg_grad((20, 26, 48), (3, 3, 8), 0.75, 0.45)
d = ImageDraw.Draw(im); big = MIN(250)
l = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(l).text((1860, 470), '31億回', font=big, fill=(255, 210, 80, 255), anchor='rm')
for _ in range(2): im.alpha_composite(l.filter(ImageFilter.GaussianBlur(40)))
im.alpha_composite(l)
ImageDraw.Draw(im).text((1860, 665), '一生で心臓が動く回数（目安）', font=SANS(40), fill=(235, 232, 225), anchor='rm')
glowline(im, ecg(900, 1960, 860, 110, 4.5), (230, 60, 70), 6, 2)
im = left_shade(im, 0.75, 0.42); im = vignette(im, 0.5)
headline(im, 'あなたの一生を', '数字にすると？', s1=120, s2=140, max_w=800, english='Your whole life in numbers')
save(im, 'out/hlf_thumb.jpg')
# 4) 筋肉リミッター：メーター
im = bg_grad((50, 30, 12), (4, 3, 4), 0.72, 0.55)
cx, cy, R = 1530, 640, 350
arc = Image.new('RGBA', im.size, (0, 0, 0, 0)); da = ImageDraw.Draw(arc)
da.arc((cx - R, cy - R, cx + R, cy + R), 160, 380, fill=(90, 90, 100, 255), width=26)
da.arc((cx - R, cy - R, cx + R, cy + R), 160, 300, fill=(255, 210, 80, 255), width=26)
da.arc((cx - R, cy - R, cx + R, cy + R), 300, 380, fill=(230, 40, 35, 255), width=26)
for _ in range(2): im.alpha_composite(arc.filter(ImageFilter.GaussianBlur(26)))
im.alpha_composite(arc)
ang = math.radians(372); nx, ny = cx + math.cos(ang) * (R - 40), cy + math.sin(ang) * (R - 40)
glowline(im, [(cx, cy), (nx, ny)], (255, 245, 230), 12, 2)
ImageDraw.Draw(im).ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(250, 245, 235))
ImageDraw.Draw(im).text((cx, cy + 150), '300%', font=MIN(150), fill=(240, 60, 50), anchor='mm')
im = left_shade(im, 0.85, 0.5); im = vignette(im, 0.5)
headline(im, '筋肉のリミッターを', '外したら最強？', s1=118, s2=150, max_w=950, english='What if your muscles had no limiter?')
save(im, 'out/mlm_thumb.jpg')
# 5) ノミ：夜のビルと、ジャンプの光の弧
im = bg_grad((18, 24, 48), (2, 3, 8), 0.75, 0.3)
rng = np.random.default_rng(9); d = ImageDraw.Draw(im)
for _ in range(300):
    x, y = rng.uniform(0, W), rng.uniform(0, 600); b = int(rng.uniform(70, 200)); d.point((x, y), fill=(b, b, b))
x = 760
while x < W:
    w = rng.uniform(70, 160); h = rng.uniform(140, 380) if not (1400 < x < 1560) else 820
    d.rectangle((x, H - h, x + w, H), fill=(8, 10, 18))
    for wy in range(int(H - h + 20), H, 26):
        for wx in range(int(x + 10), int(x + w - 10), 20):
            if rng.random() < 0.28: d.rectangle((wx, wy, wx + 8, wy + 12), fill=(255, 210, 120, 255))
    x += w + rng.uniform(4, 20)
pts = []
for i in range(201):
    u = i / 200; px = 1000 + 900 * u; py = 1000 - 4 * 900 * u * (1 - u)
    pts.append((px, py))
glowline(im, pts, (255, 210, 80), 8, 3)
glow(im, 1450, 100, 30, (255, 250, 230), 255)
ImageDraw.Draw(im).text((1530, 200), '170m？', font=MIN(90), fill=(255, 210, 80), anchor='lm')
im = left_shade(im, 0.85, 0.5); im = vignette(im, 0.45)
headline(im, 'ノミの跳躍力なら', '何m跳べる？', s1=118, s2=160, max_w=900, english='What if humans could jump like fleas?')
save(im, 'out/nomi_thumb.jpg')
print('ok')
