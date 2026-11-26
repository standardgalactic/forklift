"""Shared native HTML presentation; SVG exports are independent."""
from .visuals import esc
CSS = '''
:root{color-scheme:light dark}body{font:1rem/1.55 system-ui,sans-serif;max-width:76rem;margin:2rem auto;padding:0 1rem;background:Canvas;color:CanvasText}a{color:LinkText}h2{margin-top:2rem}button,input,select{font:inherit;color:CanvasText;background:Canvas;border:1px solid GrayText;padding:.45rem;max-width:100%;box-sizing:border-box}input{width:min(100%,36rem)}button,summary{cursor:pointer}code,pre,td,th,summary,.bar-label{overflow-wrap:anywhere}pre{white-space:pre-wrap;font:inherit}.table-scroll{overflow-x:auto;margin-bottom:1.5rem}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:.6rem;border-bottom:1px solid GrayText;vertical-align:top}th button{border:0;text-align:left;font-weight:bold;padding:0}td[data-number]{font-variant-numeric:tabular-nums;text-align:right}.bar-row{margin:.75rem 0}.bar-label{display:flex;flex-wrap:wrap;justify-content:space-between;gap:.25rem 1rem}.bar-track{height:.65rem;border:1px solid GrayText;border-radius:.2rem;overflow:hidden}.bar-fill{height:100%;background:#267b83}@media(prefers-color-scheme:dark){.bar-fill{background:#72c9d0}}details{margin:.7rem 0}nav a{margin-right:1rem}[hidden]{display:none!important}#tree-tiles{display:block}#tree-tiles button{display:block;width:100%;text-align:left;white-space:normal;overflow-wrap:anywhere;margin:.4rem 0}
'''
SORT = '''<script>document.querySelectorAll('table').forEach(t=>{const body=t.tBodies[0];if(!body)return;t.querySelectorAll('thead th').forEach((h,i)=>{const b=document.createElement('button');b.type='button';b.textContent=h.textContent;h.replaceChildren(b);let dir=1;b.onclick=()=>{const rows=[...body.rows];rows.sort((a,b)=>{const x=a.cells[i],y=b.cells[i];return dir*(x.hasAttribute('data-number')&&y.hasAttribute('data-number')?Number(x.dataset.number)-Number(y.dataset.number):x.textContent.localeCompare(y.textContent,undefined,{numeric:true}))});rows.forEach(r=>body.append(r));t.querySelectorAll('th').forEach(k=>k.removeAttribute('aria-sort'));h.setAttribute('aria-sort',dir===1?'ascending':'descending');dir=-dir}})})</script>'''
def bars(title, rows, unit):
    rows=list(rows); maximum=max([v for _,v in rows]+[1]); parts=[f'<section class="bars"><h2>{esc(title)}</h2><p>{esc(unit)}</p>']
    for label,value in rows:
        parts.append(f'<div class="bar-row"><div class="bar-label"><span>{esc(label)}</span><strong>{value:,}</strong></div><div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:{100*value/maximum:.4f}%"></div></div></div>')
    if not rows: parts.append('<p>No observations</p>')
    return ''.join(parts)+'</section>'
def exports(names):
    return '<details><summary>Optional SVG exports</summary><ul>'+''.join(f'<li><a href="images/{esc(n)}.svg">{esc(n)}</a></li>' for n in names)+'</ul></details>'
def page(title,body):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+esc(title)+'</title><style>'+CSS+'</style></head><body>'+body+SORT+'</body></html>'
