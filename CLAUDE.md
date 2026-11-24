# YouTube 科学シミュレーション動画：自動制作の手順書

このリポジトリは、日本語の YouTube チャンネル向けに「ネタ考案 → 動画制作 → 投稿」を自動で進めるための作業場所です。
毎回まっさらな環境で始まるので、最初に必ず `bash setup.sh` を実行してください。

## チャンネルの方針
- 子ども〜大人向けの、科学・もしも・バトル系の解説動画（いわゆる「ドパガキ」層にも刺さるもの）。
- 型：**実データをもとにした単純化シミュレーション**で「予想を裏切る」結論を見せる。必ず画面に「※実データをもとにした、単純化した空想のシミュレーションです」を入れる。
- 伸びた回：巨人 vs 蚊、巨人 vs 人間の綱引き、巨人は立つと気絶する？（二乗三乗の法則・人体スケール系が強い）。

## 1本ぶんの成果物（すべて必須）
1. **本編**（4〜5分、1920×1080、30fps、80MB 以下、映像約1100kbps）
2. **ショート**（約30〜37秒、1080×1920）。最初の1秒でフック。最後は答えを伏せて「答えは 画面の下の関連動画で ↓」。
3. **横サムネ**（1280×720）と**縦カバー**（1080×1920）：明朝体（Noto Serif CJK Black）、アクセント色は1色（金 #FFD250）、上に「実データでシミュレーション」、小さな英語の1行。
4. **クレジット txt**、**タイトル案3つ**、**ショートのタイトル**、**ハッシュタグ**、**固定コメント**。

## 制作のスタイル（今までと同じ品質を守る）
- ナレーション：VOICEVOX「青山龍星」（speaker 13）、speedScale 1.12。数字や漢字の読みは YOMI 表で直し、`python3 xaudio.py kana` で読みを必ず確認してから合成。
- BGM：Kevin MacLeod（Investigations / Volatile Reaction、CC BY 4.0）。効果音はすべてプログラムで合成。
- 画像：Wikimedia Commons の自由ライセンス画像（クレジット必須）。Commons は 429 が出やすいので、ダメなら自作の絵で代用。
- 構成：タイトル → データ比較 → ルール → 1回戦 → 結果 → 種明かし → 人数・条件を変えた表 → 決勝 → 結果 → まとめ（法則の話）→ コメント誘導。
- 音量：acompressor → loudnorm I=-14:TP=-2.5 → alimiter。仕上がり -13〜-15 LUFS、ピーク -1 dBFS 以下。
- 参考になるコード：`pipeline/examples/`（gvm＝巨人vs蚊、gva＝巨人vs綱引き、gfa＝巨人は気絶する？）、`pipeline/legacy/`（それ以前の動画の部品）。`setup.sh` が examples を /home/claude/gvm などにコピーするので、そのまま import できる。
  - 背景・巨人の描画：gvm/grender.py、gva/arender.py（群衆・回転・土けむり）、gfa/frender.py（メーター・視界が暗くなる演出）
  - 場面の作り方：gva/ascenes.py、gfa/fscenes.py／音のミックス：gva/mixlib.py（一時ファイルは出力名ごとに分けてある）
- メモリは約8GB。描画プロセスは同時に**2つまで**（それ以上は強制終了されやすい）。

## 品質チェック（公開前に必ず全部）
- 数値は資料で確認し、出典をクレジットに書く。推定・仮定は画面と説明欄に「目安」「仮定」と明記。
- 各場面の静止画を並べて、文字の重なり・はみ出し・欠け（フォントにない記号は □ になる）を目で確認。
- ナレーションと画面の数字が一致しているか確認。
- ffprobe で長さ、ebur128 で音量を確認。
- 基準に届かない場合は**公開しない**。その日の分はスキップして、理由をユーザーに知らせる。

## ネタの流れ（ユーザーは「ネタだけ先に確認」を選択）
- `topics/queue.md` がネタの一覧。状態は `提案中` → `OK`（ユーザーが承認）→ `制作中` → `投稿済み`（または `差し替え`）。
- 週に1回、次の1週間分（1日3本 × 7日 = 21本、枠は 03:00 / 06:00 / 11:00）を `提案中` で追記し、ユーザーに確認を頼む。過去のネタと重ならないようにする。
- 制作では **`OK` のネタだけ**を上から順に使う。`OK` がなければ作らずに、ユーザーに承認を頼む。

## 投稿（Metricool → YouTube）
1. 完成品を**枠ごとのブランチ**（3時枠＝`media-03`、6時枠＝`media-06`、11時枠＝`media-11`）に置く。履歴をためないよう、毎回まっさらな orphan ブランチで作って force push する（同時に動く別の枠の動画を消さないよう、ブランチは必ず自分の枠のものだけ）：
   ```
   B=media-03   # 自分の枠に合わせる
   rm -rf /home/claude/media-wt && mkdir -p /home/claude/media-wt && cd /home/claude/media-wt
   git init -q -b $B && git remote add origin https://github.com/ryutordmail71-alt/youtube-videos
   mkdir <slug> && cp <本編.mp4> <ショート.mp4> <サムネ.jpg> <slug>/
   git add -A && git -c user.name=Claude -c user.email=noreply@anthropic.com commit -qm "media for <slug>"
   git push -f origin $B
   ```
   URL：`https://raw.githubusercontent.com/ryutordmail71-alt/youtube-videos/<ブランチ>/<slug>/<file>.mp4`（`curl -sI` で 200 と content-length を確認してから Metricool に渡す）
2. Metricool `createScheduledPost`（blogId **8312411**、YouTube のみ）：
   - 本編：`youtubeData.type="video"`、ショート：`type="short"`
   - `privacy="public"`（ユーザー指定：ネタ承認済みなら公開でよい）、`madeForKids=false`、`category="SCIENCE_TECHNOLOGY"`、`isAiGeneratedContent=false`（リアルな偽映像ではないため）、tags を付ける
   - `text`＝説明欄：要約、固定コメントの文、ハッシュタグ、クレジット全文
   - サムネ：チャンネルは電話番号で確認済み（2026-11-25）。**本編には毎回** `videoThumbnailUrl` に横サムネ（media ブランチの jpg の raw URL）を付ける。
     ショートには付けない（ショートのサムネ機能が使えないチャンネルだと投稿ごと拒否されるため）。
     もし VIDEO_THUMBNAIL_NOT_APPLICABLE などで拒否されたら、サムネなしで予約し直し、ユーザーに「サムネは手動で設定してほしい」と伝える。
   - 公開時刻：本編とショートは同じ時刻。1日3枠：**03:00 / 06:00 / 11:00（Asia/Tokyo）**。制作は前日の 13:43 / 15:43 / 17:43 に始まり、翌日の枠に予約する
3. Metricool は予約時点で動画を自分の保存先にコピーする。予約後に `getScheduledPosts` で `media` が static.metricool.com になっているか確認。
4. 公開後、`getScheduledPosts` の status が `PUBLISHED` になり、`publicUrl` が出る。

## 終わったら
- `topics/queue.md` の状態を `投稿済み` にして、YouTube の URL を書く（main ブランチに push）。
- ユーザーに、タイトル・URL・固定コメント（YouTube Studio で手動で固定してもらう）を短く知らせる。サムネを自動で付けられなかった場合だけ、手動設定をお願いする。

## 注意
- ユーザーの個人情報（メールアドレスなど）を外部サービスに渡さない。
- 動画ファイルは main ブランチに入れない（リポジトリが大きくなるため）。
