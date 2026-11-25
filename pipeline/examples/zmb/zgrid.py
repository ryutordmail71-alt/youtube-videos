"""日本の人口グリッド（2020年国勢調査の都道府県人口 × Natural Earth の地図・都市）"""
import json, math, numpy as np
from PIL import Image, ImageDraw
POP = [5224614,1237984,1210534,2301996,959502,1068027,1833152,2867009,1933146,1939110,7344765,6284480,14047594,9237337,2201272,1034814,1132526,766863,809974,2048011,1978742,3633202,7542415,1770254,1413610,2578087,8837685,5465002,1324473,922584,553407,671126,1888432,2799702,1342059,719559,950244,1334841,691527,5135214,811442,1312317,1738301,1123852,1069576,1588256,1467480]
LON0, LON1, LAT0, LAT1 = 122.8, 146.0, 24.0, 45.7
DLAT = 0.05; DLON = 0.0625
NX = int((LON1 - LON0) / DLON); NY = int((LAT1 - LAT0) / DLAT)
def ij(lon, lat): return (lon - LON0) / DLON, (LAT1 - lat) / DLAT
def build():
    d = json.load(open('/home/claude/dl/jp_pref.geojson'))
    code = np.zeros((NY, NX), np.int16); im = Image.new('I', (NX * 4, NY * 4), 0); dr = ImageDraw.Draw(im)
    for f in d['features']:
        c = int(f['properties']['iso_3166_2'][3:]); g = f['geometry']
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for P in polys:
            ring = [(ij(x, y)[0] * 4, ij(x, y)[1] * 4) for x, y in P[0]]
            if len(ring) > 2: dr.polygon(ring, fill=c)
    a = np.array(im).reshape(NY, 4, NX, 4)
    # 4x4 の中の最頻値（0 以外を優先）
    flat = a.transpose(0, 2, 1, 3).reshape(NY, NX, 16)
    for k in range(1, 48):
        cnt = (flat == k).sum(2); m = cnt >= 4
        code[m & (cnt > (flat == code[..., None]).sum(2) * (code > 0))] = k
    lat = LAT1 - (np.arange(NY) + 0.5) * DLAT
    cell_km2 = (DLAT * 111.0) * (DLON * 111.0 * np.cos(np.radians(lat)))[:, None] * np.ones((1, NX))
    pp = json.load(open('/home/claude/dl/pp.geojson'))
    cities = [(f['properties']['longitude'], f['properties']['latitude'], f['properties']['pop_max']) for f in pp['features'] if f['properties'].get('adm0_a3') == 'JPN']
    Y, X = np.mgrid[0:NY, 0:NX]; kern = np.zeros((NY, NX))
    for lo, la, p in cities:
        x, y = ij(lo, la); kern += math.sqrt(p) * np.exp(-((X - x) ** 2 + (Y - y) ** 2) / (2 * 2.2 ** 2))
    pop = np.zeros((NY, NX))
    for k in range(1, 48):
        m = code == k
        if not m.any(): print('missing', k); continue
        u = cell_km2 * m; u = u / u.sum(); w = kern * m
        w = w / w.sum() if w.sum() > 0 else u
        if k == 13:   # 東京都：島しょ部（人口は約2万4千人）を本土と分ける
            isl = m & (np.arange(NY)[:, None] * np.ones((1, NX)) > (LAT1 - 35.45) / DLAT)
            mm = m & ~isl; u = cell_km2 * mm; u = u / u.sum(); w = kern * mm; w = w / w.sum()
            pop[mm] = ((POP[k - 1] - 24000) * (0.5 * u + 0.5 * w))[mm]; ui = cell_km2 * isl; pop[isl] = (24000 * ui / ui.sum())[isl]; continue
        pop[m] = (POP[k - 1] * (0.5 * u + 0.5 * w))[m]
    np.savez_compressed('grid.npz', code=code, pop=pop, km2=cell_km2)
    print(NX, NY, (code > 0).sum(), pop.sum())
if __name__ == '__main__': build()
