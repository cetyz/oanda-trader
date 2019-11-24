# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 22:50:56 2019

@author: Cetyz
"""

from api_wrapper import Oanda
from temp.google_utils.authentication.authenticator import Authenticator
from temp.google_utils.sheets.sheetmanager import SheetManager

keys = 'google-keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


spreadsheetId = '1YAaNGBjZOIAFafTdIfxq9rO6n8RyY8RER7pkVEWdD-U'
append_range = 'Data'



authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)

manager = SheetManager(creds)

print(manager.get_values(spreadsheetId=spreadsheetId,
                         data_range=append_range))

# =============================================================================
# if __name__ == "__main__":
#     with open('config.json', 'r') as f:
#         configs = json.load(f)
#         token = configs['token']
#         account = configs['account']
#         user = configs['user']
#         
#     oanda = Oanda(token=token, account=account, user=user)
#     print(oanda.get_candle())
# =============================================================================
