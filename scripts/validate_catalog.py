"""Validate source coverage, identity redirects, and map publication gates. Standard library only."""
import collections,json,pathlib,math
DATA=pathlib.Path(__file__).resolve().parents[1]/'data'
def read(name):return json.loads((DATA/name).read_text(encoding='utf-8'))
source=read('catalog_source.json')['records'];catalog=read('catalog_working.json')['records'];links=read('source_entity_links.json')
assert len(source)==2789
source_ids={r['source_id'] for r in source};assert len(source_ids)==len(source)
assert {r['source_id'] for r in links}==source_ids and len(links)==len(source)
ids={r['stable_id'] for r in catalog};assert len(ids)==len(catalog)
assert all(r['stable_id'] in ids for r in links)
assert collections.Counter(i for r in catalog for i in r['source_ids'])==collections.Counter(source_ids)
link_map={r['source_id']:r['stable_id'] for r in links}
assert all(link_map[i]==r['stable_id'] for r in catalog for i in r['source_ids'])
redirects=read('entity_id_redirects.json');assert len({r['old_stable_id'] for r in redirects})==len(redirects)
assert all(r['stable_id'] in ids and r['old_stable_id'] not in ids for r in redirects)
rejected={i:{f"https://www.openstreetmap.org/{dict(N='node',W='way',R='relation')[x['osm_type']]}/{x['osm_id']}" for x in rr} for i,rr in read('coordinate_rejections.json').items()}
for r in catalog:
 assert (r['latitude'] is None)==(r['longitude'] is None)
 if r['latitude'] is not None:
  assert math.isfinite(r['latitude']) and math.isfinite(r['longitude'])
  assert 45<=r['latitude']<=56 and 5<=r['longitude']<=25
  assert r['coordinate_source']['url'].startswith('https://www.openstreetmap.org/')
 if r['map_ready']:
  assert r['latitude'] is not None and r['record_kind']=='place'
  assert r['verification_status'] in ['cross_checked_osm_geonames','reviewed_source_context']
  assert r.get('coordinate_review')
  assert all(r['coordinate_source']['url'] not in rejected.get(i,set()) for i in r['source_ids'])
 if r['record_kind']=='suggested_visit_group':
  assert r['latitude'] is None and not r['map_ready']
  assert r['group_status']=='draft_from_source_requires_curation' and r['ordered_place_ids']==[]
status=read('completion_status.json')
assert status['source_records']==len(source) and status['working_entities']==len(catalog)
assert status['merged_occurrences']==len(source)-len(catalog)
assert status['map_ready']==sum(r['map_ready'] for r in catalog)
assert not status['complete'], 'Only change this gate after final catalog review.'
print(f'PASS: {len(source)} source links; {len(catalog)} entities; {status["map_ready"]} map-ready points; complete=false')
