import re
def short(proj, bmod, yomi, picks, hook, nar, cta, kicker, title, en, circ, hook_lines, hook_photo, cta_lines, cta_photo, out_mp4, bgm, out_py):
    s = open('/home/claude/oxy/oshort.py').read()
    s = s.replace("['/home/claude/oxy']; os.chdir('/home/claude/oxy')", f"['/home/claude/{proj}']; os.chdir('/home/claude/{proj}')").replace('import obuild as B', f'import {bmod} as B')
    s = re.sub(r'^B\.YOMI\[:0\] = .*$', lambda m: f'B.YOMI[:0] = {yomi!r}', s, flags=re.M)
    s = re.sub(r'^PICKS = .*$', lambda m: f'PICKS = {picks!r}', s, flags=re.M)
    s = re.sub(r'^HOOK = .*$', lambda m: f'HOOK = {hook!r}', s, flags=re.M)
    s = re.sub(r'^NAR = .*$', lambda m: f'NAR = {nar!r}', s, flags=re.M)
    s = re.sub(r'^CTA = .*$', lambda m: f'CTA = {cta!r}', s, flags=re.M)
    s = s.replace("'息を止めれば、助かる？', font=Fo(BK, 56)", f"{kicker!r}, font=Fo(BK, 56)")
    s = s.replace("d.text((W / 2, 190), 'もし酸素が5秒消えたら', font=fitf('もし酸素が5秒消えたら',", f"d.text((W / 2, 190), {title!r}, font=fitf({title!r},")
    s = s.replace("'What if oxygen vanished for 5 seconds?', font=Fo(BD, 34)", f"{en!r}, font=Fitf_EN")
    s = s.replace('font=Fitf_EN', f"font=fitf({en!r}, BD, 34, 1000)")
    s = s.replace('fill=(80, 170, 230)); d.text((95', f'fill={circ}); d.text((95')
    def L(lines): return '[' + ', '.join(f"({t!r}, {f}, {sz}, {col}, {y})" for t, f, sz, col, y in lines) + ']'
    s = re.sub(r"^card\(\[\('酸素が'.*$", lambda m: f"card({L(hook_lines)}, B.PICK[{hook_photo[0]!r}][{hook_photo[1]}]['file'], 0.1 + D['hook'] + 0.2)", s, flags=re.M)
    s = re.sub(r"^card\(\[\('でも、もし'.*$", lambda m: f"card({L(cta_lines)}, B.PICK[{cta_photo[0]!r}][{cta_photo[1]}]['file'], 0.2 + D['cta'] + 1.5, cta_extra)", s, flags=re.M)
    s = s.replace("'oxy_short.mp4'", repr(out_mp4)).replace('/home/claude/bgm/Long_Note_Two.mp3', f'/home/claude/bgm/{bgm}')
    open(out_py, 'w').write(s)
