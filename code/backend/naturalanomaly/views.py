from django.http import JsonResponse, HttpResponse
import json
from ollama import chat
from ollama import ChatResponse
from .queryOllama import *

from django.http import JsonResponse
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

@api_view(['POST'])
def queryOllama(request):
    print('query')
    data = json.loads(request.body)
    query = data.get('message')
    if query:
        response = chatWithOllama(query)
        return Response({'response': response})
    else:
        return Response({'error': 'Missing query parameter'}, status=400)



