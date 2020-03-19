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

from data_funcs import create_historical_data, create_future_data

"""
Need functions to:
    
1. Start training model
2. Return model (and the keras model itself should have its own predcit function)


I NEED TO TIDY UP AND DOCUMENT THIS THING. Get rid of the hardcoded function
parameters. Initialize constants in the main Bot script and use them instead

"""

def prepare_prediction_data(candles_df, features_list=['volume', 'c'],
                            historical_periods=48):
    df = candles_df.copy()
    historical_data = create_historical_data(candles_df, features_list, historical_periods)
    df = df.join(historical_data)
    df = df.dropna()
    return(df)
    

def prepare_data(candles_df, features_list=['volume', 'c'], target_feature='c',
                 historical_periods=48, future_periods=36, future_targets=6,
                 percent_diff_threshold=0.004, future_median_name='future_median',
                 target_cat_name='is_diff'):

    df = candles_df.copy()
    historical_data = create_historical_data(candles_df, features_list, historical_periods)
    df = df.join(historical_data)
    
    future_data = create_future_data(candles_df, target_feature, future_targets, future_periods)
    median_future_data = future_data.median(axis=1)
    median_future_data.name = future_median_name
    
    compare_df = pd.DataFrame()
    compare_df[target_feature] = df[target_feature]
    compare_df = compare_df.join(median_future_data)
    
    compare_df['diff prop'] = ((compare_df[future_median_name] - df[target_feature]) / df[target_feature])
    compare_df[target_cat_name] = 0
    compare_df.loc[compare_df['diff prop'] > percent_diff_threshold, target_cat_name] = 1
    compare_df.loc[compare_df['diff prop'] < -percent_diff_threshold, target_cat_name] = 2
    
    df = df.join(compare_df[target_cat_name])
    df = df.dropna()
    return(df)

def balance_classes(unbalanced_df, col_to_balance='is_diff', random_state=0):
    df = unbalanced_df.copy()
    classes = df[col_to_balance].unique().tolist()
    max_class_size = max([len(df[df[col_to_balance] == class_]) for class_ in classes])
    
    balanced_df = pd.DataFrame()
    for class_ in classes:
        working_df = df[df[col_to_balance] == class_]
        if len(working_df) < max_class_size:
            working_df = resample(working_df,
                                  replace=True,
                                  n_samples=max_class_size,
                                  random_state=random_state)
        
        balanced_df = pd.concat([balanced_df, working_df])
    return(balanced_df)
    
def get_targets(df, classification_label='is_diff'):    
    return(pd.get_dummies(df[classification_label]))

def get_features_list(features_list=['volume', 'c'], historical_periods=48):
    list_of_features = []
    for feature in features_list:
        list_of_features.append(feature)
        temp = [feature+'-'+str(period+1) for period in range(historical_periods)]
        list_of_features.extend(temp)
    return(list_of_features)

def get_normalized_matrix(df, features_list):
    features = df[features_list]
    dataset = features.values
    data_mean = dataset.mean(axis=0)
    data_std = dataset.std(axis=0)
    dataset = (dataset-data_mean)/data_std
    return(dataset)

def get_model(candle_df, features_list, target_feature,
              historical_periods, future_periods, future_targets,
              percent_diff_threshold, future_median_name, target_cat_name,
              random_seed, epochs):
    
    df = prepare_data(candle_df, features_list=features_list,
                      target_feature=target_feature,
                      historical_periods=historical_periods,
                      future_periods=future_periods,
                      future_targets=future_targets,
                      percent_diff_threshold=percent_diff_threshold,
                      future_median_name=future_median_name,
                      target_cat_name=target_cat_name)
    
    df = balance_classes(df, col_to_balance=target_cat_name)
    
    targets_df = get_targets(df, classification_label=target_cat_name)
    
    full_features_list = get_features_list(features_list=features_list,
                                           historical_periods=historical_periods)
    
    if random_seed is not None:
        tf.random.set_seed(random_seed)
        
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(98, activation='relu'))
    model.add(tf.keras.layers.Dense(60, activation='relu'))
    model.add(tf.keras.layers.Dense(3, activation='softmax'))
    
    loss_fn = tf.keras.losses.CategoricalCrossentropy()
        
    dataset = get_normalized_matrix(df, features_list=full_features_list)
    
    TRAIN_SPLIT = int(len(dataset) * 2 / 3)

    targets = targets_df.values
    
    dataset, targets = shuffle(dataset, targets, random_state=0)
    
    x_train = dataset[:TRAIN_SPLIT]    
    x_test = dataset[TRAIN_SPLIT:]
    y_train = targets[:TRAIN_SPLIT]
    y_test = targets[TRAIN_SPLIT:]
        
    model.compile(optimizer='adam',
                  loss=loss_fn,
                  metrics=['CategoricalAccuracy'])   
    
    model.fit(x_train, y_train, epochs=epochs)
    
    model.evaluate(x_test, y_test)
    
    return(model)
    

if __name__ == '__main__':
    
    RANDOM_SEED = 0 # integer or None
    
    FEATURES_LIST = ['volume', 'c']
    TARGET_FEATURE = 'c'
    HISTORICAL_PERIODS = 48
    FUTURE_PERIODS = 36
    FUTURE_TARGETS = 6
    PERCENT_DIFF_THRESHOLD = 0.004
    FUTURE_MEDIAN_NAME = 'future_median'
    TARGET_CAT_NAME = 'is_diff'
    EPOCHS = 200
    
    data_path = 'test_data.csv'
    df = pd.read_csv(data_path)
    
    model = get_model(df, features_list=FEATURES_LIST, target_feature=TARGET_FEATURE,
                      historical_periods=HISTORICAL_PERIODS, future_periods=FUTURE_PERIODS,
                      future_targets=FUTURE_TARGETS, percent_diff_threshold=PERCENT_DIFF_THRESHOLD,
                      future_median_name=FUTURE_MEDIAN_NAME, target_cat_name=TARGET_CAT_NAME,
                      random_seed=RANDOM_SEED, epochs=EPOCHS)
    
    full_features_list = get_features_list(FEATURES_LIST, HISTORICAL_PERIODS)
    prediction_data = prepare_prediction_data(df)
    print(prediction_data)
    prediction_data = get_normalized_matrix(prediction_data, full_features_list)[-1]
    print(prediction_data)
    prediction_data = prediction_data.reshape(1,len(prediction_data))
    print(prediction_data)
    prediction = model(prediction_data).numpy().round()[0]
    print('Model prediction:', prediction)
