import sys, os, mscn as S
os.makedirs('/home/claude/mrt/stills', exist_ok=True)
def fake(out, dur, fn):
    nm = os.path.basename(out)[2:-4]
    for q in (0.05, 0.3, 0.55, 0.8, 0.97):
        fn(dur * q).convert('RGB').resize((960, 540)).save(f'/home/claude/mrt/stills/{nm}_{int(q*100):02d}.jpg')
S.run = fake
if sys.argv[1] == 'static': S.statics()
