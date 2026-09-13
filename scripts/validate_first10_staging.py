#!/usr/bin/env python3
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];D=ROOT/'data';O=D/'first10_backlog'
oldw=json.loads((D/'catalog_working.json').read_text(encoding='utf-8'))
neww=json.loads((O/'catalog_working_next.json').read_text(encoding='utf-8'))
oldr=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))
newr=json.loads((O/'catalog_main_candidate.json').read_text(encoding='utf-8'))
summary=json.loads((O/'summary.json').read_text(encoding='utf-8'));patch=json.loads((O/'ready_patch.json').read_text(encoding='utf-8'));review=json.loads((O/'needs_review.json').read_text(encoding='utf-8'))
assert summary['processed']==10 and summary['ready']==9 and summary['review']==1 and summary['duplicates']==0
assert summary['production_overwritten'] is False and summary['stable_ids_preserved'] is True
assert len(patch)==9 and len(review)==1 and review[0]['name']=='Saffenburg-Blick'
ow={x['stable_id']:x for x in oldw['records']};nw={x['stable_id']:x for x in neww['records']};orr={x['id']:x for x in oldr['places']};nr={x['id']:x for x in newr['places']}
assert set(ow)==set(nw) and set(orr)==set(nr)
ids={x['stable_id'] for x in patch};assert len(ids)==9
allowed_runtime={'lat','lon','mapReady','source','coordinateRole'}
for sid in set(orr):
 changed={k for k in set(orr[sid])|set(nr[sid]) if orr[sid].get(k)!=nr[sid].get(k)}
 if sid in ids:
  assert changed<=allowed_runtime and nr[sid]['mapReady'] is True and orr[sid]['mapReady'] is False,(sid,changed)
  assert nr[sid]['id']==orr[sid]['id'] and nr[sid]['name']==orr[sid]['name'] and nr[sid]['category']==orr[sid]['category'] and nr[sid]['country']==orr[sid]['country']
  assert nr[sid]['source'].startswith('https://www.openstreetmap.org/')
 else:assert not changed,(sid,changed)
for sid in ids:
 w=nw[sid];assert w['map_ready'] is True and w['verification_status']=='reviewed_source_context' and w.get('coordinate_review') and w['coordinate_source']['url'].startswith('https://www.openstreetmap.org/')
review_id=review[0]['stable_id'];assert nw[review_id].get('map_ready') is False and nr[review_id].get('mapReady') is False
assert sum(bool(x.get('map_ready')) for x in neww['records'])==sum(bool(x.get('map_ready')) for x in oldw['records'])+9
assert sum(bool(x.get('mapReady')) for x in newr['places'])==sum(bool(x.get('mapReady')) for x in oldr['places'])+9
print('PASS first10 staging: 9 READY, 1 REVIEW, 0 duplicate; IDs/names/categories preserved; production unchanged')
