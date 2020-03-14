# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 23:04:47 2020

@author: Cetyz
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils import shuffle
from sklearn.utils import resample

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
    
    time_periods = 48
    features_list = ['volume', 'c']
    
    historical_data = create_historical_data(df, features_list, time_periods)
    
    df = df.join(historical_data)
    
    target_name = 'c'
    num_of_targets = 6
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
    
    # BALANCE
    df_no_diff = df[df['is_diff'] == 0]
    
    df_higher = df[df['is_diff'] == 1]
    df_lower = df[df['is_diff'] == 2]
    
    df_higher_upsampled = resample(df_higher,
                                  replace=True,
                                  n_samples=len(df_no_diff),
                                  random_state=0)
    
    df_lower_upsampled = resample(df_lower,
                                 replace=True,
                                 n_samples=len(df_no_diff),
                                 random_state=0)
    
    df = pd.concat([df_no_diff, df_higher_upsampled, df_lower_upsampled])
    
    
    targets_df = pd.get_dummies(df['is_diff'])
    
    num_of_cats = len(targets_df.columns)
    
    features_considered = ['volume'+'-'+str(period+1) for period in range(time_periods)]
    features_considered2 = ['c'+'-'+str(period+1) for period in range(time_periods)]
    
    features_considered.extend(features_considered2)
    
    features = df[features_considered]
    features.index=df['time']

    TRAIN_SPLIT = int(len(features) * 2 / 3)
    
    tf.random.set_seed(0)    
    
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(600, activation='relu'))
    model.add(tf.keras.layers.Dense(256, activation='relu'))
    model.add(tf.keras.layers.Dense(3, activation='softmax'))
    
    # model = tf.keras.models.Sequential([
    #     tf.keras.layers.Dense(600, activation='relu'),
    #     tf.keras.layers.Dense(256, activation='relu'),
    #     tf.keras.layers.Dense(3, activation='softmax'),
    #     ])
    
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
    
    
    
    model.fit(x_train, y_train, epochs=5000)
    
    model.evaluate(x_test, y_test)
    
    predictions = model(x_test).numpy()
