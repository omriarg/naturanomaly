import pandas as pd
import pandasql as psql
from vanna.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from .cleanData import *
import os
# Define a custom Vanna class combining Ollama and ChromaDB
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)
# Initialize Vanna with model and ChromaDB vector store

vn = MyVanna(config={
    'model': 'llama3.2:3b',
    'persist_directory': os.path.join(BASE_DIR,'vector_store')
})
# Load CSV as DataFrame
df = pd.read_csv(os.path.join(BASE_DIR,'tracked_objects.csv'))
# Define SQL runner on DataFrame using pandasql
def run_sql(sql):
    try:
        return psql.sqldf(sql, {'df': df})
    except Exception as e:
        print(f"SQL execution error: {e}")
        return pd.DataFrame()
# Register run_sql with Vanna
vn.run_sql = run_sql
vn.run_sql_is_set = True
print("DataFrame connected and SQL runner set.")

# Train Vanna with questions and SQL queries
training_data = [
    ("Which track_id had the lowest confidence score?",
     "SELECT track_id, MIN(confidence) AS lowest_confidence FROM df GROUP BY track_id ORDER BY lowest_confidence ASC LIMIT 1;"),

    ("What are the top 5 object types by average confidence?",
     "SELECT object_name, AVG(confidence) AS avg_confidence FROM df GROUP BY object_name ORDER BY avg_confidence DESC LIMIT 5;"),

    ("What is the average score for each track_id?",
     "SELECT track_id, AVG(score) AS avg_score FROM df GROUP BY track_id ORDER BY avg_score DESC;"),

    ("How many unique object types were detected?",
     "SELECT COUNT(DISTINCT object_name) AS unique_object_types FROM df;"),

    ("Which track_id had the most recent detection?",
     "SELECT track_id, MAX(time_date) AS last_seen FROM df GROUP BY track_id ORDER BY last_seen DESC LIMIT 1;"),

    ("What is the average confidence score across the dataset?",
     "SELECT AVG(confidence) AS overall_avg_confidence FROM df;")
]

for question, sql in training_data:
    vn.train(question=question, sql=sql)

def execute_sql(query):
    try:
        print(query)
        result = vn.generate_sql(query,allow_llm_to_see_data=True)
        return run_sql(result).to_string()
    except Exception as e:
        return f"Error in vn.ask: {e}"

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
                "You are a helpful assistant that decides whether to use an internal SQL tool or give a general response.\n"
                "- If the user asks a question that relates to the df (e.g., confidence scores, object names, track IDs), "
                "and it would require querying data, then simply pass the **original user query unchanged** to the `execute_sql` function.\n"
                "- **Do NOT attempt to write or modify SQL yourself.** The SQL tool will handle interpretation.\n"
                "- If the question is general or unrelated to tracked data, use the `respond_to_user` function instead.\n\n"
                "Available fields in the dataset are:\n"
                "(bbox, track_id, object_name, time_date, bbox_image_path, confidence, score)\n"
                "Base your judgment on whether the query requires analyzing this data."
                f'added context:{Context}'
            ),
        },
        {'role': 'user', 'content': query}
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
                # Ensure that the original query is passed to the SQL execution tool
                if tool.function.name == 'execute_sql':
                    return execute_sql(query)  # Pass the original user query directly

                function_to_call = available_functions.get(tool.function.name)
                if function_to_call:
                    return function_to_call(**tool.function.arguments)


        return response.message.content  # Return Ollama's direct response if no tool is needed

    except Exception as e:
        return f"Error during Ollama API call: {e}"
