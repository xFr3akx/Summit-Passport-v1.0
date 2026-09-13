#!/usr/bin/env python3
"""Process backlog positions 11-110 with strict OSM/GeoNames cross-checking.
Production files are read-only; outputs go to data/next100_backlog/.
"""
import collections,datetime,difflib,json,math,pathlib,re,time,unicodedata,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data/next100_backlog'; OUT.mkdir(parents=True,exist_ok=True)
PHOTON='https://photon.komoot.io/api/'
NOM='https://nominatim.openstreetmap.org/search'
OVERPASS=('https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter')
COUNTRY={'PL':('Polska','pl'),'DE':('Deutschland','de')}

def norm(v):
 s=str(v or '').replace('ß','ss').replace('ł','l');s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','',s)
def toks(v):
 s=unicodedata.normalize('NFKD',str(v or '')).encode('ascii','ignore').decode().lower();return [x for x in re.findall(r'[a-z0-9]+',s) if x not in {'w','we','na','nad','pod','i','im','in','der','die','das','am','an','zu','zum','zur','unesco'}]
def sim(a,b):
 na,nb=norm(a),norm(b)
 if not na or not nb:return 0
 if na==nb:return 1
 if min(len(na),len(nb))>=6 and (na in nb or nb in na):return .93
 A,B=set(toks(a)),set(toks(b));jac=len(A&B)/max(1,len(A|B));seq=difflib.SequenceMatcher(None,' '.join(toks(a)),' '.join(toks(b))).ratio();return max(jac,seq)
def dist(a,b):
 lat1,lon1=a;lat2,lon2=b;x=math.radians(lon2-lon1)*math.cos(math.radians((lat1+lat2)/2));y=math.radians(lat2-lat1);return 6371000*math.hypot(x,y)
def osm_url(t,i):
 k={'N':'node','W':'way','R':'relation','node':'node','way':'way','relation':'relation'}.get(str(t));return f'https://www.openstreetmap.org/{k}/{i}' if k and i is not None else None
def req(url,data=None,timeout=35,tries=3):
 err=None
 for n in range(tries):
  try:
   r=urllib.request.Request(url,data=data,headers={'User-Agent':'SummitPassportCatalogAudit/4.0 next100'});return json.load(urllib.request.urlopen(r,timeout=timeout))
  except Exception as e:err=e;time.sleep(min(4,0.7*(2**n)))
 raise err

def type_ok(cat,key='',value='',tags=None):
 tags=tags or {};key=str(key or '');value=str(value or '')
 n=tags.get('natural') or (value if key=='natural' else '');h=tags.get('historic') or (value if key=='historic' else '');t=tags.get('tourism') or (value if key=='tourism' else '');mm=tags.get('man_made') or (value if key=='man_made' else '')
 if cat=='peak':return n=='peak'
 if cat=='pass':return n=='saddle' or tags.get('mountain_pass')=='yes'
 if cat=='water':return n=='water' or tags.get('water') in {'lake','reservoir','pond'} or value in {'lake','reservoir','pond','water'} or tags.get('landuse')=='reservoir'
 if cat=='waterfall':return n=='waterfall' or tags.get('waterway')=='waterfall' or value=='waterfall'
 if cat=='cave':return n=='cave_entrance' or value=='cave_entrance'
 if cat=='rock':return n in {'rock','stone','cliff','peak'} or value in {'rock','stone','cliff','geological_site','peak'}
 if cat=='viewpoint':return t=='viewpoint' or value=='viewpoint'
 if cat=='lighthouse':return mm=='lighthouse' or h=='lighthouse' or value=='lighthouse'
 if cat=='castle':return h in {'castle','fort','ruins','manor'} or value in {'castle','fort','ruins','manor'} or bool(tags.get('castle_type'))
 if cat=='heritage':return bool(h) or t in {'museum','attraction'} or key=='heritage' or value in {'museum','attraction','monument','memorial','archaeological_site','ruins'}
 if cat=='industrial':return mm in {'works','mine','adit','mineshaft','chimney','kiln'} or key=='industrial' or value in {'works','mine','adit','mineshaft','chimney','kiln'}
 if cat=='nature':return key in {'natural','leisure','boundary','place','tourism','bridge','waterway'} or value in {'nature_reserve','protected_area','national_park','wood','heath','wetland','valley','viewpoint','attraction','locality','bridge','gorge'}
 return False

def photon(q,country,cat):
 cn,lang=COUNTRY[country];url=PHOTON+'?'+urllib.parse.urlencode({'q':q+', '+cn,'limit':12,'lang':lang});raw=req(url,timeout=30);out={}
 for f in raw.get('features',[]):
  p=f.get('properties') or {};co=(f.get('geometry') or {}).get('coordinates') or []
  if len(co)<2 or str(p.get('countrycode') or '').upper()!=country:continue
  name=p.get('name') or '';s=sim(q.split(',')[0],name)
  if s<.80 or not type_ok(cat,p.get('osm_key'),p.get('osm_value'),p):continue
  u=osm_url(p.get('osm_type'),p.get('osm_id'))
  if u:out[u]={'name':name,'lat':float(co[1]),'lon':float(co[0]),'source':u,'osm_type':{'N':'node','W':'way','R':'relation'}.get(str(p.get('osm_type')),str(p.get('osm_type'))),'osm_id':p.get('osm_id'),'score':round(s,3),'engine':'photon','context':[p.get('city'),p.get('county'),p.get('state')]}
 return out

def nominatim(name,country,cat):
 url=NOM+'?'+urllib.parse.urlencode({'q':name,'countrycodes':country.lower(),'format':'jsonv2','limit':10,'addressdetails':1,'namedetails':1});raw=req(url,timeout=30);out={}
 for p in raw:
  nm=(p.get('namedetails') or {}).get('name') or str(p.get('display_name') or '').split(',')[0];s=sim(name,nm)
  if s<.82 or not type_ok(cat,p.get('class'),p.get('type'),{}):continue
  u=osm_url(str(p.get('osm_type')).lower(),p.get('osm_id'))
  if u:out[u]={'name':nm,'lat':float(p['lat']),'lon':float(p['lon']),'source':u,'osm_type':str(p.get('osm_type')).lower(),'osm_id':p.get('osm_id'),'score':round(s,3),'engine':'nominatim','context':[str(p.get('display_name') or '')]}
 return out

def overpass(name,cat,lat,lon):
 q=f'[out:json][timeout:30];nwr(around:700,{lat:.7f},{lon:.7f})["name"];out center tags;';data=urllib.parse.urlencode({'data':q}).encode();raw=None;err=None
 for ep in OVERPASS:
  try:raw=req(ep,data=data,timeout=45,tries=2);break
  except Exception as e:err=e
 if raw is None:raise err
 out={}
 for e in raw.get('elements',[]):
  tags=e.get('tags') or {};names=[]
  for k in ('name','name:de','name:pl','official_name','alt_name','short_name'):
   if tags.get(k):names+=str(tags[k]).split(';')
  if not names:continue
  sc=max(sim(name,x) for x in names)
  if sc<.86 or not type_ok(cat,tags=tags):continue
  c=e.get('center') or {};u=osm_url(e.get('type'),e.get('id'))
  if u:out[u]={'name':tags.get('name') or names[0],'lat':float(e.get('lat',c.get('lat',lat))),'lon':float(e.get('lon',c.get('lon',lon))),'source':u,'osm_type':e.get('type'),'osm_id':e.get('id'),'score':round(sc,3),'engine':'overpass_geonames','context':[]}
 return out

def sf(x):
 try:return float(x)
 except:return None

working=json.loads((ROOT/'data/catalog_working.json').read_text(encoding='utf-8'));runtime=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'));g64=json.loads((ROOT/'data/germany_completion_064.json').read_text(encoding='utf-8'));first=json.loads((ROOT/'data/first10_backlog/decisions.json').read_text(encoding='utf-8'))
wrecords=working['records'];rplaces=runtime['places'];widx={r['stable_id']:r for r in wrecords if r.get('stable_id')};ridx={r['id']:r for r in rplaces}
dup_ids={r['id'] for r in g64.get('duplicates',[]) if r.get('status')=='duplicate'}
# tolerate schema where duplicate rows live under another list
for key,val in g64.items():
 if isinstance(val,list):
  for r in val:
   if isinstance(r,dict) and r.get('status')=='duplicate' and r.get('duplicateOf'):dup_ids.add(r.get('id'))
assert len(dup_ids)==12,len(dup_ids)
back=[r for r in wrecords if r.get('country') in COUNTRY and r.get('record_kind')=='place' and not r.get('map_ready') and r.get('stable_id') in ridx and not ridx[r['stable_id']].get('mapReady') and r.get('stable_id') not in dup_ids]
back.sort(key=lambda r:(r.get('country',''),str((r.get('source_regions') or [''])[0]),r.get('name',''),r.get('stable_id','')))
assert collections.Counter(r['country'] for r in back)=={'PL':522,'DE':331}
batch=back[10:110];assert len(batch)==100
selection=[]
for i,r in enumerate(batch,11):
 rp=ridx[r['stable_id']];selection.append({'index':i,'stable_id':r['stable_id'],'country':r['country'],'name':r.get('name') or rp.get('name'),'category':rp.get('category') or r.get('category'),'area':rp.get('area') or str((r.get('source_regions') or [''])[0]),'source_ids':r.get('source_ids') or [],'coordinate_candidate':r.get('coordinate_candidate')})
(OUT/'selection.json').write_text(json.dumps({'backlog_total':853,'slice':'11-110','records':selection},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# mapped-reference index from runtime
mapped={c:[] for c in COUNTRY};mapped_osm={}
for p in rplaces:
 if p.get('country') not in COUNTRY or not p.get('mapReady'):continue
 lat,lon=sf(p.get('lat')),sf(p.get('lon'))
 if lat is None or lon is None:continue
 rec={'id':p['id'],'name':p.get('name',''),'category':p.get('category',''),'lat':lat,'lon':lon,'source':p.get('source')};mapped[p['country']].append(rec)
 if str(p.get('source') or '').startswith('https://www.openstreetmap.org/'):mapped_osm[p['source']]=rec

results=[]
for n,item in enumerate(selection,1):
 name=item['name'];country=item['country'];cat=item['category'];area=item.get('area') or '';pool={};evidence=[];errors=[]
 cc=item.get('coordinate_candidate') or {};clat,clon=sf(cc.get('latitude')),sf(cc.get('longitude'))
 if clat is not None and clon is not None and str(cc.get('country') or country)==country:
  try:
   z=overpass(name,cat,clat,clon);pool.update(z);evidence.append({'engine':'overpass_geonames','count':len(z)})
  except Exception as e:errors.append('overpass:'+type(e).__name__)
  time.sleep(.15)
 try:
  z=photon(name,country,cat);pool.update(z);evidence.append({'engine':'photon_name','count':len(z)})
 except Exception as e:errors.append('photon:'+type(e).__name__)
 time.sleep(.20)
 # context-enriched Photon query if raw name was weak or ambiguous
 if len(pool)!=1 and area:
  context=re.sub(r'[/&-]+',' ',area).strip().split()[0:4]
  if context:
   try:
    z=photon(name+', '+' '.join(context),country,cat);pool.update(z);evidence.append({'engine':'photon_context','count':len(z)})
   except Exception as e:errors.append('photon_context:'+type(e).__name__)
   time.sleep(.20)
 if len(pool)!=1:
  try:
   z=nominatim(name,country,cat);pool.update(z);evidence.append({'engine':'nominatim','count':len(z)})
  except Exception as e:errors.append('nominatim:'+type(e).__name__)
  time.sleep(.25)
 candidates=list(pool.values());status='REVIEW';reason=[];dup=None;chosen=None
 if len(candidates)==1:
  chosen=candidates[0]
  # source/name/type checks already applied. Extra duplicate checks against mapped runtime.
  if chosen['source'] in mapped_osm:
   status='POSSIBLE_DUPLICATE';dup=mapped_osm[chosen['source']]['id'];reason.append('same_osm_identity_as_existing')
  else:
   same=[e for e in mapped[country] if norm(e['name'])==norm(name) and dist((chosen['lat'],chosen['lon']),(e['lat'],e['lon']))<15000]
   near=[e for e in mapped[country] if e['category']==cat and dist((chosen['lat'],chosen['lon']),(e['lat'],e['lon']))<60]
   if same:status='POSSIBLE_DUPLICATE';dup=same[0]['id'];reason.append('same_name_near_existing')
   elif near:status='POSSIBLE_DUPLICATE';dup=near[0]['id'];reason.append('same_category_within_60m_existing')
   elif chosen.get('score',0)>=.90 or chosen.get('engine')=='overpass_geonames':status='READY'
   else:reason.append('single_candidate_but_name_score_below_0.90')
 elif len(candidates)==0:reason.append('no_supported_osm_identity')
 else:reason.append('multiple_supported_osm_identities:'+str(len(candidates)))
 results.append({**item,'status':status,'reason':reason,'duplicate_of':dup,'chosen':chosen,'candidates':candidates,'evidence':evidence,'errors':errors})
 print(f'{n:03d}/100 #{item["index"]} {country} {status} {name} :: {" | ".join(reason) if reason else (chosen or {}).get("source","")}')

# Batch duplicate guards among newly READY.
seen_src={};seen_name={}
for x in results:
 if x['status']!='READY':continue
 src=x['chosen']['source'];nk=(x['country'],norm(x['name']))
 if src in seen_src:
  x['status']='POSSIBLE_DUPLICATE';x['duplicate_of']=seen_src[src]['stable_id'];x['reason']=['batch_same_osm_identity']
 elif nk in seen_name and dist((x['chosen']['lat'],x['chosen']['lon']),(seen_name[nk]['chosen']['lat'],seen_name[nk]['chosen']['lon']))<15000:
  x['status']='POSSIBLE_DUPLICATE';x['duplicate_of']=seen_name[nk]['stable_id'];x['reason']=['batch_same_name_nearby']
 else:seen_src[src]=x;seen_name[nk]=x

# Build cumulative staging: apply first10 READY, then this batch READY.
wstage=json.loads(json.dumps(working));rstage=json.loads(json.dumps(runtime));wi={r['stable_id']:r for r in wstage['records'] if r.get('stable_id')};ri={r['id']:r for r in rstage['places']};today=datetime.date.today().isoformat()
def apply(sid,name,lat,lon,source,role,verification,review):
 w,r=wi[sid],ri[sid];assert not r.get('mapReady') and not w.get('map_ready');assert norm(w.get('name'))==norm(r.get('name'))==norm(name)
 w['latitude']=float(lat);w['longitude']=float(lon);w['map_ready']=True;w['verification_status']=verification;w['coordinate_role']=role;w['coordinate_source']={'url':source,'provider':'OpenStreetMap','retrieved_on':today,'method':'Reviewed backlog staging; production not overwritten.'};w['coordinate_review']=review
 r['lat']=float(lat);r['lon']=float(lon);r['mapReady']=True;r['source']=source;r['coordinateRole']=role
for d in first['decisions']:
 if d.get('status')=='READY':apply(d['stable_id'],d['name'],d['lat'],d['lon'],d['source'],d['coordinate_role'],d['verification_status'],d.get('review','First10 reviewed'))
ready=[];review=[];dups=[]
for x in results:
 if x['status']=='READY':
  c=x['chosen'];role='osm_point' if c['osm_type']=='node' else 'representative_point_not_entrance';verification='cross_checked_osm_geonames' if c['engine']=='overpass_geonames' else 'reviewed_source_context';apply(x['stable_id'],x['name'],c['lat'],c['lon'],c['source'],role,verification,'Next100 strict OSM/GeoNames staging audit; not field surveyed.');ready.append({'stable_id':x['stable_id'],'name':x['name'],'country':x['country'],'category':x['category'],'lat':c['lat'],'lon':c['lon'],'source':c['source'],'coordinate_role':role,'verification_status':verification})
 elif x['status']=='POSSIBLE_DUPLICATE':dups.append({'stable_id':x['stable_id'],'name':x['name'],'duplicate_of':x['duplicate_of'],'reason':x['reason']})
 else:review.append({'stable_id':x['stable_id'],'name':x['name'],'country':x['country'],'category':x['category'],'area':x['area'],'reason':x['reason'],'candidate_count':len(x['candidates']),'candidates':x['candidates'][:8],'errors':x['errors']})
summary={'processed':100,'range':'11-110','ready':len(ready),'review':len(review),'duplicates':len(dups),'prior_first10_ready':sum(d.get('status')=='READY' for d in first['decisions']),'cumulative_staging_ready_added':sum(d.get('status')=='READY' for d in first['decisions'])+len(ready),'production_overwritten':False,'stable_ids_preserved':True,'backlog_total':853,'backlog_by_country':{'PL':522,'DE':331},'batch_by_country':dict(collections.Counter(x['country'] for x in results))}
for fn,obj in [('results.json',results),('ready_patch.json',ready),('needs_review.json',review),('possible_duplicates.json',dups),('summary.json',summary),('catalog_working_next.json',wstage),('catalog_main_candidate.json',rstage)]: (OUT/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False))
