from abc import ABCMeta, abstractmethod

class BuilderGen(metaclass=ABCMeta):
    """
    Builder interface base class.
    """

    def  __init__(self, logger, *args, **kwargs):
        self.logger = logger

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def data_acq(self, conn, d_rdirs, **kwargs):
        """document's data acquisition"""

    @abstractmethod
    def format_wrt(self, output_file, dat):
        """writes the document"""

    @abstractmethod
    def data_rel(self, dat):
        """release resources previously gotten"""
