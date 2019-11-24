# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 16:19:38 2019

@author: charles.tan
"""

'''
Create a class to handle authentication
1. Read in your keys (json) when you create the authenticator
2. Get your creds (using get_creds) that you can then use!
'''

import json
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account

class Authenticator():
    def __init__(self, keys):
        self.keys = keys

    def get_creds(self, scopes):
        '''
        Perform the necessary authentications
        And return credentials
        '''
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        key_type = json.load(open(self.keys, 'r'))['type']
        if key_type != 'service_account':
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.keys, scopes)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
        else:
            # in case you're using service account keys
            creds = service_account.Credentials.from_service_account_file(
                    'keys.json').with_scopes(scopes)
        return(creds)

# if you want to run for debugging purposes
if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive',]
    keys = 'keys.json'
    authenticator = Authenticator(keys)
    creds = authenticator.get_creds(scopes)
    print(creds)
