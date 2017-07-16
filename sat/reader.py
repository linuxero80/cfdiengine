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
            'STAMP_DATE': None,
            'SAT_CERT_NUMBER': None,
            'UUID': None,
            'SAT_SEAL': None,
            'CFD_SEAL': None,
            'INCEPTOR_NAME': None,
            'INCEPTOR_RFC': None,
            'INCEPTOR_CP': None,
            'RECEPTOR_NAME': None,
            'RECEPTOR_RFC': None,
            'CFDI_CERT_NUMBER': None,
            'CFDI_DATE': None,
            'CFDI_SERIE': None,
            'CFDI_FOLIO': None,
            'CFDI_SUBTOTAL': None,
            'CFDI_TOTAL': None,
            'ARTIFACTS': [],
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

        if name == "cfdi:Emisor":
            for (k, v) in attrs.items():
                if k == "Nombre":
                    self.__ds['INCEPTOR_NAME'] = v
                if k == "Rfc":
                    self.__ds['INCEPTOR_RFC'] = v

        if name == "cfdi:Receptor":
            for (k, v) in attrs.items():
                if k == "Nombre":
                    self.__ds['RECEPTOR_NAME'] = v
                if k == "Rfc":
                    self.__ds['RECEPTOR_RFC'] = v

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
                if k == "LugarExpedicion":
                    self.__ds['INCEPTOR_CP'] = v

        if name == "cfdi:Concepto":
            c = {}
            for (k, v) in attrs.items():
                if k == "Cantidad":
                    c[k.upper()] = v
                if k == "Descripcion":
                    c[k.upper()] = v
                if k == "Importe":
                    c[k.upper()] = v
                if k == "NoIdentificacion":
                    c[k.upper()] = v
                if k == "ClaveUnidad":
                    c[k.upper()] = v
                if k == "ValorUnitario":
                    c[k.upper()] = v
            self.__ds['ARTIFACTS'].append(c)

        if name == "cfdi:Impuestos":
            for (k, v) in attrs.items():
                if k == "TotalImpuestosRetenidos":
                    self.__ds['TAXES']['RET']['TOTAL'] = v
                if k == "TotalImpuestosTrasladados":
                    self.__ds['TAXES']['TRAS']['TOTAL'] = v

        if name == "tfd:TimbreFiscalDigital":
            for (k, v) in attrs.items():
                if k == "UUID":
                    self.__ds['UUID'] = v
                if k == "SelloSAT":
                    self.__ds['SAT_SEAL'] = v
                if k == "SelloCFD":
                    self.__ds['CFD_SEAL'] = v
                if k == "NoCertificadoSAT":
                    self.__ds['SAT_CERT_NUMBER'] = v
                if k == "FechaTimbrado":
                    self.__ds['STAMP_DATE'] = v
