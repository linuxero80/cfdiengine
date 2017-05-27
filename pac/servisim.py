from suds.client import Client
from suds.transport import TransportError
import urllib.error

class Servisim(PacAdapter):
    """
    Current WS API of PAC Servisim
    """
    __PAC_DESC = 'Servisim - Facturacion Electronica'
    __DEFAULT_EP = 'http://201.150.37.20/wstest/CFDI.svc?wsdl' #testing
    __CUST_SIGNER = 1
    __USING_UUID = "UUID"

    def __init__(self, logger, *args, **kwargs):
        super().__init__(logger, self.__PAC_DESC)
        self.config = {
            'EP': kwargs.get('end_point', self.__DEFAULT_EP),
            'LOGIN': kwargs.get('login', None),
            'PASSWD': kwargs.get('passwd', None),
            'RFC': kwargs.get('rfc', None)
        }

    def __setup_req(self, m):

        def connect():
            try:
                conn = Client(self.config['EP'])
                self.logger.debug(
                "{0} adapter is up and ready to kick buttocks\n{1}".format(
                    self.pac_name, self.conn))
                return conn
            except (TransportError, urllib.error.HTTPError) as e:
                self.logger.fatal(e)
                raise PacAdapterError(
                    'can not connect with end point{0}'.format(self.ep))

        conn = connect()
        req = conn.factory.create(m)
        req.User = self.config['LOGIN']
        req.Pass = self.config['PASSWD']

        return req, conn

    def stamp(self, xml_str, xid):
        try:
            req, conn = self.__setup_req('ns0:TimbradoCFDIRequest')
            req.TipoPeticion = self.__CUST_SIGNER
            req.IdComprobante = xid
            req.Xml = xml_str
            self.logger.debug(
                "The following request for stamp will be sent\n{0}".format(req)
            )
            return conn.service.timbrarCFDI(req)

        except (WebFault, Exception) as e:
            self.logger.fatal(e)
            raise PacAdapterError("Stamp experimenting problems")

    def fetch(self, xid):
        try:
            req, conn = self.__setup_req('ns0:ObtencionCFDIRequest')
            req.TipoPeticion = self.__USING_UUID
            req.Emisor = self.config['RFC']
            req.Identificador = xid
            self.__logger.debug(
                "The following request for fetch will be sent\n{0}".format(req)
            )
            return conn.service.obtenerCFDI(req)

        except (WebFault, Exception) as e:
            self.logger.fatal(e)
            raise PacAdapterError("Fetch experimenting problems")

    def cancel(self, xml_signed_str, xid):
        try:
            req, conn = self.__setup_req('ns0:CancelacionCFDIRequest')
            req.TipoPeticion = self.__CUST_SIGNER
            req.Emisor = self.config['RFC']
            req.Xml = xml_signed_str
            self.logger.debug(
                "The following request for cancel will be sent\n{0}".format(req))
            return conn.service.cancelarCFDI(req)

        except (WebFault, Exception) as e:
            self.logger.fatal(e)
            raise PacAdapterError("Cancel experimenting problems")
