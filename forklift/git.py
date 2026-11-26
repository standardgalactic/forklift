import subprocess
import os

def git(repo, *args):
    return subprocess.check_output(['git','--no-optional-locks','-C',os.fspath(repo),*args])

def decode(value):
    return value.decode('utf-8','surrogateescape')

def revision(repo, ref):
    return decode(git(repo,'rev-parse','--verify','--end-of-options',ref+'^{commit}')).strip()

def files(repo, ref):
    result=[]
    for row in git(repo,'ls-tree','-r','-l','-z',ref).split(b'\0'):
        if not row: continue
        meta,path=row.split(b'\t',1)
        mode,kind,oid,size=meta.split()
        result.append(dict(path=decode(path),mode=decode(mode),kind=decode(kind),oid=decode(oid),size=None if size==b'-' else int(size)))
    return result

def commits(repo, ref, base=None):
    args=['log','-z','--format=%H%x00%P%x00%aI%x00%aN%x00%aE%x00%s',ref]
    if base: args.append('^'+base)
    fields=git(repo,*args).split(b'\0')
    if fields[-1]==b'': fields.pop()
    if len(fields)%6: raise ValueError('Unexpected Git log framing')
    for i in range(0,len(fields),6):
        h,p,date,name,email,subject=map(decode,fields[i:i+6])
        yield dict(hash=h,parents=p.split(),date=date,author=name,email=email,subject=subject)

def changes(repo, commit, renames=False):
    # First-parent diff; root commits compare against the empty tree.
    args=['diff-tree','--no-commit-id','-r','--numstat','-z','-M50%' if renames else '--no-renames','--no-ext-diff','--no-textconv']
    parents=commit['parents']
    args += [parents[0],commit['hash']] if parents else ['--root',commit['hash']]
    result=[]
    fields=iter(git(repo,*args).split(b'\0'))
    for row in fields:
        if not row: continue
        a,d,path=row.split(b'\t',2)
        old=None
        if not path:
            old=decode(next(fields)); path=next(fields)
        change=dict(path=decode(path),added=None if a==b'-' else int(a),deleted=None if d==b'-' else int(d))
        if old is not None: change['old_path']=old
        result.append(change)
    return result
