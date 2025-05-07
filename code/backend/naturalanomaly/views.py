from .queryOllama import *


from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from .models import Video
from DataProccessor.proccesVideoModule import process_video
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


@api_view(['POST'])
def processVideo(request):
    data = json.loads(request.body)
    video_url = data.get('video_url')

    if video_url:
        try:
            # Call the process_video function and get the response
            response = process_video(video_url)
            # Check if the response is a dictionary
            if isinstance(response, dict):
                # Extract csv_path and video_id from the response
                csv_path = response.get('csv_path')
                video_id = response.get('video_id')
                # Save the video data to the database (assuming Video is your model)
                video = Video(csv_path=csv_path, video_id=video_id, video_url=video_url)
                video.save()
                return Response({'response': f'Video proccessed and saved  video id: {video_id}'})

        except Exception as e:
            return Response({'error':'error occured while proccessing video: ' + str(e)}, status=500)

    else:
        return Response({'error': 'Missing query parameter: video_url'}, status=400)