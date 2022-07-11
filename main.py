import json
import sys
import os
from lxml import etree
from lxml.builder import unicode
from psycopg2 import DatabaseError, connect
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


def getMathMlCode(mathml):
    if mathml[:7] == '<math> ':
        mathml = "<math xmlns=\"http://www.w3.org/1998/Math/MathML\"> " + mathml[7:]
    mathml = mathml.replace('\\\"', "'")
    mathml = mathml.replace('\\n', "")
    return mathml


def getLatexCode(mathml):
    latex = mathml2latex_yarosh(mathml)
    latex = latex.replace("$", "")
    latex = latex.replace("\[", "")
    latex = latex.replace("\]", "")
    latex = latex.strip()
    return latex


def insertToTemp(conn, processed):
    try:
        cur = conn.cursor()
        query = """
            Insert into temp.question_update(id, old_question_content, updated_question_content)
            values(%s,%s,%s)
            """
        print(processed[0][2])
        cur.executemany(query, processed)
        conn.commit()
    except Exception as e:
        raise Exception(e)

def converter():
    try:
        conn = newConnection(districts[0]['district_name'])
        cur = conn.cursor()
        # cur.execute('SELECT question_content FROM edg.asmt_question OFFSET 0 LIMIT 2')
        # cur.execute('SELECT question_content FROM edg.asmt_question WHERE id = 6050457')
        cur.execute('SELECT question_content, id FROM edg.asmt_question WHERE id = 2073509')

        # display the PostgreSQL database server version
        # content = cur.fetchone()
        contents = cur.fetchall()
        processed = []
        
        # print(len(contents))
        
        for content in contents:
            # print(content)
            # print('\n')

            newContent = content[0]
            ques_id = content[1]
            
            
            for item in content[0]:
                if ('choice' in item and item != 'choicesArr') or item == 'question':
                    # print(item)
                    
                    soup = BeautifulSoup(content[0][item], 'html.parser')
                    # print(soup.math)
                    if soup.mstyle != None:
                        soup.math.mstyle.unwrap()
                    maths = soup.find_all('math')
                    
                    index = 0
                    while index < len(maths):
                        parent_span_id = maths[index].find_parent("span").get('id')
                        
                        mathml = getMathMlCode(str(maths[index]))
                        # print("MathMl: " + mathml + '\n')
                        
                        latex = getLatexCode(mathml)
                        # print('Latex: ' + latex + '\n')

                        latex_tag = ('<span class="latexSpan" contenteditable="false" cursor="pointer"><span id="txtbox2"'
                        'class="latexTxtEdit" alttext="" contenteditable="false" style="cursor:pointer; font-size:;'
                        'color:; font-weight:; font-style: font-family:sans-serif">#latex#</span></span>')

                        latex_tag = latex_tag.replace("#latex#", latex)
                        

                        soup.find(id=parent_span_id).clear() # clear math
                        soup.find(id=parent_span_id).append(soup.new_tag(latex_tag))

                        newContent[item] = str(soup)
                        # print(newContent)
                        # print('\n')
                        index += 1
                        # create a schema 'temp' and create table 'question_update'
                        # Save into this, id / original question / updated content

            processed.append((ques_id, json.dumps(content[0]), json.dumps(newContent)))
        insertToTemp(conn, processed)
        

        # close the communication with the PostgreSQL
        cur.close()

    except (Exception, DatabaseError) as error:
        print(error)
    except:
        print("Please enter a valid MathML expression!")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    converter()
    
