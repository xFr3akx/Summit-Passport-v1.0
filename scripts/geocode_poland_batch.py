#!/usr/bin/env python3
import argparse,csv,json,pathlib,re,time,unicodedata,urllib.parse,urllib.request

def norm(s):
 s=unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','',s)
def query(name):
 url='https://photon.komoot.io/api/?'+urllib.parse.urlencode({'q':name+', Polska','limit':8,'lang':'pl'});req=urllib.request.Request(url,headers={'User-Agent':'SummitPassportCatalogAudit/1.0'})
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
p=argparse.ArgumentParser();p.add_argument('input',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--delay',type=float,default=.25);p.add_argument('--allow-live',action='store_true');a=p.parse_args()
rows=list(csv.DictReader(a.input.open(encoding='utf-8-sig')));out=[]
for i,row in enumerate(rows,1):
 name=row['name'];cat=row['category'];source_cat=row.get('source_category','');status='REVIEW';reason='no offline coordinate candidate';matches=[];lat=row.get('latitude','').strip();lon=row.get('longitude','').strip();meta={}
 try:meta=json.loads(row.get('notes') or '{}')
 except Exception:meta={}
 geonames_id=str(meta.get('geonames_id') or '').strip();feature_code=str(meta.get('feature_code') or '').strip()
 if lat and lon and geonames_id:
  try:
   matches=[{'name':name,'lat':float(lat),'lon':float(lon),'osm_type':'GEONAMES','osm_id':geonames_id,'osm_key':'geonames','osm_value':feature_code,'state':row.get('region',''),'county':None,'city':None}];status='CANDIDATE';reason='existing GeoNames coordinate_candidate from catalog_working'
  except ValueError:reason='invalid offline coordinate_candidate'
 elif a.allow_live:
  try:
   raw=query(name)
   for f in raw.get('features',[]):
    prop=f.get('properties',{});coords=f.get('geometry',{}).get('coordinates',[])
    if len(coords)<2 or prop.get('countrycode','').upper()!='PL':continue
    pname=prop.get('name','')
    if not pname:continue
    similarity=1 if norm(pname)==norm(name) else (0.8 if norm(name) in norm(pname) or norm(pname) in norm(name) else 0)
    if similarity<0.8:continue
    matches.append({'name':pname,'lat':coords[1],'lon':coords[0],'osm_type':prop.get('osm_type'),'osm_id':prop.get('osm_id'),'osm_key':prop.get('osm_key'),'osm_value':prop.get('osm_value'),'state':prop.get('state'),'county':prop.get('county'),'city':prop.get('city')})
   identities={(m['osm_type'],m['osm_id']) for m in matches}
   if len(identities)==1:status='CANDIDATE';reason='one matching PL OSM identity by name'
   elif len(identities)>1:reason=f'{len(identities)} matching OSM identities require review'
  except Exception as e:reason='query error: '+type(e).__name__
 out.append({'stable_id':row['stable_id'],'name':name,'category':cat,'source_category':source_cat,'region':row.get('region',''),'status':status,'reason':reason,'matches':matches})
 print(f'{i:03d}/{len(rows)} {status} {name} - {reason}')
 if a.allow_live and not (lat and lon and geonames_id):time.sleep(a.delay)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
from collections import Counter
print('SUMMARY '+json.dumps(Counter(x['status'] for x in out),ensure_ascii=False))
