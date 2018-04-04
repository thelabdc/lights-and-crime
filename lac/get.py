from functools import partial
from multiprocessing import Pool

import pandas as pd

import geopandas as gpd
import numpy as np

import urllib.request
import geopandas as gpd
import shapely

shapely.speedups.enable()

from pathlib import Path
from dask import delayed

from .dask import persist_disk, pickle_disk


@delayed(pure=True)
def _assign_cols(df, **col_fns):
    return df.assign(
        **{col:fn(df[col]) for [col, fn] in col_fns.items()}
    )

@delayed(pure=True)
def _to_gdf(df, x, y, crs):
    return gpd.GeoDataFrame(
        df,
        crs=crs,
        geometry=[shapely.geometry.Point(xy) for xy in zip(df[x], df[y])]
    )

_download_and_parse = lambda url, name: persist_disk(gpd.read_file, urllib.request.urlretrieve, url, f'data/{name}')

def _download_parse_and_concat(soure_url_and_target_files):
    return delayed(pd.concat, pure=True)(
        [_download_and_parse(source_url, target_file) for [source_url, target_file] in soure_url_and_target_files]
    )

crimes = pickle_disk(
        _assign_cols(
            _download_parse_and_concat([
                ['https://opendata.arcgis.com/datasets/38ba41dd74354563bce28a359b59324e_0.geojson', 'crimes_2018.geojson'],
                ["https://opendata.arcgis.com/datasets/6af5cb8dc38e4bcbac8168b27ee104aa_38.geojson", "crimes_2017.geojson"],
                ["https://opendata.arcgis.com/datasets/bda20763840448b58f8383bae800a843_26.geojson", "crimes_2016.geojson"],
                ["https://opendata.arcgis.com/datasets/35034fcb3b36499c84c94c069ab1a966_27.geojson", "crimes_2015.geojson"],
                ["https://opendata.arcgis.com/datasets/6eaf3e9713de44d3aa103622d51053b5_9.geojson", "crimes_2014.geojson"],
                ["https://opendata.arcgis.com/datasets/5fa2e43557f7484d89aac9e1e76158c9_10.geojson", "crimes_2013.geojson"],
                ["https://opendata.arcgis.com/datasets/010ac88c55b1409bb67c9270c8fc18b5_11.geojson", "crimes_2012.geojson"],
                ["https://opendata.arcgis.com/datasets/9d5485ffae914c5f97047a7dd86e115b_35.geojson", "crimes_2011.geojson"],
                ["https://opendata.arcgis.com/datasets/fdacfbdda7654e06a161352247d3a2f0_34.geojson", "crimes_2010.geojson"],
        ]),
        REPORT_DAT=pd.to_datetime,
        START_DATE=pd.to_datetime,
        END_DATE=partial(pd.to_datetime, errors='coerce'),
        OFFENSE=lambda s: s.astype('category'),
        SHIFT=lambda s: s.astype('category'),
    ).to_crs(
        {'init': 'epsg:2804'}
    ),
    'data/crimes.pickle'
)



roads = pickle_disk(
    _download_and_parse(
        'https://opendata.arcgis.com/datasets/e8299c86b4014f109fedd7e95ae20d52_61.geojson',
        'roads.geojson'
    ).to_crs({'init': 'epsg:2804'}),
    'data/roads.pickle'
)

workorders = pickle_disk(
    _download_and_parse(
        'https://opendata.arcgis.com/datasets/a1dd480eb86445239c8129056ab05ade_0.geojson',
        'workorders.geojson'
    ),
    'data/workorders.pickle'
)

streetlights = pickle_disk(
    _download_and_parse(
        'https://opendata.arcgis.com/datasets/6cb6520725b0489d9a209a337818fad1_90.geojson',
        'streetlights.geojson'
    ),
    'data/streetlights.pickle'
)

service_requests = pickle_disk(
    _download_and_parse(
        'https://opendata.arcgis.com/datasets/96bb7f56588c4d4595933c0ba772b3cb_1.geojson',
        'service_requests.geojson'
    ),
    'data/service-requiests.pickle'
)


repairs = pickle_disk(
    _assign_cols(
        workorders[workorders.DESCRIPTION.str.contains('light', case=False)],
        WORKORDERCLOSEDDATE=pd.to_datetime,
        INITIATEDDATE=pd.to_datetime,
    ).dropna(subset=['INITIATEDDATE', 'WORKORDERCLOSEDDATE']),
    'data/repairs.pickle'
)
