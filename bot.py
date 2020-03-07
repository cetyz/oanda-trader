# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 00:24:04 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd
import json

from api_wrapper import Oanda

# get log in info from json
with open('config.json', 'r') as f:
    configs = json.load(f)
    token = configs['token']
    account = configs['account']
    user = configs['user']
    
    
# initialize oanda api wrapper and get candles    
oanda = Oanda(token=token, account=account, user=user)
candles = oanda.get_candle(count=760)['candles']

# load candles into pandas dataframe
df = pd.DataFrame(candles)
df['time'] = pd.to_datetime(df['time'])

def get_value(series, key):
    return(series[key])

df['o'] = df.apply(lambda x: get_value(x['mid'], 'o'), axis=1)
df['h'] = df.apply(lambda x: get_value(x['mid'], 'h'), axis=1)
df['l'] = df.apply(lambda x: get_value(x['mid'], 'l'), axis=1)
df['c'] = df.apply(lambda x: get_value(x['mid'], 'c'), axis=1)

df = df[['complete', 'volume', 'time', 'o', 'h', 'l', 'c']].set_index('time')

df['o'] = pd.to_numeric(df['o'])
df['h'] = pd.to_numeric(df['h'])
df['l'] = pd.to_numeric(df['l'])
df['c'] = pd.to_numeric(df['c'])

# get RSI
# which is 100 - (100 / (1 + RS))
# where RS = Average Gain / Average Loss

# create new df for this using only close data


#print(rsi_df)

#print(df)