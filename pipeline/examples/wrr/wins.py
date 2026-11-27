"""差し込み場面：ジングル・リフック・驚きの大字幕"""
import json, sys
sys.path.insert(0, '/home/claude/air')
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, wscn as S
from arnd import W, H, Fo, Mi, PALE, GOLD, RED, ctext, fade
G = '/home/claude/wrr'; D = json.load(open(f'{G}/dur.json'))
def pop(t, t0=0.0, d=0.25): u = fade((t - t0) / d); return 1.3 - 0.3 * (1 - (1 - u) ** 3)
def glow_rgb(im, x, y, r, col, a):
    g = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((x - r, y - r, x + r, y + r), fill=col + (int(a),)); g = g.filter(ImageFilter.GaussianBlur(r * 0.5)); im.paste(g, (0, 0), g)
def scene_insert(name, key, big, col, small='', sub='', kind='impact', pre=0.15, post=0.3):
    dur = pre + D[key] + post; base = ImageEnhance.Brightness(S.stadium_bg().filter(ImageFilter.GaussianBlur(3))).enhance(0.8)
    def fr(t):
        im = base.copy(); glow_rgb(im, W / 2, H / 2, 600, col, int(140 * (1 - fade(t / 0.6)) + 40))
        if kind == 'impact' and t < 0.12: im = Image.blend(im, Image.new('RGB', (W, H), (255, 255, 255)), 0.7 * (1 - t / 0.12))
        d = ImageDraw.Draw(im, 'RGBA'); s = pop(t)
        if small: ctext(d, (W / 2, 330), small, Mi(int(90 * min(s, 1.15))), PALE, sw=6)
        ctext(d, (W / 2, 560), big, Mi(int((210 if kind != 'jingle' else 170) * s)), col, sw=10)
        if sub and t > 0.3: ctext(d, (W / 2, 800), sub, Fo(52), PALE, sw=4)
        R.note(d); return im
    S.run(f'{G}/c_{name}.mp4', dur, fr); return dur, [(pre, key)]
if __name__ == '__main__':
    res = {}
    res['jingle'] = scene_insert('jingle', 'jingle', '実データで 検証！', GOLD, kind='jingle')
    res['rh1'] = scene_insert('rh1', 'rh1', 'ここからが本番', S.ICE, small='でも…', sub='次は 10,000m！', kind='rehook')
    res['wow2'] = scene_insert('wow2', 'wow2', 'たった1割', GOLD, small='えっ!?', sub='スケートは 長い距離でも 速さが落ちにくい')
    res['rh2'] = scene_insert('rh2', 'rh2', '決勝戦', RED, small='そして…', sub='人間 vs 動物　秘密兵器も登場', kind='rehook')
    res['wow3'] = scene_insert('wow3', 'wow3', 'まさか…', S.CHEE, small='', sub='チーターが 負ける？')
    json.dump(res, open(f'{G}/scene_ins.json', 'w')); print('done ins')
