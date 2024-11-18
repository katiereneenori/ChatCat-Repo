# handlers.py

import logging
from database import run_query
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_greeting(user_message):
    """
    Handles greeting intents.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Greeting response.
    """
    response = "Hello! I'm ChatCat, your virtual assistant. How can I help you today?"
    logger.info("Handled Greeting Intent.")
    return response

def handle_program_information(user_message):
    """
    Provides information about software engineering programs.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Program information response.
    """
    query = "SELECT program_name, description FROM Program_Info"
    df = run_query(query)
    
    if df.empty:
        logger.warning("No program information found in the database.")
        return "I'm sorry, I couldn't find any information about our programs at the moment."
    
    response = "**Our Software Engineering Programs:**\n"
    for _, row in df.iterrows():
        response += f"**{row['program_name']}**: {row['description']}\n\n"
    
    logger.info("Provided Program Information.")
    return response.strip()

def handle_admissions_assistance(user_message):
    """
    Provides admissions assistance information.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Admissions assistance response.
    """
    query = """
    SELECT requirement, description 
    FROM Admissions_Info 
    WHERE LOWER(program) = %s
    """
    program_name = 'software engineering'
    df = run_query(query, (program_name,))
    
    if df.empty:
        logger.warning(f"No admissions information found for program '{program_name}'.")
        return "I'm sorry, I couldn't retrieve admissions information right now."
    
    response = "**Admissions Assistance for Software Engineering Program:**\n"
    for _, row in df.iterrows():
        response += f"**{row['requirement']}**: {row['description']}\n\n"
    
    logger.info("Provided Admissions Assistance.")
    return response.strip()

def handle_curriculum_details(user_message):
    """
    Provides details about the software engineering curriculum.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Curriculum details response.
    """
    query = """
    SELECT course_name, description 
    FROM Curriculum_Details 
    WHERE program = 'Software Engineering'
    """
    df = run_query(query)
    
    if df.empty:
        logger.warning("No curriculum details found in the database.")
        return "I'm sorry, I couldn't find curriculum details at the moment."
    
    response = "**Software Engineering Curriculum:**\n"
    for _, row in df.iterrows():
        response += f"**{row['course_name']}**: {row['description']}\n\n"
    
    logger.info("Provided Curriculum Details.")
    return response.strip()

def handle_financial_aid(user_message):
    """
    Provides information about financial aid options.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Financial aid information response.
    """
    query = "SELECT aid_type, description FROM Financial_Aid"
    df = run_query(query)
    
    if df.empty:
        logger.warning("No financial aid information found in the database.")
        return "I'm sorry, I couldn't retrieve financial aid information right now."
    
    response = "**Financial Aid Options:**\n"
    for _, row in df.iterrows():
        response += f"**{row['aid_type']}**: {row['description']}\n\n"
    
    logger.info("Provided Financial Aid Information.")
    return response.strip()

def handle_research_opportunities(user_message):
    """
    Provides information about research opportunities.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Research opportunities response.
    """
    query = "SELECT research_area, description FROM Research_Opportunities"
    df = run_query(query)
    
    if df.empty:
        logger.warning("No research opportunities found in the database.")
        return "I'm sorry, I couldn't find any research opportunities at the moment."
    
    response = "**Research Opportunities:**\n"
    for _, row in df.iterrows():
        response += f"**{row['research_area']}**: {row['description']}\n\n"
    
    logger.info("Provided Research Opportunities Information.")
    return response.strip()

def handle_career_opportunities(user_message):
    """
    Provides information about career opportunities for graduates.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Career opportunities response.
    """
    query = "SELECT industry, job_title, description FROM Career_Opportunities"
    df = run_query(query)
    
    if df.empty:
        logger.warning("No career opportunities found in the database.")
        return "I'm sorry, I couldn't find any career opportunities at the moment."
    
    response = "**Career Opportunities for Software Engineering Graduates:**\n"
    for _, row in df.iterrows():
        response += f"**{row['job_title']}** in **{row['industry']}**: {row['description']}\n\n"
    
    logger.info("Provided Career Opportunities Information.")
    return response.strip()

def handle_university_resources(user_message):
    """
    Provides information about university resources and support services.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: University resources response.
    """
    query = "SELECT resource_name, description FROM University_Resources"
    df = run_query(query)
    
    if df.empty:
        logger.warning("No university resources found in the database.")
        return "I'm sorry, I couldn't retrieve university resources information right now."
    
    response = "**University Resources and Support Services:**\n"
    for _, row in df.iterrows():
        response += f"**{row['resource_name']}**: {row['description']}\n\n"
    
    logger.info("Provided University Resources Information.")
    return response.strip()

def handle_transfer_credits(user_message):
    """
    Provides information about transferring credits.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Transfer credits information response.
    """
    query = "SELECT course, status, notes FROM Transfer_Credits"
    df = run_query(query)
    
    if df.empty:
        logger.warning("No transfer credits information found in the database.")
        return "I'm sorry, I couldn't find any information about transferring credits at the moment."
    
    response = "**Transfer Credits Information:**\n"
    for _, row in df.iterrows():
        response += f"**{row['course']}**: {row['status']} - {row['notes']}\n\n"
    
    logger.info("Provided Transfer Credits Information.")
    return response.strip()

def handle_advisor_contact(user_message):
    """
    Provides contact information for academic advisors based on advisor type.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Advisor contact information response.
    """
    # Extract advisor type from the user message
    advisor_type = extract_advisor_type(user_message)
    if not advisor_type:
        logger.warning("Advisor type not specified or unrecognized.")
        return "Please specify whether you're looking for an Undergraduate or Graduate advisor."

    query = "SELECT advisor_name, contact_email, contact_phone FROM Advisors WHERE advisor_type = %s"
    df = run_query(query, (advisor_type,))
    
    if df.empty:
        logger.warning(f"No advisors found for advisor type: {advisor_type}.")
        return f"I'm sorry, I couldn't find contact information for {advisor_type} advisors."

    response = f"**{advisor_type} Academic Advisors:**\n"
    for _, row in df.iterrows():
        response += f"**{row['advisor_name']}**\nEmail: {row['contact_email']}\nPhone: {row['contact_phone']}\n\n"
    
    logger.info(f"Provided Advisor Contact Information for {advisor_type} advisors.")
    return response.strip()

def handle_general_queries(user_message):
    """
    Handles general queries that don't fit into other specific intents.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: General query response.
    """
    response = "I'm here to help! Could you please provide more details or specify your question?"
    logger.info("Handled General Queries Intent.")
    return response

def handle_unknown_intent(user_message):
    """
    Handles unknown or unrecognized intents.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str: Unknown intent response.
    """
    response = "I'm sorry, I didn't understand that. Could you please rephrase or ask something else?"
    logger.info("Handled Unknown Intent.")
    return response

def handle_show_tables():
    """
    Lists all available tables in the database.
    
    Returns:
        str: List of table names.
    """
    query = "SHOW TABLES"
    df = run_query(query)
    
    if df.empty:
        logger.warning("No tables found in the database.")
        return "No tables are available in the database."
    
    tables = df.iloc[:, 0].tolist()
    table_list = ", ".join(tables)
    response = f"**Available Tables:** {table_list}"
    
    logger.info("Provided List of Available Tables.")
    return response

def handle_get_table(table_name):
    """
    Retrieves and returns the first few rows of a specified table.
    
    Args:
        table_name (str): The name of the table to retrieve.
    
    Returns:
        str: Table data or error message if table does not exist.
    """
    # Validate table name to prevent SQL injection
    query = "SHOW TABLES LIKE %s"
    df = run_query(query, (table_name,))
    
    if df.empty:
        logger.warning(f"Requested table '{table_name}' does not exist.")
        return f"Table '{table_name}' does not exist. Please check the table name and try again."
    
    # Fetch the first 5 rows of the table
    query = f"SELECT * FROM {table_name} LIMIT 5"
    table_df = run_query(query)
    
    if table_df.empty:
        logger.info(f"Table '{table_name}' is empty.")
        return f"Table '{table_name}' is empty."
    
    # Convert DataFrame to HTML table with proper formatting
    table_html = table_df.to_html(classes='dataframe table', escape=False, index=False)
    
    response = f"**First 5 Rows of {table_name}:**\n" + table_html
    logger.info(f"Provided data for table '{table_name}'.")
    return response

# Helper function to extract advisor type
def extract_advisor_type(user_message):
    """
    Extracts the advisor type (Undergraduate or Graduate) from the user message.
    
    Args:
        user_message (str): The user's message.
    
    Returns:
        str or None: 'Undergraduate' or 'Graduate' if found, else None.
    """
    message = user_message.lower()
    if "undergraduate" in message or "bs" in message:
        return "Undergraduate"
    elif "graduate" in message or "ms" in message or "phd" in message:
        return "Graduate"
    else:
        return None
