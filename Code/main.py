from flask import Flask, render_template, request, session, jsonify
import mysql.connector
import pandas as pd
from textblob import TextBlob
import re
import logging

from data_processing import load_and_process_data
from model import train_model
from intent_recognition import recognize_intent
from handlers import (
    handle_greeting,
    handle_program_information,
    handle_admissions_assistance,
    handle_curriculum_details,
    handle_financial_aid,
    handle_research_opportunities,
    handle_career_opportunities,
    handle_university_resources,
    handle_transfer_credits,
    handle_advisor_contact,
    handle_general_queries,
    handle_unknown_intent,
    handle_show_tables,
    handle_get_table
)
from database import run_query, get_conn_cur  # Ensure database.py has necessary functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = '345543a3-53b0-43bb-1253-1f4aab3a2a3e'

@app.context_processor
def inject_current_year():
    return {'current_year': 2024}

# In-memory storage for conversation states
conversation_states = {}

def validate_input(input_text):
    """
    Validates the user input to prevent empty inputs and disallowed characters.
    """
    if not input_text.strip():
        return False, "Input cannot be empty."

    # Define allowed characters (letters, numbers, common punctuation)
    if re.search(r'[^a-zA-Z0-9\s,.?!\'"-]', input_text):
        return False, "Input contains invalid characters."

    return True, ""

def get_conversation_state():
    """
    Retrieves the conversation state for the current user session.
    """
    user_id = session.get("user_id", "default_user")
    if user_id not in conversation_states:
        conversation_states[user_id] = {"step": "greeting"}  # Initial default state
    return conversation_states[user_id]

def set_conversation_state(state):
    """
    Updates the conversation state for the current user session.
    """
    user_id = session.get("user_id", "default_user")
    if user_id in conversation_states:
        conversation_states[user_id].update(state)
    else:
        conversation_states[user_id] = state

def get_table_names():
    """
    Retrieves the list of table names from the database.
    """
    query = "SHOW TABLES"
    df = run_query(query)
    tables = df.iloc[:,0].tolist() if not df.empty else []
    return tables

# Route for home page
@app.route('/')
def start():
    session["user_id"] = "default_user"  # Initialize User ID
    tables = get_table_names()  # Fetch available table names
    return render_template('home.html', tables=tables)

# Route for displaying a table
@app.route('/table', methods=['POST'])
def table():
    table_name = request.form.get('table_name')
    if not table_name:
        return render_template('table.html', table_html="<p>Please provide a table name.</p>", table_name="")

    # Validate table name to prevent SQL injection
    if table_name not in get_table_names():
        table_html = f"<p>Table '{table_name}' does not exist.</p>"
    else:
        query = f"SELECT * FROM {table_name} LIMIT 10"  # Fetch first 10 rows for display
        table_df = run_query(query)
        if table_df.empty:
            table_html = f"<p>Table '{table_name}' is empty.</p>"
        else:
            # Replace newline characters in string columns
            table_df = table_df.applymap(lambda x: x.replace('\n', '<br>') if isinstance(x, str) else x)
            table_html = table_df.to_html(classes='dataframe table', escape=False)

    return render_template('table.html', table_html=table_html, table_name=table_name)

# Route for sentiment analysis
@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    if request.method == 'POST':
        user_input = request.form['user_input']

        # Validate the user input
        is_valid, error_message = validate_input(user_input)
        if not is_valid:
            sentiment_result = {'polarity': error_message, 'subjectivity': ''}
            return render_template('sentiment.html', user_input=user_input, sentiment_result=sentiment_result)

        # Analyze sentiment using TextBlob
        blob = TextBlob(user_input)
        sentiment = blob.sentiment
        sentiment_result = {
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity
        }
        return render_template('sentiment.html', user_input=user_input, sentiment_result=sentiment_result)
    return render_template('sentiment.html')

# Route for chatting
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "").strip()

    # Validate the user input
    is_valid, error_message = validate_input(user_message)
    if not is_valid:
        logger.warning(f"Invalid input received: {error_message}")
        return jsonify({"response": error_message}), 400

    # Retrieve the current conversation state for the user
    conversation_state = get_conversation_state()

    # Check if we are awaiting specific information
    if conversation_state.get("step") == "awaiting_program_selection":
        program = extract_program(user_message)
        if program:
            response = provide_program_details(program)
            conversation_state["step"] = "program_info_provided"
        else:
            response = "Please specify whether you're interested in the BS, MS, or PhD program."
    elif conversation_state.get("step") == "awaiting_advisor_type":
        advisor_type = extract_advisor_type(user_message)
        if advisor_type:
            response = provide_advisor_contact(advisor_type)
            conversation_state["step"] = "advisor_info_provided"
        else:
            response = "Please specify whether you need contact information for undergraduate or graduate advisors."
    else:
        # Recognize the intent
        intent = recognize_intent(user_message)
        logger.info(f"User Message: {user_message}")
        logger.info(f"Recognized Intent: {intent}")
        conversation_state["intent"] = intent  # Update intent in state

        # Handle the intent
        if intent == "Greeting":
            response = handle_greeting(user_message)
            conversation_state["step"] = "awaiting_response"
        elif intent == "ProgramInformation":
            response = handle_program_information(user_message)
            conversation_state["step"] = "awaiting_program_selection"
        elif intent == "AdmissionsAssistance":
            response = handle_admissions_assistance(user_message)
            conversation_state["step"] = "awaiting_program_selection"
        elif intent == "CurriculumDetails":
            response = handle_curriculum_details(user_message)
            conversation_state["step"] = "awaiting_program_selection"
        elif intent == "FinancialAid":
            response = handle_financial_aid(user_message)
            conversation_state["step"] = "provided_financial_aid_info"
        elif intent == "ResearchOpportunities":
            response = handle_research_opportunities(user_message)
            conversation_state["step"] = "awaiting_research_details"
        elif intent == "CareerOpportunities":
            response = handle_career_opportunities(user_message)
            conversation_state["step"] = "awaiting_career_details"
        elif intent == "UniversityResources":
            response = handle_university_resources(user_message)
            conversation_state["step"] = "awaiting_resource_selection"
        elif intent == "TransferCredits":
            response = handle_transfer_credits(user_message)
            conversation_state["step"] = "awaiting_transfer_details"
        elif intent == "AdvisorContact":
            response = handle_advisor_contact(user_message)
            conversation_state["step"] = "awaiting_advisor_type"
        elif intent == "ShowTables":
            response = handle_show_tables()
        elif intent == "GetTable":
            table_name = extract_table_name(user_message)
            response = handle_get_table(table_name)
        elif intent == "GeneralQueries":
            response = handle_general_queries(user_message)
            conversation_state["step"] = "awaiting_general_query"
        else:
            response = handle_unknown_intent(user_message)
            conversation_state["step"] = "unknown_intent"

        logger.info(f"Response: {response}")

    # Update conversation state in memory
    set_conversation_state(conversation_state)

    return jsonify({"response": response})

# Route for getting state (optional)
@app.route('/get_state', methods=['GET'])
def get_state():
    """
    Endpoint to retrieve the current conversation state.
    """
    conversation_state = get_conversation_state()
    return {"conversation_state": conversation_state}, 200

# Helper functions for multi-turn conversations
def extract_program(user_message):
    """
    Extracts the program type (BS, MS, PhD) from the user message.
    """
    programs = ["bs", "ms", "phd", "bachelor", "master", "doctoral"]
    for program in programs:
        if program in user_message.lower():
            if program in ["bs", "bachelor"]:
                return "BS"
            elif program in ["ms", "master"]:
                return "MS"
            elif program in ["phd", "doctoral"]:
                return "PhD"
    return None

def provide_program_details(program):
    """
    Provides detailed information about the specified program.
    """
    logger.info(f"Providing details for {program} program.")
    query = "SELECT description, duration, requirements FROM Program_Info WHERE program_name=%s"
    df = run_query(query, (program,))

    if df.empty:
        logger.warning(f"No details found for {program} program.")
        return f"I'm sorry, I couldn't find details for the {program} program."

    row = df.iloc[0]
    response = (f"**{program} in Software Engineering**\n"
                f"**Description:** {row['description']}\n"
                f"**Duration:** {row['duration']} years\n"
                f"**Requirements:** {row['requirements']}\n")
    logger.info(f"Program details for {program} generated successfully.")
    return response

def extract_advisor_type(user_message):
    """
    Extracts the advisor type (Undergraduate or Graduate) from the user message.
    """
    if "undergraduate" in user_message.lower() or "bs" in user_message.lower():
        return "Undergraduate"
    elif "graduate" in user_message.lower() or "ms" in user_message.lower() or "phd" in user_message.lower():
        return "Graduate"
    else:
        return None

def provide_advisor_contact(advisor_type):
    """
    Provides contact information for the specified advisor type.
    """
    logger.info(f"Providing contact for {advisor_type} advisors.")
    query = "SELECT contact_email, contact_phone FROM Advisors WHERE advisor_type=%s"
    df = run_query(query, (advisor_type,))

    if df.empty:
        logger.warning(f"No contact information found for {advisor_type} advisors.")
        return f"I'm sorry, I couldn't find contact information for {advisor_type} advisors."

    row = df.iloc[0]
    response = (f"**{advisor_type} Academic Advisor Contact Information**\n"
                f"**Email:** {row['contact_email']}\n"
                f"**Phone:** {row['contact_phone']}\n")
    logger.info(f"Advisor contact for {advisor_type} advisors generated successfully.")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
