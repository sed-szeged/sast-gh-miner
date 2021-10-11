import os
import unidecode
import datetime


def check_file(path: str) -> bool:
    """
    :param path: str
    :return: bool
    """
    return os.path.isfile(path)


def remove_non_ascii(txt: str) -> str:
    """
    Remove all non-ascii characters from a text.
    Convert all non-ascii characters to the closest ascii character available

    :param txt: file info string
    :return: cleared file info string
    """
    return unidecode.unidecode(txt)


def report(start: datetime.datetime, counter: int, total: int, report_frequency: int):
    """
    Prints out process status. Should be done with bars from modern python library

    :param start: datetime.now()
    :param counter: str, actual row
    :param total: int, total number of rows in csv
    :param report_frequency: int
    :return:  None
    """
    # At the start:
    if counter < report_frequency:
        print(f'{counter}/{total} - Started at: {start.day}/{start.hour}:{start.minute}   ', end='\r')

    else:
        if counter % report_frequency == 0:
            now = datetime.datetime.now()
            delta = now - start
            estimate = delta.total_seconds() * total / counter
            date = start + datetime.timedelta(seconds=estimate)
            day, hour, minute = date.day, date.hour, date.minute
            print(f'{counter}/{total} - Finishing around: {day}/{hour}:{minute}', end='\r')


def split_row(row: str) -> list:
    """
    Split comma separated row into list

    :param row:
    :return: list of strings
    """
    return [x.strip() for x in row.split(',')]


def get_file_len(path: str) -> int:
    """
    Get number of lines in a file.

    :param path: str
    :return: int if path is valid else None
    """
    if os.path.isfile(path):
        with open(path) as f:
            for i, _ in enumerate(f):
                pass
        return i + 1
    return 0


def create_row_dict(line: str, keys: list) -> dict:
    """
    Create a dictionary from row.

    :param line: str, one row in csv
    :param keys: list of attributes of a downloaded file, names of columns in csv
    :return: dictionary
    """
    info = dict()
    line_list = split_row(line)
    for index, attr in enumerate(keys):
        info[attr] = line_list[index]
    return info
