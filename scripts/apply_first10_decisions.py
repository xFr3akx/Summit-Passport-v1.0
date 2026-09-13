#!/usr/bin/env python3
import collections,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data';OUT=DATA/'first10_backlog'
working=json.loads((DATA/'catalog_working.json').read_text(encoding='utf-8'))
runtime=json.loads((ROOT/'app/src/main/assets/ui/catalog.json').read_text(encoding='utf-8'))
dec=json.loads((OUT/'decisions.json').read_text(encoding='utf-8'))['decisions']
assert len(dec)==10
assert collections.Counter(x['status'] for x in dec)=={'READY':9,'REVIEW':1}
widx={r['stable_id']:r for r in working['records']};ridx={r['id']:r for r in runtime['places']}
rejections=json.loads((DATA/'coordinate_rejections.json').read_text(encoding='utf-8'))
rejected={sid:{f"https://www.openstreetmap.org/{dict(N='node',W='way',R='relation')[x['osm_type']]}/{x['osm_id']}" for x in rows} for sid,rows in rejections.items()}
changes=[]
for d in dec:
 sid=d['stable_id'];assert sid in widx and sid in ridx
 w=widx[sid];r=ridx[sid]
 assert w.get('record_kind')=='place'
 assert not w.get('map_ready') and not r.get('mapReady'),f'already ready {sid}'
 assert w.get('country')==r.get('country')=='DE'
 assert str(w.get('name'))==d['name'] or str(r.get('name'))==d['name']
 if d['status']=='REVIEW':continue
 source=d['source'];assert source.startswith('https://www.openstreetmap.org/')
 assert all(source not in rejected.get(source_id,set()) for source_id in w.get('source_ids',[])),f'previously rejected source {sid}'
 lat=float(d['lat']);lon=float(d['lon']);assert 45<=lat<=56 and 5<=lon<=25
 assert d['verification_status']=='reviewed_source_context'
 role=d['coordinate_role'];assert role in {'osm_point','representative_point_not_entrance','start_or_entrance'}
 # Preserve stable IDs, names, country and runtime category. Only publication fields change.
 before_cat=r.get('category')
 w['latitude']=lat;w['longitude']=lon;w['map_ready']=True
 w['verification_status']=d['verification_status'];w['coordinate_role']=role
 w['coordinate_source']={'url':source,'provider':'OpenStreetMap','retrieved_on':'2026-09-13','method':'First-10 backlog manual source-context review; exact identity or explicitly documented representative point.'}
 w['coordinate_review']=d['review']
 if not w.get('category'):w['category']=before_cat
 r['lat']=lat;r['lon']=lon;r['mapReady']=True;r['source']=source;r['coordinateRole']=role
 assert r.get('category')==before_cat
 changes.append({'stable_id':sid,'name':r['name'],'country':r['country'],'category':r['category'],'lat':lat,'lon':lon,'source':source,'coordinateRole':role,'verification_status':d['verification_status']})
assert len(changes)==9
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'catalog_working_next.json').write_text(json.dumps(working,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'catalog_main_candidate.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'ready_patch.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=[x for x in dec if x['status']=='REVIEW'];(OUT/'needs_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'processed':10,'ready':9,'review':1,'duplicates':0,'production_overwritten':False,'stable_ids_preserved':True,'ready_names':[x['name'] for x in changes],'review_names':[x['name'] for x in review]}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
