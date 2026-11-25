import zsim
C = [(136.88, 35.17, 'Nagoya'), (135.50, 34.70, 'Osaka'), (140.88, 38.26, 'Sendai'), (130.42, 33.59, 'Fukuoka'), (132.46, 34.40, 'Hiroshima'), (139.04, 37.91, 'Niigata'), (136.65, 36.56, 'Kanazawa')]
seeds = [(139.70, 35.66, 0)] + [(lo, la, 12) for lo, la, _ in C]
zsim.run(300, seeds=seeds, tag='_train')
