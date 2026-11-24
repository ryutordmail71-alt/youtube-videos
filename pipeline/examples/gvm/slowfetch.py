import hashlib, json, time, urllib.request, urllib.parse
UA = {'User-Agent': 'MyVideoTool/1.0 (educational video; contact@example.org) python-urllib'}
picks = {"macro": "Mosquito-Macro.jpg", "aedes": "Aedes aegypti mosquito.jpg", "frenzy": "Mosquito frenzy (48750692121).jpg"}
for k, t in picks.items():
    n = t.replace(' ', '_'); h = hashlib.md5(n.encode()).hexdigest(); q = urllib.parse.quote(n)
    url = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/1280px-{q}'
    for attempt in range(12):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read(); open(f'img/{k}.jpg', 'wb').write(b); print('ok', k, len(b), flush=True); break
        except urllib.error.HTTPError as e:
            ra = int(e.headers.get('retry-after') or 120); print('wait', k, e.code, ra, flush=True); time.sleep(ra + 10)
    time.sleep(30)
print('ALL DONE')
