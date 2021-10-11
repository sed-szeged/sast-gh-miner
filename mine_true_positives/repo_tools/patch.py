class Patch:
    def __init__(self, patch):
        self._raw_patch = patch
        self.hunks = self.get_hunks(patch)
    
    def get_hunks(self, patch):
        monkey = patch.split('@@')
        monkey

        hunks = []
        for i, v in enumerate(monkey):
            if i%2 is not 0 and i is not 0:
                hunks.append(Hunk(v, monkey[i+1]))
        return hunks

    def __str__(self):
        return self._raw_patch
    

class Hunk:
    def __init__(self, info, code):
        self._info = info
        self._raw_code = code
        self._code = code.split('\n')
        self._first_row = self.get_first_row(self._info)
        self._added_lines = self.get_added_lines(self._code)
        self._subtracted_lines = self.get_subtracted_lines(self._code)
        self._modified_code = self.get_modified_code()
        self._original_code = self.get_original_code()
    
    def get_original_code(self):
        og_code = []
        for line in self._code[1:-1]:
            if line.startswith('+') is False:
                if line.startswith('-'):
                    og_code.append(line[1:])
                else:
                    og_code.append(line[1:])  # a patch file kezdete: +, -, space
        return og_code
    
    def get_modified_code(self):
        modified_code = []
        for line in self._code[1:-1]:
            if line.startswith('-') is False:
                if line.startswith('+'):
                    modified_code.append(line[1:]) # repr
                else:
                    modified_code.append(line[1:])
        return modified_code
    
    def get_added_lines(self, value):
        added_lines = []
        for line in self._code:
            if line.startswith('+'):
                added_lines.append(line)
        return added_lines

    def get_subtracted_lines(self, value):
        subtracted_lines = []
        for line in self._code:
            if line.startswith('-'):
                subtracted_lines.append(line)
        return subtracted_lines

    @property
    def added_lines(self):
        return self._added_lines
    @added_lines.setter
    def added_lines(self, value):
        self._added_lines = value
    
    @property
    def subtracted_lines(self):
        return self._subtracted_lines
    @subtracted_lines.setter
    def subtracted_lines(self, value):
        self._subtracted_lines = value
    
    @property
    def raw_code(self):
        return self._raw_code
    @raw_code.setter
    def raw_code(self, value):
        self._raw_code = value
    
    @property
    def info(self):
        return self._info
    @info.setter
    def info(self, value):
        self._info = value
    
    @property
    def modified_code(self):
        return self._modified_code
    @modified_code.setter
    def modified_code(self, value):
        self._modified_code = value
    
    @property
    def original_code(self):
        return self._original_code
    @original_code.setter
    def original_code(self, value):
        self._original_code = value
    
    @property
    def code(self):
        return self._code
    @code.setter
    def code(self, value):
        self._code = value
    
    @property
    def first_row(self):
        return self._first_row
    
    @first_row.setter
    def first_row(self, value):
        self._first_row = value
    
    def get_first_row(self, value):
        return int(value.strip().split(',')[0])
    
    def __str__(self):
        return self._info


def read_file_in_hunks(file, size):
    hunk = []
    counter = 1
    with open(file, 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            if len(hunk) >= size:
                # print('asd')
                yield counter, hunk
                hunk.pop(0)
            hunk.append(line.replace('\n',''))
            counter += 1
            line = f.readline()

def read_file_in_hunks2(file, size):
    hunk = []
    counter = 1
    with open(file, 'rb') as f:
        line = f.readline()
        while line:
            if len(hunk) >= size:
                # print('asd')
                yield counter, hunk
                hunk.pop(0)
            hunk.append(line.replace(b'\n',b'').replace(b'\r',b'').decode())
            counter += 1
            line = f.readline()

def investigate_similarity(hunk, code):
    similar = True
    for i, line in enumerate(hunk):
        
        line = line.replace('\n','')
        c = code[i]


        if line in c:
            print('NEM', line)
            print("-  ", c)
            similar = False
            # return False
        else:
            print('HASONLO', line)
            print("-  ", c)
    return similar #True

def search_hunk_in_file(file, code):
    size = len(code)
    end = None
    start = None
    for counter, hunk in read_file_in_hunks2(file, size):
        # print('==============================================================')
        # for i, l in enumerate(hunk):
        #    print("h", repr(l))
        #     print("c", repr(code[i]))
        # print('==============================================================')
        if hunk == code:
            # print('yay')
            return (counter - size, counter, hunk)
    if end is None and start is None:
        if '404: Not Found' in create_file_string(file):
            return 404
        else:
            return 909
    return (None, None, None)

def create_original_file(modified_file, original_file, patch):
    for hunk in patch.hunks:
        
        start, end, hunk = search_hunk_in_file(modified_file, hunk.modified_code)

        # new original file
        og = open(original_file, 'a')

        counter = 1
        write_once = True
        with open(modified_file, 'r') as mf:
            line = mf.readline()
            while line:
                if counter < start or counter >= end:
                    og.write(line)
                elif write_once is True:
                    # og.write("--------------------------------------------------------------------\n")
                    for original_line in hunk.original_code:               
                        og.write(original_line + '\n')
                    # og.write("--------------------------------------------------------------------\n")
                    write_once = False
                counter += 1
                line = mf.readline()
        og.close()

def create_file_string(path):
    og_patch = ''
    with open(path, 'rb') as f: # encoding='utf-8'
        line = f.readline()
        while line:
            # print(line.replace(b'\r', b''))
            og_patch += line.replace(b'\r', b'').decode()
            line = f.readline()
    return og_patch