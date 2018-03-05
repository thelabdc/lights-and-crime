from .get import roads
from dask import delayed

from .get import roads

def plot_with_roads(df, **plot_kwargs):
    base = roads.plot(color='white', edgecolor='black', figsize=[40, 40], linewidth=0.1)
    return df.plot(ax=base, **plot_kwargs)