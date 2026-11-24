import json, os, sys, urllib.request, urllib.parse, time
sys.path.insert(0, '/home/claude/video')
from scripts import MOVES, ORDER

BASE = 'http://127.0.0.1:50021'
OUT = '/home/claude/video/voice'
os.environ['NO_PROXY'] = '127.0.0.1,localhost'
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def get(path):
    return json.loads(opener.open(BASE + path, timeout=60).read())

def post(path, data=None, raw=False):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode() if data is not None else b'',
                                 headers={'Content-Type': 'application/json'}, method='POST')
    r = opener.open(req, timeout=300).read()
    return r if raw else json.loads(r)

# readings that the engine tends to get wrong, applied only to the spoken text
YOMI = [('|', ''), ('〜', 'から'), ('−', 'マイナス'), ('3.3', '3てん3'), ('89.2', '89てん2'),
        ('1万ボルト', 'いちまんボルト'), ('10まんボルト', 'じゅうまんボルト'), ('「ひんし」', 'ひんし'),
        ('1000℃', 'せんど'), ('1538℃', 'せんごひゃくさんじゅうはちど'), ('660℃', 'ろっぴゃくろくじゅうど'),
        ('3000℃', 'さんぜんど'), ('196℃', 'ひゃくきゅうじゅうろくど'), ('89てん2℃', 'はちじゅうきゅうてんにど'),
        ('1基', 'いっき'), ('1軒', 'いっけん'), ('1秒', 'いちびょう'), ('1g', 'いちグラム'),
        ('60kg', 'ろくじゅっキロ'), ('12kg', 'じゅうにキロ'), ('100kg', 'ひゃっキロ'), ('400杯', 'よんひゃっぱい'),
        ('6000気圧', 'ろくせんきあつ'), ('10気圧', 'じっきあつ'), ('2から4気圧', 'にからよんきあつ'),
        ('1000分の1秒', 'せんぶんのいちびょう'), ('3万アンペア', 'さんまんアンペア'), ('30億ワット', 'さんじゅうおくワット'),
        ('600万世帯', 'ろっぴゃくまんせたい'), ('100万キロワット', 'ひゃくまんキロワット'), ('24万キロカロリー', 'にじゅうよんまんキロカロリー'),
        ('10万キロカロリー', 'じゅうまんキロカロリー'), ('4か月', 'よんかげつ'), ('3個', 'さんこ'), ('2時間', 'にじかん'),
        ('撃った', 'うった'), ('撃つ', 'うつ'), ('釘', 'くぎ'), ('凍りつく', 'こおりつく')]

def yomi(t):
    for a, b in YOMI: t = t.replace(a, b)
    return t

def main(style_name='ノーマル', speed=1.12, which=None):
    sp = get('/speakers')
    sid = None
    for s in sp:
        if '青山' in s['name']:
            print('speaker', s['name'], [(x['name'], x['id']) for x in s['styles']])
            for x in s['styles']:
                if x['name'] == style_name: sid = x['id']
            if sid is None: sid = s['styles'][0]['id']
    assert sid is not None, 'speaker not found'
    os.makedirs(OUT, exist_ok=True)
    for k in (which or ORDER):
        for i, ln in enumerate(MOVES[k]['lines']):
            text = yomi(ln['text'])
            q = post('/audio_query?' + urllib.parse.urlencode({'text': text, 'speaker': sid}))
            q['speedScale'] = speed; q['intonationScale'] = 1.15; q['volumeScale'] = 1.0
            q['prePhonemeLength'] = 0.05; q['postPhonemeLength'] = 0.08
            q['outputSamplingRate'] = 44100
            if ln.get('reveal'): q['speedScale'] = speed * 0.95; q['intonationScale'] = 1.3
            wav = post(f'/synthesis?speaker={sid}', q, raw=True)
            open(f'{OUT}/{k}_{i}.wav', 'wb').write(wav)
            print(k, i, q.get('kana', ''), flush=True)

if __name__ == '__main__':
    main(which=sys.argv[1:] or None)
