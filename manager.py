# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 02:51:48 2020

@author: Cetyz
"""

import json
import numpy as np
import pandas as pd

from api_wrapper import Oanda

# get log in info from json
with open('config.json', 'r') as f:
    configs = json.load(f)
    token = configs['token']
    account = configs['account']
    user = configs['user']
    
