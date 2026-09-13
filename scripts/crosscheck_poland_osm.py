#!/usr/bin/env python3
"""Cross-check READY Poland GeoNames candidates against nearby OSM features.

A record is CROSS_CHECKED only when a single nearby OSM identity has an exact
normalized name and a category-compatible OSM tag. Failed Overpass batches are
recursively split down to individual records. Catalog files are never edited.
"""
import argparse,csv,json,math,pathlib,re,time,unicodedata,urllib.parse,urllib.request

ENDPOINTS=(
    'https://overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
)

def norm(value):
    s=unicodedata.normalize('NFKD',str(value or '')).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','',s)

def distance_m(a,b):
    lat1,lon1=a;lat2,lon2=b
    x=math.radians(lon2-lon1)*math.cos(math.radians((lat1+lat2)/2))
    y=math.radians(lat2-lat1)
    return 6371000*math.hypot(x,y)

def fits(category,tags):
    natural=tags.get('natural');historic=tags.get('historic');tourism=tags.get('tourism')
    if category=='peak': return natural=='peak'
    if category=='pass': return tags.get('mountain_pass')=='yes' or natural=='saddle'
    if category=='water': return natural=='water' or tags.get('water') in {'lake','reservoir','pond'} or tags.get('landuse')=='reservoir'
    if category=='waterfall': return natural=='waterfall' or tags.get('waterway')=='waterfall'
    if category=='cave': return natural=='cave_entrance'
    if category=='rock': return natural in {'rock','stone','cliff'} or tags.get('geological')=='geological_site'
    if category=='nature': return tags.get('boundary') in {'protected_area','national_park'} or tags.get('leisure') in {'nature_reserve','park'} or natural in {'wood','heath','wetland'}
    if category=='viewpoint': return tourism=='viewpoint'
    if category=='heritage': return tourism=='museum' or historic in {'memorial','monument','archaeological_site','building'}
    if category=='lighthouse': return tags.get('man_made')=='lighthouse' or historic=='lighthouse'
    if category=='castle': return historic in {'castle','fort','ruins','manor'} or tags.get('castle_type') is not None
    return False

def overpass(rows,radius):
    parts=[f'nwr(around:{radius},{float(r["latitude"]):.7f},{float(r["longitude"]):.7f})["name"];' for r in rows]
    q='[out:json][timeout:60];('+''.join(parts)+');out center tags;'
    data=urllib.parse.urlencode({'data':q}).encode()
    last=None
    for endpoint in ENDPOINTS:
        try:
            req=urllib.request.Request(endpoint,data=data,headers={'User-Agent':'SummitPassportCatalogAudit/1.0'})
            with urllib.request.urlopen(req,timeout=90) as resp:return json.load(resp),endpoint
        except Exception as e:
            last=e;time.sleep(1)
    raise last

def fetch_resilient(batch,radius,label,errors):
    try:
        raw,endpoint=overpass(batch,radius)
        print(f'OVERPASS {label} endpoint={endpoint} elements={len(raw.get("elements",[]))}')
        return raw.get('elements',[])
    except Exception as e:
        if len(batch)>1:
            mid=len(batch)//2
            print(f'OVERPASS_SPLIT {label} {type(e).__name__} count={len(batch)}')
            return fetch_resilient(batch[:mid],radius,label+'a',errors)+fetch_resilient(batch[mid:],radius,label+'b',errors)
        errors.append({'stable_id':batch[0].get('stable_id'),'name':batch[0].get('name'),'error':type(e).__name__})
        print(f'OVERPASS_ERROR {label} {batch[0].get("name")} {type(e).__name__}')
        return []

def element_point(e):
    if 'lat' in e and 'lon' in e:return float(e['lat']),float(e['lon'])
    c=e.get('center') or {}
    if 'lat' in c and 'lon' in c:return float(c['lat']),float(c['lon'])
    return None

def osm_url(e):
    kind={'node':'node','way':'way','relation':'relation'}.get(e.get('type'))
    return f'https://www.openstreetmap.org/{kind}/{e.get("id")}' if kind and e.get('id') is not None else None

p=argparse.ArgumentParser()
p.add_argument('input',type=pathlib.Path)
p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--crosschecked-csv',type=pathlib.Path,required=True)
p.add_argument('--radius',type=int,default=500)
p.add_argument('--batch-size',type=int,default=10)
a=p.parse_args()
rows=list(csv.DictReader(a.input.open(encoding='utf-8-sig')))
all_elements=[];query_errors=[]
for start in range(0,len(rows),a.batch_size):
    batch=rows[start:start+a.batch_size]
    all_elements.extend(fetch_resilient(batch,a.radius,f'{start+1}-{start+len(batch)}',query_errors))
unique={(e.get('type'),e.get('id')):e for e in all_elements if e.get('type') and e.get('id') is not None}
elements=list(unique.values())
results=[];cross=[]
for r in rows:
    origin=(float(r['latitude']),float(r['longitude']));target=norm(r['name']);category=r['category']
    matches=[]
    for e in elements:
        pt=element_point(e);tags=e.get('tags') or {};name=tags.get('name','')
        if not pt or distance_m(origin,pt)>a.radius:continue
        if norm(name)!=target or not fits(category,tags):continue
        matches.append({'type':e['type'],'id':e['id'],'name':name,'lat':pt[0],'lon':pt[1],'distance_m':round(distance_m(origin,pt),1),'tags':tags,'url':osm_url(e)})
    identities={(m['type'],m['id']) for m in matches}
    status='CROSS_CHECKED' if len(identities)==1 else 'REVIEW'
    reason='one exact normalized-name + category OSM identity within radius' if status=='CROSS_CHECKED' else ('no compatible OSM identity' if not identities else f'{len(identities)} compatible OSM identities')
    result=dict(r,status=status,reason=reason,matches=matches);results.append(result)
    if status=='CROSS_CHECKED':
        m=matches[0]
        cross.append(dict(r,osm_url=m['url'],osm_type=m['type'],osm_id=m['id'],osm_latitude=m['lat'],osm_longitude=m['lon'],distance_m=m['distance_m'],verification_status='cross_checked_osm_geonames'))
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps({'query_errors':query_errors,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if rows:
    fields=[k for k in rows[0].keys() if k!='verification_status']+['osm_url','osm_type','osm_id','osm_latitude','osm_longitude','distance_m','verification_status']
    with a.crosschecked_csv.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cross)
else:
    a.crosschecked_csv.write_text('',encoding='utf-8')
print(json.dumps({'input':len(rows),'cross_checked':len(cross),'review':len(rows)-len(cross),'query_errors':query_errors},ensure_ascii=False))
for x in results:print(x['status'],x['name'],x['reason'])
