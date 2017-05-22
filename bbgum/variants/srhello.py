from bbgum.controller import Sr

class SrHello(Sr):
    '''
    Deals with single recive transaction's actions
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def process_buff(buff):
        rc = 0
        buff.decode("utf-8")
        return rc
