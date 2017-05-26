import xml.etree.ElementTree as ET

def dom_makeup(d):
    """makes up a cfdi's dom"""
    namespaces = {
        'cfdi': 'http://www.sat.gob.mx/cfd/3',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    root = ET.fromstring(d.toxml("utf-8").decode())
    t = ET.ElementTree(root)
    t.write("myoutput.xml",
           xml_declaration=True,encoding='utf-8',
           method="xml"
