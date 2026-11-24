import json, sys, time, urllib.request, urllib.parse, re, hashlib, os
UA = {'User-Agent': 'video-research-bot/1.0 (educational; contact via site)'}
def get(url, tries=5):
    for k in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(int(e.headers.get('retry-after', 30)) + 2); continue
            raise
    raise RuntimeError('fail ' + url)
def fetch(key, title, width=1800):
    q = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(dict(action='query', titles='File:' + title, prop='imageinfo', iiprop='url|extmetadata', iiurlwidth=width, format='json'))
    p = list(json.loads(get(q))['query']['pages'].values())[0]['imageinfo'][0]; md = p['extmetadata']
    art = re.sub('<[^>]+>', '', md.get('Artist', {}).get('value', '?')).strip(); lic = md.get('LicenseShortName', {}).get('value', '?')
    url = p.get('thumburl') or p['url']; ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or '.jpg'
    out = f'img/{key}{ext}'; open(out, 'wb').write(get(url)); time.sleep(3)
    return dict(key=key, title=title, artist=art, lic=lic, file=out)
if __name__ == '__main__':
    picks = json.load(open(sys.argv[1])); res = json.load(open('credits.json')) if os.path.exists('credits.json') else []
    done = {r['key'] for r in res}
    for k, t in picks.items():
        if k in done: continue
        r = fetch(k, t); res.append(r); print(r, flush=True)
        json.dump(res, open('credits.json', 'w'), ensure_ascii=False, indent=1)
