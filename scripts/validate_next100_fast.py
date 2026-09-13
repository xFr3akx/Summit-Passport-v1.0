#!/usr/bin/env python3
import json,pathlib
R=pathlib.Path(__file__).resolve().parents[1];O=R/'data/next100_fast'
s=json.loads((O/'summary.json').read_text(encoding='utf-8'));base=json.loads((R/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'));stage=json.loads((O/'catalog_main_candidate.json').read_text(encoding='utf-8'));ready=json.loads((O/'ready_patch.json').read_text(encoding='utf-8'));review=json.loads((O/'needs_review.json').read_text(encoding='utf-8'));dups=json.loads((O/'possible_duplicates.json').read_text(encoding='utf-8'))
assert s['processed']==100 and s['range']=='11-110';assert len(ready)+len(review)+len(dups)==100;assert s['ready']==len(ready) and s['review']==len(review) and s['duplicates']==len(dups);assert s['production_overwritten'] is False
b={p['id']:p for p in base['places']};t={p['id']:p for p in stage['places']};assert set(b)==set(t);changed=[]
for k,p in t.items():
 q=b[k]
 if p!=q:
  changed.append(k);assert p['name']==q['name'] and p['category']==q['category'] and p['country']==q['country'];assert not q.get('mapReady') and p.get('mapReady') is True;assert {x for x in set(p)|set(q) if p.get(x)!=q.get(x)}<={'lat','lon','mapReady','source','coordinateRole'}
assert len(changed)==s['cumulative_staged'];assert all(x['stable_id'] in changed for x in ready);assert all(t[x['stable_id']].get('mapReady')==b[x['stable_id']].get('mapReady') for x in review+dups)
print(f"PASS next100 fast: {len(ready)} READY, {len(review)} REVIEW, {len(dups)} DUP; cumulative staged={len(changed)}; production unchanged")
