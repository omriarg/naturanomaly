import os
import cv2
import ast
import base64
import pickle
import pandas as pd
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

def compute_roi_probability_from_pickle(video_session, bbox=None):
    if(bbox is None):
        return
    VIDEO_DIR=video_session.get_video_dir()
    pickle_path=os.path.join(VIDEO_DIR,f'Video{video_session.get_video_id()}','routine_map.pkl')
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
def extract_bbox_from_heatmap_cv(video_session, bbox=None):
    """
    Extract a region from the heatmap image using OpenCV and a bounding box.

    Args:
        video_id (int): ID of the video.
        bbox (list or None): Bounding box [x1, y1, x2, y2], or None for full image.

    Returns:
        str: Base64-encoded PNG image string.
    """
    VIDEO_DIR=video_session.get_video_dir()
    img_path = os.path.join(VIDEO_DIR, f'Video{video_session.get_video_id()}', 'heat_map_display.png')
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

def heatmap_image_tool(video_session) -> str:
    """Return base64 encoded heatmap image, cropped if bbox given."""
    try:
        img_base64 = extract_bbox_from_heatmap_cv(video_session, bbox=None)
        return img_base64 # Return base64 string for rendering image in UI
    except Exception as e:
        return f"Error retrieving heatmap image: {e}"

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
