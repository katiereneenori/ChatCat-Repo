# database.py

import mysql.connector
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL Configuration from environment variables for security
MYSQL_ADDRESS = os.getenv('MYSQL_ADDRESS', 'chatcatserver.cxau00w82zgn.us-east-2.rds.amazonaws.com')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', 'admin')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'chatcatdb')

def get_conn_cur():
    """
    Establishes a connection to the MySQL database and returns the connection and cursor.
    """
    try:
        cnx = mysql.connector.connect(
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            host=MYSQL_ADDRESS,
            database=MYSQL_DATABASE,
            port='3306'
        )
        cursor = cnx.cursor()
        logger.info("Database connection established successfully.")
        return cnx, cursor
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to database: {err}")
        return None, None

def run_query(query_string, params=None):
    """
    Executes a SQL query and returns the result as a pandas DataFrame.
    """
    conn, cur = get_conn_cur()
    if conn is None or cur is None:
        logger.error("Database connection failed. Cannot execute query.")
        return pd.DataFrame()  # Return empty DataFrame on connection failure

    try:
        if params:
            cur.execute(query_string, params)
            logger.info(f"Executing query with params: {query_string} | {params}")
        else:
            cur.execute(query_string)
            logger.info(f"Executing query: {query_string}")
        my_data = cur.fetchall()
        columns = cur.column_names
        result_df = pd.DataFrame(my_data, columns=columns)
        logger.info("Query executed and data fetched successfully.")
    except mysql.connector.Error as err:
        logger.error(f"Error executing query: {err}")
        result_df = pd.DataFrame()
    finally:
        cur.close()
        conn.close()
        logger.info("Database connection closed.")

    return result_df
