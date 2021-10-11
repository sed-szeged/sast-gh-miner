

def skip_non_utf8(txt):
    return bytes(txt, 'utf-8').decode("utf-8", 'ignore')


def replace_windows_reserved_chars(txt):
    windows_reserved_chars = '<>:"/\\|?*'
    for char in windows_reserved_chars:
        txt = txt.replace(char, '')
    return txt
