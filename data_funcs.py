# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 17:42:40 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd

def create_historical_data(df, col_name_list, time_periods):
    
    new_df = pd.DataFrame()
    
    for col_name in col_name_list:
        for period in range(time_periods):
            period += 1
            new_df[col_name+'-'+str(period)] = df[col_name].shift(period)
        
    return(new_df)

def create_future_data(df, target_name, num_of_targets, future_periods):
    
    new_df = pd.DataFrame()
    
    for i in range(num_of_targets):
        i += future_periods
        new_df[target_name+'+'+str(i)] = df[target_name].shift(-i)
        
    return(new_df)