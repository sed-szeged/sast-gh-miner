import requests
from collections import abc


class GraphQL:
    def __init__(self, token=''):
        self._token = token
        self._headers = self._create_header()
        # self._query = query
        
    @property
    def token(self):
        print('Token was set:', end=' ') 
        print(self._token is not '')
        
    @token.setter
    def token(self, value):
        self._token = value

    def _create_header(self):
        return {"Authorization": "Bearer " + self._token}
    
    def run_query(self, query):
        page = 'https://api.github.com/graphql'
        request = requests.post(page, json={'query': query}, headers=self._headers)
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


class Generic:
        def __init__(self, dictionary={}):
            self.fill(dictionary)
        
        def fill(self, dictionary):
            for key, value in dictionary.items():
                #print(key)
                if isinstance(value, abc.Mapping):
                    a = Generic(value)
                    setattr(self, key, a)
                else:
                    setattr(self, key, value)



class GenericSimpleDict():
    def __init__(self, valami):
        for key, value in valami.items():
            setattr(self, key, value)
            
class Result:
    def __init__(self, res):
        try:
            self.rateLimit = GenericSimpleDict(res['data']['rateLimit'])
        except KeyError as e:
            print("Key error:", e)

        try:
            self.pageInfo = GenericSimpleDict(res['data']['search']['pageInfo'])
        except KeyError as e:
            print("Key error:", e)
        
        try:
            self.codeCount = res['data']['search']['codeCount']
        except KeyError as e:
            print("Key error:", e)
        
        try:
            self.repos = res['data']['search']['edges']    
        except KeyError as e:
            print("Key error:", e)
        
            
    def get_issues(self):
        for repo in self.repos:
            yield GenericSimpleDict(repo['node'])


class DictObj:
        def __init__(self, dictionary={}):
            try:
                self.fill(dictionary)
            except Exception:
                pass
        def fill(self, dictionary):
                for key, value in dictionary.items():
                    if isinstance(value, abc.Mapping):
                        setattr(self, key, DictObj(value))
                    elif isinstance(value, (list,)):
                        setattr(self, key, ListObj(value))
                    else:
                        setattr(self, key, value)


class SonarDictObj:
    def __init__(self, data, name='a'):
            self.fill(data, name)

    def fill(self, data, name='a'):
            if isinstance(data, abc.Mapping):
                # print('asdasdsdadsdas')
                for key, value in data.items():
                    if isinstance(value, list):
                        setattr(self, key, SonarDictObj(value))
                    else:
                        setattr(self, key, value)


            elif isinstance(data, list):
                
                for i in data:
                    if isinstance(i, abc.Mapping):

                        if i.get('path', False) is not False:                                          
                            #print('PATH')
                            name = i['path'].split('/')[1]
                            setattr(self, name, SonarDictObj(i))
                        elif i.get('key', False) is not False:
                            #print('KEY')
                            name = i['key']
                            setattr(self, name, SonarDictObj(i))
                        else:
                            for ki, vi in i.items():
                                setattr(self, ki, SonarDictObj(vi, ki))

                    else: 
                        setattr(self, name, i)

            else:
                setattr(self, name, data)

    def __str__(self):
        for attr in self.__dir__():
            # print('-', attr)        
            if attr.startswith('__') is False and attr is not 'fill':
                call = self.__getattribute__(attr)
                print(attr, ' - ', call)
                call()



class SonarList:
    def __init__(self, items, name):
        for i in items:
            if isinstance(i, abc.Mapping):
                setattr(self, name, SonarDictObj(i))
            else:
                setattr(self, name, i)


class ListObj:
    def __init__(self, items):
        self.elements = []
        self.append(items)
    
    def append(self, items):
        for i in items:
            self.elements.append(DictObj(i))


