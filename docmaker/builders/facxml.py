import math
import os
import base64
import datetime
import tempfile
import pyxb
from misc.helperstr import HelperStr
from docmaker.error import DocBuilderStepError
from misc.tricks import truncate
from docmaker.gen import BuilderGen
from sat.v33 import Comprobante
from sat.requirement import writedom_cfdi, sign_cfdi
from sat.artifacts import CfdiType


impt_class='FacXml'


class FacXml(BuilderGen):

    __MAKEUP_PROPOS = CfdiType.FAC

    def __init__(self, logger):
        super().__init__(logger)

    def __q_no_certificado(self, conn, usr_id):
        """
        Consulta el numero de certificado en dbms
        """
        SQL =  """select CFDI_CONF.numero_certificado
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc AS USR_SUC ON USR_SUC.gral_suc_id = SUC.id
            LEFT JOIN fac_cfds_conf AS CFDI_CONF ON CFDI_CONF.gral_suc_id = SUC.id
            WHERE USR_SUC.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return row['numero_certificado']
        
    def __q_serie_folio(self, conn, usr_id):
        """
        Consulta la serie y folio a usar en dbms
        """
        SQL = """select fac_cfds_conf_folios.serie as serie,
            fac_cfds_conf_folios.folio_actual::character varying as folio
            FROM gral_suc AS SUC
            LEFT JOIN fac_cfds_conf ON fac_cfds_conf.gral_suc_id = SUC.id
            LEFT JOIN fac_cfds_conf_folios ON fac_cfds_conf_folios.fac_cfds_conf_id = fac_cfds_conf.id
            LEFT JOIN gral_usr_suc AS USR_SUC ON USR_SUC.gral_suc_id = SUC.id
            WHERE fac_cfds_conf_folios.proposito = 'FAC'
            AND USR_SUC.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return {
                'SERIE': row['serie'],
                'FOLIO': row['folio']
            }
        
    def __q_emisor(self, conn, usr_id):
        """
        Consulta el emisor en dbms
        """
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
        """
        Consulta el lugar de expedicion en dbms
        """
        SQL = """select SUC.cp
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc as USR_SUC ON USR_SUC.gral_suc_id=SUC.id
            WHERE USR_SUC.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return row['cp']

    def __q_moneda(self, conn, prefact_id):
        """
        Consulta la moneda de la prefactura en dbms
        """
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
        """
        Consulta el cliente de la prefactura en dbms
        """
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
        """
        Consulta los conceptos de la prefactura en dbms
        """
        SQL = """SELECT upper(inv_prod.sku) as sku,
            upper(inv_prod.descripcion) as descripcion,
            cfdi_claveprodserv.clave AS prodserv,
            cfdi_claveunidad.clave AS unidad,
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
            LEFT JOIN inv_prod_tipos on inv_prod_tipos.id = inv_prod.tipo_de_producto_id
            LEFT JOIN cfdi_claveunidad on inv_prod_unidades.cfdi_unidad_id = cfdi_claveunidad.id
            LEFT JOIN cfdi_claveprodserv on inv_prod_tipos.cfdi_prodserv_id = cfdi_claveprodserv.id
            WHERE erp_prefacturas_detalles.prefacturas_id="""
        rowset = []
        for row in self.pg_query(conn, "{0}{1}".format(SQL, prefact_id)):
            rowset.append({
                'SKU': row['sku'],
                'DESCRIPCION': row['descripcion'],
                'UNIDAD': row['unidad'],
                'PRODSERV': row['prodserv'],
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

    def __calc_totales(self, l_items):
        totales = {
            'MONTO_TOTAL': 0,
            'MONTO_RETENCION': 0,
            'IMPORTE_SUM': 0,
            'IMPORTE_SUM_IMPUESTO': 0,
            'IMPORTE_SUM_IEPS': 0,
            'IMPORTE_SUM_RETENCION': 0,
            'TASA_RETENCION': 0
        }

        for item in l_items:
            totales['IMPORTE_SUM'] += (item['IMPORTE'])
            totales['IMPORTE_SUM_IEPS'] += (item['IMPORTE_IEPS'])
            totales['IMPORTE_SUM_IMPUESTO'] += (item['IMPORTE_IMPUESTO'])
            totales['TASA_RETENCION'] = item['TASA_RETENCION']
            totales['IMPORTE_SUM_RETENCION'] += (item['IMPORTE_RETENCION'])

        totales['MONTO_RETENCION'] = totales['IMPORTE_SUM'] * totales['TASA_RETENCION']
        totales['MONTO_TOTAL'] = totales['IMPORTE_SUM'] + totales['IMPORTE_SUM_IEPS'] + totales['IMPORTE_SUM_IMPUESTO'] - totales['MONTO_RETENCION']

        # Sumar el acumulado de retencion de las partidas
        totales['MONTO_RETENCION'] += totales['IMPORTE_SUM_RETENCION']
        return totales

    def __calc_traslados(self, l_items, l_ieps, l_iva):
        """
        Calcula los impuestos trasladados
        """
        traslados = []

        for tax in l_iva:
            # next two variables shall get lastest value of loop
            # It's not me. It is the Noe approach :|
            impto_id = 0
            tasa = 0
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
            impto_id = 0
            tasa = 0
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
        """
        Consulta el total de IVA activos en dbms
        """
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
        """
        Consulta el total de lo IEPS activos en dbms
        """
        SQL = """SELECT gral_ieps.id as id,
            gral_ieps.titulo as desc, gral_ieps.tasa as tasa
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc AS USR_SUC ON USR_SUC.gral_suc_id = SUC.id
            LEFT JOIN gral_emp AS EMP ON EMP.id = SUC.empresa_id
            LEFT JOIN gral_ieps ON gral_ieps.gral_emp_id = EMP.id
            WHERE gral_ieps.borrado_logico=false AND
            USR_SUC.gral_usr_id="""
        rowset = []
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            rowset.append({
                'ID' : row['id'],
                'DESC': row['desc'],
                'TASA': row['tasa']
            })
        return rowset

    def __q_sign_params(self, conn, usr_id):
        """
        Consulta parametros requeridos para firmado cfdi
        """
        SQL = """SELECT fac_cfds_conf.password_llave as passwd,
            fac_cfds_conf.archivo_llave as pk,
            fac_cfds_conf.archivo_xsl as xslt
            FROM gral_suc AS SUC
            LEFT JOIN gral_usr_suc AS USR_SUC ON USR_SUC.gral_suc_id = SUC.id
            LEFT JOIN fac_cfds_conf ON fac_cfds_conf.gral_suc_id = SUC.id
            WHERE USR_SUC.gral_usr_id="""
        for row in self.pg_query(conn, "{0}{1}".format(SQL, usr_id)):
            # Just taking first row of query result
            return {
                'PKNAME': row['pk'],
                'PKPASSWD': row['passwd'],
                'XSLTNAME': row['xslt']
            }

    def __q_cert_file(self, conn, usr_id):
        """
        Consulta el certificado que usa el usuario en dbms
        """
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
        sp = self.__q_sign_params(conn, usr_id)

        # dirs with full emisor rfc path
        sslrfc_dir = os.path.join(d_rdirs['ssl'], ed['RFC'])
        xsltrfc_dir = os.path.join(d_rdirs['cfdi_xslt'], ed['RFC'])

        cert_file = os.path.join(
                       sslrfc_dir, self.__q_cert_file(conn, usr_id))
        certb64 = None
        with open(cert_file, 'rb') as f:
            content = f.read()
            certb64 = base64.b64encode(content).decode('ascii')

        conceptos = self.__q_conceptos(conn, prefact_id)

        sp['PKNAME'] = sp['PKNAME'].replace('.key', '.pem')  # workaround to test
        sp['XSLTNAME'] = "cadenaoriginal_3_3.xslt"  # workaround to test

        return {
            'TIME_STAMP': '{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()),
            'CONTROL': self.__q_serie_folio(conn, usr_id),
            'CERT_B64': certb64,
            'KEY_PRIVATE': os.path.join(sslrfc_dir, sp['PKNAME']),
            'XSLT_SCRIPT': os.path.join(xsltrfc_dir, sp['XSLTNAME']),
            'EMISOR': ed,
            'NUMERO_CERTIFICADO': self.__q_no_certificado(conn, usr_id),
            'RECEPTOR': self.__q_receptor(conn, prefact_id),
            'MONEDA': self.__q_moneda(conn, prefact_id),
            'LUGAR_EXPEDICION': self.__q_lugar_expedicion(conn, usr_id),
            'CONCEPTOS': conceptos,
            'TOTALES': self.__calc_totales(conceptos)
        }

    def format_wrt(self, output_file, dat):
        self.logger.debug('dumping contents of dat: {}'.format(repr(dat)))

        def save(xo):
            tmp_dir = tempfile.gettempdir()
            f = os.path.join(tmp_dir, HelperStr.random_str())
            writedom_cfdi(xo.toDOM(), self.__MAKEUP_PROPOS, f)
            return f

        def trunc(m):
            return truncate(m, 2)

        c = Comprobante()
        c.Version = '3.3'
        c.Serie = dat['CONTROL']['SERIE']  # optional
        c.Folio = dat['CONTROL']['FOLIO']  # optional
        c.Fecha = dat['TIME_STAMP']
        c.Sello = '__DIGITAL_SIGN_HERE__'
        c.FormaPago = "01"  # optional
        c.NoCertificado = dat['NUMERO_CERTIFICADO']
        c.Certificado = dat['CERT_B64']
        c.SubTotal = dat['TOTALES']['IMPORTE_SUM']
        c.Total = dat['TOTALES']['MONTO_TOTAL']
        if dat['MONEDA']['ISO_4217'] == 'MXN':
            c.TipoCambio = 1
        else:
            c.TipoCambio = trunc(dat['MONEDA']['TIPO_DE_CAMBIO'])  # optional (requerido en ciertos casos)
        c.Moneda = dat['MONEDA']['ISO_4217']
        c.TipoDeComprobante = 'I'
        c.MetodoPago = "PUE"  # optional and hardcode until ui can suply such value
        c.LugarExpedicion = dat['LUGAR_EXPEDICION']

        c.Emisor = pyxb.BIND()
        c.Emisor.Nombre = dat['EMISOR']['RAZON_SOCIAL']  # optional
        c.Emisor.Rfc = dat['EMISOR']['RFC']
        c.Emisor.RegimenFiscal = dat['EMISOR']['REGIMEN_FISCAL']

        c.Receptor = pyxb.BIND()
        c.Receptor.Nombre = dat['RECEPTOR']['RAZON_SOCIAL']  # optional
        c.Receptor.Rfc = dat['RECEPTOR']['RFC']
        c.Receptor.UsoCFDI = dat['RECEPTOR']['USO_CFDI']

        c.Conceptos = pyxb.BIND()
        for i in dat['CONCEPTOS']:
            c.Conceptos.append(pyxb.BIND(
                Cantidad=i['CANTIDAD'],
                ClaveUnidad=i['UNIDAD'],
                ClaveProdServ=i['PRODSERV'],
                Descripcion=i['DESCRIPCION'],
                ValorUnitario=i['PRECIO_UNITARIO'],
                NoIdentificacion=i['SKU'],  # optional
                Importe=i['IMPORTE'],
                Impuestos=self.__tag_impuestos(i)
            ))

        tmp_file = save(c)
        with open(output_file, 'w') as a:
            a.write(sign_cfdi(dat['KEY_PRIVATE'], dat['XSLT_SCRIPT'], tmp_file))
        os.remove(tmp_file)

    def data_rel(self, dat):
        pass

    def __place_tasa(self, x):
        """
        smart method to deal with a tasa less
        than zero or greater than zero
        """
        try:
            return x * 10 ** -2 if math.log10(x) >= 0 else x
        except ValueError:
            # Silent the error and just return value passed
            return x

    def __tag_traslados(self, i):

        def traslado(b, c, tc, imp):
            return pyxb.BIND(
                Base=b, TipoFactor='Tasa',
                Impuesto=c, TasaOCuota=tc, Importe=imp)

        taxes = []
        if i['IMPORTE_IMPUESTO'] > 0:
            taxes.append(traslado(i['IMPORTE'], "002", self.__place_tasa(i['TASA_IMPUESTO']), i['IMPORTE_IMPUESTO']))
        if i['IMPORTE_IEPS'] > 0:
            taxes.append(traslado(i['IMPORTE'], "003", self.__place_tasa(i['TASA_IEPS']), i['IMPORTE_IEPS']))
        return pyxb.BIND(*tuple(taxes))

    def __tag_retenciones(self, i):

        def retencion(b, c, tc, imp):
            return pyxb.BIND(
                Base=b, TipoFactor='Tasa',
                Impuesto=c, TasaOCuota=tc, Importe=imp)

        return pyxb.BIND(*tuple([
            retencion(i['IMPORTE'], "001", self.__place_tasa(i['TASA_RETENCION']), i['IMPORTE_RETENCION'])
        ]))

    def __tag_impuestos(self, i):

        notaxes = True
        kwargs = {}
        if i['IMPORTE_IMPUESTO'] > 0 or i['IMPORTE_IEPS'] > 0:
            notaxes = False
            kwargs['Traslados'] = self.__tag_traslados(i)
        if i['IMPORTE_RETENCION'] > 0:
            notaxes = False
            kwargs['Retenciones'] = self.__tag_retenciones(i)

        return pyxb.BIND() if notaxes else pyxb.BIND(**kwargs)
