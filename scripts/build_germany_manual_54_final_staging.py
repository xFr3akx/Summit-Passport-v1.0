#!/usr/bin/env python3
import json,math,pathlib,copy
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
decisions=copy.deepcopy(pins['decisions'])
assert len(decisions)==54, len(decisions)
assert len({d['id'] for d in decisions})==54

# Manually verified corrections after semantic duplicate review.
overrides={
    # Elztal and Elzbachtal are the same Elzbach valley concept around Pyrmont.
    'SP-54a45d82-f2ca-5e6d-80d0-2a6debb5ec72': {
        'status':'DUPLICATE','duplicateOf':'SP-67fa2d8d-bd23-55eb-a2f0-a062338d10ca',
        'source':'https://www.rlp-tourismus.com/de/ausflugsziele/elzbachtal/poi.html',
        'note':'Alias/duplicate of Elzbachtal; keep one canonical valley entry.'
    },
    # Hannoversche Klippen are the natural cliff group; Weser-Skywalk is a platform on one cliff.
    'SP-1415aa7e-34a2-5863-bfdb-02ee7e2dce79': {
        'lat':51.65,'lon':9.43167,'coordinateRole':'representative_point_not_entrance',
        'source':'https://de.wikivoyage.org/wiki/Hannoversche_Klippen',
        'note':'Representative point for the natural Hannoversche Klippen, distinct from Weser-Skywalk.'
    },
    # Correct plural Mühlsteinhöhlen to Rother Kopf, not the singular cave at Nerother Kopf.
    'SP-51859a71-8d48-56d3-978a-c3302a13486c': {
        'lat':50.247649,'lon':6.620380,'coordinateRole':'exact_point',
        'source':'https://www.outdooractive.com/de/poi/eifel/muehlsteinhoehlen-rother-kopf/15029416/',
        'note':'Mühlsteinhöhlen am Rother Kopf near Gerolstein; corrected from mistaken Nerother Kopf match.'
    },
    # Ürziger Felsen refers to the eastern rocky Urley landscape, not the Würzgarten vineyard itself.
    'SP-50db4623-bc26-5587-82d2-6fc72e263974': {
        'lat':49.9809,'lon':7.0167,'coordinateRole':'representative_point_not_entrance',
        'source':'https://www.uerzig.de/uerzig/wissenswertes-von-a-z/',
        'note':'Representative point for the eastern Ürzig rock/Urley landscape, distinct from Ürziger Würzgarten.'
    }
}
for d in decisions:
    ov=overrides.get(d['id'])
    if ov:
        # Clear stale explicit duplicate fields unless override itself remains duplicate.
        if ov.get('status')!='DUPLICATE':
            d.pop('status',None); d.pop('duplicateOf',None)
        d.update(ov)

places=cat['places']; byid={p['id']:p for p in places}
existing=[p for p in places if p.get('country')=='DE' and p.get('mapReady') and p.get('lat') is not None and p.get('lon') is not None]
newcat=json.loads(json.dumps(cat)); newby={p['id']:p for p in newcat['places']}
results=[]; missing=[]
for d in decisions:
    m=meta.get(d['id'],{})
    if d.get('status')=='DUPLICATE':
        results.append(dict(d,finalStatus='DUPLICATE',reason=d.get('note','explicit semantic duplicate')))
        continue
    lat=float(d['lat']);lon=float(d['lon'])
    if not (47.0 <= lat <= 55.2 and 5.5 <= lon <= 15.6):
        results.append(dict(d,finalStatus='REVIEW',reason='outside conservative Germany bounds'))
        continue
    near=[]
    for p in existing:
        if p['id']==d['id']: continue
        dd=dist((lat,lon),(float(p['lat']),float(p['lon'])))
        if dd<80: near.append({'distanceM':round(dd,1),'id':p['id'],'name':p.get('name'),'category':p.get('category')})
    # Proximity alone is NOT a duplicate. Preserve as an auditable warning.
    p=newby.get(d['id'])
    if p:
        if p.get('mapReady'):
            results.append(dict(d,finalStatus='DUPLICATE',reason='same stable ID already mapReady in runtime',nearExisting=near))
            continue
        p.update(lat=lat,lon=lon,mapReady=True,source=d['source'],coordinateRole=d['coordinateRole'])
        results.append(dict(d,finalStatus='STAGE_EXISTING',nearExisting=near))
    else:
        proposed={
            'id':d['id'],'country':'DE','name':d['name'],'category':m.get('category'),
            'lat':lat,'lon':lon,'mapReady':True,'area':m.get('area',''),
            'source':d['source'],'coordinateRole':d['coordinateRole'],
            'nearExisting':near,
            'note':d.get('note','')+'; missing_from_runtime_requires_region_and_collection_metadata_before_merge'
        }
        missing.append(proposed)
        results.append(dict(d,finalStatus='STAGE_NEW_RUNTIME_RECORD',reason='stable ID absent from current runtime; metadata gate remains',nearExisting=near))

counts={}
for r in results: counts[r['finalStatus']]=counts.get(r['finalStatus'],0)+1
summary={
    'input':54,
    'counts':counts,
    'stageTotal':counts.get('STAGE_EXISTING',0)+counts.get('STAGE_NEW_RUNTIME_RECORD',0),
    'duplicateTotal':counts.get('DUPLICATE',0),
    'reviewTotal':counts.get('REVIEW',0),
    'missingRuntime':len(missing),
    'nearExistingWarnings':sum(bool(r.get('nearExisting')) for r in results),
    'productionOverwritten':False,
    'duplicatePolicy':'explicit semantic duplicate or same stable ID; proximity is warning only'
}
assert sum(counts.values())==54
assert summary['productionOverwritten'] is False
OUT.write_text(json.dumps({'summary':summary,'results':results,'newRuntimeRecords':missing},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
OUTCAT.write_text(json.dumps(newcat,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('FINAL_SUMMARY',json.dumps(summary,ensure_ascii=False))
for r in results:
    print(r['finalStatus'],r['name'],r.get('reason',''),('near='+str(len(r.get('nearExisting',[]))) if r.get('nearExisting') else ''))
