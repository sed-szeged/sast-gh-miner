import time
from repo_tools import DictObj, GraphQL


class Gather:

    def __init__(self):
        self._remaining = 5000
        self._save_file = None

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

    def _pagination(self, pageInfo, codeCount, some_id, page_number):
        has_next = pageInfo.hasNextPage
        if has_next is True:
            after = ', after:"' + pageInfo.endCursor + '"'
            page_number += 1
        else:
            after = ''
            if codeCount >= 1000:
                print(f'''
{some_id} may need further division.
Pagination stopped at page number:{page_number}.
Maximum page number is 10.
Based on page_number the possibility of further division: {page_number >= 10}
''')
        return page_number, after, has_next
