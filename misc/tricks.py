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

def truncate(f, n):
    """
    Truncates/pads a float f to n decimal places without rounding
    """
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])
