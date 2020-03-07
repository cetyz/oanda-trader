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
    def __init__(self, token, account, user, practice=True, time_format='RFC3339'):
        """
        Create your Oanda client to make requests from.
        
        Parameters:
        token (str): Your secret key.
        account (str): Your account number.
        user (str): Your username.
        pratice (bool): If True, the practice server, else, the regular server.
        time_format (str): Format to return time values in. 'RFC3339' or 'UNIX'.
        
        Returns:
        Oanda object.
        """
        if practice:
            self.base_url = 'https://api-fxpractice.oanda.com'
        else:
            self.base_url = 'https://api-fxtrade.oanda.com'
        self.token = token
        self.account = account
        self.user = user
        self.time_format = time_format
        print('Client initialized for user', self.user)
        print()

#    def generate_header(self, header_dictionary):
#        header = {}
#        for key, value in header_dictionary.items():
#            header[str(key)] = str(value)
#        return(json.dumps(header))
            
    
    def get_candle(self, instrument='USD_JPY', count=1, granularity='S5'):
        """
        Function to get the lastest 5 second candle.
        
        Aside for the params to pass in, all other query parameters will be the default.
        
        Parameters:
        time_format (str): Default time format to 'RFC3339'. Can also be 'UNIX'.
        instrument (str): One of the currency pairs. Defaults to 'USD_JPY'.
        count (int): Number of candles to return. Defaults to '1'. Maximum of '5000'.
        granularity (str): S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1,
            H2, H3, H4, H6, H8, H12, D, W, M. Defaults to 'S5'.
        
        Returns:
        JSON object
        """
        print('Attemping to get the last', count, instrument, granularity, 'candles')
        headers = {'Authorization': 'Bearer ' + self.token,
                  'Accept-Datetime-Format': self.time_format}

        url = self.base_url + '/v3/instruments/' + instrument + '/candles' +\
            '?count=' + str(count) + '&granularity=' + str(granularity)
        success = False
        while not success:
            r = requests.get(url=url, headers=headers)
            if r:
                success = True
            else:
                print('Request failed, trying again in 3 secs')
                time.sleep(3)
        return json.loads(r.text)

    def market_order(self, instrument='USD_JPY', units=10.0, stop_loss=None, take_profit=None):
        """
        Function to create a market order.
        
        For simplicity's sake, you can only pass in the instrument (pair)
        and the number of units to buy/sell
        
        Parameters:
        time_format(str): Default time format to 'RFC3339'. Can also be 'UNIX'
        instrument(str): One of the currency pairs. Defaults to 'USD_JPY'.
        units(float): Number of units to buy (if positive) or sell (if negative)
        stop_loss(float or int): Price at which to set stop loss
        take_profit(float or int): Price at which to set take profit
        """
        headers = {
                'Authorization': 'Bearer ' + self.token,
                'Accept-Datetime-Format': self.time_format,
                'Content-type': 'application/json',
                }
        
        stop_loss_details = {
                'price': stop_loss,
                }
        
        take_profit_details = {
                'price': take_profit,
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
        
        if stop_loss is not None:
            data['order']['stopLossOnFill'] = stop_loss_details
        
        if take_profit is not None:
            data['order']['takeProfitOnFill'] = take_profit_details
        
        url = self.base_url + '/v3/accounts/' + self.account + '/orders'
        
        r = requests.post(url=url, headers=headers, data=json.dumps(data))

        print(json.loads(r.text))
        return(r)
        
    def get_open_positions(self):
        """
        Function to get all OPEN positions.
        
        """
        
        headers = {
                'Authorization': 'Bearer ' + self.token,
                }
        
        url = self.base_url + '/v3/accounts/' + self.account + '/openPositions'
        
        r = requests.get(url=url, headers=headers)
        
        return(r.text)
        
        
if __name__ == "__main__":
   
    with open('config.json', 'r') as f:
        configs = json.load(f)
        token = configs['token']
        account = configs['account']
        user = configs['user']
        
    oanda = Oanda(token=token, account=account, user=user)
    candles = oanda.get_candle(count=5)['candles']
    print(candles)
#        
#    print(oanda.get_open_positions())
#        
#    oanda.market_order(instrument='USD_JPY', units=10.0, stop_loss=1, take_profit=10000)
#    print(oanda.get_open_positions())
#    time.sleep(10)
#    oanda.market_order(instrument='USD_JPY', units=-10.0, stop_loss=1, take_profit=10000)
#    print(oanda.get_open_positions())