import json, nscn as S
st = json.load(open('/home/claude/mon/scene_static.json'))
st['data'] = S.scene_data(); st['rule'] = S.scene_rule(); st['sweep'] = S.scene_sweep()
json.dump(st, open('/home/claude/mon/scene_static.json', 'w')); print('done rerun')
