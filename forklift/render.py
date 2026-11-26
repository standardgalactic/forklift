import csv
import json
from pathlib import Path
from html import escape
from .visuals import metrics, figures, svg
from .artifacts import artifacts, treemap
from .interactive import relationships, panel
from .htmlview import bars, exports, page
from .extra import distribution, calendar, growth, explorer

def safe(x):
    return escape(str(x).encode('utf-8','backslashreplace').decode())

def table(title,headers,rows):
    return '<h2>'+safe(title)+'</h2><div class="table-scroll"><table><thead><tr>'+''.join('<th>'+safe(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<td data-number="'+str(v)+'">' if isinstance(v,(int,float)) else '<td>')+safe(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def write_report(data,out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    derived=metrics(data)
    relations=relationships(data)
    (out/'relationships.json').write_text(json.dumps(relations,ensure_ascii=True,indent=2)+'\n')
    charts=figures(data,out/'images')
    derived['commit_size_distribution']=distribution(data)
    derived['artifacts']=artifacts(data['files'])
    charts['artifacts']=svg('Artifact classes',((k,v['bytes']) for k,v in sorted(derived['artifacts'].items(),key=lambda x:-x[1]['bytes'])),'Logical bytes; heuristic classes')
    charts['treemap']=treemap(data['files'])
    charts['calendar']=calendar(derived['daily'])
    charts['commit-sizes']=svg('Commit size distribution',derived['commit_size_distribution'].items(),'Text lines added + deleted; binary changes excluded')
    if data.get('snapshots'):
        for key in ('bytes','files'): charts['growth-'+key]=growth(data['snapshots'],key)
        with (out/'snapshots.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['hash','date','files','bytes']); w.writeheader(); w.writerows(data['snapshots'])
    for name,content in charts.items(): (out/'images'/f'{name}.svg').write_text(content,encoding='utf-8')
    (out/'derived.json').write_text(json.dumps(derived,ensure_ascii=True,indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n')
    for name,fields in [('files',['path','mode','kind','oid','size']),('commits',['hash','date','author','email','subject']),('contributors',['name','email','commits']),('coupling',['a','b','count','a_to_b','b_to_a','jaccard','lift'])]:
        with (out/(name+'.csv')).open('w',encoding='utf-8',errors='backslashreplace',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(data[name])
    body='<h1>Forklift</h1><p>'+safe(data['repository'])+'</p><p>Revision <code>'+safe(data['revision'])+'</code></p>'
    body+='<nav><a href="summary.json">Raw JSON</a> <a href="derived.json">Derived metrics</a> <a href="relationships.json">Relationships JSON</a></nav>'
    body+=table('Summary',['Metric','Value'],data['summary'].items())
    body+=exports(charts)
    for title,rows,unit in [
        ('Snapshot size by directory',derived['directories'].items(),'Bytes'),
        ('Snapshot size by extension',derived['extensions'].items(),'Bytes'),
        ('Most changed files',[(p,a+d) for p,(a,d,b) in derived['churn'].items()],'Text lines added + deleted'),
        ('Primary authors',[(x['name'],x['commits']) for x in data['contributors']],'Commits'),
        ('Recent monthly activity',list(data['months'].items())[-20:],'Commits'),
        ('Artifact classes',[(k,v['bytes']) for k,v in derived['artifacts'].items()],'Logical bytes'),
        ('Commit size distribution',derived['commit_size_distribution'].items(),'Commits per textual churn interval')]:
        body+=bars(title,list(rows)[:20],unit)
    body+=table('Daily activity',['Date','Commits'],derived['daily'].items())
    if data.get('snapshots'):
        body+=table('Historical snapshots',['Date','Commit','Files','Bytes'],[(r['date'],r['hash'],r['files'],r['bytes']) for r in data['snapshots']])
    body+=table('File coupling (retained pairs)',['File A','File B','Shared commits','Jaccard'],[(r['a'],r['b'],r['count'],round(r['jaccard'],3)) for r in relations['edges']])
    body+=table('Rename transitions',['Date','Commit','Old path','New path'],[(r['date'],r['commit'],r['old'],r['new']) for r in relations['renames']])
    body+=panel(data,relations)
    body+=explorer(data['files'])
    body+=table('Text churn by month',['Month','Added','Deleted','Binary changes'],[(k,*v) for k,v in derived['monthly_churn'].items()])
    body+=table('Architectural incidence',['Category','Commits'],data['incidence'].items())
    body+=table('Exclusive footprints',['Categories','Commits'],[(' + '.join(x['categories']) or 'No files',x['count']) for x in data['footprints']])
    body+=table('Historical coupling',['A','B','Count','A → B','B → A','Jaccard','Lift'],[(x['a'],x['b'],x['count'],*(round(x[k],3) for k in ('a_to_b','b_to_a','jaccard','lift'))) for x in data['coupling']])
    body+=table('Monthly activity',['Month','Commits'],data['months'].items())
    body+=table('Contributors',['Name','Commits'],[(x['name'],x['commits']) for x in data['contributors']])
    body+=table('File modification frequency',['Path','Commits'],data['modifications'].items())
    body+=table('Snapshot files',['Path','Bytes'],[(x['path'],x['size']) for x in data['files']])
    body+=table('Commit history',['Date','Hash','Author','Subject'],[(x['date'],x['hash'][:12],x['author'],x['subject']) for x in data['commits']])
    body='<label>Filter table rows <input id="filter" type="search"></label>'+body+'<script>document.getElementById("filter").addEventListener("input",e=>{for(const r of document.querySelectorAll("tbody tr"))r.hidden=!r.textContent.toLowerCase().includes(e.target.value.toLowerCase())})</script>'
    (out/'index.html').write_text(page('Forklift report',body),encoding='utf-8')
