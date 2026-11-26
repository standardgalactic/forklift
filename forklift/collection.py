"""Local repository discovery and comparison; no network by default."""
from concurrent.futures import ThreadPoolExecutor
import csv, json, os, hashlib, subprocess
from pathlib import Path
from .analysis import analyze
from .render import write_report, safe
from .visuals import svg
from .htmlview import bars, exports, page

def discover(root, depth=2):
    root=Path(root).resolve()
    if not root.is_dir(): raise ValueError(f'Not a directory: {root}')
    found=[]
    for current, dirs, files in os.walk(root):
        p=Path(current); level=len(p.relative_to(root).parts)
        if '.git' in dirs or '.git' in files or ('HEAD' in files and 'objects' in dirs and 'refs' in dirs):
            found.append(p); dirs[:]=[]; continue
        dirs[:]=sorted(d for d in dirs if not d.startswith('.') and d not in {'node_modules','__pycache__'}) if level<depth else []
    return found

def github(repo):
    try:
        p=subprocess.run(['gh','repo','view','--json','nameWithOwner,url,stargazerCount,forkCount,isFork'],cwd=repo,capture_output=True,text=True,timeout=30,check=True)
        return json.loads(p.stdout)
    except (OSError,subprocess.SubprocessError,ValueError) as e:
        return {'error':str(e)}

def collection(repos,out,individual=False,remote=False, *, cache=None, renames=False, jobs=1):
    out=Path(out); out.mkdir(parents=True,exist_ok=True); rows=[]; errors=[]
    def one(repo):
        try:
            if cache:
                from .cache import cached_analyze
                data=cached_analyze(repo,cache=cache,renames=renames)
            else: data=analyze(repo,renames=renames)
            s=data['summary']; key=hashlib.sha256(os.fsencode(repo)).hexdigest()[:16]
            row=dict(repository=str(repo),revision=data['revision'],**s,added=sum(x['added'] or 0 for c in data['commits'] for x in c['changes']),deleted=sum(x['deleted'] or 0 for c in data['commits'] for x in c['changes']),report=f'repositories/{key}/index.html' if individual else '')
            if remote: row['github']=github(repo)
            if individual: write_report(data,out/'repositories'/key)
            return row,None
        except (OSError,subprocess.SubprocessError,ValueError) as e: return None,{'repository':str(repo),'error':str(e)}
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for row,error in pool.map(one,sorted({Path(p).resolve() for p in repos})):
            if error: errors.append(error)
            else: rows.append(row)
    (out/'collection.json').write_text(json.dumps({'schema_version':1,'repositories':rows,'errors':errors},indent=2)+'\n')
    fields=['repository','revision','commits','files','bytes','contributors','added','deleted','report']
    with (out/'collection.csv').open('w',newline='',encoding='utf-8',errors='backslashreplace') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    charts=[]; (out/'images').mkdir(exist_ok=True)
    for metric in fields[2:8]:
        chart=svg(metric.title(),[(r['repository'],r[metric]) for r in sorted(rows,key=lambda r:r[metric],reverse=True)],metric)
        (out/'images'/f'{metric}.svg').write_text(chart); charts.append(bars(metric.title(),[(r['repository'],r[metric]) for r in sorted(rows,key=lambda r:r[metric],reverse=True)],metric))
    body=''.join('<tr><td>'+safe(r['repository'])+(' <a href="'+r['report']+'">Report</a>' if r['report'] else '')+'</td>'+''.join(f'<td data-number="{r[k]}">{r[k]:,}</td>' for k in fields[2:8])+'</tr>' for r in rows)
    content='<h1>Repository collection</h1><nav><a href="collection.json">JSON and errors</a> <a href="collection.csv">CSV</a></nav><p>Click column headers to sort.</p><label>Filter repositories <input id="q" type="search"></label><div class="table-scroll"><table><thead><tr><th>Repository</th>'+''.join('<th>'+k+'</th>' for k in fields[2:8])+'</tr></thead><tbody>'+body+'</tbody></table></div><p>Failed repositories: '+str(len(errors))+'</p>'+exports(fields[2:8])+''.join(charts)
    content+='<script>document.getElementById("q").oninput=e=>{for(const r of document.querySelectorAll("tbody tr"))r.hidden=!r.textContent.toLowerCase().includes(e.target.value.toLowerCase())}</script>'
    (out/'index.html').write_text(page('Forklift collection',content),encoding='utf-8')
    return rows,errors
