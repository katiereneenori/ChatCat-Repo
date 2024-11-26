from flask import Flask, render_template, request, session, jsonify
import mysql.connector
import pandas as pd
from nltk.corpus import wordnet 

from textblob import TextBlob
from textblob import Word
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

def preprocess_input(user_input):
    """
    Preprocesses the input text by cleaning and standardizing it.
    """
    cleaned_input = user_input.strip()  # Remove leading and trailing spaces
    cleaned_input = cleaned_input.lower()  # Convert to lowercase
    cleaned_input = re.sub(r'[^\w\s]', '', cleaned_input)  # Remove special characters
    return cleaned_input

def get_conversation_state():
    user_id = session.get("user_id", "default_user")
    if user_id not in conversation_states:
        conversation_states[user_id] = {"step" : "greeting", "query_history": [], "lemma_lists": [], "synsets_lists": [], "admin": False} #Initial default state
    return conversation_states[user_id]

def set_conversation_state(state):
    user_id = session.get("user_id", "default_user")
    if user_id in conversation_states:
        conversation_states[user_id].update(state)
    else:
        conversation_states[user_id] = state



def authenticate(username, password):
    conn, cur = get_conn_cur()
    
    # Query to check if the username and password match
    query = "SELECT admin FROM Users WHERE username = %s AND password = %s"
    cur.execute(query, (username, password))
    result = cur.fetchone()
    
    if result:
        is_admin = result[0]  
        state = get_conversation_state()
        state["admin"] = is_admin
        set_conversation_state(state)
        return True
    
    return False  




# Fetch result
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
#function to get tags in proper format for use with wordnet
def get_wordnet_pos(tag):
    if tag.startswith('VB'):  # Verbs
        return wordnet.VERB
    elif tag.startswith('NN'):  # Nouns
        return wordnet.NOUN
    elif tag.startswith('JJ'):  # Adjectives
        return wordnet.ADJ
    elif tag.startswith('RB'):  # Adverbs
        return wordnet.ADV
    else:
        return wordnet.NOUN

# adds the query to the state. It also adds a lemmatized form of the query.
def add_query_to_state(user_message, conversation_state):
     
    query_history = conversation_state.get("query_history", [])
    lemma_lists = conversation_state.get("lemma_lists", [])
    synsets_lists = conversation_state.get("synsets_list", [])
    user_message_tb = TextBlob(user_message)
    query_history.append(user_message_tb)

    #checks if more than 3 queries stored and gets rid of oldest if true
    if len(query_history) > 3:
        query_history.pop(0)
        lemma_lists.pop(0)
        synsets_lists.pop(0)


    synsets_list = []
    lemma_list = []
    tags = user_message_tb.tags  #gets a list of tags to use for lemmatization
   
    for word, tag in tags:
        word_obj = Word(word)
        lemma = word_obj.lemmatize(get_wordnet_pos(tag))
        lemma_list.append(lemma)
        lemma_obj = Word(lemma)
        synsets_list.append(lemma_obj.synsets)
       
        
    lemma_lists.append(lemma_list)
    synsets_lists.append(synsets_list)

    conversation_state["query_history"] = query_history
    conversation_state["lemma_lists"] = lemma_lists
    conversation_state["synsets_list"] = synsets_lists
    set_conversation_state(conversation_state)
    



# Route for home page
@app.route('/')
def start():
    session.clear() #Clear session data 
    session["user_id"] = "default_user" #Initialize User ID
    logged_in = session.get('logged_in', False)
    tables = get_table_names()  # Fetch available table names
    return render_template('home.html', tables=tables, logged_in=logged_in)

@app.route('/chatbot')
def chatbot():
    # put chatbot code here
    # maybe we use a loop to keep displaying the messages
    # return: render chatbot page 
    return

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

        preprocessed_input = preprocess_input(user_input)

        # Analyze sentiment using TextBlob
        blob = TextBlob(preprocessed_input)
        sentiment = blob.sentiment
        sentiment_result = f"Polarity: {sentiment.polarity}, Subjectivity: {sentiment.subjectivity}"
        return render_template('sentiment.html', user_input=user_input, sentiment_result=sentiment_result)
    return render_template('sentiment.html')

@app.route('/chat-load')
def loadChat_HTML():
    return render_template('chat.html')

# New Route for chatting
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "").strip()

    # Preprocess the user message
    preprocessed_message = preprocess_input(user_message)

    # Retrieve the current conversation state for the user
    conversation_state = get_conversation_state()


    add_query_to_state(user_message, conversation_state)



    # Fetch available table names
    table_names = get_table_names()

    # Input handling based on specific commands
    if "show tables" in preprocessed_message:
        # User asked to list all tables in the database
        response = "Available tables are: " + ", ".join(table_names)

    elif preprocessed_message.startswith("get"):
        # User wants to retrieve a specific table by name
        table_name = preprocessed_message.split("get", 1)[1].strip()
        if table_name in table_names:
            table_df = sql_head(table_name)
            response = f"Here are the first 5 rows of {table_name}:\n" + table_df.to_string(index=False)
        else:
            response = f"Table '{table_name}' does not exist. Please check the table name and try again."

    elif conversation_state.get("step") == "greeting":
        response = "Hello! How can I assist you today?"
        conversation_state["step"] = "awaiting_response"

    elif "help" in preprocessed_message:
        response = "Sure, I can help you. What do you need assistance with?"
        conversation_state["step"] = "help_requested"  # Update intent in state

    else:
        response = "I'm here to help. Please provide more details or specify a valid command."
    
    # Update conversation state in memory
    set_conversation_state(conversation_state)
    
    return jsonify({"response": response})

#route for logging in

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if authenticate(username, password):
        session['logged_in'] = True
        session['username'] = username  
        return render_template('home.html', tables=get_table_names(), logged_in=True)
    else:
        error_message = "Invalid username or password. Please try again."
        return render_template('home.html', tables=get_table_names(), logged_in=False, error=error_message)


# New Route for getting state
@app.route('/get_state', methods=['GET'])
def get_state():
    # Endpoint to retrieve the current conversation state
    conversation_state = get_conversation_state()
    return {"conversation_state": conversation_state}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    
