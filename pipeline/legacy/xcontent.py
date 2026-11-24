A, B, C3 = 'どんな災害  WHAT', 'ヤバいポイント  INSANE', '豆知識  TRIVIA'
def it(t, en, place, place_en, kind, kind_en, year, year_en, s):
    return dict(t=t, en=en, place=place, place_en=place_en, kind=kind, kind_en=kind_en, year=year, year_en=year_en,
                segs=[(A, '', s[0], s[1], s[2]), (B, '', s[3], s[4], s[5]), (C3, '', s[6], s[7], s[8])])
K = [
it('タンボラ山の大噴火', 'Eruption of Mount Tambora', 'インドネシア・スンバワ島', 'Sumbawa, Indonesia', '火山噴火', 'Volcanic eruption', '1815年', '1815', [
 '記録に残る、史上最大級の噴火', 'One of the largest eruptions in recorded history',
 '第十位は、タンボラ山の大噴火です。千八百十五年、インドネシアのタンボラ山が、大爆発を起こしました。記録に残る中では、史上最大級の噴火です。',
 '「夏のない年」がやってきた', 'It brought the Year Without a Summer',
 '噴き上げられた火山灰などが、地球全体の空をおおい、太陽の光をさえぎりました。その翌年、ヨーロッパや北アメリカでは、夏なのに雪が降るなど、異常な寒さとなり、夏のない年と呼ばれました。',
 '名作小説が、生まれるきっかけに', 'It helped give birth to a classic novel',
 'この寒い夏、スイスの湖のほとりで、雨に降りこめられた作家たちが、怪談を作り合いました。そこで生まれたのが、小説、フランケンシュタインだと言われています。']),
it('ツングースカ大爆発', 'The Tunguska Event', 'ロシア・シベリア', 'Siberia, Russia', '天体の爆発', 'Cosmic airburst', '1908年', '1908', [
 'シベリアの森で、謎の大爆発', 'A mysterious explosion over a Siberian forest',
 '第九位は、ツングースカ大爆発です。千九百八年、ロシアのシベリアの上空で、とてつもない大爆発が起きました。',
 '約8000万本の木が、なぎ倒された', 'About 80 million trees flattened',
 'その爆風で、東京都とほぼ同じ広さの森が、なぎ倒され、倒れた木は、およそ八千万本にもなると言われています。それなのに、地面には、隕石が落ちたあとの、クレーターが見つかりませんでした。',
 '正体は、空中で爆発した天体？', 'A space rock that exploded in midair?',
 '今では、小さな小惑星か、彗星のかけらが、地面に落ちる前に、空中で爆発したという説が、有力です。もし、大都市の上空で起きていたら、街は、壊滅していたかもしれません。']),
it('ミズーラ大洪水', 'The Missoula Floods', 'アメリカ北西部', 'Northwestern United States', '大洪水', 'Megaflood', '約1万5000年前ごろ', 'Around 15,000 years ago', [
 '氷のダムが、決壊した', 'An ice dam burst',
 '第八位は、ミズーラ大洪水です。氷河時代の終わりごろ、アメリカ北西部では、巨大な氷河が、川をせき止め、大きな湖を作っていました。',
 '一気に流れ出た、湖の水', 'An entire lake emptied in a rush',
 'ところが、この氷のダムが決壊すると、湖の水が、一気に流れ出しました。その水の量は、世界中の川を合わせた流れの、何倍にもなったと考えられています。しかも、こうした大洪水は、何十回も、くり返されたとみられています。',
 '水のない、巨大な滝', 'A giant waterfall with no water',
 'その爆発的な流れが、大地を削って作った、巨大な滝の跡が、今も残っています。ドライフォールズと呼ばれる、幅およそ五キロの崖で、かつては、ナイアガラの滝をはるかに超える、大瀑布だったのです。']),
it('地中海が、干上がった', 'The Mediterranean dried up', 'ヨーロッパとアフリカの間', 'Between Europe and Africa', '海の消失', 'A vanishing sea', '約600万年前', 'About 6 million years ago', [
 '海が、まるごと干上がる', 'An entire sea dries out',
 '第七位は、地中海が干上がった事件です。およそ六百万年前、大西洋と地中海をつなぐ海峡が、地面の動きなどで、閉じてしまいました。',
 '深い谷と、塩の大地', 'Deep canyons and plains of salt',
 '水の入らなくなった地中海は、蒸発が進み、大部分が、干上がってしまったと考えられています。海の底だった場所には、分厚い塩の層が、積み重なりました。',
 'そして、史上最大の洪水へ', 'And then, the greatest flood of all',
 'その後、およそ五百三十万年前、ジブラルタル海峡から、大西洋の水が、一気に流れ込み、地中海は、再び海に戻ったと考えられています。一説では、わずか数年ほどで、満たされたとも言われています。ここまでで、四つ。この後は、人類を絶滅寸前に追い込んだとも言われる、大噴火が登場します。']),
it('トバ火山の超巨大噴火', 'The Toba supereruption', 'インドネシア・スマトラ島', 'Sumatra, Indonesia', '超巨大噴火', 'Supereruption', '約7万4000年前', 'About 74,000 years ago', [
 '地球史に残る、超巨大噴火', 'One of the largest eruptions in Earth\'s history',
 '第六位は、トバ火山の噴火です。およそ七万四千年前、インドネシアのスマトラ島で、超巨大噴火が起きました。過去、数百万年の中でも、最大級とされる噴火です。',
 '人類を、絶滅寸前に追い込んだ？', 'Did it push humans to the brink?',
 'この噴火で、地球の気温が下がり、私たちの祖先は、数千人ほどにまで減ってしまった、という説があります。ただし、最近の研究では、人類への影響は、それほど大きくなかった、という見方もあり、今も、議論が続いています。',
 '世界最大級の、カルデラ湖', 'One of the largest crater lakes on Earth',
 '噴火の跡には、長さおよそ百キロにもなる、巨大なくぼ地ができ、そこに水がたまって、トバ湖が生まれました。世界最大級の、カルデラ湖です。ここまでで、五つ。残りは五つです。']),
it('大酸化イベント', 'The Great Oxidation Event', '地球全体', 'The whole planet', '大気の大変化', 'Atmospheric upheaval', '約24億年前', 'About 2.4 billion years ago', [
 '酸素が、生き物を追いつめた', 'When oxygen became a killer',
 '第五位は、大酸化イベントです。およそ二十四億年前、地球の空気に、急に、酸素が増え始めました。原因は、光合成をする、小さな生き物、シアノバクテリアです。',
 '酸素は、もともと「毒」だった', 'Oxygen was originally poison',
 '当時、地球に暮らしていた生き物の多くは、酸素のない世界で生きていました。彼らにとって、酸素は、体を傷つける、毒だったのです。そのため、多くの生き物が、追いつめられたと考えられています。',
 '今の私たちに、つながる大事件', 'The event that made us possible',
 'でも、この酸素があったからこそ、やがて、酸素を使って、大きなエネルギーを生み出す、生き物が現れました。私たち人間も、その子孫なのです。']),
it('恐竜を滅ぼした巨大隕石', 'The asteroid that killed the dinosaurs', 'メキシコ・ユカタン半島', 'Yucatán Peninsula, Mexico', '天体衝突', 'Asteroid impact', '約6600万年前', 'About 66 million years ago', [
 '直径約10キロの、巨大隕石', 'An asteroid about 10 km wide',
 '第四位は、恐竜を滅ぼした、巨大隕石です。およそ六千六百万年前、直径およそ十キロの小惑星が、今のメキシコ、ユカタン半島のあたりに、衝突しました。',
 '生き物の、約4分の3が絶滅', 'About three-quarters of species wiped out',
 '衝突の衝撃で、巨大な津波や、山火事が起き、空は、舞い上がったちりで、おおわれました。太陽の光が届かず、地球は、急激に冷え込み、恐竜をはじめ、生き物の種の、およそ四分の三が、絶滅したと考えられています。',
 '今も残る、直径約180キロのクレーター', 'A crater about 180 km wide still remains',
 'その跡が、チクシュルーブ・クレーターです。直径は、およそ百八十キロ。今は、地下に埋もれていますが、研究によって、その姿が、明らかになっています。ここまでで、七つ。でも、これよりも、さらにヤバい大災害が、まだ三つ残っています。']),
it('史上最悪の大量絶滅', 'The worst mass extinction ever', 'シベリアの大噴火が原因？', 'Possibly triggered by vast Siberian eruptions', '大量絶滅', 'Mass extinction', '約2億5200万年前', 'About 252 million years ago', [
 '「大絶滅」と呼ばれる事件', 'Known as the Great Dying',
 '第三位は、ペルム紀末の大量絶滅です。およそ二億五千二百万年前に起きた、地球の歴史上、最悪とされる大量絶滅で、大絶滅、とも呼ばれています。',
 '海の生き物の、8割以上が消えた', 'Over 80% of marine species vanished',
 'このとき、海の生き物の種の、八割以上が、絶滅したと考えられています。恐竜を滅ぼした隕石よりも、さらに、多くの生き物が、姿を消したのです。',
 '原因は、超巨大な火山活動？', 'Caused by gigantic volcanism?',
 '有力な原因と考えられているのが、今のシベリアで、長い期間続いた、超巨大な火山活動です。大量の二酸化炭素などが放出され、地球は、急激に温暖化し、海からは、酸素が失われていったとみられています。']),
it('スノーボールアース', 'Snowball Earth', '地球全体が、氷におおわれた？', 'The whole planet covered in ice?', '全球凍結', 'Global glaciation', '約7億年前ごろ', 'Around 700 million years ago', [
 '地球が、まるごと凍った', 'The entire Earth froze over',
 '第二位は、スノーボールアースです。およそ七億年前ごろ、地球は、赤道付近まで、氷におおわれていたと考えられています。地球全体が、まるで、巨大な雪の玉のようになっていたのです。',
 '何百万年も、凍りついた世界', 'A frozen world for millions of years',
 'しかも、この凍りついた状態は、何百万年も続いたとみられています。海の表面も、厚い氷に閉ざされ、生き物たちは、わずかに残った、氷の少ない場所などで、生き延びたと考えられています。',
 '火山が、地球を救った？', 'Did volcanoes save the planet?',
 'この氷の世界を終わらせたのは、火山だと考えられています。火山から出た二酸化炭素が、長い年月をかけて、空気中にたまり、地球を、温め直したのです。そして、その後、さまざまな生き物が、一気に、増えていきました。ここまでで、九つ。いよいよ、第一位です。']),
it('ジャイアント・インパクト', 'The Giant Impact', '原始の地球に、火星ほどの天体が衝突', 'A Mars-sized body hits the young Earth', '天体衝突', 'Planetary collision', '約45億年前', 'About 4.5 billion years ago', [
 '地球に、別の惑星がぶつかった', 'Another planet slammed into Earth',
 'そして、第一位は、ジャイアント・インパクトです。およそ四十五億年前、生まれたばかりの地球に、火星ほどの大きさの天体が、衝突したと考えられています。',
 '地球の表面が、すべて溶けた', "Earth's entire surface melted",
 'この衝突の熱で、地球の表面は、どろどろに溶けて、マグマの海におおわれたとみられています。恐竜の隕石とは、比べものにならない、地球そのものを、作り変えてしまうほどの、大衝突です。',
 'そして、月が生まれた', 'And so the Moon was born',
 'このとき、宇宙に飛び散った、大量のかけらが集まって、できたのが、月だと考えられています。夜空に浮かぶ月は、地球史上、最大の大災害が残した、贈り物なのかもしれません。']),
]
