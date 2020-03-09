# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 23:04:47 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd
import tensorflow as tf

'''
# current plan is to get the mean of the future 24? closes and if it is larger
# than 0.3% (testing on 5M candles) of the original flag as larger

# then part two is to do the same but to flag for lower
# then depending on whether we want to buy or sell, we can fit either model

def shift_data(df, series_name, time_periods=1):
    
    new_df = df.copy()
    
    for period in range(time_periods):
        period += 1
        new_df[series_name+str(period)] = df[series_name].shift(-period)
    
    return(new_df)

def get_future_mean(df, series_name, time_periods=1):
    cols = [series_name+str(period+1) for period in range(time_periods)]
    return(df[cols].mean(axis=1))

def get_larger_flag(df, future_mean_prop_series_name):
    df['flag'] = 0
    df.loc[df[future_mean_prop_series_name] > 0.003, 'flag'] = 1
    
    return(df['flag'])

def get_smaller_flag(df, future_mean_prop_series_name):
    df['flag'] = 0
    df.loc[df[future_mean_prop_series_name] < -0.003, 'flag'] = 1
    
    return(df['flag'])
'''

# FORGET IT LET'S JUST PREDICT 30 MINS INTO THE FUTURE WITH M2 CANDLES

# let's use the last 30 closes and volumes

def shift_data(df, series_name, time_periods=1, down=True):
    
    new_df = df.copy()
    
    for period in range(time_periods):
        period += 1
        if down:
            period = -period
        new_df[series_name+str(period)] = df[series_name].shift(period)
    
    return(new_df)

if __name__ == '__main__':
    
    data_path = 'test_data.csv'
    df = pd.read_csv(data_path)
    
    time_periods = 30
    df = shift_data(df, 'volume', time_periods, down=False)
    df = shift_data(df, 'c', time_periods, down=False)
    
    df['target'] = df['c'].shift(-15)
    
    df = df.dropna()
    
    TRAIN_SPLIT = int(len(df) * 2 / 3)
    
    tf.random.set_seed(0)
    
    
    features_considered = ['volume'+str(period+1) for period in range(time_periods)]
    features_considered2 = ['c'+str(period+1) for period in range(time_periods)]
    
    features_considered.extend(features_considered2)
    features_considered.append('target')
    
    features = df[features_considered]
    features.index=df['time']
    
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(128, activation='relu')
        ])
    
    loss_fn = tf.keras.losses.MeanSquaredError()
    
    dataset = features.iloc[:, :-1].values
    data_mean = dataset.mean(axis=0)
    data_std = dataset.std(axis=0)
    dataset = (dataset-data_mean)/data_std
    
    x_train = dataset[:TRAIN_SPLIT]
    
    x_test = dataset[TRAIN_SPLIT:]
    

    
    # x_train = features.iloc[:TRAIN_SPLIT, :-1].values
    y_train = features.iloc[:TRAIN_SPLIT, -1].values
    
    # x_test = features.iloc[TRAIN_SPLIT:, :-1].values
    y_test = features.iloc[TRAIN_SPLIT:, -1].values
    
    
    model.compile(optimizer='adam',
                  loss=loss_fn,
                  metrics=['MeanAbsoluteError'])
    model.fit(x_train, y_train, epochs=10000)
    model.evaluate(x_test, y_test)
