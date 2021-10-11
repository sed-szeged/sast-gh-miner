import os
from datetime import datetime

from tp_utils.csv import csr2dict
from tp_utils.csv import dict2csr


from tp_utils.file import file_len
from tp_utils.file import file_line_by_line

from tp_utils.patch_tools import get_hunks
from tp_utils.patch_tools import search_hunk_in_file


class FilePatchLocator:

    def __init__(self, csv_files, csv_result, file_keys, result_keys, file_type='.java'):

        self._init_counters()

        self.file_type = file_type
        self.csv_files_path = csv_files
        self.csv_result_path = csv_result
        self._num_of_rows = file_len(self.csv_files_path)

        self.csv_files_keys = file_keys
        self.csv_result_keys = result_keys

        self._start = None
        self._end = None
        print(f'Results will be stored in: {self.csv_result_path}')

    def _init_counters(self):
        self._cnt_404 = 0               # parent not found
        self._cnt_909 = 0               # unknown mistakes e.g. in patch "\ no new line at the end" /139_SonarSource
        self._cnt_found = 0             # successfully found hunk
        self._cnt_all = 0               # every hunk
        self._cnt_not_java = 0          # not java file
        self._cnt_rows_in_file = 0      # all rows in db

    def reset(self):
        """
        Deletes the result csv file.
        """
        if os.path.isfile(self.csv_result_path):
            os.remove(self.csv_result_path)

    def execute(self, reset=True):
        if reset:
            self.reset()

        self._start = datetime.now()
        print(f'Start time: {self._start}')
        self._find_locations()
        self._end = datetime.now()
        print(f'End time: {self._end}')
        print(f'Duration: {self._end - self._start}')

        print('Searching for patch locations is finished.\n')
        return self
    
    def _find_locations(self):
        for row in file_line_by_line(self.csv_files_path):
            row_dict = csr2dict(row, self.csv_files_keys)

            if not row_dict['prev_file_location'].endswith(self.file_type):
                self._cnt_not_java += 1
                print(self._cnt_not_java, row_dict['prev_file_location'], self.file_type)
                continue
                
            for hunk in get_hunks(row_dict['patch_location']):
                self._cnt_all += 1
                res = (None, None, None)
                try:
                    res = search_hunk_in_file(row_dict['prev_file_location'], hunk.original_code)
                except Exception as e:
                    print('Hunk search: ', e)
                    
                if res == 404:
                    # something went wrong while downloading
                    # multiple things can happen e.g. file or repository ceased to exist
                    self._cnt_404 += 1
                    continue
                    
                if res == 909:
                    # something wild
                    self._cnt_909 += 1
                    continue
                
                # hunky is good
                start, end, _ = res                    
                if start is not None and end is not None:
                    new_row_dict = row_dict.copy()
                    new_row_dict['id'] = self._cnt_found
                    new_row_dict['patch_start_row'] = start
                    new_row_dict['patch_end_row'] = end

                    with open(self.csv_result_path, 'a', encoding='utf-8') as f:
                        f.write(dict2csr(new_row_dict, self.csv_result_keys))

                    self._cnt_found += 1
                else:
                    print('Hnf!')

            print(f'\r{self._cnt_rows_in_file}/{self._num_of_rows}', end='')
            self._cnt_rows_in_file += 1
        
        self.result = f'''
Rows in file   : {self._cnt_rows_in_file},
All hunks      : {self._cnt_all},
Found hunks    : {self._cnt_found},
Parent missing : {self._cnt_404},
Not java file  : {self._cnt_not_java},
Other error    : {self._cnt_909}
'''
        print(self.result)
