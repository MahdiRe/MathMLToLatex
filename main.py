import sys
import os
from lxml import etree
from lxml.builder import unicode


def mathml2latex_yarosh(equation):
    """ MathML to LaTeX conversion with XSLT from Vasil Yaroshevich """
    script_base_path = os.path.dirname(os.path.realpath(__file__))
    xslt_file = os.path.join(script_base_path, 'service', 'mmltex.xsl')
    dom = etree.fromstring(equation)
    xslt = etree.parse(xslt_file)
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    return unicode(newdom)


if __name__ == '__main__':
    try:
        mathml = input('Enter MathML: ')
        if mathml[:7] == '<math> ':
            mathml = "<math xmlns=\"http://www.w3.org/1998/Math/MathML\"> " + mathml[7:]

        latex = mathml2latex_yarosh(mathml)
        latex = latex.replace("$", "")
        print('Latex: ' + latex)
    except:
        print("Please enter a valid MathML expression!")
