from crypto.signer import OpenSslSigner
import tempfile

class Sha256rsa(OpenSslSigner):
    """
    """

    __init__(self, priv_key):
        super().__init__(priv_key)

    def sign(self, str2sign):

        def create_pivots():
            return (
                tempfile.TemporaryFile(),
                tempfile.TemporaryFile(),
                tempfile.TemporaryFile()
            )

        def perform(s, sealbin_f, input_f, result_f):

            with input_f as cf:
                cf.write(s)

            dgst_args = [
                'dgst',
                '-sha256',
                '-sign',
                self.pk,
                input_f,
                '-out',
                sealbin_f
            ]

            base64_args = [
                'base64',
                '-in',
                sealbin_f,
                '-out',
                result_f
            ]

            try:
                self.le([self.ssl_bin] + dgst_args, cmd_timeout = 10)
                self.le([self.ssl_bin] + base64_args, cmd_timeout = 10)
            except subprocess.CalledProcessError as e:
                self.logger.error("Command raised exception: " + str(e))
                raise SignerError("Output: " + str(e.output))

            t = result_f.readline()
            os.remove(sealbin_f, input_f, result_f)
            return t

        return perform(str2sign, create_pivots())
