from docmaker.gen import BuilderGen
from docmaker.error import DocBuilderStepError
from misc.numspatrans import numspatrans

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

import os


impt_class='FacPdf'


class FacPdf(BuilderGen):

    __CAPTIONS = {
        'SPA': {
            'TL_DOC_LANG': 'ESPAÑOL',
            'TL_DOC_NAME': 'FACTURA',
            'TL_DOC_DATE': 'FECHA Y HORA',
            'TL_DOC_OBS': 'OBSERVACIONES',
            'TL_CUST_NAME': 'CLIENTE',
            'TL_CUST_ADDR': 'DIRECCIÓN',
            'TL_CUST_ZIPC': 'C.P.',
            'TL_CUST_REG': 'R.F.C',
            'TL_CUST_NUM': 'NO. DE CLIENTE',
            'TL_ORDER_NUM': 'NO. DE ORDEN',
            'TL_BILL_CURR': 'MONEDA',
            'TL_BILL_EXC_RATE': 'TIPO DE CAMBIO',
            'TL_PAY_DATE': 'FECHA DE PAGO',
            'TL_SALE_MAN': 'AGENTE DE VENTAS',
            'TL_PAY_COND': 'CONDICIONES DE PAGO',
            'TL_ACC_NUM': 'NO. DE CUENTA',
            'TL_PAY_MET': 'METODO DE PAGO',
            'TL_PAY_WAY': 'FORMA DE PAGO',
            'TL_ART_SKU': 'CLAVE',
            'TL_ART_DES': 'DESCRIPCIÓN',
            'TL_ART_UNIT': 'UNIDAD',
            'TL_ART_QUAN': 'CANTIDAD',
            'TL_ART_UP': 'P. UNITARIO',
            'TL_ART_AMNT': 'IMPORTE',
            'TL_ART_SUBT': 'SUB-TOTAL',
            'TL_ART_TOTAL': 'TOTAL'
        },
        'ENG': {
            'TL_DOC_LANG': 'ENGLISH',
            'TL_DOC_NAME': 'INVOICE',
            'TL_DOC_DATE': 'DATE',
            'TL_DOC_OBS': 'OBS',
            'TL_CUST_NAME': 'CUSTOMER',
            'TL_CUST_ADDR': 'ADDRESS SOLD TO',
            'TL_CUST_ZIPC': 'ZIP CODE',
            'TL_CUST_REG': 'TAX ID',
            'TL_CUST_NUM': 'CUSTOMER #',
            'TL_ORDER_NUM': 'ORDER #',
            'TL_BILL_CURR': 'CURRENCY',
            'TL_BILL_EXC_RATE': 'EXCHANGE RATE',
            'TL_PAY_DATE': 'PAYMENT DATE',
            'TL_SALE_MAN': 'SALE REP',
            'TL_PAY_COND': 'PAYMENT TERMS',
            'TL_ACC_NUM': 'ACCOUNT #',
            'TL_PAY_MET': 'PAYMENT METHOD',
            'TL_PAY_WAY': 'TERMS',
            'TL_ART_SKU': 'SKU',
            'TL_ART_DES': 'DESCRIPTION',
            'TL_ART_UNIT': 'MEASURE',
            'TL_ART_QUAN': 'QUANTITY',
            'TL_ART_UP': 'UNIT PRICE',
            'TL_ART_AMNT': 'AMOUNT',
            'TL_ART_SUBT': 'SUBT',
            'TL_ART_TOTAL': 'TOTAL'
        }
    }

    def __init__(self, logger):
        super().__init__(logger)

    def __load_extra_info(self, conn, serie_folio, cap):

        __EXTRA_INF_SQL = """SELECT  fac_docs.orden_compra AS purchase_number,
            cxc_agen.nombre AS sales_man,
            cxc_clie_credias.descripcion AS payment_constraint,
            (CASE
                 WHEN fac_docs.fecha_vencimiento IS NULL THEN ''
                 ELSE to_char(fac_docs.fecha_vencimiento,'dd/mm/yyyy')
            END) AS payment_date,
            upper(gral_mon.descripcion) AS currency_name,
            gral_mon.descripcion_abr AS currency_abr,
            cxc_clie.numero_control AS customer_control_id,
            fac_docs.observaciones,
    		fac_docs.no_cuenta,
            (SELECT
                ARRAY(
                    SELECT leyenda FROM gral_emp_leyenda
                     WHERE gral_emp_id = cxc_clie.empresa_id
                ) as legends
            ),
            (SELECT
                ARRAY(
                    SELECT leyenda_eng FROM gral_emp_leyenda
                     WHERE gral_emp_id = cxc_clie.empresa_id
                ) as legends_eng
            )
            FROM fac_docs
            LEFT JOIN cxc_clie_credias ON cxc_clie_credias.id = fac_docs.terminos_id
            LEFT JOIN gral_mon on gral_mon.id = fac_docs.moneda_id
            JOIN cxc_agen ON cxc_agen.id =  fac_docs.cxc_agen_id
            JOIN cxc_clie ON fac_docs.cxc_clie_id = cxc_clie.id
            WHERE fac_docs.serie_folio="""
        for row in self.pg_query(conn, "{0}{1}".format(__EXTRA_INF_SQL, serie_folio)):
            # Just taking first row of query result
            return {
                'PURCHASE_NUMBER': row['purchase_number'] if row['purchase_number'] else 'N/D',
                'CUSTOMER_CONTROL_ID': row['customer_control_id'],
                'PAYMENT_CONSTRAINT': row['payment_constraint'],
                'SALES_MAN': row['sales_man'],
                'PAYMENT_DATE': row['payment_date'],
                'CURRENCY_ABR': row['currency_abr'],
                'CURRENCY_NAME': row['currency_name'],
                'NO_CUENTA': row['no_cuenta'],
                'OBSERVACIONES': row['observaciones'],
                'BILL_LEGENDS': row['legends'] if cap == 'SPA' else row['legends_eng']
            }

    def data_acq(self, conn, d_rdirs, **kwargs):

        def fetch_info(f, xslt):
            parser = CfdiReader()
            try:
                return parser(f) , __apply_xslt(f, xslt)
            except xml.sax.SAXParseException as e:
                raise DocBuilderStepError("cfdi xml could not be parsed : {}".format(e))
            except Exception as e:
                raise DocBuilderStepError("xsl could not be applied : {}".format(e)

        def extra(serie_folio, c):
            try:
                return self.__load_extra_info(conn, serie_folio, c)
            except Exception as e:
                raise DocBuilderStepError("loading extra info fails: {}".format(e))

        xml = kwargs.get('xml', None)
        if xml is None:
            raise DocBuilderStepError("xml not found")
        f_xml = os.path.join(d_rdirs['cfdi_output'], ed['RFC'], xml)
        if not os.path.isfile(f_xml):
            raise DocBuilderStepError("cfdi xml not found")

        cap = kwargs.get('cap', 'SPA')
        if not cap in self.__CAPTIONS:
            raise DocBuilderStepError("caption {0} not found".format(cap))

        logo_filename = os.path.join(d_rdirs['images'], "{}_logo.png".format(ed['RFC']))
        if not os.path.isfile(logo_filename):
            raise DocBuilderStepError("logo image {0} not found".format(logo_filename))

        cedula_filename = os.path.join(d_rdirs['images'], "{}_cedula.png".format(ed['rfc'])
        if not os.path.isfile(cedula_filename):
            raise DocBuilderStepError("cedula image {0} not found".format(cedula_filename))

        xml_parsed, original = fetch_info(f_xml, xslt)

        return {
            'CAP_LOADED': self.__CAPTIONS[cap],
            'LOGO': logo_filename,
            'CEDULA': cedula_filename,
            'STAMP_ORIGINAL_STR': original,
            'XML_PARSED': xml_parsed,
            'CUSTOMER_WWW':'www.saar.com.mx',
            'CUSTOMER_PHONE':'83848025,8384-8085, 8384-8028',
            'FOOTER_ABOUT': "ESTE DOCUMENTO ES UNA REPRESENTACIÓN IMPRESA DE UN CFDI",
            'EXTRA_INFO': extra("%s%s" % (xml_parsed['CFDI_SERIE'], xml_parsed['CFDI_FOLIO']), cap)
        }


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        width, height = letter
        self.setFont("Helvetica", 7)
        self.drawCentredString(width / 2.0, 0.65*cm,
            "Pagina %d de %d" % (self._pageNumber, page_count))