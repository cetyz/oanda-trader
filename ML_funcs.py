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

"""

def prepare_data(candles_df, features_list=['volume', 'c'], target_feature='c',
                 historical_periods=48, future_periods=36, future_targets=6,
                 percent_diff_threshold=0.004, future_median_name='future_median',
                 target_cat_name='is_diff'):
    
    print('Preparing data...')
    print('Converting candles json into DataFrame...')
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

def get_features_list(features_considered=['volume', 'c'], historical_periods=48):
    features_list = []
    for feature in features_considered:
        features_list.append(feature)
        temp = [feature+'-'+str(period+1) for period in range(historical_periods)]
        features_list.extend(temp)
    return(features_list)

def get_normalized_matrix(df, features_list):
    features = df[features_list]
    dataset = features.values
    data_mean = dataset.mean(axis=0)
    data_std = dataset.std(axis=0)
    dataset = (dataset-data_mean)/data_std
    return(dataset)

if __name__ == '__main__':
    
    data_path = 'test_data.csv'
    df = pd.read_csv(data_path)
    df = prepare_data(df)
    df = balance_classes(df)    
    targets_df = get_targets(df)
    num_of_cats = len(targets_df.columns)
    features_list = get_features_list()
    
    tf.random.set_seed(0)    
    
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(600, activation='relu'))
    model.add(tf.keras.layers.Dense(256, activation='relu'))
    model.add(tf.keras.layers.Dense(3, activation='softmax'))
    
    loss_fn = tf.keras.losses.CategoricalCrossentropy()
    
    # dataset = features.values
    # data_mean = dataset.mean(axis=0)
    # data_std = dataset.std(axis=0)
    # dataset = (dataset-data_mean)/data_std
    
    dataset = get_normalized_matrix(df, features_list)
    
    TRAIN_SPLIT = int(len(dataset) * 2 / 3)
    print(TRAIN_SPLIT)
    
    targets = targets_df.values
    
    dataset, targets = shuffle(dataset, targets, random_state=0)
    
    x_train = dataset[:TRAIN_SPLIT]
    
    x_test = dataset[TRAIN_SPLIT:]

    y_train = targets[:TRAIN_SPLIT]

    y_test = targets[TRAIN_SPLIT:]
    
    
    model.compile(optimizer='adam',
                  loss=loss_fn,
                  metrics=['CategoricalAccuracy'])
    
    
    
    model.fit(x_train, y_train, epochs=200)
    
    model.evaluate(x_test, y_test)
    
    predictions = model(x_test).numpy()
    
    print(model(x_test[-1].reshape(1,len(x_test[-1]))).numpy().round())
