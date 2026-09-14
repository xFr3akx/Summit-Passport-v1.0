#!/usr/bin/env python3
import json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
PINS=ROOT/'data/germany_manual_54_final_pins.json'
MAN=ROOT/'data/germany_review_manual_resolution.json'
CAT=ROOT/'app/src/main/assets/ui/catalog.json'
OUT=ROOT/'data/germany_manual_54_final_staging.json'
OUTCAT=ROOT/'data/catalog_germany_manual_54_final_candidate.json'

def dist(a,b):
    la1,lo1=a;la2,lo2=b
    x=math.radians(lo2-lo1)*math.cos(math.radians((la1+la2)/2));y=math.radians(la2-la1)
    return 6371000*math.hypot(x,y)

pins=json.loads(PINS.read_text(encoding='utf-8'))
manual=json.loads(MAN.read_text(encoding='utf-8'))
cat=json.loads(CAT.read_text(encoding='utf-8'))
meta={r['id']:r for r in manual['results']}
decisions=pins['decisions']
assert len(decisions)==54, len(decisions)
assert len({d['id'] for d in decisions})==54
assert sum(d.get('status')=='DUPLICATE' for d in decisions)==1

places=cat['places']; byid={p['id']:p for p in places}
existing=[p for p in places if p.get('country')=='DE' and p.get('mapReady') and p.get('lat') is not None and p.get('lon') is not None]
newcat=json.loads(json.dumps(cat)); newby={p['id']:p for p in newcat['places']}
results=[]; missing=[]
for d in decisions:
    m=meta.get(d['id'],{})
    if d.get('status')=='DUPLICATE':
        results.append(dict(d,finalStatus='DUPLICATE'))
        continue
    lat=float(d['lat']);lon=float(d['lon'])
    if not (47.0 <= lat <= 55.2 and 5.5 <= lon <= 15.6):
        results.append(dict(d,finalStatus='REVIEW',reason='outside conservative Germany bounds'))
        continue
    near=[]
    for p in existing:
        if p['id']==d['id']: continue
        dd=dist((lat,lon),(float(p['lat']),float(p['lon'])))
        if dd<80: near.append({'distanceM':round(dd,1),'id':p['id'],'name':p.get('name')})
    if near:
        results.append(dict(d,finalStatus='DUPLICATE',reason='within 80m of existing mapReady DE point',near=sorted(near,key=lambda x:x['distanceM'])[:5]))
        continue
    p=newby.get(d['id'])
    if p:
        if p.get('mapReady'):
            results.append(dict(d,finalStatus='DUPLICATE',reason='stable ID already mapReady in runtime'))
            continue
        p.update(lat=lat,lon=lon,mapReady=True,source=d['source'],coordinateRole=d['coordinateRole'])
        results.append(dict(d,finalStatus='STAGE_EXISTING'))
    else:
        proposed={
            'id':d['id'],'country':'DE','name':d['name'],'category':m.get('category'),
            'lat':lat,'lon':lon,'mapReady':True,'area':m.get('area',''),
            'source':d['source'],'coordinateRole':d['coordinateRole'],
            'note':d.get('note','')+'; missing_from_runtime_requires_region_and_collection_metadata_before_merge'
        }
        missing.append(proposed)
        results.append(dict(d,finalStatus='STAGE_NEW_RUNTIME_RECORD',reason='stable ID absent from current runtime; metadata gate remains'))

counts={}
for r in results: counts[r['finalStatus']]=counts.get(r['finalStatus'],0)+1
summary={
    'input':54,
    'counts':counts,
    'stageTotal':counts.get('STAGE_EXISTING',0)+counts.get('STAGE_NEW_RUNTIME_RECORD',0),
    'duplicateTotal':counts.get('DUPLICATE',0),
    'reviewTotal':counts.get('REVIEW',0),
    'missingRuntime':len(missing),
    'productionOverwritten':False
}
assert sum(counts.values())==54
assert summary['productionOverwritten'] is False
OUT.write_text(json.dumps({'summary':summary,'results':results,'newRuntimeRecords':missing},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
OUTCAT.write_text(json.dumps(newcat,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('FINAL_SUMMARY',json.dumps(summary,ensure_ascii=False))
for r in results:
    print(r['finalStatus'],r['name'],r.get('reason',''))
