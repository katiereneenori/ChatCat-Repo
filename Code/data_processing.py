import pandas as pd
import re
from sklearn.model_selection import train_test_split

def load_and_process_data(file_path):
    # Load the dataset
    df = pd.read_csv(file_path) 

    # Step 1: Remove duplicates
    df.drop_duplicates(inplace=True)

    # Step 2: Handle missing values
    df.dropna(subset=['question', 'answer'], inplace=True) 

    # Step 3: Clean text data
    df['question'] = df['question'].apply(clean_text)

    # Step 4: Reset index after processing
    df.reset_index(drop=True, inplace=True)

    return df

def clean_text(text):
    # Basic text cleaning function
    text = text.lower()  
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = text.strip()  # Remove leading and trailing spaces
    return text
