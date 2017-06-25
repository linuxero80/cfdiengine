from bbgum.controller import Sr

impt_class = 'SrPostBuff'


class SrPostBuff(Sr):
    """
    Deals with single receive transaction's actions
    """

    ERROR_CODES = {
        'SUCCESS': 0
    }

    def __init__(self, logger, bm):
        super().__init__()
        self.logger = logger
        self.bm = bm

    def process_buff(self, buff):
        rc = self.ERROR_CODES['SUCCESS']
        sid = buff[0]
        self.bm.write(sid, buff[1:])
        return rc
