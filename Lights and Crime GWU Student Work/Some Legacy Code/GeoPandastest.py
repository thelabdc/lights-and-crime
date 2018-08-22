#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:55:50 2018

@author: Garrett
"""

#%% Packages

# %matplotlib inline #used for notebook grpahs

from __future__ import (absolute_import, division, print_function)
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import datetime as dt

#%% Data
Windows = 'C:/Users/Sade/Documents/GitHub/lights-and-crime/Lights and Crime Garrett/Data'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Linux

Lights = pd.read_excel(choice + '/Lights.xlsx')
NCR = pd.read_excel(choice + '/NCR.xlsx')

# Setting up data into geopandas
geometry = [Point(xy) for xy in zip(Lights['gpsX'], Lights['gpsY'])]
gLights = GeoDataFrame(Lights, geometry=geometry)
gLights = gLights.drop_duplicates(subset = ['WoID'])
geometry = [Point(xy) for xy in zip(NCR['X'], NCR['Y'])]
gNCR = GeoDataFrame(NCR, geometry=geometry)

BUFFER = .000625 # 1/4th of a city block in radius of Maryland coordinates.
#BUFFER = .00125 # 1/2 of a city block in radius of Maryland coordinates.

gLights_Buff = gLights.assign(geometry = lambda x: x.geometry.buffer(BUFFER)) 
# Overwrites geometry variable with a buffer centered at the point of interest. A.k.a. applies the function geometry(x) to gNCR and saves it as geometry.

Matched_Lights = gpd.sjoin(gLights_Buff, gNCR, 'left') #2467865 observations after join
# Left geojoin by buffer

#%% Filtering

Matched_Lights['Tdelta'] = [0]*len(Matched_Lights) # Counter to be used

Matched_Lights = Matched_Lights.dropna(subset = ['WoCompleted'])
Matched_Lights = Matched_Lights.dropna(subset = ['REPORT_DAT'])
Matched_Lights = Matched_Lights.reset_index()

# Flagging possible lights that influenced crime:
for i in range(len(Matched_Lights)):
    try:
        if abs(Matched_Lights.loc[i, 'WoCompleted'] - Matched_Lights.loc[i, 'REPORT_DAT']).days <= 10:
            Matched_Lights.loc[i, 'Tdelta'] = 1
    except:
        Matched_Lights.loc[i, 'WoCompleted'] = dt.datetime.strptime(Matched_Lights.loc[i, 'WoCompleted'], '%Y-%m-%dT%H:%M:%S.%fZ') # Some values coded incorrectly.
        if abs(Matched_Lights.loc[i, 'WoCompleted'] - Matched_Lights.loc[i, 'REPORT_DAT']).days <= 10:
            Matched_Lights.loc[i, 'Tdelta'] = 1

sum(Matched_Lights['Tdelta'])/len(Matched_Lights) # Very Rough Hit Ratio = .005% (Number of possible crimes to be linked with a light outage)

# Lights matched with a crime nearby outside of likely bulb outage
Matched_Lights0 = Matched_Lights[Matched_Lights['Tdelta'] == 0].drop_duplicates(subset = ['WoID'])

# Lights matched with a crime nearby within timeframe of light outage
Matched_Lights1 = Matched_Lights[Matched_Lights['Tdelta'] == 1].drop_duplicates(subset = ['OBJECTID'])

# Other light outages were unmatched.

#%% To excel

Matched_Lights0.to_excel(choice + '/geoLights0test.xlsx')
Matched_Lights1.to_excel(choice + '/geolights1test.xlsx')

Matched_NLights0 = pd.read_excel(choice + '/geoLights0Ntest.xlsx')
Matched_NLights1 = pd.read_excel(choice + '/geolights1Ntest.xlsx')
