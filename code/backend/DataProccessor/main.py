import pickle
import pandas as pd
from datetime import datetime
from collections import defaultdict
import copy
import datetime
import time
import numpy as np
import cv2
#import matplotlib.pyplot as plt
from pathlib import Path
from ultralytics import YOLO
import os
import gdown


def download_missing_video_files(video_link=None,
                                 video_name_routine=None):
    if not os.path.exists(video_name_routine):
        gdown.download(video_link, video_name_routine)
    pass


def detect_objects(result):
    # Extract bounding box coordinates (x,y,x,y), labels, and confidences
    bboxes = result.boxes.xyxy.numpy().astype(np.uint16).tolist() # The boxes in [x_upper_right, y_upper_right, x_lower_left, y_lower_left] format
    labels = [result.names[name] for name in result.boxes.cls.numpy().tolist()]
    confidences = result.boxes.conf.numpy().tolist()
    return bboxes, labels, confidences


def track_objects(result, bboxes, labels, confidences, tracked_objects, bbox_path):

    # extract the current_ids from the result,boxes.id only if its not empty
    if result.boxes.id is not None:
        current_ids = result.boxes.id.numpy().tolist()
    else:
        current_ids = -1

    # go over all the bboxes
    for index, bbox in enumerate(bboxes):
        # extract x_upper_left, y_upper_left, x_lower_right, y_lower_right from the bounding box as numpy to list
        (x_upper_left, y_upper_left, x_lower_right, y_lower_right) = map(int, bbox)

        # Extract tracked object information (track_id, object_name, time_date, confidence)
        track_id = current_ids[index]
        object_name = labels[index]
        time_date = datetime.datetime.now().strftime('%Y-%m-%d__%H_%M_%S_%f')
        confidence = confidences[index]

        # bounding box image name is the track_id_time_date.jpg
        bbox_image_path = os.path.join(bbox_path, f'{track_id}_{time_date}.jpg')

        # crop the bounding box from the frame
        output_image = result.orig_img[y_upper_left:y_lower_right, x_upper_left:x_lower_right,:]
        # resize the bounding box to 72X72 pixels
        output_image = cv2.resize(output_image, (72, 72))
        # Save bounding box image to the bbox_image_path
        cv2.imwrite(bbox_image_path, output_image)

        # Add tracked track_id, object_name, time_date, confidence to a tracked_objects dictionary with the track_id as its key
        tracked_objects[track_id] = {
            'bbox': bbox,
            'track_id': track_id,
            'object_name': object_name,
            'time_date': time_date,
            'bbox_image_path': bbox_image_path,
            'confidence': np.max(confidence)
        }
    return tracked_objects


def build_detections_and_routine_map(tracked_objects, routine_map, width, height):

    # initialize the detection frame to zeros
    detection_frame = np.zeros((height, width))

    # go over all the tracked objects
    for track_object_index in tracked_objects.keys():

        # extract the x_upper_left, y_upper_left, x_lower_right, y_lower_right from the tracked_objects dictionary bbox key
        (x_upper_left, y_upper_left, x_lower_right, y_lower_right) = tracked_objects[track_object_index]['bbox']

        # calculate w and h
        h = y_lower_right - y_upper_left
        w = x_lower_right - x_upper_left

         # set the current detection as np.ones by the size w,h
        detection = np.ones((h, w))

        # create the detection frame by adding the detection at location x,y
        detection_frame[y_upper_left :y_lower_right, x_upper_left: x_lower_right] += detection

        # create the routine map frame by adding the detection at location x,y
        routine_map[y_upper_left :y_lower_right, x_upper_left: x_lower_right] += detection

    return routine_map, detection_frame


def init_system(video_path,video_folder_path):
    # Initialize YOLOv8 model
    model = YOLO('yolov8n.pt')

    # set path for the bounding box images as ./bbox_images and create if doesn't exists
    bbox_path = os.path.join(video_folder_path,'bbox_images')
    if not os.path.exists(bbox_path):
        os.mkdir(bbox_path)

    # set the results to be the model.track of the video_path with stream=True
    results = model.track(video_path, stream=True)
    ######################## tracker + detector + recognizer #############################

    # current_date is the current date
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # csv file name is current_date_tracked_objects.csv
    csv_filename = os.path.join(video_folder_path,'tracked_objects.csv')

    # Initialize CSV file and header 'bbox', 'track_id', 'object_name', 'time_date', 'bbox_image_path', 'confidence', 'score'
    csv_header = ['bbox', 'track_id', 'object_name', 'time_date', 'bbox_image_path', 'confidence', 'score']

    # Create a csv if not exists or append to existing CSV file
    if not Path(csv_filename).is_file():
        pd.DataFrame(columns=csv_header).to_csv(csv_filename, index=False)

    # set the frame_counter to zero
    fame_counter = 0

    return csv_filename, results, bbox_path, fame_counter


def run_main_routine_loop(video_path,video_folder_path):

    # initialize the csv_filename, results, bbox_path, fame_counter variables
    csv_filename, results, bbox_path, fame_counter = init_system(video_path,video_folder_path)

    for result in results:
        # Initialize dictionary to store tracked objects
        tracked_objects = defaultdict(dict)

        # try to Read next frame from the video if fail than break
        try:
            next(results)
            fame_counter += 1
        except Exception as e:
            print(e)
            break

        # if first frame then
        if fame_counter == 1:

            # get the width and height
            height, width, channels = result.orig_img.shape

            # Initialize routine routine_map as a fame of ones
            routine_map = np.ones((height, width), dtype=np.float32)

            # Initialize video writer for anomaly_detection.mp4  width and height to be same as the video input
            fps = 30
            width = int(width)
            height = int(height)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(os.path.join(video_folder_path, 'object_detection.mp4'), fourcc, fps, (width, height))

        # Detect objects
        bboxes, labels, confidences = detect_objects(result)

        # Track objects
        tracked_objects = track_objects(result, bboxes, labels, confidences, tracked_objects, bbox_path)

        # # Save tracked objects to CSV
        save_tracked_objects_to_csv(tracked_objects, csv_filename)

        # build routine map
        routine_map, detection_frame = build_detections_and_routine_map(tracked_objects, routine_map, width, height)

        # multiply detection_frame by 255 and convert it to uint8 and to RGB
        output_frame = cv2.cvtColor((detection_frame*255).astype(np.uint8), cv2.COLOR_GRAY2BGR)


        # show results (original frame, detection fame, noamalized routine_map as colormap_jet  # keep in comment for github
        cv2.imshow('Frame', result.plot())
        cv2.imshow('Detections', output_frame)
        routine_map_display = (routine_map/np.max(routine_map)*255).astype(np.uint8)
        routine_map_display = cv2.applyColorMap(routine_map_display, cv2.COLORMAP_JET)
        cv2.imwrite(os.path.join(video_folder_path,'heat_map_display.png'), routine_map_display)
        # save detection frame
        out.write(output_frame)

        # is pressed escape than break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Save routine_map.pkl
    with open(os.path.join(video_folder_path,'routine_map.pkl'), 'wb') as f:
        pickle.dump(routine_map, f)

    # release the output video
    out.release()

    # Close all windows
    cv2.destroyAllWindows()
pass

def anomaly_detection(tracked_objects, routine_map, result, height=None, width=None, out=None):

    # Create probability map (normalized routine map by dividing each pixel by its maximum global value)
    probability_map = routine_map/np.max(routine_map)
    # probability_map[probability_map==0]=1

    # initialize the current_frame_detections as a zeros frame
    _, detection_frame = build_detections_and_routine_map(tracked_objects, routine_map, width, height)

    # create prediction_map as a multiplication between normalized motion frame and probability map
    prediction_map = detection_frame*probability_map

    # set pixel to 1 if prediction_map is equal to zero
    prediction_map[prediction_map==0]=1

    # create log_likelihood_map by the following formula 10*logarithm(prediction map)
    log_likelihood_map = -np.log(prediction_map)

    # perform noise removal by morphological filters kernel_size_open = (3, 3) kernel_size_close = (10, 10)
    kernel_open = np.ones((3, 3), np.float64)
    kernel_close = np.ones((10, 10), np.float64)
    log_likelihood_map = cv2.morphologyEx(log_likelihood_map, cv2.MORPH_OPEN, kernel_open)
    log_likelihood_map = cv2.morphologyEx(log_likelihood_map, cv2.MORPH_CLOSE, kernel_close)

    # go over all the tracked objects keys
    for track_object_index in tracked_objects.keys():

        # extract bounding box data
        (x_upper_left, y_upper_left, x_lower_right, y_lower_right) = tracked_objects[track_object_index]['bbox']

        # calculate score as the mean score inside the bounding box
        score = np.mean(log_likelihood_map[y_upper_left :y_lower_right, x_upper_left: x_lower_right])

        # add the score to the tracked objects
        tracked_objects[track_object_index]['score'] = score
    # perform threshold on the log_likelihood_map (smaller than 2) equal to zero
    log_likelihood_map[log_likelihood_map < 2] = 0

    # create output frame by setting each pixel larger than zero to 255 and as uint8
    output_frame = ((log_likelihood_map > 0) * 255).astype(np.uint8)

    # write output video frame
    output_frame = cv2.cvtColor(output_frame, cv2.COLOR_GRAY2BGR)
    out.write(output_frame)

    # show results
    cv2.imshow('Frame', result.plot())
    cv2.imshow('anomaly frame', output_frame)

    return tracked_objects

def save_tracked_objects_to_csv(tracked_objects, csv_filename=None):

    tracked_objects_df = pd.DataFrame(tracked_objects.values())
    tracked_objects_df.to_csv(csv_filename, mode='a', header=False, index=False)


def run_main_anomaly_loop(video_name_routine=None,video_folder_path=None):
    csv_filename, results, bbox_path, frame_counter = init_system(video_name_routine,video_folder_path)


    # Read routine_map from routine_map.pkl
    with open(os.path.join(video_folder_path,'routine_map.pkl'), 'rb') as f:
        routine_map = pickle.load(f)

    for result in results:
        # Initialize dictionary to store tracked objects
        tracked_objects = defaultdict(dict)

        # try to Read next frame from the video if fail than break
        try:
            next(results)
            frame_counter += 1
        except Exception as e:
            print(e)
            break

        if frame_counter == 1:

            # get the height, and width, from the original frame
            height, width, channels = result.orig_img.shape

            # Initialize video writer for anomaly_detection.mp4  width and height to be same as the video input
            fps = 30
            width = int(width)
            height = int(height)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(os.path.join(video_folder_path,'anomaly_detection.mp4'), fourcc, fps, (width, height))
        # Detect objects
        bboxes, labels, confidences = detect_objects(result)

        # Track objects
        tracked_objects = track_objects(result, bboxes, labels, confidences, tracked_objects, bbox_path)

        # detect anomaly
        tracked_objects = anomaly_detection(tracked_objects, routine_map, result, height=height, width=width, out=out)

        # append the new tracked_objects data frame to the CSV file. no need to save header and index
        save_tracked_objects_to_csv(tracked_objects, csv_filename)

        # if pressed escape than break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and writer
    out.release()

    # Close all windows
    cv2.destroyAllWindows()

    pass

def main(video_url,video_folder_path):
    current_direcotry = video_folder_path
    if not os.path.exists(current_direcotry):
        os.makekdirs(video_folder_path)
    video_name_routine = os.path.join(current_direcotry, 'routine_frame.mp4')
    download_missing_video_files(video_link=video_url, video_name_routine=video_name_routine)
    run_main_routine_loop(video_name_routine,video_folder_path)
    run_main_anomaly_loop(video_name_routine,video_folder_path)
