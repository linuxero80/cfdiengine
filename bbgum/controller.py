class Controller(object):
    '''
    Deals back and forth with transaction's actions
    '''

    def finished(self):
        """indicates when internal state machine has finished"""
        pass

    def outcomming(self, mon, act):
        """handler to work outcomming action out"""
        pass

    def incomming(self, mon, act):
        """handler to work incomming action out"""
        pass

    def get_reply(self):
        """comforms reply for blocking transaction"""
        pass
