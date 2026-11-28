import json, sys, subprocess, urllib.parse, time
UA='YouTubeVideoBot/1.0 (https://github.com/ryutordmail71-alt/youtube-videos)'
def api(params):
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(dict(params,format='json'))
    for i in range(8):
        r=subprocess.run(['curl','-s','-m','40','-A',UA,url],capture_output=True,text=True).stdout
        try: return json.loads(r)
        except Exception: time.sleep(6+i*4)
    raise SystemExit('api fail: '+r[:200])
def search(q,n=15):
    d=api(dict(action='query',generator='search',gsrsearch=q+' filetype:bitmap',gsrnamespace=6,gsrlimit=n,prop='imageinfo',iiprop='url|extmetadata|size',iiurlwidth=1280))
    out=[]
    for p in (d.get('query',{}).get('pages',{}) or {}).values():
        ii=p['imageinfo'][0]; em=ii.get('extmetadata',{})
        lic=em.get('LicenseShortName',{}).get('value',''); art=em.get('Artist',{}).get('value','')
        import re; art=re.sub('<[^>]+>','',art)[:40]
        out.append(dict(title=p['title'],lic=lic,artist=art,w=ii['width'],h=ii['height'],thumb=ii.get('thumburl'),page=ii.get('descriptionurl')))
        print(f"{p['title'][:70]} | {lic} | {art} | {ii['width']}x{ii['height']}")
    return out
if __name__=='__main__':
    r=search(sys.argv[1], int(sys.argv[2]) if len(sys.argv)>2 else 15)
    json.dump(r,open('/home/claude/tkc/cand/last.json','w'),ensure_ascii=False,indent=0)
