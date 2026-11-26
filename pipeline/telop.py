"""バラエティ風の字幕（ツッコミ・擬音・強調）。どの場面の描画にも上から重ねて使う。
   im は RGBA の 1920×1080（ショートは 1080×1920 でも可）。t は字幕が出てからの秒数（ポンと出る動きに使う）。"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
N = '/usr/share/fonts/opentype/noto/'
def _f(name, s): return ImageFont.truetype(N + name, s, index=0)
SANS = lambda s: _f('NotoSansCJK-Black.ttc', s)
SERIF = lambda s: _f('NotoSerifCJK-Black.ttc', s)
def _pop(t, d=0.18): u = max(0.0, min(1.0, t / d)); return 1.0 + 0.35 * (1 - u) ** 2 - 0.08 * math.sin(u * math.pi)
def _layer_text(t_, font, fill, stroke_w, stroke_fill, rot=0, inner=None, inner_w=0):
    w = int(font.getlength(t_) + stroke_w * 4 + 40); h = int(font.size * 1.5 + stroke_w * 4)
    l = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(l); xy = (w / 2, h / 2)
    d.text(xy, t_, font=font, fill=stroke_fill, anchor='mm', stroke_width=stroke_w + inner_w, stroke_fill=stroke_fill)
    if inner: d.text(xy, t_, font=font, fill=inner, anchor='mm', stroke_width=inner_w, stroke_fill=inner)
    d.text(xy, t_, font=font, fill=fill, anchor='mm')
    return l.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else l
def _paste_center(im, l, x, y, shadow=True):
    if shadow:
        sh = Image.new('RGBA', l.size, (0, 0, 0, 0)); sh.putalpha(l.getchannel('A').point(lambda v: v * 0.6))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (int(x - l.width / 2 + 6), int(y - l.height / 2 + 8)))
    im.alpha_composite(l, (int(x - l.width / 2), int(y - l.height / 2)))
def tsukkomi(im, text, t, x=None, y=None, col=(70, 160, 255)):
    """心の声のツッコミ：「（いや多すぎ）」。右上に小さい角丸の箱で、少し傾けて"""
    W, H = im.size; x = x or W * 0.78; y = y or H * 0.2; s = _pop(t)
    f = SANS(int(54 * s)); w = f.getlength(text) + 60; h = 54 * s + 40
    box = Image.new('RGBA', (int(w + 20), int(h + 20)), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), 22, fill=(255, 255, 255, 245), outline=col + (255,), width=6)
    d.text((10 + w / 2, 10 + h / 2), text, font=f, fill=col, anchor='mm')
    _paste_center(im, box.rotate(-4, resample=Image.BICUBIC, expand=True), x, y)
def giongo(im, text, t, x, y, size=180, col=(255, 230, 60), rot=8):
    """擬音：「ドーン！」「ゴゴゴ…」「シーン…」。太い黒フチ＋白の内フチで、傾けてポンと出す"""
    s = _pop(t); l = _layer_text(text, SANS(int(size * s)), col, 12, (0, 0, 0), rot=rot, inner=(255, 255, 255), inner_w=8)
    _paste_center(im, l, x, y)
def kyocho(im, parts, t, x, y, base=110):
    """強調の1行：[('たった', 'w'), ('28時間', 'r'), ('で全滅', 'w')]。r＝赤で大きく、y＝黄色、w＝白"""
    s = _pop(t); cols = {'w': (255, 255, 255), 'r': (240, 40, 45), 'y': (255, 220, 40)}
    ls = [_layer_text(tx, SANS(int(base * (1.45 if c == 'r' else 1.0) * (s if c == 'r' else 1))), cols[c], 10, (0, 0, 0), inner=(255, 255, 255) if c == 'r' else None, inner_w=6 if c == 'r' else 0) for tx, c in parts]
    tw = sum(l.width for l in ls) - 40 * (len(ls) - 1); xx = x - tw / 2
    for l in ls: _paste_center(im, l, xx + l.width / 2, y + (0 if l.height < base * 2 else -10)); xx += l.width - 40
def speaker(im, name, text, t, y=None, col=(255, 120, 60)):
    """話し手つきの字幕（下）：名前の札＋セリフ。相方キャラを入れる場合用"""
    W, H = im.size; y = y or H - 170; d = ImageDraw.Draw(im); f = SANS(56); fn = SANS(34)
    tw = f.getlength(text); x0 = W / 2 - tw / 2 - 40
    d.rounded_rectangle((x0, y - 50, x0 + tw + 80, y + 50), 18, fill=(0, 0, 0, 200))
    d.rounded_rectangle((x0 - 10, y - 95, x0 + fn.getlength(name) + 40, y - 45), 12, fill=col)
    d.text((x0 + 15, y - 70), name, font=fn, fill=(255, 255, 255), anchor='lm')
    d.text((W / 2, y), text, font=f, fill=(255, 255, 255), anchor='mm')
