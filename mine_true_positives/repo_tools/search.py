def sonar_search(txt):
    if 'sonar' in txt:
        if 'fix' in txt:
            return True
    return False

def squid_search(txt):
    if 'squid:' in txt or 'quid:' in txt:
        return True
    return False