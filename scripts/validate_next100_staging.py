#!/usr/bin/env python3
import json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
out=R/'data/next100_backlog'
summary=json.loads((out/'summary.json').read_text(encoding='utf-8'))
base=json.loads((R/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))
stage=json.loads((out/'catalog_main_candidate.json').read_text(encoding='utf-8'))
ready=json.loads((out/'ready_patch.json').read_text(encoding='utf-8'))
review=json.loads((out/'needs_review.json').read_text(encoding='utf-8'))
dups=json.loads((out/'possible_duplicates.json').read_text(encoding='utf-8'))
assert summary['processed']==100 and summary['range']=='11-110'
assert summary['ready']==len(ready) and summary['review']==len(review) and summary['duplicates']==len(dups)
assert len(ready)+len(review)+len(dups)==100
assert summary['production_overwritten'] is False and summary['stable_ids_preserved'] is True
assert summary['backlog_total']==853 and summary['backlog_by_country']=={'PL':522,'DE':331}
b={p['id']:p for p in base['places']};s={p['id']:p for p in stage['places']};assert set(b)==set(s)
changed=[]
for sid,p in s.items():
 q=b[sid]
 if p!=q:
  changed.append(sid)
  assert p['name']==q['name'] and p['category']==q['category'] and p['country']==q['country']
  assert not q.get('mapReady') and p.get('mapReady') is True
  allowed={'lat','lon','mapReady','source','coordinateRole'}
  assert {k for k in set(p)|set(q) if p.get(k)!=q.get(k)}<=allowed
# cumulative candidate contains prior first10 + current ready
assert len(changed)==summary['cumulative_staging_ready_added'],(len(changed),summary)
assert all(x['stable_id'] in changed for x in ready)
review_ids={x['stable_id'] for x in review};dup_ids={x['stable_id'] for x in dups}
assert not review_ids&dup_ids
assert all(s[x]['mapReady']==b[x]['mapReady'] for x in review_ids|dup_ids)
print(f"PASS next100 staging: {len(ready)} READY, {len(review)} REVIEW, {len(dups)} duplicates; cumulative staged={len(changed)}; production unchanged")
