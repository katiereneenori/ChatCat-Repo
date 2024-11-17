# intent_recognition.py

import spacy
from spacy.matcher import Matcher
from intents import intents

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Add patterns for each intent
for intent, keywords in intents.items():
    patterns = []
    for keyword in keywords:
        pattern = [{"LOWER": token} for token in keyword.split()]
        patterns.append(pattern)
    matcher.add(intent, patterns)

def recognize_intent(user_message):
    """
    Recognizes the intent of the user message using spaCy's Matcher.
    """
    doc = nlp(user_message.lower())
    matches = matcher(doc)
    if matches:
        # Return the first matched intent
        match_id, start, end = matches[0]
        intent = nlp.vocab.strings[match_id]
        return intent
    return "Unknown"
