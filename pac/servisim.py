from pac.adapter import Adapter
from suds.client import Client
from suds.transport import TransportError
import urllib.error

class Servisim(Adapter):
    """
    Current WS API of PAC Servisim
    """
    __PAC_DESC = 'Servisim - Facturacion Electronica'
    __DEFAULT_EP = 'http://201.150.37.20/wstest/CFDI.svc?wsdl' #testing

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
                raise AdapterError(
                    'can not connect with end point{0}'.format(self.ep))
        conn = connect()
        req = conn.factory.create(m)
        req.User = self.config['LOGIN']
        req.Pass = self.config['PASSWD']
        return req, conn

    def stamp(self, xml, xid):
        '''
        Timbrado usando XML firmado por el cliente
        Args:
            xml (str): xml de cfdi firmado por cliente
            xid (str): mi identificador alternativo de cfdi
        '''
        try:
            req, conn = self.__setup_req('ns0:TimbradoCFDIRequest')
            req.TipoPeticion = '1' # SIGNED BY CUSTOMER
            req.IdComprobante = xid
            req.Xml = xml
            self.logger.debug(
                "The following request for stamp will be sent\n{0}".format(req)
            )
            return conn.service.timbrarCFDI(req)
        except (WebFault, Exception) as e:
            raise AdapterError("Stamp experimenting problems")

    def fetch(self, xid):
        '''
        Obtencion de cfdi previamente timbrado mediante
        identificador de cfdi
        Args:
            xid (str): mi identificador alternativo de cfdi
        '''
        try:
            req, conn = self.__setup_req('ns0:ObtencionCFDIRequest')
            req.TipoPeticion = '2' # TO EXPECT CFDI ALTERNATIVE ID
            req.Emisor = self.config['RFC']
            req.Identificador = xid
            self.__logger.debug(
                "The following request for fetch will be sent\n{0}".format(req)
            )
            return conn.service.obtenerCFDI(req)
        except (WebFault, Exception) as e:
            raise AdapterError("Fetch experimenting problems")

    def cancel(self, xml):
        '''
        Cancelacion de XML firmado por el cliente
        Args:
            xml (str): xml de cfdi firmado por cliente
        '''
        try:
            req, conn = self.__setup_req('ns0:CancelacionCFDIRequest')
            req.TipoPeticion = '1' # SIGNED BY CUSTOMER
            req.Emisor = self.config['RFC']
            req.Xml = xml
            self.logger.debug(
                "The following request for cancel will be sent\n{0}".format(req))
            return conn.service.cancelarCFDI(req)
        except (WebFault, Exception) as e:
            raise AdapterError("Cancel experimenting problems")
