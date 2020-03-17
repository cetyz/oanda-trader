# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 00:24:04 2020

@author: Cetyz
"""

"""
This "bot" is supposed to perform the high level actions (i.e. listed below).
Let everything else be handled by other .
Do I need to convert this into a class?


SETUP PHASE:
(Just once when script is launched)
1. Import necessary libraries
2. Load in Oanda account data from json
3. Initialize Oanda wrapper
4. Initialize constants

PREPARATION PHASE:
(When trading closes for the weekend)

1. Get latest 5000 (max request) candles
2. Get new model for the upcoming week based on this data
3. Check if trading is open?

TRADING PHASE:
(When trading is open)

1. Check if trading is open (if open, proceed, else proceed to Prep phase)
2. Refresh candles every interval (only what is necessary to get X last values)
3a. Using the new data, get TA indicators
3b. Get model prediction based on model from Prep Phase
4. Do checks to decide on action (e.g. if RSI < .25 and whatever, do X)

"""
##############################################################################
# SETUP PHASE ################################################################
# 1. Import necessary libraries
import numpy as np
import pandas as pd
import json

from api_wrapper import Oanda
from TA_funcs import RSI, MACD, MACD_signal
from data_funcs import transform_candle_data
from ML_funcs import get_model, get_features_list, prepare_prediction_data, get_normalized_matrix


# Load in Oanda account data from json
with open('config.json', 'r') as f:
    configs = json.load(f)
    token = configs['token']
    account = configs['account']
    user = configs['user']
    
# Initialize Oanda wrapper
oanda = Oanda(token=token, account=account, user=user)

# Initialize constants
FEATURES_LIST = get_features_list()
RSI_UPPER_THRESHOLD = 75
RSI_LOWER_THRESHOLD = 25
##############################################################################
##############################################################################



##############################################################################
# PREPARATION PHASE ##########################################################
#  if prep_phase or something? lol

# 1. Get latest candles
candles = oanda.get_candle(count=5000, granularity='M5')['candles']
df = pd.DataFrame(candles)
df = transform_candle_data(df)

# 2a. Function call to start training the model?
# 2b. Get new model for the upcoming week based on this data
model = get_model(df)

# 3. Check if trading is open?
# Based on time? Figure this out
##############################################################################
##############################################################################



##############################################################################
# TRADING PHASE ##############################################################
# if trading_phase or something
# WRITE SOME LOOP

# 1. Check if trading is open
# INSERT CHECK HERE

# 2. Refresh candles every interval
candles = oanda.get_candle(count=100, granularity='M5')['candles'] # might change count to 48 or whatever
df = pd.DataFrame(candles)
df = transform_candle_data(df)

# 3a. Get TA indicators
df['RSI'] = RSI(df['c'])
df['MACD'] = MACD(df['c'])
df['MACD Signal'] = MACD_signal(df['c'])

# 3b. Get model prediction
prediction_data = prepare_prediction_data(df)
prediction_data = get_normalized_matrix(prediction_data, FEATURES_LIST)[-1]
prediction_data = prediction_data.reshape(1,len(prediction_data))
prediction = model(prediction_data).numpy().round()[0]
print(prediction)


# 4. Do checks to decide on action
latest_rsi = df.iloc[-1]['RSI']
# let's do MACD another time

# Check if we should buy
if (latest_rsi < RSI_LOWER_THRESHOLD) and (prediction[1] == 1):
    print('BUYYYYY')
elif (latest_rsi > RSI_UPPER_THRESHOLD) and (prediction[2] == 1):
    print('SELLLLL')
else:
    print('DO NOTHING')


##############################################################################
##############################################################################