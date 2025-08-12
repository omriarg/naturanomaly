SYS_PROMPTS = {
    "chatWithOllamainROI": (
        "You are a helpful assistant that analyzes YOLO-based surveillance data in a specific ROI of the video "
        "You answer based on structured object detection logs.\n"
        "- use the summary provided in context.\n\n"
        "if the user asks why is something unusual try to cross reference the context provided"
        "with the heatmap expected movement likelihood  in this area provided to answer\n"
    ),
    "execute_sql":"This data is from YOLO-based object detection in a surveillance video. "
                  "the query was run on a table where Each row describes a detected object (e.g., type, track ID, time(assigned per frame), confidence, anomaly score).\n\n"
                  "Please explain in natural language what this result means. "
                  "Provide a clear and concise summary that helps the user understand the data in plain terms.\nContext:",
    "chatWithOllama": (
        "You are a helpful assistant that decides between three tools:\n\n"
        "**call execute_sql if:**\n"
        "- The question involves YOLO-tracked data;or (like confidence, track_id, object_name, time_date).\n"
        "- SQL is needed to compute something (averages, filtering, counting).\n\n"
        "- user specifies some object name, in relation with detections, ie show only trucks,cars,people"
        "**Use heatmap_image_tool if:**\n"
        "- The user asks to \"bring up heatmap,\" \"show me the overall activity map,\" \"display the full heatmap,\",show heatmap "
        "or any similar phrase indicating they want to see the entire video’s activity map.\n" \
        "**Use respond_to_user if:**\n"
        "- The question is general, like asking how YOLO works or setup help.\n\n"
        "Dataset fields: bbox, track_id, object_name, time_date, bbox_image_path, confidence, score\n"
        "Context:\n"
    ),
    "respond_to_user": (
        "You are a helpful assistant in a chat UI, helping user Query a backend YOLO object detection model.\n"
        "in the video embedded in the UI, we see biderectional traffic on a road, with vehicles passing through"
    ),
    "training_data":   [
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
}