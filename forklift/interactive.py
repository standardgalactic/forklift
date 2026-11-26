"""Bounded historical association and offline interactive exploration."""
from collections import Counter, defaultdict
from itertools import combinations
import json


def relationships(data, max_paths=100, max_pairs=200):
    frequency = Counter()
    for c in data['commits']:
        frequency.update({x['path'] for x in c['changes']})
    selected = set(sorted(frequency, key=lambda p: (-frequency[p], p))[:max_paths])
    pairs = Counter()
    renames = []
    for c in data['commits']:
        paths = sorted({x['path'] for x in c['changes']} & selected)
        pairs.update(combinations(paths, 2))
        for x in c['changes']:
            if 'old_path' in x:
                renames.append(dict(old=x['old_path'], new=x['path'], commit=c['hash'], date=c['date']))
    edges = [dict(a=a,b=b,count=n,jaccard=n/(frequency[a]+frequency[b]-n)) for (a,b),n in sorted(pairs.items(),key=lambda x:(-x[1],x[0]))[:max_pairs]]
    return dict(nodes=[dict(path=p,commits=frequency[p]) for p in sorted(selected)], edges=edges, renames=renames, policy=dict(max_paths=max_paths,max_pairs=max_pairs,observed_pairs=len(pairs),rename_identity='path transitions only'))


def panel(data, relations):
    payload=json.dumps(dict(files=[dict(path=f['path'],size=f['size'] or 0) for f in data['files']], commits=data['commits'], **relations),ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return '''<section id="explore"><h2>Interactive repository exploration</h2><h3>Directory drill-down</h3><button id="tree-up">Parent directory</button><p id="tree-path"></p><div class="tiles" id="tree-tiles"></div><p id="tree-info"></p><h3>Commit explorer</h3><label>Search commits <input id="commit-query" type="search"></label><select id="commit-select" aria-label="Commit"></select><button id="commit-prev">Previous</button><button id="commit-next">Next</button><pre id="commit-detail"></pre><h3>File coupling explorer</h3><p>Top 100 modified paths; up to 200 strongest co-occurrences. Select a file to inspect its neighbors.</p><label>File <select id="network-select"></select></label><pre id="network-detail"></pre><h3>Observed rename transitions</h3><label>Filter paths <input id="rename-query" type="search"></label><pre id="rename-detail"></pre></section><script type="application/json" id="explore-data">'''+payload+'''</script><script>
(()=>{const d=JSON.parse(document.getElementById('explore-data').textContent), $=id=>document.getElementById(id), fmt=n=>n.toLocaleString();let prefix='';
function tree(){const groups=new Map();for(const f of d.files){if(!f.path.startsWith(prefix))continue;const rest=f.path.slice(prefix.length),i=rest.indexOf('/'),k=i<0?rest:rest.slice(0,i+1);const g=groups.get(k)||{size:0,count:0};g.size+=f.size;g.count++;groups.set(k,g)}const entries=[...groups].sort((a,b)=>b[1].size-a[1].size),total=entries.reduce((n,x)=>n+x[1].size,0);$('tree-path').textContent=prefix||'/';$('tree-up').disabled=!prefix;$('tree-tiles').replaceChildren();for(const [k,g] of entries){const b=document.createElement('button');b.className='tile';b.textContent=`${k} — ${fmt(g.size)} bytes (${g.count} files)`;b.title=`${k}: ${fmt(g.size)} bytes, ${g.count} files`;b.onclick=()=>{if(k.endsWith('/')){prefix+=k;tree()}else $('tree-info').textContent=b.title};$('tree-tiles').append(b)}$('tree-info').textContent=`${fmt(total)} bytes; ${entries.length} entries`} $('tree-up').onclick=()=>{prefix=prefix.slice(0,-1).split('/').slice(0,-1).join('/');if(prefix)prefix+='/';tree()};tree();
let matches=[];function detail(){const c=matches[Number($('commit-select').value)];$('commit-detail').textContent=c?`${c.hash}\\n${c.date} · ${c.author}\\n${c.subject}\\n\\n`+c.changes.map(x=>`${x.old_path?x.old_path+' → ':''}${x.path}  +${x.added??'binary'} −${x.deleted??'binary'}`).join('\\n'):'No matching commits'}function search(){const q=$('commit-query').value.toLowerCase();matches=d.commits.filter(c=>[c.hash,c.author,c.subject,c.date].join(' ').toLowerCase().includes(q));$('commit-select').replaceChildren();matches.forEach((c,i)=>$('commit-select').add(new Option(c.hash.slice(0,8)+' '+c.subject,i)));detail()}$('commit-query').oninput=search;$('commit-select').onchange=detail;for(const [id,step] of [['commit-prev',-1],['commit-next',1]])$(id).onclick=()=>{$('commit-select').selectedIndex=Math.max(0,Math.min(matches.length-1,$('commit-select').selectedIndex+step));detail()};search();
d.nodes.forEach(n=>$('network-select').add(new Option(n.path,n.path)));function neighbors(){const p=$('network-select').value;$('network-detail').textContent=d.edges.filter(e=>e.a===p||e.b===p).map(e=>`${e.a===p?e.b:e.a}: ${e.count} commits; Jaccard ${e.jaccard.toFixed(3)}`).join('\\n')||'No retained edges'}$('network-select').onchange=neighbors;neighbors();function renames(){const q=$('rename-query').value.toLowerCase();$('rename-detail').textContent=d.renames.filter(r=>(r.old+' '+r.new).toLowerCase().includes(q)).map(r=>`${r.date} ${r.commit.slice(0,8)} ${r.old} → ${r.new}`).join('\\n')||'No observed rename transitions (enable --renames during extraction).'}$('rename-query').oninput=renames;renames();})();</script>'''
