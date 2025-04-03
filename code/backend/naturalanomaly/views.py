from django.http import HttpResponse
import json
from ollama import chat
from ollama import ChatResponse

def queryOllama(query):
    body = query.body
    response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': query.query,
        },
    ])
    print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)
    return HttpResponse(response.message.content)