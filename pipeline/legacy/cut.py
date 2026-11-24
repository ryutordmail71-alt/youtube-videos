import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import binary_erosion, gaussian_filter, label

im = np.asarray(Image.open('/home/claude/chara/sheet.png').convert('RGB')).astype(np.float32)
xs = [(1, 325), (330, 654), (658, 982), (987, 1311)]
ys = [(1, 597), (601, 1198)]
names = ['p1_stand', 'p2_fire', 'p3_soot', 'p4_down', 'p5_ice', 'p6_water', 'p7_tired', 'p8_shock']
k = 0
for (y0, y1) in ys:
    for (x0, x1) in xs:
        p = im[y0 + 2:y1 - 2, x0 + 2:x1 - 2].copy()
        r, g, b = p[..., 0], p[..., 1], p[..., 2]
        mx = np.maximum(r, b)
        gd = g - mx                                        # green dominance
        a = 1 - np.clip((gd - 35) / 70, 0, 1)              # key
        # keep only the main connected subject (drops stray specks)
        solid = a > 0.5
        lab, n = label(solid)
        if n > 1:
            sizes = np.bincount(lab.ravel()); sizes[0] = 0
            keep = sizes > sizes.max() * 0.02
            mask = keep[lab]
            a = np.where(mask | (a < 0.5), a, 0)
        # despill: pull green down toward max(r,b) where it dominates
        spill = np.clip(gd, 0, None)
        g2 = g - spill * 0.95
        p[..., 1] = g2
        a = gaussian_filter(a, 0.6)
        rgba = np.dstack([np.clip(p, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)
        out = Image.fromarray(rgba, 'RGBA')
        bb = out.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox()
        out = out.crop(bb)
        # 2x upscale for screen use (smooth)
        out = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
        out.save(f'/home/claude/chara/{names[k]}.png')
        print(names[k], out.size)
        k += 1
