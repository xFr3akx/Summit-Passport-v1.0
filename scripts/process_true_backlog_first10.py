#!/usr/bin/env python3
"""Process the first 10 *true* unresolved PL+DE runtime records.

Runtime catalog is authoritative: a record is included only when catalog_working says
not map_ready AND app catalog says mapReady=false. Produces staging only; production
files are never overwritten.
"""
import collections,csv,datetime,difflib,json,math,pathlib,re,time,unicodedata,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
PHOTON='https://photon.komoot.io/api/'
NOMINATIM='https://nominatim.openstreetmap.org/search'
OVERPASS=('https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter','https://overpass.nchc.org.tw/api/interpreter')
CFG={'PL':('Polska','pl'),'DE':('Deutschland','de')}
ALLOWED={'peak','pass','water','waterfall','cave','rock','nature','viewpoint','heritage','lighthouse','castle','industrial'}

def norm(v):
 s=str(v or '').replace('ß','ss').replace('ł','l');s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','',s)
def toks(v):
 s=unicodedata.normalize('NFKD',str(v or '')).encode('ascii','ignore').decode().lower();return [x for x in re.findall(r'[a-z0-9]+',s) if x not in {'w','we','na','nad','pod','i','im','der','die','das','am','an','in','zu','zum','zur','unesco'}]
def score(a,b):
 na,nb=norm(a),norm(b)
 if not na or not nb:return 0
 if na==nb:return 1
 if min(len(na),len(nb))>=7 and (na in nb or nb in na):return .92
 wa,wb=set(toks(a)),set(toks(b));jac=len(wa&wb)/max(1,len(wa|wb));seq=difflib.SequenceMatcher(None,' '.join(toks(a)),' '.join(toks(b))).ratio();return max(jac,seq)
def dist(a,b):
 lat1,lon1=a;lat2,lon2=b;x=math.radians(lon2-lon1)*math.cos(math.radians((lat1+lat2)/2));y=math.radians(lat2-lat1);return 6371000*math.hypot(x,y)
def ring_contains(x,y,ring):
 inside=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
def make_inside(boundaries,code):
 g=boundaries[code];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
 return lambda lat,lon:any(ring_contains(lon,lat,p[0]) and not any(ring_contains(lon,lat,h) for h in p[1:]) for p in polys)
def osm_url(t,i):
 k={'N':'node','W':'way','R':'relation','node':'node','way':'way','relation':'relation'}.get(str(t));return f'https://www.openstreetmap.org/{k}/{i}' if k and i is not None else None
def fits(cat,key='',value='',tags=None):
 tags=tags or {};key=str(key or '');value=str(value or '');natural=tags.get('natural') or (value if key=='natural' else '');historic=tags.get('historic') or (value if key=='historic' else '');tourism=tags.get('tourism') or (value if key=='tourism' else '')
 if cat=='peak':return natural=='peak'
 if cat=='pass':return natural=='saddle' or tags.get('mountain_pass')=='yes'
 if cat=='water':return natural=='water' or value in {'lake','reservoir','pond'} or tags.get('water') in {'lake','reservoir','pond'} or tags.get('landuse')=='reservoir'
 if cat=='waterfall':return natural=='waterfall' or tags.get('waterway')=='waterfall' or value=='waterfall'
 if cat=='cave':return natural=='cave_entrance' or value=='cave_entrance'
 if cat=='rock':return natural in {'rock','stone','cliff'} or value in {'rock','stone','cliff','geological_site'}
 if cat=='nature':return tags.get('boundary') in {'protected_area','national_park'} or value in {'protected_area','national_park','nature_reserve','park','wood','heath','wetland','valley','scrub'} or natural in {'wood','heath','wetland','valley','scrub'}
 if cat=='viewpoint':return tourism=='viewpoint' or value=='viewpoint'
 if cat=='heritage':return bool(historic) or tourism in {'museum','attraction'} or key=='heritage' or value in {'museum','attraction','monument','memorial','archaeological_site'}
 if cat=='lighthouse':return tags.get('man_made')=='lighthouse' or historic=='lighthouse' or value=='lighthouse'
 if cat=='castle':return historic in {'castle','fort','ruins','manor'} or value in {'castle','fort','ruins','manor'} or bool(tags.get('castle_type'))
 if cat=='industrial':return tags.get('man_made') in {'works','mine','adit','mineshaft','chimney','kiln'} or value in {'works','mine','adit','mineshaft','chimney','kiln'} or key=='industrial'
 return False
def request(url,data=None,timeout=35,attempts=4):
 last=None
 for n in range(attempts):
  try:
   req=urllib.request.Request(url,data=data,headers={'User-Agent':'SummitPassportCatalogAudit/3.0 first10'})
   with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
  except Exception as e:last=e;time.sleep(min(5,1.0*(2**n)))
 raise last
def photon(name,country,cat):
 q,lang=CFG[country];url=PHOTON+'?'+urllib.parse.urlencode({'q':f'{name}, {q}','limit':12,'lang':lang});raw=request(url,timeout=30)
 out={}
 for f in raw.get('features',[]):
  p=f.get('properties') or {};c=(f.get('geometry') or {}).get('coordinates') or []
  if len(c)<2 or str(p.get('countrycode') or '').upper()!=country or score(name,p.get('name'))<.78 or not fits(cat,p.get('osm_key'),p.get('osm_value'),p):continue
  u=osm_url(p.get('osm_type'),p.get('osm_id'))
  if u:out[u]={'name':p.get('name'),'lat':float(c[1]),'lon':float(c[0]),'osm_type':{'N':'node','W':'way','R':'relation'}.get(str(p.get('osm_type')),str(p.get('osm_type'))),'osm_id':p.get('osm_id'),'source':u,'name_score':score(name,p.get('name')),'method':'photon'}
 return list(out.values())
def nominatim(name,country,cat):
 cc={'PL':'pl','DE':'de'}[country];url=NOMINATIM+'?'+urllib.parse.urlencode({'q':name,'countrycodes':cc,'format':'jsonv2','limit':10,'addressdetails':1,'namedetails':1});raw=request(url,timeout=30)
 out={}
 for p in raw:
  pname=(p.get('namedetails') or {}).get('name') or str(p.get('display_name') or '').split(',')[0]
  if score(name,pname)<.82 or not fits(cat,p.get('class'),p.get('type'),{}):continue
  u=osm_url({'node':'node','way':'way','relation':'relation'}.get(str(p.get('osm_type')).lower()),p.get('osm_id'))
  if u:out[u]={'name':pname,'lat':float(p['lat']),'lon':float(p['lon']),'osm_type':str(p.get('osm_type')).lower(),'osm_id':p.get('osm_id'),'source':u,'name_score':score(name,pname),'method':'nominatim'}
 return list(out.values())
def overpass(name,cat,lat,lon):
 q=f'[out:json][timeout:35];nwr(around:500,{lat:.7f},{lon:.7f})["name"];out center tags;';payload=urllib.parse.urlencode({'data':q}).encode();raw=None;last=None
 for ep in OVERPASS:
  try:raw=request(ep,data=payload,timeout=50,attempts=3);break
  except Exception as e:last=e
 if raw is None:raise last
 out={}
 for e in raw.get('elements',[]):
  tags=e.get('tags') or {};names=[]
  for k in ('name','name:pl','name:de','official_name','alt_name','short_name'):
   if tags.get(k):names+=str(tags[k]).split(';')
  if not names or max(score(name,x) for x in names)<.86 or not fits(cat,tags=tags):continue
  c=e.get('center') or {};plat=e.get('lat',c.get('lat',lat));plon=e.get('lon',c.get('lon',lon));u=osm_url(e.get('type'),e.get('id'))
  if u:out[u]={'name':tags.get('name') or names[0],'lat':float(plat),'lon':float(plon),'osm_type':e.get('type'),'osm_id':e.get('id'),'source':u,'name_score':max(score(name,x) for x in names),'method':'overpass_geonames'}
 return list(out.values())

def sf(v):
 try:return float(v)
 except:return None

working=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'));runtime=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'));bounds=json.loads((ROOT/'app/src/main/assets/ui/boundaries.json').read_text(encoding='utf-8'))
wrecords=working['records'];rplaces=runtime['places'];ridx={p['id']:p for p in rplaces};widx={r['stable_id']:r for r in wrecords if r.get('stable_id')};inside={c:make_inside(bounds,c) for c in CFG}
raw=[r for r in wrecords if r.get('country') in CFG and r.get('record_kind')=='place' and not r.get('map_ready') and r.get('stable_id') in ridx]
true=[r for r in raw if not ridx[r['stable_id']].get('mapReady')]
counts=collections.Counter(r['country'] for r in true);assert counts=={'PL':522,'DE':331},counts
true.sort(key=lambda r:(r.get('country',''),str((r.get('source_regions') or [''])[0]),r.get('name',''),r.get('stable_id','')));batch=true[:10];assert len(batch)==10
existing={c:[] for c in CFG};existing_osm={}
for r in wrecords:
 sid=r.get('stable_id');rp=ridx.get(sid);c=r.get('country')
 if not rp or c not in CFG or not rp.get('mapReady'):continue
 lat=sf(r.get('latitude',rp.get('lat')));lon=sf(r.get('longitude',rp.get('lon')))
 if lat is None or lon is None:continue
 rec={'stable_id':sid,'name':r.get('name',rp.get('name','')),'category':rp.get('category',''),'lat':lat,'lon':lon,'source':rp.get('source')};existing[c].append(rec)
 if str(rp.get('source') or '').startswith('https://www.openstreetmap.org/'):existing_osm[rp['source']]=rec
results=[]
for i,r in enumerate(batch,1):
 sid=r['stable_id'];rp=ridx[sid];country=r['country'];name=r.get('name') or rp.get('name');cat=rp.get('category') or r.get('category') or '';reasons=[];cand=[];origin=None
 if cat not in ALLOWED:reasons.append('unsupported_category:'+cat)
 cc=r.get('coordinate_candidate') or {};clat=sf(cc.get('latitude'));clon=sf(cc.get('longitude'));ccountry=str(cc.get('country') or country)
 if not reasons and clat is not None and clon is not None and ccountry==country:
  try:cand=overpass(name,cat,clat,clon);origin='geonames+overpass'
  except Exception as e:reasons.append('overpass_error:'+type(e).__name__)
 if not reasons and not cand:
  try:cand=photon(name,country,cat);origin='photon'
  except Exception as e:reasons.append('photon_error:'+type(e).__name__)
 if not cand:
  try:cand=nominatim(name,country,cat);origin='nominatim'
  except Exception as e:reasons.append('nominatim_error:'+type(e).__name__)
 uniq={x['source']:x for x in cand};cand=list(uniq.values());chosen=cand[0] if len(cand)==1 else None;status='REVIEW';dup=None
 if len(cand)>1:reasons.append('multiple_osm_identities:'+str(len(cand)))
 elif not cand:reasons.append('no_unambiguous_osm_identity')
 else:
  lat,lon=chosen['lat'],chosen['lon'];src=chosen['source']
  if not inside[country](lat,lon):reasons.append('outside_country_boundary')
  if src in existing_osm:status='POSSIBLE_DUPLICATE';dup=existing_osm[src]['stable_id'];reasons.append('same_osm_identity_as_existing')
  else:
   same=[e for e in existing[country] if norm(e['name'])==norm(name) and dist((lat,lon),(e['lat'],e['lon']))<15000]
   near=[e for e in existing[country] if e['category']==cat and dist((lat,lon),(e['lat'],e['lon']))<75]
   if same:status='POSSIBLE_DUPLICATE';dup=same[0]['stable_id'];reasons.append('same_name_near_existing')
   elif near:status='POSSIBLE_DUPLICATE';dup=near[0]['stable_id'];reasons.append('same_category_within_75m_existing')
   elif not reasons:status='READY'
 results.append({'index':i,'stable_id':sid,'country':country,'name':name,'category':cat,'status':status,'reasons':sorted(set(reasons)),'duplicate_of':dup,'candidate_origin':origin,'coordinate_candidate':cc or None,'candidates':cand,'chosen':chosen})
 print(f'{i:02d}/10 {country} {status} {name} :: {" | ".join(sorted(set(reasons))) if reasons else origin}')

# Batch duplicate guard.
seen={}
for x in results:
 if x['status']!='READY' or not x['chosen']:continue
 key=x['chosen']['source']
 if key in seen:x['status']='POSSIBLE_DUPLICATE';x['duplicate_of']=seen[key]['stable_id'];x['reasons'].append('batch_same_osm_identity')
 else:seen[key]=x

# Apply READY to staging copies only.
today=datetime.date.today().isoformat();changes=[]
for x in results:
 if x['status']!='READY':continue
 sid=x['stable_id'];w=widx[sid];rp=ridx[sid];c=x['chosen'];assert not w.get('map_ready') and not rp.get('mapReady')
 lat,lon=float(c['lat']),float(c['lon']);role='osm_point' if c['osm_type']=='node' else 'representative_point_not_entrance';verification='cross_checked_osm_geonames' if x['candidate_origin']=='geonames+overpass' else 'verified_osm_'+x['candidate_origin']
 w['latitude']=lat;w['longitude']=lon;w['map_ready']=True;w['verification_status']=verification;w['coordinate_role']=role;w['coordinate_source']={'url':c['source'],'provider':'OpenStreetMap','retrieved_on':today,'method':'First-10 true backlog audit; unique name/category/country-compatible OSM identity; production not overwritten.'};w['coordinate_review']='Automated staging audit; not field surveyed.'
 rp['lat']=lat;rp['lon']=lon;rp['mapReady']=True;rp['source']=c['source'];rp['coordinateRole']=role
 changes.append({'stable_id':sid,'country':x['country'],'name':x['name'],'category':x['category'],'lat':lat,'lon':lon,'source':c['source'],'verification_status':verification})
out=ROOT/'data/first10_backlog';out.mkdir(parents=True,exist_ok=True)
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(out/'catalog_working_next.json').write_text(json.dumps(working,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(out/'catalog_main_candidate.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(out/'ready_patch.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'true_backlog_total':len(true),'backlog_by_country':dict(counts),'processed':10,'status_counts':dict(collections.Counter(x['status'] for x in results)),'ready_to_stage':len(changes),'stable_ids_preserved':True,'production_catalog_overwritten':False,'records':[{'stable_id':x['stable_id'],'country':x['country'],'name':x['name'],'status':x['status'],'reasons':x['reasons'],'duplicate_of':x['duplicate_of'],'source':(x['chosen'] or {}).get('source')} for x in results]};(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SUMMARY '+json.dumps(summary,ensure_ascii=False))
