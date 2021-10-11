from .graphql import DictObj
from .session import Session

class Sonar:
    def __init__(self, token):
        self._sess = Session(token)
        self.ps = 500
    
    def activate_rule(self, quality_profile, rule):
        '''
        rule str, squid:S12345
        '''
        url = f'http://localhost:9000/api/qualityprofiles/activate_rule?key={quality_profile}&rule={rule}'
        status, data = self._sess.post(url)        
        return status, data
    
    def activate_rules(self, quality_profile : str, rules : list):
        for rule in rules:
            status, data = self.activate_rule(quality_profile, rule)
            print(status, data)
    
    def deactivate_rules(self, quality_profile, languages='java'):
        url = f'http://localhost:9000/api/qualityprofiles/deactivate_rules?targetKey={quality_profile}&languages={languages}'
        status, data = self._sess.post(url)
        return status, data
    
    def quality_profile_search(self, name):
        url = f'http://localhost:9000/api/qualityprofiles/search?qualityProfile={name}'
        status, data = self._sess.post(url)
        return status, data
    
    def quality_profile_rules(self, quality_profile_key, activation='true', p=1):
        url = f'http://localhost:9000/api/rules/search?activation={activation}&qprofile={quality_profile_key}'
        status, data = self._sess.post(url)
        return status, data
    
    def get_projects(self, csl_of_pkeys, p=1):
        '''
        csl_of_pkeys : comma separated list of project keys 
        '''
        url = f'http://localhost:9000/api/projects/search?projects={csl_of_pkeys}&ps={seld.ps}&p={p}'
        print(url)
    
    def delete_projects(self, word='squid'):
        url = f'http://localhost:9000/api/projects/bulk_delete?q={word}'
        status, data = self._sess.post(url)
        return status, data