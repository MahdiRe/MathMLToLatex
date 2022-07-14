import json
import sys
import os
from lxml import etree
from lxml.builder import unicode
from psycopg2 import DatabaseError, connect
from bs4 import BeautifulSoup
import copy
import random

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
        cur.executemany(query, processed)
        conn.commit()
        print("Inserted to DB successfully")
    except Exception as e:
        raise Exception(e)
    
# # # This method is used only for testing purpose. It updates the specific question Id's question_content.
# def UpdateSystem(conn, processed):
#     try:
#         cur = conn.cursor()
#         query = "UPDATE edg.asmt_question SET question_content=%s WHERE id='2073514';"
#         cur.execute(query, [processed])
#         conn.commit()
#         print('Updated the question id 2073514 question content successfully')
#     except Exception as e:
#         raise Exception(e)


def converter():
    try:
        conn = newConnection(districts[0]['district_name'])
        cur = conn.cursor()
        cur.execute('SELECT question_content, id FROM edg.asmt_question OFFSET 0 LIMIT 10')

        contents = cur.fetchall()
        processed = []
        
        for content in contents:
            oldContent = copy.deepcopy(content[0])
            newContent = copy.deepcopy(content[0])
            ques_id = content[1]
               
            for item in oldContent:                            
                if ('choice' in item and item != 'choicesArr') or item == 'question':                             
                    soup = None
                    if oldContent[item][:3] == '<p>' or oldContent[item][:5] == '<div>':
                        soup = BeautifulSoup(oldContent[item], 'html.parser')
                    else:
                        soup = BeautifulSoup("<p>"+oldContent[item]+"</p>", 'html.parser')
                   
                    for prompts in soup.find_all('prompt'):
                        prompts.parent.prompt.wrap(soup.new_tag("span"))
                        prompts.parent.prompt.unwrap() 
                  
                    for divs in soup.find_all('div'):
                        divs.parent.div.wrap(soup.new_tag("p"))
                        divs.parent.div.unwrap()
                                     
                    maths = None
                    maths = soup.find_all('math')
                    
                    latex_dict = {}
                    index = 0
                    while index < len(maths):
                        
                        if maths[index].mstyle != None:
                            maths[index].mstyle.unwrap()
                        
                        # wrap mathml in a <span>
                        parent_span_id = "mathml" + str(random.randint(0,1000))
                        maths[index].parent.math.wrap(soup.new_tag("span")).attrs['id'] = parent_span_id
                                               
                        mathml = getMathMlCode(str(maths[index]))
                        latex = getLatexCode(mathml)

                        latex_tag = ('<span class="latexSpan" contenteditable="false" cursor="pointer"><span id="txtbox#randomID#"'
                        'class="latexTxtEdit" alttext="" contenteditable="false" style="cursor:pointer; font-size:;'
                        'color:; font-weight:; font-style: font-family:sans-serif">#latex#</span></span>')

                        latex_tag = latex_tag.replace("#randomID#", str(random.randint(0,1000)))
                        latex_tag = latex_tag.replace("#latex#", latex)
                            
                        soup.find(id=parent_span_id).clear() # clear mathml content 
                                                
                        replace_code = "#ReplaceLatexHere"+ str(index) +"#"
                        soup.find(id=parent_span_id).append(replace_code) # Add latex
                        latex_dict[replace_code] = latex_tag
                        
                        index += 1
                        
                    soup_str = str(soup)
                    for key in latex_dict.keys():
                        soup_str = soup_str.replace(key, latex_dict[key])
                    newContent[item] = soup_str
                                
            processed.append((ques_id, json.dumps(oldContent), json.dumps(newContent)))
            
        insertToTemp(conn, processed)
        # For testing purpose only
        # UpdateSystem(conn, json.dumps(newContent))
        
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
    
