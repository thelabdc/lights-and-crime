# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 11:03:15 2018

@author: Garrett
"""
#%% Packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

Windows = 'C:/Users/Sade/Documents/GitHub/lights-and-crime/Lights and Crime Garrett/Data'
Linux = '/home/sade/Desktop/Git Cloned Repos/lights-and-crime/Lights and Crime Garrett/Data'

choice = Windows

#%% Data
L_full = pd.read_excel(choice + '/Final_Lights.xlsx')

