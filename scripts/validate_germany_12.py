"""Validate the work-in-progress German completion against the published 1.1 catalog."""
from pathlib import Path
import json,hashlib,collections
r=Path(__file__).resolve().parents[1];u=r/'app/src/main/assets/ui'
def read(p):return json.loads(p.read_text(encoding='utf8'))
old=read(r/'data/catalog_runtime_11.json');raw=(u/'catalog.json').read_bytes();cat=json.loads(raw)
before={p['id']:p for p in old['places']};after={p['id']:p for p in cat['places']}
assert len(after)==len(cat['places']) and set(before)<=set(after)
assert all(after[k]==p for k,p in before.items() if p['country']=='PL' or p['mapReady'])
audit=read(r/'data/germany_completion_12.json');report=read(r/'data/release_12.json')
assert hashlib.sha256(raw).hexdigest()==report['catalog_sha256']
assert hashlib.sha256((r/'data/catalog_runtime_11.json').read_bytes()).hexdigest()==report['previous_catalog_sha256']
original_pending={p['id'] for p in before.values() if p['country']=='DE' and not p['mapReady'] and not p.get('duplicateOf')}
reviewed=[p['id'] for p in audit['accepted'] if not p['addedBySplit']]+[p['id'] for section in ['groups','duplicates','excluded','unresolved'] for p in audit[section]]
assert len(reviewed)==len(set(reviewed)) and set(reviewed)==original_pending
new_ids={p['id'] for p in audit['accepted'] if p['addedBySplit']}
assert new_ids==set(after)-set(before)
for entry in audit['accepted']:
 p=after[entry['id']];e=entry['evidence']
 assert p['country']=='DE' and p['mapReady'] and p['source']==e['source']
 assert p['lat']==e['lat'] and p['lon']==e['lon'] and p['category']==e['category']
 assert 47.1<p['lat']<55.3 and 5.7<p['lon']<15.2
 if p['coordinateRole']=='documented_start':assert e.get('identitySource')
for entry in audit['groups']:
 p=after[entry['id']];ids=p['resolvedInto']
 assert not p['mapReady'] and len(ids)>1 and len(ids)==len(set(ids))
 assert all(after[id]['mapReady'] and after[id]['country']=='DE' for id in ids)
for entry in audit['duplicates']:
 p=after[entry['id']];assert not p['mapReady'] and p['duplicateOf']==entry['duplicateOf'] and after[p['duplicateOf']]['mapReady']
for id in new_ids:
 assert all(id in after[parent]['resolvedInto'] for parent in after[id]['sourceParentIds'])
for entry in audit['excluded']:
 p=after[entry['id']];assert not p['mapReady'] and p['resolutionStatus']=='outside_country' and p['actualCountry']!='DE' and entry['source'] and entry['secondSource']
ready=[p for p in after.values() if p['mapReady'] and p['country']=='DE']
sources=[p['source'] for p in ready];assert len(sources)==len(set(sources))
meta=read(u/'achievement-places.json')['places'];assert set(meta)=={p['id'] for p in after.values() if p['mapReady']}
assert collections.Counter(p['country'] for p in after.values() if p['mapReady'])==report['map_points']
assert report['unresolvedGermany']==len(audit['unresolved']) and report['germany_complete']==(not audit['unresolved'])
print('PASS: source-backed updates, unique sources, group resolution, documented starts, old IDs/Poland preserved, complete metadata, honest pending count')
