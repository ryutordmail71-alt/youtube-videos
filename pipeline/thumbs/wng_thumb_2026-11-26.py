import math, sys
import numpy as np
sys.path.insert(0, '/home/claude/thumbs')
from thumbkit import *
SRC = Image.open('nasa/KSC-08pd1627.jpg').crop((620, 220, 1280, 1250))
def feather(l, x, y, ang, L, w, col):
    """(x,y) 付け根。ang 方向に長さL、幅w の先細りの羽"""
    ca, sa = math.cos(ang), math.sin(ang); nx, ny = -sa, ca; pts = []
    for i in range(21):
        q = i / 20; ww = w * math.sin(math.pi * min(1, q * 1.15)) ** 0.6 * (1 - 0.35 * q)
        pts.append((x + ca * L * q + nx * ww, y + sa * L * q + ny * ww))
    for i in range(20, -1, -1):
        q = i / 20; ww = w * math.sin(math.pi * min(1, q * 1.15)) ** 0.6 * (1 - 0.35 * q)
        pts.append((x + ca * L * q - nx * ww * 0.6, y + sa * L * q - ny * ww * 0.6))
    ImageDraw.Draw(l).polygon(pts, fill=col)
    ImageDraw.Draw(l).line((x, y, x + ca * L * 0.97, y + sa * L * 0.97), fill=(255, 245, 220, 200), width=max(2, int(w * 0.12)))
def wing(size, sx, sy, s, sg):
    """肩(sx,sy)から sg=+1 右へ / -1 左へ 広がる翼"""
    l = Image.new('RGBA', size, (0, 0, 0, 0))
    # 骨格：肩→ひじ→手首
    el = (sx + sg * s * 0.38, sy - s * 0.30); wr = (sx + sg * s * 0.72, sy - s * 0.36)
    def P(q):  # 前縁の上の点 q:0..1
        if q < 0.5: u = q / 0.5; return (sx + (el[0] - sx) * u, sy + (el[1] - sy) * u)
        u = (q - 0.5) / 0.5; return (el[0] + (wr[0] - el[0]) * u, el[1] + (wr[1] - el[1]) * u)
    # 風切り羽（手首から扇形）＋ 次列（腕から下向き）
    for k in range(10):   # 初列
        q = k / 9; a = math.radians(-20 + 75 * q) if sg > 0 else math.pi - math.radians(-20 + 75 * q)
        feather(l, wr[0] - sg * s * 0.04 * q, wr[1] + s * 0.03 * q, a, s * (0.55 - 0.18 * q), s * 0.055, (250, 214, 130, 255))
    for k in range(12):   # 次列
        q = k / 11; x, y = P(0.15 + 0.8 * (1 - q)); a = math.radians(80 + 8 * q) if sg > 0 else math.pi - math.radians(80 + 8 * q)
        a = math.radians(75 - 10 * (1 - q)) if sg > 0 else math.pi - math.radians(75 - 10 * (1 - q))
        feather(l, x, y, a, s * (0.42 + 0.06 * q), s * 0.06, (245, 205, 120, 255))
    d = ImageDraw.Draw(l)
    for r in range(2):    # 雨おおい（上の短い羽）
        for k in range(14):
            q = k / 13; x, y = P(0.05 + 0.9 * q); yy = y + s * (0.05 + r * 0.07); rr = s * 0.06
            d.ellipse((x - rr, yy - rr * 1.4, x + rr, yy + rr * 1.4), fill=(255, 228, 160, 255) if r == 0 else (252, 220, 150, 255))
    d.line([P(q) for q in np.linspace(0, 1, 30)], fill=(255, 240, 200, 255), width=int(s * 0.05), joint='curve')
    return l
def put_wings(im, cx, cy, s):
    for sg in (-1, 1):
        wl = wing(im.size, cx + sg * s * 0.06, cy, s, sg)
        g = wl.copy(); g.putalpha(g.getchannel('A').point(lambda v: v * 170 // 255))
        for _ in range(2): im.alpha_composite(g.filter(ImageFilter.GaussianBlur(s * 0.08)))
        im.alpha_composite(wl)
    glow(im, cx, cy - s * 0.15, s * 0.12, (255, 250, 230), 255)
if __name__ == '__main__':
    im = grade(cover(SRC, cx=0.5, cy=0.5, zoom=1.0), 1.15, 1.1, 0.8)
    put_wings(im, 1480, 620, 400)
    im = left_shade(im, 0.92, 0.55); im = vignette(im, 0.5)
    headline(im, '翼があったら', '人間は飛べる？', s1=150, s2=160, max_w=1000, english='What if humans had wings?')
    save(im, '/home/claude/wng/wng_thumb.jpg')
    # 縦カバー
    W2, H2 = 1080, 1920
    v = grade(cover(SRC, W2, H2, cx=0.5, cy=0.5), 1.15, 1.1, 0.8); put_wings(v, 540, 1000, 440)
    a = np.zeros((H2, W2), np.float32); yv = np.arange(H2)[:, None] / H2; a[:] = np.clip((yv - 0.6) / 0.3, 0, 1) * 0.85 + np.clip((0.3 - yv) / 0.3, 0, 1) * 0.75
    v.paste(Image.new('RGBA', (W2, H2), (4, 5, 10, 255)), (0, 0), Image.fromarray((a * 255).astype(np.uint8)))
    import thumbkit as TK
    d = ImageDraw.Draw(v); TK.spaced(d, (210, 170), '実データでシミュレーション', SANS(44), GOLD, 5)
    def ctr(t, f, y, col, glowc=None):
        x = (W2 - f.getlength(t)) / 2; TK._shadow_text(v, (x, y), t, f, col, stroke=2, glowcol=glowc)
    ctr('翼があったら', MIN(140), 400, WHITE); ctr('人間は', MIN(150), 1560, WHITE); ctr('飛べる？', MIN(190), 1770, GOLD, (255, 170, 40))
    TK.spaced(ImageDraw.Draw(v), (250, 1860), 'WHAT IF HUMANS HAD WINGS?', SANS(30), (230, 228, 222), 4)
    v.convert('RGB').save('/home/claude/wng/wng_short_cover.jpg', quality=92)
    print('ok')
