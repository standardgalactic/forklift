"""Additional offline figures and directory explorer."""
from collections import Counter, defaultdict
from datetime import date,timedelta
from .visuals import esc,svg

def distribution(data):
    counts=Counter()
    for c in data['commits']:
        n=sum((x['added'] or 0)+(x['deleted'] or 0) for x in c['changes'])
        counts[next(label for upper,label in [(0,'0'),(10,'1–10'),(100,'11–100'),(1000,'101–1,000'),(10000,'1,001–10,000'),(float('inf'),'>10,000')] if n<=upper)]+=1
    return {k:counts[k] for k in ['0','1–10','11–100','101–1,000','1,001–10,000','>10,000']}

def calendar(daily):
    end=date.fromisoformat(max(daily)) if daily else date.today(); start=end-timedelta(days=363); start-=timedelta(days=start.weekday())
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 160" role="img" aria-label="Commit calendar"><rect width="900" height="160" fill="#ffffff"/><g font-family="system-ui" fill="#000000"><text x="15" y="24" font-size="24" font-weight="bold">Commit calendar (latest 52 weeks)</text>']
    for i in range((end-start).days+1):
        day=start+timedelta(days=i); n=daily.get(day.isoformat(),0); x=40+15*(i//7); y=42+15*(i%7); color=['#edf2f5','#b8d9d7','#72b4b0','#347b83','#17484e'][min(4,n.bit_length())]
        parts.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{color}"><title>{day}: {n} commits</title></rect>')
    return ''.join(parts)+'</g></svg>'

def growth(rows,key):
    maximum=max([r[key] for r in rows]+[1]); points=[]; marks=[]
    for i,r in enumerate(rows):
        x=65+790*i/max(1,len(rows)-1); y=210-155*r[key]/maximum; points.append(f'{x:.2f},{y:.2f}'); marks.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#347b83"><title>{esc(r["date"])} {r[key]:,} {key} ({esc(r["hash"][:12])})</title></circle>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 250"><rect width="900" height="250" fill="#ffffff"/><g font-family="system-ui" fill="#000000"><text x="15" y="25" font-size="24" font-weight="bold">Historical snapshot {key} (commit order)</text><text x="65" y="49" font-size="16">{maximum:,}</text><path d="M65 55 V210 H855" fill="none" stroke="#aaa"/><polyline points="{" ".join(points)}" fill="none" stroke="#347b83" stroke-width="2"/>{"".join(marks)}<text x="65" y="235" font-size="16">{len(rows)} sampled first-parent commits</text></g></svg>'

def explorer(files):
    root={}
    for f in files:
        node=root
        for part in f['path'].split('/')[:-1]: node=node.setdefault(part,{})
        node[f['path'].split('/')[-1]]=f['size'] or 0
    def walk(node):
        total=0; html=[]
        for k,v in sorted(node.items()):
            if isinstance(v,dict):
                size,inner=walk(v); total+=size; html.append(f'<details><summary>{esc(k)}/ ({size:,} bytes)</summary>{inner}</details>')
            else: total+=v; html.append(f'<div>{esc(k)} ({v:,} bytes)</div>')
        return total,'<div style="padding-left:1em">'+''.join(html)+'</div>'
    return '<h2>Directory explorer</h2>'+walk(root)[1]
