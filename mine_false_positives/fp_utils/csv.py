def csr2list(row: str) -> list:
    """
    Split comma separated row into list

    :param row:
    :return: list of strings
    """
    return [x.strip() for x in row.split(',')]


def csr2dict(line: str, keys: list) -> dict:
    """
    Create a dictionary from row.

    :param line: str, one row in csv
    :param keys: list of attributes of a downloaded file, names of columns in csv
    :return: dictionary
    """
    info = dict()
    line_list = csr2list(line)
    for index, attr in enumerate(keys):
        info[attr] = line_list[index]
    return info


def list2csr(_list: list) -> str:
    """
    Create comma separated row from list.

    :param _list:list
    :return: str
    """
    return ','.join(map(str, _list))
