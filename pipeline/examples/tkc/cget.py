import json,glob,subprocess,sys
UA='YouTubeVideoBot/1.0 (https://github.com/ryutordmail71-alt/youtube-videos)'
allr={}
for f in glob.glob('cand/s_*.json')+['cand/last.json']:
    for r in json.load(open(f)): allr[r['title']]=r
def get(prefix,out):
    m=[r for t,r in allr.items() if t.startswith(prefix)]
    if not m: print('none',prefix); return
    r=m[0]
    import time
    for i in range(5):
        c=subprocess.run(['curl','-s','-m','60','-A',UA,'-o','cand/'+out,'-w','%{http_code}',r['thumb']],capture_output=True,text=True).stdout
        if c=='200': break
        time.sleep(8)
    print(c,out,r['title'],r['lic'])
    meta=json.load(open('cand/meta.json')) if __import__('os').path.exists('cand/meta.json') else {}
    meta[out]=r; json.dump(meta,open('cand/meta.json','w'),ensure_ascii=False,indent=0)
for a in sys.argv[1:]:
    p,o=a.split('=>'); get(p,o)
