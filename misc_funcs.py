# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 22:01:27 2020

@author: Cetyz
"""

from datetime import datetime as dt

def is_trading_hours():
    full_open_days = [0, 1, 2, 3]
    now = dt.utcnow()
    if now.weekday() in full_open_days:
        return(True)
    elif (now.weekday() == 6) and (now.hour > 22):
        return(True)
    elif (now.weekday() == 4) and (now.hour < 22):
        return(True)
    else:
        return(False)
    