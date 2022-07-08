import sys
import os
from lxml import etree
from lxml.builder import unicode
from psycopg2 import connect

SERVERNAME = 'localhost'
USERNAME = 'postgres'
PASSWORD = ''
PORT = '5432'

# district name is the database name.
districts = [{"db_name": "demo"}]


def newConnection(district):
    try:
        conn = connect("host=" + SERVERNAME + " port=" + PORT + " dbname=" +
                       district + " user=" + USERNAME + " password=" + PASSWORD)
        return conn
    except Exception as e:
        raise Exception(e)


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
        conn = newConnection(districts[0]['district_name'])
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        # cur.execute('SELECT version()')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()


        mathml = input('Enter MathML: ')
        if mathml[:7] == '<math> ':
            mathml = "<math xmlns=\"http://www.w3.org/1998/Math/MathML\"> " + mathml[7:]

        latex = mathml2latex_yarosh(mathml)
        latex = latex.replace("$", "")
        print('Latex: ' + latex)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    except:
        print("Please enter a valid MathML expression!")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    
