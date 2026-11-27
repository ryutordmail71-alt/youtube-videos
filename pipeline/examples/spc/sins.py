"""差し込み場面：ジングル・リフック・驚きの大きな字幕（ホラーなので控えめ）"""
import json, sys
sys.path.insert(0, '/home/claude/air')
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import arnd as R, sscn as S
from arnd import W, H, Fo, Mi, PALE, GOLD, RED, ctext, fade
G = '/home/claude/spc'; D = json.load(open(f'{G}/dur.json')); ICE = S.ICE
def pop(t, t0=0.0, d=0.3): u = fade((t - t0) / d); return 1.25 - 0.25 * (1 - (1 - u) ** 3)
def scene_insert(name, key, big, col, small='', sub='', kind='impact', pre=0.15, post=0.5):
    dur = pre + D[key] + post; base = ImageEnhance.Brightness(S.space_bg().filter(ImageFilter.GaussianBlur(3))).enhance(0.6)
    def fr(t):
        im = base.copy().convert('RGBA')
        R.glow(im, W / 2, H / 2, 600, col, int(120 * (1 - fade(t / 0.7)) + 40))
        d = ImageDraw.Draw(im, 'RGBA'); s = pop(t)
        if small: ctext(d, (W / 2, 330), small, Mi(int(90 * min(s, 1.15))), PALE, sw=6)
        ctext(d, (W / 2, 560), big, Mi(int((220 if kind != 'jingle' else 170) * s)), col, sw=10)
        if sub and t > 0.3: ctext(d, (W / 2, 800), sub, Fo(52), PALE, sw=4)
        S.note(d); return im.convert('RGB')
    S.run(f'{G}/c_{name}.mp4', dur, fr); return dur, [(pre, key)]
if __name__ == '__main__':
    res = {}
    res['jingle'] = scene_insert('jingle', 'jingle', '実データで 検証！', GOLD, kind='jingle')
    res['rh1'] = scene_insert('rh1', 'rh1', 'ここからが本番', ICE, small='でも…', sub='宇宙はマイナス270℃', kind='rehook')
    res['wow2'] = scene_insert('wow2', 'wow2', '1分で 0.2℃', GOLD, small='えっ!?', sub='体温は ほとんど下がらない（目安）')
    res['rh2'] = scene_insert('rh2', 'rh2', '決勝戦', RED, small='そして…', sub='うわさ3「息がもたない」', kind='rehook')
    res['wow3'] = scene_insert('wow3', 'wow3', 'たった15秒', RED, small='', sub='意識がもつのは 約10〜15秒')
    json.dump(res, open(f'{G}/scene_ins.json', 'w')); print('done ins')
