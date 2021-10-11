from tp_utils import list2csr_nl, dict2csr_nl
import os


def file_len(path):
    with open(path) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1


def write_line_nl(path, list_, mode='a'):
    """
    Writes row to csv file.

    :param path: str, path to file
    :param list_: list of column values of a row.
    :param mode: write type, default: `a`
    :return:
    """
    with open(path, mode, encoding='utf-8') as f:
        f.write(list2csr_nl(list_))


def write_line_dict_nl(path, list_, keys, mode='a'):
    """
    Writes row to csv file.

    :param path: str, path to file
    :param list_: list of column values of a row.
    :param mode: write type, default: `a`
    :return:
    """
    with open(path, mode, encoding='utf-8') as f:
        f.write(dict2csr_nl(list_, keys))


def file_content(path, mode='r'):
    """
    Reads file.

    :param path: str, path to file
    :param mode: write type, default: `a`
    :return:
    """
    with open(path, mode, encoding='utf-8') as f:
        return f.readlines()


def last_line(path, mode='r'):
    """
    Reads file.

    :param path: str, path to file
    :param mode: write type, default: `a`
    :return:
    """
    with open(path, mode, encoding='utf-8') as f:
        for line in f:
            pass
    return line


def delete_file(path):
    """
    :param path: str, path to file
    :return:
    """
    if os.path.isfile(path):
        os.remove(path)


def file_line_by_line(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            yield line


def delete_folder_files(folder):
    for file in os.listdir(folder):
        file = os.path.join(folder, file)
        delete_file(file)
