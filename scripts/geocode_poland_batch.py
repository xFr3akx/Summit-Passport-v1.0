#!/usr/bin/env python3
import argparse,csv,json,pathlib,re,time,unicodedata,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]

def norm(s):
 s=unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','',s)

def fits(category,p):
 k=p.get('osm_key');v=p.get('osm_value')
 rules={
  'peak': k=='natural' and v=='peak',
  'pass': k in ('mountain_pass','natural') and v in ('yes','saddle'),
  'castle': (k=='historic' and v in ('castle','ruins','manor')) or (k=='building' and v in ('castle','historic','manor')),
  'waterfall': v=='waterfall',
  'cave': v=='cave_entrance',
  'rock': (k=='natural' and v in ('rock','stone','cliff')) or (k=='geological','geological_site'),
  'water': (k=='natural' and v=='water') or k=='water' or (k=='landuse' and v=='reservoir'),
  'nature': (k in ('leisure','boundary') and v in ('park','nature_reserve','national_park','protected_area')),
  'viewpoint': k=='tourism' and v=='viewpoint',
  'heritage': k in ('historic','tourism'),
  'lighthouse': v=='lighthouse',
  'industrial': k in ('man_made','industrial','historic'),
  'underground': v in ('mine','adit','cave_entrance'),
  'memory': k=='historic' and v in ('memorial','monument'),
  'trail': k in ('route','highway','tourism'),
 }
 return rules.get(category,True)

def query(name):
 url='https://photon.komoot.io/api/?'+urllib.parse.urlencode({'q':name+', Polska','limit':8,'lang':'pl'})
 req=urllib.request.Request(url,headers={'User-Agent':'SummitPassportCatalogAudit/1.0'})
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)

p=argparse.ArgumentParser();p.add_argument('input',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--delay',type=float,default=.25);a=p.parse_args()
rows=list(csv.DictReader(a.input.open(encoding='utf-8-sig')));out=[]
for i,row in enumerate(rows,1):
 name=row['name'];cat=row['category'];status='REVIEW';reason='no unambiguous Photon/OSM match';matches=[]
 try:
  raw=query(name)
  for f in raw.get('features',[]):
   prop=f.get('properties',{});coords=f.get('geometry',{}).get('coordinates',[])
   if len(coords)<2 or prop.get('countrycode','').upper()!='PL':continue
   pname=prop.get('name','')
   if not pname or not fits(cat,prop):continue
   similarity=1 if norm(pname)==norm(name) else (0.8 if norm(name) in norm(pname) or norm(pname) in norm(name) else 0)
   if similarity<0.8:continue
   matches.append({'name':pname,'lat':coords[1],'lon':coords[0],'osm_type':prop.get('osm_type'),'osm_id':prop.get('osm_id'),'osm_key':prop.get('osm_key'),'osm_value':prop.get('osm_value'),'state':prop.get('state'),'county':prop.get('county'),'city':prop.get('city')})
  identities={(m['osm_type'],m['osm_id']) for m in matches}
  if len(identities)==1:
   m=matches[0];status='CANDIDATE';reason='one matching PL OSM identity by name and category'
  elif len(identities)>1:reason=f'{len(identities)} matching OSM identities require review'
 except Exception as e:reason='query error: '+type(e).__name__
 out.append({'stable_id':row['stable_id'],'name':name,'category':cat,'region':row.get('region',''),'status':status,'reason':reason,'matches':matches})
 print(f'{i:03d}/{len(rows)} {status} {name}')
 time.sleep(a.delay)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
from collections import Counter
print('SUMMARY '+json.dumps(Counter(x['status'] for x in out),ensure_ascii=False))
