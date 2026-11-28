"""見ていて飽きないかの自動チェック（視聴維持率のため）。
使い方：python3 retention_check.py <動画.mp4> [main|short]
- 画面がほとんど動かない区間（本編 10秒以上／ショート 3秒以上）
- 音が止まる区間（1秒以上の無音）
- 最初の2秒で画面が動いているか（フック）
を一覧にする。見つかったら、絵の動き・字幕・場面の切り替えを足して直す（直せない理由があればメモに書く）。"""
import subprocess, sys, re
import numpy as np
path = sys.argv[1]; mode = sys.argv[2] if len(sys.argv) > 2 else 'main'
LIM = 10.0 if mode == 'main' else 3.0
# 1) 画面の動き：4fps・小さく縮めて、前のコマとの差を測る
w, h = 160, 90 if mode == 'main' else 160
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps=4,scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
diff = np.r_[0, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))]
moving = diff > 0.6          # 平均で0.6段階以上かわれば「動いている」
static = []; start = None
for i, m in enumerate(moving):
    t = i / 4
    if not m and start is None: start = t
    if m and start is not None:
        if t - start >= LIM: static.append((start, t))
        start = None
if start is not None and len(moving) / 4 - start >= LIM: static.append((start, len(moving) / 4))
if mode == 'main':   # 最後の12秒は終了画面用なので対象外
    endcut = len(moving) / 4 - 12
    static = [(a, min(b, endcut)) for a, b in static if a < endcut and min(b, endcut) - a >= LIM]
# 2) 無音
err = subprocess.run(['ffmpeg', '-v', 'info', '-i', path, '-af', 'silencedetect=noise=-45dB:d=1.0', '-f', 'null', '-'], capture_output=True, text=True).stderr
sil = [(float(a), float(b)) for a, b in re.findall(r'silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)', err)]
# 3) フック：最初の2秒の動き
hook = float(diff[1:9].mean()) if len(diff) > 9 else 0
dur = len(moving) / 4
print(f'長さ {dur:.1f}秒')
print(f'最初の2秒の画面の動き：{hook:.2f}（0.6未満なら、冒頭が止まって見える）')
print(f'画面が {LIM:.0f}秒以上ほぼ止まる区間：{len(static)}か所')
for a, b in static: print(f'  {int(a//60)}:{a%60:04.1f} 〜 {int(b//60)}:{b%60:04.1f}（{b-a:.1f}秒）')
print(f'1秒以上の無音：{len(sil)}か所')
for a, b in sil: print(f'  {int(a//60)}:{a%60:04.1f} 〜 {int(b//60)}:{b%60:04.1f}（{b-a:.1f}秒）')
ok = not static and not [s for s in sil if s[0] < dur - 3] and hook >= 0.6
print('判定：OK' if ok else '判定：直すところあり')
