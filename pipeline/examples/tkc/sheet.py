import sys
from PIL import Image, ImageDraw
keys=sys.argv[2].split(','); out=sys.argv[1]
sh=Image.new('RGB',(4*640,len(keys)*360+0),(0,0,0))
for r,k in enumerate(keys):
    for j in range(4):
        im=Image.open(f'still/{k}_{j}.jpg').resize((640,360)); sh.paste(im,(j*640,r*360))
sh.save(out,quality=85)
