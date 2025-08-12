from .SysPrompts_LLM import SYS_PROMPTS
from .cleanData import *
import ollama
from .Tools_and_Context_LLM import *
from .VideoContextManager import VannaVideoWrapper
def chatWithOllamainROI(query: str, video_session:VannaVideoWrapper, bbox=None) -> str:
    # ensure the wrapper is on the right video (no retrain/reinit)
    if not bbox:
        return "Error: No bounding box (ROI) provided."

    try:
        x1, y1, x2, y2 = bbox
    except Exception as e:
        return f"Invalid bounding box format: {e}"

    region_df = pd.DataFrame(anomalies_in_region(video_session.df, x1, y1, x2, y2))
    if region_df.empty:
        return "No data available in the selected region this is a dead zone."

    # keyword inference
    lowercase_query = query.lower()
    full_history = ("all people" in lowercase_query) or ("past week" in lowercase_query) or ("list all" in lowercase_query)
    if full_history:
        return region_df.sort_values(by="time_date")

    context = summarize_roi_events(region_df)
    probability_of_movement = compute_roi_probability_from_pickle(video_session=video_session, bbox=bbox)
    unusuality_explanation = analyze_most_unusual_event(region_df, likelihood=probability_of_movement)

    Context = (
        f"\nContext from coordinates {bbox}:\n{context}\n"
        f"movement likelihood in this area: {probability_of_movement:.2f}\n"
        "if the user asks what happens here? or something that hints at a general explanation of the events in the ROI, use summary to give explanation\n"
        f"if the user asks why is something unusual use the explanation more: {unusuality_explanation}"
    )

    messages = [
        {"role": "system", "content": (SYS_PROMPTS["chatWithOllamainROI"] + Context)},
        {"role": "user", "content": query},
    ]

    try:
        response = ollama.chat(model=video_session.model, messages=messages)
        return response.message.content
    except Exception as e:
        return f"Error during Ollama call: {e}"


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
                'content': SYS_PROMPTS["respond_to_user"],
            },
                {'role': 'user', 'content': query}],
        )
        return response.message.content
    except Exception as e:
        return f"Error during Ollama API call: {e}"

def chatWithOllama(query: str, video_session:VannaVideoWrapper) -> str:
    video_id=video_session.get_video_id()
    if(video_id==1):
        Context = preprocess_query(query) #use embedded data for default video
    else:
        Context=preprocess_query_without_embedding(video_id=video_id)#get some lines from DF otherwise
    messages = [
        {
            'role': 'system',
            'content': SYS_PROMPTS["chatWithOllama"] + Context
        },
        {'role': 'user', 'content': query}
    ]

    try:
        response = ollama.chat(
            model=video_session.model,
            messages=messages,
            tools=[video_session.execute_sql, respond_to_user, heatmap_image_tool],  # Passing function references directly
        )
        response_content=response.message.content.lstrip()
        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                function_name = tool_call.function.name
                ##account for failure ollama failure in tool call
                if function_name == 'execute_sql':
                    return video_session.execute_sql(query)
                elif function_name == 'heatmap_image_tool':
                    return heatmap_image_tool(video_session=video_session)
                elif function_name == 'respond_to_user':
                    return respond_to_user(query=query)
                else:
                    return f"Unknown tool: {function_name}"
        ##ollama sometimes try to answer with tool call parameters as a response,account for it
        elif response_content.startswith('{"name":"execute_sql'):
            return video_session.execute_sql(query)
        elif response_content.startswith('{"name":"heatmap_image_tool'):
            return heatmap_image_tool(video_session=video_session)
        elif response_content.startswith('{"name":"respond_to_user'):
            return respond_to_user(query=query)

        else:
            return response.message.content  # Rturn Ollama's direct response if no tool is needed

    except Exception as e:
        return f"Error during Ollama API call: {e}"
