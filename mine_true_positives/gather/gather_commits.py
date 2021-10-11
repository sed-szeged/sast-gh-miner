import time

from repo_tools import GraphQL
from repo_tools import clear_text

from gather.main_gather import Gather
from tp_utils import commit_gatherer_from_pr_node_query
from tp_utils import delete_file
from tp_utils import file_len, file_line_by_line, csr2dict, write_line_nl


class GatherCommitsFromPullRequests(Gather):

    def __init__(self, user, password, token, pr_filtered_csv, commits_csv, pr_keys, commit_keys, sec=0.72):
        super().__init__()
        self.u = user
        self.p = password
        self.token = token
        self.sec = sec
        self.gql = self._init_gql()

        # Csv files:
        self.pr_filtered_csv = pr_filtered_csv
        self.commits_csv = commits_csv

        # Keys:
        self.pr_keys = pr_keys
        self.commit_keys = commit_keys

        # query string
        self.query = commit_gatherer_from_pr_node_query

        self.pr_keys = pr_keys
        self.commit_keys = commit_keys

        self.total = file_len(self.pr_filtered_csv)
        self.counter = 0

        print(f'Commits will be saved to file: {self.commits_csv}.')
        print(f'With columns: {", ".join(self.commit_keys)}')

    def _init_gql(self):
        return GraphQL(self.token)

    def reset(self):
        """
        Delete commits csv
        """
        delete_file(self.commits_csv)

    def _filtered_row_dicts(self):
        """
        Reads the filtered pr csv and yields the values in dict format.
        """
        for line in file_line_by_line(self.pr_filtered_csv):
            yield csr2dict(line, self.pr_keys)
    
    def _save_commit(self, pid, commit, prev_txt):
        """
        Receives a commit node. Tha information about the commit is wrote down to commits csv file.
        :param pid: str,
        :param commit: node obj,
        :param prev_txt: str,
        :return:
        """
        c_id = commit.id
        c_oid = commit.oid
        c_repo = commit.repository.nameWithOwner
        c_msg = clear_text(commit.message)

        write_line_nl(self.commits_csv, [self.counter, pid, c_id, c_oid, c_repo, prev_txt, c_msg])

    def get_commits(self):
        for row_dict in self._filtered_row_dicts():
            cnt = row_dict['id']
            pid = row_dict['pid']
            prev_txt = row_dict['txt']

            c_after = ''
            has_next = True
            time.sleep(self.sec)

            page_number = 1
            while has_next:
                query = self.query.format(pid, c_after)
                res_obj = self._get_query_result(some_id=pid, query=query)

                if res_obj is not None:
                    page_number, c_after, has_next = self._pagination(res_obj.data.node.commits.pageInfo,
                                                                      res_obj.data.node.commits.totalCount,
                                                                      pid, page_number)
                    for element in res_obj.data.node.commits.edges.elements:
                        c = element.node.commit
                        self._save_commit(pid, c, prev_txt)
                        self.counter += 1
                else:
                    has_next = False

            print(f'\r{self.total}/{cnt}', end='')

    def execute(self, reset=True):
        if reset:
            self.reset()
        self.get_commits()
