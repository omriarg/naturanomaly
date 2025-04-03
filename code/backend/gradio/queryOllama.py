from ollama import chat
from ollama import ChatResponse
def queryOllama(query):
    response: ChatResponse = chat(
        model='llama3.2',  # Replace with the model you're using
        messages=[
            {
                'role': 'system',  # Define system role clearly
                'content': (
                    "You are an AI assistant in a project where users query a web chat interface "
                    "about a backend YOLO model that analyzes and detects objects and anomalies. "
                    "Users can upload videos and ask questions about the videos. Tool support will be added soon, "
                    "and we are sorry for the wait."
                ),
            },
            {
                'role': 'user',  # User's query
                'content': query,
            },
        ]
    )

    # or access fields directly from the response object
    return response.message.content