#!/usr/bin/env python3
import argparse,csv,json,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--limit',type=int,default=100)
p.add_argument('--offset',type=int,default=0)
p.add_argument('--output',type=pathlib.Path,default=ROOT/'data/poland_backlog_batch_001.csv')
a=p.parse_args()
data=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'))
records=data['records']
runtime=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))['places']
backlog=[r for r in records if r.get('country')=='PL' and r.get('record_kind')=='place' and not r.get('map_ready')]
assert len(backlog)==522, f'Expected 522 unresolved PL places, got {len(backlog)}'
print('DIAG source_categories',dict(collections.Counter(tuple(r.get('source_categories') or []) for r in backlog)))
print('DIAG coordinate_candidate',sum(bool(r.get('coordinate_candidate')) for r in backlog))
print('DIAG coordinate_candidate_PL',sum(bool(r.get('coordinate_candidate')) and (r.get('coordinate_candidate') or {}).get('country')=='PL' for r in backlog))
print('DIAG latlon',sum(r.get('latitude') is not None and r.get('longitude') is not None for r in backlog))
print('DIAG feature_codes',dict(collections.Counter((r.get('coordinate_candidate') or {}).get('feature_code') for r in backlog if r.get('coordinate_candidate'))))
print('DIAG sourcecat_feature',dict(collections.Counter(((r.get('source_categories') or [''])[0],(r.get('coordinate_candidate') or {}).get('feature_code')) for r in backlog if r.get('coordinate_candidate'))))
print('DIAG source_regions_top',collections.Counter((r.get('source_regions') or [''])[0] for r in backlog).most_common(25))
# Empirical mapping: source category in working data -> category already used by the runtime catalog.
rt_by_id={str(p.get('id') or p.get('stable_id') or ''):p for p in runtime if p.get('country')=='PL'}
source_to_runtime=collections.defaultdict(collections.Counter)
source_feature_runtime=collections.defaultdict(collections.Counter)
for r in records:
 if r.get('country')!='PL' or r.get('record_kind')!='place' or not r.get('map_ready'): continue
 rp=rt_by_id.get(str(r.get('stable_id') or ''))
 if not rp: continue
 source=(r.get('source_categories') or [''])[0]
 runtime_cat=str(rp.get('category') or '')
 source_to_runtime[source][runtime_cat]+=1
 c=r.get('coordinate_candidate') or {}
 if c.get('feature_code'): source_feature_runtime[(source,c.get('feature_code'))][runtime_cat]+=1
print('DIAG empirical_source_to_runtime',{k:dict(v) for k,v in source_to_runtime.items()})
print('DIAG empirical_source_feature_to_runtime',{str(k):dict(v) for k,v in source_feature_runtime.items()})
backlog.sort(key=lambda r:(str((r.get('source_regions') or [''])[0]),str((r.get('source_categories') or [''])[0]),str(r.get('name') or ''),r.get('stable_id','')))
selected=backlog[a.offset:a.offset+a.limit]
a.output.parent.mkdir(parents=True,exist_ok=True)
fields=['stable_id','country','name','category','region','area','latitude','longitude','verification_status','source_ids','notes']
with a.output.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in selected:
  source_cat=(r.get('source_categories') or [''])[0]
  source_region=(r.get('source_regions') or [''])[0]
  c=r.get('coordinate_candidate') or {}
  w.writerow({
   'stable_id':r.get('stable_id',''),'country':r.get('country',''),'name':r.get('name',''),'category':source_cat,
   'region':source_region,'area':'',
   'latitude':c.get('latitude','') if c else '',
   'longitude':c.get('longitude','') if c else '',
   'verification_status':r.get('verification_status',''),'source_ids':'|'.join(r.get('source_ids',[])),
   'notes':json.dumps({'feature_code':c.get('feature_code'),'geonames_id':c.get('geonames_id')},ensure_ascii=False) if c else ''})
print(json.dumps({'unresolved_pl':len(backlog),'offset':a.offset,'exported':len(selected),'output':str(a.output)},ensure_ascii=False))
