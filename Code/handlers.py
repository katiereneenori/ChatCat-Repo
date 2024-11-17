# handlers.py (continued)

def extract_table_name(user_message):
    """
    Extracts the table name from the user message for the GetTable intent.
    """
    # Example: "get Program_Info"
    parts = user_message.lower().split()
    if len(parts) >= 2:
        return parts[-1].capitalize()  # Assuming table names are capitalized
    return None
