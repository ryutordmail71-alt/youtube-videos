"""手法v2の差し込み場面：ジングル・リフック・驚きの大きな字幕（「ドン」）"""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, ascn as S
from arnd import W, H, FPS, Fo, Fb, Mi, PALE, GOLD, GREEN, ctext, fade, ease
G = '/home/claude/air'; D = json.load(open(f'{G}/dur.json')); AIR = S.AIR
def pop(t, t0=0.0, d=0.22): u = fade((t - t0) / d); return 1.35 - 0.35 * (1 - (1 - u) ** 3)
def scene_insert(name, key, big, col, small='', sub='', kind='impact', pre=0.15, post=0.45):
    dur = pre + D[key] + post; base = ImageEnhance.Brightness(S.dark_bg().filter(ImageFilter.GaussianBlur(3))).enhance(0.7)
    def fr(t):
        im = base.copy().convert('RGBA')
        if kind == 'jingle':
            R.glow(im, W / 2, H / 2, 520, GOLD, int(140 * (1 - fade(t / 0.6)) + 40))
        else:
            R.glow(im, W / 2, H / 2, 650, col, int(190 * (1 - fade(t / 0.5)) + 50))
            if t < 0.12: im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(200 * (1 - t / 0.12)))))
        d = ImageDraw.Draw(im, 'RGBA'); s = pop(t)
        if small: ctext(d, (W / 2, 330), small, Mi(int(90 * min(s, 1.15))), PALE, sw=6)
        ctext(d, (W / 2, 560), big, Mi(int((230 if kind != 'jingle' else 170) * s)), col, sw=10)
        if sub and t > 0.3: ctext(d, (W / 2, 800), sub, Fo(52), PALE, sw=4)
        S.note(d); return im.convert('RGB')
    S.run(f'{G}/c_{name}.mp4', dur, fr); return dur, [(pre, key)]
def all_inserts():
    res = {}
    res['jingle'] = scene_insert('jingle', 'jingle', '実データで 検証！', GOLD, kind='jingle')
    res['rh1'] = scene_insert('rh1', 'rh1', 'ここからが本番', GOLD, small='でも…', sub='AIは 作戦を変えてくる', kind='rehook')
    res['wow2'] = scene_insert('wow2', 'wow2', 'たった28時間', AIR, small='えっ!?', sub='約2億台が 使えなくなる（架空の速さ）')
    res['rh2'] = scene_insert('rh2', 'rh2', '最後の作戦', AIR, small='そして AIは…', sub='ロボット 約500万台', kind='rehook')
    res['wow3'] = scene_insert('wow3', 'wow3', 'まさかの…', GOLD, small='決勝戦の結果は', sub='')
    json.dump(res, open(f'{G}/scene_ins.json', 'w')); print('done ins')
if __name__ == '__main__': all_inserts()
