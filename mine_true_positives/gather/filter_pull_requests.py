from tp_utils import csr2dict, dict2csr
from tp_utils import delete_file
from tp_utils import search_patterns


class FilterPullRequests:
    def __init__(self, keys, pr_csv, pr_filtered_csv, patterns):
        """
        :param keys:  list of str, id, pid, txt
        :param pr_csv: str, path to pr csv
        :param pr_filtered_csv: str, path to pr filtered csv
        :param patterns: list of str patterns
        """
        self.keys = keys
        self.pr_csv = pr_csv
        self.pr_filtered_csv = pr_filtered_csv
        self.patterns = patterns

        print(f'{self.pr_csv} will be filtered by patterns: {self.patterns}.')
        print(f'The results will be saved to {self.pr_filtered_csv}.')

    def reset(self):
        """
        Delete filtered pull request file.
        """
        delete_file(self.pr_filtered_csv)

    def _write_squid_file(self):
        with open(self.pr_filtered_csv, 'a', encoding='utf-8') as filtered:
            with open(self.pr_csv, 'r', encoding='utf-8') as pr:
                for line in pr.readlines():
                    data = csr2dict(line, self.keys)
                    data['txt'] = search_patterns(self.patterns, data['txt'])
                    filtered.write(dict2csr(data, self.keys))

    def execute(self, reset=True):
        if reset:
            self.reset()
        self._write_squid_file()
