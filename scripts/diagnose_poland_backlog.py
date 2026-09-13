#!/usr/bin/env python3
import json,collections,pathlib,re,unicodedata
ROOT=pathlib.Path(__file__).resolve().parents[1]
working=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'))['records']
runtime=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))['places']
rt={str(p.get('id') or p.get('stable_id')):p for p in runtime}
backlog=[r for r in working if r.get('country')=='PL' and r.get('record_kind')=='place' and not r.get('map_ready')]
ready=[r for r in working if r.get('country')=='PL' and r.get('record_kind')=='place' and r.get('map_ready')]
print('BACKLOG',len(backlog),'READY_WORKING',len(ready),'RUNTIME_PL',sum(1 for p in runtime if p.get('country')=='PL'))

def keycats(r): return tuple(r.get('source_categories') or [])
def keyregions(r): return tuple(r.get('source_regions') or [])
print('BACKLOG_SOURCE_CATEGORIES')
for k,v in collections.Counter(keycats(r) for r in backlog).most_common(): print(repr(k),v)
print('BACKLOG_COORDINATE_CANDIDATE',sum(bool(r.get('coordinate_candidate')) for r in backlog))
print('BACKLOG_COORDINATE_CANDIDATE_PL',sum(bool(r.get('coordinate_candidate')) and r['coordinate_candidate'].get('country')=='PL' for r in backlog))
print('BACKLOG_EXISTING_LATLON',sum(r.get('latitude') is not None and r.get('longitude') is not None for r in backlog))
print('BACKLOG_FEATURE_CODES')
for k,v in collections.Counter((r.get('coordinate_candidate') or {}).get('feature_code') for r in backlog if r.get('coordinate_candidate')).most_common(): print(repr(k),v)
print('BACKLOG_TOP_SOURCE_REGIONS')
for k,v in collections.Counter((r.get('source_regions') or [''])[0] for r in backlog).most_common(30): print(repr(k),v)
print('SOURCE_CATEGORY_TO_RUNTIME_CATEGORY')
mapcount=collections.defaultdict(collections.Counter)
examples=collections.defaultdict(list)
for r in ready:
    p=rt.get(str(r.get('stable_id')))
    if not p: continue
    sk=keycats(r)
    cat=str(p.get('category') or '')
    mapcount[sk][cat]+=1
    if len(examples[(sk,cat)])<5: examples[(sk,cat)].append(r.get('name'))
for sk,cnt in sorted(mapcount.items(),key=lambda kv:(str(kv[0]))):
    print(repr(sk),'->',dict(cnt))
    for cat,n in cnt.most_common(): print('  ',cat,examples[(sk,cat)])
print('BACKLOG_CANDIDATE_SAMPLES')
shown=0
for r in backlog:
    c=r.get('coordinate_candidate')
    if c and shown<50:
        print(json.dumps({'stable_id':r.get('stable_id'),'name':r.get('name'),'source_categories':r.get('source_categories'),'source_regions':r.get('source_regions'),'candidate':c},ensure_ascii=False))
        shown+=1
