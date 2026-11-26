from pathlib import Path

def plots(data,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    for name,values in [('incidence',data['incidence']),('monthly',data['months']),('modifications',dict(list(data['modifications'].items())[:20]))]:
        fig,ax=plt.subplots(figsize=(10,6)); ax.barh(list(values)[::-1],list(values.values())[::-1]); ax.set_xlabel('Commits'); ax.set_title(name.capitalize()); fig.tight_layout()
        for ext in ('svg','png','pdf'): fig.savefig(out/f'{name}.{ext}')
        plt.close(fig)
