"""筋肉のリミッターを外したら最強？（垂直跳びシミュレーション）"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/hlf')
import hscenes as HS
W, H, FPS = 1920, 1080, 30
G = '/home/claude/mlm'
D = json.load(open(f'{G}/dur.json'))
Fo, Fb, Mi, BE = HS.Fo, HS.Fb, HS.Mi, HS.BE
PALE, GOLD, RED, BLUE, GREEN, GRAY = HS.PALE, HS.GOLD, HS.RED, HS.BLUE, HS.GREEN, HS.GRAY
ctext, ease, fade, writer = HS.ctext, HS.ease, HS.fade, HS.writer
DISC = '※実データをもとにした、単純化した空想のシミュレーションです（数値は目安）'
g = 9.8; D_PUSH = 0.40; BASE = 2.125            # ふつうの全力：平均の押す力＝体重の2.125倍 → 45cm
S_BASE = 90.0; S_LIMIT = 100.0; S_BREAK = 120.0  # アキレス腱にかかる応力（MPa、目安）
def jump_h(k): return max(0.0, (BASE * k - 1) * D_PUSH)
def stress(k): return S_BASE * k
ROUNDS = {'r1': 1.0, 'r2': 1 / 0.9, 'r3': 3.0}

def bgimg(): return HS.bg(W, H, (18, 22, 36))
def disc(d): d.text((W - 24, H - 20), DISC, font=Fb(20), fill=(215, 215, 220), anchor='rs')

FLOOR = 900; CM = 2.2        # 1cm = 2.2px（身長175cm ≒ 385px）
def figure(d, x, yfoot, crouch=0.0, fallen=0.0, leg_col=(235, 225, 210), calf_col=None):
    """横向きの人。crouch：0〜1（しゃがみ）、fallen：0〜1（倒れる）"""
    col = (235, 225, 210); L = 175 * CM
    if fallen > 0:
        y = yfoot - 30 * (1 - fallen); cx = x
        d.rounded_rectangle((cx - L * 0.45, y - 46, cx + L * 0.45, y), 20, fill=col)
        d.ellipse((cx + L * 0.42, y - 70, cx + L * 0.56, y + 4), fill=col); return
    shin = L * 0.25; thigh = L * 0.25; torso = L * 0.32; head = L * 0.12
    kb = crouch * 0.95                          # ひざの曲がり（ラジアン）
    ankle = (x, yfoot); knee = (x + shin * math.sin(kb * 0.8), yfoot - shin * math.cos(kb * 0.8))
    hip = (knee[0] - thigh * math.sin(kb * 1.3), knee[1] - thigh * math.cos(kb * 1.3))
    sh = (hip[0] + torso * math.sin(kb * 0.55), hip[1] - torso * math.cos(kb * 0.55))
    w = int(L * 0.07)
    d.line([ankle, knee], fill=calf_col or leg_col, width=w + 6); d.line([knee, hip], fill=leg_col, width=w + 10)
    d.line([hip, sh], fill=col, width=w + 22)
    d.ellipse((sh[0] - head / 2 + 6, sh[1] - head - 4, sh[0] + head / 2 + 6, sh[1] + 6), fill=col)
    arm = (sh[0] - L * 0.18 * math.cos(crouch * 1.2), sh[1] + L * 0.2 * (1 - crouch * 1.6))
    d.line([sh, arm], fill=col, width=w)
    d.polygon([(x - 14, yfoot), (x + 70, yfoot), (x + 70, yfoot - 18), (x - 6, yfoot - 22)], fill=(60, 70, 90))
def ruler(d, x):
    d.line((x, FLOOR, x, FLOOR - 250 * CM), fill=(200, 200, 205), width=4)
    for c in range(0, 251, 10):
        y = FLOOR - c * CM; ln = 28 if c % 50 == 0 else 12
        d.line((x, y, x + ln, y), fill=(200, 200, 205), width=3)
        if c % 50 == 0: d.text((x - 12, y), f'{c}cm', font=Fb(24), fill=GRAY, anchor='rm')
def gauge(d, x0, y0, w, h, s, broken=False):
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 16, fill=(10, 12, 20, 230))
    d.text((x0 + w / 2, y0 + 30), 'アキレス腱', font=Fo(32), fill=PALE, anchor='mm')
    d.text((x0 + w / 2, y0 + 66), 'にかかる力', font=Fb(22), fill=GRAY, anchor='mm')
    gx0, gx1, gy0, gy1 = x0 + w / 2 - 34, x0 + w / 2 + 34, y0 + 100, y0 + h - 70; top = 150.0
    def Y(v): return gy1 - (gy1 - gy0) * min(1, v / top)
    d.rectangle((gx0, gy0, gx1, gy1), fill=(58, 62, 78))
    v = min(top, s); col = GREEN if v < 80 else (GOLD if v < S_LIMIT else RED)
    d.rectangle((gx0, Y(v), gx1, gy1), fill=col)
    for val, lab, c in [(S_LIMIT, '限界', GOLD), (S_BREAK, '切れる', RED)]:
        d.line((gx0 - 14, Y(val), gx1 + 14, Y(val)), fill=c, width=4); d.text((gx1 + 20, Y(val)), lab, font=Fb(24), fill=c, anchor='lm')
    d.text((x0 + w / 2, y0 + h - 34), '切れた！' if broken else f'{int(s / S_BREAK * 100)}%', font=Fo(40), fill=RED if (broken or s >= S_LIMIT) else PALE, anchor='mm')

def jump_state(tt, k):
    """tt：踏み切り開始からの秒。戻り値：(足の高さcm, しゃがみ, 腱の力, 切れた, 倒れ)"""
    h = jump_h(k); s_pk = stress(k); brk = s_pk >= S_BREAK
    if tt < 0: return 0, fade((tt + 0.8) / 0.6), 0.25 * s_pk * fade((tt + 0.8) / 0.6), False, 0
    if brk:
        if tt < 0.12: return 0, 1 - tt / 0.3, s_pk * (0.25 + 0.75 * tt / 0.12) , False, 0
        return 0, 0.6, 0, True, fade((tt - 0.3) / 0.5)
    if tt < 0.3: return 0, 1 - tt / 0.3, s_pk * (0.25 + 0.75 * math.sin(tt / 0.3 * math.pi / 2)), False, 0
    v0 = math.sqrt(2 * g * h); tf = 2 * v0 / g; q = tt - 0.3
    if q < tf: return (v0 * q - 0.5 * g * q * q) * 100, 0.0, 0, False, 0
    return 0, max(0, 0.5 - (q - tf) * 1.5), 0, False, 0
def battle(key, title, k, t_jump, cues, extra=0.0):
    dur = cues[-1][0] + D[cues[-1][1]] + 1.2 + extra; n = int(dur * FPS)
    caps = [(vt, vt + D[c] + 0.6, HS_CAP[c]) for vt, c in cues if c in HS_CAP]
    p = writer(f'{G}/c_{key}.mp4'); best = 0.0; sts = []; peak = 0.0
    for f in range(n):
        t = f / FPS; tt = t - t_jump; im = bgimg(); d = ImageDraw.Draw(im)
        hcm, cr, s, brk, fall = jump_state(tt, k); best = max(best, hcm); peak = max(peak, s)
        d.rectangle((0, FLOOR, W, H), fill=(52, 58, 76)); ruler(d, 700)
        if best > 1: d.line((720, FLOOR - best * CM, 1180, FLOOR - best * CM), fill=GOLD, width=3); d.text((1190, FLOOR - best * CM), f'{best:.0f}cm', font=Fo(40), fill=GOLD, anchor='lm')
        figure(d, 930, FLOOR - hcm * CM, crouch=cr, fallen=fall, calf_col=RED if (s >= S_LIMIT or brk) else None)
        if brk and tt < 1.2:
            r = 40 + 200 * fade((tt - 0.12) / 0.3); al = int(220 * (1 - fade((tt - 0.12) / 1.0)))
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); od.ellipse((930 - r, FLOOR - r, 930 + r, FLOOR + r), outline=(255, 60, 60, al), width=12); im.alpha_composite(ov); d = ImageDraw.Draw(im)
            if tt > 0.12: ctext(d, (1030, FLOOR - 200), 'ブチッ！', Fo(80), RED, sw=5)
        gauge(d, 1500, 240, 300, 600, max(s, peak * 0.999) if not brk else S_BREAK * 1.25, broken=brk and tt >= 0.12)
        d.rectangle((0, 0, W, 120), fill=(8, 10, 16, 215))
        ctext(d, (W / 2, 40), title, Fo(40), GOLD); ctext(d, (W / 2, 92), f'筋肉の力：ふつうの全力の {k:.2f}倍' if k != 1 else '筋肉の力：ふつうの全力（筋肉の約90%）', Fb(30), PALE)
        cap = next((c for a0, a1, c in caps if a0 <= t < a1), None)
        if cap:
            f_ = Fo(52); tw = f_.getlength(cap); col = RED if ('切れ' in cap or 'ギリギリ' in cap) else PALE
            d.rounded_rectangle((W / 2 - tw / 2 - 40, H - 170, W / 2 + tw / 2 + 40, H - 80), 16, fill=(8, 10, 16, 220)); d.text((W / 2, H - 125), cap, font=f_, fill=col, anchor='mm')
        disc(d); p.stdin.write(im.convert('RGB').tobytes()); sts.append(round(tt, 3))
    p.stdin.close(); p.wait(); json.dump(dict(st=sts, k=k, t_jump=t_jump), open(f'{G}/c_{key}_st.json', 'w')); return dur, cues
HS_CAP = {'r1b': '記録 約45cm', 'r2b': '記録 約54cm（約2割アップ）', 'r2c': 'アキレス腱 限界ギリギリ！', 'r3b': '踏み切った瞬間…', 'r3c': 'アキレス腱が切れた！'}

def scene(key, dur, draw, cues):
    n = int(dur * FPS); p = writer(f'{G}/c_{key}.mp4')
    for f in range(n):
        im = bgimg(); d = ImageDraw.Draw(im); draw(im, d, f / FPS); disc(d); p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); return dur, cues

def s_title():
    dur = 0.6 + D['intro'] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.6)
        d.rounded_rectangle((W / 2 - 230, 110, W / 2 + 230, 165), 27, fill=(0, 0, 0, 170)); ctext(d, (W / 2, 138), '実データでシミュレーション', Fb(30), GOLD)
        ctext(d, (W / 2, 300), '筋肉のリミッターを', Mi(int(100 * (1.2 - 0.2 * u))), PALE, sw=4)
        ctext(d, (W / 2, 440), '外したら最強？', Mi(int(140 * (1.2 - 0.2 * u))), GOLD, sw=5)
        ctext(d, (W / 2, 545), 'WHAT IF YOU REMOVED YOUR MUSCLE LIMITER?', Fb(30), GRAY)
        d.rectangle((0, FLOOR, W, H), fill=(52, 58, 76))
        cr = 0.5 + 0.5 * math.sin(t * 2.2); figure(d, W / 2, FLOOR, crouch=max(0, cr) * 0.8)
    return scene('title', dur, dr, [(0.6, 'intro')])

def s_myth():
    dur = 0.5 + D['myth'] + 0.8; dd = D['myth']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 110), '人は筋肉を何％使っている？', Mi(72), PALE, sw=3)
        bars = [(0.05, 'よく聞くうわさ', 30, (150, 150, 160), 'うわさ'), (0.3, 'ふつうの人（実験）', 90, GREEN, '約90%'), (0.62, '力を出せる人（実験）', 97, GOLD, '約97%')]
        for i, (tr, lab, v, col, tag) in enumerate(bars):
            if u < tr: continue
            y = 280 + i * 190; gg = ease((u - tr) * dd / 1.0)
            d.text((570, y + 55), lab, font=Fo(44), fill=col, anchor='rm')
            d.rounded_rectangle((600, y + 15, 1700, y + 95), 40, fill=(58, 62, 78))
            d.rounded_rectangle((600, y + 15, 600 + 1100 * v / 100 * gg, y + 95), 40, fill=col)
            d.text((1740, y + 55), f'{v * gg:.0f}%', font=Fo(52), fill=PALE, anchor='lm')
            if i == 0 and u > 0.25: d.line((600, y + 55, 1000, y + 55), fill=RED, width=8); ctext(d, (1380, y + 55), '× まちがい', Fo(48), RED, sw=2)
        if u > 0.82: ctext(d, (W / 2, 900), '隠れている力は、思ったよりずっと少ない！', Mi(56), GOLD, sw=3)
        d.text((24, H - 20), '出典：ひざを伸ばす筋肉の「随意的な活性化率」の研究（PubMed Central PMC1914240 ほか）', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('myth', dur, dr, [(0.5, 'myth')])

def s_rule():
    dur = 0.5 + D['rule'] + 0.8; dd = D['rule']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 100), 'ルール', Mi(80), PALE, sw=3)
        d.rectangle((0, FLOOR, W, H), fill=(52, 58, 76)); figure(d, 420, FLOOR, crouch=0.6, calf_col=RED if u > 0.35 else None)
        if u > 0.35: d.line((420, FLOOR - 20, 600, FLOOR - 200), fill=RED, width=4); d.text((610, FLOOR - 210), 'アキレス腱', font=Fo(40), fill=RED, anchor='ls')
        rows = [(0.05, '体重70kgの人が、垂直跳び'), (0.35, 'ジャンプのとき、アキレス腱には体重の約6〜8倍の力'), (0.7, 'アキレス腱が切れたら、そこで終わり')]
        for i, (tr, txt) in enumerate(rows):
            if u < tr: continue
            y = 260 + i * 150
            d.rounded_rectangle((760, y, W - 120, y + 115), 18, fill=(10, 12, 20, 225), outline=GOLD if i == 2 else None, width=4 if i == 2 else 0)
            d.text((800, y + 58), txt, font=Fo(40), fill=PALE, anchor='lm')
        d.text((24, H - 20), '出典：アキレス腱の力（ジャンプ・ランニングで体重の約6〜8倍）UBC「Injury Tolerance of the Achilles Tendon」ほか', font=Fb(20), fill=(200, 200, 205), anchor='ls')
    return scene('rule', dur, dr, [(0.5, 'rule')])

def card(key, title, big, bigcol, lines):
    dur = 0.6 + D[key] + 0.8
    def dr(im, d, t):
        u = ease(t / 0.4)
        ctext(d, (W / 2, 220), title, Fb(38), (220, 220, 225))
        ctext(d, (W / 2, 370), big, Mi(int(120 * (1.3 - 0.3 * u))), bigcol, sw=5)
        for r, (lab, val, col) in enumerate(lines):
            if t < 0.8 + r * (D[key] / (len(lines) + 1)): continue
            y = 570 + r * 120
            d.rounded_rectangle((W / 2 - 560, y - 48, W / 2 + 560, y + 48), 16, fill=(10, 12, 20, 220))
            d.text((W / 2 - 520, y), lab, font=Fb(36), fill=(210, 210, 215), anchor='lm'); d.text((W / 2 + 520, y), val, font=Fo(52), fill=col, anchor='rm')
    return scene(key, dur, dr, [(0.6, key)])

TABLE = [('ふつうの全力', '45cm', '腱 75%', GREEN), ('リミッター解除（1.11倍）', '54cm', '腱 83%　限界ギリギリ', GOLD), ('1.2倍', '62cm', '腱 90%　危険ゾーン', RED), ('1.5倍', '88cm のはず', '跳ぶ前に切れる', RED)]
def s_sweep():
    dur = 0.5 + D['sweep'] + 1.2; dd = D['sweep']
    rv = [0.05, 0.12, 0.3, 0.62]
    def dr(im, d, t):
        u = (t - 0.5) / dd
        ctext(d, (W / 2, 110), '筋肉の力を上げていくと？', Mi(68), GOLD, sw=3)
        ctext(d, (W / 2, 185), '（％は「切れる」までの割合。限界を超えると危険）', Fb(28), GRAY)
        for i, (a, b, c, col) in enumerate(TABLE):
            if u < rv[i]: continue
            y = 260 + i * 160
            d.rounded_rectangle((160, y, W - 160, y + 130), 18, fill=(10, 12, 20, 225), outline=col if i >= 2 else None, width=4 if i >= 2 else 0)
            d.text((210, y + 65), a, font=Fo(46), fill=PALE, anchor='lm'); d.text((1080, y + 65), b, font=Fo(54), fill=GOLD, anchor='mm'); d.text((W - 210, y + 65), c, font=Fo(42), fill=col, anchor='rm')
    return scene('sweep', dur, dr, [(0.5, 'sweep')])

def s_outro():
    dur = 0.5 + D['outro'] + 2.0; dd = D['outro']
    def dr(im, d, t):
        u = (t - 0.5) / dd
        if u < 0.62:
            ctext(d, (W / 2, 200), 'リミッター ＝ 体を守る安全装置', Mi(76), GOLD, sw=4)
            if u > 0.12:
                d.rounded_rectangle((260, 340, W - 260, 560), 24, fill=(10, 12, 20, 225))
                ctext(d, (W / 2, 400), 'けいれんや感電で、筋肉が全部いっぺんに縮むと…', Fo(42), PALE)
                ctext(d, (W / 2, 490), '自分の筋肉の力で、骨が折れることも', Fo(56), RED)
            if u > 0.4: ctext(d, (W / 2, 720), '強くなるには、腱や骨もゆっくり鍛える', Mi(60), PALE, sw=3)
        else:
            ctext(d, (W / 2, 380), 'リミッター解除で何cm跳べると思った？', Mi(76), PALE, sw=4)
            ctext(d, (W / 2, 500), 'コメントで教えてください', Mi(54), GOLD, sw=3)
            if u > 0.85:
                d.rounded_rectangle((W / 2 - 520, 620, W / 2 + 520, 800), 24, fill=(10, 12, 20, 225), outline=GOLD, width=4)
                ctext(d, (W / 2, 670), '次に見たい雑学は？', Fo(52), PALE); ctext(d, (W / 2, 750), 'リクエスト募集中！', Fo(44), GOLD)
    return scene('outro', dur, dr, [(0.5, 'outro')])

ORDER = ['title', 'myth', 'rule', 'r1', 'res1', 'r2', 'res2', 'sweep', 'r3', 'res3', 'outro']
def build(k):
    if k == 'title': return s_title()
    if k == 'myth': return s_myth()
    if k == 'rule': return s_rule()
    if k == 'sweep': return s_sweep()
    if k == 'outro': return s_outro()
    if k == 'r1': return battle('r1', '1回戦　ふつうの全力', 1.0, 4.6, [(0.2, 'r1a'), (6.0, 'r1b')])
    if k == 'r2': return battle('r2', '2回戦　リミッター解除（筋肉100%）', 1 / 0.9, 4.0, [(0.2, 'r2a'), (5.2, 'r2b'), (8.8, 'r2c')])
    if k == 'r3': return battle('r3', '決勝戦　漫画のリミッター解除（筋肉の力 3倍）', 3.0, 9.6, [(0.2, 'r3a'), (8.0, 'r3b'), (9.75, 'r3c')], extra=1.0)
    if k == 'res1': return card('res1', 'RESULT　1回戦　ふつうの全力', '記録 約45cm', PALE, [('アキレス腱', '切れる手前の約7〜9割', GOLD)])
    if k == 'res2': return card('res2', 'RESULT　2回戦　リミッター解除', '記録 約54cm', GOLD, [('筋肉の力', '約1割アップ', PALE), ('ジャンプ', '約2割アップ', GREEN), ('アキレス腱', '限界ギリギリ', RED)])
    if k == 'res3': return card('res3', 'RESULT　決勝戦　筋肉の力 3倍', '記録 0cm', RED, [('計算上のジャンプ', '約2m15cm', PALE), ('結果', 'アキレス腱が先に切れた', RED)])
if __name__ == '__main__':
    which = sys.argv[1:] or ORDER; res = {}
    for k in which: res[k] = build(k); print('done', k, round(res[k][0], 1), flush=True)
    json.dump(res, open(f'{G}/scenes_{"_".join(which)}.json', 'w'))
