# pattern_builder.py

import spacy
from spacy.matcher import Matcher
from intents import intents

def create_patterns(nlp, intents_dict):
    matcher = Matcher(nlp.vocab)
    for intent, phrases in intents_dict.items():
        patterns = []
        for phrase in phrases:
            doc = nlp(phrase.lower())
            pattern = [{"LOWER": token.text.lower()} for token in doc]
            patterns.append(pattern)
        matcher.add(intent, patterns)
    return matcher
