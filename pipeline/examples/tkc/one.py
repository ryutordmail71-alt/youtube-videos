import sys, tscn as M
P, tot = M.plan(); idx = {k: (fn, pre, off, T) for k, fn, pre, off, T in P}
outs=[]
for a in sys.argv[1:]:
    k, u = a.split(':'); fn, pre, off, T = idx[k]; t = T * float(u)
    im = fn(t, T, off + t, pre).convert('RGB').resize((960, 540)); outs.append(im)
from PIL import Image
sh = Image.new('RGB', (1920, 540 * ((len(outs) + 1) // 2)))
for i, im in enumerate(outs): sh.paste(im, ((i % 2) * 960, (i // 2) * 540))
sh.save('still/one.jpg', quality=85)
