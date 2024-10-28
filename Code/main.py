from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
from textblob import TextBlob

app = Flask(__name__)
app.secret_key = '345543a3-53b0-43bb-1253-1f4aab3a2a3e'

# SQL information
MYSQL_ADDRESS = 'chatcatserver.cxau00w82zgn.us-east-2.rds.amazonaws.com'
MYSQL_USERNAME='admin'
MYSQL_PASSWORD='password'
MYSQL_DATABASE = 'chatcatdb'

def get_conn_cur():
    cnx = mysql.connector.connect(  user=MYSQL_USERNAME, password=MYSQL_PASSWORD,
                                    host=MYSQL_ADDRESS, database=MYSQL_DATABASE, 
                                    port='3306')
    return (cnx, cnx.cursor())

def run_query(query_string):
    conn, cur = get_conn_cur() # get connection and cursor

    cur.execute(query_string) # executing string as before

    my_data = cur.fetchall() # fetch query data as before

    # Fetch the column names from the cursor
    columns = cur.column_names
    result_df = pd.DataFrame(my_data, columns=columns)  # Use the column names

    cur.close() # close
    conn.close() # close

    return result_df

def get_table_names():
    conn, cur = get_conn_cur()
    cur.execute("SHOW TABLES")
    tables = [table[0] for table in cur.fetchall()]
    cur.close()
    conn.close()
    return tables

def sql_head(self, table_name):
    conn, cur = self.get_conn_cur()

    cur.execute(f"DESCRIBE {table_name}")
    columns = [col[0] for col in cur.fetchall()]

    cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cur.fetchall()

    df = pd.DataFrame(rows, columns=columns)
    cur.close()
    conn.close()

    return df

#      Tables_in_chatcatdb
# 0         Admissions_Info
# 1    Career_Opportunities
# 2          Course_Details
# 3     Degree_Requirements
# 4           Financial_Aid
# 5            Program_Info
# 6  Research_Opportunities
# 7                Websites
# print(run_query("SHOW tables"))

@app.route('/')
def start():
    tables = get_table_names()  # Fetch available table names
    return render_template('home.html', tables=tables)

@app.route('/table', methods=['POST'])
def table():
    table_name = request.form.get('table_name')
    table_df = pd.DataFrame(run_query(f"SELECT * FROM {table_name}"))
    table_df = table_df.applymap(lambda x: x.replace('\n', '<br>') if isinstance(x, str) else x)
    table_html = table_df.to_html(classes='dataframe table', escape=False)
    return render_template('table.html', table_html=table_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)







