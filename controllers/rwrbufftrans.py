from bbgum.controller import Rwr

impt_class = 'RwrBuffTrans'

class RwrBuffTrans(Rwr):
    """
    Deals with receive with response transaction's actions
    """
    def __init__(self):
        super().__init__()

    def process_buff(self, buff):
        rc = 0
        return (rc, '666'.encode())

    def postmortem(self, failure):
        print('hola mundo')