#!/usr/bin/env python3
import collections,datetime,difflib,json,math,pathlib,re,time,unicodedata,urllib.parse,urllib.request
R=pathlib.Path(__file__).resolve().parents[1];O=R/'data/next100_broad';O.mkdir(parents=True,exist_ok=True);PH='https://photon.komoot.io/api/'
work=json.loads((R/'data/catalog_working.json').read_text(encoding='utf-8'));run=json.loads((R/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'));g=json.loads((R/'data/germany_completion_064.json').read_text(encoding='utf-8'));first=json.loads((R/'data/first10_backlog/decisions.json').read_text(encoding='utf-8'));ridx={p['id']:p for p in run['places']}
def norm(v):
 s=unicodedata.normalize('NFKD',str(v or '').replace('ß','ss').replace('ł','l')).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','',s)
def sim(a,b):
 a,b=norm(a),norm(b)
 if a==b and a:return 1
 if min(len(a),len(b))>=6 and (a in b or b in a):return .93
 return difflib.SequenceMatcher(None,a,b).ratio()
def dist(a,b):
 lat1,lon1=a;lat2,lon2=b;x=math.radians(lon2-lon1)*math.cos(math.radians((lat1+lat2)/2));y=math.radians(lat2-lat1);return 6371000*math.hypot(x,y)
def osmurl(t,i):
 k={'N':'node','W':'way','R':'relation'}.get(str(t));return f'https://www.openstreetmap.org/{k}/{i}' if k and i else None
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
allg=list(walk(g));dupids={d.get('id') for d in allg if d.get('status')=='duplicate' and d.get('duplicateOf')};assert len(dupids)==12
back=[r for r in work['records'] if r.get('country') in {'PL','DE'} and r.get('record_kind')=='place' and not r.get('map_ready') and r.get('stable_id') in ridx and not ridx[r['stable_id']].get('mapReady') and r.get('stable_id') not in dupids];back.sort(key=lambda r:(r.get('country',''),str((r.get('source_regions') or [''])[0]),r.get('name',''),r.get('stable_id','')));assert collections.Counter(r['country'] for r in back)=={'PL':522,'DE':331};batch=back[10:110]
mapped={p.get('source'):p for p in run['places'] if p.get('mapReady') and str(p.get('source') or '').startswith('https://www.openstreetmap.org/')};mappedlist=[p for p in run['places'] if p.get('mapReady') and p.get('country') in {'PL','DE'} and p.get('lat') is not None]
def photon(name,country):
 q=name+', '+('Deutschland' if country=='DE' else 'Polska');url=PH+'?'+urllib.parse.urlencode({'q':q,'limit':14,'lang':'de' if country=='DE' else 'pl'});err=None
 for n in range(2):
  try:
   raw=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SummitPassportCatalogAudit/6.0 broad100'}),timeout=12));break
  except Exception as e:err=e;time.sleep(.4*(n+1))
 else:return [],type(err).__name__
 out={}
 for f in raw.get('features',[]):
  p=f.get('properties') or {};co=(f.get('geometry') or {}).get('coordinates') or [];nm=p.get('name') or '';sc=sim(name,nm)
  if len(co)<2 or str(p.get('countrycode') or '').upper()!=country or sc<.93:continue
  u=osmurl(p.get('osm_type'),p.get('osm_id'))
  if u:out[u]={'source':u,'lat':float(co[1]),'lon':float(co[0]),'name':nm,'score':round(sc,3),'osm_type':{'N':'node','W':'way','R':'relation'}.get(str(p.get('osm_type'))),'osm_id':p.get('osm_id'),'osm_key':p.get('osm_key'),'osm_value':p.get('osm_value'),'context':[p.get('district'),p.get('city'),p.get('county'),p.get('state')]}
 return list(out.values()),None
results=[]
for pos,r in enumerate(batch,11):
 rp=ridx[r['stable_id']];name=rp['name'];country=r['country'];cand,err=photon(name,country);cc=r.get('coordinate_candidate') or {};chosen=None;reason=[];status='REVIEW';dupto=None
 if cand:
  clat,clon=cc.get('latitude'),cc.get('longitude')
  if clat is not None and clon is not None:
   near=sorted([(dist((float(clat),float(clon)),(c['lat'],c['lon'])),c) for c in cand],key=lambda x:x[0]);within=[x for x in near if x[0]<=3000]
   if len(within)==1:chosen=within[0][1];reason.append('unique_exact_identity_within_3km_of_geonames')
  if chosen is None and len(cand)==1:chosen=cand[0];reason.append('single_exact_country_osm_identity')
 if chosen:
  if chosen['source'] in mapped:status='POSSIBLE_DUPLICATE';dupto=mapped[chosen['source']]['id'];reason=['same_osm_identity_as_existing']
  else:
   same=[p for p in mappedlist if p['country']==country and norm(p.get('name'))==norm(name) and dist((chosen['lat'],chosen['lon']),(float(p['lat']),float(p['lon'])))<15000]
   if same:status='POSSIBLE_DUPLICATE';dupto=same[0]['id'];reason=['same_name_near_existing']
   else:status='READY'
 elif not cand:reason.append('no_exact_country_osm_identity'+((':'+err) if err else ''))
 else:reason.append('multiple_exact_country_osm_identities:'+str(len(cand)))
 results.append({'index':pos,'stable_id':r['stable_id'],'country':country,'name':name,'category':rp['category'],'area':rp.get('area'),'status':status,'reason':reason,'duplicate_of':dupto,'coordinate_candidate':cc or None,'chosen':chosen,'candidates':cand})
 print(f'{pos:03d} {status} {name} :: {" | ".join(reason)}')
 time.sleep(.06)
seen={}
for x in results:
 if x['status']!='READY':continue
 s=x['chosen']['source']
 if s in seen:x['status']='POSSIBLE_DUPLICATE';x['duplicate_of']=seen[s]['stable_id'];x['reason']=['batch_same_osm_identity']
 else:seen[s]=x
ws=json.loads(json.dumps(work));rs=json.loads(json.dumps(run));wi={r['stable_id']:r for r in ws['records'] if r.get('stable_id')};ri={p['id']:p for p in rs['places']};today=datetime.date.today().isoformat()
def apply(sid,c,review):
 w,p=wi[sid],ri[sid];assert not w.get('map_ready') and not p.get('mapReady');role='osm_point' if c.get('osm_type')=='node' else 'representative_point_not_entrance';w['latitude']=c['lat'];w['longitude']=c['lon'];w['map_ready']=True;w['verification_status']='reviewed_source_context';w['coordinate_role']=role;w['coordinate_source']={'url':c['source'],'provider':'OpenStreetMap / Photon','retrieved_on':today,'method':'Broad exact-identity next-100 audit; category taxonomy preserved; production unchanged.'};w['coordinate_review']=review;p['lat']=c['lat'];p['lon']=c['lon'];p['mapReady']=True;p['source']=c['source'];p['coordinateRole']=role
for d in first['decisions']:
 if d.get('status')=='READY':apply(d['stable_id'],{'lat':d['lat'],'lon':d['lon'],'source':d['source'],'osm_type':'node' if d['coordinate_role']=='osm_point' else 'way'},d.get('review','first10'))
ready=[];review=[];dups=[]
for x in results:
 if x['status']=='READY':apply(x['stable_id'],x['chosen'],'Next100 broad exact-name/country identity; runtime category deliberately preserved; not field surveyed.');ready.append(x)
 elif x['status']=='POSSIBLE_DUPLICATE':dups.append(x)
 else:review.append(x)
summary={'processed':100,'range':'11-110','ready':len(ready),'review':len(review),'duplicates':len(dups),'prior_first10_ready':9,'cumulative_staged':9+len(ready),'production_overwritten':False,'batch_by_country':dict(collections.Counter(x['country'] for x in results))}
for fn,obj in [('results.json',results),('ready_patch.json',ready),('needs_review.json',review),('possible_duplicates.json',dups),('summary.json',summary),('catalog_working_next.json',ws),('catalog_main_candidate.json',rs)]: (O/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False))
