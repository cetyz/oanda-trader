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
3. Once model is trained, move to Waiting Phase

WAITING PHASE:
1. Model is trained (from Prep Phase) but market is closed
2. Wait while checking if the market is opening

TRADING PHASE:
(When trading is open)

1a. Check if trading is open (if open, proceed, else proceed to Prep phase)
1b. Check if we have an open position
2. Refresh candles every interval (only what is necessary to get X last values)
3a. Using the new data, get TA indicators
3b. Get model prediction based on model from Prep Phase
4. Do checks to decide on action (e.g. if RSI < .25 and whatever, do X)

"""

"""
TODO: In addition to MAKING IT WORK

Currently in ML_funcs, a lot of parameters are hardcoded and called as default
parameters

Tidy that up and include them as constants that we can tweak in this script

"""

##############################################################################
# SETUP PHASE ################################################################
# 1. Import necessary libraries
import json
from time import sleep

import numpy as np
import pandas as pd

from api_wrapper import Oanda
from TA_funcs import RSI, MACD, MACD_signal
from data_funcs import transform_candle_data
from ML_funcs import get_model, get_features_list, prepare_prediction_data, get_normalized_matrix
from misc_funcs import is_trading_hours


# Load in Oanda account data from json
with open('config.json', 'r') as f:
    configs = json.load(f)
    token = configs['token']
    account = configs['account']
    user = configs['user']
    
# Initialize Oanda wrapper
oanda = Oanda(token=token, account=account, user=user)

# Initialize constants
CANDLE_GRANULARITY = 'M5'
FEATURES_LIST = get_features_list()
RSI_UPPER_THRESHOLD = 75
RSI_LOWER_THRESHOLD = 25

RANDOM_SEED = None # integer or None
FEATURES_LIST = ['volume', 'c']
TARGET_FEATURE = 'c'
HISTORICAL_PERIODS = 48
FUTURE_PERIODS = 12
FUTURE_TARGETS = 6
PERCENT_DIFF_THRESHOLD = 0.004
FUTURE_MEDIAN_NAME = 'future_median'
TARGET_CAT_NAME = 'is_diff'
EPOCHS = 400
##############################################################################
##############################################################################


# start main loop here?
while True:

##############################################################################
# PREPARATION PHASE ##########################################################


# 1. Get latest candles
    candles = oanda.get_candle(count=5000, granularity=CANDLE_GRANULARITY)['candles']
    df = pd.DataFrame(candles)
    df = transform_candle_data(df)

# 2a. Function call to start training the model?
# 2b. Get new model for the upcoming week based on this data
    model = get_model(df, features_list=FEATURES_LIST, target_feature=TARGET_FEATURE,
                      historical_periods=HISTORICAL_PERIODS, future_periods=FUTURE_PERIODS,
                      future_targets=FUTURE_TARGETS, percent_diff_threshold=PERCENT_DIFF_THRESHOLD,
                      future_median_name=FUTURE_MEDIAN_NAME, target_cat_name=TARGET_CAT_NAME,
                      random_seed=RANDOM_SEED, epochs=EPOCHS)

# 3. Once model is trained, enter next phase



##############################################################################
##############################################################################



##############################################################################
# WAITING PHASE ##############################################################

    while not is_trading_hours():
        print('Not trading hours...')
        sleep(300)

##############################################################################
##############################################################################



##############################################################################
# TRADING PHASE ##############################################################

# 1a. Check if trading is open
    while is_trading_hours():   

# 1b. Check if we have an open position
        open_positions = json.loads(oanda.get_open_positions())['positions']
        if len(open_positions) <= 0:

# # 2. Refresh candles every interval
            candles = oanda.get_candle(count=100, granularity=CANDLE_GRANULARITY)['candles'] # might change count to 48 or whatever
            df = pd.DataFrame(candles)
            df = transform_candle_data(df)

# 3a. Get TA indicators
            df['RSI'] = RSI(df['c'])
            df['MACD'] = MACD(df['c'])
            df['MACD Signal'] = MACD_signal(df['c'])

# 3b. Get model prediction
            full_features_list = get_features_list(FEATURES_LIST, HISTORICAL_PERIODS)
            prediction_data = prepare_prediction_data(df)
            prediction_data = get_normalized_matrix(prediction_data, full_features_list)[-1]
            prediction_data = prediction_data.reshape(1,len(prediction_data))
            prediction = model(prediction_data).numpy().round()[0]
            print('Model prediction:', prediction)


# 4. Do checks to decide on action
            latest_rsi = df.iloc[-1]['RSI']
            print('RSI is:', latest_rsi)
# let's do MACD another time

# Check if we should buy

# Get latest price
            latest_price = df.iloc[-1]['c']
            stop_loss = 0.0015
            take_profit = 0.003
        
            print('Decision is:')
            if (latest_rsi < RSI_LOWER_THRESHOLD) and (prediction[1] == 1):
                print('Buying...')
                oanda.market_order(instrument='USD_JPY', units=1000.0,
                                   stop_loss=str(round(latest_price-latest_price*stop_loss, 3)),
                                   take_profit=str(round(latest_price+latest_price*take_profit, 3)))
            elif (latest_rsi > RSI_UPPER_THRESHOLD) and (prediction[2] == 1):
                print('Selling...')
                oanda.market_order(instrument='USD_JPY', units=-1000.0,
                                   stop_loss=str(round(latest_price+latest_price*stop_loss, 3)),
                                   take_profit=str(round(latest_price-latest_price*take_profit, 3)))
            else:
                print('Doing nothing...')
            
            print('Waiting...')
            sleep(300)
            print('----------------------------------------------------------')
            
        else:
            print('Current position:', open_positions[0])
            sleep(300)
            print('----------------------------------------------------------')

##############################################################################
##############################################################################