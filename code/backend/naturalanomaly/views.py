from .queryOllama import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from .models import Video
from DataProccessor.proccesVideoModule import process_video
VIDEO_SESSION = VannaVideoWrapper(video_id=1, model="llama3.2:3b")
@api_view(['POST'])
def queryOllama(request):
    data = json.loads(request.body)
    query = data.get('message')
    if query:
        response = chatWithOllama(query,VIDEO_SESSION)
        if isinstance(response, str) and response.startswith('data:image/'):
            return Response({'image': response.split(',', 1)[1]})
        elif isinstance(response,pd.DataFrame):
            if not response.empty:
                columns = list(response.columns)
                rows = response.to_dict(orient="records")
                cols_text = ", ".join(columns)
                summary = (f"Showing {len(rows)} rows and {len(columns)} columns: {cols_text}."
                           f"This table is a response to your query: '{query}'.")
                structured_data = {
                    "columns": columns,
                    "rows": rows,
                    "summary": summary
                }
                return Response({
                    "Table": structured_data,
                })
            else:
                return Response({'response': 'No results were generated from your query'})
        return Response({'response': response})
    else:
        return Response({'error': 'Missing query parameter'}, status=400)
@api_view(['POST'])
def queryOllamainROI(request):
    data = json.loads(request.body)
    query = data.get('message')
    bbox = data.get('bbox')  # Expecting a list like [x1, y1, x2, y2]

    if not query:
        return Response({'error': 'Missing query parameter'}, status=400)

    if not bbox or len(bbox) != 4:
        return Response({'error': 'Invalid or missing bbox. It should be a list like [x1, y1, x2, y2].'}, status=400)

    try:
        bbox = [int(coord) for coord in bbox]
    except Exception:
        return Response({'error': 'Bounding box coordinates must be integers.'}, status=400)
    response = chatWithOllamainROI(query, bbox=bbox,video_session=VIDEO_SESSION)
    return Response({'response': response})

@api_view(['POST'])
def processVideo(request):
    #method for future support in uploading of new videos
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
                VIDEO_SESSION.set_video_context(video_id)#switch discussion to focus on new video
                return Response({'response': f'Video proccessed and saved  video id: {video_id}'})

        except Exception as e:
            return Response({'error':'error occured while proccessing video: ' + str(e)}, status=500)

    else:
        return Response({'error': 'Missing query parameter: video_url'}, status=400)
