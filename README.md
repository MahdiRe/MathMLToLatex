# MathMLToLatex
Convert MathML to Latex

Before run the project, intsall lxml, psycopg2, BeautifulSoup
(pip3 install -r requirements.txt)

We have used the code from: https://github.com/oerpub/mathconverter to convert the MathMl into Latex.

Sample sql query to create temporary table is below.

```sql
CREATE TABLE temp.question_update
(
  id bigint NOT NULL,
  old_question_content jsonb,
  updated_question_content jsonb,
  CONSTRAINT question_update_pkey PRIMARY KEY (id)
)
```
