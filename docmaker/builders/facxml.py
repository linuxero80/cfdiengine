import datetime
import pyxb
import psycopg2.extras

from sat.v33 import Comprobante
from sat.requirement import writedom_cfdi

class FacXml(BuilderGen):

    __MAKEUP_PROPOS = 'FAC'

    def __init__(self, logger):
        super().__init__(logger)

    def __q_no_certificado(self, conn, usr_id):
        '''
        Consulta el numero de certificado en dbms
        '''
        SQL =  """select CFDI_CONF.numero_certificado
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc AS USR_SUC ON USR_SUC.gral_suc_id = SUC.id
            LEFT JOIN fac_cfds_conf AS CFDI_CONF ON CFDI_CONF.gral_suc_id = SUC.id
            WHERE USR_SUC.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return row['numero_certificado']

    def __q_emisor(self, conn, usr_id):
        '''
        Consulta el emisor en dbms
        '''
        SQL = """select upper(EMP.rfc), upper(EMP.titulo), upper(REG.descripcion)
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc AS USR_SUC ON USR_SUC.gral_suc_id = SUC.id
            LEFT JOIN gral_emp AS EMP ON EMP.id = SUC.empresa_id
            LEFT JOIN cfdi_regimenes AS REG ON REG.numero_control = EMP.regimen_fiscal
            WHERE USR_SUC.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return {
                'RFC': row['rfc'],
                'RAZON_SOCIAL': row['titulo'],
                'REGIMEN_FISCAL': row['descripcion']
            }

    def __q_lugar_expedicion(self, conn, usr_id):
        '''
        Consulta el lugar de expedicion en dbms
        '''
        SQL = """select SUC.cp
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc as USR_SUC ON USR_SUC.gral_suc_id=SUC.id
            WHERE USR_SUC.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return row['cp']

    def __q_moneda(self, conn, prefact_id):
        '''
        Consulta la moneda de la prefactura en dbms
        '''
        SQL = """SELECT
            upper(gral_mon.iso_4217) AS moneda_iso_4217,
            upper(gral_mon.simbolo) AS moneda_simbolo,
            erp_prefacturas.tipo_cambio
            FROM erp_prefacturas
            LEFT JOIN gral_mon ON gral_mon.id=erp_prefacturas.moneda_id
            WHERE erp_prefacturas.id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, prefact_id)):
            # Just taking first row of query result
            return {
                'ISO_4217': row['moneda_iso_4217'],
                'SIMBOLO': row['moneda_simbolo'],
                'TIPO_DE_CAMBIO': row['tipo_cambio']
            }

    def __q_receptor(self, conn, prefact_id):
        '''
        Consulta el cliente de la prefactura en dbms
        '''
        SQL = """SELECT
            upper(cxc_clie.razon_social),
            upper(cxc_clie.rfc)
            FROM erp_prefacturas
            LEFT JOIN cxc_clie ON cxc_clie.id=erp_prefacturas.cliente_id
            WHERE erp_prefacturas.id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, prefact_id)):
            # Just taking first row of query result
            return {
                'RFC': row['rfc'],
                'RAZON_SOCIAL']: row['razon_social'],
                'USO_CFDI': 'G01'
            }

    def __q_conceptos(self, conn, prefact_id):
        '''
        Consulta los conceptos de la prefactura en dbms
        '''
        SQL = """SELECT upper(inv_prod.sku), upper(inv_prod.descripcion),
            upper(inv_prod_unidades.titulo) AS unidad,
            erp_prefacturas_detalles.cant_facturar AS cantidad,
            erp_prefacturas_detalles.precio_unitario,
            (erp_prefacturas_detalles.cant_facturar * erp_prefacturas_detalles.precio_unitario) AS importe
            FROM erp_prefacturas
            JOIN erp_prefacturas_detalles on erp_prefacturas_detalles.prefacturas_id=erp_prefacturas.id
            LEFT JOIN inv_prod on inv_prod.id = erp_prefacturas_detalles.producto_id
            LEFT JOIN inv_prod_unidades on inv_prod_unidades.id = erp_prefacturas_detalles.inv_prod_unidad_id
            WHERE erp_prefacturas_detalles.prefacturas_id="""
        rowset = []
        for row in self.pg_query(conn, "{0}{1}".format(SQL, prefact_id)):
            rowset.append({
                'SKU': row['sku'],
                'DESCRIPCION': row['inv_prod.descripcion'],
                'UNIDAD': row['unidad'],
                'CANTIDAD': row['cantidad'],
                'PRECIO_UNITARIO': row['precio_unitario'],
                'IMPORTE': row['importe']
            })
        return rowset

    def data_acq(self, conn, d_rdirs, **kwargs):

        usr_id = kwargs.get('usr_id', None)
        prefact_id = kwargs.get('prefact_id', None)

        if usr_id is None:
            raise DocBuilderStepError("user id not fed")
        if prefact_id is None:
            raise DocBuilderStepError("prefact id not fed")

        return {
            'EMISOR': self.__q_emisor(conn, usr_id),
            'NUMERO_CERTIFICADO': self.__q_no_certificado(conn, usr_id),
            'RECEPTOR': self.__q_receptor(conn, prefact_id),
            'MONEDA': self.__q_moneda(conn, prefact_id),
            'LUGAR_EXPEDICION': self._q_lugar_expedicion(conn, usr_id),
            'CONCEPTOS': self.__q_conceptos(conn, prefact_id)
        }

    def format_wrt(self, output_file, dat):
        c = Comprobante()
        c.Version = '3.3'
        c.Folio = "test attribute" #optional
        c.Fecha = '{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now())
        c.Sello = "BLABLALASELLO"
        c.FormaPago = "01" #optional
        c.NoCertificado = dat['NUMERO_CERTIFICADO']
        c.Certificado = "certificado en base64"
        c.SubTotal = "4180.0"
        c.Total = "4848.80"
        c.Moneda = ['MONEDA']['ISO_4217']
        c.TipoCambio = ['MONEDA']['TIPO_DE_CAMBIO'] #optional (requerido en ciertos casos)
        c.TipoDeComprobante = 'I'
    #    c.metodoDePago = "NO IDENTIFICADO" #optional
        c.LugarExpedicion = dat['LUGAR_EXPEDICION']

        c.Emisor = pyxb.BIND()
        c.Emisor.Nombre = dat['EMISOR']['RAZON_SOCIAL'] #opcional
        c.Emisor.Rfc = dat['EMISOR']['RFC']
        c.Emisor.RegimenFiscal = dat['EMISOR']['REGIMEN_FISCAL']

        c.Receptor = pyxb.BIND()
        c.Receptor.Nombre = dat['RECEPTOR']['RAZON_SOCIAL'] #opcional
        c.Receptor.Rfc = dat['RECEPTOR']['RFC']
        c.Receptor.UsoCFDI = dat['RECEPTOR']['USO_CFDI']

        c.Conceptos = pyxb.BIND(
            pyxb.BIND(
                Cantidad=5,
                ClaveUnidad='C81',
                ClaveProdServ='01010101',
                Descripcion='Palitroche',
                ValorUnitario='10',
                Importe='50'
            )
        )

        writedom_cfdi(c.toDOM(), self.__MAKEUP_PROPOS, output_file)

    def data_rel(self, dat):
        pass
