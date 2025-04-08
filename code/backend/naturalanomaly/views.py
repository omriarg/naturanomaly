from django.http import JsonResponse, HttpResponse
import json
from ollama import chat
from ollama import ChatResponse
from .queryOllama import *

def queryOllama(request):
    if request.method == "POST":#no video_id use for now
            data = json.loads(request.body)#get ollama query
            query = data['message']
            response = chatWithOllama(query)
            return HttpResponse(response)
    else:
        return  HttpResponse({'error': 'Only POST requests are allowed'}, status=405)

