import base64
import pickle

import cv2
import pandas as pd
import pandasql as psql
from matplotlib import pyplot as plt
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

    current_video_id = video_id

    vn = MyVanna(config={
        'model': 'llama3.2:3b',
        'path': os.path.join(BASE_DIR, 'vector_store')
    })

    df = pd.read_csv(os.path.join(VIDEO_DIR, f'Video{video_id}', 'tracked_objects.csv'))

    # SQL Runner
    def run_sql(sql):
        try:
            return preprocess_data_without_embedding(psql.sqldf(sql, {'df': df}))
        except Exception as e:
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
        result = vn.generate_sql(query,allow_llm_to_see_data=True)
        return vn.run_sql(result)
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
    lowercase_query=query.lower()
    full_history = "all people" in lowercase_query or "past week" in lowercase_query or "list all" in lowercase_query
    if(full_history):#user wants full history of region return df
        return region_df.sort_values(by="time_date")
    context = summarize_roi_events(region_df)
    probability_of_movement=compute_roi_probability_from_pickle(video_id=video_id,bbox=bbox)
    unusuality_explanation= analyze_most_unusual_event(region_df, likelihood=probability_of_movement)
    messages = [
        {
            'role': 'system',
            'content': (
                "You are a helpful assistant that analyzes YOLO-based surveillance data in a specific ROI of the video "
                "You answer based on structured object detection logs.\n"
                "- use the summary provided in context.\n\n"
                "if the user asks why is something unusual try to cross reference the context provided"
                "with the heatmap expected movement likelihood   in this area provided to answer"
                f"Context from coordinates {bbox}:\n{context}"
                f"roi expected movement likelihood:{probability_of_movement}"
                "if the user asks what happens here? or something that hints at a general explanation of the events in the ROI, use summary to give explanation"
                f"if the user asks why is something unusual use the explanation more: {unusuality_explanation}"
            )
        },
        {'role': 'user', 'content': query}
    ]

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=messages,
        )


        return response.message.content

    except Exception as e:
        return f"Error during Ollama call: {e}"


def analyze_most_unusual_event(region_df, likelihood):
    if region_df.empty:
        return "There are no events in the selected region to analyze."

    # Get the most unusual event — e.g., rarest object
    object_counts = region_df['object_name'].value_counts()
    rarest_object = object_counts.idxmin()
    rarest_count = object_counts.min()
    total_objects = object_counts.sum()
    ratio = rarest_count / total_objects if total_objects else 0

    cooccur_msg = ""

    if 'time_date' in region_df.columns:
        # Check what co-occurs with the rarest object
        timestamps = region_df[region_df['object_name'] == rarest_object]['time_date'].unique()
        cooccur_objs = region_df[region_df['time_date'].isin(timestamps)]['object_name'].unique()
        cooccur_objs = [obj for obj in cooccur_objs if obj != rarest_object]
        if cooccur_objs:
            cooccur_msg = f" It co-occurred with: {', '.join(cooccur_objs)}."

    # Construct explanation
    if likelihood < 0.3 and ratio < 0.1:
        return (
                f"The most unusual event is the appearance of a **{rarest_object}**, "
                f"seen only {rarest_count} times out of {total_objects} ({ratio:.2%}). "
                f"This region also has a low expected movement likelihood ({likelihood:.2f})." +
                cooccur_msg
        )
    elif ratio < 0.1:
        return (
                f"The most unusual event is the **{rarest_object}**, which is rarely seen in this area "
                f"({rarest_count} out of {total_objects} detections, {ratio:.2%})." +
                cooccur_msg
        )
    elif likelihood < 0.3:
        return (
                f"While the **{rarest_object}** appears with some frequency, this ROI has low movement probability ({likelihood:.2f})." +
                cooccur_msg
        )
    else:
        return f"Nothing stands out as particularly unusual in this ROI."

def summarize_roi_events(region_df: pd.DataFrame, top_n: int = 5) -> str:
    """
    Summarize the most anomalous or all tracked events in a region of interest (ROI).

    Args:
        region_df (pd.DataFrame): Data filtered by bounding box.
        top_n (int): Number of top anomalies to include.

    Returns:
        str: A descriptive summary of events or anomalies.
    """
    if region_df.empty:
        return "No tracked objects found in the selected region."

    # Use top anomalies
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

    # Add object type counts from full region_df
    object_counts = region_df['object_name'].value_counts()
    counts_summary = "\n".join(
        f"- **{obj}**: {count} object(s) passed through the area"
        for obj, count in object_counts.items()
    )

    summaries.append("\n**Summary of object types in the region:**\n" + counts_summary)

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
                    "in the video embedded in the UI, we see biderectional traffic on a road, with vehicles passing through"

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
                "You are a helpful assistant that decides between three tools:\n\n"
                "**call `execute_sql` if:**\n"
                "- The question involves YOLO-tracked data;or (like confidence, track_id, object_name, time_date).\n"
                "- SQL is needed to compute something (averages, filtering, counting).\n\n"
                "- user specifies some object name, in relation with detections, ie show only trucks,cars,people"
                "**Use `heatmap_image_tool` if:**\n"
                "- The user asks to \"bring up heatmap,\" \"show me the overall activity map,\" \"display the full heatmap,\",show heatmap "
                "or any similar phrase indicating they want to see the entire video’s activity map.\n" \
                "**Use `respond_to_user` if:**\n"
                "- The question is general, like asking how YOLO works or setup help.\n\n"
                "Dataset fields: bbox, track_id, object_name, time_date, bbox_image_path, confidence, score\n"
                f"Context:\n{Context}"
            )
        },
        {'role': 'user', 'content': query}
    ]

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=messages,
            tools=[execute_sql, respond_to_user,heatmap_image_tool],  # Passing function references directly
        )
        response_content=response.message.content.lstrip()
        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                function_name = tool_call.function.name
                ##account for failure ollama failure in tool call
                if function_name == 'execute_sql':
                    return execute_sql(query)
                elif function_name == 'heatmap_image_tool':
                    return extract_bbox_from_heatmap_cv(video_id=video_id,bbox=None)
                elif function_name == 'respond_to_user':
                    return respond_to_user(query=query)
                else:
                    return f"Unknown tool: {function_name}"
        ##ollama sometimes try to answer with tool call parameters as a response,account for it
        elif response_content.startswith('{"name":"execute_sql'):
            return execute_sql(query)
        elif response_content.startswith('{"name":"heatmap_image_tool'):
            return respond_to_user(query=query)
        elif response_content.startswith('{"name":"respond_to_user'):
            return extract_bbox_from_heatmap_cv(video_id=video_id,bbox=None)
        else:
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

def compute_roi_probability_from_pickle(video_id=1, bbox=None):
    if(bbox is None):
        return
    current_video=f'Video{video_id}'
    pickle_filename='routine_map.pkl'
    pickle_path=os.path.join(VIDEO_DIR,current_video,pickle_filename)
    with open(pickle_path, 'rb') as f:
        routine_map = pickle.load(f)  #load heatmap

    x1, y1, x2, y2 = bbox

    sum_prob = 0.0
    count = 0

    for i in range(y1, y2):
        for j in range(x1, x2):
            if 0 <= i < len(routine_map) and 0 <= j < len(routine_map[0]):
                sum_prob += routine_map[i][j]
                count += 1

    if count == 0:
        return 0.0

    return sum_prob / count
def extract_bbox_from_heatmap_cv(video_id=1, bbox=None):
    """
    Extract a region from the heatmap image using OpenCV and a bounding box.

    Args:
        video_id (int): ID of the video.
        bbox (list or None): Bounding box [x1, y1, x2, y2], or None for full image.

    Returns:
        str: Base64-encoded PNG image string.
    """
    img_path = os.path.join(VIDEO_DIR, f'Video{video_id}', 'heat_map_display.png')
    img = cv2.imread(img_path)

    if img is None:
        raise FileNotFoundError(f"Image not found at path: {img_path}")

    # Crop the image only if bbox is provided
    if bbox is None:
        region = img
    else:
        x1, y1, x2, y2 = bbox
        region = img[y1:y2, x1:x2]

    success, buffer = cv2.imencode('.png', region)
    if not success:
        raise ValueError("Failed to encode image as PNG")

    base64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"
def heatmap_likelihood_tool(video_id=1, bbox=None) -> str:
    """Return a natural language explanation of unusual activity likelihood."""
    if bbox:
        likelihood = compute_roi_probability_from_pickle(video_id, bbox)
        if likelihood is None:
            return "No heatmap likelihood data available for this region."
        return (f"Based on the likelihood of movement in the specified region, "
                f"the activity is {'likely normal' if likelihood > 0.8 else 'unlikely or unusual'} "
                f"(probability score: {likelihood:.2f}).")
    else:
        return "Please specify a region to compute likelihood."

def heatmap_image_tool(video_id=1, bbox=None) -> str:
    """Return base64 encoded heatmap image, cropped if bbox given."""
    try:
        img_base64 = extract_bbox_from_heatmap_cv(video_id, bbox)
        return img_base64 # Return base64 string for rendering image in UI
    except Exception as e:
        return f"Error retrieving heatmap image: {e}"