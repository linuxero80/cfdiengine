def dict_params(l, k, v): 
    '''
    creates a dictionary from a list of
    dictionaries with name/value elements
    '''
    n = {}
    for d in l:
        n[d[k]] = d[v]
    return n
