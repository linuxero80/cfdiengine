import base64
import datetime
import pyxb
import psycopg2.extras

from docmaker.gen import BuilderGen
from sat.v33 import Comprobante
from sat.requirement import writedom_cfdi


impt_class='FacXml'


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
        SQL = """select upper(EMP.rfc) as rfc, upper(EMP.titulo) as titulo,
            upper(REG.numero_control) as numero_control
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
                'REGIMEN_FISCAL': row['numero_control']
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
            upper(cxc_clie.razon_social) as razon_social,
            upper(cxc_clie.rfc) as rfc
            FROM erp_prefacturas
            LEFT JOIN cxc_clie ON cxc_clie.id=erp_prefacturas.cliente_id
            WHERE erp_prefacturas.id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, prefact_id)):
            # Just taking first row of query result
            return {
                'RFC': row['rfc'],
                'RAZON_SOCIAL': row['razon_social'],
                'USO_CFDI': 'G01'
            }

    def __q_conceptos(self, conn, prefact_id):
        '''
        Consulta los conceptos de la prefactura en dbms
        '''
        SQL = """SELECT upper(inv_prod.sku) as sku,
            upper(inv_prod.descripcion) as descripcion,
            upper(inv_prod_unidades.titulo) AS unidad,
            erp_prefacturas_detalles.cant_facturar AS cantidad,
            erp_prefacturas_detalles.precio_unitario,
            (
              erp_prefacturas_detalles.cant_facturar * erp_prefacturas_detalles.precio_unitario
            ) AS importe,
            -- From this point onwards tax related columns
            (
              (erp_prefacturas_detalles.cant_facturar * erp_prefacturas_detalles.precio_unitario) *
              erp_prefacturas_detalles.valor_ieps
            ) AS importe_ieps,
            (
              (erp_prefacturas_detalles.cant_facturar * erp_prefacturas_detalles.precio_unitario) *
              erp_prefacturas_detalles.tasa_ret
            ) AS importe_retencion,
            (
              (
                (erp_prefacturas_detalles.cant_facturar * erp_prefacturas_detalles.precio_unitario) +
                (
                  (erp_prefacturas_detalles.cant_facturar * erp_prefacturas_detalles.precio_unitario) *
                  erp_prefacturas_detalles.valor_ieps
                )
              ) * erp_prefacturas_detalles.valor_imp
            ) AS importe_impuesto,
            (erp_prefacturas_detalles.valor_ieps * 100::double precision) AS tasa_ieps,
            (erp_prefacturas_detalles.tasa_ret * 100::double precision) AS tasa_ret,
            (erp_prefacturas_detalles.valor_imp * 100::double precision) AS tasa_impuesto,
            erp_prefacturas_detalles.gral_ieps_id as ieps_id,
            erp_prefacturas_detalles.tipo_impuesto_id as impto_id
            FROM erp_prefacturas
            JOIN erp_prefacturas_detalles on erp_prefacturas_detalles.prefacturas_id=erp_prefacturas.id
            LEFT JOIN inv_prod on inv_prod.id = erp_prefacturas_detalles.producto_id
            LEFT JOIN inv_prod_unidades on inv_prod_unidades.id = erp_prefacturas_detalles.inv_prod_unidad_id
            WHERE erp_prefacturas_detalles.prefacturas_id="""
        rowset = []
        for row in self.pg_query(conn, "{0}{1}".format(SQL, prefact_id)):
            rowset.append({
                'SKU': row['sku'],
                'DESCRIPCION': row['descripcion'],
                'UNIDAD': row['unidad'],
                'CANTIDAD': row['cantidad'],
                'PRECIO_UNITARIO': row['precio_unitario'],
                'IMPORTE': row['importe'],
                # From this point onwards tax related elements
                'IMPORTE_IEPS': row['importe_ieps'],
                'IMPORTE_RETENCION': row['importe_retencion'],
                'IMPORTE_IMPUESTO' : row['importe_impuesto'],
                'TASA_IEPS': row['tasa_ieps'],
                'TASA_RETENCION': row['tasa_ret'],
                'TASA_IMPUESTO': row['tasa_impuesto'],
                'IEPS_ID': row['ieps_id'],
                'IMPUESTO_ID': row['impto_id']
            })
        return rowset

    def __calc_traslados(self, l_items, l_ieps, l_iva):
        """calcula los impuestos trasladados"""
        traslados = []

        for tax in l_iva:
            # next two variables shall get lastest value of loop
            # It's not me. It is the Noe approach :|
            impto_id = None
            tasa = None
            importe_sum = 0
            for item in l_items:
                if tax['ID'] == item['IMPUESTO_ID']:
                    impto_id = item['IMPUESTO_ID']
                    tasa = item['TASA_IMPUESTO']
                    importe_sum += item['IMPORTE_IMPUESTO']
            if impto_id > 0:
                traslados.append({
                    'impuesto': 'IVA',
                    'importe': importe_sum,
                    'tasa': tasa
                })

        for tax in l_ieps:
            # next two variables shall get lastest value of loop
            # It's not me. It is the Noe approach :|
            impto_id = None
            tasa = None

            importe_sum = 0
            for item in l_items:
                if tax['ID'] == item['IEPS_ID']:
                    impto_id = item['IEPS_ID']
                    tasa = item['TASA_IEPS']
                    importe_sum += item['IMPORTE_IEPS']
            if impto_id > 0:
                traslados.append({
                    'impuesto': 'IEPS',
                    'importe': importe_sum,
                    'tasa': tasa
                })
        return traslados

    def __q_ivas(self, conn):
        '''
        Consulta el total de IVA activos en dbms
        '''
        SQL = """SELECT id, descripcion AS titulo, iva_1 AS tasa
            FROM gral_imptos
            WHERE borrado_logico=false"""
        rowset = []
        for row in self.pg_query(conn, SQL):
            rowset.append({
                'ID' : row['id'],
                'DESC': row['titulo'],
                'TASA': row['tasa']
            })
        return rowset

    def __q_ieps(self, conn, usr_id):
        '''
        Consulta el total de lo IEPS activos en dbms
        '''
        SQL = """SELECT id, titulo, tasa
            FROM gral_ieps
            WHERE borrado_logico=false """
        rowset = []
        for row in self.pg_query(conn, SQL):
            rowset.append({
                'ID' : row['id'],
                'DESC': row['titulo'],
                'TASA': row['tasa']
            })
        return rowset

    def __q_cert_file(self, conn, usr_id):
        '''
        Consulta el certificado que usa el usuario en dbms
        '''
        SQL = """select fac_cfds_conf.archivo_certificado as cert_file
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc ON gral_usr_suc.gral_suc_id = SUC.id
            LEFT JOIN fac_cfds_conf ON fac_cfds_conf.gral_suc_id = SUC.id
            WHERE gral_usr_suc.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return row['cert_file']

    def data_acq(self, conn, d_rdirs, **kwargs):

        usr_id = kwargs.get('usr_id', None)
        prefact_id = kwargs.get('prefact_id', None)

        if usr_id is None:
            raise DocBuilderStepError("user id not fed")
        if prefact_id is None:
            raise DocBuilderStepError("prefact id not fed")

        ed = self.__q_emisor(conn, usr_id)
        cert_file = '{}/{}/{}'.format(
                d_rdirs['ssl'], ed['RFC'], self.__q_cert_file(conn, usr_id))

        certb64 = None
        with open(cert_file, 'rb') as f:
            content = f.read()
            certb64 = base64.b64encode(content).decode('ascii')

        return {
            'TIME_STAMP': '{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()),
            'CERT_B64': certb64,
            'EMISOR': ed,
            'NUMERO_CERTIFICADO': self.__q_no_certificado(conn, usr_id),
            'RECEPTOR': self.__q_receptor(conn, prefact_id),
            'MONEDA': self.__q_moneda(conn, prefact_id),
            'LUGAR_EXPEDICION': self.__q_lugar_expedicion(conn, usr_id),
            'CONCEPTOS': self.__q_conceptos(conn, prefact_id)
        }


    def format_wrt(self, output_file, dat):
        c = Comprobante()
        c.Version = '3.3'
        c.Folio = "test attribute" #optional
        c.Fecha = dat['TIME_STAMP']
        c.Sello = '__DIGITAL_SIGN_HERE__'
        c.FormaPago = "01" #optional
        c.NoCertificado = dat['NUMERO_CERTIFICADO']
        c.Certificado = dat['CERT_B64']
        c.SubTotal = "4180.0"
        c.Total = "4848.80"
        c.Moneda = dat['MONEDA']['ISO_4217']
        c.TipoCambio = dat['MONEDA']['TIPO_DE_CAMBIO'] #optional (requerido en ciertos casos)
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

        c.Conceptos = pyxb.BIND()
        for i in dat['CONCEPTOS']:
            c.Conceptos.append(pyxb.BIND(
                Cantidad = 1, #i['CANTIDAD'],
                ClaveUnidad='C81', # se deben usar las claves del catalogo sat sobre medidas estandarizadas
                ClaveProdServ='01010101', # se deben usar las claves del catalogo sat producto-servicios
                Descripcion=i['DESCRIPCION'],
                ValorUnitario = i['PRECIO_UNITARIO'],
                NoIdentificacion = i['SKU'], #opcional
                Importe='50' # #i['IMPORTE']
            ))

        writedom_cfdi(c.toDOM(), self.__MAKEUP_PROPOS, output_file)

    def data_rel(self, dat):
        pass
