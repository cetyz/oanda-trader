# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 00:24:04 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd
import json

from api_wrapper import Oanda
from TA_funcs import RSI, MACD, MACD_signal

# get log in info from json
with open('config.json', 'r') as f:
    configs = json.load(f)
    token = configs['token']
    account = configs['account']
    user = configs['user']
    
    
# initialize oanda api wrapper and get candles    
oanda = Oanda(token=token, account=account, user=user)
candles = oanda.get_candle(count=5000, granularity='M5')['candles']

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

#df.to_csv('test_data.csv')

df['o'] = pd.to_numeric(df['o'])
df['h'] = pd.to_numeric(df['h'])
df['l'] = pd.to_numeric(df['l'])
df['c'] = pd.to_numeric(df['c'])

df['RSI'] = RSI(df['c'])
df['MACD'] = MACD(df['c'])
df['MACD Signal'] = MACD_signal(df['c'])

print(df.head())