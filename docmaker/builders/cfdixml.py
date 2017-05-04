import xml.etree.ElementTree as etree

namespaces = {
    'cfdi': 'http://www.sat.gob.mx/cfd/3',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

for prefix, uri in namespaces.items():
    etree.register_namespace(prefix, uri)


comprobante = etree.Element(
    '{http://www.sat.gob.mx/cfd/3}Comprobante',
    attrib={
        '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd',
        'Version':'3.3',
        'Folio': "test attribute", #optional
        'Fecha': "2014-06-26T09:13:00",
        'Sello': "BLABLALASELLO",
        'FormaPago': "clave forma de pago", #optional
        'Nocertificado': "00001000000202529199",
        'Certificado': "certificado en base64",
        'SubTotal': "4180.0",
        'Total': "4848.80",
        'Moneda': "MXN",
        'TipoCambio': "1.0", #optional (requerido en ciertos casos)
        'TipoDeComprobante': 'UNO_CHIDO',
        'metodoDePago': "NO IDENTIFICADO", #optional
        'LugarExpedicion': "GRAL. ESCOBEDO, NUEVO LEON"
    }
)

emisor = etree.SubElement(
    comprobante, "{http://www.sat.gob.mx/cfd/3}Emisor",
    attrib={
        'Nombre': "PRODUCTOS INDUSTRIALES SAAR S.A. DE C.V.", #opcional
        'Rfc': "PIS850531CS4",
        'RegimenFiscal': 'clave regimen contribuyente',
        
    }
)

receptor = etree.SubElement(
    comprobante, "{http://www.sat.gob.mx/cfd/3}Emisor",
    attrib={
        'Nombre': "PRODUCTOS INDUSTRIALES SAAR S.A. DE C.V.", #opcional
        'Rfc': "PIS850531CS4",
        'UsoCFDI': "clave de uso que dara el receptor de esta factura"
    }
)


print(etree.tostring(comprobante))

t= etree.ElementTree(comprobante)

t.write("borrame.xml",
           xml_declaration=True,encoding='utf-8',
           method="xml")
