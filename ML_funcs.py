# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 23:04:47 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils import shuffle

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



if __name__ == '__main__':
    
    data_path = 'test_data.csv'
    df = pd.read_csv(data_path)
    
    time_periods = 36
    features_list = ['volume', 'c']
    
    historical_data = create_historical_data(df, features_list, time_periods)
    
    df = df.join(historical_data)
    
    target_name = 'c'
    num_of_targets = 5
    future_periods = 36
    future_data = create_future_data(df, target_name, num_of_targets, future_periods)
    
    mean_future_data = future_data.median(axis=1)
    mean_future_data.name = 'future_median'
    
    df = df.join(mean_future_data)
    
    df['diff prop'] = (df['future_median'] - df['c']) / df['c']
    
    df['is_diff'] = 0
    df.loc[df['diff prop'] > 0.005, 'is_diff'] = 1
    df.loc[df['diff prop'] < -0.005, 'is_diff'] = 2
    
    df = df.dropna()
    
    targets_df = pd.get_dummies(df['is_diff'])
    
    num_of_cats = len(targets_df.columns)
    
    features_considered = ['volume'+'-'+str(period+1) for period in range(time_periods)]
    features_considered2 = ['c'+'-'+str(period+1) for period in range(time_periods)]
    
    features_considered.extend(features_considered2)
    
    features = df[features_considered]
    features.index=df['time']

    TRAIN_SPLIT = int(len(features) * 2 / 3)
    
    tf.random.set_seed(0)    
    
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(600, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax'),
        ])
    
    loss_fn = tf.keras.losses.CategoricalCrossentropy()
    
    # dataset = features.iloc[:, :-1].values
    dataset = features.values
    data_mean = dataset.mean(axis=0)
    data_std = dataset.std(axis=0)
    dataset = (dataset-data_mean)/data_std
    
    targets = targets_df.values
    
    dataset, targets = shuffle(dataset, targets, random_state=0)
    
    x_train = dataset[:TRAIN_SPLIT]
    
    x_test = dataset[TRAIN_SPLIT:]

    y_train = targets[:TRAIN_SPLIT]

    y_test = targets[TRAIN_SPLIT:]
    
    
    model.compile(optimizer='adam',
                  loss=loss_fn,
                  metrics=['CategoricalAccuracy'])
    
    predictions = model(x_train).numpy()
    
    model.fit(x_train, y_train, epochs=1000)
    
    model.evaluate(x_test, y_test)
