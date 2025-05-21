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
def chatWithOllamainROI(query: str, bbox=None, video_id=1) -> str:
    if vn is None or video_id != current_video_id:
        set_video_context(video_id=video_id)

    if not bbox:
       return "Error: No bounding box (ROI) provided."

    try:
        x1, y1, x2, y2 = bbox
    except Exception as e:
        return f"Invalid bounding box format: {e}"

    region_df = pd.DataFrame(anomalies_in_region(df, x1, y1, x2, y2))
    if region_df.empty:
        return "No data available in the selected region this is a dead zone."

    # Use keywords to infer what the user wants
    is_history = "all people" in query.lower() or "past week" in query.lower()
    context = summarize_roi_events(region_df, full_history=is_history)
    print(context)
    messages = [
        {
            'role': 'system',
            'content': (
                "You are a helpful assistant that analyzes YOLO-based surveillance data. "
                "You answer based on structured object detection logs.\n"
                "- Use SQL if the user asks about counts, filters, or stats.\n"
                "- Otherwise, use the summary provided in context.\n\n"
                "Fields available: bbox, track_id, object_name, time_date, confidence, score\n\n"
                f"Context from coordinates {bbox}:\n{context}"
            )
        },
        {'role': 'user', 'content': query}
    ]

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=messages,
        )

        # if response.message.tool_calls:
        #     for tool in response.message.tool_calls:
        #         function_to_call = {
        #             'execute_sql': execute_sql,
        #             'respond_to_user': respond_to_user
        #         }.get(tool.function.name)
        #         if function_to_call:
        #             return function_to_call(**tool.function.arguments)

        return response.message.content

    except Exception as e:
        return f"Error during Ollama call: {e}"
def summarize_roi_events(region_df: pd.DataFrame, top_n: int = 5, full_history: bool = False) -> str:
    """
    Summarize the most anomalous or all tracked events in a region of interest (ROI).
    Args:
        region_df (pd.DataFrame): Data filtered by bounding box.
        top_n (int): Number of top anomalies to include (if not full_history).
        full_history (bool): If True, include all events in the region.

    Returns:
        str: A descriptive summary of events or anomalies.
    """
    if region_df.empty:
        return "No tracked objects found in the selected region."

    # Use top anomalies or full event list
    if full_history:
        df = region_df.sort_values(by="time_date")
    else:
        df = region_df.sort_values(by="score", ascending=False).head(top_n)

    summaries = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        try:
            timestamp = row.get('time_date', 'unknown time')
            object_name = row.get('object_name', 'unknown object')
            track_id = row.get('track_id', 'N/A')
            confidence = float(row.get('confidence', 0))
            score = float(row.get('score', 0))
            bbox = row.get('bbox', '[bbox missing]')
            summary = (
                f"{i}. At **{timestamp}**, a **{object_name}** (track ID `{track_id}`) "
                f"was detected at **{bbox}** with confidence **{confidence:.2f}** and anomaly score **{score:.2f}**."
            )
            summaries.append(summary)
        except Exception as e:
            summaries.append(f"{i}. (Error parsing row: {e})")

    return "\n".join(summaries)

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
                "**call `execute_sql` if:**\n"
                "- The question involves YOLO-tracked data;or (like confidence, track_id, object_name, time_date).\n"
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
def parse_bbox(bbox_str):
    # bbox_str example: "[428, 495, 523, 576]"
    return ast.literal_eval(bbox_str)  # converts string to list of ints

def anomalies_in_region(df, x1, y1, x2, y2, threshold=0.8):
    """
    Returns list of anomalies in df whose bbox overlaps given region and
    whose score exceeds threshold.
    """
    anomalies = []

    def bbox_inside_region(bbox):
        bx1, by1, bx2, by2 = bbox
        # Check if bbox overlaps with the region
        return  bx2 >= x1 and bx1 <= x2 and by2 >= y1  and by1 <= y2



    for idx, row in df.iterrows():
        bbox = parse_bbox(row['bbox'])
        score = row['score']

        if score > threshold and bbox_inside_region(bbox):
            anomalies.append(row.to_dict())

    return anomalies
