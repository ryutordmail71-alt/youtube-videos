import sys, os, jscenes as S
os.makedirs('/home/claude/jmp/stills', exist_ok=True)
def fake(out, dur, fn):
    nm = os.path.basename(out)[2:-4]
    for q in (0.15, 0.45, 0.7, 0.97):
        fn(dur * q).resize((960, 540)).save(f'/home/claude/jmp/stills/{nm}_{int(q*100):02d}.jpg')
S.run = fake
for f in sys.argv[1:]:
    if f.startswith('res'): getattr(S, 'scene_card')
for name in sys.argv[1:]: getattr(S, 'scene_' + name)()
