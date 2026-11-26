"""Explicit, disposable cache of complete normalized analyses."""
import sqlite3, json, hashlib
from pathlib import Path
from contextlib import closing
from . import git, __version__

def cached_analyze(repo, ref='HEAD', base=None, rules=None, *, cache, renames=False):
    from .analysis import analyze, DEFAULT_RULES
    repo=Path(repo).resolve(); head=git.revision(repo,ref)
    base=git.revision(repo,base) if base else None
    # Local Git configuration and mailmap can affect extraction. Include their
    # observed contents; external attributes still require manual invalidation.
    config=git.git(repo,'config','--null','--list').hex()
    mailmap=(repo/'.mailmap').read_bytes().hex() if (repo/'.mailmap').is_file() else ''
    key=hashlib.sha256(json.dumps([__version__,str(repo),head,base,list((DEFAULT_RULES if rules is None else rules).items()),renames,config,mailmap],ensure_ascii=True).encode()).hexdigest()
    path=Path(cache); path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path,timeout=30)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS analyses (key TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        row=db.execute('SELECT payload FROM analyses WHERE key=?',(key,)).fetchone()
        if row:
            data=json.loads(row[0]); data['cache_hit']=True; return data
        data=analyze(repo,head,base,rules,renames=renames)
        db.execute('INSERT OR REPLACE INTO analyses VALUES (?,?)',(key,json.dumps(data,ensure_ascii=True))); db.commit()
        data['cache_hit']=False; return data
