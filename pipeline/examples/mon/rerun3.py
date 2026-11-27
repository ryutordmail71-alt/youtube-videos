import json, nscn as S
from arnd import PALE, GOLD, GREEN, CYAN
st = json.load(open('/home/claude/mon/scene_static.json'))
st['res1'] = S.scene_card('res1', 'RESULT  1回戦', [('満月の見かけの大きさ（いま）', '約0.5度', PALE, '満月の'), ('半分の距離では', '約1度（幅2倍）', GOLD, '半分の距離'),
                 ('見かけの面積・明るさ', '約4倍', CYAN, '幅が二倍')], '/home/claude/mon/c_res1.mp4', big='うわさ1は ウソ', bigcol=GREEN, icon=S.icon_coin,
                 sub='※見かけの大きさ（視直径）は 約0.52度。腕をのばして持った五円玉の穴（約0.9度）に入る大きさ')
json.dump(st, open('/home/claude/mon/scene_static.json', 'w')); print('done rerun3')
