#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 13:41:24 2018

@author: Garrett

iSlims getting back inventoryID
"""

#%% Packages

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from __future__ import (absolute_import, division, print_function)
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import datetime as dt


#%% Choice
Windows = 'C:/Users/paperspace/Documents/GitHub/lights-and-crime/Lights and Crime Garrett/Data'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Windows

#%% Dats set prepping
isf = pd.read_excel(choice + '/Lights.xlsx')
inv = pd.read_excel(choice + '/islims_inventory.xlsx')
wo = pd.read_excel(choice + '/islims_workorders.xlsx')
wo = wo.rename(columns={'woID':'WoID'})
NCR = pd.read_excel(choice + '/NCR.xlsx')

isf_wo = pd.merge(isf, wo, how='left', on = 'WoID')
isf_wo = isf_wo.drop(['srchAssetID', 'gpscoordinateX', 'gpscoordinateY', 'initialproblemID', \
       'resolveddatetime', 'entereddate', 'finalresolutionID'], axis = 1)

isf_wo_inv = pd.merge(isf_wo, inv, how='left', on = 'inventoryID')
isf_wo_inv = isf_wo_inv.drop(['gpscoordinateX', 'gpscoordinateY'], axis = 1)

#%% geo join
# Setting up data into geopandas
geometry = [Point(xy) for xy in zip(isf_wo_inv['gpsX'], isf_wo_inv['gpsY'])]
gLights = GeoDataFrame(isf_wo_inv, geometry=geometry)
gLights = gLights.drop_duplicates(subset = ['WoID'])
geometry = [Point(xy) for xy in zip(NCR['gpsX'], NCR['gpsY'])]
gNCR = GeoDataFrame(NCR, geometry=geometry)

BUFFER = .000625 # 1/4th of a city block in radius of Maryland coordinates.
#BUFFER = .00125 # 1/2 of a city block in radius of Maryland coordinates.

gLights_Buff = gLights.assign(geometry = lambda x: x.geometry.buffer(BUFFER)) 
# Overwrites geometry variable with a buffer centered at the point of interest. A.k.a. applies the function geometry(x) to gNCR and saves it as geometry.

#%% Filtering
Matched_Lights = gpd.sjoin(gLights_Buff, gNCR, 'left')

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

Matched_Lights0.to_excel(choice + '/inv_geoLights0.xlsx')
Matched_Lights1.to_excel(choice + '/inv_geolights1.xlsx')
