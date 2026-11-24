import sys
sys.path.insert(0, '/home/claude/video')
from scripts import MOVES, ORDER, FILES
from compose import timeline

def fmt(x):
    return f'{int(x // 60)}:{x % 60:04.1f}'

out = ['ナレーション原稿（6本）', '',
       '使い方：各行をCapCutの「テキスト読み上げ」やVOICEVOXに貼り付けて音声を作り、',
       '動画の字幕が出るタイミングに合わせて置いてください。時間は字幕が出始める位置です。',
       '同じ名前の .srt ファイルを読み込むと、字幕の位置に合わせて作業できます。', '']
for k in ORDER:
    M = MOVES[k]; tl, dur = timeline(M['lines'])
    out.append('=' * 40)
    out.append(f'{FILES[k]}  「{M["title"]}」  約{dur:.0f}秒')
    out.append('=' * 40)
    for (a, b), ln in zip(tl, M['lines']):
        out.append(f'[{fmt(a)}] {ln["text"].replace("|", "")}')
    out.append('')
open('/home/claude/video/out/narration_script.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
