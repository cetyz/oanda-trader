# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 17:42:40 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd

def get_value(series, key):
    return(series[key])

def transform_candle_data(df):
    
    df['time'] = pd.to_datetime(df['time'])
    
    df['o'] = df.apply(lambda x: get_value(x['mid'], 'o'), axis=1)
    df['h'] = df.apply(lambda x: get_value(x['mid'], 'h'), axis=1)
    df['l'] = df.apply(lambda x: get_value(x['mid'], 'l'), axis=1)
    df['c'] = df.apply(lambda x: get_value(x['mid'], 'c'), axis=1)
    
    df = df[['complete', 'volume', 'time', 'o', 'h', 'l', 'c']].set_index('time')
    
    df['o'] = pd.to_numeric(df['o'])
    df['h'] = pd.to_numeric(df['h'])
    df['l'] = pd.to_numeric(df['l'])
    df['c'] = pd.to_numeric(df['c'])
    
    return(df)

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