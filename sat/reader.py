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
        except xml.sax.SAXParseException as e:
            raise

    def __reset(self):
        self.__ds = {
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

        if name == "cfdi:Impuestos":
            for (k, v) in attrs.items():
                if k == "totalImpuestosRetenidos":
                    self.__ds['TAXES']['RET']['TOTAL'] = v
                if k == "totalImpuestosTrasladados":
                    self.__ds['TAXES']['TRAS']['TOTAL'] = v
