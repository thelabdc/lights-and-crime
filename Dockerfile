# FROM jupyter/scipy-notebook:27ba57364579
FROM jupyter/scipy-notebook
RUN conda install -y -c conda-forge \
    geopy \
    rtree \
    fiona \
    geopandas \
    dask \
    distributed \
    python-graphviz

RUN jupyter labextension install @jupyterlab/vega3-extension
RUN pip install astral git+https://github.com/altair-viz/altair cachey
CMD start.sh jupyter lab
