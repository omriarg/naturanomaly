import pandas as pd
import pandasql as psql
from vanna.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from .cleanData import *
import os
import ast

vn = None
df = None
current_video_id = None
VIDEO_DIR = os.path.join(settings.BASE_DIR, 'DataProccessor', 'processed_video')
# Define a custom Vanna class combining Ollama and ChromaDB
class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)
# Initialize Vanna with model and ChromaDB vector store
def set_video_context(video_id=1):
    global vn, df, current_video_id

    if current_video_id == video_id:
        return  # already loaded

    print(f"Loading data for video_id={video_id}")
    current_video_id = video_id

    vn = MyVanna(config={
        'model': 'llama3.2:3b',
        'path': os.path.join(BASE_DIR, 'vector_store')
    })

    df = pd.read_csv(os.path.join(VIDEO_DIR, f'Video{video_id}', 'tracked_objects.csv'))

    # SQL Runner
    def run_sql(sql):
        try:
            return psql.sqldf(sql, {'df': df})
        except Exception as e:
            print(f"SQL execution error: {e}")
            return pd.DataFrame()

    vn.run_sql = run_sql
    vn.run_sql_is_set = True

    # Training
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
         "SELECT AVG(confidence) AS overall_avg_confidence FROM df;"),
        ("What is the busiest time?",
         "SELECT time_date, COUNT(*) AS detection_count FROM df GROUP BY time_date ORDER BY detection_count DESC LIMIT 1;")
    ]
    for question, sql in training_data:
        vn.train(question=question, sql=sql)

def execute_sql(query):
    try:
        print(query)
        result = vn.generate_sql(query,allow_llm_to_see_data=True)
        return vn.run_sql(result).to_string()
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


def chatWithOllama(query: str,video_id=1) -> str:
    """
    Query Ollama with a user prompt and determine whether to use an SQL tool or a direct response.
    Args:
        query (str): The user's input question.
    Returns:
        str: The result of either tool execution or Ollama's response.
    """
    if(vn is None or video_id!=current_video_id):
        set_video_context(video_id=video_id)
    if(video_id==1):
        Context = preprocess_query(query) #use embedded data for default video
    else:
        Context=preprocess_query_without_embedding(video_id=video_id)#get some lines from DF otherwise
    messages = [
        {
            'role': 'system',
            'content': (
                "You are a helpful assistant that decides between two tools:\n\n"
                "**Use `execute_sql` if:**\n"
                "- The question involves YOLO-tracked data (like confidence, track_id, object_name, time_date).\n"
                "- SQL is needed to compute something (averages, filtering, counting).\n\n"
                "**Use `respond_to_user` if:**\n"
                "- The question is general, like asking how YOLO works or setup help.\n\n"
                "Dataset fields: bbox, track_id, object_name, time_date, bbox_image_path, confidence, score\n"
                f"Context:\n{Context}"
            )
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


        return response.message.content  # Rturn Ollama's direct response if no tool is needed

    except Exception as e:
        return f"Error during Ollama API call: {e}"

def anomalies_in_region(tracked_objects_df, x1, y1, x2, y2, threshold=2.0):
    def is_inside_region(bbox):
        bbox = ast.literal_eval(bbox)  # safely parse string list
        bx1, by1, bx2, by2 = bbox
        #Check if any part of the bbox is inside the region
        return not (bx2 < x1 or bx1 > x2 or by2 < y1 or by1 > y2)

    anomalies = tracked_objects_df[
        (tracked_objects_df['log_likelihood_score'] > threshold) &
        (tracked_objects_df['bbox'].apply(is_inside_region))
        ]
    return anomalies
