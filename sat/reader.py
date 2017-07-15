import xml.sax


class SaxReader(xml.sax.ContentHandler):
    """
    A very basic cfdi reader.
    """
    __ds = None

    def __init__(self):
        pass

    def __call__(self, xml_file_path):
        try:
            self.__reset()
            xml.sax.parse(xml_file_path, self)
            return self.__ds
        except xml.sax.SAXParseException:
            raise

    def __reset(self):
        self.__ds = {
            'CFDI_CERT_NUMBER': None,
            'CFDI_DATE': None,
            'CFDI_SERIE': None,
            'CFDI_FOLIO': None,
            'CFDI_SUBTOTAL': None,
            'CFDI_TOTAL': None,
            'TAXES': {
                'RET': {
                    'DETAILS': [],
                    'TOTAL': 0
                },
                'TRAS': {
                    'DETAILS': [],
                    'TOTAL': 0
                }
            }
        }

    def startElement(self, name, attrs):

        if name == "cfdi:Comprobante":
            for (k, v) in attrs.items():
                if k == "Total":
                    self.__ds['CFDI_TOTAL'] = v
                if k == "SubTotal":
                    self.__ds['CFDI_SUBTOTAL'] = v
                if k == "TipoCambio":
                    self.__ds['MONEY_EXCHANGE'] = v
                if k == "Serie":
                    self.__ds['CFDI_SERIE'] = v
                if k == "Folio":
                    self.__ds['CFDI_FOLIO'] = v
                if k == "Fecha":
                    self.__ds['CFDI_DATE'] = v
                if k == "NoCertificado":
                    self.__ds['CFDI_CERT_NUMBER'] = v

        if name == "cfdi:Impuestos":
            for (k, v) in attrs.items():
                if k == "TotalImpuestosRetenidos":
                    self.__ds['TAXES']['RET']['TOTAL'] = v
                if k == "TotalImpuestosTrasladados":
                    self.__ds['TAXES']['TRAS']['TOTAL'] = v
