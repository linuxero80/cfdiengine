import lxml.etree as et


class HelperXml(object):

    @staticmethod
    def run_xslt(xml_filename, xsl_filename):
        """"""
        dom = et.parse(xml_filename)
        xslt = et.parse(xsl_filename)
        transform = et.XSLT(xslt)
        newdom = transform(dom)
        return str(newdom)
