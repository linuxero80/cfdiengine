from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

class CommonBill(BuilderGen):

    def __init__(self, logger):
        super().__(logger)

    def __top_table(self, t0, t1, t3):
        cont = [[t0, t1, t3]]
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

    def __create_emisor_table(self, dat):
        st = ParagraphStyle(
            name='info',
            fontName='Helvetica',
            fontSize=7,
            leading = 9.7 
        )

        context = {
            'inceptor': dat['INCEPTOR_NAME'],
            'rfc': dat['INCEPTOR_RFC'],
            'phone': dat['CUSTOMER_PHONE'],
            'www': dat['CUSTOMER_WWW'],
            'street': dat['INCEPTOR_STREET'],
            'number': dat['INCEPTOR_STREET_NUMBER'],
            'settlement': dat['INCEPTOR_SETTLEMENT'],
            'state': dat['INCEPTOR_STATE'].upper(),
            'town': dat['INCEPTOR_TOWN'].upper(),
            'cp': dat['INCEPTOR_CP'].upper(),
            'regimen': dat['INCEPTOR_REGIMEN'].upper(),
            'op': dat['CFDI_ORIGIN_PLACE'].upper(),
            'fontSize': '7',
            'fontName':'Helvetica',
        }

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
            ''' % context, st)

        cont = [[text]]
        table = Table(cont, colWidths = [ 9.0 *cm])
        table.setStyle(TableStyle(
            [('VALIGN',(-1,-1),(-1,-1),'TOP')]))
        return table

    def __create_factura_table(self, dat):
        st = ParagraphStyle(
            name='info',
            fontName='Helvetica',
            fontSize=7,
            leading = 8)

        serie_folio = "%s%s" % (dat['CFDI_SERIE'], dat['CFDI_FOLIO'])
        cont = []
        cont.append([ dat['CAP_LOADED']['TL_DOC_NAME'] ])
        cont.append(['No.' ])
        cont.append([ serie_folio ])
        cont.append([ dat['CAP_LOADED']['TL_DOC_DATE'] ])
        cont.append([ dat['CFDI_DATE'] ])
        cont.append(['FOLIO FISCAL'])
        cont.append([ Paragraph( dat['UUID'], st ) ])
        cont.append(['NO. CERTIFICADO'])
        cont.append([ dat['CFDI_CERT_NUMBER'] ])

        table = Table(cont,
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

        table.setStyle( TableStyle([

            #Body and header look and feel (common)
            ('BOX', (0, 1), (-1, -1), 0.25, colors.black),
            ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 10),

            ('TEXTCOLOR', (0, 1),(-1, 1), colors.white),
            ('FONT', (0, 1), (-1, 2), 'Helvetica-Bold', 7),

            ('TEXTCOLOR', (0, 3),(-1, 3), colors.white),
            ('FONT', (0, 3), (-1, 3), 'Helvetica-Bold', 7),
            ('FONT', (0, 4), (-1, 4), 'Helvetica', 7),

            ('TEXTCOLOR', (0, 5),(-1, 5), colors.white),
            ('FONT', (0, 5), (-1, 5), 'Helvetica-Bold', 7),

            ('FONT', (0, 7), (-1, 7), 'Helvetica-Bold', 7),
            ('TEXTCOLOR', (0, 7),(-1, 7), colors.white),
            ('FONT', (0, 8), (-1, 8), 'Helvetica', 7),

            ('ROWBACKGROUNDS', (0, 1),(-1, -1), [colors.black, colors.white]),
            ('ALIGN', (0, 0),(-1, -1), 'CENTER'),
            ('VALIGN', (0, 1),(-1, -1), 'MIDDLE'),
        ]))

        return table

    def data_acq(self, conn, d_rdirs, **kwargs):
        doc = BaseDocTemplate(
            output_file, pagesize=letter,
            rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18,
        )

        story = []

        logo = Image(dat['LOGO'])
        logo.drawHeight = 3.8*cm
        logo.drawWidth = 5.2*cm

        cedula = Image(dat['CEDULA'])
        cedula.drawHeight = 3.2*cm
        cedula.drawWidth = 3.2*cm

        story.append(
            self.__top_table(
                logo,
                __create_emisor_table(dat),
                __create_factura_table(dat)
            )
        )

    def format_wrt(self, output_file, dat):
        pass

    def data_rel(self, dat):
        pass
