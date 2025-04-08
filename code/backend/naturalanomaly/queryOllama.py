import ollama
import pandas as pd
import pandasql as psql
from typing import Dict, Callable


def chatWithOllama(query: str) -> str:
    """
    Query Ollama with a user prompt and determine whether to use an SQL tool or a direct response.

    Args:
        query (str): The user's input question.

    Returns:
        str: The result of either tool execution or Ollama's response.
    """
    messages = [
        {
            'role': 'system',
            'content': (
                "You are a helpful assistant that determines whether a query requires SQL execution or a general response.\n"
                "you have access to a file track_objects which is a file with data outputted from an object detection routine"
                "- If the user asks about tracked object data (e.g., confidence scores, track IDs), use `execute_sql`.\n"
                "- If the question is general (e.g., 'What is your role?'), use `respond_to_user`.\n\n"
                "**Examples:**\n"
                "- ✅ 'What is the highest confidence for track_id 413?' → Use execute_sql\n"
                "- ✅ 'How does YOLO work?' → Use respond_to_user\n"
                "- ❌ 'What is your role?' → Use respond_to_user\n"
            ),
        },
        {'role': 'user', 'content': query},
    ]


    try:
        response = ollama.chat(
            model='llama3.2',
            messages=messages,
        )

        return response.message.content  # Return Ollama's direct response if no tool is needed

    except Exception as e:
        return f"Error during Ollama API call: {e}"
