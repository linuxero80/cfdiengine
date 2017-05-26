import os
import qrcode
from misc.helperstr import HelperStr

def create_qrcode(as_usr, uuid, erfc, rrfc, total, chunk):
    """creates qrcode as per cfdi v33"""
    def incept_file(i):
        SIZE_RANDOM_STR = 8
        fname = '{}/{}.jpg'.format(
            tempfile.gettempdir(),
            HelperStr.random_str(SIZE_RANDOM_STR)
        )
        with open(fname, 'wb') as q:
            i.save(q, 'JPEG')
        return fname

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(
        '{}{}{}{}{}{}'.format(
            as_usr, uuid, erfc, rrfc, total, chunk
        )
    )
    qr.make(fit=True)
    return incept_file(qr.make_image())
