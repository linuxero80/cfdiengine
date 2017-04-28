from misc.localexec import LocalExec
from abc import ABCMeta, abstractmethod
from distutils.spawn import find_executable
import tempfile, os

class Signer(object):
    """
    """
    __SSL_BIN = "openssl"

    def __init__(self, logger, fullpath_pk):

        def seekout_openssl():
            executable = find_executable(self.__SSL_BIN)
            if executable:
                return os.path.abspath(executable)
            raise SignerError("it has not found {} binary".format(self.__SSL_BIN))

        self.le = LocalExec(logger)
        self.pk = fullpath_pk
        self.ssl_bin = seekout_openssl()

    @abstractmethod
    def sign(self, str2sign):
        """signs an string and returns base64 string"""

class SignerError(Exception):
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message   
