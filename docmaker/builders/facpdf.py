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

import misc.helperxml as xmltricks
import misc.helperstr as strtricks
import sat.reader as xmlreader
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
            parser = xmlreader.SaxReader()
            try:
                return parser(f) , xmltricks.HelperXml.run_xslt(f, xslt)
            except xml.sax.SAXParseException as e:
                raise DocBuilderStepError("cfdi xml could not be parsed : {}".format(e))
            except Exception as e:
                raise DocBuilderStepError("xsl could not be applied : {}".format(e))

        def extra(serie_folio, c):
            try:
                return self.__load_extra_info(conn, serie_folio, c)
            except Exception as e:
                raise DocBuilderStepError("loading extra info fails: {}".format(e))

        rfc = kwargs.get('rfc', None)
        if rfc is None:
            raise DocBuilderStepError("rfc not found")

        xml = kwargs.get('xml', None)
        if xml is None:
            raise DocBuilderStepError("xml not found")
        f_xml = os.path.join(d_rdirs['cfdi_output'], rfc, xml)
        if not os.path.isfile(f_xml):
            raise DocBuilderStepError("cfdi xml not found")

        cap = kwargs.get('cap', 'SPA')
        if not cap in self.__CAPTIONS:
            raise DocBuilderStepError("caption {0} not found".format(cap))

        logo_filename = os.path.join(d_rdirs['images'], "{}_logo.png".format(rfc))
        if not os.path.isfile(logo_filename):
            raise DocBuilderStepError("logo image {0} not found".format(logo_filename))

        cedula_filename = os.path.join(d_rdirs['images'], "{}_cedula.png".format(rfc))
        if not os.path.isfile(cedula_filename):
            raise DocBuilderStepError("cedula image {0} not found".format(cedula_filename))

        f_xslt = os.path.join(
            os.path.join(d_rdirs['cfdi_xslt'], rfc),
            'cadena_original_timbre.xslt'
        )
        if not os.path.isfile(f_xslt):
            raise DocBuilderStepError("cadena_original_timbre.xslt not found")

        xml_parsed, original = fetch_info(f_xml, f_xslt)

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

    def format_wrt(self, output_file, dat):
        self.logger.debug('dumping contents of dat: {}'.format(repr(dat)))

        doc = BaseDocTemplate(output_file, pagesize=letter,
            rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18,)
        story = []
        logo = Image(dat['LOGO'])
        logo.drawHeight = 3.8*cm
        logo.drawWidth = 5.2*cm

        cedula = Image(dat['CEDULA'])
        cedula.drawHeight = 3.2*cm
        cedula.drawWidth = 3.2*cm

        story.append(self.__top_table(logo, dat))
        story.append(Spacer(1, 0.4 * cm))
        story.append(self.__customer_table(dat))
        story.append(Spacer(1, 0.4 * cm))
        story.append(self.__items_section(dat))
        story.append(self.__amount_section(dat))
        story.append(Spacer(1, 0.45 * cm))

        def fp_foot(c, d):
            c.saveState()
            width, height = letter
            c.setFont('Helvetica', 7)
            c.drawCentredString(width / 2.0, (1.00 * cm), dat['FOOTER_ABOUT'])
            c.restoreState()

        bill_frame = Frame(
            doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
            id='bill_frame'
        )

        doc.addPageTemplates(
            [
                PageTemplate(id='biil_page', frames=[bill_frame], onPage=fp_foot),
            ]
        )
        doc.build(story, canvasmaker=NumberedCanvas)
        return

    def __amount_section(self, dat):

        def letra_section():
            c = [[''], ["IMPORTE CON LETRA"]]
            (c, d) = dat['XML_PARSED']['CFDI_TOTAL'].split('.')
            n = numspatrans(c)
            result = "{0} {1} {2}/100 {3}".format(
                n.upper(),
                dat['EXTRA_INFO']['CURRENCY_NAME'],
                d,
                dat['EXTRA_INFO']['CURRENCY_ABR']
            )
            # substitute multiple whitespace with single whitespace
            c.append([' '.join(result.split())])
            table_letra = Table(c,
                [
                    12.3 * cm  # rowWitdhs
                ],
                [0.4 * cm] * len(c)  # rowHeights
            )
            table_letra.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONT', (0, 1), (-1, 1), 'Helvetica-Bold', 7),
                ('FONT', (0, 2), (-1, 2), 'Helvetica', 7),
            ]))
            return table_letra

        def total_section():
            cont = [
                [
                    dat['CAP_LOADED']['TL_ART_SUBT'],
                    dat['EXTRA_INFO']['CURRENCY_ABR'],
                    strtricks.HelperStr.format_currency(dat['XML_PARSED']['CFDI_SUBTOTAL'])
                ]
            ]

            for imptras in dat['XML_PARSED']['TAXES']['TRAS']['DETAILS']:
                (tasa, _) = imptras['TASA'].split('.')

                row = [
                    "{0} {1}%".format(
                        'TAX' if dat['CAP_LOADED']['TL_DOC_LANG'] == 'ENGLISH' else imptras['IMPUESTO'],
                        tasa
                    ),
                    dat['EXTRA_INFO']['CURRENCY_ABR'],
                    strtricks.HelperStr.format_currency(imptras['IMPORTE'])
                ]
                cont.append(row)

            cont.append([
                dat['CAP_LOADED']['TL_ART_TOTAL'], dat['EXTRA_INFO']['CURRENCY_ABR'],
                strtricks.HelperStr.format_currency(dat['XML_PARSED']['CFDI_TOTAL'])
            ])
            table_total = Table(cont,
                [
                    3.8 * cm,
                    1.28 * cm,
                    2.5 * cm  # rowWitdhs
                ],
                [0.4 * cm] * len(cont)  # rowHeights
            )
            table_total.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),

                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 7),

                ('BOX', (1, 0), (2, -1), 0.25, colors.black),

                ('FONT', (1, 0), (1, 1), 'Helvetica', 7),
                ('FONT', (1, 2), (1, 2), 'Helvetica-Bold', 7),
                ('FONT', (-1, 0), (-1, -1), 'Helvetica-Bold', 7),
            ]))
            return table_total

        cont = [[letra_section(), total_section()]]
        table = Table(cont,
            [
               12.4 * cm,
               8 * cm
            ],
            [1.31 * cm] * len(cont)  # rowHeights
        )
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
        ]))
        return table

    def __items_section(self, dat):
        add_currency_simbol = lambda c: '${0:>40}'.format(c)

        st = ParagraphStyle(
            name='info',
            fontName='Helvetica',
            fontSize=7,
            leading=8
        )
        header_concepts = (
            dat['CAP_LOADED']['TL_ART_SKU'], dat['CAP_LOADED']['TL_ART_DES'],
            dat['CAP_LOADED']['TL_ART_UNIT'], dat['CAP_LOADED']['TL_ART_QUAN'],
            dat['CAP_LOADED']['TL_ART_UP'], dat['CAP_LOADED']['TL_ART_AMNT']
        )

        cont_concepts = []
        for i in dat['XML_PARSED']['ARTIFACTS']:
            row = [
                i['NOIDENTIFICACION'],
                Paragraph(i['DESCRIPCION'], st),
                i['UNIDAD'].upper(),
                strtricks.HelperStr.format_currency(i['CANTIDAD']),
                add_currency_simbol(strtricks.HelperStr.format_currency(i['VALORUNITARIO'])),
                add_currency_simbol(strtricks.HelperStr.format_currency(i['IMPORTE']))
            ]
            cont_concepts.append(row)

        cont = [header_concepts] + cont_concepts

        table = Table(cont,
            [
                2.2 * cm,
                5.6 * cm,
                2.3 * cm,
                2.3 * cm,
                3.8 * cm,
                3.8 * cm
            ]
        )

        table.setStyle( TableStyle([
            #Body and header look and feel (common)
            ('ALIGN', (0,0),(-1,0), 'CENTER'),
            ('VALIGN', (0,0),(-1,-1), 'TOP'),
            ('BOX', (0, 0), (-1, 0), 0.25, colors.black),
            ('BACKGROUND', (0,0),(-1,0), colors.black),
            ('TEXTCOLOR', (0,0),(-1,0), colors.white),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 7),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 7),
            ('ROWBACKGROUNDS', (0, 1),(-1, -1), [colors.white, colors.sandybrown]),
            ('ALIGN', (0, 1),(1, -1), 'LEFT'),
            ('ALIGN', (2, 0),(2, -1), 'CENTER'),
            ('ALIGN', (3, 1),(-1, -1), 'RIGHT'),

            #Clave column look and feel (specific)
            ('BOX', (0, 1), (0, -1), 0.25, colors.black),

            #Description column look and feel (specific)
            ('BOX', (1, 1), (1, -1), 0.25, colors.black),

            #Unit column look and feel (specific)
            ('BOX', (2, 1), (2, -1), 0.25, colors.black),

            #Amount column look and feel (specific)
            ('BOX', (3, 1),(3, -1), 0.25, colors.black),

            #Amount column look and feel (specific)
            ('BOX', (4, 1),(4, -1), 0.25, colors.black),

            #Amount column look and feel (specific)
            ('BOX', (5, 1),(5, -1), 0.25, colors.black),

            #Amount column look and feel (specific)
            ('BOX', (6, 1),(6, -1), 0.25, colors.black),

            #Amount column look and feel (specific)
            ('BOX', (7, 1),(7, -1), 0.25, colors.black),
        ]))
        return table

    def __customer_table(self, dat):

        def customer_sec():
            c = []
            c.append([ dat['CAP_LOADED']['TL_CUST_NAME'] ])
            c.append([ dat['XML_PARSED']['RECEPTOR_NAME'].upper() ])
            c.append([ dat['CAP_LOADED']['TL_CUST_REG'] ] )
            c.append([ dat['XML_PARSED']['RECEPTOR_RFC'].upper() ])
            c.append([ dat['CAP_LOADED']['TL_CUST_ADDR'] ])
            c.append([ (
                "{0} {1}".format(
                    dat['XML_PARSED']['RECEPTOR_STREET'],
                    dat['XML_PARSED']['RECEPTOR_STREET_NUMBER']
            )).upper() ])
            c.append([ dat['XML_PARSED']['RECEPTOR_SETTLEMENT'].upper() ])
            c.append([ "{0}, {1}".format(
                dat['XML_PARSED']['RECEPTOR_TOWN'],
                dat['XML_PARSED']['RECEPTOR_STATE']
            ).upper()])
            c.append([ dat['XML_PARSED']['RECEPTOR_COUNTRY'].upper() ])
            c.append([ "%s %s" % ( dat['CAP_LOADED']['TL_CUST_ZIPC'], dat['XML_PARSED']['RECEPTOR_CP']) ])
            t = Table(c,
                [
                    8.6 * cm   # rowWitdhs
                ],
                [0.35*cm] * 10 # rowHeights
            )
            t.setStyle(TableStyle([
                # Body and header look and feel (common)
                ('ROWBACKGROUNDS', (0, 0), (-1, 4), [colors.sandybrown, colors.white]),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 7),
                ('FONT', (0, 1), (-1, 1), 'Helvetica', 7),
                ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold', 7),
                ('FONT', (0, 3), (-1, 3), 'Helvetica', 7),
                ('FONT', (0, 4), (-1, 4), 'Helvetica-Bold', 7),
                ('FONT', (0, 5), (-1, 9), 'Helvetica', 7),
            ]))
            return t

        def addons():
            c = []
            c.append([dat['CAP_LOADED']['TL_CUST_NUM'], dat['CAP_LOADED']['TL_PAY_MET']])
            c.append([dat['EXTRA_INFO']['CUSTOMER_CONTROL_ID'], dat['XML_PARSED']['METODO_PAGO']])
            c.append([dat['CAP_LOADED']['TL_ORDER_NUM'], dat['CAP_LOADED']['TL_PAY_COND']])
            c.append([dat['EXTRA_INFO']['PURCHASE_NUMBER'], dat['EXTRA_INFO']['PAYMENT_CONSTRAINT']])
            c.append([dat['CAP_LOADED']['TL_BILL_CURR'], dat['CAP_LOADED']['TL_PAY_WAY']])
            c.append([dat['EXTRA_INFO']['CURRENCY_ABR'], dat['XML_PARSED']['FORMA_PAGO']])
            c.append([dat['CAP_LOADED']['TL_BILL_EXC_RATE'], dat['CAP_LOADED']['TL_ACC_NUM']])
            c.append([dat['XML_PARSED']['MONEY_EXCHANGE'], dat['EXTRA_INFO']['NO_CUENTA']])
            c.append([dat['CAP_LOADED']['TL_PAY_DATE'], dat['CAP_LOADED']['TL_SALE_MAN']])
            c.append([dat['EXTRA_INFO']['PAYMENT_DATE'], dat['EXTRA_INFO']['SALES_MAN']])
            t = Table(c,
                [
                    4.0 * cm,
                    7.0 * cm  # rowWitdhs
                ],
                [0.35 * cm] * 10  # rowHeights
            )
            t.setStyle(TableStyle([
                # Body and header look and feel (common)
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 7),
                ('FONT', (0, 1), (-1, 1), 'Helvetica', 7),
                ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold', 7),
                ('FONT', (0, 3), (-1, 3), 'Helvetica', 7),
                ('FONT', (0, 4), (-1, 4), 'Helvetica-Bold', 7),
                ('FONT', (0, 5), (-1, 5), 'Helvetica', 7),
                ('FONT', (0, 6), (-1, 6), 'Helvetica-Bold', 7),
                ('FONT', (0, 7), (-1, 7), 'Helvetica', 7),
                ('FONT', (0, 8), (-1, 8), 'Helvetica-Bold', 7),
                ('FONT', (0, 9), (-1, 9), 'Helvetica', 7),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.sandybrown, colors.white]),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ]))
            return t

        table = Table([[customer_sec(), addons()]], [
            8.4 * cm,
            12 * cm
        ])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
        ]))
        return table

    def __top_table(self, logo, dat):

        def create_emisor_table():
            st = ParagraphStyle(
                name='info',
                fontName='Helvetica',
                fontSize=7,
                leading=9.7
            )
            context = dict(
                inceptor=dat['XML_PARSED']['INCEPTOR_NAME'], rfc=dat['XML_PARSED']['INCEPTOR_RFC'],
                phone=dat['CUSTOMER_PHONE'], www=dat['CUSTOMER_WWW'],
                street=dat['XML_PARSED']['INCEPTOR_STREET'],
                number=dat['XML_PARSED']['INCEPTOR_STREET_NUMBER'],
                settlement=dat['XML_PARSED']['INCEPTOR_SETTLEMENT'],
                state=dat['XML_PARSED']['INCEPTOR_STATE'].upper(),
                town=dat['XML_PARSED']['INCEPTOR_TOWN'].upper(), cp=dat['XML_PARSED']['INCEPTOR_CP'].upper(),
                regimen=dat['XML_PARSED']['INCEPTOR_REGIMEN'].upper(),
                op=dat['XML_PARSED']['CFDI_ORIGIN_PLACE'].upper(), fontSize='7', fontName='Helvetica'
            )
            text = Paragraph(
                '''
                <para align=center spaceb=3>
                    <font name=%(fontName)s size=10 >
                        <b>%(inceptor)s</b>
                    </font>
                    <br/>
                    <font name=%(fontName)s size=%(fontSize)s >
                        <b>RFC: %(rfc)s</b>
                    </font>
                    <br/>
                    <font name=%(fontName)s size=%(fontSize)s >
                        <b>DOMICILIO FISCAL</b>
                    </font>
                    <br/>
                    %(street)s %(number)s %(settlement)s
                    <br/>
                    %(town)s, %(state)s C.P. %(cp)s
                    <br/>
                    TEL./FAX. %(phone)s
                    <br/>
                    %(www)s
                    <br/>
                    %(regimen)s
                    <br/><br/>
                    <b>LUGAR DE EXPEDICIÓN</b>
                    <br/>
                    %(op)s
                </para>
                ''' % context, st
            )
            t = Table([[text]], colWidths = [ 9.0 *cm])
            t.setStyle(TableStyle([('VALIGN',(-1,-1),(-1,-1),'TOP')]))
            return t

        def create_factura_table():
            st = ParagraphStyle(
                name='info',
                fontName='Helvetica',
                fontSize=7,
                leading=8
            )
            serie_folio = "%s%s" % (
                dat['XML_PARSED']['CFDI_SERIE'],
                dat['XML_PARSED']['CFDI_FOLIO']
            )

            cont = []
            cont.append([dat['CAP_LOADED']['TL_DOC_NAME']])
            cont.append(['No.'])
            cont.append([serie_folio])
            cont.append([dat['CAP_LOADED']['TL_DOC_DATE']])
            cont.append([dat['XML_PARSED']['CFDI_DATE']])
            cont.append(['FOLIO FISCAL'])
            cont.append([Paragraph(dat['XML_PARSED']['UUID'], st)])
            cont.append(['NO. CERTIFICADO'])
            cont.append([dat['XML_PARSED']['CFDI_CERT_NUMBER']])

            t = Table(cont,
                [
                    5  * cm,
                ],
                [
                    0.40 * cm,
                    0.37* cm,
                    0.37 * cm,
                    0.38 * cm,
                    0.38 * cm,
                    0.38 * cm,
                    0.70 * cm,
                    0.38 * cm,
                    0.38 * cm,
                ] # rowHeights
            )
            t.setStyle(TableStyle([
                # Body and header look and feel (common)
                ('BOX', (0, 1), (-1, -1), 0.25, colors.black),
                ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 10),

                ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
                ('FONT', (0, 1), (-1, 2), 'Helvetica-Bold', 7),

                ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
                ('FONT', (0, 3), (-1, 3), 'Helvetica-Bold', 7),
                ('FONT', (0, 4), (-1, 4), 'Helvetica', 7),

                ('TEXTCOLOR', (0, 5), (-1, 5), colors.white),
                ('FONT', (0, 5), (-1, 5), 'Helvetica-Bold', 7),

                ('FONT', (0, 7), (-1, 7), 'Helvetica-Bold', 7),
                ('TEXTCOLOR', (0, 7), (-1, 7), colors.white),
                ('FONT', (0, 8), (-1, 8), 'Helvetica', 7),

                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.black, colors.white]),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ]))
            return t

        et = create_emisor_table()
        ft = create_factura_table()
        cont = [[logo, et, ft]]
        table = Table(cont,
           [
               5.5 * cm,
               9.4 * cm,
               5.5 * cm
           ]
        )
        table.setStyle( TableStyle([
            ('ALIGN', (0, 0),(0, 0), 'LEFT'),
            ('ALIGN', (1, 0),(1, 0), 'CENTRE'),
            ('ALIGN', (-1, 0),(-1, 0), 'RIGHT'),
        ]))
        return table


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
