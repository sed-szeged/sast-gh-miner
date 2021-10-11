import datetime
from calendar import monthrange


def date_check(start_year, end_year, start_month, end_month):
    current_year = datetime.datetime.now().year + 1

    if type(start_year) is not int:
        raise TypeError(f'start_year argument must be an int, not type of {type(start_year).__name__}')
    if start_year <= 2007:
        raise ValueError('Github was founded in 2008.')
    if start_year >= current_year:
        raise ValueError('start_year argument should not be greater than the current year.')

    if type(end_year) is not int:
        raise TypeError(f'end_year argument must be an int, not type of {type(end_year).__name__}')
    if end_year <= 2007:
        raise ValueError('Github was founded in 2008.')
    if end_year >= current_year:
        raise ValueError('end_year argument should not be greater than current year.')

    if type(start_month) is not int:
        raise TypeError(f'start_month argument must be an int, not type {type(start_month).__name__}')
    if start_month >= 13:
        raise ValueError('start_month argument should not be greater than 12 (December).')
    if start_month <= 0:
        raise ValueError('start_month argument should not be less than 1 (January).')

    if type(end_month) is not int:
        raise TypeError(f'end_month argument must be an int, not type {type(end_month).__name__}')
    if end_month >= 13:
        raise ValueError('end_month argument should not be greater than 12 (December).')
    if end_month <= 0:
        raise ValueError('end_month argument should not be less than 1 (January).')

    if start_year > end_year:
        raise ValueError(f'Empty intersection. Between {start_year} and {end_year}')

    if start_month > end_month:
        raise ValueError(f'Empty intersection. Between {start_month} and {end_month}')


def get_months(start_year=2011, end_year=2019, start_month=1, end_month=12) -> list:
    """
    :param start_year: int,
    :param start_month: int,
    :param end_year: int,
    :param end_month: int,

    :return: list of string, e.g. ['2011-01', '2011-02', '2011-03', ...]
    """
    date_check(start_year, end_year, start_month, end_month)
    years = [x for x in range(start_year, end_year + 1)]
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    months = months[start_month - 1:end_month]
    print('Years to be investigated: ', years)
    print('Months to be investigated: ', months)
    months_by_year = []
    for y in years:
        for m in months:
            date = f"{y}-{m}"
            months_by_year.append(date)
    return months_by_year


def get_days_string(month):
    """
    Splits the month into days.
    :param month: str, e.g. `2011-08`
    :return: days, list of day strings in ISO 8601 format e.g. "[2018-01-01, .. ,2018-01-31]"
    """
    params = month.split('-')
    number_of_days = monthrange(*[int(x) for x in params])[1]
    days = [f"{month}-{x:02d}" for x in range(1, number_of_days+1)]
    return days


def str_date(date):
    # fancy print later
    return f'{date}\n'
