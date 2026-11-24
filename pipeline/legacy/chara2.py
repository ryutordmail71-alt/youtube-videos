"""本格派だけどアホっぽいキャラ（SVG→Chromiumでレンダリング）"""
import os, hashlib
from PIL import Image

def eyes_svg(kind, lx, rx, y, r, ink='#2b1d14'):
    s = ''
    if kind == 'derp':  # 左右で大きさ・視線がバラバラ
        s += f'<ellipse cx="{lx}" cy="{y}" rx="{r*1.15}" ry="{r*1.25}" fill="#fff" stroke="{ink}" stroke-width="5"/>'
        s += f'<ellipse cx="{rx}" cy="{y+4}" rx="{r*0.95}" ry="{r*1.05}" fill="#fff" stroke="{ink}" stroke-width="5"/>'
        s += f'<circle cx="{lx+r*0.45}" cy="{y+r*0.25}" r="{r*0.42}" fill="{ink}"/><circle cx="{lx+r*0.32}" cy="{y+r*0.08}" r="{r*0.13}" fill="#fff"/>'
        s += f'<circle cx="{rx-r*0.35}" cy="{y-r*0.2}" r="{r*0.36}" fill="{ink}"/><circle cx="{rx-r*0.46}" cy="{y-r*0.34}" r="{r*0.11}" fill="#fff"/>'
    elif kind == 'shout':  # ギュッと閉じた ><
        s += f'<path d="M{lx-r} {y-r*0.8} L{lx+r*0.8} {y} L{lx-r} {y+r*0.8}" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
        s += f'<path d="M{rx+r} {y-r*0.8} L{rx-r*0.8} {y} L{rx+r} {y+r*0.8}" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
    elif kind == 'calm':  # 半目（ぼーっと）
        for x in (lx, rx):
            s += f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*1.1}" fill="#fff" stroke="{ink}" stroke-width="5"/>'
            s += f'<circle cx="{x}" cy="{y+r*0.35}" r="{r*0.42}" fill="{ink}"/>'
            s += f'<path d="M{x-r*1.05} {y-r*0.1} Q{x} {y-r*0.35} {x+r*1.05} {y-r*0.1} L{x+r*1.05} {y-r*1.2} L{x-r*1.05} {y-r*1.2} Z" fill="var(--lid)" stroke="{ink}" stroke-width="5"/>'
    elif kind == 'dizzy':
        for x in (lx, rx):
            s += f'<path d="M{x} {y} m-2 0 a2 2 0 1 1 4 0 a6 6 0 1 1 -12 0 a10 10 0 1 1 20 0 a14 14 0 1 1 -28 0 a18 18 0 1 1 36 0" fill="none" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>'
    elif kind == 'wide':
        for x in (lx, rx):
            s += f'<circle cx="{x}" cy="{y}" r="{r*1.3}" fill="#fff" stroke="{ink}" stroke-width="5"/><circle cx="{x}" cy="{y}" r="{r*0.28}" fill="{ink}"/>'
    elif kind == 'closed':
        for x in (lx, rx):
            s += f'<path d="M{x-r} {y} Q{x} {y+r*0.7} {x+r} {y}" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
    return s

def mouth_svg(m, cx, y, w, ink='#2b1d14', teeth=True):
    if m <= 0.02:  # ぽかん口＋出っ歯
        s = f'<path d="M{cx-w*0.45} {y} Q{cx} {y+w*0.28} {cx+w*0.45} {y}" fill="#7a2a2a" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
        if teeth: s += f'<rect x="{cx-w*0.17}" y="{y-2}" width="{w*0.16}" height="{w*0.2}" rx="4" fill="#fff" stroke="{ink}" stroke-width="3.5"/><rect x="{cx+0.01*w}" y="{y-2}" width="{w*0.16}" height="{w*0.2}" rx="4" fill="#fff" stroke="{ink}" stroke-width="3.5"/>'
        return s
    mw = w * (0.35 + 0.45 * m); mh = w * (0.25 + 0.95 * m)
    s = f'<path d="M{cx-mw} {y-mh*0.1} Q{cx} {y-mh*0.35} {cx+mw} {y-mh*0.1} Q{cx+mw*0.9} {y+mh} {cx} {y+mh} Q{cx-mw*0.9} {y+mh} {cx-mw} {y-mh*0.1} Z" fill="#5a1620" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>'
    s += f'<ellipse cx="{cx}" cy="{y+mh*0.78}" rx="{mw*0.55}" ry="{mh*0.22}" fill="#ef7b86"/>'  # 舌
    if m > 0.5: s += f'<ellipse cx="{cx}" cy="{y+mh*0.12}" rx="{mw*0.1}" ry="{mh*0.12}" fill="#c9455a"/>'  # のどちんこ
    if teeth: s += f'<rect x="{cx-w*0.17}" y="{y-mh*0.22}" width="{w*0.16}" height="{w*0.2}" rx="4" fill="#fff" stroke="{ink}" stroke-width="3.5"/><rect x="{cx+0.01*w}" y="{y-mh*0.22}" width="{w*0.16}" height="{w*0.2}" rx="4" fill="#fff" stroke="{ink}" stroke-width="3.5"/>'
    return s

def hamster(mouth=0.0, eyes='derp', sweat=False, ear=False, arms_up=0.0):
    """B案：ヘッドセットを付けたハムスター『こえまる』"""
    ink = '#3a2416'
    arm_y = 430 - 150 * arms_up
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="640" viewBox="0 0 600 640" style="--lid:#e9a868">
<defs>
 <radialGradient id="fur" cx="40%" cy="30%" r="75%"><stop offset="0" stop-color="#ffd79a"/><stop offset="0.55" stop-color="#f0a85a"/><stop offset="1" stop-color="#c9772f"/></radialGradient>
 <radialGradient id="belly" cx="50%" cy="35%" r="70%"><stop offset="0" stop-color="#fffaf0"/><stop offset="1" stop-color="#f3dcc0"/></radialGradient>
 <radialGradient id="ear" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#ff9fae"/><stop offset="1" stop-color="#e2707f"/></radialGradient>
 <radialGradient id="cheek" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff7d8c" stop-opacity="0.85"/><stop offset="1" stop-color="#ff7d8c" stop-opacity="0"/></radialGradient>
 <linearGradient id="metal" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#5d6470"/><stop offset="1" stop-color="#22262d"/></linearGradient>
 <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>
</defs>
<ellipse cx="300" cy="600" rx="190" ry="24" fill="#000" opacity="0.35" filter="url(#sh)"/>
<!-- ears -->
<g stroke="{ink}" stroke-width="7">
 <circle cx="160" cy="150" r="58" fill="url(#fur)"/><circle cx="160" cy="152" r="34" fill="url(#ear)" stroke="none"/>
 <circle cx="440" cy="150" r="58" fill="url(#fur)"/><circle cx="440" cy="152" r="34" fill="url(#ear)" stroke="none"/>
</g>
<!-- body -->
<path d="M300 110 C430 110 505 210 505 360 C505 500 420 590 300 590 C180 590 95 500 95 360 C95 210 170 110 300 110 Z" fill="url(#fur)" stroke="{ink}" stroke-width="8"/>
<path d="M300 300 C390 300 440 370 440 450 C440 530 380 575 300 575 C220 575 160 530 160 450 C160 370 210 300 300 300 Z" fill="url(#belly)"/>
<!-- ahoge -->
<path d="M300 112 C285 70 320 55 305 25" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>
<path d="M300 112 C285 70 320 55 305 25" fill="none" stroke="#f0a85a" stroke-width="3" stroke-linecap="round"/>
<!-- rim light -->
<path d="M150 230 C175 170 230 135 290 128" fill="none" stroke="#fff6dc" stroke-width="10" stroke-linecap="round" opacity="0.8"/>
<!-- cheeks -->
<ellipse cx="170" cy="330" rx="62" ry="44" fill="url(#cheek)"/><ellipse cx="430" cy="330" rx="62" ry="44" fill="url(#cheek)"/>
{eyes_svg(eyes, 222, 378, 255, 34, ink)}
<!-- nose -->
<path d="M288 296 Q300 288 312 296 Q300 312 288 296 Z" fill="#d9566b" stroke="{ink}" stroke-width="4"/>
<path d="M300 306 L300 318" stroke="{ink}" stroke-width="4"/>
{mouth_svg(mouth, 300, 320, 110, ink)}
<!-- whiskers -->
<g stroke="{ink}" stroke-width="3.5" stroke-linecap="round" opacity="0.75"><path d="M200 305 L135 292"/><path d="M200 318 L132 322"/><path d="M400 305 L465 292"/><path d="M400 318 L468 322"/></g>
<!-- headset -->
<path d="M120 245 C120 95 480 95 480 245" fill="none" stroke="url(#metal)" stroke-width="16" stroke-linecap="round"/>
<rect x="96" y="222" width="44" height="78" rx="18" fill="url(#metal)" stroke="#111" stroke-width="4"/>
<rect x="460" y="222" width="44" height="78" rx="18" fill="url(#metal)" stroke="#111" stroke-width="4"/>
<path d="M118 290 C130 360 180 385 228 380" fill="none" stroke="#2a2e35" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="236" cy="380" rx="17" ry="12" fill="#1c1f24" stroke="#000" stroke-width="3"/>
'''
    # arms
    if ear:
        s += f'<path d="M150 420 C110 380 95 320 112 270" fill="none" stroke="{ink}" stroke-width="30" stroke-linecap="round"/><path d="M150 420 C110 380 95 320 112 270" fill="none" stroke="#f0a85a" stroke-width="20" stroke-linecap="round"/>'
        s += f'<path d="M450 420 C490 380 505 320 488 270" fill="none" stroke="{ink}" stroke-width="30" stroke-linecap="round"/><path d="M450 420 C490 380 505 320 488 270" fill="none" stroke="#f0a85a" stroke-width="20" stroke-linecap="round"/>'
    else:
        for sx in (-1, 1):
            x0 = 300 + sx * 150; x1 = 300 + sx * (175 + 40 * arms_up)
            s += f'<path d="M{x0} 440 Q{300+sx*190} 440 {x1} {arm_y}" fill="none" stroke="{ink}" stroke-width="30" stroke-linecap="round"/><path d="M{x0} 440 Q{300+sx*190} 440 {x1} {arm_y}" fill="none" stroke="#f0a85a" stroke-width="20" stroke-linecap="round"/>'
            s += f'<circle cx="{x1}" cy="{arm_y}" r="17" fill="#ffd8b0" stroke="{ink}" stroke-width="5"/>'
    # feet
    s += f'<ellipse cx="235" cy="585" rx="42" ry="20" fill="#ffd8b0" stroke="{ink}" stroke-width="6"/><ellipse cx="365" cy="585" rx="42" ry="20" fill="#ffd8b0" stroke="{ink}" stroke-width="6"/>'
    if sweat: s += '<path d="M470 120 C450 160 452 178 470 182 C488 178 490 160 470 120 Z" fill="#9fd4ff" stroke="#3a6a9a" stroke-width="4"/>'
    return s + '</svg>'

def blob(mouth=0.0, eyes='derp', sweat=False, ear=False, arms_up=0.0):
    """A案：ツヤツヤのおもち型（前のこえまるの本格版）"""
    ink = '#4a2a10'
    arm_y = 430 - 150 * arms_up
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="640" viewBox="0 0 600 640" style="--lid:#f4b04a">
<defs>
 <radialGradient id="b" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="#ffe9a8"/><stop offset="0.5" stop-color="#ffbe4d"/><stop offset="1" stop-color="#e07e1c"/></radialGradient>
 <radialGradient id="cheek" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff6f7f" stop-opacity="0.8"/><stop offset="1" stop-color="#ff6f7f" stop-opacity="0"/></radialGradient>
 <linearGradient id="metal" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#5d6470"/><stop offset="1" stop-color="#22262d"/></linearGradient>
 <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>
 <filter id="gl"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<ellipse cx="300" cy="600" rx="210" ry="24" fill="#000" opacity="0.35" filter="url(#sh)"/>
<path d="M300 92 C292 55 330 45 312 12" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>
<path d="M300 140 C450 140 530 250 530 380 C530 520 430 590 300 590 C170 590 70 520 70 380 C70 250 150 140 300 140 Z" fill="url(#b)" stroke="{ink}" stroke-width="8"/>
<path d="M300 140 C300 120 300 100 300 92" stroke="{ink}" stroke-width="9"/>
<ellipse cx="200" cy="215" rx="70" ry="34" fill="#fffbe8" opacity="0.85" filter="url(#gl)" transform="rotate(-22 200 215)"/>
<ellipse cx="185" cy="210" rx="22" ry="12" fill="#fff" transform="rotate(-22 185 210)"/>
<ellipse cx="160" cy="380" rx="62" ry="40" fill="url(#cheek)"/><ellipse cx="440" cy="380" rx="62" ry="40" fill="url(#cheek)"/>
{eyes_svg(eyes, 222, 378, 300, 36, ink)}
{mouth_svg(mouth, 300, 375, 120, ink)}
<path d="M95 300 C95 160 505 160 505 300" fill="none" stroke="url(#metal)" stroke-width="16" stroke-linecap="round"/>
<rect x="68" y="282" width="46" height="80" rx="18" fill="url(#metal)" stroke="#111" stroke-width="4"/>
<rect x="486" y="282" width="46" height="80" rx="18" fill="url(#metal)" stroke="#111" stroke-width="4"/>
<path d="M92 350 C105 420 170 445 225 438" fill="none" stroke="#2a2e35" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="233" cy="438" rx="17" ry="12" fill="#1c1f24" stroke="#000" stroke-width="3"/>
'''
    for sx in (-1, 1):
        x0 = 300 + sx * 215; x1 = 300 + sx * (250 + 30 * arms_up)
        if ear: x1, ay = 300 + sx * 240, 300
        else: ay = arm_y
        s += f'<path d="M{x0} 450 Q{300+sx*262} 440 {x1} {ay}" fill="none" stroke="{ink}" stroke-width="28" stroke-linecap="round"/><path d="M{x0} 450 Q{300+sx*262} 440 {x1} {ay}" fill="none" stroke="#ffbe4d" stroke-width="18" stroke-linecap="round"/>'
    if sweat: s += '<path d="M480 150 C460 190 462 208 480 212 C498 208 500 190 480 150 Z" fill="#9fd4ff" stroke="#3a6a9a" stroke-width="4"/>'
    return s + '</svg>'

CACHE = '/home/claude/db/sprites'
_pw = None
def render(svg, size):
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.md5((svg + str(size)).encode()).hexdigest(); p = f'{CACHE}/{key}.png'
    if not os.path.exists(p):
        global _pw
        if _pw is None:
            from playwright.sync_api import sync_playwright
            pw = sync_playwright().start(); br = pw.chromium.launch(); pg = br.new_page(viewport={'width': 600, 'height': 640}, device_scale_factor=2)
            _pw = (pw, br, pg)
        pg = _pw[2]
        pg.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
        pg.locator('svg').screenshot(path=p, omit_background=True)
    im = Image.open(p).convert('RGBA')
    w = int(size * 1.3); return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)

if __name__ == '__main__':
    S = '/tmp/claude-0/-home-claude/3f2fb178-41da-56af-8da6-007907094230/scratchpad/'
    vs = [dict(), dict(mouth=0.35, eyes='calm'), dict(mouth=1.0, eyes='shout', arms_up=1.0), dict(eyes='dizzy', sweat=True, mouth=0.15), dict(eyes='shout', ear=True, sweat=True)]
    for name, fn in (('A', blob), ('B', hamster)):
        out = Image.new('RGB', (5 * 400, 440), (28, 32, 44))
        for i, v in enumerate(vs):
            c = render(fn(**v), 300); out.paste(c, (i * 400 + (400 - c.width) // 2, 10), c)
        out.save(S + f'chara_{name}.jpg', quality=90)
