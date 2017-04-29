import lxml.etree as ET
import random
import string
import re

class HelperXml(object):

    @staticmethod
    def transform_xslt(xml_filename, xsl_filename):
        """"""
        dom = ET.parse(xml_filename)
        xslt = ET.parse(xsl_filename)
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
        return str(newdom)
