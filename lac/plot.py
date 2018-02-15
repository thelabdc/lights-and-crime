def plot_with_roads(roads, df, **plot_kwargs):
    base = roads.plot(color='white', edgecolor='black', figsize=[40, 40], linewidth=0.1)
    df.plot(ax=base, **plot_kwargs)