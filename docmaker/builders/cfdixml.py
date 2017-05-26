class CommonBill(BuilderGen):

    def __init__(self, logger):
        super().__init__(logger)

    def data_acq(self, conn, d_rdirs, **kwargs):
        pass

    def format_wrt(self, output_file, dat):
        c = Comprobante()
        c.Version = '3.3'
        c.Folio = "test attribute" #optional
        c.Fecha = "2014-06-26T09:13:00"
        c.Sello = "BLABLALASELLO"
        c.FormaPago = "01" #optional
        c.NoCertificado = "00001000000202529199"
        c.Certificado = "certificado en base64"
        c.SubTotal = "4180.0"
        c.Total = "4848.80"
        c.Moneda = "MXN"
        c.TipoCambio = "1.0" #optional (requerido en ciertos casos)
        c.TipoDeComprobante = 'I'
    #    c.metodoDePago = "NO IDENTIFICADO" #optional
        c.LugarExpedicion = "60050"

        c.Emisor = pyxb.BIND()
        c.Emisor.Nombre = "PRODUCTOS INDUSTRIALES SAAR S.A. DE C.V." #opcional
        c.Emisor.Rfc = "PIS850531CS4"
        c.Emisor.RegimenFiscal = '601'

        c.Receptor = pyxb.BIND()
        c.Receptor.Nombre = "PRODUCTOS INDUSTRIALES SAAR S.A. DE C.V." #opcional
        c.Receptor.Rfc = "PIS850531CS4"
        c.Receptor.UsoCFDI = 'G01'

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

        writedom_cfdi(c.toDOM(), output_file)

    def data_rel(self, dat):
        pass
