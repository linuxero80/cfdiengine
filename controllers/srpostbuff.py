from bbgum.controller import Sr

impt_class = 'SrPostBuff'


class SrPostBuff(Sr):
    """
    Deals with single receive transaction's actions
    """
    def __init__(self, logger, bm):
        super().__init__()
        self.logger = logger
        self.bm = bm

    def process_buff(self, buff):
        rc = 0
        return rc
