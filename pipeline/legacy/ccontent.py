A, B, C3 = 'どんな天体  WHAT', 'ヤバいポイント  INSANE', '豆知識  TRIVIA'
def it(t, en, place, place_en, kind, kind_en, year, year_en, s):
    return dict(t=t, en=en, place=place, place_en=place_en, kind=kind, kind_en=kind_en, year=year, year_en=year_en,
                segs=[(A, '', s[0], s[1], s[2]), (B, '', s[3], s[4], s[5]), (C3, '', s[6], s[7], s[8])])
K = [
it('金星', 'Venus', '地球のとなりの惑星', "Earth's next-door neighbor", '惑星', 'Planet', '地表は約465℃・90気圧以上', 'Surface: ~465 °C, over 90 atmospheres', [
 '地球の「双子」と呼ばれる惑星', "Called Earth's twin",
 '第十位は、金星です。大きさが、地球とほぼ同じことから、地球の双子とも呼ばれる、すぐとなりの惑星です。',
 '鉛も溶ける、灼熱の世界', 'Hot enough to melt lead',
 'ところが、その地表の温度は、およそ四百六十五度。鉛も溶けてしまうほどの、灼熱の世界です。分厚い二酸化炭素の大気が、熱を閉じ込めているのです。',
 '空には、硫酸の雲', 'Clouds made of sulfuric acid',
 '空をおおう雲は、硫酸でできていて、地表の気圧は、地球の九十倍以上。深い海の底のような圧力です。かつて着陸した探査機も、わずか数時間で、壊れてしまいました。']),
it('TrES-2b', 'TrES-2b', '地球から約750光年', 'About 750 light-years away', '惑星', 'Planet', '光をほとんど反射しない', 'Reflects almost no light', [
 '宇宙で最も暗い惑星の一つ', 'One of the darkest planets known',
 '第九位は、TrES-2bです。地球から、およそ七百五十光年離れた場所にある、木星ほどの大きさの惑星です。',
 '石炭よりも、黒い', 'Blacker than coal',
 'この惑星は、届いた光の、一パーセントも反射しないと考えられています。黒い絵の具や、石炭よりも暗い、真っ黒な惑星なのです。',
 'それでも、かすかに赤く光る', 'Yet it faintly glows red',
 'ただし、恒星のすぐ近くを回っているため、表面は、千度を超える高温です。そのため、炭火のように、ぼんやりと赤く光っているとも言われています。']),
it('グリーゼ436b', 'Gliese 436 b', '地球から約33光年', 'About 33 light-years away', '惑星', 'Planet', '400℃を超える「燃える氷」？', '"Burning ice" at over 400 °C?', [
 '熱いのに、凍っている？', 'Hot, and yet frozen?',
 '第八位は、グリーゼ四三六bです。地球から、およそ三十三光年の場所にある、海王星ほどの大きさの惑星です。',
 '400℃を超える氷', 'Ice at over 400 degrees',
 'この惑星の表面温度は、四百度を超えるほど。それなのに、そこには、氷があるかもしれないと考えられました。とてつもない重力で押し固められて、熱くても溶けない、特別な氷です。',
 '彗星のような、長い尾', 'A long tail like a comet',
 'さらに、この惑星からは、大量の水素が逃げ出していて、まるで彗星のような、巨大な尾を引いていることも、観測されています。']),
it('かに座55番星e', '55 Cancri e', '地球から約41光年', 'About 41 light-years away', '惑星', 'Planet', 'ダイヤモンドの惑星？', 'A diamond planet?', [
 '地球の約2倍の大きさの惑星', 'A planet about twice Earth\'s size',
 '第七位は、かに座五十五番星eです。地球の、およそ二倍の大きさで、地球から、およそ四十一光年の場所にあります。',
 '中身は、ダイヤモンド？', 'Made of diamond inside?',
 'かつて、この惑星には、炭素がとても多く、その一部は、ダイヤモンドになっているかもしれない、と発表され、ダイヤモンドの惑星として、話題になりました。',
 '表面は、溶岩の海', 'A surface of lava oceans',
 '最近の観測では、ダイヤモンド説には、疑問の声もあります。ただ、昼側の温度は、二千度を超えるとも言われ、表面は、溶けた岩の海におおわれていると考えられています。ここまでで、四つ。ここから、さらにヤバい天体が登場します。']),
it('HD 189733b', 'HD 189733 b', '地球から約64光年', 'About 64 light-years away', '惑星', 'Planet', 'ガラスの雨が、横から降る', 'It rains glass, sideways', [
 '地球のような、青い惑星', 'A planet as blue as Earth',
 '第六位は、HD 189733bです。宇宙から見ると、地球のように、美しい青色をしています。',
 'ガラスの雨が、横から降る', 'Glass rain falling sideways',
 'ところが、その青色の正体は、海ではありません。大気の中には、ガラスの成分が含まれていて、それが、雨のように降っていると考えられています。しかも、秒速二キロほどの猛烈な風で、雨は、真横に吹き付けるのです。',
 '世界一、行きたくない青い星', 'The blue planet nobody wants to visit',
 '温度は、千度を超えるとも言われています。見た目は美しくても、ガラスの雨が、真横から降り注ぐ世界。宇宙で一番、行きたくない星の一つかもしれません。']),
it('ベテルギウス', 'Betelgeuse', 'オリオン座の肩・地球から約550〜700光年', "Orion's shoulder, ~550-700 light-years away", '恒星', 'Star', 'いつ爆発してもおかしくない', 'Could explode at any time (astronomically)', [
 '冬の夜空で見える、赤い星', 'The red star of the winter sky',
 '第五位は、ベテルギウスです。オリオン座の肩に輝く、赤い星で、日本からも、冬の夜空で、肉眼で見ることができます。',
 '太陽系に置くと、木星の近くまで', 'In our solar system, it would reach toward Jupiter',
 'ベテルギウスは、赤色超巨星と呼ばれる、巨大な星です。もし、太陽の位置に置いたら、その表面は、火星の軌道を越えて、木星の近くにまで達するとも言われています。',
 'いつ超新星爆発を起こしても、おかしくない', 'A supernova could happen any time',
 'この星は、寿命の終わりに近づいていて、十万年以内には、超新星爆発を起こすと考えられています。爆発すれば、昼間でも見えるほど、明るく輝くかもしれません。ここまでで、六つ。残りは四つです。']),
it('うしかい座ボイド', 'Boötes Void', '地球から約7億光年', 'About 700 million light-years away', '宇宙の大空洞', 'Cosmic void', '直径約3億3000万光年の「何もない」空間', '~330 million light-years of near emptiness', [
 '宇宙に空いた、巨大な穴', 'A giant hole in the universe',
 '第四位は、うしかい座ボイドです。これは、星ではありません。宇宙の中に、ぽっかりと空いた、巨大な空洞です。',
 '直径、約3億3000万光年', 'About 330 million light-years across',
 'その大きさは、直径、およそ三億三千万光年。普通なら、この広さには、何千もの銀河があってもおかしくありません。ところが、ここでは、ごくわずかな銀河しか、見つかっていないのです。',
 'もし、ここに住んでいたら', 'If we lived in there',
 'もし、私たちの銀河が、この空洞の真ん中にあったら、夜空に、ほかの銀河が見えることは、ほとんどなく、天文学の発展も、ずっと遅れていた、とも言われています。']),
it('マグネター', 'Magnetar', '超強力な磁場を持つ中性子星', 'A neutron star with an extreme magnetic field', '中性子星', 'Neutron star', '地球の磁場の、約1000兆倍', 'About 1,000 trillion times Earth\'s field', [
 '宇宙最強の磁石', 'The strongest magnets in the universe',
 '第三位は、マグネターです。超新星爆発の後に残る、中性子星の中でも、とてつもなく強い磁場を持つものです。',
 '近づくだけで、命が危ない', 'Coming close would be deadly',
 'その磁場の強さは、地球の、およそ千兆倍にもなると言われています。千キロ以内に近づくだけで、体を作る原子が、磁場で引き伸ばされ、生き物は、生きていられないとも言われています。',
 '5万光年先から、地球に届いた衝撃', 'A blast felt on Earth from 50,000 light-years away',
 '二千四年には、およそ五万光年も離れたマグネターが、巨大な爆発を起こし、その放射が、地球の上空の大気にまで、影響を与えたことが、観測されました。ここまでで、八つ。残りは、いよいよ二つです。']),
it('GRB 221009A', 'GRB 221009A', '地球から約24億光年', 'About 2.4 billion light-years away', 'ガンマ線バースト', 'Gamma-ray burst', '観測史上、最も明るい爆発', 'The brightest explosion ever recorded', [
 '宇宙で最も激しい爆発', 'The most violent explosions in the universe',
 '第二位は、ガンマ線バーストです。巨大な星が、一生の最後に崩れ落ちるときなどに起きる、宇宙で最も激しい爆発の一つです。',
 '史上最も明るい「BOAT」', '"BOAT": the brightest of all time',
 '二千二十二年十月に観測された、GRB 二二一〇〇九Aは、およそ二十四億光年も離れていたにもかかわらず、観測史上、最も明るいガンマ線バーストでした。研究者たちは、これを、史上最も明るいという意味の英語の頭文字から、BOATと呼びました。',
 '地球の大気まで、揺らした', 'It even shook Earth\'s upper atmosphere',
 'この爆発の光は、地球の上空にある、電離層にまで、影響を与えたと報告されています。もし、もっと近くで起きていたら、地球の生き物にとって、大きな脅威になっていたかもしれません。']),
it('TON 618', 'TON 618', '地球から約108億光年', 'About 10.8 billion light-years away', '超大質量ブラックホール', 'Supermassive black hole', '太陽の約660億倍の質量とも', 'Possibly ~66 billion solar masses', [
 '知られている中で、最も重いブラックホールの一つ', 'One of the most massive black holes known',
 'そして、第一位は、TON 六一八です。およそ百八億光年の彼方にある、クエーサーと呼ばれる天体で、その中心には、とてつもなく巨大な、ブラックホールがあります。',
 '太陽の、約660億倍の重さ', 'About 66 billion times the mass of the Sun',
 'その重さは、太陽の、およそ六百六十億倍とも言われています。これは、私たちの天の川銀河の中心にある、ブラックホールの、一万倍以上です。',
 '太陽系が、まるごと入る大きさ', 'Big enough to swallow the whole solar system',
 'この重さから計算すると、ブラックホールの境目、事象の地平面の大きさは、海王星の軌道よりも、はるかに大きくなります。太陽系が、まるごとのみ込まれてしまうほどの、怪物なのです。宇宙には、私たちの想像を、はるかに超える天体が、まだまだ眠っています。']),
]
