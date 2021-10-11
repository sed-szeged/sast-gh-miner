import os

class Path:
    def __init__(self, path):
        self.path = path
    
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        
        folder = '/'.join(value.split('/')[0:-1])
        print(f'Folder check: {folder}')
        if not os.path.exists(folder):
            self._path = 'Invalid Path'
            raise ValueError('Path does not exists!')
        if os.path.isabs(folder):
            self._path = value
        else:
            self._path = os.path.abspath(value).replace('\\','/')

    def __str__(self):
        return self._path


def check_path(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)