import os

import pandas as pd
from sonar_qube_api.api import SonarQube
from tp_utils import KeyHolder
import datetime


class ProjectScanner:

    def __init__(self, token: str,  projects_and_chunks: dict,
                 patch_checked_csv: str,
                 patch_located_keys: list, result_keys: list,
                 good_files_csv_path: str, result_folder: str,
                 result_file_base_name='squids_date'):

        self.token = token


        self.patch_located_keys = patch_located_keys
        self.result_info_keys = result_keys

        self.result_df = self._init_result_df()

        self.patch_checked_df = pd.read_csv(patch_checked_csv, names=self.patch_located_keys)
        print(self.patch_checked_df.iloc[0])

        self.good_files_csv_path = good_files_csv_path
        self.good_files_list = self._load_good_files_list(self.good_files_csv_path)
        self.projects_and_chunks = projects_and_chunks

        self.sonar_qube = SonarQube(self.token, port=9000)
        self.result_file_name = result_file_base_name

        self.result_folder = os.path.join(result_folder, self.result_file_name)
        if not os.path.isdir(self.result_folder):
            os.mkdir(self.result_folder)

    def _init_result_df(self):
        return pd.DataFrame(columns=self.result_info_keys)

    def _sonar_issue_search(self, component, p=1):
        args = {
            'componentKeys': component,
            'type': 'CODE_SMELL,BUG,VULNERABILITY,SECURITY_HOTSPOT',
            'p': p
        }
        return self.sonar_qube.api_issues_search(verbose=False, **args)

    @staticmethod
    def _load_good_files_list(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().split(',')

    @staticmethod
    def _get_number_of_total_pages(num_of_issues):
        return round(num_of_issues / 500) + 1

    @staticmethod
    def _concatenate_file_and_project(project, file):
        return f'{project}:{file}'

    @staticmethod
    def _concatenate_dataframes(parts):
        dfs = []
        for part in parts:
            dfs.append(pd.read_csv(part))
        return pd.concat(dfs)

    def search_projects_issues(self):
        start = datetime.datetime.now()
        print('Start: ', start)
        zero_issues_counter = 0
        not_zero_issues_counter = 0

        parts = []
        for chunk_index, chunk in enumerate(self.projects_and_chunks.items()):
            key, borders = chunk
            # key = key + '_Key'
            self.result_df = self._init_result_df()
            print(f'Searching in {key} - that corresponds to files: {borders}')

            chunk = self.good_files_list[borders[0]:borders[1]]
            for i, row in self.patch_checked_df[self.patch_checked_df['prev_file_location'].isin(chunk)].iterrows():

                component_key = self._concatenate_file_and_project(key, row['prev_file_location'])
                save_row = row.to_dict()
                # print(component_key)
                issues = self._sonar_issue_search(component_key)

                print('search component key', component_key)
                total_number_of_issues = issues['total']

                if total_number_of_issues == 0:
                    zero_issues_counter += 1
                else:
                    not_zero_issues_counter += 1

                number_of_pages = self._get_number_of_total_pages(total_number_of_issues)

                p = 1
                while p <= number_of_pages + 1:
                    issues = self._sonar_issue_search(component_key, p=p)

                    if not issues.get('issues', False):  # added later
                        p += 1
                        continue

                    for issue in issues['issues']:

                        squids = row['possible_squids'].split('-')
                        squids = list(set([squid.replace('%3A', ':') if '%3A' in squid else squid for squid in squids]))
                        # print(squids)

                        rule = issue.get('rule', '')

                        if rule not in squids:
                            pass
                            # print(rule, squids)
                        else:

                            if issue.get('textRange', False):
                                tr = issue['textRange']

                                sl = tr['startLine']
                                el = tr['endLine']
                                so = tr['startOffset']
                                eo = tr['endOffset']

                                if row['patch_start_row'] <= sl <= row['patch_end_row']:

                                    severity = issue.get('severity', '')
                                    message = issue.get('message', '')

                                    save_row['startLine'] = sl
                                    save_row['endLine'] = el
                                    save_row['startOffset'] = so
                                    save_row['endOffset'] = eo
                                    save_row['rule'] = rule
                                    save_row['severity'] = severity
                                    save_row['message'] = message

                                    self.result_df = self.result_df.append(save_row, ignore_index=True)
                                    # print(len(self.result_df.columns))

                    p += 1
            # print(self.result_info_keys)
            # print(self.result_df.columns)
            self.result_df.columns = self.result_info_keys
            self.result_df.to_csv(f'{self.result_folder}/{self.result_file_name}_chunk_{chunk_index}.csv', index=False)
            parts.append(f'{self.result_folder}/{self.result_file_name}_chunk_{chunk_index}.csv')

        result_df = self._concatenate_dataframes(parts)
        result_df.columns = self.result_info_keys
        result_df.to_csv(f'{self.result_folder}/{self.result_file_name}_complete.csv', index=False)
        end = datetime.datetime.now()
        print('End: ', end)
        print('Duration: ', end-start)
        print('Finished.')


if __name__ == '__main__':

    args = {
        'componentKeys': '0827_chunk_5_Key_Key:results/2020_8_27_sonar_java/prev_files/9999_darcy-framework__darcy-webdriver_4d9ba45e31c668c270e1345e76a01b6abf5d92c6_ByAttribute.java',
        'type': 'CODE_SMELL,BUG,VULNERABILITY,SECURITY_HOTSPOT',
        'p': 1
    }
    sonar_token = ""
    sq = SonarQube(sonar_token, port=9000)
    response = sq.api_issues_search(verbose=True, **args)
    print(response)
