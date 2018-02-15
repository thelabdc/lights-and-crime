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

def get_repairs():
    """
    <class 'geopandas.geodataframe.GeoDataFrame'>
    Int64Index: 9477 entries, 0 to 9506
    Data columns (total 7 columns):
    Description (Workorder)    9477 non-null object
    Applytoentity              9477 non-null object
    311 SR #                   9477 non-null object
    Woxcoordinate              9477 non-null float64
    Woycoordinate              9477 non-null float64
    Day of Datewoclosed        9477 non-null datetime64[ns]
    geometry                   9477 non-null object
    dtypes: datetime64[ns](1), float64(2), object(4)
    memory usage: 592.3+ KB
    """
    return _assign_cols(
        _to_gdf(
            pd.read_excel(
                'data/repairs.xlsx',
                thousands=',',
                converters={
                    'Day of Datewoclosed': pd.to_datetime
                },
                na_values='0'
            ).dropna(),
            x='Woxcoordinate',
            y='Woycoordinate',
            crs={"init": "EPSG:2804"}
        ).rename(index=str, columns={
            "Description (Workorder)": "description"
        }),
        description=lambda s: s.astype('category'),
        Applytoentity=lambda s: s.astype('category'),
    )


def get_crimes():
    """
    Int64Index: 284454 entries, 0 to 31582
    Data columns (total 23 columns):
    CCN                     284454 non-null object
    REPORT_DAT              284454 non-null object
    SHIFT                   284454 non-null object
    METHOD                  284454 non-null object
    OFFENSE                 284454 non-null object
    BLOCK                   284454 non-null object
    XBLOCK                  284454 non-null float64
    YBLOCK                  284454 non-null float64
    WARD                    284442 non-null object
    ANC                     284454 non-null object
    DISTRICT                284291 non-null object
    PSA                     284273 non-null object
    NEIGHBORHOOD_CLUSTER    280819 non-null object
    BLOCK_GROUP             283595 non-null object
    CENSUS_TRACT            283595 non-null object
    VOTING_PRECINCT         284387 non-null object
    LATITUDE                284454 non-null float64
    LONGITUDE               284454 non-null float64
    BID                     46117 non-null object
    START_DATE              284446 non-null object
    END_DATE                274756 non-null object
    OBJECTID                284454 non-null int64
    geometry                284454 non-null object
    dtypes: float64(4), int64(1), object(18)
    memory usage: 52.1+ MB
    """
    return _assign_cols(
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
    )



def get_roads():
    return gpd.read_file("data/Roads_All").to_crs({'init': 'epsg:2804'})


def get_workorders():
    return _download_and_parse(
        'https://opendata.arcgis.com/datasets/a1dd480eb86445239c8129056ab05ade_0.geojson',
        'workorders.geojson'
    )

def get_streetlights():
    """
    RangeIndex: 70207 entries, 0 to 70206
    Data columns (total 96 columns):
    OBJECTID                   70207 non-null int64
    FACILITYID                 70206 non-null object
    PEPCOLIGHTID               29376 non-null object
    ASSETTYPE                  70207 non-null int64
    ISMETERED                  70201 non-null float64
    LIGHTTYPE                  70165 non-null float64
    POLETYPE                   69999 non-null object
    POLEHEIGHT                 69803 non-null object
    POWERFEED                  70190 non-null float64
    NUMBERARMS                 66316 non-null float64
    PROXIMITY                  70055 non-null float64
    STREETNAME                 70207 non-null object
    QUADRANT                   70207 non-null int64
    CROSSSTREET                70136 non-null object
    ROADTYPE                   70207 non-null int64
    OWNER                      70207 non-null int64
    WARD                       70207 non-null int64
    COMMENTS                   2573 non-null object
    HOUSENO                    69370 non-null object
    RMS                        70185 non-null float64
    STREETSEGMID               70207 non-null int64
    OTHEREQUIPMENT             5088 non-null object
    CONDITION                  3943 non-null float64
    CREATED_USER               3425 non-null object
    CREATED_DATE               3425 non-null object
    LASTMODIFIED               10851 non-null object
    LIGHTHISTORY               69092 non-null object
    INOPERATION                3937 non-null object
    ADDTOGIS                   70201 non-null object
    ADDEDBY                    70207 non-null object
    WHATMODIFIED               11374 non-null object
    LASTLOGGED                 70207 non-null object
    LOGGEDBY                   70207 non-null object
    STREETLIGHTID              70206 non-null object
    SHIELD                     44 non-null object
    LASTPAINTED                8914 non-null object
    LEDINOPERATION             5409 non-null object
    XCOORDINAT                 70207 non-null float64
    YCOORDINAT                 70207 non-null float64
    ISMETERED_DESC             70201 non-null object
    LIGHTTYPE_DESC             70057 non-null object
    POLETYPE_DESC              34413 non-null object
    POLEHEIGHT_DESC            69763 non-null object
    POWERFEED_DESC             70186 non-null object
    NUMBERARMS_DESC            66316 non-null object
    PROXIMITY_DESC             70055 non-null object
    QUADRANT_DESC              70207 non-null object
    ROADTYPE_DESC              70207 non-null object
    OWNER_DESC                 70207 non-null object
    WARD_DESC                  70207 non-null object
    RMS_DESC                   70185 non-null object
    CONDITION_DESC             3942 non-null object
    SHIELD_DESC                39 non-null object
    GLOBALID                   70207 non-null object
    LAST_EDITED_USER           0 non-null object
    LAST_EDITED_DATE           0 non-null object
    POLECOLOR                  18842 non-null object
    AFFILIATION                4175 non-null object
    SCRATCH                    70200 non-null object
    CCT                        5411 non-null object
    WATTAGE1                   70135 non-null object
    WATTAGE1_DESC              69981 non-null object
    POLECOMPOSITION            69849 non-null object
    POLECOMPOSITION_DESC       69849 non-null object
    ARMLENGTH1                 66311 non-null float64
    ARMLENGTH1_DESC            66309 non-null object
    NUMBERLIGHTS               70207 non-null int64
    NUMBERLIGHTS_DESC          70202 non-null object
    FIXTURESTYLE               70178 non-null float64
    FIXTURESTYLE_DESC          70174 non-null object
    TRAFFICCOMBO               69851 non-null object
    TRAFFICCOMBO_DESC          345 non-null object
    OTHEREQUIPMENT_DESC        340 non-null object
    LIGHTMANUFACTURER          63729 non-null object
    LIGHTMANUFACTURER_DESC     63729 non-null object
    TBASETYPE                  69715 non-null object
    TBASETYPE_DESC             69715 non-null object
    POLECOLOR_DESC             17908 non-null object
    CCT_DESC                   5411 non-null object
    INSPECTIONGROUP            9235 non-null object
    ASSETSTATUS                70207 non-null object
    ASSETSTATUS_DESC           70207 non-null object
    WHYINACTIVE                0 non-null object
    WATTAGE2                   2839 non-null object
    WATTAGE2_DESC              2829 non-null object
    FEEDMANHOLE                70 non-null object
    FEEDMANHOLE_DESC           70 non-null object
    ARMSTYLE                   56650 non-null object
    ARMSTYLE_DESC              56650 non-null object
    ARMLENGTH2                 402 non-null float64
    ARMLENGTH2_DESC            402 non-null object
    ROADCLASSIFICATION         70203 non-null float64
    ROADCLASSIFICATION_DESC    70203 non-null object
    ISMODIFIED                 559 non-null object
    ISMODIFIED_DESC            551 non-null object
    geometry                   70207 non-null object
    dtypes: float64(13), int64(8), object(75)
    memory usage: 51.4+ MB
    """
    return _download_and_parse(
        'https://opendata.arcgis.com/datasets/6cb6520725b0489d9a209a337818fad1_90.geojson',
        'streetlights.geojson'
    )


def _assign_cols(df, **col_fns):
    return df.assign(
        **{col:fn(df[col]) for [col, fn] in col_fns.items()}
    )

def _to_gdf(df, x, y, crs):
    return gpd.GeoDataFrame(
        df,
        crs=crs,
        geometry=[shapely.geometry.Point(xy) for xy in zip(df[x], df[y])]
)

def _check_download(source_url, target_file):
    if Path(target_file).is_file():
        print(f'{target_file} exists; skipping download')
    else: 
        print(f'downloading {target_file} to {target_file}')
        urllib.request.urlretrieve(source_url, target_file)  

def _download_and_parse(source_url, target_file):
    target_file = f'data/{target_file}'
    _check_download(source_url, target_file)
    print(f'reading {target_file} into geopandas')
    return gpd.read_file(target_file)

def _download_parse_and_concat(soure_url_and_target_files):
    with Pool() as pool:
        return pd.concat(
            pool.starmap(_download_and_parse, soure_url_and_target_files, 1)
        )