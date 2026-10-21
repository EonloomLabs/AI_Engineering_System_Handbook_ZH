"""Two independent databases model an executor and a downstream effect store.
A deliberate os._exit occurs ONLY inside the supplied temporary directory.
"""
import json, os, sqlite3, sys
from pathlib import Path

def main():
    root=Path(sys.argv[1]).resolve(); mode=sys.argv[2]; phase=sys.argv[3]
    if mode not in {'unsafe','keyed'} or phase not in {'crash','resume'}:
        raise ValueError('invalid mode')
    external=sqlite3.connect(root/'external.sqlite')
    external.execute('CREATE TABLE IF NOT EXISTS effects(id INTEGER PRIMARY KEY, intent TEXT UNIQUE, value TEXT)')
    journal=sqlite3.connect(root/'journal.sqlite')
    journal.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, status TEXT)')
    journal.execute("INSERT OR IGNORE INTO jobs VALUES('job7','pending')");journal.commit()
    done=journal.execute("SELECT status FROM jobs WHERE id='job7'").fetchone()[0]=='done'
    if not done:
        intent=None if mode=='unsafe' else 'stable-operation-7'
        external.execute('INSERT OR IGNORE INTO effects(intent,value) VALUES(?,?)',(intent,'effect'))
        external.commit()
        if phase=='crash': os._exit(17)  # downstream committed; journal NOT acknowledged
        journal.execute("UPDATE jobs SET status='done' WHERE id='job7'");journal.commit()
    print(json.dumps({'status':'done'}))
    external.close();journal.close()
if __name__=='__main__': main()
