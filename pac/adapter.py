from abc import ABCMeta, abstractmethod


class AdapterError(Exception):
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

class Adapter(metaclass=ABCMeta):
    '''
    Template class for any pac's adapter
    '''

    def __init__(self, logger, pac_name):
        self.logger = logger
        self.pac_name = pac_name


    @abstractmethod
    def stamp(self, xml_str, xid):
        """
        """

    @abstractmethod
    def fetch(self, xid):
        """
        """

    @abstractmethod
    def cancel(self, xml_signed_str, xid):
        """
        """
