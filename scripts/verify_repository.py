"""Independent native-Git checks for a generated report; writes JSON evidence."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('report',type=Path); p.add_argument('--repository',default='.'); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
d=json.loads(a.report.read_text())
def git(*args): return subprocess.check_output(['git','-C',a.repository,*args])
rev=d['revision']; args=[rev]+(['^'+d['base']] if d['base'] else [])
checks=[]
def check(name,actual,expected): checks.append(dict(name=name,actual=actual,expected=expected,passed=actual==expected))
check('commit count',d['summary']['commits'],int(git('rev-list','--count',*args)))
check('snapshot entry count',d['summary']['files'],len(git('ls-tree','-r','--name-only','-z',rev).split(b'\0'))-1)
check('snapshot bytes',d['summary']['bytes'],sum(int(git('cat-file','-s',f['oid'])) for f in d['files'] if f['kind']=='blob'))
check('footprint partition',sum(x['count'] for x in d['footprints']),d['summary']['commits'])
a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(checks,indent=2)+'\n'); raise SystemExit(not all(x['passed'] for x in checks))
