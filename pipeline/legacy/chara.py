"""Character compositing helpers (keyed PNG panels -> lit RGBA layers)."""
import numpy as np
from PIL import Image, ImageFilter, ImageChops
from scipy.ndimage import shift as nd_shift, gaussian_filter

CDIR = '/home/claude/chara'
FIRE_POS = dict(h=640, left=-40, top=345)          # pose 2 placement on the 1080x1920 frame
HAND = (330, 462)

def load(name):
    return Image.open(f'{CDIR}/{name}.png').convert('RGBA')

def lit_layer(im, h, rim_col, tint=(1.0, 1.0, 1.0), rim_dir=1, rim_k=1.0, flip=False):
    """scale to height h, colour-grade toward the scene, add a rim light on the side facing the effect"""
    s = h / im.height
    im = im.resize((max(1, int(im.width * s)), int(h)), Image.LANCZOS)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.asarray(im, np.float32)
    rgb = a[..., :3] / 255; al = a[..., 3] / 255
    rgb = rgb * np.array(tint, np.float32)
    # slight contrast/saturation to sit in the cinematic grade
    l = rgb.mean(-1, keepdims=True); rgb = np.clip(l + (rgb - l) * 1.08, 0, 1)
    # rim: alpha minus alpha shifted away from the light
    sh = nd_shift(al, (0, -rim_dir * 7), order=1, cval=0)
    edge = np.clip(al - sh, 0, 1)
    edge = gaussian_filter(edge, 1.2) * al
    rim = np.array(rim_col, np.float32) / 255
    rgb = rgb + edge[..., None] * rim * 0.9 * rim_k
    wash = gaussian_filter(edge, 14)[..., None] * rim * 0.35 * rim_k * al[..., None]
    rgb = np.clip(rgb + wash, 0, 1)
    out = np.dstack([rgb * 255, al * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

def glow_disc(r, col, k=1.0):
    n = int(r * 4)
    y, x = np.mgrid[0:n, 0:n] - n / 2
    g = np.exp(-(x ** 2 + y ** 2) / (r ** 2)) * k
    core = np.exp(-(x ** 2 + y ** 2) / ((r * 0.25) ** 2))
    rgb = np.clip(np.array(col, np.float32)[None, None] * g[..., None] + 255 * core[..., None] * 0.9, 0, 255)
    a = np.clip(np.maximum(g, core) * 255, 0, 255)
    return Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), 'RGBA')
