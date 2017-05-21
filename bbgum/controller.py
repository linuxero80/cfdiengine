from abc import ABCMeta, abstractmethod

class Controller(object):
    '''
    Deals back and forth with transaction's actions
    '''

    @abstractmethod
    def finished(self):
        """indicates when internal state machine has finished"""

    @abstractmethod
    def outcomming(self, mon, act):
        """handler to work outcomming action out"""

    @abstractmethod
    def incomming(self, mon, act):
        """handler to work incomming action out"""

    @abstractmethod
    def get_reply(self):
        """comforms reply for blocking transaction"""
