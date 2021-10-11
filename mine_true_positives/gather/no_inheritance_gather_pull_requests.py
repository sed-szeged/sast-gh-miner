import time
from calendar import monthrange
import os

from repo_tools import get_months
from repo_tools import gather_specific_word_pr_by_date, get_codeCount_of_month
from repo_tools import FileHandler
from repo_tools import GraphQL, DictObj
from repo_tools import clear_text
from repo_tools import Path


class GatherPullRequests:
    def __init__(self):

        self.pull_requests_file = ''
        # only on run can be determined
        self.remaining = 5000
        self._date_ops = {}
        self.setup_finished = False
    
    @property
    def remaining(self):
        return self._remaining
    @remaining.setter
    def remaining(self, value):
        self._remaining = value

    @property
    def word(self):
        return self._word
    @word.setter
    def word(self, value):
        if type(value) is not str:
            raise TypeError(f'specific_word must be of type str instead of {type(value).__name__}')
        self._word = clear_text(value)
        print(f'Serching for {self._word} in pull requests.')
        
    @property
    def pr_db(self):
        return self._pr_db
    @pr_db.setter
    def pr_db(self, value):
        self._pr_db = Path(value).path
    
    @property
    def months(self):
        return self._months
    @months.setter
    def months(self, value):
        self._months = value

    @property
    def query(self):
        return self._query
    @query.setter
    def query(self, value):
        if type(value) is not str:
                raise TypeError(f'query should be of type str instead of {type(value).__name__}')
        self._query = value

    @property
    def gql(self):
        return self._gql
    @gql.setter
    def gql(self, value):
        if type(value) is not GraphQL:
            raise TypeError(f'gql should be a GraphQL object instead of {type(value)}')
        self._gql = value
    
    @property
    def sec(self):
        return self._sec
    @sec.setter
    def sec(self, value):
        if type(value) is float or type(value) is int:
            self._sec = value
            print(f'Searches will be executed every {self._sec} seconds.')    
        else:
            raise TypeError(f'sec should be an int or float instead of {type(value)}')
    
    @property
    def date_ops(self):
        return self._date_ops
    @date_ops.setter
    def date_ops(self, value):
        if not all (p in value for p in ['start_year', 'end_year', 'start_month', 'end_month']):
            raise Exception(f'Date should contain start_year, end_year, start_month, end_month')
        self._date_ops = value
    

    def _save_pr(self, path, pid, msg):
        '''
        Receives a pull request node and a counter. Writes to a file.

        param path : string, path where the pull requests should be saved

        yields     : string, comma separated values of a single pull request
        '''
        line = f'{self.counter}, {pid}, {msg}\n'
        sf =  open(path, 'a')
        sf.write(line)
        sf.close()
    
    def _get_p_after_and_has_next(self, pageInfo):  
        '''
        Sets loop variables according to the page info.

        param   pageInfo : DictObj, from query

        return  p_after : str, for formattign the query with the end cursor of the current page
        return  has_next : bool, loop variable
        '''
        has_next = pageInfo.hasNextPage
        if has_next is True:
            p_after = ', after:"' + pageInfo.endCursor + '"'
        else:
            p_after = ''
        return p_after, has_next
    
    
    def _get_query_result(self, query: str, specific_word: str, month: str, p_after: str) -> DictObj:
        '''
        Runs the query until it is not successful (error code:502).

        param  gql          : object, GraphQL
        param  query        : string, query string
        param  specific_word: string, the word to search by
        param  month        : string, date ISO8601
        param  p_after      : string, last pull request id on previous page

        return res_dict_obj : object, DictObj, dictionary objectlike representation
        '''
        success = True
        while success is not False:
            try:
                result = self._gql.run_query(query.format(specific_word, month, p_after))
                res_dict_obj = DictObj(result)
                success = False
            except Exception as e:
                print(e)
                time.sleep(300)
        return res_dict_obj
    
    def _more_than_1000(self, month):
        '''
        Checks for matching results in the given month.
        
        param month: str, e.g. "2018-01"

        return bool, true if more than 1000 matches in the month else false
        return int, number of matches
        '''
        res_obj = self._get_query_result(self._month_test_query, self._word, month, p_after='')
        if res_obj.data.search.codeCount >= 1000:
            return True, res_obj.data.search.codeCount
        else:
            return False, res_obj.data.search.codeCount

    def _get_days_string(self, month):
        '''
        Splits the month into days.
        param str, month
        return days, list of day strings in ISO 8601 format e.g. "[2018-01-01, .. ,2018-01-31]"
        '''
        params = month.split('-')
        number_of_days = monthrange(*[int(x) for x in params] )[1]
        days = [f"{month}-{x:02d}" for x in range(1, number_of_days+1)]
        return days


    def _get_pull_requests(self, date):
        '''
        Main function. Running the query and processing the results.
        param date, list of str e.g. "[2015-01, ..., 2016-02-01, ..., 2018-03]"
        '''
        has_next = True
        p_after = ''
        time.sleep(self._sec)
        while has_next:

            res_obj = self._get_query_result(self._query, self._word, date, p_after)
            # self.remaining = res_obj.data.rateLimit.remaining

            p_after, has_next = self._get_p_after_and_has_next(res_obj.data.search.pageInfo)

            for element in res_obj.data.search.edges.elements:
                
                pr = element.node
                comments = ""
                bodyText = ""
                title = ""
                try:
                    for c in pr.comments.edges.elements:
                        comments += clear_text(c.node.bodyText)
                except Exception as e:
                    print('Caught an exception while processing comments: ', e)

                try:
                    bodyText = clear_text(pr.bodyText)
                except Exception as e:
                    print('Caught an exception while processing bodyText: ', e)

                try:
                    title = clear_text(pr.title)
                except Exception as e:
                    print('Caught an exception while processing title: ', e)

                txt = f'TITLE--{title} BODY--{bodyText} COMMENTS--{comments}'
                self._save_pr(self._pr_db, pr.id, txt)
                self.counter += 1
                

    def _get_pull_request_for_a_month(self, month):
        '''
        Checks if the month needs further division.
        Calls the _get_pull_requests for every date(single month, or month with days).

        param month, str e.g. "2018-01"
        '''
        further, codeCount = self._more_than_1000(month)
        self.stat[month] = codeCount

        if further:
            query_input = self._get_days_string(month)
            print(f'{month} will be divided further.\nPull requests number: {codeCount}.')
        else:
            query_input = [month]

        for param in query_input:
            self._get_pull_requests(param)

        
    def setup(self, graphql, date_ops, specific_word, save_file_path, seconds=0.72):
        '''
        Sets the variables that are important for the pull requet gathering.
        
        param graphql        : GraphQl object
        param seconds        : int or float, execution rate
        param date_ops       : list of date strings
        param specific_word  : the word to be searched for
        param save_file_path : the path where the results should be saved
        '''
        self.gql = graphql
        self.sec = seconds

        self.date_ops = date_ops
        self.months = get_months(**self._date_ops)
        
        self.word = clear_text(specific_word)
        self.query = gather_specific_word_pr_by_date
        self._month_test_query = get_codeCount_of_month
        
        self._pull_requests_path = save_file_path
        self.pull_requests_file = self.pr_db = save_file_path
        self.pr_cols = ['id', 'pid', 'msg']
        self.stat = {}

        self.setup_finished = True
        print(f'Results will be saved to a new version of file: {self._pull_requests_path}')

    def execute(self):
        '''
        After setup runs the process.
        '''
        if self.setup_finished is True:
            self.reset()
            self.counter = 1
            for month in self._months:
                self._get_pull_request_for_a_month(month)
                print(month, end='\r')
            return self
        else:
            raise Exception('The setup of object not yet completed.')

    def _delete_file(self, file_path):
        '''
        param file_path, str
        '''
        try:
            if os.path.isfile(file_path):
                # os.unlink
                os.remove(file_path)
        except Exception as e:
            print(e, file_path)

    def reset(self):
        '''
        Deletes the pull requests file.
        '''
        self._delete_file(self._pull_requests_path)
        