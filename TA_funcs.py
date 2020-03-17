# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 19:29:41 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd

def RSI(series, window=14):
    # which is 100 - (100 / (1 + RS))
    # where RS = Average Gain / Average Loss
    
    delta = series.diff()
    up_days = delta.copy()
    up_days[delta<=0]=0.0
    down_days = abs(delta.copy())
    down_days[delta>0]=0.0
    RS_up = up_days.rolling(window).mean()
    RS_down = down_days.rolling(window).mean()
    return(100-100/(1+RS_up/RS_down))
    
def MACD(series):
    
    close = series
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    return(macd)

def MACD_signal(series):
    close = series
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    return(signal)

if __name__ == '__main__':
        
    data_path = 'test_data.csv'
    df = pd.read_csv(data_path, index_col=0)
    
    df['RSI'] = RSI(df['c'])
    df['MACD'] = MACD(df['c'])
    df['MACD Signal'] = MACD_signal(df['c'])
    
    print(df)