# ChatCat - University of Arizona Virtual Assistant, SFWE403, Fall, 2024, Professor ONeal
# Team 9

**ChatCat** is a Flask-based web application designed to serve as a virtual assistant for the University of Arizona's Software Engineering program. 
It provides users with information about programs, admissions, curriculum, financial aid, research opportunities, career prospects, 
and more through an interactive chatbot interface. Additionally, it offers functionalities like sentiment analysis and database table viewing.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Description of Each File](#description-of-each-file)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)

## Features

- **Interactive Chatbot:** Engage with ChatCat to get information about software engineering programs, admissions, curriculum, 
  financial aid, research, and career opportunities.
- **Sentiment Analysis:** Analyze the sentiment of user-provided text.
- **Database Viewer:** View and interact with database tables.
- **Responsive Design:** Accessible on various devices with a user-friendly interface.
- **Secure Database Connections:** Utilizes environment variables to manage sensitive database credentials.

## Project Structure

ChatCat/
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── images/
│   │   │   ├── background.jpg
│   │   │   └── ua_logo.jpg
├── templates/
│   ├── chatbot.html
│   ├── home.html
│   ├── sentiment.html
│   └── table.html
├── data_processing.py
├── database.py
├── handlers.py
├── intent_recognition.py
├── intents.py
├── main.py
├── model.py
├── nlp_processing.py
├── pattern_builder.py
├── requirements.txt
└── README.md


### Description of Each File

- **`main.py`**
  - The entry point of the application. Initializes the Flask app, defines routes, handles user interactions, and manages the chatbot's conversation flow.

- **`database.py`**
  - Manages database connections and queries. Utilizes MySQL Connector to interact with the MySQL database securely using environment variables.

- **`data_processing.py`**
  - Handles data loading and preprocessing tasks, such as removing duplicates, handling missing values, and cleaning text data.

- **`handlers.py`**
  - Contains functions to handle different user intents recognized by the chatbot. Each function corresponds to a specific intent and provides appropriate responses based on database queries.

- **`intent_recognition.py`**
  - Utilizes spaCy's Matcher to recognize user intents based on predefined patterns. Determines the intent behind user messages to trigger corresponding handler functions.

- **`intents.py`**
  - Defines a dictionary of intents and associated keywords or phrases used by `intent_recognition.py` for matching user messages to intents.

- **`model.py`**
  - Contains functions to train machine learning models (e.g., RandomForestClassifier) for tasks like intent classification. Evaluates model performance using classification reports.

- **`nlp_processing.py`**
  - Provides natural language processing utilities, such as extracting and lemmatizing keywords from user messages using TextBlob.

- **`pattern_builder.py`**
  - Builds matching patterns for intents using spaCy, enhancing the intent recognition capabilities of the chatbot.

- **`static/css/style.css`**
  - Defines the styling for the web application's frontend, including layout, colors, responsiveness, and component-specific styles.

- **`static/css/images/background.jpg`**
  - Background image used in the application's design.

- **`static/images/ua_logo.jpg`**
  - University of Arizona logo displayed in the application's header.

- **`templates/chatbot.html`**
  - HTML template for the chatbot interface, including the chat history, input field, and loading indicators.

- **`templates/home.html`**
  - HTML template for the home page, integrating the chatbot and additional sections like database viewer and sentiment analysis forms.

- **`templates/sentiment.html`**
  - HTML template for the sentiment analysis feature, allowing users to input text and view sentiment results.

- **`templates/table.html`**
  - HTML template for viewing database tables, displaying table contents based on user input.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System:** Windows, macOS, or Linux.
- **Python:** Python 3.7 or higher installed. [Download Python](https://www.python.org/downloads/)
- **pip:** Python package manager installed. It typically comes with Python.

### Install Dependencies

1. **Ensure you have pip updated:**

    pip install --upgrade pip

2. **Install required packages:**

    pip install Flask mysql-connector-python pandas scikit-learn textblob spacy
    python -m textblob.download_corpora
    python -m spacy download en_core_web_sm

## Configuration

### Set Up Environment Variables

The application uses environment variables to securely manage database credentials. Create a `.env` file in the project's root directory or set the variables in your system.

## Running the Application

Navigate to the Project Directory:
  cd ...\ChatCat\KatieBranchFinal\ChatCat-Repo\Code

Run the Application:
  python main.py

You should see output indicating that the Flask server is running, e.g.:
  * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)

## Access the Application:
  Open your web browser and navigate to the IP address and port where the Flask app is running. If running locally, go to:
  http://127.0.0.1:5001/
  Or use the IP address provided in the terminal output.

## Usage
Chat with ChatCat
  On the home page, interact with the chatbot by typing your queries related to software engineering programs, admissions, curriculum, etc.
  Press the 'Send' button or hit 'Enter' to submit your message.
  ChatCat will respond with relevant information based on your intent.
  
Sentiment Analysis
  Navigate to the Sentiment Analysis section.
  Enter the text you wish to analyze.
  Submit the form to view the sentiment polarity and subjectivity of the input text.
  
Database Viewer
  Use the Database Viewer form to enter the name of a table you wish to view.
  Submit the form to see the first few rows of the specified table.

## License
This project is licensed under The University of Arizona, 2024.

## Contact
For any inquiries or issues, please contact:
Name: Katie Dionne
Email: katierenee@arizona.edu
GitHub: katiereneenori
