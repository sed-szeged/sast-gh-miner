from deprecated import deprecated
import datetime
import os

from code_search_tools.generic import check_file
from code_search_tools import GithubCodeSearchBySize
from code_search_tools import GithubCodeSearchByYear, Downloader, Modifier
from check_files import JavaFileChecker

from fp_utils import KeyHolder


class GatherNosonarFiles:

    def __init__(self, u: str, p: str, word: str, lang='java', run_time=(None, None, None)):
        """
        Creates necessary folders and variables.

        :param u: github user
        :param p: github pass
        :param word: str, searched word
        :param lang: str, searched language
        :return: None
        """

        # Folders:
        self.main_folder = None
        self.csv_folder = None
        self.original_files_folder = None
        self.modified_files_folder = None

        # Csv files
        self.github_search_result = None
        self.downloaded_csv = None
        self.modification_csv = None
        self.good_files_csv = None
        self.bad_files_csv = None

        # Lists
        self.good_files_list = None
        self.bad_files_list = None

        # Dictionaries
        self.projects_and_chunks = None

        # Inputs
        self.u = u
        self.p = p
        self.word = word
        self.lang = lang

        # ezt valahogy mashogy kellene
        if all(run_time):
            self.date = datetime.date(*run_time)
        else:
            self.date = datetime.datetime.now()

        # Setup:
        self._create_folders()
        self._create_csv_paths()
        self.counter = 0

        print('Setup finished:')
        print('Folders: ')
        print(f'csv files                - > {self.csv_folder}')
        print(f'downloaded files         - > {self.original_files_folder}')
        print(f'modified files           - > {self.modified_files_folder}')
        print('Csv files:')
        print(f'github search result csv - > {self.github_search_result}')
        print(f'downloaded files csv     - > {self.downloaded_csv}')
        print(f'modified files csv       - > {self.modification_csv}')
        print(f'good files csv           - > {self.good_files_csv}')
        print(f'bad files csv            - > {self.bad_files_csv}')

        # Keys setup:
        self.keys = KeyHolder()
        self.github_file_keys = self.keys.get_github_file_keys()
        self.code_search_keys = self.keys.get_code_search_keys()
        self.download_keys = self.keys.get_download_keys()
        self.modified_keys = self.keys.get_modified_keys()

    def _create_folders(self):
        results_folder = 'results'
        if not os.path.exists(results_folder):
            os.mkdir(results_folder)

        for x in '~!@#$%^&*()_+/.,;\\][+-*/ ':
            self.word = self.word.replace(x, '')
        date_part = f'{self.date.year}_{self.date.month}_{self.date.day}'
        self.main_folder = f'{results_folder}/{date_part}_{self.word}_{self.lang}'

        if not os.path.exists(self.main_folder):
            os.mkdir(self.main_folder)

        self.csv_folder = f'{self.main_folder}/csv'
        if not os.path.exists(self.csv_folder):
            os.mkdir(self.csv_folder)

        self.original_files_folder = f'{self.main_folder}/original_files'
        if not os.path.exists(self.original_files_folder):
            os.mkdir(self.original_files_folder)

        self.modified_files_folder = f'{self.main_folder}/modified_files'
        if not os.path.exists(self.modified_files_folder):
            os.mkdir(self.modified_files_folder)

        self.squid_folder = f'{self.main_folder}/squids'
        if not os.path.exists(self.squid_folder):
            os.mkdir(self.squid_folder)

        self.binaries_folder = f'binaries'
        if not os.path.exists(self.binaries_folder):
            os.mkdir(self.binaries_folder)

    def _create_csv_paths(self):
        self.github_search_result = f'{self.csv_folder}/github_search_result.csv'
        self.downloaded_csv = f'{self.csv_folder}/downloaded_files.csv'
        self.modification_csv = f'{self.csv_folder}/modified_files.csv'
        self.good_files_csv = f'{self.csv_folder}/good_files.csv'
        self.bad_files_csv = f'{self.csv_folder}/bad_files.csv'

    def _reset_github_search_result_file(self):
        """
        If the urls containing file already exists delete it.

        :return: None
        """
        if check_file(self.github_search_result):
            os.remove(self.github_search_result)

    def _reset_downloaded_files(self):
        """
        Delete all files in specified folder and the downloaded csv.

        :return: None
        """
        for file in os.listdir(self.original_files_folder):
            os.remove(os.path.join(self.original_files_folder + file))
        if check_file(self.downloaded_csv):
            os.remove(self.downloaded_csv)

    def _reset_modification_csv(self):
        if check_file(self.modification_csv):
            os.remove(self.modification_csv)

    def _reset_good_files_csv(self):
        if check_file(self.good_files_csv):
            os.remove(self.good_files_csv)

    def _reset_bad_files_csv(self):
        if check_file(self.bad_files_csv):
            os.remove(self.bad_files_csv)

    def _reset_modified_files(self):
        """
        Delete all modified files and modification csv.

        :return: None
        """
        for file in os.listdir(self.modified_files_folder):
            os.remove(f'{self.modified_files_folder}/{file}')

    @deprecated(version='0.0.1', reason="unclear results, overlapping")
    def code_year_search(self, start_year=2010, end_year=2019):
        print('Code search..\n')
        # reset previous file
        years = [x for x in range(start_year, end_year + 1)]
        print(years)
        self._reset_github_search_result_file()
        github_search = GithubCodeSearchByYear(self.u, self.p, self.word, self.lang,
                                               years, self.github_search_result, self.github_file_keys)
        github_search.run_github_search()

    def code_size_search(self, file_sizes=None):
        """
        Main step 1.
        Search code by file size.

        :param file_sizes: None or list (format: ['size:0..500'], ['size:10000..10250', 'size:10250..10500', ...])
        :return: None
        """
        print('Code search..\n')
        self._reset_github_search_result_file()
        github_search = GithubCodeSearchBySize(self.u, self.p, self.word, self.lang,
                                               self.github_search_result, self.github_file_keys)
        if file_sizes is None:
            file_sizes = github_search.get_sizes()
        print(file_sizes)
        github_search.run_github_search(file_sizes)

    def download_files(self):
        """
        Main step 2.
        :return: None
        """
        print('Download files..\n')
        self._reset_downloaded_files()
        downloader = Downloader(self.original_files_folder, self.github_search_result,
                                self.downloaded_csv, self.code_search_keys)
        downloader.download_files()

    def modify_files(self):
        print('Modify files..\n')
        self._reset_modification_csv()
        self._reset_modified_files()
        modifier = Modifier(self.original_files_folder, self.modified_files_folder,
                            self.downloaded_csv, self.modification_csv, self.download_keys)
        modifier.modify()

    def check_java_files(self):
        print('Checking files for parsing errors...')
        checker = JavaFileChecker(self.modified_files_folder, self.good_files_csv, self.bad_files_csv)
        checker.check_files()
        self.load_good_files_list()

    def load_good_files_list(self):
        with open(self.good_files_csv, 'r', encoding='utf-8') as f:
            _list = f.read().split(',')
        print('good_files_list size: ', len(_list))
        self.good_files_list = _list

    def create_project_names_and_good_files_chunks(self, project_base='project_date', size=1000):
        total = len(self.good_files_list)
        chunks = [[i, i+size] for i in range(0, total, size)]
        project_to_chunk = {}
        for i, chunk in enumerate(chunks):
            project_to_chunk[f'{project_base}_chunk_{i}'] = chunk
        self.projects_and_chunks = project_to_chunk
        return self.projects_and_chunks
