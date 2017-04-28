from crypto.signer import Signer
from misc.helperstr import HelperStr
import os
import subprocess
import tempfile

class Sha256rsa(Signer):
    """
    """

    def __init__(self, logger, pem_privkey):
        super().__init__(logger, pem_privkey)

    def sign(self, str2sign):

        def touch(path):
            with open(path, 'a'):
                os.utime(path, None)

        sealbin_f = '/tmp/{0}'.format(HelperStr.random_str(8))
        input_f = '/tmp/{0}'.format(HelperStr.random_str(8))
        result_f = '/tmp/{0}'.format(HelperStr.random_str(8))

        touch(sealbin_f)
        touch(input_f)
        touch(result_f)

        with open(input_f, 'a') as cf:
            cf.write(str2sign)

        dgst_args = [
            'dgst',
            '-sha256',
            '-sign',
            self.pk,
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

        t = None
        with open(result_f, 'r') as rf:
            t = rf.readline()

        os.remove(sealbin_f)
        os.remove(input_f)
        os.remove(result_f)
        return t
