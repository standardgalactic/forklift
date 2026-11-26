"""Exact sampled first-parent snapshots, not cumulative churn estimates."""
from . import git

def snapshots(repo, head, base=None, limit=60):
    if limit < 2: raise ValueError('snapshot limit must be at least two')
    args=['rev-list','--first-parent','--reverse',head]
    if base: args.append('^'+base)
    ids=git.decode(git.git(repo,*args)).splitlines()
    if len(ids)>limit:
        ids=[ids[i*(len(ids)-1)//(limit-1)] for i in range(limit)]
    result=[]
    for oid in ids:
        files=git.files(repo,oid)
        date=git.decode(git.git(repo,'show','-s','--format=%cI',oid)).strip()
        result.append(dict(hash=oid,date=date,files=len(files),bytes=sum(f['size'] or 0 for f in files)))
    return result
