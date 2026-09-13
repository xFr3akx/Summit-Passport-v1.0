#!/usr/bin/env python3
import csv,json,pathlib,subprocess,tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/import_places.py'

def main():
    with tempfile.TemporaryDirectory() as td:
        td=pathlib.Path(td)
        catalog=td/'catalog.json';queue=td/'queue.csv';report=td/'report.json';out=td/'next.json'
        catalog.write_text(json.dumps({'version':'test','places':[{'id':'SP-old','country':'PL','name':'Testowa Gora','category':'peak','lat':50.0,'lon':19.0,'mapReady':True,'region':'','area':'','source':'https://www.openstreetmap.org/node/10','coordinateRole':'osm_point'}]}),encoding='utf-8')
        with queue.open('w',encoding='utf-8',newline='') as h:
            w=csv.writer(h);w.writerow(['country','name','category','lat','lon','region','area','source','coordinate_role','priority','notes'])
            w.writerow(['PL','Testowa Gora','peak','50.0001','19.0001','','','https://www.openstreetmap.org/node/10','exact','A',''])
            w.writerow(['PL','Nowa Skala','ROCK_GEOLOGY','50.2','19.2','','','https://www.openstreetmap.org/node/20','exact','A',''])
            w.writerow(['PL','Bliski Inny Punkt','nature','50.0002','19.0002','','','https://www.openstreetmap.org/node/30','exact','B',''])
        subprocess.run(['python3',str(SCRIPT),str(queue),'--catalog',str(catalog),'--report',str(report),'--output',str(out)],check=True)
        r=json.loads(report.read_text(encoding='utf-8'));c=json.loads(out.read_text(encoding='utf-8'))
        assert r['summary']['input']==3
        assert r['summary']['new']==1
        assert r['summary']['status_counts']['EXISTS']==1
        assert r['summary']['status_counts']['POSSIBLE_DUPLICATE']==1
        assert len(c['places'])==2
        new=c['places'][1]
        assert new['name']=='Nowa Skala' and new['category']=='rock' and new['id'].startswith('SP-')
    print('PASS: batch importer')

if __name__=='__main__':main()
