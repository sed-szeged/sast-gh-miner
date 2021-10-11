import requests
import json

class Session:
    def __init__(self, token):
        self.token = token
        self._create_session()
        
    def get(self, url):
        data = {}
        result = self.session.get(url)
        try:
            # json loads from binary data
            data = json.loads(result.content) 
        except Exception as e:
            print('Exception: ', e)
        return (result.status_code, data)
    
    def post(self, url):
        data = {}
        result = self.session.post(url)
        try:
            # json loads from binary data
            data = json.loads(result.content) 
        except Exception as e:
            print('Exception: ', e)
        return (result.status_code, data)
    
    def _create_session(self):
        self.session = requests.Session()
        self.session.auth = self.token, ''
    
    