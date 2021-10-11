from os.path import isfile

class FileHandler:
    def __init__(self, path):
#        if not isfile(path):
#            raise OSError('Bad path given.')
        if type(path) is not str:
            raise TypeError(f'path should be a \'str\', {type(path).__name__} was given.')
        self._path = path
            
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, value):
        self._path = value

    def write(self, line):
        file = open(self.path, 'a')
        file.write(line)
        file.close()

    def write_lines(self, chunk):
        pass

    def len(self):
        with open(self.path, 'r') as f:
            for i, _  in enumerate(f):
                pass
        return i + 1

    def read(self):
        with open(self.path, 'r') as f:
            line = f.readline()
            while line:
                yield line
                line = f.readline()
    
    def last_row(self):
        with open(self._path, 'r') as f:
            for _, row in enumerate(f):
                pass
        return row

    def __str__(self):
        return self._path
