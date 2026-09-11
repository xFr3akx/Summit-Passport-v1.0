"""Exercise the application's SQL on SQLite, including an existing v1 visit.

This verifies schema/data preservation, not Android UI or the Java bridge.
"""
import re
import sqlite3
from pathlib import Path

source = (Path(__file__).resolve().parents[1] / 'app/src/main/java/com/summitpassport/app/PassportDatabase.java').read_text(encoding='utf-8')
statements = re.findall(r'db.execSQL\("([^"]+)"\)', source)
creates = re.findall(r'db.execSQL\("([^"]+)"\)', source.split('public void onCreate')[1].split('@Override public void onUpgrade')[0])
upgrades = [s for s in statements if s.startswith('ALTER')]
old_visits = "CREATE TABLE visits (id TEXT PRIMARY KEY NOT NULL, place_id TEXT NOT NULL REFERENCES places(stable_id), visited_on TEXT NOT NULL, distance_m INTEGER NOT NULL DEFAULT 0 CHECK(distance_m >= 0), duration_minutes INTEGER NOT NULL DEFAULT 0 CHECK(duration_minutes >= 0), elevation_gain_m INTEGER NOT NULL DEFAULT 0 CHECK(elevation_gain_m >= 0), notes TEXT NOT NULL DEFAULT '')"
db = sqlite3.connect(':memory:')
db.execute('PRAGMA foreign_keys=ON')
for sql in creates:
    db.execute(old_visits if sql.startswith('CREATE TABLE visits') else sql.replace(', earned_on TEXT NOT NULL',''))
db.execute("INSERT INTO places VALUES ('PL-test','PL','Test','','peak',50,19,0)")
db.execute("INSERT INTO visits (id,place_id,visited_on,notes) VALUES ('v1','PL-test','2026-09-01','Zachowana notatka')")
for sql in upgrades:
    db.execute(sql)
assert db.execute('SELECT id,notes,weather,trail_url,photos FROM visits').fetchone() == ('v1','Zachowana notatka','','','[]')
db.execute("INSERT INTO visits (id,place_id,visited_on,weather,trail_url,photos) VALUES ('v2','PL-test','2026-09-10','Deszcz','https://www.alltrails.com/trail/test','[\"test.jpg\"]')")
db.execute("UPDATE visits SET notes='Edycja' WHERE id='v1' AND place_id='PL-test'")
assert db.execute('SELECT count(*) FROM visits').fetchone()[0] == 2
assert db.execute('SELECT count(DISTINCT place_id) FROM visits').fetchone()[0] == 1
assert not db.execute('PRAGMA foreign_key_check').fetchall()
fresh = sqlite3.connect(':memory:')
for sql in creates:
    fresh.execute(sql)
assert db.execute('PRAGMA table_info(visits)').fetchall() == fresh.execute('PRAGMA table_info(visits)').fetchall()
assert db.execute("SELECT rating FROM visits WHERE id='v1'").fetchone()[0] == 0
# A v2 database already contains weather, link and photos; add only rating.
v2 = sqlite3.connect(':memory:')
for sql in creates:
    v2.execute(sql.replace(", rating INTEGER NOT NULL DEFAULT 0 CHECK(rating BETWEEN 0 AND 5)", ""))
v2.execute("INSERT INTO places VALUES ('PL-test','PL','Test','','peak',50,19,0)")
v2.execute("INSERT INTO visits (id,place_id,visited_on,notes,photos) VALUES ('existing','PL-test','2026-09-01','Keep me','[]')")
v2.execute(next(s for s in upgrades if 'ADD COLUMN rating' in s))
assert v2.execute('SELECT notes,rating FROM visits').fetchone() == ('Keep me',0)
v2.execute("UPDATE visits SET rating=5 WHERE id='existing'")
assert v2.execute('SELECT rating FROM visits').fetchone()[0] == 5
try:
    v2.execute('UPDATE visits SET rating=6')
    raise AssertionError('Out of range rating accepted')
except sqlite3.IntegrityError:
    pass
db.execute("DELETE FROM visits WHERE id='v1'")
assert db.execute('SELECT count(DISTINCT place_id) FROM visits').fetchone()[0] == 1
db.execute("DELETE FROM visits WHERE id='v2'")
assert db.execute('SELECT count(DISTINCT place_id) FROM visits').fetchone()[0] == 0
print('PASS: v1/v2 migration to v3 preserves data, ratings/default/range, multiple vs last visit deletion, fresh schema parity')
