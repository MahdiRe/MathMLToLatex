import sys
import os
from lxml import etree
from lxml.builder import unicode
from psycopg2 import connect
from bs4 import BeautifulSoup

SERVERNAME = 'localhost'
USERNAME = 'postgres'
PASSWORD = 'postgres'
PORT = '5432'

# district name is the database name.
districts = [{"district_name": "demo"}]


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


def converter():
    try:
        conn = newConnection(districts[0]['district_name'])
        cur = conn.cursor()
        # cur.execute('SELECT question_content FROM edg.asmt_question OFFSET 0 LIMIT 1')
        # cur.execute('SELECT question_content FROM edg.asmt_question WHERE id = 6050457')
        cur.execute('SELECT question_content FROM edg.asmt_question WHERE id = 2073509')

        # display the PostgreSQL database server version
        content = cur.fetchone()
        # print(content)
        
        for item in content[0]:
            # print(item)
            if item != 'answer' and item != 'choicesArr':
                # print(content[0][item])
                # print (content[0][item])
                soup = BeautifulSoup(content[0][item], 'html.parser')
                maths = soup.find_all('math')
                
                index = 0
                while index < len(maths):
                    mathml = str(maths[index])
                    print('\nMathml: ' + mathml + '\n')
                    if mathml[:7] == '<math> ':
                        mathml = "<math xmlns=\"http://www.w3.org/1998/Math/MathML\"> " + mathml[7:]
                        # print(mathml)
                    latex = mathml2latex_yarosh(mathml)
                    latex = latex.replace("$", "")
                    print('Latex: ' + latex + '\n')
                    index += 1
                    # create a schema 'temp' and create table 'question_update'
                    # Save into this, id / original question / updated content

        
        # mathml = """<prompt  xmlns:m=\"http://www.w3.org/1998/Math/MathML\" ><p>Graph the solution set to <span class=\"rsc_eqtn\"><math>   <mn>5</mn>   <mi>x</mi>   <mo>&#8722;<!-- &#8722; --></mo>   <mn>3</mn>   <mi>y</mi>   <mo>&lt;</mo>   <mo>&#8722;</mo>   <mn>15</mn> </math></span>.</p>  <p></p></prompt>"""
        # if mathml[:7] == '<math> ':
        #     mathml = "<math xmlns=\"http://www.w3.org/1998/Math/MathML\"> " + mathml[7:]
        # print(mathml)
        # close the communication with the PostgreSQL
        cur.close()


        # mathml = input('Enter MathML: ')
        # if mathml[:7] == '<math> ':
        #     mathml = "<math xmlns=\"http://www.w3.org/1998/Math/MathML\"> " + mathml[7:]

        # latex = mathml2latex_yarosh(mathml)
        # latex = latex.replace("$", "")
        # print('Latex: ' + latex)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    except:
        print("Please enter a valid MathML expression!")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    converter()
    
