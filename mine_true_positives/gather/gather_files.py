import time
import requests
from github import Github

from repo_tools import wait

from tp_utils import delete_folder_files, delete_file, file_line_by_line
from tp_utils import file_len
from tp_utils import csr2dict, write_line_dict_nl
from tp_utils import replace_windows_reserved_chars, skip_non_utf8


class GatherFiles:

    def __init__(self, user, password,
                 commits_filtered_csv, commit_filtered_keys,
                 files_csv, file_keys,
                 patch_folder, current_files_folder, prev_files_folder,
                 file_type='java', sec=0.72):

        # Folders:
        self.current_files_folder = current_files_folder
        self.prev_files_folder = prev_files_folder
        self.patch_folder = patch_folder

        # Csv files:
        self.commits_filtered_csv = commits_filtered_csv
        self.files_csv = files_csv

        # Keys:
        self.commit_filtered_keys = commit_filtered_keys
        self.file_keys = file_keys

        self.u = user
        self.p = password
        self.file_type = file_type
        self.sec = sec
        self.total = file_len(self.commits_filtered_csv)
        self.commit_counter = 1

        self.g = self._init_g()
        print(f'Patches folder: {self.patch_folder}\nResults will be saved to: {self.files_csv}')

    def _init_g(self):
        return Github(self.u, self.p, timeout=120)

    def reset(self):
        delete_folder_files(self.patch_folder)
        delete_folder_files(self.prev_files_folder)
        delete_folder_files(self.current_files_folder)
        delete_file(self.files_csv)

    def _check_url(self, url):
        first_line = self._get_first_line_for(url)
        if first_line is None:
            print('Parent error.')
            return False
        if '404: Not Found' in first_line:
            return False
        return True

    def _get_first_line_for(self, url):
        try:
            wait(self.g)
            r = requests.get(url)
            first_line = ''
            for c in r.text:
                if c is not '\n':
                    first_line += c
                else:
                    break
        except Exception as e:
            print('first_line error: ', e)
            first_line = None
        return first_line

    def _get_prev_url(self, repo, commit, path):
        for parent in commit.parents:
            wait(self.g)
            url = 'https://raw.githubusercontent.com/' + repo + '/' + parent.sha + '/' + path
            if self._check_url(url):
                return True, url, parent.sha
        return False, None, None

    @staticmethod
    def _save_patch(patch_name, folder, patch_content):
        path = f'{folder}/{patch_name}'
        patch_file = open(path, 'a', encoding='utf-8')
        for line in patch_content.split('\n'):
            patch_file.write(line + '\n')
        patch_file.close()
        return path

    @staticmethod
    def _download_file_with_request(file_name, folder, url):
        success = False
        loc = ''
        while not success:
            try:
                r = requests.get(url)
                content = r.content.decode('utf-8', 'ignore')
                loc = f'{folder}/{file_name}'
                with open(loc, 'w', encoding='utf-8') as f:
                    for line in content:
                        f.write(line)
                success = True
            except requests.exceptions.ConnectionError:
                print(f'requests.exceptions.ConnectionError: HTTPSConnectionPool(host=raw.githubusercontent.com, '
                      f'port=443): Max retries exceeded with url: {url}'
                      f'(Caused by NewConnectionError(<urllib3.connection.VerifiedHTTPSConnection object at'
                      f' 0x000001FD59988080>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed)')
                print('Sleep.. 1 min')
                time.sleep(60)
                print('Resume')
        return loc

    def _save_selected_files(self, file_name, patch_name, patch_content, prev_url, current_url):

        p_loc = self._save_patch(patch_name, self.patch_folder, patch_content)
        pf_loc = self._download_file_with_request(file_name, self.prev_files_folder, prev_url)
        cf_loc = self._download_file_with_request(file_name, self.current_files_folder, current_url)
        print(p_loc, pf_loc, cf_loc)
        return p_loc, pf_loc, cf_loc

    def _valid_file_name(self, name, repository, sha):
        """
        Creates a valid file name.

        :param name: str,
        :param repository: str,
        :param sha: str,
        :return: str, file name
        """
        name = name.split('/').pop()
        name = replace_windows_reserved_chars(skip_non_utf8(name))

        repo_name = repository.replace('/', '__')

        file_name = f'{self.counter}_{repo_name}_{sha}_{name}'
        patch_name = f'{self.counter}_{repo_name}_{sha}_{name}_patch.txt'

        return file_name, patch_name

    def _search_and_save_files(self, commit, data):
        repo = data['repo']
        pid = data['pid']
        c_id = data['c_id']
        c_oid = data['c_oid']
        possible_squids = data['possible_squids']

        for file in commit.files:

            wait(self.g)
            name = file.filename
            if not name.endswith(self.file_type):    
                continue

            wait(self.g)
            patch_content = file.patch
            if patch_content is None:
                # probably the file was just uploaded, we are looking for changed files.
                continue
            
            wait(self.g)
            current_url = file.raw_url
            current_sha = file.sha

            ok, prev_url, prev_sha = self._get_prev_url(repo, commit, name)
            if not ok:
                continue

            valid_file_name, valid_patch_name = self._valid_file_name(name, repo, current_sha)

            p_loc, pf_loc, cf_loc = self._save_selected_files(valid_file_name, valid_patch_name,
                                                              patch_content,
                                                              prev_url, current_url)
            new_line = {
                'id': self.counter,
                'pid': pid,
                'c_id': c_id,
                'c_oid': c_oid,
                'repo': repo,
                'possible_squids': possible_squids,
                'current_sha': current_sha,
                'prev_sha': prev_sha,
                'current_url': current_url,
                'prev_url': prev_url,
                'patch_location': p_loc,
                'prev_file_location': pf_loc,
                'current_file_location': cf_loc}

            write_line_dict_nl(self.files_csv, new_line, self.file_keys)
            self.counter += 1

    def _get_commit_obj(self, repository, commit_id, commit_counter):
        """
        :param repository: str, repository of the searched commit
        :param commit_id: str, ordinary api v3 id of the commit
        :param commit_counter: int, line number in filtered commits csv
        :return: github commit object
        """
        successful = False
        single_commit = None

        while not successful:
            try:
                time.sleep(self.sec)
                wait(self.g)
                repo = self.g.get_repo(repository)
                single_commit = repo.get_commit(commit_id)
                successful = True
            except Exception as e:
                print('Triggered. 10 mins sleep.', e, 'commit counter: ', commit_counter)
                time.sleep(600)
                self.g = self._init_g()
        return single_commit
    
    def _get_files(self):
        self.counter = 1

        for line in file_line_by_line(self.commits_filtered_csv):
            print(self.counter, line)
            data = csr2dict(line, self.commit_filtered_keys)

            single_commit = self._get_commit_obj(data['repo'],
                                                 data['c_oid'],
                                                 self.commit_counter)

            self._search_and_save_files(single_commit, data)
            self.commit_counter += 1

    def execute(self, reset=True):
        if reset:
            self.reset()
        self._get_files()
