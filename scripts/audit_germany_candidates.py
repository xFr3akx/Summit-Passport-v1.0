import json,math,unicodedata,re,collections,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[1];folder=Path(sys.argv[1]) if len(sys.argv)>1 else repo/'../../work/germany061'
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s.lower().replace('ß','ss').replace('ł','l')).encode('ascii','ignore').decode())
def distance(a,b):return math.hypot((a[0]-b[0])*111195,(a[1]-b[1])*111195*math.cos(math.radians((a[0]+b[0])/2)))
def fits(category,p):
 k,v=p.get('osm_key'),p.get('osm_value')
 return {'peak':k=='natural' and v=='peak','castle':(k=='historic' and v in ['castle','ruins','manor']) or (k=='building' and v in ['castle','historic','yes','civic','manor']),'water':(k=='natural' and v=='water') or (k=='water' and v in ['lake','pond','reservoir']) or (k=='landuse' and v=='reservoir'),'heritage':(k=='historic' and v in ['monument','memorial','archaeological_site']) or (k=='tourism' and v in ['museum','attraction']),'nature':k in ['leisure','boundary'] and v in ['park','nature_reserve','national_park','protected_area'],'lighthouse':v=='lighthouse','cave':v=='cave_entrance','waterfall':v=='waterfall'}.get(category,False)
def ring_contains(x,y,ring):
 inside=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
boundary=json.loads((repo/'app/src/main/assets/ui/boundaries.json').read_text(encoding='utf-8'))['DE'];polygons=boundary['coordinates'] if boundary['type']=='MultiPolygon' else [boundary['coordinates']]
def inside(lat,lon):return any(ring_contains(lon,lat,p[0]) and not any(ring_contains(lon,lat,h) for h in p[1:]) for p in polygons)
catalog=json.loads((repo/'data/catalog_runtime_060.json').read_text(encoding='utf-8'))['places'];old=[p for p in catalog if p['country']=='DE' and p['mapReady']]
rows={r['geonamesId']:r for r in json.loads((folder/'candidates.json').read_text(encoding='utf-8'))};matched={r['geonamesId']:r for r in json.loads((folder/'cached_matches.json').read_text(encoding='utf-8'))};rejected=[]
for file in (folder/'queries').glob('*.json'):
 raw=json.loads(file.read_text(encoding='utf-8'));row=rows[raw['geonamesId']];candidates={}
 for f in raw['response'].get('features',[]):
  p=f['properties'];lon,lat=f['geometry']['coordinates']
  if p.get('countrycode','').upper()!='DE' or not fits(row['category'],p) or norm(p.get('name','')) not in row['aliases'] :continue
  state=p.get('state');state={'Freie Hansestadt Bremen':'Bremen','Freie und Hansestadt Hamburg':'Hamburg'}.get(state,state)
  if state!=row['region'] and not (not state and row['region'] in ['Berlin','Hamburg'] and any(row['region'].lower() in str(p.get(k,'')).lower() for k in ['city','district','county','name'])):continue
  if distance((lat,lon),(row['lat'],row['lon']))>500:continue
  candidates[(p['osm_type'],p['osm_id'])]=f
 if len(candidates)==1:matched[row['geonamesId']]=dict(row,osm=next(iter(candidates.values())),retrievedOn=raw['retrievedOn'],query=raw['query'],method='Photon exact canonical/alternate name, matching feature category, German state and country; GeoNames position within 500 m')
 else:rejected.append({'geonamesId':row['geonamesId'],'name':row['name'],'reason':'no unambiguous name/type/state/country/coordinate match'})
# Reuse additional named results from the same queries with the same strict checks.
alias_index=collections.defaultdict(list)
identities=collections.defaultdict(set)
for id,row in matched.items():identities[id].add((row['osm']['properties']['osm_type'],row['osm']['properties']['osm_id']))
for row in rows.values():
 for alias in row['aliases']:alias_index[alias].append(row)
for file in (folder/'queries').glob('*.json'):
 raw=json.loads(file.read_text(encoding='utf-8'))
 for f in raw['response'].get('features',[]):
  p=f['properties'];lon,lat=f['geometry']['coordinates'];state={'Freie Hansestadt Bremen':'Bremen','Freie und Hansestadt Hamburg':'Hamburg'}.get(p.get('state'),p.get('state'))
  for row in alias_index.get(norm(p.get('name','')),[]):
   if p.get('countrycode','').upper()!='DE' or not fits(row['category'],p):continue
   if state!=row['region'] and not (not state and row['region'] in ['Berlin','Hamburg'] and any(row['region'].lower() in str(p.get(k,'')).lower() for k in ['city','district','county','name'])):continue
   if distance((lat,lon),(row['lat'],row['lon']))>500:continue
   identities[row['geonamesId']].add((p['osm_type'],p['osm_id']))
   if row['geonamesId'] in matched:continue
   matched[row['geonamesId']]=dict(row,osm=f,retrievedOn=raw['retrievedOn'],query=raw['query'],method='Named additional Photon result; exact GeoNames canonical/alternate name, matching type/state/country, coordinates within 500 m')
for id,ids in identities.items():
 if len(ids)>1:
  matched.pop(id,None);rejected.append({'geonamesId':id,'name':rows[id]['name'],'reason':'multiple nearby same-name OSM identities'})
# Exclude duplicate source IDs, close points, border-mask mismatches and near homonyms.
accepted=[];osm_ids=set()
for r in sorted(matched.values(),key=lambda p:(p['regionCode'],p['category'],-len(p['aliases']),p['name'])):
 lon,lat=r['osm']['geometry']['coordinates'];osm=r['osm']['properties'];key=(osm['osm_type'],osm['osm_id'])
 reason=None
 if key in osm_ids:reason='same OSM feature'
 elif not inside(lat,lon):reason='outside application country polygon'
 elif any(distance((lat,lon),(p['lat'],p['lon']))<400 for p in old):reason='within 400 m of an existing point'
 elif any(distance((lat,lon),(p['osm']['geometry']['coordinates'][1],p['osm']['geometry']['coordinates'][0]))<400 or (set(r['aliases'])&set(p['aliases']) and distance((lat,lon),(p['osm']['geometry']['coordinates'][1],p['osm']['geometry']['coordinates'][0]))<10000) for p in accepted):reason='duplicate or nearby same-name candidate'
 if reason:rejected.append({'geonamesId':r['geonamesId'],'name':r['name'],'reason':reason});continue
 accepted.append(r);osm_ids.add(key)
(folder/'accepted.json').write_text(json.dumps(accepted,ensure_ascii=False),encoding='utf-8');(folder/'rejected.json').write_text(json.dumps(rejected,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'queried':len(list((folder/'queries').glob('*.json'))),'accepted':len(accepted),'categories':dict(collections.Counter(p['category'] for p in accepted)),'states':dict(collections.Counter(p['regionCode'] for p in accepted))},ensure_ascii=False))
