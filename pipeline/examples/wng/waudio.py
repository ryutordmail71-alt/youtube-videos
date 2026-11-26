"""ナレーション音声（VOICEVOX 青山龍星 13）。python3 baudio.py [kana]"""
import json, os, sys, urllib.request, urllib.parse, wave
import wcontent as C
os.environ['NO_PROXY'] = '127.0.0.1,localhost'
op = urllib.request.build_opener(urllib.request.ProxyHandler({})); BASE = 'http://127.0.0.1:50021'
def post(path, data=None, raw=False):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode() if data is not None else b'', headers={'Content-Type': 'application/json'}, method='POST')
    r = op.open(req, timeout=300).read(); return r if raw else json.loads(r)
def yomi(t):
    for a, b in C.YOMI: t = t.replace(a, b)
    return t
if __name__ == '__main__':
    os.makedirs('voice', exist_ok=True); dur = json.load(open('dur.json')) if os.path.exists('dur.json') else {}
    for k, txt in C.NAR.items():
        q = post('/audio_query?' + urllib.parse.urlencode(dict(text=yomi(txt), speaker=13)))
        if len(sys.argv) > 1: print(k, q['kana']); continue
        out = f'voice/{k}.wav'
        if os.path.exists(out) and k in dur: continue
        q['speedScale'] = 1.12; q['prePhonemeLength'] = 0.05; q['postPhonemeLength'] = 0.1; q['volumeScale'] = 1.0
        open(out, 'wb').write(post('/synthesis?speaker=13', q, raw=True))
        with wave.open(out) as w: dur[k] = w.getnframes() / w.getframerate()
        json.dump(dur, open('dur.json', 'w'), ensure_ascii=False, indent=0)
