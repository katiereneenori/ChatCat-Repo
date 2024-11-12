from flask import Flask, render_template, request, session, jsonify
import mysql.connector
import pandas as pd
from textblob import TextBlob
import re

from data_processing import load_and_process_data
from model import train_model

#      Tables_in_chatcatdb
# 0         Admissions_Info
# 1    Career_Opportunities
# 2          Course_Details
# 3     Degree_Requirementss
# 4           Financial_Aid
# 5            Program_Info
# 6  Research_Opportunities
# 7                Websites
# print(run_query("SHOW tables"))

app = Flask(__name__)
app.secret_key = '345543a3-53b0-43bb-1253-1f4aab3a2a3e'

# In-memory storage for conversation states
conversation_states = {}

# SQL information
MYSQL_ADDRESS = 'chatcatserver.cxau00w82zgn.us-east-2.rds.amazonaws.com'
MYSQL_USERNAME = 'admin'
MYSQL_PASSWORD = 'password'
MYSQL_DATABASE = 'chatcatdb'

def get_conn_cur():
    cnx = mysql.connector.connect(user=MYSQL_USERNAME, password=MYSQL_PASSWORD,
                                  host=MYSQL_ADDRESS, database=MYSQL_DATABASE,
                                  port='3306')
    return (cnx, cnx.cursor())

def run_query(query_string):
    conn, cur = get_conn_cur()  # get connection and cursor

    cur.execute(query_string)  # executing string

    my_data = cur.fetchall()  # fetch query data

    # Fetch the column names from the cursor
    columns = cur.column_names
    result_df = pd.DataFrame(my_data, columns=columns)  # Use the column names

    cur.close()  # close
    conn.close()  # close

    return result_df

def get_table_names():
    conn, cur = get_conn_cur()
    cur.execute("SHOW TABLES")
    tables = [table[0] for table in cur.fetchall()]
    cur.close()
    conn.close()
    return tables

def validate_input(input_text):
    # Check if input is empty
    if not input_text.strip():
        return False, "Input cannot be empty."

    # Define invalid characters (adjust pattern as needed)
    if re.search(r'[^a-zA-Z0-9\s,.?!]', input_text):
        return False, "Input contains invalid characters."

    return True, ""


def sql_head(table_name):
    conn, cur = get_conn_cur()

    # query = "DESCRIBE %s"
    # cur.execute(query, table_name)
    cur.execute(f"DESCRIBE {table_name}")
    columns = [col[0] for col in cur.fetchall()]

    # query = "SELECT * FROM %s LIMIT 5"
    # cur.execute(query, table_name)
    cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cur.fetchall()

    df = pd.DataFrame(rows, columns=columns)
    cur.close()
    conn.close()

    return df

def get_conversation_state():
    user_id = session.get("user_id", "default_user")
    if user_id not in conversation_states:
        conversation_states[user_id] = {"step" : "greeting"} #Initial default state
    return conversation_states[user_id]

def set_conversation_state(state):
    user_id = session.get("user_id", "default_user")
    if user_id in conversation_states:
        conversation_states[user_id].update(state)
    else:
        conversation_states[user_id] = state

# Route for home page
@app.route('/')
def start():
    session["user_id"] = "default_user" #Initialize User ID
    tables = get_table_names()  # Fetch available table names
    return render_template('home.html', tables=tables)

@app.route('/chatbot')
def chatbot():
    # put chatbot code here
    # maybe we use a loop to keep displaying the messages
    # return: render chatbot page 

# Route for displaying a table
@app.route('/table', methods=['POST'])
def table():
    table_name = request.form.get('table_name')
    table_df = pd.DataFrame(run_query(f"SELECT * FROM {table_name}"))
    table_df = table_df.applymap(lambda x: x.replace('\n', '<br>') if isinstance(x, str) else x)
    table_html = table_df.to_html(classes='dataframe table', escape=False)
    return render_template('table.html', table_html=table_html)

# Route for sentiment analysis
@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    if request.method == 'POST':
        user_input = request.form['user_input']

        # Validate the user input
        is_valid, error_message = validate_input(user_input)
        if not is_valid:
            return render_template('sentiment.html', user_input=user_input, sentiment_result=error_message)

        # Analyze sentiment using TextBlob
        blob = TextBlob(user_input)
        sentiment = blob.sentiment
        sentiment_result = f"Polarity: {sentiment.polarity}, Subjectivity: {sentiment.subjectivity}"
        return render_template('sentiment.html', user_input=user_input, sentiment_result=sentiment_result)
    return render_template('sentiment.html')

# New Route for chatting
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "").strip()

    # Validate the user input
    is_valid, error_message = validate_input(user_message)
    if not is_valid:
        return jsonify({"response": error_message}), 400
    
    # Retrieve the current conversation state for the user
    conversation_state = get_conversation_state()

    table_names = get_table_names()

    # Input handling based on specific commands
    if "show tables" in user_message.lower():
        # User asked to list all tables in the database
        response = "Available tables are: " + ", ".join(table_names)

    elif user_message.lower().startswith("get"):
        # User wants to retrieve a specific table by name
        table_name = user_message.split("get", 1)[1].strip()
        if table_name in table_names:
            table_df = sql_head(table_name)
            response = f"Here are the first 5 rows of {table_name}:\n" + table_df.to_string(index=False)
        else:
            response = f"Table '{table_name}' does not exist. Please check the table name and try again."

    elif conversation_state.get("step") == "greeting":
        response = "Hello! How can I assist you today?"
        conversation_state["step"] = "awaiting_response"

    elif "help" in user_message.lower():
        response = "Sure, I can help you. What do you need assistance with?"
        conversation_state["step"] = "help_requested"  # Update intent in state

    else:
        response = "I'm here to help. Please provide more details or specify a valid command."
    
    # Update conversation state in memory
    set_conversation_state(conversation_state)
    
    return jsonify({"response": response})

# New Route for getting state
@app.route('/get_state', methods=['GET'])
def get_state():
    # Endpoint to retrieve the current conversation state
    conversation_state = get_conversation_state()
    return {"conversation_state": conversation_state}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    
