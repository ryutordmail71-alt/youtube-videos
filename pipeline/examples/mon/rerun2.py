import json, nscn as S
st = json.load(open('/home/claude/mon/scene_static.json'))
st['outro'] = S.scene_outro()
json.dump(st, open('/home/claude/mon/scene_static.json', 'w')); print('done rerun2')
