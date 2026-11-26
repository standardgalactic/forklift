import argparse,json,tomllib,sys
from pathlib import Path
from .analysis import analyze
from .render import write_report

def main():
    if len(sys.argv)>1 and sys.argv[1] in ('scan','compare'):
        from .collection import discover, collection
        mode=sys.argv[1]; p=argparse.ArgumentParser(prog='forklift '+mode)
        p.add_argument('paths',nargs='+' if mode=='compare' else 1); p.add_argument('--output',required=True,type=Path); p.add_argument('--depth',type=int,default=2); p.add_argument('--individual',action='store_true'); p.add_argument('--github',action='store_true')
        p.add_argument('--cache',type=Path); p.add_argument('--renames',action='store_true'); p.add_argument('--jobs',type=int,default=1); a=p.parse_args(sys.argv[2:]);
        if a.jobs<1: p.error('--jobs must be positive')
        repos=discover(a.paths[0],a.depth) if mode=='scan' else a.paths
        rows,errors=collection(repos,a.output,a.individual,a.github,cache=a.cache,renames=a.renames,jobs=a.jobs); print(a.output/'index.html'); return 1 if errors else 0
    p=argparse.ArgumentParser(description='Generate persistent Git repository reports')
    p.add_argument('repository',nargs='?',default='.')
    p.add_argument('--revision',default='HEAD'); p.add_argument('--base'); p.add_argument('--output',required=True,type=Path); p.add_argument('--rules',type=Path); p.add_argument('--from-json',type=Path); p.add_argument('--plots',action='store_true')
    p.add_argument('--snapshots',type=int,default=0,help='Sample exact first-parent trees (0 disables)')
    p.add_argument('--cache',type=Path); p.add_argument('--renames',action='store_true')
    a=p.parse_args(); rules=tomllib.loads(a.rules.read_text())['categories'] if a.rules else None
    if a.from_json: data=json.loads(a.from_json.read_text())
    elif a.cache:
        from .cache import cached_analyze
        data=cached_analyze(a.repository,a.revision,a.base,rules,cache=a.cache,renames=a.renames)
    else: data=analyze(a.repository,a.revision,a.base,rules,renames=a.renames)
    if data['schema_version']!=1: p.error('Unsupported schema')
    if a.snapshots:
        if a.from_json or a.snapshots<2: p.error('--snapshots requires a repository and a count of at least two')
        from .history import snapshots
        data['snapshots']=snapshots(a.repository,data['revision'],data['base'],a.snapshots)
    write_report(data,a.output)
    if a.plots:
        from .plots import plots
        plots(data,a.output/'images')
    print(a.output/'index.html')
if __name__=='__main__': sys.exit(main())
