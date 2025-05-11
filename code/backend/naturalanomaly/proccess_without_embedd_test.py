from pathlib import Path

import ollama
import pandas as pd
import pandasql as psql
import chromadb
from typing import Dict, Callable
from chromadb.config import Settings
import re
import os
def preprocess_data_without_embedding(df):
    # data Cleaning, reduce signal to noise
    # Keep only relevant fields
    semantic_fields = ['track_id', 'object_name', 'confidence', 'time_date','score']
    df = df[semantic_fields]
    documents = df.apply(lambda row: ' | '.join(f"{col}: {row[col]}" for col in semantic_fields), axis=1).tolist()
    return df
def preprocess_query_without_embedding(video_id=1):
    parent_dir = Path(os.getcwd()).parent
    csv_path = os.path.join(parent_dir, 'DataProccessor', 'processed_video', f'Video{video_id}', 'tracked_objects.csv')
    csv_filename=csv_path
    if os.path.exists(csv_filename):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_filename)

        # Drop rows where 'score' is NaN
        df_cleaned = df.dropna(subset=['score'])

        # Resave the cleaned DataFrame back to the CSV file
        df_cleaned.to_csv(csv_filename, index=False)
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = preprocess_data_without_embedding(df)
        # Return the first 5 results where score is not NaN
        return df.head(5)
    else:
        return csv_path

Context = preprocess_query_without_embedding(1)
print(Context)