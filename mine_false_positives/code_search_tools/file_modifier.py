import os
import datetime

from code_search_tools.generic import remove_non_ascii
from code_search_tools import get_file_len, create_row_dict, report


class Modifier:

    def __init__(self, original_files_folder, modified_files_folder,
                 downloaded_csv, modification_csv, download_keys):

        # Folders:
        self.original_files_folder = original_files_folder
        self.modified_files_folder = modified_files_folder

        # Csv files:
        self.downloaded_csv = downloaded_csv
        self.modification_csv = modification_csv

        self.num_lines = get_file_len(self.downloaded_csv)
        self.download_keys = download_keys

    def modify(self):
        start = datetime.datetime.now()

        with open(self.modification_csv, 'a') as mod_csv:
            with open(self.downloaded_csv, 'r') as df:
                for line in df:
                    info = create_row_dict(line, self.download_keys)

                    path = info['original_file_path'].split(self.original_files_folder)[1]
                    mp = f'{self.modified_files_folder}{path}'

                    if not os.path.exists(info['original_file_path']):
                        continue

                    with open(info['original_file_path'], 'r', encoding="utf8") as of:
                        with open(mp, 'a', encoding="utf8") as mf:
                            original_line = of.readline()
                            line_number = 0
                            on_lines = []

                            while original_line:

                                if 'NOSONAR' in original_line:
                                    # s0 = original_line
                                    splitted_line = original_line.rsplit('//', 1)
                                    original_line = splitted_line[0].strip() + '\n'
                                    flag = splitted_line[1:]
                                    # print(s0, '\n', s1, '\n', flag)
                                    # print()
                                    on_lines.append(line_number)

                                line_number += 1
                                mf.write(original_line)
                                original_line = of.readline()

                    mods = '-'.join(map(str, on_lines))

                    flag = remove_non_ascii(''.join(map(str, flag)))
                    for x in ['\n', '\r', '\t', ',']:
                        flag = flag.replace(x, '')

                    info['modified_file'] = mp
                    info['mods'] = mods
                    info['flag'] = flag

                    row = ','.join([str(v) for v in info.values()]) + '\n'
                    mod_csv.write(row)

                    report(start, int(info['id']), self.num_lines, 10)
