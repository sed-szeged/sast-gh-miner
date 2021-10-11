import calendar, datetime
import time

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

def get_months(start_year=2011, end_year=2019, start_month=1, end_month=12):
    date_check(start_year, end_year, start_month, end_month)
    years = [x for x in range(start_year, end_year + 1)]
    # nyilvan nem kellene 12 folott bevinni meg ilyenek
    months = ['01','02','03','04','05','06','07','08','09','10','11','12']
    months = months[start_month - 1:end_month]
    print('Years to be investigated: ', years)
    print('Months to be investigated: ', months)
    months_by_year = []
    for y in years:
        for m in months:
            date = f"{y}-{m}"
            months_by_year.append(date)
    return months_by_year

def get_days(start_year=2008, end_year=2019, start_month=1, end_month=12):
    date_check(start_year, end_year, start_month, end_month)
    years = [x for x in range(start_year,end_year + 1)]
    months = [x for x in range(start_month, end_month + 1)]
    days = {}
    for y in years:
        days[y] = []
        for m in months:
            weeks = calendar.monthcalendar(y, m)
            for week in weeks:
                for d in week:
                    if d is not 0:
                        # date = str(y) + '-' + str(m) + '-' + str(d)
                        date = datetime.datetime(y,m,d)
                        date = date.strftime('%Y-%m-%d')
                        days[y].append(date)
    return days