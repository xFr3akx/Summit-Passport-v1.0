#!/usr/bin/env python3
import json,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
working=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'))['records']
runtime=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))['places']
germany=json.loads((ROOT/'data/germany_completion_064.json').read_text(encoding='utf-8'))
ridx={p['id']:p for p in runtime}
dup_ids=set()
def walk(x):
    if isinstance(x,dict):
        if x.get('status')=='duplicate' and x.get('id') and x.get('duplicateOf'):
            dup_ids.add(x['id'])
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(germany)
assert len(dup_ids)==12, f'Expected 12 DE duplicate links, got {len(dup_ids)}'
backlog=[r for r in working if r.get('country') in {'PL','DE'} and r.get('record_kind')=='place' and not r.get('map_ready') and r.get('stable_id') in ridx and not ridx[r['stable_id']].get('mapReady') and r.get('stable_id') not in dup_ids]
counts=collections.Counter(r['country'] for r in backlog)
assert counts=={'PL':522,'DE':331},counts
backlog.sort(key=lambda r:(r.get('country',''),str((r.get('source_regions') or [''])[0]),r.get('name',''),r.get('stable_id','')))
rows=[]
for i,r in enumerate(backlog[:10],1):
    p=ridx[r['stable_id']]
    row={'index':i,'stable_id':r['stable_id'],'country':r['country'],'name':r.get('name') or p.get('name'),'category':p.get('category'),'region':p.get('region'),'area':p.get('area'),'source_ids':r.get('source_ids',[]),'coordinate_candidate':r.get('coordinate_candidate')}
    rows.append(row);print(json.dumps(row,ensure_ascii=False))
out=ROOT/'data/first10_backlog';out.mkdir(parents=True,exist_ok=True);(out/'selection.json').write_text(json.dumps({'backlog_total':len(backlog),'by_country':dict(counts),'duplicates_excluded':len(dup_ids),'records':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SUMMARY',json.dumps({'backlog_total':len(backlog),'by_country':dict(counts),'duplicates_excluded':len(dup_ids),'selected':len(rows)},ensure_ascii=False))
