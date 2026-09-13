#!/usr/bin/env python3
import collections,json,pathlib,re,unicodedata,difflib
R=pathlib.Path(__file__).resolve().parents[1];O=R/'data/next100_evidence';O.mkdir(parents=True,exist_ok=True)
work=json.loads((R/'data/catalog_working.json').read_text(encoding='utf-8'));run=json.loads((R/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'));g=json.loads((R/'data/germany_completion_064.json').read_text(encoding='utf-8'))
ridx={p['id']:p for p in run['places']}
def norm(v):
 s=unicodedata.normalize('NFKD',str(v or '').replace('ß','ss').replace('ł','l')).encode('ascii','ignore').decode().lower();return re.sub(r'[^a-z0-9]+','',s)
def sim(a,b):
 a,b=norm(a),norm(b)
 if a==b and a:return 1
 if min(len(a),len(b))>=6 and (a in b or b in a):return .93
 return difflib.SequenceMatcher(None,a,b).ratio()
def url(p):
 t={'N':'node','W':'way','R':'relation','node':'node','way':'way','relation':'relation'}.get(str(p.get('osm_type')));return f"https://www.openstreetmap.org/{t}/{p.get('osm_id')}" if t and p.get('osm_id') else None
def typeok(cat,p):
 k=str(p.get('osm_key') or '');v=str(p.get('osm_value') or '')
 if cat=='peak':return k=='natural' and v=='peak'
 if cat=='pass':return (k=='natural' and v=='saddle') or v=='mountain_pass'
 if cat=='water':return v in {'water','lake','reservoir','pond'}
 if cat=='waterfall':return v=='waterfall'
 if cat=='cave':return v=='cave_entrance'
 if cat=='rock':return v in {'rock','stone','cliff','peak','geological_site'}
 if cat=='castle':return k=='historic' and v in {'castle','fort','ruins','manor'}
 if cat=='viewpoint':return k=='tourism' and v=='viewpoint'
 if cat=='lighthouse':return v=='lighthouse'
 if cat=='heritage':return k in {'historic','heritage','tourism'} or v in {'museum','attraction','monument','memorial','archaeological_site','ruins'}
 if cat=='industrial':return k in {'industrial','man_made'}
 if cat=='nature':return k in {'natural','leisure','boundary','place','tourism','bridge','waterway'}
 return False
# duplicate IDs already linked in 0.6.4
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
all_dicts=list(walk(g));dup={d.get('id') for d in all_dicts if d.get('status')=='duplicate' and d.get('duplicateOf')};assert len(dup)==12,len(dup)
back=[r for r in work['records'] if r.get('country') in {'PL','DE'} and r.get('record_kind')=='place' and not r.get('map_ready') and r.get('stable_id') in ridx and not ridx[r['stable_id']].get('mapReady') and r.get('stable_id') not in dup]
back.sort(key=lambda r:(r.get('country',''),str((r.get('source_regions') or [''])[0]),r.get('name',''),r.get('stable_id','')));assert collections.Counter(r['country'] for r in back)=={'PL':522,'DE':331};batch=back[10:110]
byid=collections.defaultdict(list)
for d in all_dicts:
 if d.get('id'):byid[d['id']].append(d)
# mapped OSM refs
mapped={p.get('source'):p for p in run['places'] if p.get('mapReady') and str(p.get('source') or '').startswith('https://www.openstreetmap.org/')}
ready=[];review=[];dups=[]
for i,r in enumerate(batch,11):
 sid=r['stable_id'];rp=ridx[sid];name=rp['name'];cat=rp['category'];entries=byid.get(sid,[]);cand={}
 for e in entries:
  for c in e.get('candidates') or []:
   p=c.get('properties') or {};co=(c.get('geometry') or {}).get('coordinates') or [];u=url(p)
   if u and len(co)>=2 and str(p.get('countrycode') or '').upper()=='DE' and sim(name,p.get('name'))>=.90 and typeok(cat,p):cand[u]={'source':u,'lat':float(co[1]),'lon':float(co[0]),'name':p.get('name'),'osm_key':p.get('osm_key'),'osm_value':p.get('osm_value'),'score':round(sim(name,p.get('name')),3)}
  m=((e.get('match') or {}).get('osm') or {});p=m.get('properties') or {};co=(m.get('geometry') or {}).get('coordinates') or [];u=url(p)
  if u and len(co)>=2 and str(p.get('countrycode') or '').upper()=='DE' and sim(name,p.get('name'))>=.90 and typeok(cat,p):cand[u]={'source':u,'lat':float(co[1]),'lon':float(co[0]),'name':p.get('name'),'osm_key':p.get('osm_key'),'osm_value':p.get('osm_value'),'score':round(sim(name,p.get('name')),3)}
 vals=list(cand.values())
 rec={'index':i,'stable_id':sid,'name':name,'country':r['country'],'category':cat,'area':rp.get('area'),'evidence_candidates':vals}
 if len(vals)==1:
  c=vals[0]
  if c['source'] in mapped:
   rec.update(status='POSSIBLE_DUPLICATE',duplicate_of=mapped[c['source']]['id'],reason='same_osm_identity_as_existing');dups.append(rec)
  else:
   rec.update(status='READY',chosen=c,reason='one exact/type/country-compatible OSM identity in existing 0.6.4 evidence');ready.append(rec)
 else:
  rec.update(status='REVIEW',reason=('no exact supported OSM identity in existing evidence' if not vals else f'{len(vals)} exact supported OSM identities remain ambiguous'));review.append(rec)
summary={'processed':100,'range':'11-110','ready':len(ready),'review':len(review),'duplicates':len(dups),'source':'germany_completion_064 existing evidence','production_overwritten':False}
for fn,obj in [('ready.json',ready),('review.json',review),('duplicates.json',dups),('summary.json',summary)]: (O/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False));
for x in ready:print('READY',x['index'],x['name'],x['chosen']['source'])
for x in dups:print('DUP',x['index'],x['name'],'->',x['duplicate_of'])
