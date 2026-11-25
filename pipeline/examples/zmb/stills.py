import subprocess, sys, json
from PIL import Image
G='/home/claude/zmb'
def dur(p): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]))
for k in sys.argv[1:]:
    p=f'{G}/c_{k}.mp4' if not k.endswith('.mp4') else k; T=dur(p); ims=[]
    for i,fr in enumerate([0.12,0.35,0.6,0.8,0.97]):
        o=f'{G}/st/{k.replace("/","_")}_{i}.png'; subprocess.run(['ffmpeg','-v','error','-y','-ss',str(T*fr),'-i',p,'-frames:v','1',o]); ims.append(Image.open(o))
    w,h=ims[0].size; s=Image.new('RGB',(w*3//2*1, h*2//2*1)) 
    sheet=Image.new('RGB',(w, h*5//2 + h//2)) if False else None
    for i,im in enumerate(ims): im.resize((w//2,h//2)).save(f'{G}/st/{k}_s{i}.png')
    cs=Image.new('RGB',(w, (h//2)*3)); 
    for i,im in enumerate(ims[:6]): cs.paste(im.resize((w//2,h//2)), ((i%2)*w//2, (i//2)*h//2))
    cs.save(f'{G}/st/{k}_sheet.png')
