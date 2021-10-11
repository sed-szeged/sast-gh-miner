import time
import calendar


def check(api):
    rate, search, graphql, reset = get_times(api)
    t = time.localtime(reset)
    print(
        f'rate: {rate} \nsearch: {search}\ngraphql: {graphql}\nreset_time day/hour/min: {t.tm_mday}/{t.tm_hour}/{t.tm_min}')


def get_times(api):
    success = False
    while not success:
        try:
            limit = api.get_rate_limit()
            reset = api.rate_limiting_resettime
            rate = limit.core.remaining
            search = limit.search.remaining
            graphql = limit.graphql.remaining
            success = True
        except Exception:
            time.sleep(600)
    return rate, search, graphql, reset


def get_times_for_rest_api(api):
    success = False
    while not success:
        try:
            limit = api.get_rate_limit()
            reset = api.rate_limiting_resettime
            rate = limit.core.remaining
            search = limit.search.remaining
            success = True
        except Exception:
            time.sleep(600)
    return rate, search, reset


def wait(api):
    rate, search, reset = get_times_for_rest_api(api)

    if rate < 100 or search < 10:
        sleepy_seconds = reset - calendar.timegm(time.gmtime())
        t = time.localtime(reset)
        print(f'''
Sleep    : {sleepy_seconds} seconds
Rate     : {rate}
Search   : {search}

Rate limiting resettime (day - hour - min)
                        {t.tm_mday} - {t.tm_hour} - {t.tm_min}''')
        time.sleep(sleepy_seconds)
        print("Continue")

