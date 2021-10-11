import re


def search_for_pattern(pattern, txt, flag=re.I):
    re_match_obj = re.search(pattern, txt, flag)

    if re_match_obj is not None:
        return '--'.join(re_match_obj.groups())
    return ''

def search_for_patterns(patterns, txt, flag=re.I):
    matches = []
    for pattern in patterns:
        matches.append(search_for_pattern(pattern, txt, flag))
    
    while('' in matches) : 
        matches.remove('')

    return '--'.join(matches)

