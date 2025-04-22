import ollama
import pandas as pd
import pandasql as psql
import chromadb
from typing import Dict, Callable
from chromadb.config import Settings
import re
def preprocess_data(csv_path="tracked_objects.csv", persist_path="./vector_store", collection_name="tracked_data"):
    # data Cleaning and Embedding
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


def preprocess_query(query, persist_path="./vector_store", collection_name="tracked_data"):
    client = chromadb.PersistentClient(path=persist_path, settings=Settings(allow_reset=True))
    collection = client.get_collection(name=collection_name)

    response = ollama.embed(model="mxbai-embed-large", input=query)
    query_embedding = response["embeddings"][0]

    results = collection.query(query_embeddings=[query_embedding], n_results=7)
    retrieved_data = "\n".join(results['documents'][0])
    return retrieved_data
