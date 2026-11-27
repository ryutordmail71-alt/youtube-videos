"""本物の写真を集める（Openverse 経由。シェルから使える）
使い方：
  python3 photos.py search "Poveglia island" 8        → 候補を表示（ライセンス・作者・説明）
  python3 photos.py get <id> <保存名.jpg>               → 1024px の写真を保存し、credits.json にクレジットを追記
- Wikimedia Commons と Flickr の画像そのものはシェルから取れない（429 / 403）が、Openverse の thumb（full_size）経由なら取れる。
- 1回の検索・取得のあいだは2秒以上あける（ログインなしだと、たくさん続けると数十分止められる）。
- **先に集めた写真があればそれを使う**：`assets/photos/<slug>/`（写真＋credits.json）。なければ自分で集め、使った写真は同じ場所に入れて main に push しておく（1枚300KB以下に縮めてから）。
- ライセンスは CC0 / Public Domain / CC BY を優先。CC BY-SA は、クレジットに「CC BY-SA」と書けば使ってよい。NC（非営利）・ND（改変禁止）は使わない（検索で除外している）。
- 必ず目で見て選ぶ：場所が合っているか、知らない人の顔がはっきり写っていないか、事件・事故・遺体を連想させないか。
"""
import json, os, subprocess, sys, time, urllib.parse
API = 'https://api.openverse.org/v1/images/'
CRED = 'credits.json'
def _get(url, out=None):
    time.sleep(2)
    args = ['curl', '-s', '-m', '40', '-A', 'YouTubeVideoBot/1.0 (https://github.com/ryutordmail71-alt/youtube-videos)']
    if out: args += ['-o', out, '-w', '%{http_code}']
    r = subprocess.run(args + [url], capture_output=True, text=not out)
    return r.stdout
def search(q, n=8):
    url = API + '?' + urllib.parse.urlencode({'q': q, 'license_type': 'commercial,modification', 'mature': 'false'})
    d = json.loads(_get(url))
    if 'results' not in d: print(d); return []
    for r in d['results'][:n]:
        print(f"{r['id']} | {r['license']} {r.get('license_version') or ''} | {(r.get('creator') or '?')[:20]} | {r.get('width')}x{r.get('height')} | {r['title'][:60]}")
    json.dump(d, open('.last_search.json', 'w')); return d['results']
def get(pid, out):
    meta = None
    if os.path.exists('.last_search.json'):   # 検索結果にある情報を使って、APIを呼ぶ回数を減らす
        meta = next((r for r in json.load(open('.last_search.json')).get('results', []) if r['id'] == pid), None)
    if meta is None: meta = json.loads(_get(API + pid + '/'))
    code = _get(API + pid + '/thumb/?full_size=true', out)
    if str(code) != '200': print('取得失敗', code); return None
    c = json.load(open(CRED)) if os.path.exists(CRED) else []
    c.append({'file': out, 'title': meta.get('title'), 'creator': meta.get('creator'), 'license': f"CC {meta.get('license', '').upper()} {meta.get('license_version') or ''}".replace('CC PDM', 'Public Domain').replace('CC CC0', 'CC0'),
              'source': meta.get('foreign_landing_url'), 'provider': meta.get('source')})
    json.dump(c, open(CRED, 'w'), ensure_ascii=False, indent=1); print('保存', out); return out
def credit_text():
    """説明欄に貼るクレジット"""
    c = json.load(open(CRED)) if os.path.exists(CRED) else []
    return '\n'.join(f"・\"{x['title']}\" by {x['creator'] or '作者不明'}（{x['license']}）{x['source']}" for x in c)
if __name__ == '__main__':
    if sys.argv[1] == 'search': search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    elif sys.argv[1] == 'get': get(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'credits': print(credit_text())
