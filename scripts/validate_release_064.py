"""Verify that the completion updates only previously pending DE IDs."""
from pathlib import Path
import json,hashlib,collections
r=Path(__file__).resolve().parents[1];u=r/'app/src/main/assets/ui'
old=json.loads((r/'data/catalog_runtime_063.json').read_text(encoding='utf8'))
raw=(u/'catalog.json').read_bytes();new=json.loads(raw)
before={p['id']:p for p in old['places']};after={p['id']:p for p in new['places']}
audit=json.loads((r/'data/germany_completion_064.json').read_text(encoding='utf8'));release=json.loads((r/'data/release_064.json').read_text(encoding='utf8'))
assert set(before)==set(after)
assert all(after[k]==p for k,p in before.items() if p['country']=='PL' or p['mapReady'])
assert len(audit['accepted'])==333 and len(audit['duplicates'])==12 and len(audit['unresolved'])==331
reviewed=[p['id'] for section in ['accepted','duplicates','unresolved'] for p in audit[section]]
assert len(reviewed)==len(set(reviewed))==676
assert set(reviewed)=={p['id'] for p in before.values() if p['country']=='DE' and not p['mapReady']}
sources={p['source'] for p in before.values() if p['mapReady'] and p['country']=='DE'}
for c in audit['accepted']:
 p=after[c['id']]
 assert not before[p['id']]['mapReady'] and p['mapReady'] and c['sourceIds']
 assert c['source'] not in sources;sources.add(c['source'])
 assert p['source']==c['source'] and p['lat']==c['lat'] and p['lon']==c['lon']
 assert 47.2<=p['lat']<=55.2 and 5.8<=p['lon']<=15.1
for c in audit['duplicates']:
 assert not after[c['id']]['mapReady'] and after[c['duplicateOf']]['mapReady']
 assert after[c['id']]['duplicateOf']==c['duplicateOf']
meta=json.loads((u/'achievement-places.json').read_text(encoding='utf8'))['places']
assert set(meta)=={p['id'] for p in after.values() if p['mapReady']}
assert collections.Counter(p['country'] for p in after.values() if p['mapReady'])=={'PL':451,'DE':1333}
assert hashlib.sha256(raw).hexdigest()==release['catalog_sha256']
assert not release['catalog_complete'] and not release['germany_complete']
print('PASS: 333 completed existing DE records, 12 linked duplicates, 331 honestly unresolved; all old mapped records and all PL records unchanged; complete achievement metadata')
