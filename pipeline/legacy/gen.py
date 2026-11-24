import re
def build(template, src_proj, src_mod, src_pick, proj, cmod, pick, intro, outro, yomi, hdr_jp, hdr_en, redc, tagc, intro_card, outro_card, bgm, note, out):
    s = open(template).read()
    s = s.replace(f'/home/claude/{src_proj}/{src_pick}', f'/home/claude/{proj}/{pick}').replace(f"'/home/claude/{src_proj}'", f"'/home/claude/{proj}'")
    s = s.replace(f'import {src_mod} as C', f'import {cmod} as C')
    s = re.sub(r"^INTRO_N = .*$", lambda m: f"INTRO_N = {intro!r}", s, count=1, flags=re.M)
    s = re.sub(r"^OUTRO_N = .*$", lambda m: f"OUTRO_N = {outro!r}", s, count=1, flags=re.M)
    i = s.index('YOMI[:0] = ['); j = s.index("os.makedirs('voice', exist_ok=True)")
    s = s[:i] + 'YOMI[:0] = ' + repr(yomi) + '\n' + s[j:]
    s = re.sub(r"(d\.text\(\(1870, 32\), )'[^']*'", lambda m: m.group(1) + repr(hdr_jp), s)
    s = re.sub(r"(d\.text\(\(1870, 68\), )(['\"]).*?\2(, font)", lambda m: m.group(1) + repr(hdr_en) + m.group(3), s)
    s = re.sub(r"REDC = \(\d+, \d+, \d+\)", f"REDC = {redc}", s)
    s = re.sub(r"outline=\(\d+, \d+, \d+, 255\), width=3", f"outline={redc + (255,)}, width=3", s)
    s = re.sub(r"^TAGC = \{.*\}$", lambda m: f"TAGC = {tagc!r}", s, flags=re.M)
    s = re.sub(r"card\('intro', \(.*?, PICK\[", lambda m: "card('intro', (" + ', '.join(map(repr, intro_card)) + ", PICK[", s)
    s = re.sub(r"card\('outro', \(.*?, PICK\[", lambda m: "card('outro', (" + ', '.join(map(repr, outro_card)) + ", PICK[", s)
    s = re.sub(r'BGM: \\?"([^"\\]+)\\?"', lambda m: m.group(0).replace(m.group(1), bgm), s)
    s = re.sub(r"(加工をしています。)[^']*'\]", lambda m: m.group(1) + note + "']", s)
    open(out, 'w').write(s)
