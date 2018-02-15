# FROM jupyter/scipy-notebook:27ba57364579
FROM jupyter/scipy-notebook
RUN conda install -c conda-forge geopy rtree fiona geopandas postgis psycopg2
RUN conda install -c conda-forge altair
RUN pip install astral
CMD start.sh jupyter lab
