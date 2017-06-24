from bbgum.controller import Rwr
from engine.buffmediator import BuffMediator
from engine.erp import do_request


impt_class = 'RwrBuffTrans'


class RwrBuffTrans(Rwr):
    """
    Deals with receive with response transaction's actions
    """

    START_BUFF_TRANS_MODE_GET = b'\xAA'
    START_BUFF_TRANS_MODE_POST = b'\xBB'
    STOP_BUFF_TRANS = b'\xCC'

    def __init__(self, logger, bm):
        super().__init__()
        self.logger = logger
        self.bm = bm

    def process_buff(self, buff):
        mode = buff[0]
        data_str = buff[1:].decode(encoding='UTF-8')
        if mode == ord(self.START_BUFF_TRANS_MODE_POST):
            sid = self.bm.mediate(BuffMediator.IN_STREAM, int(data_str), do_request)
            return 0, str(sid).encode()
        elif mode == ord(self.STOP_BUFF_TRANS):
            sid = int(data_str)
            rc = self.bm.release(sid)
            return rc, str(sid).encode()
        else:
            # non-supported command
            return 1, None

    def postmortem(self, failure):
        self.logger.error(failure)
