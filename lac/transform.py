import geopandas as gpd
import numpy as np
from astral import Astral
from functools import lru_cache
from dask import delayed
from .get import repairs, crimes
from .dask import pickle_disk

WITHIN_M = 100

repairs_circles = repairs.assign(
    circles_geometry=repairs.geometry.buffer(WITHIN_M)
).set_geometry('circles_geometry')


repairs_with_crimes = pickle_disk(
    delayed(gpd.sjoin, pure=True)(repairs_circles, crimes, 'left').dropna(
        subset=['START_DATE', 'Day of Datewoclosed'],
        how='any'
    ).assign(
        is_day=lambda df: df['START_DATE'].apply(is_day),
        rel_days=lambda df: np.floor((df['START_DATE'] - df['Day of Datewoclosed']) / np.timedelta64(1, 'D'))
    ),
    'data/repairs_with_crimes.pickle'
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
