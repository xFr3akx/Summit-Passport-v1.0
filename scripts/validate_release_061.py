"""Verify the release delta, immutable baseline identities and every new coordinate source."""
from pathlib import Path
import json,hashlib,math,collections,unicodedata,re
r=Path(__file__).resolve().parents[1];u=r/'app/src/main/assets/ui'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
baseline=read(r/'data/catalog_runtime_060.json');current=read(u/'catalog.json');delta=read(r/'data/germany_expansion_061.json');report=read(r/'data/release_061.json')
assert hashlib.sha256((r/'data/catalog_runtime_060.json').read_bytes()).hexdigest()=='298a39583194276c8e1821ba22bffb758490453506c6b46c466c51de081c6b67'
old={p['id']:p for p in baseline['places']};new={p['id']:p for p in current['places']};assert len(new)==len(current['places'])==len(old)+386
assert all(new[id]==point for id,point in old.items()),'Existing places, including all Polish records, must remain unchanged'
assert len(delta['records'])==386;assert {p['place']['id'] for p in delta['records']}==set(new)-set(old)
def dist(a,b):return math.hypot((a[0]-b[0])*111195,(a[1]-b[1])*111195*math.cos(math.radians((a[0]+b[0])/2)))
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s.lower().replace('ß','ss').replace('ł','l')).encode('ascii','ignore').decode())
seen_osm=set();seen_gn=set();published=[p for p in old.values() if p['country']=='DE' and p['mapReady']];oldnames={norm(p['name']) for p in old.values() if p['country']=='DE'}
for row in delta['records']:
 p=row['place'];gn=row['geonames'];osm=row['osm'];props=osm['properties'];assert p==new[p['id']] and p['country']=='DE' and p['mapReady']
 assert p['source'] not in seen_osm and gn['id'] not in seen_gn;seen_osm.add(p['source']);seen_gn.add(gn['id'])
 assert [p['lon'],p['lat']]==osm['geometry']['coordinates'];assert dist((p['lat'],p['lon']),(gn['lat'],gn['lon']))<=500
 assert norm(p['name']) not in oldnames and norm(p['name']) in gn['aliases']
 assert all(dist((p['lat'],p['lon']),(q['lat'],q['lon']))>=400 for q in published);published.append(p)
 assert row['regionCode'].startswith('DE-') and p['name']==props['name']
assert len(seen_gn)==386
counts=dict(collections.Counter(p['country'] for p in new.values() if p['mapReady']));assert counts=={'PL':451,'DE':1000}
meta=read(u/'achievement-places.json')['places'];assert set(meta)=={p['id'] for p in new.values() if p['mapReady']}
assert all(meta[id]['regionCode'].startswith(new[id]['country']+'-') for id in meta)
assert collections.Counter(new[id]['country'] for id in meta if meta[id]['mustSee'])=={'PL':30,'DE':30}
assert hashlib.sha256((u/'catalog.json').read_bytes()).hexdigest()==report['catalog_sha256']
print('PASS: DE 1000 / PL 451; 386 unique sourced additions; baseline preserved; OSM/GeoNames names and <=500m positions; 400m duplicate exclusion; all administrative metadata')
