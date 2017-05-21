from bbgum.controller import Controller
import abc

class Sr(Controller):
    '''
    Deals with single recive transaction's actions
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def finished(self):
        return True

    def incomming(self, mon, act):

        def result_buff():
            rc = self.process_buff(act.buff)
            return bytes([
                Frame.REPLY_PASS if rc == 0 else Frame.REPLY_FAIL,
                rc
            ])

        a = Action()
        a.archetype = Frame.reply_archetype(act.archetype)
        a.transnum = act.transnum
        a.buff = result_buff
        mon.send(a)

    @abc.abstractmethod
    def process_buff(buff):
        """processes incomming buffer"""
