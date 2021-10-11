import time

from .main_gather import Gather

from repo_tools import GraphQL, DictObj
from repo_tools import clear_text

from tp_utils import delete_file, write_line_nl
from tp_utils import get_months, get_days_string
from tp_utils import gather_specific_word_pr_by_date, get_codeCount_of_month


class GatherPullRequests(Gather):
    def __init__(self, github_token, date_ops, specific_word, pull_request_csv, keys, sec=0.72, lang='java'):
        """
        :param github_token: to create GraphQl object, for sending requests
        :param date_ops: dict, of date interval
        :param specific_word : str, the word to be searched for
        :param pull_request_csv: str, the path where the results should be saved
        :param sec: int or float, execution rate
        :param lang: str, on which the related pull requests should be written
        """
        super().__init__()

        # init
        self.token = github_token
        self.date_ops = date_ops
        self.word = clear_text(specific_word)
        self.pr_csv = pull_request_csv
        self.pr_keys = keys
        self.sec = sec
        self.language = lang

        # set
        self.gql = self._init_gql()
        self.months = get_months(**self._date_ops)
        self.query = gather_specific_word_pr_by_date
        self._month_test_query = get_codeCount_of_month

        self.stat = {}
        self.counter = 0

    def _init_gql(self):
        return GraphQL(self.token)

    @property
    def date_ops(self):
        return self._date_ops

    @date_ops.setter
    def date_ops(self, value):
        if not all(p in value for p in ['start_year', 'end_year', 'start_month', 'end_month']):
            raise Exception(f'Date should contain start_year, end_year, start_month, end_month')
        self._date_ops = value

    def _more_than_1000(self, month):
        """
        Checks if there are more results than what could be handled.
        :param month: str, e.g. "2018-01"
        :return: (bool, int) true if more than 1000 matches in the month else false, number of matches
        """
        query = self._month_test_query.format(self.word, self.language, month, '')
        res_obj = self._get_query_result(month, query)
        if res_obj.data.search.codeCount >= 1000:
            return True, res_obj.data.search.codeCount
        else:
            return False, res_obj.data.search.codeCount

    def _get_query_result(self, some_id: str, query: str) -> DictObj:
        """
        Runs the query until it is not successful (error code:502).
        :param  query: str, formatted query string.
        :param some_id: str, for row identification purpose.
        :return: res_dict_obj - object, DictObj, dictionary object like representation.
        """

        success = True
        while success is not False:
            try:
                result = self.gql.run_query(query)
                res_dict_obj = DictObj(result)
                success = False
            except AttributeError as e:
                print(f'Exception {e}\nSkipping {some_id}')
                return None
            except Exception as e:
                print(f'Unexpected error occured.\n{some_id}\n{e}')
                time.sleep(60)
        return res_dict_obj

    def _get_pull_requests(self, date):
        """
        Main function. Running the query and processing the results.
        :param date: list of str e.g. month: [`2015-01`] or month with days: [`2015-01-01`, `2015-01-02`, ...]
        :return:
        """
        has_next = True
        p_after = ''
        time.sleep(self.sec)
        page_number = 1
        while has_next:
            query = self.query.format(self.word, self.language, date, p_after)
            res_obj = self._get_query_result(date, query)
            self.remaining = res_obj.data.rateLimit.remaining

            page_number, p_after, has_next = self._pagination(res_obj.data.search.pageInfo,
                                                              res_obj.data.search.codeCount,
                                                              date,
                                                              page_number)

            for element in res_obj.data.search.edges.elements:
                
                pr = element.node
                comments = ""
                body_text = ""
                title = ""
                try:
                    for c in pr.comments.edges.elements:
                        comments += clear_text(c.node.bodyText)
                except Exception as e:
                    print('Caught an exception while processing comments: ', e)

                try:
                    body_text = clear_text(pr.bodyText)
                except Exception as e:
                    print('Caught an exception while processing bodyText: ', e)

                try:
                    title = clear_text(pr.title)
                except Exception as e:
                    print('Caught an exception while processing title: ', e)

                txt = f'TITLE--{title} BODY--{body_text} COMMENTS--{comments}'
                write_line_nl(self.pr_csv, [self.counter, pr.id, txt])
                self.counter += 1

    def _get_pull_request_for_a_month(self, month):
        """
        Checks if the month needs further division.
        Calls the _get_pull_requests for every date(single month, or month with days).

        :param month: str, e.g. "2018-01"
        """
        further, code_count = self._more_than_1000(month)
        self.stat[month] = code_count

        if further:
            query_input = get_days_string(month)
            print(f'{month} will be divided further.\nPull requests number: {code_count}.')
        else:
            query_input = [month]

        for param in query_input:
            self._get_pull_requests(param)

    def execute(self, reset=True):
        if reset:
            delete_file(self.pr_csv)

        self.counter = 1

        for month in self.months:
            print(f'Search in: {month}')
            self._get_pull_request_for_a_month(month)
            print(f'Finished: {month}')

        return self.stat
