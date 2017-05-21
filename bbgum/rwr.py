from bbgum.controller import Controller
import abc

class Rwr(Controller):
    '''
    Deals with recive with response transaction's actions
    '''
    __metaclass__ = abc.ABCMeta
    IN_RECV_REQ, IN_RECV_REPLY = range(2)

    def __init__(self):
        self.current_step = self.IN_RECV_REQ
        self.steps = [self.__recv_request, self.__recv_reply]
        self.finish_flag = False

    def finished(self):
        return self.finish_flag

    def incomming(self, mon, act):
        self.steps[self.current_step](mon, act)

    def __recv_request(self, mon, act):
        '''process an incomming request'''

        def res_action(s):
            '''creates action with request result code'''
            a = Action()
            a.archetype = Frame.reply_archetype(act.archetype)
            a.transnum = act.transnum
            a.buff = bytes([
                Frame.REPLY_PASS if s == 0 else Frame.REPLY_FAIL,
                s
            ])
            return a

        def resp_action(d):
            '''creates action with response's data'''
            a = Action()
            a.archetype = act.archetype
            a.transnum = act.transnum
            a.buff = d

        (status, buff) = self.process_buff(act.buff)
        mon.send(res_action(status))

        if status == 0:
            mon.send(resp_action(buff))
        else:
            self.finish_flag = True

    @abc.abstractmethod
    def process_buff(buff):
        """processes incomming buffer"""
