import json, ascn as S
G='/home/claude/air'; res=json.load(open(f'{G}/scene_static.json'))
res['reveal']=S.scene_reveal(); res['sweep']=S.scene_sweep()
res['res2']=S.scene_card('res2', 'RESULT  2回戦', [('約2億台が 使えなくなるまで', 'たった約28時間', S.AIR, '一時間ごと'), ('止まるもの', '電子マネー・地図・連絡', S.PALE, '電子マネー'),
    ('人類の反撃', '線を抜いて電源を切る', S.GREEN, 'ネットの線')], f'{G}/c_res2.mp4', big='AIの勝ち', bigcol=S.AIR, sub='※ウイルスも広がる速さ（1時間で2倍）も架空。台数は仮定')
json.dump(res, open(f'{G}/scene_static.json','w')); print('ok')
