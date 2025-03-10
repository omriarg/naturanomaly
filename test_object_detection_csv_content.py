import pickle
import cv2
import gdown
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')
import numpy as np
from main import run_main_anomaly_loop
import pytest
import os
import params_links
import pandas

@pytest.mark.order(5)
@pytest.mark.parametrize("input_video_name, input_video_link, gt_csv_file_name, gt_csv_file_name_link,csv_file_name,"
                         " max_error",
                         [('test1.mp4',
                           params_links.test1_link(),
                          'tracked_objects_gt.csv',
                          params_links.csv_anomaly_link(),
                          'tracked_objects.csv',
                           100)
                          ])
def test_check_created_csv_bbox(input_video_name, input_video_link, gt_csv_file_name,
                                    gt_csv_file_name_link,  csv_file_name, max_error):
    current_directory = os.getcwd()
    input_video_name = os.path.join(current_directory, input_video_name)
    gdown.download(input_video_link, input_video_name)
    gdown.download(gt_csv_file_name_link, gt_csv_file_name)
    anomaly_video_file = os.path.join(current_directory, 'anomaly_detection.mp4')
    # run_main_anomaly_loop(input_video_name) # no need to run this if test_object_detection_csv_creation was run

    dataframe_gt = pandas.read_csv(gt_csv_file_name)
    dataframe = pandas.read_csv(csv_file_name)

    # assert false if column titles in dataframe are different from the dataframe_gt

    # assert false if comparison of two dataframe bbox columns in dataframe are different from the dataframe_gt
    pass