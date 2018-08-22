# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 10:53:03 2018

@author: Garrett
"""

#%% Merging and Cleaning iSLims data

# Packages
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import datetime as dt

#%% Data
Windows = 'C:/Users/Sade/Documents/GitHub/lights-and-crime/Lights and Crime Garrett/Data'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Windows

wo = pd.read_excel(choice + '/islims_workorders.xlsx')
de = pd.read_excel(choice + '/islims_workorders_detail.xlsx')
iv = pd.read_excel(choice + '/islims_inventory.xlsx')
fc = pd.read_excel(choice + '/islims_failure_codes.xlsx')

#%% Merging and Cleaning Data

# Merging work order and details sets on woID
wode = pd.merge(wo, de, on='woID')

# Merging wode and inventory sets on inventoryID
iSlimsa = pd.merge(wode, iv, on='inventoryID')

# Merging the GPS coordinates to fill in as many NaN gaps as possible
gpsX = iSlimsa['gpscoordinateX_x'].combine_first(iSlimsa['gpscoordinateX_y'])
gpsX = gpsX.combine_first(iSlimsa['gpscoordinateX_x'])
gpsY = iSlimsa['gpscoordinateY_x'].combine_first(iSlimsa['gpscoordinateY_y'])
gpsY = gpsY.combine_first(iSlimsa['gpscoordinateY_x'])

# Removing irrelevant variables
iSlimsb = iSlimsa.iloc[:,0:18]
iSlimsb['gpsX'] = gpsX
iSlimsb['gpsY'] = gpsY

# final merged dataset
iSlimsc = iSlimsb.drop(['gpscoordinateX_x', 'gpscoordinateY_x'], axis = 1)

# Throwing out observations without GPS coordinate
iSlimsd = iSlimsc.dropna(subset = ['gpsX', 'gpsY'])

# Will use codes: 2, 196, 201, 209
fc[fc['description'].str.contains('ight')].head()

# Filtering by observations with the desired failure codes
iSlimse = iSlimsd[iSlimsd['finalresolutionID'].isin([2, 196, 201, 209])]

# Filtering by times of interest
resolv_t = (iSlimse['resolveddatetime'] > '2007-12-31') & (iSlimse['resolveddatetime'] < '2017-01-01') 
enter_t = (iSlimse['entereddate_x'] > '2007-12-31') & (iSlimse['entereddate_x'] < '2017-01-01')
iSlimsf = iSlimse[resolv_t & enter_t]

# Filtering out observations with excessively long completion / late completion times
iSlimsg = iSlimsf[(iSlimsf['daysToComplete'] <= 23)]
iSlimsg['finalresolutionID'].value_counts()

# Dropping duplicate woID's
iSlimsh = iSlimsg.drop_duplicates(subset = ['woID'])

# Throwing out observations with a GPS coordinate that is too large in magnitude to be possible
iSlimsh[['gpsX', 'gpsY']] = iSlimsh[['gpsX', 'gpsY']].apply(pd.to_numeric)
iSlims = iSlimsh[iSlimsh['gpsX'] <= 20000 ]
iSlims = iSlims[iSlims['gpsY']<= 20000]

# Removing 2 observations whos GPS coordinates were entered incorrectly and limiting bounds of GPS coordinates to realistic numbers in the bounds of DC
iSlims = iSlims.drop([465076, 144970])
iSlims = iSlims[(iSlims['gpsX'] >= 38.7) & (iSlims['gpsX'] <= 39) ]
iSlims = iSlims[(iSlims['gpsY'] >= -77.15) & (iSlims['gpsY'] <= -76.90)]
# Cutting out close outliers
iSlims = iSlims[~((iSlims['gpsX'] >= 38.828) & (iSlims['gpsX'] <= 38.8395) & (iSlims['gpsY'] <= -76.9632) & (iSlims['gpsY'] >= -76.9777))]
iSlims = iSlims[~((iSlims['gpsX'] >= 38.955) & (iSlims['gpsX'] <= 38.96) & (iSlims['gpsY'] >= -76.98) & (iSlims['gpsY'] <= -76.97))]
iSlims = iSlims.reset_index()
del iSlims['index']

# For some reason the coordinate system is backwards
iSlims[['gpsX', 'gpsY']] = iSlims[['gpsY', 'gpsX']]

#%% To Excel

iSlims.to_excel(choice + '/iSlims_final.xlsx')

#%% EDA

# Summary Statistics and histogram on completion days
iSlims[['daysToComplete', 'daysLate']].describe()
# on average it takes 2 days to complete a task and the completion tasks are rarely late (excluding completion tasks beyond 14 days).
plt.figure(1)
plt.hist(iSlims['daysToComplete'], bins = 23)
# Something to note: A Poisson distribution for count data.  Could do a GLM to predict what contributes to repair time.
# Also Interesting jump at 14ish days and predictible drop after 5ish days.

# Scatter of GPS coordinates
plt.figure(2)
plt.scatter(iSlims['gpsX'], iSlims['gpsY'])
# No obvious problem areas jump out.
# Could also filter by Completion time and Late time, no obvious problem areas there either

#%% Merged Ready and Standardized iSlims Data

#Standardized iSlims
SDiSlims = iSlims[['woID', 'entereddate_x', 'resolveddatetime', 'gpsX', 'gpsY']]
SDiSlims.columns = ['WoID', 'WoEntered', 'WoCompleted', 'gpsX', 'gpsY']

#%% To Excel

SDiSlims.to_excel(choice + '/SDiSlims_final.xlsx')

#%% Merging iSlims and Citywork

CW = pd.read_excel(choice + '/city_works_merger_data.xlsx')
CW = CW[(CW['gpsY'] >= 38.7)]
plt.scatter(CW['gpsX'], CW['gpsY'])


Lights = pd.concat([SDiSlims, CW], ignore_index = True)

#%% To Excel

Lights.to_excel(choice + '/Lights.xlsx')

#%% Crimes and EDA

CR = pd.read_excel(choice + '/crimes.xlsx')
CR[['gpsX', 'gpsY']] = CR[['X', 'Y']]
CR = CR.drop(['X', 'Y'], axis = 1)

# Relative category numbers
CR[['SHIFT', 'METHOD', 'OFFENSE']].describe()
for i in ['SHIFT', 'METHOD', 'OFFENSE']:
    print(i + ':',Counter(CR[i]))
    
CR['REPORT_DAT'] = [dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') for date in CR['REPORT_DAT']]

NCR = CR[(CR.REPORT_DAT.dt.hour <= 6) | (CR['REPORT_DAT'].dt.hour > 18)]
# Night crimes

# Midnight offenses have least number of occurances.

# Looked at offenses by type
plt.figure(3)
plt.scatter(CR[CR['OFFENSE'] == 'BURGLARY']['gpsX'], CR[CR['OFFENSE'] == 'BURGLARY']['gpsY'])

#%% To Excel

NCR.to_excel(choice + '/NCRold.xlsx')


#%% Play

'''
decimal_range = list(range(3,9))

merge = pd.DataFrame()

for i in decimal_range:
    CR[['gridX', 'gridY']] = CR[['gpsX', 'gpsY']].round(i)
    Lights[['gridX', 'gridY']] = Lights[['gpsX', 'gpsY']].round(i)
    merge = merge.append( CR.merge(Lights, on=['gridX','gridY'], how='inner'), )

merge = pd.DataFrame()
CR[['gridX', 'gridY']] = CR[['gpsX', 'gpsY']].round(4)
Lights[['gridX', 'gridY']] = Lights[['gpsX', 'gpsY']].round(4)
merge = merge.append( CR.merge(Lights, on=['gridX','gridY'], how=''), )
merge = merge.dropna(subset = ['CCN'])

plt.scatter(merge['gridX'], merge['gridY'])


######################

merge = pd.DataFrame()
roundd = 4

CR['new_col'] = list(zip(CR.gpsX.round(roundd), CR.gpsY.round(roundd)))
Lights['new_col'] = list(zip(Lights.gpsX.round(roundd), Lights.gpsY.round(roundd)))
merge = merge.append( CR.merge(Lights, on=['new_col'], how='inner'), )

merge['REPORT_DAT'] = [dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ') for date in merge['REPORT_DAT']]
merge['Tdelta'] = [0]*len(merge)
merge['night'] = [0]*len(merge)
merge = merge.dropna(subset = ['WoCompleted'])
merge = merge[merge['SHIFT'] != 'DAY']
merge = merge.reset_index()

for t in range(len(merge)):
    if merge.loc[t, 'REPORT_DAT'].hour > 18 or merge.loc[t, 'REPORT_DAT'].hour < 8:
        merge.loc[t, 'night'] = 1
        
merge = merge[merge['night'] == 1]
merge = merge.reset_index()

for i in range(len(merge)):
    try:
        if (merge.loc[i, 'WoCompleted'] - merge.loc[i, 'REPORT_DAT']).days <= 10 and (merge.loc[i, 'WoCompleted'] - merge.loc[i, 'REPORT_DAT']).days > 0:
            merge.loc[i, 'Tdelta'] = 1
    except:
        merge.loc[i, 'WoCompleted'] = dt.datetime.strptime(merge.loc[i, 'WoCompleted'], '%Y-%m-%dT%H:%M:%S.%fZ') #some values coded incorrectly
        if (merge.loc[i, 'WoCompleted'] - merge.loc[i, 'REPORT_DAT']).days <= 10 and (merge.loc[i, 'WoCompleted'] - merge.loc[i, 'REPORT_DAT']).days > 0:
            merge.loc[i, 'Tdelta'] = 1

sum(merge['Tdelta'])
sum(merge['Tdelta'])/len(merge)
len(merge)/len(Lights)

'''

















