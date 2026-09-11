import json
import hashlib
from pathlib import Path
from collections import Counter

root = Path(__file__).resolve().parents[1] / 'app/src/main/assets/ui'
raw = (root / 'catalog.json').read_bytes()
release=Path(__file__).resolve().parents[1]/'data/release_061.json'
expected=json.loads(release.read_text(encoding='utf-8'))['catalog_sha256'] if release.exists() else '298a39583194276c8e1821ba22bffb758490453506c6b46c466c51de081c6b67'
assert hashlib.sha256(raw).hexdigest()==expected
places = {p['id']: p for p in json.loads(raw)['places'] if p['mapReady']}
data = json.loads((root / 'collections.json').read_text(encoding='utf-8'))
assert len({c['id'] for c in data['collections']}) == len(data['collections'])
for c in data['collections'] + data['proposals']:
    assert c['placeIds'] and len(c['placeIds']) == len(set(c['placeIds']))
    assert all(id in places and places[id]['country'] == c['country'] for id in c['placeIds'])
for country in ('PL', 'DE'):
    themes = Counter(id for c in data['collections'] if c['kind'] == 'theme' and c['country'] == country for id in c['placeIds'])
    assert set(themes) == {id for id,p in places.items() if p['country'] == country}
    assert set(themes.values()) == {1}
    peaks = Counter(id for c in data['collections'] if c['kind'] == 'peaks' and c['country'] == country for id in c['placeIds'])
    assert set(peaks) == {id for id,p in places.items() if p['country'] == country and p['category'] == 'peak'}
    assert set(peaks.values()) == {1}
for p in data['proposals']:
    assert len(p['placeIds']) >= 2 and p['sources'] and set(p['anchorIds']) <= set(p['placeIds'])
assert [places[id]['name'] for id in data['proposals'][0]['placeIds']] == ['Malinów','Jaskinia Malinowska','Małe Skrzyczne','Skrzyczne']
print('PASS: frozen catalog, complete category/peak coverage, unique same-country IDs, proposal order and sources')
