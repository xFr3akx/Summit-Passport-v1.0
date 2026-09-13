#!/usr/bin/env python3
import argparse,csv,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--limit',type=int,default=100)
p.add_argument('--offset',type=int,default=0)
p.add_argument('--output',type=pathlib.Path,default=ROOT/'data/poland_backlog_batch_001.csv')
a=p.parse_args()
data=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'))
records=data['records']
backlog=[r for r in records if r.get('country')=='PL' and r.get('record_kind')=='place' and not r.get('map_ready')]
assert len(backlog)==522, f'Expected 522 unresolved PL places, got {len(backlog)}'
backlog.sort(key=lambda r:(str(r.get('region_code') or r.get('region') or ''),str(r.get('category') or ''),str(r.get('name') or ''),r.get('stable_id','')))
selected=backlog[a.offset:a.offset+a.limit]
a.output.parent.mkdir(parents=True,exist_ok=True)
fields=['stable_id','country','name','category','region','area','latitude','longitude','verification_status','source_ids','notes']
with a.output.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in selected:
  w.writerow({
   'stable_id':r.get('stable_id',''),'country':r.get('country',''),'name':r.get('name',''),'category':r.get('category',''),
   'region':r.get('region_code') or r.get('region') or '','area':r.get('area') or r.get('source_region') or '',
   'latitude':r.get('latitude') if r.get('latitude') is not None else '',
   'longitude':r.get('longitude') if r.get('longitude') is not None else '',
   'verification_status':r.get('verification_status',''),'source_ids':'|'.join(r.get('source_ids',[])),
   'notes':r.get('coordinate_review') or ''})
print(json.dumps({'unresolved_pl':len(backlog),'offset':a.offset,'exported':len(selected),'output':str(a.output)},ensure_ascii=False))
