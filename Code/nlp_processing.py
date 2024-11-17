# nlp_processing.py
from textblob import TextBlob

def process_user_message(user_message):
    blob = TextBlob(user_message)
    keywords = [word.lemmatize() for word, pos in blob.tags if pos.startswith('NN') or pos.startswith('VB')]
    return keywords
