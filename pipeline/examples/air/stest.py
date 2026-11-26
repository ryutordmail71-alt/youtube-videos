import sys, os, ascn as S
os.makedirs('/home/claude/air/stills', exist_ok=True)
def fake(out, dur, fn):
    nm = os.path.basename(out)[2:-4]
    for q in (0.1, 0.35, 0.6, 0.8, 0.97):
        fn(dur * q).convert('RGB').resize((960, 540)).save(f'/home/claude/air/stills/{nm}_{int(q*100):02d}.jpg')
S.run = fake
for name in sys.argv[1:]: getattr(S, 'scene_' + name)()
