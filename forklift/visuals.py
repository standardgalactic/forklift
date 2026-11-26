"""Derived metrics and dependency-free, standalone SVG figures."""
from collections import Counter, defaultdict
from pathlib import PurePosixPath
from html import escape

def metrics(data):
    extensions=Counter(); directories=Counter(); churn=defaultdict(lambda: [0,0,0]); daily=Counter(); monthly=defaultdict(lambda:[0,0,0])
    for f in data['files']:
        p=PurePosixPath(f['path']); size=f['size'] or 0
        extensions[p.suffix.lower() or '(none)']+=size
        directories[p.parts[0] if len(p.parts)>1 else '(root)']+=size
    for c in data['commits']:
        daily[c['date'][:10]]+=1
        for x in c['changes']:
            for v in (churn[x['path']],monthly[c['date'][:7]]):
                if x['added'] is None or x['deleted'] is None: v[2]+=1
                else: v[0]+=x['added']; v[1]+=x['deleted']
    return dict(extensions=dict(extensions.most_common()),directories=dict(directories.most_common()),daily=dict(sorted(daily.items())),churn=dict(sorted(churn.items(),key=lambda x:sum(x[1][:2]),reverse=True)),monthly_churn=dict(sorted(monthly.items())))

def esc(x):
    return escape(str(x).encode('utf-8','backslashreplace').decode())

def svg(title, rows, unit):
    rows=list(rows)[:20]; h=95+34*max(1,len(rows)); maximum=max([v for _,v in rows]+[1]); parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {h}" role="img" aria-label="{esc(title)}"><rect width="900" height="{h}" fill="#ffffff"/><g font-family="system-ui,sans-serif" fill="#000000"><text x="20" y="30" font-size="24" font-weight="bold">{esc(title)}</text><text x="20" y="52" font-size="16">{esc(unit)}</text>']
    for i,(label,value) in enumerate(rows):
        y=70+i*34; short=label if len(label)<=28 else '…'+label[-27:]; w=360*value/maximum
        parts.append(f'<g><title>{esc(label)}: {value:,}</title><text x="20" y="{y+15}" font-size="16">{esc(short)}</text><rect x="390" y="{y}" width="{w:.2f}" height="19" rx="2" fill="#347b83"/><text x="{400+w:.2f}" y="{y+15}" font-size="16">{value:,}</text></g>')
    if not rows: parts.append('<text x="20" y="80">No observations</text>')
    return ''.join(parts)+'</g></svg>'

def heatmap(data):
    names=list(data['incidence']); n=len(names); size=48; offset=300; width=max(500,offset+n*size+20); height=offset+n*size+40
    lookup={(x['a'],x['b']):x['count'] for x in data['coupling']}; lookup.update({(b,a):v for (a,b),v in list(lookup.items())})
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Conditional co-occurrence"><rect width="100%" height="100%" fill="#ffffff"/><g font-family="system-ui,sans-serif" fill="#000000"><text x="15" y="25" font-size="24" font-weight="bold">Conditional co-occurrence (%)</text><text x="15" y="45" font-size="16">Row category → column category</text>']
    for i,a in enumerate(names):
        y=offset+i*size; x=offset+i*size
        parts.append(f'<text x="{offset-8}" y="{y+24}" text-anchor="end" font-size="16">{esc(a)}</text><text transform="translate({x+24},{offset-8}) rotate(-60)" font-size="16">{esc(a)}</text>')
        for j,b in enumerate(names):
            v=100*(data['incidence'][a] if a==b else lookup.get((a,b),0))/data['incidence'][a]; shade=round(245-110*v/100); xx=offset+j*size
            parts.append(f'<g><title>{esc(a)} → {esc(b)}: {v:.1f}%</title><rect x="{xx}" y="{y}" width="46" height="46" fill="rgb({shade},{min(255,shade+20)},{min(255,shade+30)})"/><text x="{xx+23}" y="{y+29}" text-anchor="middle" font-size="16" fill="#000000">{v:.0f}</text></g>')
    return ''.join(parts)+'</g></svg>'

def figures(data,out):
    m=metrics(data); out.mkdir(parents=True,exist_ok=True)
    charts={'snapshot-directories':svg('Snapshot size by top-level directory',m['directories'].items(),'Bytes'), 'snapshot-extensions':svg('Snapshot size by extension',m['extensions'].items(),'Bytes'), 'file-churn':svg('Most changed files',((p,a+d) for p,(a,d,b) in m['churn'].items()),'Added + deleted text lines'), 'contributors':svg('Primary authors',((x['name'],x['commits']) for x in data['contributors']),'Commits'), 'activity':svg('Recent monthly activity',list(data['months'].items())[-20:],'Commits'), 'architecture-coupling':heatmap(data)}
    for name,content in charts.items(): (out/f'{name}.svg').write_text(content,encoding='utf-8')
    return charts
