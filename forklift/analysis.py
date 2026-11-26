from collections import Counter
from itertools import combinations
from pathlib import PurePosixPath
from fnmatch import fnmatchcase
from datetime import datetime, timezone
from . import git, __version__

DEFAULT_RULES={
 'Dependencies and packaging':['package.json','package-lock.json','bun.lock','bun.lockb','yarn.lock','pnpm-lock.yaml','requirements*.txt','pyproject.toml','Cargo.lock','Cargo.toml','go.mod','go.sum'],
 'CI and automation':['.github/*'],
 'Build and configuration':['*.config.*','tsconfig*','Dockerfile*','.npmrc','.gitignore','Makefile'],
 'Tests':['tests/*','test/*','e2e/*','*/tests/*','*/test/*','*/__tests__/*','*.test.*','*.spec.*','test_*.py'],
 'Analysis engine':['src/analyzer/*','src/server/*','src/metrics/*','forklift/analysis.py','forklift/git.py'],
 'User interface':['src/components/*','src/routes/*','src/state/*','src/styles/*','*.css','*.scss','forklift/render.py'],
 'Documentation':['*.md','*.rst','*.pdf'],
 'Media assets':['*.png','*.jpg','*.jpeg','*.gif','*.svg','*.webp','*.ico'],
 'Other application source':['src/*','forklift/*']}

def category(path,rules):
    for name,patterns in rules.items():
        if any(fnmatchcase(path,p) or ('/' not in p and fnmatchcase(PurePosixPath(path).name,p)) for p in patterns): return name
    return 'Other'

def analyze(repo, ref='HEAD', base=None, rules=None, *, renames=False):
    rules=DEFAULT_RULES if rules is None else rules
    head=git.revision(repo,ref); base=git.revision(repo,base) if base else None
    files=git.files(repo,head); history=[]
    incidence=Counter(); footprints=Counter(); pairs=Counter(); authors=Counter(); paths=Counter(); months=Counter()
    for c in git.commits(repo,head,base):
        c['changes']=git.changes(repo,c,renames)
        touched=sorted({category(path,rules) for x in c['changes'] for path in (x['path'],x.get('old_path',x['path']))})
        c['categories']=touched; history.append(c)
        incidence.update(touched); footprints[tuple(touched)]+=1; pairs.update(combinations(touched,2))
        authors[(c['author'],c['email'])]+=1; paths.update(x['path'] for x in c['changes']); months[c['date'][:7]]+=1
    n=len(history)
    coupling=[dict(a=a,b=b,count=k,a_to_b=k/incidence[a],b_to_a=k/incidence[b],jaccard=k/(incidence[a]+incidence[b]-k),lift=n*k/(incidence[a]*incidence[b])) for (a,b),k in pairs.most_common()]
    return dict(schema_version=1,version=__version__,generated_at=datetime.now(timezone.utc).isoformat(),repository=str(repo),revision=head,base=base,policy={'merges':'first-parent diff','renames':'Git similarity 50%; both categories, destination modification count' if renames else 'delete/add','authors':'Git mailmap primary author','rules':rules},summary=dict(commits=n,files=len(files),bytes=sum(f['size'] or 0 for f in files),contributors=len(authors)),files=files,commits=history,contributors=[dict(name=a,email=e,commits=k) for (a,e),k in authors.most_common()],modifications=dict(paths.most_common()),months=dict(sorted(months.items())),incidence=dict(incidence.most_common()),footprints=[dict(categories=list(f),count=k) for f,k in footprints.most_common()],coupling=coupling)
