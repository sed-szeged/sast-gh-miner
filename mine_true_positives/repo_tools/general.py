def file_len(path):
    with open(path, 'r') as f:
        for i, _ in enumerate(f):
            pass
    return i + 1