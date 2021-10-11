import time
from repo_tools import GraphQL


def run_query(gql: GraphQL, some_id: str, query: str):
    """
    Runs the query until it is not successful (error code:502).

    :param gql: GraphQL object,
    :param  query: str, formatted query string.
    :param some_id: str, for row identification purpose.
    :return: res_dict_obj - object, DictObj, dictionary object like representation.
    """
    result = None

    success = True
    while success is not False:
        try:
            result = gql.run_query(query)
            res_check = result.get('errors', False)
            if res_check:
                errors = result['errors']
                print(errors)
                for error in errors:
                    print(error['type'])
            else:
                remaining = result['data']['rateLimit']['remaining']
                print(remaining)
            # {'errors': [{'type': 'RATE_LIMITED', 'message': 'API rate limit exceeded'}]}
            success = False
        except AttributeError as e:
            print(f'Exception {e}\nSkipping {some_id}')
            return None
        except Exception as e:
            print(f'Unexpected error occured.\n{some_id}\n{e}')
            time.sleep(60)
    return result
