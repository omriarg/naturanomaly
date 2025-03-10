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

@pytest.mark.order(4)
@pytest.mark.parametrize("input_video_name, input_video_link, csv_file_name, size",
                         [('test1.mp4',
                           params_links.test1_link(),
                           'tracked_objects.csv',
                           100)
                          ])
def test_check_created_csv_file(input_video_name, input_video_link, csv_file_name, size):
    current_directory = os.getcwd()
    input_video_name = os.path.join(current_directory, input_video_name)
    if not os.path.exists(input_video_name):
        gdown.download(input_video_link, input_video_name)
    anomaly_video_file = os.path.join(current_directory, 'anomaly_detection.mp4')
    run_main_anomaly_loop(input_video_name)
    # assert True if csv_file_name file exists
    assert False
    #  assert True if csv_file_name file is larger than size
    assert False

    pass