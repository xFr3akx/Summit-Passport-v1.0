"""Run the actual v5 -> v6 migration SQL on SQLite with existing user data."""
import re,sqlite3
from pathlib import Path
source=(Path(__file__).resolve().parents[1]/'app/src/main/java/com/summitpassport/app/PassportDatabase.java').read_text(encoding='utf8')
creates=re.findall(r'db.execSQL\("([^"]+)"\)',source.split('public void onCreate')[1].split('@Override public void onUpgrade')[0])
migration=re.findall(r'db.execSQL\("([^"]+)"\)',source.split('if(oldVersion<6){')[1].split('\n  }')[0])
db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON')
for sql in creates:
 sql=sql.replace('BETWEEN 0 AND 10), form_version INTEGER NOT NULL DEFAULT 2 CHECK(form_version IN (1,2))','BETWEEN 0 AND 5)')
 db.execute(sql)
db.execute("INSERT INTO places VALUES ('p','DE','Ort','DE-BY','peak',50,11,0)")
db.execute("INSERT INTO visits VALUES ('visit','p','2026-09-01',1234,123,456,'Notatka 🏔','Śnieg','Trasa bez linku','[\"photo.jpg\"]',5)")
db.execute("INSERT INTO achievement_unlocks VALUES ('DE','peak',0,'2026-09-01T12:00:00Z','2026-09-01')")
db.execute("INSERT INTO app_state VALUES ('plans','keep plans')")
before=db.execute('SELECT * FROM visits').fetchall();db.commit()
with db:
 for sql in migration:db.execute(sql)
assert db.execute('SELECT * FROM visits').fetchall()==[before[0]+(1,)]
assert db.execute('SELECT value FROM app_state').fetchone()==('keep plans',)
assert db.execute('SELECT count(*) FROM achievement_unlocks').fetchone()==(1,)
assert not db.execute('PRAGMA foreign_key_check').fetchall()
db.execute("UPDATE visits SET rating=10,form_version=2 WHERE id='visit'")
assert db.execute('SELECT rating,form_version FROM visits').fetchone()==(10,2)
for rating in [-1,11]:
 try:db.execute('UPDATE visits SET rating=?',(rating,));raise AssertionError('Invalid rating accepted')
 except sqlite3.IntegrityError:pass
fresh=sqlite3.connect(':memory:')
for sql in creates:fresh.execute(sql)
assert db.execute('PRAGMA table_info(visits)').fetchall()==fresh.execute('PRAGMA table_info(visits)').fetchall()
assert db.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='visits_place'").fetchone()
print('PASS: v5→v6 preserves every visit field, IDs, photos, plans and awards; legacy flag; ten-point edit; range; fresh-schema parity')
