import datetime
import requests

from code_search_tools import get_file_len, create_row_dict, report


class Downloader:
    def __init__(self, original_files_folder, github_search_result, downloaded_csv, github_file_keys):
        # Folders:
        self.original_files_folder = original_files_folder

        # Csv files:
        self.github_search_result = github_search_result
        self.downloaded_csv = downloaded_csv

        self.github_file_keys = github_file_keys

    def download_files(self):
        """
        Main file downloader method.
        Downloads files form csv.

        :return: None
        """
        total = get_file_len(self.github_search_result)
        start = datetime.datetime.now()

        with open(self.downloaded_csv, 'a') as df:
            with open(self.github_search_result, 'r') as urls:
                for line in urls:
                    info = create_row_dict(line, self.github_file_keys)

                    file_name = f'{info["id"]}_{info["sha"]}_{info["name"]}'

                    if not file_name.endswith('.java'):
                        continue

                    info['file_name'] = f'{self.original_files_folder}/{file_name}'

                    self._download_file(info['file_name'], info["download_url"])

                    row = ','.join([str(v) for v in info.values()]) + '\n'
                    df.write(row)

                    report(start, int(info['id']), total, 10)

    def _download_file(self, file_name: str, url: str):
        """
        :param file_name: str
        :param url: str
        :return: None
        """
        try:
            self._download_file_with_request(file_name, url)
        except Exception as e:
            print('Error at _download_file: ', e, file_name)

    @staticmethod
    def _download_file_with_request(file_path: str, url: str):
        """
        Download file using request library.
        :param file_path: str
        :param url: str
        :return: None
        """
        r = requests.get(url)
        try:
            content = r.content.decode('utf-8', 'ignore').split('\n')
        except UnicodeDecodeError as e:
            print(e, '\nUnicode decode error at\n', file_path, url)
            content = r.text.split('\n')
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in content:
                f.write(line + '\n')
