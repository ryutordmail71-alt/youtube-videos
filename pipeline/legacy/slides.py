import os, sys, random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/claude/space')
import content as C
sys.path.insert(0, '/home/claude/trivia')
import slides as T
T.INTRO, T.ITEMS, T.OUTRO = C.INTRO, C.ITEMS, C.OUTRO

def add_planet(im, cx, cy, r, alpha=0.55):
    """faint ringed planet for a 'space' feel"""
    W_, H_ = im.size
    lay = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ring = (cx - r * 2.1, cy - r * 0.55, cx + r * 2.1, cy + r * 0.55)
    d.ellipse(ring, outline=(200, 180, 150, int(140 * alpha)), width=max(2, r // 14))
    body = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); db = ImageDraw.Draw(body)
    db.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(170, 145, 115, int(255 * alpha)))
    sh = Image.new('L', (W_, H_), 0); ImageDraw.Draw(sh).ellipse((cx - r * 0.55, cy - r * 1.25, cx + r * 1.6, cy + r * 0.9), fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(r * 0.25))
    dark = Image.new('RGBA', (W_, H_), (12, 12, 30, 0)); dark.putalpha(Image.fromarray((np.asarray(sh) * (np.asarray(body.getchannel('A')) > 0)).astype(np.uint8)))
    body = Image.alpha_composite(body, dark)
    front = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); df = ImageDraw.Draw(front)
    df.arc(ring, 0, 180, fill=(210, 190, 160, int(170 * alpha)), width=max(2, r // 14))
    out = Image.alpha_composite(im.convert('RGBA'), lay)
    out = Image.alpha_composite(out, body)
    out = Image.alpha_composite(out, front)
    return out.convert('RGB')

def bg_land():
    return add_planet(T.background(), 230, 900, 46, 0.5)

# ---------- vertical (short) ----------
VW, VH = 1080, 1920
def bg_vert():
    y = np.linspace(0, 1, VH)[:, None, None]
    a = (np.array([8, 10, 30]) * (1 - y) + np.array([24, 22, 54]) * y) * np.ones((1, VW, 1))
    im = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(im); g = random.Random(7)
    for _ in range(520):
        x, yy, r = g.uniform(0, VW), g.uniform(0, VH), g.choice([0.8, 1, 1, 1.4, 2])
        b = g.randint(90, 230); d.ellipse((x - r, yy - r, x + r, yy + r), fill=(b, b, min(255, b + 15)))
    glow = Image.new('L', (VW, VH), 0); ImageDraw.Draw(glow).ellipse((620, 180, 1000, 480), fill=60)
    im = Image.composite(Image.new('RGB', (VW, VH), (60, 60, 80)), im, glow.filter(ImageFilter.GaussianBlur(70)))
    m = Image.new('L', (VW, VH), 0); dm = ImageDraw.Draw(m)
    dm.ellipse((760, 270, 860, 380), fill=255); dm.ellipse((790, 252, 890, 362), fill=0)
    im = Image.composite(Image.new('RGB', (VW, VH), (222, 210, 175)), im, m.filter(ImageFilter.GaussianBlur(0.8)))
    return add_planet(im, 230, 1600, 60, 0.45)

def vslide(bg, big, s1, s2, idx, first=False, last=False):
    im = bg.copy(); d = ImageDraw.Draw(im)
    F = T.F
    if first:
        T_ = d.text
        T_((540, 640), s1, font=F(T.SERIF_R, 58), fill=T.SUB, anchor='mm')
        T_((540, 790), big, font=F(T.SERIF_B, 150), fill=T.TITLE, anchor='mm')
        T_((540, 940), s2, font=F(T.SERIF_B, 72), fill=T.GOLD, anchor='mm')
    elif last:
        d.text((540, 720), big, font=F(T.SERIF_B, 120), fill=T.TITLE, anchor='mm')
        d.text((540, 870), s1, font=F(T.SERIF_R, 62), fill=T.GOLD, anchor='mm')
        d.text((540, 990), s2, font=F(T.SANS_L, 50), fill=T.SUB, anchor='mm')
    else:
        d.text((540, 520), f'{idx:02d}', font=F(T.SERIF_R, 110), fill=T.GOLD, anchor='mm')
        d.line((470, 580, 610, 580), fill=T.GOLD, width=3)
        lines = big.split('\n')
        for k, ln in enumerate(lines):
            sz = 112
            while F(T.SERIF_B, sz).getlength(ln) > 940: sz -= 4
            d.text((540, 720 + k * 150), ln, font=F(T.SERIF_B, sz), fill=T.TITLE, anchor='mm')
        yy = 720 + len(lines) * 150 + 40
        sz = 46
        while F(T.SANS_L, sz).getlength(s1) > 940: sz -= 2
        d.text((540, yy), s1, font=F(T.SANS_L, sz), fill=T.SUB, anchor='mm')
    d.text((540, 1480), 'ナレーション：VOICEVOX：青山龍星', font=F(T.SANS_L, 30), fill=T.DIM, anchor='mm')
    return im

if __name__ == '__main__':
    os.makedirs('slides', exist_ok=True); os.makedirs('vslides', exist_ok=True)
    bg = bg_land()
    T.slide_intro(bg).save('slides/00.png')
    for i, it in enumerate(C.ITEMS, 1):
        T.slide_item(bg, i, it[0], it[1], it[2]).save(f'slides/{i:02d}.png')
    T.slide_outro(bg).save('slides/21.png')
    vb = bg_vert(); n = len(C.SHORT)
    for i, (big, s1, s2, _) in enumerate(C.SHORT):
        vslide(vb, big, s1, s2, i, first=(i == 0), last=(i == n - 1)).save(f'vslides/{i:02d}.png')
    print('ok')
