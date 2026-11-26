#!/usr/bin/env python3
"""Measure analysis and rendering separately; save observations as JSON."""
import argparse,json,time,resource,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from forklift import git
from forklift.analysis import analyze
from forklift.render import write_report
p=argparse.ArgumentParser(); p.add_argument('repository'); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
with patch.object(git,'git',wraps=git.git) as calls:
    start=time.perf_counter(); data=analyze(a.repository); analysis=time.perf_counter()-start
    start=time.perf_counter(); write_report(data,a.output/'report'); rendering=time.perf_counter()-start
    result=dict(revision=data['revision'],analysis_seconds=analysis,render_seconds=rendering,git_calls=calls.call_count,peak_python_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,report_bytes=sum(p.stat().st_size for p in (a.output/'report').rglob('*') if p.is_file()))
(a.output/'benchmark.json').write_text(json.dumps(result,indent=2)+'\n')
