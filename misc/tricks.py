import sys
import traceback

def dump_exception():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(
        exc_type,
        exc_value,
        exc_traceback
    )
    return ''.join('!! ' + line for line in lines)

def dict_params(l, k, v): 
    '''
    creates a dictionary from a list of
    dictionaries with name/value elements
    '''
    n = {}
    for d in l:
        n[d[k]] = d[v]
    return n
