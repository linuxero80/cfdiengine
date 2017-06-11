from bbgum.controller import Sr

impt_class = 'SrHello'

class SrHello(Sr):
    """
    Deals with single receive transaction's actions
    """
    def __init__(self):
        pass

    def process_buff(self, buff):
        rc = 0
        buff.decode("utf-8")
        return rc
