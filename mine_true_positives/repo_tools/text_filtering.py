import re

def get_squids(text):
    
    squids = []
    m = re.findall('quid:([^\s]+)', text)
    for i in m:
        #squids.append('squid:'+i)
        if i.startswith('S') or i.startswith('s'):
            s = filter_digits(i)
        else:
            s = filter_words(i)
        squids.append(s)
    
    
    mm = re.findall('quid%3A([^\s]+)', text)
    for i in mm:
        #squids.append('squid:'+i)
        if i.startswith('S') or i.startswith('s'):
            s = filter_digits(i)
        else:
            s = filter_words(i)
        squids.append(s)
    
    set_of_squids = set(squids)
    text_of_squids = ''
    
    for s in set_of_squids:
        text_of_squids = text_of_squids + '-' + s
    text_of_squids = text_of_squids[1:]
    # print(text_of_squids)
    
    return text_of_squids


# UselessParenthesesCheck\\n\\nChange-Id:'
def filter_words(squid):
    s = re.findall('\w+|$', squid)[0]
    return s

# 'UselessParenthesesCheck\\n\\nChange-Id:'
# 'UselessParenthesesCheck'

# squid = 'S12345)'
def filter_digits(squid):
    s = 'S'
    for x in squid:
        if x.isdigit():
            s += x
    if s is 'S':
        s = filter_words(squid)  ## ha %3A van a kettőspont helyett és a squid szoveggel van kiirva és S-sel kezdődik xd
    return s

# filter_digits('S12345)'), 'squid:S2057:Serializable', 'squid:S1699:'
# 'S12345', 'S2057', 'S1699'