# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 11:43:42 2018

@author: Garrett
"""
#%% Packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import datetime as dt
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import progressbar #used progressbar2
import statsmodels.api as sm


Windows = 'C:/Users/Sade/Documents/GitHub/lights-and-crime/Lights and Crime Garrett/Data'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Windows


#%% Night and Day Crimes

CR = pd.read_excel(choice + '/crimes.xlsx')
CR[['gpsX', 'gpsY']] = CR[['X', 'Y']]
CR = CR.drop(['X', 'Y'], axis = 1)

# Relative category numbers
CR[['SHIFT', 'METHOD', 'OFFENSE']].describe()
for i in ['SHIFT', 'METHOD', 'OFFENSE']:
    print(i + ':',Counter(CR[i]))
    
CR['REPORT_DAT'] = [dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') for date in CR['REPORT_DAT']]

# Shortest day/night times in DC, e.g. look at https://www.timeanddate.com/sun/usa/washington-dc.

# Night and day crimes split by Nautical(night) and Civil(day) twilight .
NCR = CR[(CR.REPORT_DAT.dt.hour <= 5) | (CR['REPORT_DAT'].dt.hour > 21)]
DCR = CR[(CR.REPORT_DAT.dt.hour <= 17) & (CR['REPORT_DAT'].dt.hour > 7)]

# Night crimes over day crimes
plt.figure(3)
plt.scatter(DCR[DCR['OFFENSE'] == 'THEFT/OTHER']['gpsX'], DCR[DCR['OFFENSE'] == 'THEFT/OTHER']['gpsY'])
plt.scatter(NCR[NCR['OFFENSE'] == 'THEFT/OTHER']['gpsX'], NCR[NCR['OFFENSE'] == 'THEFT/OTHER']['gpsY'])

#%% To Excel

#NCR.to_excel(choice + '/NCR.xlsx')
#DCR.to_excel(choice + '/DCR.xlsx')

#%% Geopandas

isf = pd.read_excel(choice + '/Lights.xlsx')
inv = pd.read_excel(choice + '/islims_inventory.xlsx')
wo = pd.read_excel(choice + '/islims_workorders.xlsx')
wo = wo.rename(columns={'woID':'WoID'})
isf_wo = pd.merge(isf, wo, how='left', on = 'WoID')
isf_wo = isf_wo.drop(['srchAssetID', 'gpscoordinateX', 'gpscoordinateY', 'initialproblemID', \
       'resolveddatetime', 'entereddate', 'finalresolutionID'], axis = 1)
isf_wo_inv = pd.merge(isf_wo, inv, how='left', on = 'inventoryID')
isf_wo_inv = isf_wo_inv.drop(['gpscoordinateX', 'gpscoordinateY'], axis = 1)

# Setting up data into geopandas
geometry = [Point(xy) for xy in zip(isf_wo_inv['gpsX'], isf_wo_inv['gpsY'])]
gLights = GeoDataFrame(isf_wo_inv, geometry=geometry)
gLights = gLights.drop_duplicates(subset = ['WoID'])
geometry = [Point(xy) for xy in zip(NCR['gpsX'], NCR['gpsY'])]
gNCR = GeoDataFrame(NCR, geometry=geometry)
geometry = [Point(xy) for xy in zip(DCR['gpsX'], DCR['gpsY'])]
gDCR = GeoDataFrame(DCR, geometry=geometry)

BUFFER = .000625 # 1/4th of a city block in radius of Maryland coordinates.
#BUFFER = .00125 # 1/2 of a city block in radius of Maryland coordinates.

gLights_Buff = gLights.assign(geometry = lambda x: x.geometry.buffer(BUFFER)) 
# Overwrites geometry variable with a buffer centered at the point of interest. A.k.a. applies the function geometry(x) to gNCR and saves it as geometry.

Matched_NLights = gpd.sjoin(gLights_Buff, gNCR, 'left')
Matched_DLights = gpd.sjoin(gLights_Buff, gDCR, 'left')

# Left geojoin by buffer

#%% Filtering (Note: this takes up the most cpu time/ skip if you already have the data)

Matched_NLights['Crime_LO_intime'] = [0]*len(Matched_NLights) # Counter to be used
Matched_DLights['Crime_LO_intime'] = [0]*len(Matched_DLights) # Counter to be used

Matched_NLights = Matched_NLights.dropna(subset = ['WoCompleted'])
Matched_NLights = Matched_NLights.dropna(subset = ['REPORT_DAT'])
Matched_NLights = Matched_NLights.reset_index(drop=True)
Matched_DLights = Matched_DLights.dropna(subset = ['WoCompleted'])
Matched_DLights = Matched_DLights.dropna(subset = ['REPORT_DAT'])
Matched_DLights = Matched_DLights.reset_index(drop=True)


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
Matched_DLights = flag(Matched_DLights)

sum(Matched_NLights['Crime_LO_intime'])/len(Matched_NLights) # Rough Hit Ratio
sum(Matched_DLights['Crime_LO_intime'])/len(Matched_DLights) # Rough Hit Ratio

# Lights matched with a crime nearby outside of likely bulb outage
Matched_NLights0 = Matched_NLights[Matched_NLights['Crime_LO_intime'] == 0].drop_duplicates(subset = 'WoID', keep = 'first')
Matched_NLights0 = Matched_NLights0.drop(['index_right', 'geometry'], axis = 1)
Matched_DLights0 = Matched_DLights[Matched_DLights['Crime_LO_intime'] == 0].drop_duplicates(subset = 'WoID', keep = 'first')
Matched_DLights0 = Matched_DLights0.drop(['index_right', 'geometry'], axis = 1)

# Lights matched with a crime nearby within timeframe of light outage
Matched_NLights1 = Matched_NLights[Matched_NLights['Crime_LO_intime'] == 1].drop_duplicates(subset = 'OBJECTID', keep = 'first')
Matched_NLights1 = Matched_NLights1.drop_duplicates(subset = 'WoID', keep = 'first')
Matched_NLights1 = Matched_NLights1.drop(['index_right', 'geometry'], axis = 1)
Matched_DLights1 = Matched_DLights[Matched_DLights['Crime_LO_intime'] == 1].drop_duplicates(subset = 'OBJECTID', keep = 'first')
Matched_DLights1 = Matched_DLights1.drop_duplicates(subset = 'WoID', keep = 'first')
Matched_DLights1 = Matched_DLights1.drop(['index_right', 'geometry'], axis = 1)

Matched_NLights_F = pd.concat([Matched_NLights0, Matched_NLights1])
Matched_DLights_F = pd.concat([Matched_DLights0, Matched_DLights1])

#Note, by only considering light outs that have had a crime within 1/4th block radius, we are conditioning by areas that plausibly exhibit criminal activity and ignoring observations where crime does not take place.
#Further we only consider one crime being mapped to one light within the window

#%% To excel

#Matched_NLights_F.to_excel(choice + '/Matched_NLights_F.xlsx')
#Matched_DLights_F.to_excel(choice + '/Matched_DLights_F.xlsx')
Matched_Lights0.to_excel(choice + '/geoNLights0.xlsx')
Matched_Lights1.to_excel(choice + '/geoNlights1.xlsx')


#%% Merging with unmatched lights

Matched_NLights_F = pd.read_excel(choice + '/Matched_NLights_F.xlsx')
Matched_DLights_F = pd.read_excel(choice + '/Matched_DLights_F.xlsx')

# Bias reduced by removing duplicate lightout observations
Matched_NLights_F = Matched_NLights_F.drop_duplicates(subset = 'WoID', keep = 'last')
Matched_DLights_F = Matched_DLights_F.drop_duplicates(subset = 'WoID', keep = 'last')

Matched_NLights_F = Matched_NLights_F.reset_index(drop = True)
Matched_NLights_F = Matched_NLights_F.rename(columns={'gpsX_right':'gpsX_CR', 'gpsY_right':'gpsY_CR', 'gpsX_left':'gpsX', 'gpsY_left':'gpsY'})
Matched_NLights_F['Crime_LO_intime'][np.isnan] = 0
Matched_DLights_F = Matched_DLights_F.reset_index(drop = True)
Matched_DLights_F = Matched_DLights_F.rename(columns={'gpsX_right':'gpsX_CR', 'gpsY_right':'gpsY_CR', 'gpsX_left':'gpsX', 'gpsY_left':'gpsY'})
Matched_DLights_F['Crime_LO_intime'][np.isnan] = 0
# Note overlap between groups in "Crime_LO_intime" will cause variance to be overstated slightly

#%% Difference in Difference

# Splitting the crimes into before and after 10 day categories (note* 1 day buffer to avoid category errors)
def BeforeAndAfter(ML,a):
    bar = progressbar.ProgressBar(maxval=len(ML), widgets=[progressbar.ETA(), ' ', progressbar.Percentage()])
    bar.start()
    ML['CR_Before_Fix'] = 0
    ML['CR_After_Fix'] = 0
    for i in ML[ML['Crime_LO_intime'] == 1].index:
        print(bar.update(i+1))
        if (ML.loc[i, 'WoCompleted'] - ML.loc[i, 'REPORT_DAT']).days >= 0 and (ML.loc[i, 'WoCompleted'] - ML.loc[i, 'REPORT_DAT']).days <= a:
            ML.loc[i, 'CR_Before_Fix'] = 1
        if (ML.loc[i, 'WoCompleted'] - ML.loc[i, 'REPORT_DAT']).days < 0 and (ML.loc[i, 'WoCompleted'] - ML.loc[i, 'REPORT_DAT']).days >= -a:
            ML.loc[i, 'CR_After_Fix'] = 1
    bar.finish()

BeforeAndAfter(Matched_NLights_F, 10)
BeforeAndAfter(Matched_DLights_F, 10)

# Raw Sums:
# Night
sum(Matched_NLights_F['CR_Before_Fix'])
sum(Matched_NLights_F['CR_After_Fix'])

# Day
sum(Matched_DLights_F['CR_Before_Fix'])
sum(Matched_DLights_F['CR_After_Fix'])

# Because we will only consider the binary crime(s) took place or not, we can consider the following means as differences in probabilities.
# Estimates are based on 10 "days out".
# Unconditional difference in means: E[u]-E[t]
def mean(ML):
    mean = sum(ML['CR_Before_Fix'])/len(ML) - sum(ML['CR_After_Fix'])/len(ML)
    return mean

# Interpretation of sum(ML['CR_Before_Fix'])/len(CR): Considering all night crimes, there is approximately a 1.5% chance 
# that a randomly chosen crime will occur within 1/4th of a city block of an out street lamp BEFORE it is repaired.
# Interpretation of sum(ML['CR_After_Fix'])/len(CR): Considering all night crimes, there is approximately a 1.4% chance
# that a randomly chosen crime will occur within 1/4th of a city block of an out street lamp AFTER it is repaired.
mdif1 = mean(Matched_NLights_F)

# For day crimes the numbers are 3.4% before and 3.1% after.
mdif2 = mean(Matched_DLights_F)

# For a Binary Random Variable:
# Var(x) = E[x^2] - E[x]^2
#        = E[x]   - E[x]^2 remember x = 1 or 0
#        = P(x = 1) - P(x = 1)^2
#        = P(x = 1)(1 - P(x = 1))
def Sd(ML):
    VarB = sum(ML['CR_Before_Fix'])/len(ML)*(1 - sum(ML['CR_Before_Fix'])/len(ML))
    VarA = sum(ML['CR_After_Fix'])/len(ML)*(1 - sum(ML['CR_After_Fix'])/len(ML))
    Sd = np.sqrt((VarB/len(ML))+(VarA/len(ML)))
    return Sd

Sd1 = Sd(Matched_NLights_F)
Sd2 = Sd(Matched_DLights_F)

t1 = mdif1/Sd1
t2 = mdif2/Sd2

# Let's take a look at estimates for different "days out".
'''
def DaysOut(ML, a):
    for a in range(1,a+1):
        BeforeAndAfter(ML, a)
        print(sum(ML['CR_Before_Fix'])/len(ML) - sum(ML['CR_After_Fix'])/len(ML))

DaysOut(Matched_NLights_F, 10)
DaysOut(Matched_DLights_F, 10)
'''

# DiD, Note* regression framework not appropriate here due to format and information in data:
DiD = mdif1 - mdif2
DiD
mdif1

Matched_NLights_F['treat'] = 1
Matched_DLights_F['treat'] = 0
Matched = pd.concat([Matched_NLights_F, Matched_DLights_F])
Matched = Matched.reset_index(drop=True)

# Checking plausibility of number of arms being as significant factor
Matched['SLnumberarms'] = Matched['SLnumberarms'].replace({"0":0, "1":1, "2":2 })
Matched['SLnumberarms'] = Matched['SLnumberarms'].replace({'?':1})
Matched['SLnumberarms'] = Matched['SLnumberarms'].fillna(1)
Arms = pd.get_dummies(Matched['SLnumberarms'])
Matched['arms'] = Arms[0]+Arms[1]
mdif1A = mean(Matched[Matched['treat'] == 1][Matched['arms'] == 1])
mdif2A = mean(Matched[Matched['treat'] == 0][Matched['arms'] == 1])
DiDA = mdif1A - mdif2A
DiDA
mdif1A
# mean differences and DiD are the same

# Checking differences across Wards
Wards = pd.get_dummies(Matched['WARD'])
Wards.rename(columns = {1:'W_One', 2:'W_Two', 3:'W_Three', 4:'W_Four', 5:'W_Five', 6:'W_Six', 7:'W_Seven', 8:'W_Eight' }, inplace = True)
Matched = pd.concat([Matched, Wards], axis = 1)
Matched = Matched.reset_index(drop=True)
Matched.rename(columns = {1:'W_One', 2:'W_Two', 3:'W_Three', 4:'W_Four', 5:'W_Five', 6:'W_Six', 7:'W_Seven', 8:'W_Eight' }, inplace = True)
for i in list(Wards.columns):
    try:
        mdif = mean(Matched[Matched['treat'] == 1][Matched[i] == 1])
        mdif
        VarB = sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_Before_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1])*(1 - sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_Before_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1]))
        VarA = sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_After_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1])*(1 - sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_After_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1]))
        Sd = np.sqrt((VarB/len(Matched[Matched['treat'] == 1][Matched[i] == 1]))+(VarA/len(Matched[Matched['treat'] == 1][Matched[i] == 1])))
        t = mdif/Sd
        print(i + ' : ' + str(round(mdif, 5)) + ', t:' + str(t))
    except:
        print('problem')
        pass

# Checking plausibility of types of crimes
# Theft/Other
Crimes = pd.get_dummies(Matched['OFFENSE'])
Matched = pd.concat([Matched, Crimes], axis = 1)
Matched = Matched.reset_index(drop=True)

for i in list(Crimes.columns):
    try:
        mdif = mean(Matched[Matched['treat'] == 1][Matched[i] == 1])
        mdif
        VarB = sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_Before_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1])*(1 - sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_Before_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1]))
        VarA = sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_After_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1])*(1 - sum(Matched[Matched['treat'] == 1][Matched[i] == 1]['CR_After_Fix'])/len(Matched[Matched['treat'] == 1][Matched[i] == 1]))
        Sd = np.sqrt((VarB/len(Matched[Matched['treat'] == 1][Matched[i] == 1]))+(VarA/len(Matched[Matched['treat'] == 1][Matched[i] == 1])))
        t = mdif/Sd
        print(i + ' : ' + str(round(mdif, 5)) + ', t:' + str(t))
    except:
        print('problem')
        pass
# Only THEFT F/AUTO is remotely significant


#%% (DiD estimates will likely bias the effect because the "time" dummy does not encompass all observations; only considers 10 day window):
Matched_NLights_F['treat'] = 1
Matched_DLights_F['treat'] = 0
Matched = pd.concat([Matched_NLights_F, Matched_DLights_F])
Matched['T'] = Matched['CR_Before_Fix'] * Matched['treat']
Matched = Matched.reset_index(drop=True)
Warddum = pd.get_dummies(Matched['WARD'])
Offence = pd.get_dummies(Matched['OFFENSE'])
Matched['SLnumberarms'] = Matched['SLnumberarms'].replace({"0":0, "1":1, "2":2 })
Matched['SLnumberarms'] = Matched['SLnumberarms'].replace({'?':1})
Matched['SLnumberarms'] = Matched['SLnumberarms'].fillna(1)
Arms = pd.get_dummies(Matched['SLnumberarms'])


x = pd.concat([Offence['THEFT/OTHER'], Warddum.loc[:,1:7], Arms.loc[:,2]], axis = 1)
x = sm.add_constant(x)
y = Matched['Crime_LO_intime']

model = sm.OLS(y, x).fit()
model.summary()


