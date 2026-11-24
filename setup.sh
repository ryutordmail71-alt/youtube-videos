#!/usr/bin/env bash
# 新しい作業環境で、動画づくりの道具をそろえる（10〜15分ほど）
set -e
REPO=$(cd "$(dirname "$0")" && pwd)
mkdir -p /home/claude/models /home/claude/fonts /home/claude/bgm /home/claude/voicevox

# Python の部品
pip install --break-system-packages -q numpy scipy pillow onnxruntime py7zr >/dev/null 2>&1 || true

# 日本語フォント（Noto CJK）
if [ ! -f /usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc ]; then
  (apt-get update -qq && apt-get install -y -qq fonts-noto-cjk fonts-noto-cjk-extra) >/dev/null 2>&1 || echo "WARN: Noto CJK の入手に失敗"
fi
cp "$REPO/assets/fonts/BebasNeue-Regular.ttf" /home/claude/fonts/

# BGM（Kevin MacLeod, CC BY 4.0）
cd /home/claude/bgm
[ -s Investigations.mp3 ] || curl -sSL -o Investigations.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Investigations.mp3"
[ -s Volatile_Reaction.mp3 ] || curl -sSL -o Volatile_Reaction.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile%20Reaction.mp3"

# 切り抜きモデル（ISNet）
[ -s /home/claude/models/isnet.onnx ] || curl -sSL -o /home/claude/models/isnet.onnx "https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx"

# VOICEVOX エンジン 0.26.2（CPU）
if [ ! -x /home/claude/voicevox/linux-cpu-x64/run ]; then
  cd /home/claude/voicevox
  curl -sSL -o vv.7z.001 "https://github.com/VOICEVOX/voicevox_engine/releases/download/0.26.2/voicevox_engine-linux-cpu-x64-0.26.2.7z.001"
  python3 -c "import py7zr; py7zr.SevenZipFile('vv.7z.001').extractall('.')"
  rm -f vv.7z.001; chmod +x linux-cpu-x64/run
fi

# 過去の動画プロジェクト（部品として import するので、元の場所に置く）
for p in gvm gva gfa; do mkdir -p /home/claude/$p; cp -n "$REPO"/pipeline/examples/$p/* /home/claude/$p/ 2>/dev/null || true; done

# VOICEVOX を起動
cd /home/claude/voicevox/linux-cpu-x64
(nohup ./run --host 127.0.0.1 > /tmp/vv.log 2>&1 &)
for i in $(seq 1 40); do curl -s --noproxy '*' http://127.0.0.1:50021/version && break; sleep 3; done
echo; echo "setup done"
