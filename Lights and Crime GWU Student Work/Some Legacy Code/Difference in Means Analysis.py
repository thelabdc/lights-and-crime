# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 13:21:43 2018

@author: Garrett
"""

#%% Packages

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#%% Final Data Cleaning
Windows = 'C:/Users/Sade/Documents/GitHub/lights-and-crime/Lights and Crime Garrett/Data'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Linux

# Setting up geo joined data 
# geoLights0 is a df of light outages and crimes that did not happen in a 10 day window
# geoLights1 is a df of light outages and crimes that happened in a 10 day window
Lights = pd.read_excel(choice + '/Lights.xlsx')
Lights = Lights[~Lights.duplicated(['WoID'], keep = False)] # Removing Incorrectly valued work orders (1606 observations).  Take note of this because this is still useful information!
L_noCR = pd.read_excel(choice + '/geoLights0.xlsx')
L_noCR = L_noCR.reset_index()
L_noCR = L_noCR.drop(['index', 'level_0', 'index_right'], 1)
L_yesCR_dup = pd.read_excel(choice + '/geoLights1.xlsx')
L_yesCR_dup = L_yesCR_dup.reset_index()
L_yesCR_dup = L_yesCR_dup.drop(['index', 'index_right'], 1)
# Be advised there is some small cross over between L_noCR and L_yesCR_dup

# Pulling out all the duplicate crimes into a side dataframe
L_yesCR_dup_only = L_yesCR_dup[L_yesCR_dup.duplicated(['WoID'], keep = False)]
L_yesCR_dup_only = L_yesCR_dup_only.reset_index()
L_yesCR_dup_only = L_yesCR_dup_only.drop(['index', 'level_0'], 1)

# Making a data set that treats multiple crimes at the same time/ place as one
L_yesCR_nodup = L_yesCR_dup[~L_yesCR_dup.duplicated(['WoID'], keep = 'first')]
L_yesCR_nodup = L_yesCR_nodup.reset_index()
L_yesCR_nodup = L_yesCR_nodup.drop(['index', 'level_0'], 1)
#L_temp = L_yesCR_dup[~L_yesCR_dup.duplicated(['WoID'], keep = False)]
#L_yesCR_nodup = pd.concat([L_yesCR_dup_1st, L_temp])

#%% Merging and setting up final dataset

# Pulling out unmatched observations
L_0_1 = pd.concat([L_noCR, L_yesCR_nodup]) # With overlap
L_temp = L_0_1[L_0_1.duplicated(['WoID'], keep = False)]
L_0_1 = L_0_1[~L_0_1.duplicated(['WoID'], keep = False)]
L_temp = L_temp[L_temp['Tdelta'] == 1]
L_0_1 = pd.concat([L_0_1, L_temp]) # Without overlap

# Final dataset
L_full = pd.merge(Lights, L_0_1, how = 'left', on = 'WoID')
L_full = L_full.drop(['WoEntered_y', 'WoCompleted_y', 'gpsX_left', 'gpsY_left'], axis = 1)
L_full = L_full.rename(columns={'gpsX':'gpsX_CR', 'gpsY':'gpsY_CR', 'WoEntered_x':'WoEntered', 'WoCompleted_x':'WoCompleted', 'gpsX_right':'gpsX', 'gpsY_right':'gpsY', 'Tdelta':'Lightout&CR' })
L_full['Lightout&CR'][np.isnan] = 0

#%% To excel

L_yesCR_dup_only.to_excel(choice + '/Rampage.xlsx')
L_full.to_excel(choice + '/Final_Lights.xlsx')

#%% Difference in Means Analysis

# Splitting the crimes into before and after 10 day categories (note* 1 day buffer to avoid category errors)
L_full['CR_Before_Fix'] = 0
for i in L_full[L_full['Lightout&CR'] == 1].index:
    if (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days >= 0 and (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days <= 10:
        L_full.loc[i, 'CR_Before_Fix'] = 1
L_full['CR_After_Fix'] = 0
for i in L_full[L_full['Lightout&CR'] == 1].index:
    if (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days < 0 and (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days >= -10:
        L_full.loc[i, 'CR_After_Fix'] = 1

# Raw Sums:
sum(L_full['CR_Before_Fix'])
sum(L_full['CR_After_Fix'])

# Because we will only consider the binary crime(s) took place or not, we can consider the following means as differences in probabilities.
# Estimates are based on 10 "days out".
# Unconditional difference in means: E[u]-E[t]
meandif = sum(L_full['CR_Before_Fix'])/len(L_full) - sum(L_full['CR_After_Fix'])/len(L_full)
# Difference in Probability: approximately 0.17 percentage points

# For a Binary Random Variable:
# Var(x) = E[x^2] - E[x]^2
#        = E[x]   - E[x]^2 remember x = 1 or 0
#        = P(x = 1) - P(x = 1)^2
#        = P(x = 1)(1 - P(x = 1))
VarB = sum(L_full['CR_Before_Fix'])/len(L_full)*(1 - sum(L_full['CR_Before_Fix'])/len(L_full))
VarA = sum(L_full['CR_After_Fix'])/len(L_full)*(1 - sum(L_full['CR_After_Fix'])/len(L_full))
Sdif = np.sqrt((VarB/len(L_full))+(VarA/len(L_full)))
t = meandif/Sdif # t is approximately 3.44
# P-value is approximately 0; estimate is statistically significant.
# This evidence supports the conculsion that light outages do affect crime generally by a very small margin unconditionally.
# Given the magnitude of our esitmate, it is likely that light outages do not effect crime.

# Conditional difference in means: E[u\'Lightout&CR' = 1] - E[t\'Lightout&CR' = 1]
meandif = sum(L_full['CR_Before_Fix'])/sum(L_full['Lightout&CR']) - sum(L_full['CR_After_Fix'])/sum(L_full['Lightout&CR'])
# Difference in Probability: approximately 3.5 percentage points

VarB = sum(L_full['CR_Before_Fix'])/sum(L_full['Lightout&CR'])*(1 - sum(L_full['CR_Before_Fix'])/sum(L_full['Lightout&CR']))
VarA = sum(L_full['CR_After_Fix'])/sum(L_full['Lightout&CR'])*(1 - sum(L_full['CR_After_Fix'])/sum(L_full['Lightout&CR']))
Sdif = np.sqrt((VarB/sum(L_full['Lightout&CR']))+(VarA/sum(L_full['Lightout&CR'])))
t = meandif/Sdif # t is approximately 4.69
# P-value is approximately 0; estimate is statistically significant.
# This evidence supports the conculsion that if a crime is to occur then it is 3.5 percentage points more likely to occur when the light is out.

# Let's take a look at different conditional estimates for different "days out".
for a in range(1,11):
    L_full['CR_Before_Fix'] = 0
    for i in L_full[L_full['Lightout&CR'] == 1].index:
        if (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days >= 0 and (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days <= a:
            L_full.loc[i, 'CR_Before_Fix'] = 1
    L_full['CR_After_Fix'] = 0
    for i in L_full[L_full['Lightout&CR'] == 1].index:
        if (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days < 0 and (L_full.loc[i, 'WoCompleted'] - L_full.loc[i, 'REPORT_DAT']).days >= -a:
            L_full.loc[i, 'CR_After_Fix'] = 1
    print(sum(L_full['CR_Before_Fix'])/sum(L_full['Lightout&CR']) - sum(L_full['CR_After_Fix'])/sum(L_full['Lightout&CR']))
#   Estimates generated by "days out"
#1  0.04733660317098209
#2  0.04494125698642637
#3  0.04094901334550016
#4  0.046880346754876234
#5  0.04608189802669099
#6  0.0477928595870879
#7  0.04471312877837347
#8  0.0392380517851032
#9  0.03912398768107678
#10 0.03535987224820347


#%% Interesting plots and other

# Interesting Clustering of multiple crimes
plt.figure(1)
plt.scatter(L_full['gpsX_CR'], L_full['gpsY_CR'])
plt.scatter(L_yesCR_dup_only['gpsX_left'], L_yesCR_dup_only['gpsY_left'])

plt.figure(2)
mask1 = (L_full['gpsX_CR'] >= -77.070) & (L_full['gpsX_CR'] <= -77.054) & (L_full['gpsY_CR'] >= 38.898) & (L_full['gpsY_CR'] <= 38.914)
mask2 = (L_yesCR_dup_only['gpsX_left'] >= -77.070) & (L_yesCR_dup_only['gpsX_left'] <= -77.054) & (L_yesCR_dup_only['gpsY_left'] >= 38.898) & (L_yesCR_dup_only['gpsY_left'] <= 38.914)

plt.scatter(L_full[mask1].gpsX_CR, L_full[mask1].gpsY_CR)
plt.scatter(L_yesCR_dup_only[mask2].gpsX_left, L_yesCR_dup_only[mask2].gpsY_left)

plt.figure(3)
mask1 = (L_full['gpsX_CR'] >= -77.046) & (L_full['gpsX_CR'] <= -77.015) & (L_full['gpsY_CR'] >= 38.88) & (L_full['gpsY_CR'] <= 38.94)
mask2 = (L_yesCR_dup_only['gpsX_left'] >= -77.046) & (L_yesCR_dup_only['gpsX_left'] <= -77.015) & (L_yesCR_dup_only['gpsY_left'] >= 38.88) & (L_yesCR_dup_only['gpsY_left'] <= 38.94)

plt.scatter(L_full[mask1].gpsX_CR, L_full[mask1].gpsY_CR)
plt.scatter(L_yesCR_dup_only[mask2].gpsX_left, L_yesCR_dup_only[mask2].gpsY_left)

plt.figure(4)
plt.scatter(L_full['gpsX_CR'], L_full['gpsY_CR'])
plt.scatter(L_yesCR_dup_only['gpsX_left'], L_yesCR_dup_only['gpsY_left'])

#%% Play

# Plotting circles
'''
x = []
y = []
for i in range(len(gLights_Buff['geometry'])):
    xc, yc = glights_Buff.loc[i, 'geometry'].exterior.coords.xy
    x.append(xc)
    y.append(yc)

plt.figure(1)
plt.scatter(x, y)

plt.figure(2)
plt.scatter(Lights['gpsX'], Lights['gpsY'])
'''

#%% Kill Street

L_yesCR_dup = L_yesCR_dup.drop(['level_0'], 1)
ks = pd.concat([L_noCR, L_yesCR_dup]) # With overlap
ks = ks.reset_index()
ks = ks.drop(['index'], 1)


L_yesCR_dup_only[mask2].columns
L_yesCR_dup_only[mask2]['OFFENSE'].value_counts()
L_yesCR_dup_only[mask2]['METHOD'].value_counts()
L_yesCR_dup_only[mask2]['SHIFT'].value_counts()

mask1 = (ks['gpsX_right'] >= -77.071) & (ks['gpsX_right'] <= -77.057) & (ks['gpsY_right'] >= 38.902) & (ks['gpsY_right'] <= 38.908)


ks['CR_Before_Fix'] = 0
for i in ks[ks['Tdelta'] == 1].index:
    if (ks.loc[i, 'WoCompleted'] - ks.loc[i, 'REPORT_DAT']).days >= 0 and (ks.loc[i, 'WoCompleted'] - ks.loc[i, 'REPORT_DAT']).days <= 10:
        ks.loc[i, 'CR_Before_Fix'] = 1
ks['CR_After_Fix'] = 0
for i in ks[ks['Tdelta'] == 1].index:
    if (ks.loc[i, 'WoCompleted'] - ks.loc[i, 'REPORT_DAT']).days < 0 and (ks.loc[i, 'WoCompleted'] - ks.loc[i, 'REPORT_DAT']).days >= -10:
        ks.loc[i, 'CR_After_Fix'] = 1

meandif = sum(ks[mask1]['CR_Before_Fix'])/len(ks[mask1]) - sum(ks[mask1]['CR_After_Fix'])/len(ks[mask1])
meandif
#1.1%

VarB = sum(ks[mask1]['CR_Before_Fix'])/len(ks[mask1])*(1 - sum(ks[mask1]['CR_Before_Fix'])/len(ks[mask1]))
VarA = sum(ks[mask1]['CR_After_Fix'])/len(ks[mask1])*(1 - sum(ks[mask1]['CR_After_Fix'])/len(ks[mask1]))
Sdif = np.sqrt((VarB/len(ks[mask1]))+(VarA/len(ks[mask1])))
t = meandif/Sdif
t # not significant


meandif = sum(ks[mask1]['CR_Before_Fix'])/sum(ks[mask1]['Tdelta']) - sum(ks[mask1]['CR_After_Fix'])/sum(ks[mask1]['Tdelta'])
meandif
#6.5%

plt.scatter(ks[mask1]['gpsX_right'], ks[mask1]['gpsY_right'])

test = ks[mask1]



# density plots

L_yesCR_dup

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kde
SL = pd.read_csv('/home/sade/Desktop/Street_Lights.csv')
NCR = pd.read_excel(choice + '/NCR.xlsx')
NCR['OFFENSE'].value_counts()
NCR2 = NCR[NCR['OFFENSE'] == 'THEFT/OTHER']
# Evaluate a gaussian kde on a regular grid of nbins x nbins over data extents
nbins=500
k = kde.gaussian_kde([SL.X,SL.Y])
xi, yi = np.mgrid[SL['X'].min():SL['X'].max():nbins*1j, SL['Y'].min():SL['Y'].max():nbins*1j]
zi = k(np.vstack([xi.flatten(), yi.flatten()]))
 
# Make the plot
plt.figure(1)
plt.pcolormesh(xi, yi, zi.reshape(xi.shape))
plt.scatter(NCR2['gpsX'], NCR2['gpsY'], s=0.3, c='red')
plt.show()
 
# Change color palette
plt.pcolormesh(xi, yi, zi.reshape(xi.shape), cmap=plt.cm.Greens_r)
plt.show()

plt.pcolormesh(xi, yi, zi.reshape(xi.shape), cmap=plt.cm.Greens_r)
plt.colorbar()
plt.show()




















