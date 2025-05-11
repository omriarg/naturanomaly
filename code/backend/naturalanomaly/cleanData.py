import ollama
import pandas as pd
import pandasql as psql
import chromadb
from typing import Dict, Callable
from chromadb.config import Settings
import re
import os
from django.conf import settings
BASE_DIR=os.path.join(settings.BASE_DIR,'naturalanomaly')
def preprocess_data(csv_path="tracked_objects.csv", persist_path="./vector_store", collection_name="tracked_data"):
    # data Cleaning and Embedding
    persist_path=os.path.join(BASE_DIR, persist_path)
    client = chromadb.PersistentClient(path=persist_path, settings=Settings(allow_reset=True))

    existing_collections = [c.name for c in client.list_collections()]
    if collection_name in existing_collections:
        print(f"✅ Vector store for '{collection_name}' already exists. Skipping preprocessing.")
        return

    df = pd.read_csv(csv_path)

    # Keep only relevant fields
    semantic_fields = ['track_id', 'object_name', 'confidence', 'time_date']
    df = df[semantic_fields]
    documents = df.apply(lambda row: ' | '.join(f"{col}: {row[col]}" for col in semantic_fields), axis=1).tolist()
    print(f"🔄 Preprocessing and embedding {len(documents)} rows...")

    collection = client.create_collection(name=collection_name)

    for i, doc in enumerate(documents):
        embedding = ollama.embed(model="mxbai-embed-large", input=doc)["embeddings"][0]
        collection.add(ids=[str(i)], documents=[doc], embeddings=[embedding])

def preprocess_data_without_embedding(df):
    # data Cleaning, reduce signal to noise
    # Keep only relevant fields
    semantic_fields = ['track_id', 'object_name', 'confidence', 'time_date','score']
    df = df[semantic_fields]
    documents = df.apply(lambda row: ' | '.join(f"{col}: {row[col]}" for col in semantic_fields), axis=1).tolist()
    return df


def preprocess_query(query, persist_path="./vector_store", collection_name="tracked_data"):
    persist_path=os.path.join(BASE_DIR, persist_path)
    client = chromadb.PersistentClient(path=persist_path, settings=Settings(allow_reset=True))
    collection = client.get_collection(name=collection_name)

    response = ollama.embed(model="mxbai-embed-large", input=query)
    query_embedding = response["embeddings"][0]

    results = collection.query(query_embeddings=[query_embedding], n_results=7)
    retrieved_data = "\n".join(results['documents'][0])
    return retrieved_data
def preprocess_query_without_embedding(video_id=1):
    csv_path=os.path.join(settings.BASE_DIR,'DataProccessor','processed_video','Video'+str(video_id),'tracked_objects.csv')
    if os.path.exists(csv_path):
         df = pd.read_csv(csv_path)
         df=  preprocess_data_without_embedding(df)
         return df.head(5)
    else:
        return ''