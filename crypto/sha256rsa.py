from crypto.signer import Signer
import os
import subprocess
import tempfile

class Sha256rsa(Signer):
    """
    """
    __CIPHER = 'sha256'

    def __init__(self, logger, pem_pubkey, pem_privkey):
        super().__init__(logger, self.__CIPHER, pem_pubkey, pem_privkey)
