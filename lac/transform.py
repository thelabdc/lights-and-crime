import geopandas as gpd
import numpy as np
from astral import Astral
from functools import lru_cache


def repairs_to_circles(repairs, within_m):
    return repairs.assign(
        circles_geometry=repairs.geometry.buffer(within_m)
    ).set_geometry('circles_geometry')


def create_repairs_with_crimes(repairs_circles, crimes):
    return gpd.sjoin(repairs_circles, crimes, 'left').dropna(
        subset=['START_DATE', 'Day of Datewoclosed'],
        how='any'
    ).assign(
        is_day=lambda df: df['START_DATE'].apply(is_day)
    )


a = Astral()
city = a['Washington DC']


@lru_cache(maxsize=None)
def sunrise(d):
    return city.sunrise(d).replace(tzinfo=None)

@lru_cache(maxsize=None)
def sunset(d):
    return city.sunset(d).replace(tzinfo=None)

def is_day(datetime):
    date = datetime.date()
    return sunrise(date) < datetime < sunset(date)
