import os

def create_qrcode(as_usr, uuid, erfc, rrfc, total, chunk):
    """creates qrcode as per cfdi v33"""

    import qrcode
    from misc.helperstr import HelperStr

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


def writedom_cfdi(d, file_out):
    """writes and makes up a cfdi's dom"""

    import xml.etree.ElementTree as ET
    from pyxb.namespace import XMLSchema_instance as xsi
    from pyxb.namespace import XMLNamespaces as xmlns

    d.documentElement.setAttributeNS(
        xsi.uri(), 'xsi:schemaLocation',
        'http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd')
    d.documentElement.setAttributeNS(xmlns.uri(), 'xmlns:xsi', xsi.uri())

    namespaces = {
        'cfdi': 'http://www.sat.gob.mx/cfd/3',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    root = ET.fromstring(d.toxml("utf-8").decode())
    t = ET.ElementTree(root)
    t.write(file_out, xml_declaration=True,
           encoding='utf-8', method="xml")
