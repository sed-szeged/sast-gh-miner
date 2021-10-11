import unicodedata
import unidecode
import sys

def remove_control_characters(string):
    # Cc : control character
    return "".join(char for char in string if unicodedata.category(char)[0]!="C")

def remove_non_ascii(txt):
    # remove all non-ascii characters from a text document. 
    # Convert all non-ascii characters to the closest ascii character available
    return unidecode.unidecode(txt) 

def replace_special_chars(txt):
    # replace comma, because a csv list will be created
    return txt.replace(',', ' ')

def clear_text(txt):
    if type(txt) is not str:
        raise TypeError(f'txt should be of type str, {type(txt).__name__} was given')
    try:
        cleared_txt = replace_special_chars(remove_control_characters(remove_non_ascii(txt)))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    return cleared_txt

# example
# '(川 (kawa, "river") and 学校漢字中国中国中国asd , ASD , squid:789'
# (Chuan  (kawa  "river") and Xue Xiao Han Zi Zhong Guo Zhong Guo Zhong Guo asd   ASD   squid:789

def remove_non_alphanumeric_characters(txt):
    # removes every special character
    return ''.join(e for e in txt if e.isalnum())