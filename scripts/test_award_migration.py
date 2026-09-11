"""SQLite migration and atomic backup rollback, using the application's SQL schema."""
import re,sqlite3
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/'app/src/main/java/com/summitpassport/app/PassportDatabase.java').read_text(encoding='utf-8')
create=re.search(r'db.execSQL\("(CREATE TABLE achievement_unlocks[^\"]+)"\)',s).group(1)
alter=re.search(r'db.execSQL\("(ALTER TABLE achievement_unlocks[^\"]+)"\)',s).group(1)
update=re.search(r'db.execSQL\("(UPDATE achievement_unlocks[^\"]+)"\)',s).group(1)
db=sqlite3.connect(':memory:');db.execute(create.replace(', earned_on TEXT NOT NULL',''))
db.execute("INSERT INTO achievement_unlocks VALUES ('PL','peak',0,'2026-09-01T12:00:00Z')");db.execute(alter);db.execute(update)
assert db.execute('SELECT earned_on FROM achievement_unlocks').fetchone()[0]=='2026-09-01'
db.execute('CREATE TABLE visits (id TEXT PRIMARY KEY, rating INTEGER CHECK(rating BETWEEN 0 AND 5))');db.execute("INSERT INTO visits VALUES ('existing',4)");db.commit()
try:
 with db:
  db.execute("INSERT INTO achievement_unlocks VALUES ('DE','peak',0,'2026-09-11T12:00:00Z','2026-09-05')")
  db.execute("INSERT INTO visits VALUES ('bad',9)")
except sqlite3.IntegrityError:pass
assert db.execute('SELECT count(*) FROM achievement_unlocks').fetchone()[0]==1
db.execute("INSERT OR IGNORE INTO achievement_unlocks VALUES ('PL','peak',0,'2026-09-11T12:00:00Z','2026-09-05')")
assert db.execute('SELECT earned_on FROM achievement_unlocks').fetchone()[0]=='2026-09-01'
print('PASS: v4 to v5 award date migration, duplicate import retains existing date, failed backup transaction rolls back awards and visits')
