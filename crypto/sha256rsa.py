from crypto.signer import Signer, SignerError
from misc.helperstr import HelperStr
import os
import subprocess
import tempfile

class Sha256rsa(Signer):
    """
    """
    __SIZE_RANDOM_STR = 8

    def __init__(self, logger, pem_pubkey, pem_privkey):
        super().__init__(logger, pem_pubkey, pem_privkey)

    def verify(self, signature, str2verify):
        tmp_dir = tempfile.gettempdir()
        decoded_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(self.__SIZE_RANDOM_STR))
        signature_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(self.__SIZE_RANDOM_STR))
        result_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(self.__SIZE_RANDOM_STR))
        verify_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(self.__SIZE_RANDOM_STR))

        self.__touch(decoded_f)
        self.__touch(signature_f)
        self.__touch(result_f)
        self.__touch(verify_f)

        with open(signature_f, 'a') as sf:
            sf.write(signature)

        with open(verify_f, 'a') as vf:
            vf.write(str2verify)

        base64_args = [
            'base64',
            '-A',
            '-d',
            '-in',
            signature_f,
            '-out',
            decoded_f
        ]

        dgst_args = [
            'dgst',
            '-sha256',
            '-verify',
            self.pem_pubkey,
            '-signature',
            decoded_f,
            verify_f
        ]

        t = None
        try:
            self.le([self.ssl_bin] + base64_args, cmd_timeout = 10, ign_rcs = None)
            self.le([self.ssl_bin] + dgst_args, cmd_timeout = 10, ign_rcs = None)
        except subprocess.CalledProcessError as e:
            self.logger.error("Command raised exception: " + str(e))
            raise SignerError("Output: " + str(e.output))


        rs = self.__fetch_result(result_f)

        os.remove(decoded_f)
        os.remove(signature_f)
        os.remove(result_f)
        os.remove(verify_f)
        return rs


    def __fetch_result(self, path):
        rs = None
        statinfo = os.stat(path)
        if statinfo.st_size > 0:
            rs = ''
            with open(path, 'r') as rf:
                for line in rf:
                    rs = rs + line.replace("\n", "")
        if rs == None:
            SignerError("Unexpected ssl output!!!")
        return rs

    def __touch(self, path):
        with open(path, 'a'):
            os.utime(path, None)

    def sign(self, str2sign):

        tmp_dir = tempfile.gettempdir()
        sealbin_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(self.__SIZE_RANDOM_STR))
        input_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(self.__SIZE_RANDOM_STR))
        result_f = '{}/{}'.format(tmp_dir, HelperStr.random_str(self.__SIZE_RANDOM_STR))

        self.__touch(input_f)

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
