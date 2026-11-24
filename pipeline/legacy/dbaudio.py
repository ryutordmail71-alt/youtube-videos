import json, os, re, sys, wave, urllib.request, urllib.parse
import numpy as np
sys.path.insert(0, '/home/claude/db'); import dbcontent as C
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
BASE = 'http://127.0.0.1:50021'; SR = 44100
def post(path, data=None, raw=False):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode() if data is not None else b'', headers={'Content-Type': 'application/json'}, method='POST')
    r = opener.open(req, timeout=300).read(); return r if raw else json.loads(r)
def yomi(t):
    for a, b in C.YOMI: t = t.replace(a, b)
    return t
def kana(text, spk):
    q = post('/audio_query?' + urllib.parse.urlencode({'text': yomi(text), 'speaker': spk}))
    return q['kana']
def tts(text, spk, speed=1.1, inton=1.15, pitch=0.0, vol=1.0, gap=0.28):
    pieces = []
    for s in [s for s in re.split(r'(?<=[。！？])', text) if s.strip()]:
        q = post('/audio_query?' + urllib.parse.urlencode({'text': yomi(s), 'speaker': spk}))
        q.update(speedScale=speed, intonationScale=inton, pitchScale=pitch, volumeScale=vol, prePhonemeLength=0.05, postPhonemeLength=0.1, outputSamplingRate=SR)
        w = post(f'/synthesis?speaker={spk}', q, raw=True); open('/tmp/dbq.wav', 'wb').write(w)
        with wave.open('/tmp/dbq.wav') as f: pieces.append(np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768)
        pieces.append(np.zeros(int(SR * gap), np.float32))
    return np.concatenate(pieces[:-1])
def save(y, out):
    y = np.clip(y, -1, 1)
    with wave.open(out, 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((y * 32767).astype(np.int16).tobytes())
def shout(word, spk, db):
    """叫び：dBに応じて声を張り、歪み・エコーを足す。最終的なピークは安全な範囲に抑える。"""
    t = (db / 194.0)
    y = tts(word, spk, speed=1.0 + 0.1 * t, inton=1.2 + 0.8 * t, pitch=0.02 + 0.06 * t if db >= 60 else 0.0, vol=1.0)
    y = y / (np.abs(y).max() + 1e-9)
    if db >= 110:  # 歪み（割れた感じ）
        drive = 1 + 6 * (db - 100) / 94
        y = np.tanh(y * drive) / np.tanh(drive)
    if db >= 100:  # エコー
        out = np.concatenate([y, np.zeros(int(SR * 1.2), np.float32)])
        for k, (dl, g) in enumerate([(0.13, 0.45), (0.27, 0.3), (0.41, 0.18), (0.6, 0.1)]):
            n = int(SR * dl); out[n:n + len(y)] += y * g * min(1, (db - 90) / 60)
        y = out
    if db >= 150:  # どーん（低音の衝撃）
        n = int(SR * 1.4); tt = np.arange(n) / SR
        boom = np.sin(2 * np.pi * (55 * np.exp(-tt * 1.5)) * tt) * np.exp(-tt * 3.2)
        boom += np.random.default_rng(1).normal(0, 1, n) * np.exp(-tt * 9) * 0.35
        y = np.concatenate([y, np.zeros(max(0, n - len(y)), np.float32)]); y[:n] += boom * 0.8 * min(1, (db - 140) / 50)
    # 音量：0dB→かなり小さく、194dB→上限（ピーク -3dBFS 程度）。実際の音量ではない。
    peak = 10 ** ((-34 + 31 * min(1, db / 150)) / 20)
    y = y / (np.abs(y).max() + 1e-9) * peak
    return y.astype(np.float32)

if __name__ == '__main__':
    os.makedirs('voice', exist_ok=True); D = {}
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode == 'kana':
        for i, l in enumerate(C.L): print(l['db'], kana(l['nar'], 13)); print('   ', kana(l['word'], l['spk']))
        for t in [C.INTRO, C.KRAKA['nar'], C.OUTRO]: print(kana(t, 13))
        sys.exit()
    def nar(key, text):
        p = f'voice/{key}.wav'
        if not os.path.exists(p): save(tts(text, 13), p)
    nar('intro', C.INTRO); nar('kraka', C.KRAKA['nar']); nar('outro', C.OUTRO)
    for i, l in enumerate(C.L):
        nar(f'n{i}', l['nar'])
        p = f'voice/s{i}.wav'
        if not os.path.exists(p): save(shout(l['word'], l['spk'], l['db']), p)
    if not os.path.exists('voice/hook.wav'): save(shout(C.HOOK_WORD, C.SPK_Q, 10), 'voice/hook.wav')
    if not os.path.exists('voice/end.wav'): save(tts(C.END_WORD, 35, speed=0.9) * 0.4, 'voice/end.wav')
    for f in sorted(os.listdir('voice')):
        with wave.open('voice/' + f) as w: D[f[:-4]] = w.getnframes() / SR
    json.dump(D, open('dur.json', 'w'), indent=0); print('done', D)
