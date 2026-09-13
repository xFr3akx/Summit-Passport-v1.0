#!/usr/bin/env python3
"""Cross-check READY Poland GeoNames candidates against nearby OSM features.

Each candidate gets its own Overpass around-query, so large ways/relations are
validated by geometry intersecting the search radius rather than by the distance
to their geometric centre. Catalog files are never edited.
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
    if category=='nature': return tags.get('boundary') in {'protected_area','national_park'} or tags.get('leisure') in {'nature_reserve','park'} or natural in {'wood','heath','wetland','valley'}
    if category=='viewpoint': return tourism=='viewpoint'
    if category=='heritage': return tourism=='museum' or historic in {'memorial','monument','archaeological_site','building'}
    if category=='lighthouse': return tags.get('man_made')=='lighthouse' or historic=='lighthouse'
    if category=='castle': return historic in {'castle','fort','ruins','manor'} or tags.get('castle_type') is not None
    return False

def aliases(tags):
    vals=[]
    for key in ('name','name:pl','official_name','alt_name','short_name'):
        raw=tags.get(key)
        if raw:
            vals.extend(str(raw).split(';'))
    return {norm(v) for v in vals if norm(v)}

def overpass_one(row,radius):
    lat=float(row['latitude']);lon=float(row['longitude'])
    q=f'[out:json][timeout:35];nwr(around:{radius},{lat:.7f},{lon:.7f})["name"];out center tags;'
    data=urllib.parse.urlencode({'data':q}).encode();last=None
    for endpoint in ENDPOINTS:
        try:
            req=urllib.request.Request(endpoint,data=data,headers={'User-Agent':'SummitPassportCatalogAudit/1.0'})
            with urllib.request.urlopen(req,timeout=45) as resp:return json.load(resp),endpoint
        except Exception as e:
            last=e;time.sleep(.5)
    raise last

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
p.add_argument('--delay',type=float,default=.15)
a=p.parse_args()
rows=list(csv.DictReader(a.input.open(encoding='utf-8-sig')))
results=[];cross=[];query_errors=[]
for index,r in enumerate(rows,1):
    target=norm(r['name']);category=r['category'];origin=(float(r['latitude']),float(r['longitude']))
    matches=[];endpoint=None
    try:
        raw,endpoint=overpass_one(r,a.radius)
        for e in raw.get('elements',[]):
            tags=e.get('tags') or {};pt=element_point(e)
            if target not in aliases(tags) or not fits(category,tags):continue
            centre_distance=round(distance_m(origin,pt),1) if pt else None
            matches.append({'type':e['type'],'id':e['id'],'name':tags.get('name',''),'lat':pt[0] if pt else None,'lon':pt[1] if pt else None,'centre_distance_m':centre_distance,'tags':tags,'url':osm_url(e)})
    except Exception as e:
        query_errors.append({'stable_id':r['stable_id'],'name':r['name'],'error':type(e).__name__})
    identities={(m['type'],m['id']) for m in matches}
    status='CROSS_CHECKED' if len(identities)==1 else 'REVIEW'
    if status=='CROSS_CHECKED':reason='one exact/alias normalized-name + category OSM identity returned by candidate-specific around query'
    elif not identities:reason='no compatible OSM identity' if not any(x['stable_id']==r['stable_id'] for x in query_errors) else 'Overpass query failed'
    else:reason=f'{len(identities)} compatible OSM identities'
    result=dict(r,status=status,reason=reason,matches=matches,overpass_endpoint=endpoint,search_radius_m=a.radius);results.append(result)
    if status=='CROSS_CHECKED':
        m=matches[0]
        cross.append(dict(r,osm_url=m['url'],osm_type=m['type'],osm_id=m['id'],osm_latitude=m['lat'],osm_longitude=m['lon'],centre_distance_m=m['centre_distance_m'],search_radius_m=a.radius,proximity_basis='candidate_specific_overpass_around_geometry',verification_status='cross_checked_osm_geonames'))
    print(f'{index:03d}/{len(rows)} {status} {r["name"]} {reason}')
    time.sleep(a.delay)
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps({'query_errors':query_errors,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if rows:
    fields=[k for k in rows[0].keys() if k!='verification_status']+['osm_url','osm_type','osm_id','osm_latitude','osm_longitude','centre_distance_m','search_radius_m','proximity_basis','verification_status']
    with a.crosschecked_csv.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cross)
else:a.crosschecked_csv.write_text('',encoding='utf-8')
print(json.dumps({'input':len(rows),'cross_checked':len(cross),'review':len(rows)-len(cross),'query_errors':query_errors},ensure_ascii=False))
