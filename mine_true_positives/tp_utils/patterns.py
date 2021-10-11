import re


def search_patterns(patterns, txt, flag=re.IGNORECASE):
    matches = set()
    for pattern in patterns:
        re_match_obj = re.findall(pattern, txt, flag)
        for r in re_match_obj:
            matches.add(r)

    while '' in matches:
        matches.remove('')

    return '-'.join(matches)
