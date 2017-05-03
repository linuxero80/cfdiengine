from crypto.signer import Signer
from misc.helperstr import HelperStr
import os
import subprocess
import tempfile

class Sha256rsa(Signer):
    """
    """

    def __init__(self, logger, pem_pubkey, pem_privkey):
        super().__init__(logger, pem_pubkey, pem_privkey)

    def verify(self, signature):
        pass

    def __fetch_result(self, path):
        rs = None
        statinfo = os.stat(path)
        if statinfo.st_size > 0:
            with open(path, 'r') as rf:
                rs = rf.readline().replace("\n", "")
        if rs == None:
            SignerError("Unexpected ssl output!!!")
        return rs

    def __touch(self, path):
        with open(path, 'a'):
            os.utime(path, None)

    def sign(self, str2sign):

        SIZE_RANDOM_STR = 8

        tmp_dir = tempfile.gettempdir()
        sealbin_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(SIZE_RANDOM_STR))
        input_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(SIZE_RANDOM_STR))
        result_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(SIZE_RANDOM_STR))

        self.__touch(sealbin_f)
        self.__touch(input_f)
        self.__touch(result_f)

        with open(input_f, 'a') as cf:
            cf.write(str2sign)

        dgst_args = [
            'dgst',
            '-sha256',
            '-sign',
            self.pem_privkey,
            '-out',
            sealbin_f,
            input_f
        ]

        base64_args = [
            'base64',
            '-in',
            sealbin_f,
            '-out',
            result_f
        ]

        t = None
        try:
            self.le([self.ssl_bin] + dgst_args, cmd_timeout = 10, ign_rcs = None)
            self.le([self.ssl_bin] + base64_args, cmd_timeout = 10, ign_rcs = None)
        except subprocess.CalledProcessError as e:
            self.logger.error("Command raised exception: " + str(e))
            raise SignerError("Output: " + str(e.output))

        rs = self.__fetch_result(result_f)

        os.remove(sealbin_f)
        os.remove(input_f)
        os.remove(result_f)

        return rs
