#!/usr/bin/env python3
import argparse,json,math,pathlib,re,unicodedata,collections,csv
ROOT=pathlib.Path(__file__).resolve().parents[1]

def norm(s):
    s=unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','',s)

def distance_m(a,b):
    lat1,lon1=a;lat2,lon2=b
    x=math.radians(lon2-lon1)*math.cos(math.radians((lat1+lat2)/2))
    y=math.radians(lat2-lat1)
    return 6371000*math.hypot(x,y)

def ring_contains(x,y,ring):
    inside=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y):
            xx=(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]
            if x<xx: inside=not inside
    return inside

def make_inside(boundary):
    geom=boundary['PL']
    polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    def inside(lat,lon):
        return any(ring_contains(lon,lat,p[0]) and not any(ring_contains(lon,lat,h) for h in p[1:]) for p in polys)
    return inside

# Conservative whitelist. Most pairs are learned directly from existing PL runtime records.
# Additional pairs below use unambiguous official GeoNames meanings and the project's existing
# source-category taxonomy. Ambiguous mappings remain REVIEW.
PAIR_TO_RUNTIME_CATEGORY={
    ('▲','MT'):'peak', ('▲','PK'):'peak', ('Szczyt','MT'):'peak',
    ('≈','RSV'):'water', ('≈','PND'):'water', ('≈','LK'):'water', ('≈','FLLS'):'waterfall',
    ('◆','PASS'):'pass', ('Przełęcz','PASS'):'pass',
    ('⬡','CAVE'):'cave', ('⬡','RK'):'rock', ('⬡','RKS'):'rock', ('⬡','MT'):'rock',
    ('♧','CLG'):'nature', ('♧','DSRT'):'nature', ('♧','PK'):'viewpoint', ('♧','MDW'):'nature',
    ('♧','MT'):'nature', ('♧','HLL'):'nature', ('♧','PRK'):'nature', ('♧','CNL'):'nature',
    ('♧','VAL'):'nature', ('♧','RESN'):'nature', ('♧','FRST'):'nature',
    ('⌂','CSTL'):'castle', ('⌂','FT'):'castle', ('⌂','TOWR'):'viewpoint',
    ('⌂','MNMT'):'heritage', ('⌂','HUT'):'heritage', ('⌂','MUS'):'heritage', ('⌂','LTHSE'):'lighthouse',
    ('Hala / panorama','CLG'):'nature', ('Polana / widok','MDW'):'viewpoint', ('Szczyt / grzbiet','PK'):'peak',
}

p=argparse.ArgumentParser()
p.add_argument('input',type=pathlib.Path)
p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--ready-csv',type=pathlib.Path,required=True)
p.add_argument('--near-m',type=float,default=150.0)
a=p.parse_args()

audit=json.loads(a.input.read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'))['records']
boundary=json.loads((ROOT/'app/src/main/assets/ui/boundaries.json').read_text(encoding='utf-8'))
inside=make_inside(boundary)
existing=[]
for r in catalog:
    if r.get('country')!='PL' or r.get('record_kind')!='place' or not r.get('map_ready'): continue
    try: lat=float(r.get('latitude'));lon=float(r.get('longitude'))
    except (TypeError,ValueError): continue
    existing.append({'stable_id':r.get('stable_id'),'name':r.get('name',''),'category':r.get('category',''),'lat':lat,'lon':lon})
existing_names=collections.defaultdict(list)
for r in existing: existing_names[norm(r['name'])].append(r)

rows=[]
for item in audit:
    row=dict(item);reasons=[];chosen=None;runtime_category=None
    if item.get('status')!='CANDIDATE': reasons.append('geocoder_not_unambiguous')
    ids={((m.get('osm_type') or ''),str(m.get('osm_id') or '')) for m in item.get('matches',[])}
    ids.discard(('', ''))
    if len(ids)!=1: reasons.append('identity_count_'+str(len(ids)))
    if item.get('matches'):
        chosen=item['matches'][0]
        feature_code=str(chosen.get('osm_value') or '')
        pair=(str(item.get('category') or ''),feature_code)
        runtime_category=PAIR_TO_RUNTIME_CATEGORY.get(pair)
        if chosen.get('osm_type')=='GEONAMES' and not runtime_category:
            reasons.append('unproven_type_pair:%s+%s'%pair)
        try: lat=float(chosen['lat']);lon=float(chosen['lon'])
        except (TypeError,ValueError,KeyError): reasons.append('invalid_coordinates');lat=lon=None
        if lat is not None and not inside(lat,lon): reasons.append('outside_pl_boundary')
        if lat is not None:
            same_name=[r for r in existing_names.get(norm(item.get('name')),[]) if r['stable_id']!=item.get('stable_id')]
            if same_name: reasons.append('existing_exact_name:'+','.join(r['stable_id'] for r in same_name if r.get('stable_id')))
            near=[r for r in existing if r['stable_id']!=item.get('stable_id') and distance_m((lat,lon),(r['lat'],r['lon']))<a.near_m]
            if near: reasons.append('existing_within_%dm:%s'%(int(a.near_m),','.join(r['stable_id'] for r in near[:5] if r.get('stable_id'))))
    else: reasons.append('no_match_payload')
    row['_chosen']=chosen;row['_reasons']=reasons;row['_runtime_category']=runtime_category;rows.append(row)

for i,r in enumerate(rows):
    c=r['_chosen']
    if not c: continue
    key=(c.get('osm_type'),str(c.get('osm_id')))
    for j,s in enumerate(rows):
        if i==j: continue
        d=s['_chosen']
        if not d: continue
        if key==(d.get('osm_type'),str(d.get('osm_id'))):
            r['_reasons'].append('batch_same_identity:'+str(s.get('stable_id')))
        elif norm(r.get('name')) and norm(r.get('name'))==norm(s.get('name')):
            r['_reasons'].append('batch_exact_name:'+str(s.get('stable_id')))
        elif r['_runtime_category'] and r['_runtime_category']==s['_runtime_category'] and distance_m((float(c['lat']),float(c['lon'])),(float(d['lat']),float(d['lon'])))<a.near_m:
            r['_reasons'].append('batch_same_category_near:'+str(s.get('stable_id')))

result=[];ready=[]
for r in rows:
    reasons=sorted(set(r.pop('_reasons')));chosen=r.pop('_chosen');runtime_category=r.pop('_runtime_category')
    status='READY' if not reasons and runtime_category else 'REVIEW'
    if not runtime_category and 'geocoder_not_unambiguous' not in reasons and not any(x.startswith('unproven_type_pair:') for x in reasons):
        reasons.append('runtime_category_unresolved')
    out=dict(r,validation_status=status,validation_reasons=reasons,runtime_category=runtime_category,chosen=chosen)
    result.append(out)
    if status=='READY' and chosen:
        source_prefix='geonames' if chosen.get('osm_type')=='GEONAMES' else 'osm'
        ready.append({
            'stable_id':r['stable_id'],'name':r['name'],'category':runtime_category,'source_category':r.get('category',''),'region':r.get('region',''),
            'latitude':chosen['lat'],'longitude':chosen['lon'],
            'source_id':'%s:%s'%(source_prefix,chosen.get('osm_id')),
            'feature_code':chosen.get('osm_value'),
            'verification_status':'verified_coordinate_candidate_type_and_collision'
        })
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
fields=['stable_id','name','category','source_category','region','latitude','longitude','source_id','feature_code','verification_status']
with a.ready_csv.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(ready)
summary=collections.Counter(x['validation_status'] for x in result)
print('VALIDATION_SUMMARY '+json.dumps(summary,ensure_ascii=False))
print('READY_COUNT',len(ready))
for x in result:
    if x['validation_status']=='READY': print('READY',x['stable_id'],x['name'],x['runtime_category'],(x.get('chosen') or {}).get('osm_value'))
    else: print('REVIEW',x['stable_id'],x['name'],' | '.join(x['validation_reasons']))
