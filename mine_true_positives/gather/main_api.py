import datetime

from tp_utils import str_date
from tp_utils import KeyHolder
from tp_utils import create_folder

from gather.gather_files import GatherFiles

from gather.patch_locator import FilePatchLocator

from gather.gather_commits import GatherCommitsFromPullRequests
from gather.filter_commits import FilterCommits

from gather.gather_pull_requests import GatherPullRequests
from gather.filter_pull_requests import FilterPullRequests

from check_files.java_parsing_check import JavaFileChecker


class TruePositiveSquidSearcher:

    def __init__(self, user, password, token, date_ops, searched_word, filtering_patterns,
                 project_name='tp', seconds=0.72, lang='java', file_type='.java', which_files='both',
                 datetimedate=(None, None, None)):
        """
        Gathers squid issues which has been fixed over time.

        :param user: str, github
        :param password: str, github
        :param token: str, github
        :param date_ops: dictionary tat contains start and end year and month
        :param searched_word: specific word to search for. best option for `sonar`
        :param filtering_patterns: regex expressions for the filters
        :param project_name: folder name
        :param seconds: seconds between searches or gets
        :param lang: programming language
        :param file_type: e.g. `.java` for java files
        :param which_files: `both` means previous the changes and after the changes.
        :param datetimedate: tuple, year, month, day used for specification because of weekly search.
        """

        # Init variables
        self.u = user
        self.p = password
        self.github_token = token
        self.date_ops = date_ops
        self.searched_word = searched_word
        self.filtering_patterns = filtering_patterns
        self.project_name = project_name
        self.sec = seconds
        self.lang = lang
        self.file_type = file_type
        self.which_files = which_files
        # Find different approach
        if all(datetimedate):
            self.date = datetime.date(*datetimedate)
        else:
            self.date = datetime.datetime.now()

        # Folders:
        self.main_folder = None
        self.csv_folder = None
        self.prev_files_folder = None
        self.current_files_folder = None
        self.patch_folder = None
        self.squid_folder = None
        self.binaries_folder = None
        self.log = None
        self._create_folders()

        # Csv files:
        self.pr_csv = None
        self.pr_filtered_csv = None
        self.commits_csv = None
        self.commits_filtered_csv = None
        self.files_csv = None
        self.patches_csv = None
        self.patch_checked_csv = None
        self.good_files_csv = None
        self.bad_files_csv = None
        self._create_csv_paths()

        # Keys:
        self.keys = KeyHolder()
        self.pr_keys = self.keys.get_pull_request_keys()
        self.commit_keys = self.keys.get_commit_keys()
        self.commit_filtered_keys = self.keys.get_commit_filtered_keys()
        self.file_keys = self.keys.get_file_keys()
        self.csv_files_keys = self.keys.get_file_keys()
        self.csv_result_keys = self.keys.get_patched_keys()

        self.good_files_list = None
        self.projects_and_chunks = None

        print('Setup finished:')
        print('Folders: ')
        print(f'- csv files       - > {self.csv_folder}')
        print(f'- prev files      - > {self.prev_files_folder}')
        print(f'- current files   - > {self.current_files_folder}')
        print(f'- patches         - > {self.patch_folder}')
        print(f'- squids          - > {self.squid_folder}')
        print(f'- binaries        - > {self.binaries_folder}')

        print('Csv files:')
        print(f'- pull requests          - > {self.pr_csv}')
        print(f'- filtered pull requests - > {self.pr_filtered_csv}')
        print(f'- commits                - > {self.commits_csv}')
        print(f'- filtered commits       - > {self.commits_filtered_csv}')
        print(f'- files                  - > {self.files_csv}')
        print(f'- patches                - > {self.patches_csv}')
        print(f'- patch checked          - > {self.patch_checked_csv}')

    def _save_log(self, txt: str):
        with open(self.log_txt, 'a', encoding='utf-8') as f:
            f.write(txt)

    def _save_log_gpr(self, stat: dict):
        txt = ''
        for k, v in stat.items():
            txt += f'{k} : {v}\n'
        self._save_log(txt)

    def _create_folders(self):
        results_folder = 'results'
        create_folder(results_folder)

        for x in '~!@#$%^&*()_+/.,;\\][+-*/ ':
            self.project_name = self.project_name.replace(x, '')

        date_part = f'{self.date.year}_{self.date.month}_{self.date.day}'
        self.main_folder = f'{results_folder}/{date_part}_{self.searched_word}_{self.lang}'
        create_folder(self.main_folder)

        self.csv_folder = f'{self.main_folder}/csv'
        create_folder(self.csv_folder)

        self.prev_files_folder = f'{self.main_folder}/prev_files'
        create_folder(self.prev_files_folder)

        self.current_files_folder = f'{self.main_folder}/current_files'
        create_folder(self.current_files_folder)

        self.patch_folder = f'{self.main_folder}/patches'
        create_folder(self.patch_folder)

        self.log_folder = f'{self.main_folder}/log'
        create_folder(self.log_folder)

        self.squid_folder = f'{self.main_folder}/squids'
        create_folder(self.squid_folder)

        self.binaries_folder = f'binaries'
        create_folder(self.binaries_folder)

    def _create_csv_paths(self):
        self.pr_csv = f'{self.csv_folder}/pr.csv'
        self.pr_filtered_csv = f'{self.csv_folder}/filtered_pr.csv'
        self.commits_csv = f'{self.csv_folder}/commits.csv'
        self.commits_filtered_csv = f'{self.csv_folder}/filtered_commits.csv'
        self.files_csv = f'{self.csv_folder}/files.csv'
        self.patches_csv = f'{self.csv_folder}/patch_locations.csv'
        self.patch_checked_csv = f'{self.csv_folder}/patch_checked.csv'
        self.good_files_csv = f'{self.csv_folder}/good_files_csv.csv'
        self.bad_files_csv = f'{self.csv_folder}/bad_files_csv.csv'
        self.log_txt = f'{self.log_folder}/log.txt'

    def gather_pull_requests(self, reset=True):
        print('Gathering pull requests...')
        start = datetime.datetime.now()
        self._save_log(str_date(start))
        gpr = GatherPullRequests(github_token=self.github_token,
                                 date_ops=self.date_ops,
                                 specific_word=self.searched_word,
                                 pull_request_csv=self.pr_csv,
                                 keys=self.pr_keys,
                                 sec=self.sec,
                                 lang=self.lang)
        stat = gpr.execute(reset)
        end = datetime.datetime.now()
        self._save_log(str_date(end))
        self._save_log(str_date(end - start))
        self._save_log_gpr(stat)
        print(f'Start time: {start}\nEnd time: {end}')
        print(f'Duration time: {end - start}')
        print('Pull request gathering is finished.\n')
        print('Done')

    def filter_pull_requests(self, reset=True):
        print('Filtering pull requests...')
        fpr = FilterPullRequests(keys=self.pr_keys,
                                 pr_csv=self.pr_csv,
                                 pr_filtered_csv=self.pr_filtered_csv,
                                 patterns=self.filtering_patterns)
        fpr.execute(reset)
        print('Done')

    def gather_commits_from_pr(self, reset=True):
        print('Gathering commits...')
        gc = GatherCommitsFromPullRequests(user=self.u,
                                           password=self.p,
                                           token=self.github_token,
                                           pr_filtered_csv=self.pr_filtered_csv,
                                           commits_csv=self.commits_csv,
                                           pr_keys=self.pr_keys,
                                           commit_keys=self.commit_keys,
                                           sec=self.sec)
        gc.execute(reset)
        print('Done')

    def filter_commits(self, reset=True):
        print('Filtering commits...')
        fc = FilterCommits(commits_csv=self.commits_csv,
                           commits_filtered_csv=self.commits_filtered_csv,
                           commit_keys=self.commit_keys,
                           commit_filtered_keys=self.commit_filtered_keys,
                           filtering_patterns=self.filtering_patterns)
        fc.execute(reset)
        print('Done')

    def gather_files(self, reset=True):
        print('Gathering files')
        gf = GatherFiles(user=self.u,
                         password=self.p,
                         commits_filtered_csv=self.commits_filtered_csv,
                         commit_filtered_keys=self.commit_filtered_keys,
                         files_csv=self.files_csv,
                         file_keys=self.file_keys,
                         patch_folder=self.patch_folder,
                         current_files_folder=self.current_files_folder,
                         prev_files_folder=self.prev_files_folder,
                         file_type=self.file_type,
                         sec=self.sec)
        gf.execute(reset)
        print('Done')

    def search_sonar_locations(self, reset=True):
        print('Gathering files')
        fpl = FilePatchLocator(csv_files=self.files_csv,
                               csv_result=self.patch_checked_csv,
                               file_keys=self.file_keys,
                               result_keys=self.csv_result_keys,
                               file_type=self.file_type)
        fpl.execute(reset)
        print('Done')

    def check_java_files(self, reset=True):
        print('Checking files for parsing errors...')
        checker = JavaFileChecker(files_path=self.prev_files_folder,
                                  good_files_csv=self.good_files_csv,
                                  bad_files_csv=self.bad_files_csv)
        checker.check_files(reset)
        print('Done')

    def load_good_files_list(self):
        with open(self.good_files_csv, 'r', encoding='utf-8') as f:
            _list = f.read().split(',')
        print('good_files_list size: ', len(_list))
        self.good_files_list = _list

    def create_project_names_and_good_files_chunks(self, project_base='project_date', size=1000):
        self.load_good_files_list()
        total = len(self.good_files_list)
        chunks = [[i, i + size] for i in range(0, total, size)]
        project_to_chunk = {}
        for i, chunk in enumerate(chunks):
            project_to_chunk[f'{project_base}_chunk_{i}_Key'] = chunk
        self.projects_and_chunks = project_to_chunk
        return self.projects_and_chunks
