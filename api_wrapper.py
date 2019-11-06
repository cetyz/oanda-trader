# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 21:19:39 2019

@author: Cetyz
"""

import requests
import json
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import time



class Oanda():
    def __init__(self, token, account, user, practice=True):
        if practice:
            self.base_url = 'https://api-fxpractice.oanda.com'
        else:
            self.base_url = 'https://api-fxtrade.oanda.com'
        self.token = token
        self.account = account
        self.user = user
        print('Client initialized for user', self.user)
        print()

#    def generate_header(self, header_dictionary):
#        header = {}
#        for key, value in header_dictionary.items():
#            header[str(key)] = str(value)
#        return(json.dumps(header))
            
    
    def get_candle(self, time_format='RFC3339', instrument='USD_JPY', count=1):
        """
        Function to get the lastest 5 second candle.
        
        Aside for the params to pass in, all other query parameters will be the default.
        
        Parameters:
        time_format (str): Default time format to 'RFC3339'. Can also be 'UNIX'.
        instrument (str): One of the currency pairs. Defaults to 'USD_JPY'.
        count (int): Number of candles to return. Defaults to '1'. Maximum of '5000'.
        
        Returns:
        JSON object
        """
        headers = {'Authorization': 'Bearer ' + self.token,
                  'Accept-Datetime-Format': time_format}

        url = self.base_url + '/v3/instruments/' + instrument + '/candles' +\
            '?count=' + str(count)
        success = False
        while not success:
            r = requests.get(url=url, headers=headers)
            if r:
                success = True
            else:
                print('Request failed, trying again in 3 secs')
                time.sleep(3)
        return json.loads(r.text)

    def market_order(self, time_format='RFC3339', instrument='USD_JPY', units=10.0):
        """
        Function to create a market order.
        
        For simplicity's sake, you can only pass in the instrument (pair)
        and the number of units to buy/sell
        
        Parameters:
        time_format(str): Default time format to 'RFC3339'. Can also be 'UNIX'
        instrument(str): One of the currency pairs. Defaults to 'USD_JPY'.
        units(float): Number of units to buy (if positive) or sell (if negative)
        """
        headers = {
                'Authorization': 'Bearer ' + self.token,
                'Accept-Datetime-Format': time_format,
                'Content-type': 'application/json',
                }
        
        data = {
            'order': {
                'type': 'MARKET',
                'instrument': instrument,
                'units': str(units),
                'timeInForce': 'FOK',
                'positionFill': 'DEFAULT',
                }
            }
        
        url = self.base_url + '/v3/accounts/' + self.account + '/orders'
        
        r = requests.post(url=url, headers=headers, data=json.dumps(data))

        print(json.loads(r.text))
        return(r)
        
        
if __name__ == "__main__":
    with open('config.json', 'r') as f:
        configs = json.load(f)
        token = configs['token']
        account = configs['account']
        user = configs['user']
        
    oanda = Oanda(token=token, account=account, user=user)
    oanda.market_buy(time_format='RFC3339', instrument='USD_JPY', units=10.0)
    time.sleep(10)
    oanda.market_buy(time_format='RFC3339', instrument='USD_JPY', units=-10.0)