#!/usr/bin/env python3
import argparse,json,math,pathlib,re,unicodedata,collections,csv
ROOT=pathlib.Path(__file__).resolve().parents[1]

def norm(s):
    s=unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','',s)
def distance_m(a,b):
    lat1,lon1=a;lat2,lon2=b;x=math.radians(lon2-lon1)*math.cos(math.radians((lat1+lat2)/2));y=math.radians(lat2-lat1);return 6371000*math.hypot(x,y)
def ring_contains(x,y,ring):
    inside=False
    for aa,b in zip(ring,ring[1:]+ring[:1]):
        if (aa[1]>y)!=(b[1]>y) and x<(b[0]-aa[0])*(y-aa[1])/(b[1]-aa[1])+aa[0]:inside=not inside
    return inside
def make_inside(boundary):
    geom=boundary['PL'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    return lambda lat,lon:any(ring_contains(lon,lat,p[0]) and not any(ring_contains(lon,lat,h) for h in p[1:]) for p in polys)

# Runtime category is authoritative. GeoNames feature code is only a semantic gate.
FEATURE_ALLOWED={
 'MT':{'peak','nature','rock'},'PK':{'peak','viewpoint'},'PASS':{'pass'},
 'LK':{'water'},'RSV':{'water'},'PND':{'water'},'FLLS':{'waterfall'},
 'CAVE':{'cave'},'RK':{'rock'},'RKS':{'rock'},
 'VAL':{'nature'},'RESN':{'nature'},'FRST':{'nature'},'CLG':{'nature'},'DSRT':{'nature'},'MDW':{'nature','viewpoint'},'HLL':{'nature'},'PRK':{'nature'},'CNL':{'nature'},
 'CSTL':{'castle','heritage'},'FT':{'castle','heritage'},'TOWR':{'viewpoint','heritage'},'MNMT':{'heritage'},'HUT':{'heritage'},'MUS':{'heritage'},'LTHSE':{'lighthouse'},
}
p=argparse.ArgumentParser();p.add_argument('input',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--ready-csv',type=pathlib.Path,required=True);p.add_argument('--near-m',type=float,default=150.0);a=p.parse_args()
audit=json.loads(a.input.read_text(encoding='utf-8'));catalog=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'))['records'];inside=make_inside(json.loads((ROOT/'app/src/main/assets/ui/boundaries.json').read_text(encoding='utf-8')))
existing=[]
for r in catalog:
    if r.get('country')!='PL' or r.get('record_kind')!='place' or not r.get('map_ready'):continue
    try:lat=float(r.get('latitude'));lon=float(r.get('longitude'))
    except (TypeError,ValueError):continue
    existing.append({'stable_id':r.get('stable_id'),'name':r.get('name',''),'lat':lat,'lon':lon})
existing_names=collections.defaultdict(list)
for r in existing:existing_names[norm(r['name'])].append(r)
rows=[]
for item in audit:
    row=dict(item);reasons=[];chosen=None;runtime_category=str(item.get('category') or '')
    if item.get('status')!='CANDIDATE':reasons.append('geocoder_not_unambiguous')
    ids={(m.get('osm_type') or '',str(m.get('osm_id') or '')) for m in item.get('matches',[])};ids.discard(('', ''))
    if len(ids)!=1:reasons.append('identity_count_'+str(len(ids)))
    if item.get('matches'):
        chosen=item['matches'][0];feature=str(chosen.get('osm_value') or '');allowed=FEATURE_ALLOWED.get(feature,set())
        if chosen.get('osm_type')=='GEONAMES' and runtime_category not in allowed:reasons.append(f'feature_category_mismatch:{feature}+{runtime_category}')
        try:lat=float(chosen['lat']);lon=float(chosen['lon'])
        except (TypeError,ValueError,KeyError):reasons.append('invalid_coordinates');lat=lon=None
        if lat is not None and not inside(lat,lon):reasons.append('outside_pl_boundary')
        if lat is not None:
            same=[r for r in existing_names.get(norm(item.get('name')),[]) if r['stable_id']!=item.get('stable_id')]
            if same:reasons.append('existing_exact_name:'+','.join(r['stable_id'] for r in same if r.get('stable_id')))
            near=[r for r in existing if r['stable_id']!=item.get('stable_id') and distance_m((lat,lon),(r['lat'],r['lon']))<a.near_m]
            if near:reasons.append('existing_within_%dm:%s'%(int(a.near_m),','.join(r['stable_id'] for r in near[:5] if r.get('stable_id'))))
    else:reasons.append('no_match_payload')
    row['_chosen']=chosen;row['_reasons']=reasons;row['_runtime_category']=runtime_category;rows.append(row)
for i,r in enumerate(rows):
    c=r['_chosen']
    if not c:continue
    key=(c.get('osm_type'),str(c.get('osm_id')))
    for j,s in enumerate(rows):
        if i==j or not s['_chosen']:continue
        d=s['_chosen']
        if key==(d.get('osm_type'),str(d.get('osm_id'))):r['_reasons'].append('batch_same_identity:'+str(s.get('stable_id')))
        elif norm(r.get('name')) and norm(r.get('name'))==norm(s.get('name')):r['_reasons'].append('batch_exact_name:'+str(s.get('stable_id')))
        elif r['_runtime_category']==s['_runtime_category'] and distance_m((float(c['lat']),float(c['lon'])),(float(d['lat']),float(d['lon'])))<a.near_m:r['_reasons'].append('batch_same_category_near:'+str(s.get('stable_id')))
result=[];ready=[]
for r in rows:
    reasons=sorted(set(r.pop('_reasons')));chosen=r.pop('_chosen');runtime_category=r.pop('_runtime_category');status='READY' if not reasons and runtime_category else 'REVIEW'
    out=dict(r,validation_status=status,validation_reasons=reasons,runtime_category=runtime_category,chosen=chosen);result.append(out)
    if status=='READY' and chosen:
        ready.append({'stable_id':r['stable_id'],'name':r['name'],'category':runtime_category,'source_category':r.get('source_category',''),'region':r.get('region',''),'latitude':chosen['lat'],'longitude':chosen['lon'],'source_id':'geonames:%s'%chosen.get('osm_id'),'feature_code':chosen.get('osm_value'),'verification_status':'verified_coordinate_candidate_type_and_collision'})
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
fields=['stable_id','name','category','source_category','region','latitude','longitude','source_id','feature_code','verification_status']
with a.ready_csv.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(ready)
summary=collections.Counter(x['validation_status'] for x in result);print('VALIDATION_SUMMARY '+json.dumps(summary,ensure_ascii=False));print('READY_COUNT',len(ready))
for x in result:
    if x['validation_status']=='READY':print('READY',x['stable_id'],x['name'],x['runtime_category'],(x.get('chosen') or {}).get('osm_value'))
    elif x.get('chosen'):print('REVIEW',x['stable_id'],x['name'],' | '.join(x['validation_reasons']))
