from tp_utils import delete_file, file_len, file_line_by_line, write_line_nl
from tp_utils import csr2dict, dict2csr
from tp_utils import search_patterns


class FilterCommits:

    def __init__(self, commits_csv, commits_filtered_csv, commit_keys, commit_filtered_keys, filtering_patterns):

        self.commits_csv = commits_csv
        self.commits_filtered_csv = commits_filtered_csv

        self.commit_keys = commit_keys
        self.commit_filtered_keys = commit_filtered_keys

        self.filtering_patterns = filtering_patterns

        self.stat = {}
        self._cnt_pr_squids = 0
        self._cnt_c_squids = 0
        self._cnt_both = 0
        self.total = file_len(self.commits_csv)
        self.counter = 0

        print(f'{self.commits_csv} will be filtered for squids.')
        print(f'The result will be saved to {self.commits_filtered_csv}.')

    def reset(self):
        """
        Delete commits filtered csv.
        """
        delete_file(self.commits_filtered_csv)

    @staticmethod
    def _get_squid_list(squids):
        """
        Check squid findings.
        :param squids: squid findings from pull requests and commits, e.g. squid%3AS1188-squid:LeftCurlyBracesCheck
        :param: list os str, empty if no squids are found to this point.
        """
        if squids.strip() is not '-' and squids.strip() is not '':
            return list({squid.strip() for squid in squids.split('-') if squid != ''})
        else:
            return []

    def _get_squids(self, pr_squids, c_msg):
        """
        :param pr_squids: str, squid findings from pull requests, e.g. squid%3AS1188-squid:LeftCurlyBracesCheck
        :param c_msg: str, text obtained from commit
        :return: str, `-` concatenated list of squids
        """
        squids = pr_squids
        
        from_pr = False
        from_c = False

        squids_from_msg = search_patterns(self.filtering_patterns, c_msg)
        squids += '-' + squids_from_msg

        if pr_squids.strip() is not '':
            from_pr = True

        if len(squids_from_msg) > 0:
            from_c = True

        if from_pr:
            self._cnt_pr_squids += 1
        if from_c:
            self._cnt_c_squids += 1
        if from_pr and from_c:
            self._cnt_both += 1

        return squids

    def _filter_commits(self):
        actual_commit = 0

        for line in file_line_by_line(self.commits_csv):
            actual_commit += 1
            line_dict = csr2dict(line, self.commit_keys)

            squids = self._get_squids(line_dict['pr_squids'], line_dict['c_msg'])
            squids = self._get_squid_list(squids)

            if len(squids) > 0:

                squids = '-'.join(map(str, squids))

                new_line_list = [self.counter,
                                 line_dict['pid'],
                                 line_dict['c_id'],
                                 line_dict['c_oid'],
                                 line_dict['c_repo'],
                                 squids]
                write_line_nl(self.commits_filtered_csv, new_line_list)
                self.counter += 1

        print(f'\r{actual_commit}/{self.total}', end='')

        self.stat = {
            'Squids from pr    ': self._cnt_pr_squids,
            'Squids from c     ': self._cnt_c_squids,
            'Squids from both  ': self._cnt_both
        }
        print('\nStats:')
        for k, v in self.stat.items():
            print(f'{k} - {v}')

    def execute(self, reset=True):
        if reset:
            self.reset()
        self._filter_commits()
