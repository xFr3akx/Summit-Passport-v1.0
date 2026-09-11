import re, sqlite3
from pathlib import Path
source=(Path(__file__).resolve().parents[1]/'app/src/main/java/com/summitpassport/app/PassportDatabase.java').read_text()
state_sql=re.search(r'db.execSQL\("(CREATE TABLE app_state[^\"]+)"\)',source).group(1)
db=sqlite3.connect(':memory:')
db.execute('CREATE TABLE visits (id TEXT PRIMARY KEY, rating INTEGER CHECK(rating BETWEEN 0 AND 5))')
db.execute("INSERT INTO visits VALUES ('old',4)")
db.execute(state_sql)
db.execute("INSERT INTO app_state VALUES ('plans','old plans')")
db.commit()
try:
    with db:
        db.execute("INSERT INTO visits VALUES ('new',5)")
        db.execute("UPDATE app_state SET value='new plans' WHERE key='plans'")
        db.execute("INSERT INTO visits VALUES ('invalid',6)")
except sqlite3.IntegrityError:
    pass
assert db.execute('SELECT * FROM visits').fetchall()==[('old',4)]
assert db.execute("SELECT value FROM app_state WHERE key='plans'").fetchone()[0]=='old plans'
with db:
    db.execute("INSERT INTO visits VALUES ('new',5)")
    db.execute("UPDATE app_state SET value='merged plans' WHERE key='plans'")
assert db.execute('SELECT count(*) FROM visits').fetchone()[0]==2
print('PASS: app_state schema preserves existing visits; settings and visits roll back together on SQL failure')
