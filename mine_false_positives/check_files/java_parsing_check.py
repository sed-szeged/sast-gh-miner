import os
import javalang


class JavaFileChecker:

    def __init__(self, modified_files_path, good_files_path, bad_files_path):
        self.folder = modified_files_path
        self.good_files_path = good_files_path
        self.bad_files_path = bad_files_path
        self.good_files_list = []
        self.bad_files_list = []

    @staticmethod
    def get_file_content(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _write_to_file(path, content):
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print('Error occurred while writing files list to file:', e)

    @staticmethod
    def _list_to_str(files):
        return ','.join(files)

    def _parsing_check(self):
        """
        Skipping files with parsing error. Parser: original javalang
        :return:
        """

        files = [self.folder + '/' + file for file in os.listdir(self.folder)]
        total = len(files)

        for i, file in enumerate(files):
            print(f'\r{i}/{total}', end='')

            if file.endswith('.java'):
                try:
                    lines = (self.get_file_content(file))
                    tokens = javalang.tokenizer.tokenize(lines)
                    parsed = javalang.parser.parse(tokens)
                    for _ in parsed:
                        pass
                    self.good_files_list.append(file)
                except Exception:
                    self.bad_files_list.append(file)

    def check_files(self):
        self._parsing_check()
        print('Files without parsing error: ', len(self.good_files_list))
        print('Files with parsing error:    ', len(self.bad_files_list))
        self._write_to_file(self.good_files_path, self._list_to_str(self.good_files_list))
        self._write_to_file(self.bad_files_path, self._list_to_str(self.bad_files_list))
