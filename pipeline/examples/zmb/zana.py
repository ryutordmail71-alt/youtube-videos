import numpy as np, sys
from zgrid import POP
tag = sys.argv[1] if len(sys.argv) > 1 else ''
d = np.load(f'sim{tag}.npz'); st = d['stats']; ti = d['t_inf']; S = d['S']
g = np.load('grid.npz'); C = g['code']; P0 = g['pop']
N = P0.sum(); main = P0[C != 47].sum()
for thr in [0.5, 0.1, 0.01]:
    k = np.argmax(st[:, 1] - N * 0 < 0) 
hrs = st[:, 0]; hum = st[:, 1]
for f in [0.9, 0.5, 0.2, 0.1, 0.05, 0.02, 0.012, 0.01]:
    i = np.argmax(hum < N * f); print(f'humans<{f*100:.1f}%: day {hrs[i]/24:.1f}' if hum[i] < N * f else f'humans<{f*100}%: never ({hum[-1]/N*100:.2f}% left)')
names = '北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄'.split()
# 都道府県の「到達日」（最初にゾンビが入った日）と、人間が1%を切った日（最後の状態から推定できないので t_inf の最大で近似）
for k in range(1, 48):
    m = C == k; t = ti[m]
    first = t.min() / 24; cov = np.isfinite(t).mean(); last = t[np.isfinite(t)].max() / 24 if np.isfinite(t).any() else np.inf
    print(f'{names[k-1]:4s} 到達 {first:6.1f}日  全域 {last:6.1f}日  到達率 {cov*100:5.1f}%  残り人間 {S[m].sum()/P0[m].sum()*100:5.1f}%')
