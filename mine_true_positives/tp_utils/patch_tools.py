from repo_tools import create_file_string
from repo_tools import Patch


def read_file_in_hunks(file, size):
    hunk = []
    counter = 1
    with open(file, 'rb') as f:
        line = f.readline()
        while line:
            if len(hunk) >= size:
                yield counter, hunk
                hunk.pop(0)
            hunk.append(line.replace(b'\n', b'').replace(b'\r', b'').decode())
            counter += 1
            line = f.readline()
        yield counter, hunk


def search_hunk_in_file(file, code):
    size = len(code)
    end = None
    start = None
    hunk = None
    for counter, hunk in read_file_in_hunks(file, size):
        if hunk == code:
            return counter - size, counter, hunk
    if end is None and start is None:
        if '404: Not Found' in create_file_string(file):
            return 404
        else:
            return 909

    return start, end, hunk


def create_patch_string(path):
    og_patch = ''
    with open(path, 'rb') as f:
        line = f.readline()
        while line:
            og_patch += line.replace(b'\r', b'').decode()
            line = f.readline()
    return og_patch


def get_hunks(path):
    try:
        patch_string = create_patch_string(path)
        patch = Patch(patch_string)
        for hunk in patch.hunks:
            yield hunk
    except Exception as e:
        print('At hunk creation: ', e)
