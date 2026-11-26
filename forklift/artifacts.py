from pathlib import PurePosixPath
from collections import Counter
from .visuals import svg,esc

def classify(path):
    p=PurePosixPath(path); ext=p.suffix.lower()
    if any(x in p.parts for x in ('node_modules','vendor','.venv')) or p.name in ('package-lock.json','bun.lock','Cargo.lock'): return 'Dependencies'
    if ext in ('.aux','.log','.out','.toc','.fls','.fdb_latexmk','.pyc','.synctex') or p.name.endswith('.synctex.gz'): return 'Likely generated'
    if ext in ('.tex','.bib','.md','.rst','.org'): return 'Manuscripts and documentation'
    if ext in ('.pdf','.png','.jpg','.jpeg','.svg','.gif','.mp3','.mp4','.wav','.webp'): return 'Documents and media'
    if ext in ('.py','.js','.ts','.tsx','.c','.cpp','.rs','.go','.sh','.html','.css','.java'): return 'Source'
    return 'Other'

def artifacts(files):
    counts=Counter(); sizes=Counter()
    for f in files:
        k=classify(f['path']); counts[k]+=1; sizes[k]+=f['size'] or 0
    return {k:{'files':counts[k],'bytes':sizes[k]} for k in counts}

def treemap(files):
    # Proportional slice-and-dice layout, grouped by directory; zero-size entries omitted.
    groups={}
    for f in files:
        if not f['size']: continue
        p=PurePosixPath(f['path']); k=p.parts[0] if len(p.parts)>1 else '(root)'; groups.setdefault(k,[]).append(f)
    total=sum(f['size'] for fs in groups.values() for f in fs); x=0; parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="File size treemap"><rect width="900" height="420" fill="#ffffff"/><text x="10" y="22" font-family="sans-serif" font-size="24" font-weight="bold" fill="#000000">File sizes by directory (hover for path)</text>']
    for i,(k,fs) in enumerate(sorted(groups.items(),key=lambda item:-sum(f['size'] for f in item[1]))):
        subtotal=sum(f['size'] for f in fs); w=900*subtotal/total; y=35
        for f in sorted(fs,key=lambda f:-f['size']):
            h=385*f['size']/subtotal; parts.append(f'<g tabindex="0"><title>{esc(f["path"])}: {f["size"]:,} bytes</title><rect x="{x:.5f}" y="{y:.5f}" width="{w:.5f}" height="{h:.5f}" fill="hsl({(i*67)%360},40%,65%)" stroke="white" stroke-width="0.3"/></g>'); y+=h
        if w>100: parts.append(f'<text x="{x+3:.3f}" y="52" font-size="16" fill="#000000" stroke="#ffffff" stroke-width="3" paint-order="stroke" pointer-events="none">{esc(k[:max(1,int((w-8)/10))])}</text>')
        x+=w
    if not total: parts.append('<text x="10" y="60">No positive-size files</text>')
    return ''.join(parts)+'</svg>'
