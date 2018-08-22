#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 12:05:33 2018

@author: sade
"""
from __future__ import (absolute_import, division, print_function)
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import datetime as dt
import progressbar #used progressbar2

Windows = 'C:/Users/Sade/Documents/GitHub/lights-and-crime/Lights and Crime Garrett/Data'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Linux

isf = pd.read_excel(choice + '/Lights.xlsx') # (from 0.0a)
inv = pd.read_excel(choice + '/islims_inventory.xlsx') # (see 0.0a iSlims and City Work Data)
wo = pd.read_excel(choice + '/islims_workorders.xlsx') # (see 0.0a iSlims and City Work Data)
NCR2 = pd.read_excel(choice + '/NCR.xlsx') # (from 0.0a)
DCR = pd.read_excel(choice + '/DCR.xlsx') # (from 0.0a)

wo = wo.rename(columns={'woID':'WoID'})
isf_wo = pd.merge(isf, wo, how='left', on = 'WoID')
isf_wo = isf_wo.drop(['srchAssetID', 'gpscoordinateX', 'gpscoordinateY', 'initialproblemID', \
       'resolveddatetime', 'entereddate', 'finalresolutionID'], axis = 1)
isf_wo_inv = pd.merge(isf_wo, inv, how='left', on = 'inventoryID')
isf_wo_inv = isf_wo_inv.drop(['gpscoordinateX', 'gpscoordinateY'], axis = 1)

# Setting up data into geopandas
geometry = [Point(xy) for xy in zip(isf_wo_inv['gpsX'], isf_wo_inv['gpsY'])]
gLights2 = GeoDataFrame(isf_wo_inv, geometry=geometry)
gLights2 = gLights2.drop_duplicates(subset = ['WoID'])
geometry = [Point(xy) for xy in zip(NCR2['X'], NCR2['Y'])]
gNCR2 = GeoDataFrame(NCR2, geometry=geometry)

BUFFER = .000625 # 1/4th of a city block in radius of Maryland coordinates.
#BUFFER = .00125 # 1/2 of a city block in radius of Maryland coordinates.

gLights_Buff2 = gLights2.assign(geometry = lambda x: x.geometry.buffer(BUFFER)) 
# Overwrites geometry variable with a buffer centered at the point of interest. A.k.a. applies the function geometry(x) to gNCR and saves it as geometry.

Matched_NLights = gpd.sjoin(gLights_Buff2, gNCR2, 'left')

Matched_NLights['Crime_LO_intime'] = [0]*len(Matched_NLights) # Counter to be used

Matched_NLights = Matched_NLights.dropna(subset = ['WoCompleted'])
Matched_NLights = Matched_NLights.dropna(subset = ['REPORT_DAT'])
Matched_NLights = Matched_NLights.reset_index(drop=True)

# Flagging possible lights that influenced crime:
def flag(z):
    bar = progressbar.ProgressBar(maxval=len(z), widgets=[progressbar.ETA(), ' ', progressbar.Percentage()])
    bar.start()
    for i in range(len(z)):
        print(bar.update(i+1))
        try:
            if abs(z.loc[i, 'WoCompleted'] - z.loc[i, 'REPORT_DAT']).days <= 10:
                z.loc[i, 'Crime_LO_intime'] = 1
        except:
            z.loc[i, 'WoCompleted'] = dt.datetime.strptime(z.loc[i, 'WoCompleted'], '%Y-%m-%dT%H:%M:%S.%fZ') # Some values coded incorrectly.
            if abs(z.loc[i, 'WoCompleted'] - z.loc[i, 'REPORT_DAT']).days <= 10:
                z.loc[i, 'Crime_LO_intime'] = 1
    bar.finish()
    return z

Matched_NLights = flag(Matched_NLights)

# Lights matched with a crime nearby outside of likely bulb outage
Matched_NLights0 = Matched_NLights[Matched_NLights['Crime_LO_intime'] == 0].drop_duplicates(subset = 'WoID', keep = 'first')
Matched_NLights0 = Matched_NLights0.drop(['index_right', 'geometry'], axis = 1)

# Lights matched with a crime nearby within timeframe of light outage
Matched_NLights1 = Matched_NLights[Matched_NLights['Crime_LO_intime'] == 1].drop_duplicates(subset = 'OBJECTID', keep = 'first')
Matched_NLights1 = Matched_NLights1.drop(['index_right', 'geometry'], axis = 1)

Matched_NLights0.to_excel(choice + '/geoLights0Ntest.xlsx')
Matched_NLights1.to_excel(choice + '/geolights1Ntest.xlsx')

Matched_Lights0 = pd.read_excel(choice + '/geoLights0test.xlsx')
Matched_Lights1 = pd.read_excel(choice + '/geolights1test.xlsx')
