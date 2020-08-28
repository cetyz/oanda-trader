# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 00:24:04 2020

@author: Cetyz
"""

"""
Oanda trading bot to use an honestly brainless algorithm.
Just interested to see if it would work.

At every time interval:
    Check for trading hours:
        Check if a position is open:
            If not, open position of size X
            If position open:
                Get the average buy in price of the position
                If current price greater than average buy in price by y%:
                    Sell entire position and make y% profit
                If not:
                    Check if current price lower than average buy in price by z%:
                        Add X to position
                    Otherwise do nothing

"""

##############################################################################
# SETUP PHASE ################################################################
# 1. Import necessary libraries
import json
from time import sleep

import numpy as np
import pandas as pd

from api_wrapper import Oanda
# from TA_funcs import RSI, MACD, MACD_signal
# from data_funcs import transform_candle_data
# from ML_funcs import get_model, get_features_list, prepare_prediction_data, get_normalized_matrix
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
time_interval = 300 # seconds?
buy_size = 100 # units
profit_threshold = 0.0005
buying_threshold = 0.00025

while True:
    
    if is_trading_hours:
        
        # check if we have an open long position
        print('Getting open positions...')
        while True:
            try:
                positions = json.loads(oanda.get_open_positions())['positions']
                break
            except:
                pass
        # if we don't
        if len(positions) == 0:
            # start a new one
            print('Opening new position')
            oanda.market_order(instrument='USD_JPY', units=buy_size)
            print('Position opened')

        # if we do
        else:
            # get size and average buy in price of the position
            print('Position found!')
            size = int(positions[0]['long']['units'])
            average_price = round(float(positions[0]['long']['averagePrice']), 3)
            
            # get the current price
            current_price = round(float(oanda.get_candle()['candles'][0]['mid']['c']), 3)
            
            price_diff = current_price - average_price
            diff_percent = price_diff / average_price
            
            print('Position size:', size, 'Average Price:', average_price)
            print('Current price:', current_price, '% diff:', diff_percent)
            
            if diff_percent > profit_threshold:
                print('Closing position...')
                oanda.market_order(units=-size)
                print('Position closed. Sold', size)
            elif diff_percent < -buying_threshold:
                print('Adding to position...')
                oanda.market_order(units=buy_size)
                print('Added', buy_size, 'to position')
            else:
                print('Doing nothing')
            
    sleep(time_interval)
            
            