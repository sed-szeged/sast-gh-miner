import re
import time
import subprocess
from subprocess import PIPE
from fp_utils import list2csr
from datetime import datetime


class SonarScanner:

    def __init__(self, token: str, project_name: str, lang: str, files_list: list):
        """
        Sonar Scanner class. Main usage is to scan a single project with specified files.

        :param token: str, SonarQube token
        :param project_name: str, arbitrary name of your project
        :param lang: str, programming language
        :param files_list: list, will be added to sonar-scanner.properties inclusions list.
        """
        self.sonar_token = token

        # for properties file:
        self.project_name = project_name
        self.project_key = project_name + '_Key'
        self.files_list = files_list
        self.lang = lang

        # logging
        date = datetime.now()
        date = f'Y{date.year}_M{date.month}_D{date.day}_H{date.hour}_M{date.minute}'
        self.log_path = f'log/sonar_scanner_{date}_log.txt'
        self._log(f'\n\nStart time: {date}\n')

    def _log(self, text: str):
        """
        Basic logging.

        :param text: str, text, that will be logged.
        :return: None
        """
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(text)

    def run_scan(self) -> bool:
        """
        Main method that should be used.

        :return: None
        """
        print(f'\n{25*"-"}\nProject: {self.project_name}')
        print(f'Creating sonar properties file for {len(self.files_list)} files')
        self._create_sonar_scanner_properties_file()
        print('Scanning..')
        info, res = self._scan()
        if res:
            log = 'Execution successful'
            self._log(f'{25*"-"}\n{self.project_name}, {log}')
        else:
            log = 'Execution failure'
            self._log(f'{25*"-"}\n{self.project_name}, {log}, \n{info}')
        print(log)
        return res

    @staticmethod
    def _scan():
        """
        Run sonar-scanner using subprocess.
        :return: tuple - (str, bool) - str: process output, bool: execution result.
        """
        # python 3.7+
        # out = subprocess.run([f"sonar-scanner"], capture_output=True, shell=True)

        # python 3.6 stdout and stderr to emulate capture_output
        out = subprocess.run([f"sonar-scanner"], stdout=PIPE, stderr=PIPE, shell=True)

        m = re.findall('(?<=EXECUTION )(.*?)(?=INFO)', str(out))
        execution = m[0][:-4]
        execution = 'EXECUTION ' + execution + ''
        if 'EXECUTION SUCCESS' in execution:
            return out, True
        return out, False

    def _create_sonar_scanner_properties_file(self):
        """
        For every sonar scan a new properties files will be created, the reason is that new files should be included
        in the sonar.inclusions.
        :return:
        """
        p_k = 'sonar.projectKey=' + self.project_key + '\n'
        p_n = 'sonar.projectName=' + self.project_name + '\n'
        s_e = 'sonar.sourceEncoding=UTF-8\n'
        s_i = 'sonar.inclusions=' + list2csr(self.files_list) + '\n'
        s_b = 'sonar.java.binaries=binaries/\n'
        s_l = 'sonar.language=' + self._get_language() + '\n'
        properties = open(f'sonar-project.properties', 'w')
        properties.writelines([p_k, p_n, s_e, s_i, s_b, s_l])
        properties.close()

    def _get_language(self):
        """
        The sonar qube might use a different language notation than github. java=java, javascript=js
        :return:
        """
        if self.lang == 'java':
            return 'java'
        if self.lang == 'javascript':
            return 'js'


class MultiSonarScanner:

    def __init__(self, token: str, projects_and_chunks: dict, lang: str, good_files_csv: str):
        self.lang = lang
        self.token = token
        self.projects = projects_and_chunks
        self.good_files_csv = good_files_csv
        self.good_files_list = self._load_good_files_list(good_files_csv)

    @staticmethod
    def _load_good_files_list(path):
        with open(path, 'r', encoding='utf-8') as f:
            _list = f.read().split(',')
        print('good_files_list size: ', len(_list))
        return _list

    def bulk_sonar_scan(self) -> dict:
        """
        Loop through projects and scan each of them.

        :return:
        """
        # lehet hogy erdemes lenne itt megnezni hogy az elozo project befejezte e az analizist, de az lehet hosszu lenne
        print('Sonar scan..')
        project_keys = {}
        for project, borders in self.projects.items():
            files = self.good_files_list[borders[0]:borders[1]]
            scanner = SonarScanner(token=self.token, project_name=project, lang=self.lang, files_list=files)
            res = scanner.run_scan()
            time.sleep(30)
            if res:
                project_keys[scanner.project_key] = borders
        return project_keys
