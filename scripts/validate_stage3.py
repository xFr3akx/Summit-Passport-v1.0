"""Release gate for frozen catalog, linked source identities and map eligibility."""
import pathlib,json,hashlib,xml.etree.ElementTree as E
R=pathlib.Path(__file__).resolve().parents[1];A=R/'app/src/main/assets/ui'
catalog_path=R/'data/catalog_runtime_060.json'
if not catalog_path.exists():catalog_path=A/'catalog.json'
app=json.loads(catalog_path.read_text(encoding='utf-8'));working=json.loads((R/'data/catalog_working.json').read_text(encoding='utf-8'))['records']
source={r['stable_id']:r for r in working if r['record_kind']=='place'}
assert len(app['places'])==2263 and len({p['id'] for p in app['places']})==2263
assert {p['id'] for p in app['places']}==set(source)
counts={}
for p in app['places']:
 original=source[p['id']]
 assert p['mapReady']==original['map_ready']
 if p['mapReady']:
  assert (p['lat'],p['lon'])==(original['latitude'],original['longitude'])
  assert p['source']==original['coordinate_source']['url']
  counts[p['country']]=counts.get(p['country'],0)+1
 else:assert p['lat'] is None and p['lon'] is None and p['source'] is None
assert counts=={'PL':451,'DE':614}
manifest=E.parse(R/'app/src/main/AndroidManifest.xml').getroot();ns='{http://schemas.android.com/apk/res/android}'
permissions={p.attrib[ns+'name'] for p in manifest.findall('uses-permission')}
assert permissions=={'android.permission.INTERNET'}
for f in ['landscape.png','vendor/leaflet.js','vendor/leaflet.css','vendor/leaflet.markercluster.js','vendor/MarkerCluster.css','vendor/LEAFLET-LICENSE.txt','vendor/MIT-LICENCE.txt']:assert (A/f).is_file()
report={'version':app['version'],'map_points':counts,'catalog_sha256':hashlib.sha256(catalog_path.read_bytes()).hexdigest(),'frozen':True,'near_me_stage':7,'catalog_complete':False}
(R/'data/stage3_release.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS',report)
