# Narration scripts. Each line: text (subtitle / narration), optional card shown above the subtitle.
# card = (small label, big text)   reveal=True -> the hidden ??? flips to the answer with a hit.

MOVES = {
 'kaen': dict(
    title='かえんほうしゃ', accent=(255, 140, 50), label='推定温度', hidden='？？？？', unit='℃', answer='約1000℃',
    lines=[
      dict(text='もし現実で、かえんほうしゃを撃ったら？'),
      dict(text='炎の温度は、燃やすものでほぼ決まる。'),
      dict(text='ガソリンや油が空気中で燃えると、だいたい1000℃前後。', card=('油やガスの炎', '約1000℃')),
      dict(text='アルミ缶が溶けるのは660℃。一瞬でドロドロだ。', card=('アルミが溶ける温度', '660℃')),
      dict(text='でも鉄が溶けるのは1538℃。かえんほうしゃでは溶かせない。', card=('鉄が溶ける温度', '1538℃')),
      dict(text='鉄まで溶かすなら、酸素を吹き込む溶接バーナー級の、約3000℃が必要。', card=('溶接バーナー', '約3000℃')),
      dict(text='つまり、かえんほうしゃの推定温度は…', reveal_pre=True),
      dict(text='約1000℃！', reveal=True),
      dict(text='次に検証してほしい技は、コメントで教えて！'),
    ]),
 'bakuhatsu': dict(
    title='だいばくはつ', accent=(255, 125, 50), label='推定エネルギー', hidden='？？？', unit='kcal', answer='約10万kcal',
    lines=[
      dict(text='もし人間が、だいばくはつを使ったら？'),
      dict(text='体に蓄えたエネルギーを、全部一瞬で出すと仮定してみよう。'),
      dict(text='体重60kgの大人なら、体脂肪はざっと12kg。', card=('体脂肪（体重60kg）', '約12kg')),
      dict(text='脂肪は1gで約9キロカロリー。', card=('脂肪1gあたり', '約9kcal')),
      dict(text='ご飯に換算すると、なんと400杯以上。', card=('ご飯に換算', '400杯以上')),
      dict(text='これを一瞬で出すと、爆薬およそ100kg分のエネルギーになる。', card=('一瞬で放つと', '爆薬約100kg分')),
      dict(text='だいばくはつの推定エネルギーは…', reveal_pre=True),
      dict(text='約10万キロカロリー！', reveal=True),
      dict(text='ゲームで「ひんし」で済むのが不思議なレベルだ。'),
    ]),
 'fubuki': dict(
    title='ふぶき', accent=(150, 210, 255), label='到達気温', hidden='−？？？', unit='℃', answer='−196℃',
    lines=[
      dict(text='もし現実で、ふぶきを撃ったら？'),
      dict(text='相手を凍らせるには、どれくらい冷やせばいい？'),
      dict(text='地球で観測された最低気温は、南極のマイナス89.2℃。', card=('地球の最低気温（南極）', '−89.2℃')),
      dict(text='それでも、一瞬で凍りつくほどではない。'),
      dict(text='一瞬で凍らせるなら、液体窒素のマイナス196℃クラスが必要。', card=('液体窒素', '−196℃')),
      dict(text='バナナで釘が打てるほど、カチカチになる温度だ。'),
      dict(text='ふぶきの推定気温は…', reveal_pre=True),
      dict(text='マイナス196℃！', reveal=True),
      dict(text='もはや吹雪のレベルじゃない。'),
    ]),
 'hydro': dict(
    title='ハイドロポンプ', accent=(90, 190, 255), label='推定噴射圧', hidden='？？？', unit='気圧', answer='約6000気圧',
    lines=[
      dict(text='もし現実で、ハイドロポンプを撃ったら？'),
      dict(text='水の威力は、どれだけ強く押し出すか、つまり圧力で決まる。'),
      dict(text='家の水道は、だいたい2〜4気圧。', card=('家の水道', '2〜4気圧')),
      dict(text='消防車の放水でも、10気圧ほど。', card=('消防車の放水', '約10気圧')),
      dict(text='ところが工場のウォータージェットは、約6000気圧。', card=('ウォータージェット', '約6000気圧')),
      dict(text='研磨剤を混ぜれば、鉄板まで切れてしまう。'),
      dict(text='ハイドロポンプの推定噴射圧は…', reveal_pre=True),
      dict(text='約6000気圧！', reveal=True),
      dict(text='水を甘く見てはいけない。'),
    ]),
 'hakai': dict(
    title='はかいこうせん', accent=(255, 160, 60), label='使用者への反動', hidden='？？？', unit='', answer='リンゴ3個分',
    lines=[
      dict(text='もし現実で、はかいこうせんを撃ったら？'),
      dict(text='ゲームでは撃ったあと、反動で動けなくなる。'),
      dict(text='仮に、原発1基分、100万キロワットの光線だとしよう。', card=('光線のパワー（仮定）', '100万kW')),
      dict(text='光にも、物を押す力がある。その反動は…', reveal_pre=True),
      dict(text='約3.3ニュートン。リンゴ3個分の重さくらい！', reveal=True),
      dict(text='意外と軽い。でも1秒撃つだけで、約24万キロカロリーを使う。', card=('1秒で使うエネルギー', '約24万kcal')),
      dict(text='大人の食事の、約4か月分だ。', card=('大人の食事に換算', '約4か月分')),
      dict(text='動けなくなる本当の理由は、反動じゃなくて…エネルギー切れ！'),
    ]),
 'volt': dict(
    title='10まんボルト', accent=(255, 215, 70), label='瞬間電力', hidden='？？？', unit='世帯分', answer='約600万世帯分',
    lines=[
      dict(text='もし現実で、10まんボルトを撃ったら？'),
      dict(text='実は、電圧だけでは威力は決まらない。'),
      dict(text='冬のドアノブの静電気も、1万ボルトを超えることがある。', card=('冬の静電気', '1万V超え')),
      dict(text='それでも平気なのは、電流がほとんど流れないから。'),
      dict(text='そこで、電流を雷なみの3万アンペアと仮定すると…', card=('電流（雷なみと仮定）', '3万A')),
      dict(text='瞬間のパワーは30億ワット。家庭の電気にすると…', reveal_pre=True),
      dict(text='約600万世帯分！', reveal=True),
      dict(text='ただし流れるのは一瞬。エネルギーにすると、家1軒の約2時間分だ。', card=('エネルギーにすると', '家1軒の約2時間分')),
    ]),
}

ORDER = ['kaen', 'bakuhatsu', 'fubuki', 'hydro', 'hakai', 'volt']
FILES = {'kaen': '1_kaenhousha', 'bakuhatsu': '2_daibakuhatsu', 'fubuki': '3_fubuki',
         'hydro': '4_hydropump', 'hakai': '5_hakaikousen', 'volt': '6_10manvolt'}
