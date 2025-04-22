import ollama
import pandas as pd
import pandasql as psql
import chromadb
from typing import Dict, Callable
from chromadb.config import Settings
import re
import vanna as vn
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


def execute_sql(query: str) -> str:
    """
    This function executes an SQL query on the tracked_objects CSV data and returns the result in table format.'
    use this Function only when user prompt specifically ask about the Data, and not when asking general questions'
    Use this example data for reference: '
    bbox, track_id, object_name, time_date, bbox_image_path, confidence, score\n'

    Args:
        query (str): The SQL query to execute on the dataset.

    Returns:
        str: The result of the SQL query in table format.
    """
    try:
        data = pd.read_csv("tracked_objects.csv")
        result = psql.sqldf(query, {"tracked_objects": data})
        return result.to_string(index=False)
    except Exception as e:
        return f"Error executing SQL query: please clarify your question"


def respond_to_user(query: str) -> str:
    """
    Ask Ollama a general question (not related to SQL queries).

    Args:
        query (str): The user's input question unaltered.

    Returns:
        str: Ollama's direct response.
    """
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[ {
                'role': 'system',
                'content': (
                    "You are a helpful assistant in a chat UI, helping user Query a backend YOLO object detection model.\n"
                ),
            },
                {'role': 'user', 'content': query}],
        )
        return response.message.content
    except Exception as e:
        return f"Error during Ollama API call: {e}"


def chatWithOllama(query: str) -> str:
    """
    Query Ollama with a user prompt and determine whether to use an SQL tool or a direct response.

    Args:
        query (str): The user's input question.

    Returns:
        str: The result of either tool execution or Ollama's response.
    """
    Context = preprocess_query(query)

    messages = [
        {
            'role': 'system',
            'content': (
                "You are a helpful assistant that determines whether a query requires SQL execution or a general response.\n"
                "- If the user asks about tracked object data (e.g., confidence scores, track IDs, object name), use `execute_sql`.\n"
                "- If the question is general (e.g., 'What is your role?'), use `respond_to_user`.\n\n"
                "Here is a sample of the data schema:\n"
                "(bbox, track_id, object_name, time_date, bbox_image_path, confidence, score)\n"

            ),
        },
        {'role': 'user', 'content':f"using this related data{Context} answer this:" + query},
    ]
    available_functions: Dict[str, Callable] = {
        'execute_sql': execute_sql,
        'respond_to_user': respond_to_user,
    }

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=messages,
            tools=[execute_sql, respond_to_user],  # Passing function references directly
        )

        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                function_to_call = available_functions.get(tool.function.name)
                if function_to_call:
                    return function_to_call(**tool.function.arguments)

        return response.message.content  # Return Ollama's direct response if no tool is needed

    except Exception as e:
        return f"Error during Ollama API call: {e}"
