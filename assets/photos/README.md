# 先に集めておいた写真（Openverse 経由・自由ライセンス）
- `<slug>/*.jpg`：使ってよいと目で確認した写真（1280px以下）。`credits.json` のクレジットを説明欄に全部入れる。
- `note` が「イメージ」の写真は、画面にも小さく「イメージ」と出す。
- 候補の元画像（cand/）は git に入れない。

## どのネタの写真か
- polybius ＝ 都市伝説：ポリビアス
- bielefeld ＝ 都市伝説：ビーレフェルトは存在しない
- maboroshi-eki ＝ 都市伝説：東京の地下鉄の「幻の駅」
- skyfish ＝ 都市伝説：スカイフィッシュ
- black-eyed-kids ＝ 都市伝説：ブラックアイド・キッズ（2026-11-28 制作時に Wikimedia Commons の API から取得。Openverse は4時間待ちと言われて使えなかった。Commons の API 検索〔commons.wikimedia.org/w/api.php、generator=search＋imageinfo の iiurlwidth=1280〕と thumburl の取得はシェルから通った。429 が出たら数十秒あけて再試行。作業用のスクリプトは pipeline/examples/bek/commons.py・cget.py）
- skyfish の写真は Openverse が混雑で使えなかったため NASA（パブリックドメイン）から取った（2026-11-28）
- tokyo-chika ＝ 都市伝説：東京の地下に眠る秘密の通路（2026-11-29 制作時に Wikimedia Commons の API から取得。制作コードは pipeline/examples/tkc。コードは /home/claude/tkc にコピーして ph/ に写真を置く前提）
