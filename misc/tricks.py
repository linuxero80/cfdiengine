def dict_params(): 
    '''
    creates a dictionary from a list of
    dictionaries with name/value elements
    '''
    n = {}
    for d in l:
        n[d["name"]] = d["value"]
    return n
