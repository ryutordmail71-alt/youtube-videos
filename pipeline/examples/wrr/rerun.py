import json, sys, wscn as S
st = json.load(open('/home/claude/wrr/scene_static.json'))
st['title'] = S.scene_title(); st['data'] = S.scene_data(); st['outro'] = S.scene_outro()
json.dump(st, open('/home/claude/wrr/scene_static.json', 'w')); print('done rerun')
