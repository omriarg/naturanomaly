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
import glob
@pytest.mark.order(6)
@pytest.mark.parametrize("input_video_name, input_video_link, jpg_file_name, size",
                         [('test1.mp4',
                           params_links.test1_link(),
                           '1.0_*.jpg',
                           100)
                          ])
def test_check_created_jpg_file(input_video_name, input_video_link, jpg_file_name, size):
    current_directory = os.getcwd()
    input_video_name = os.path.join(current_directory, input_video_name)
    gdown.download(input_video_link, input_video_name)
    run_main_anomaly_loop(input_video_name) # run this only if needed
    # assert True if 1.0_*.jpg file exists in /bbox_images directory
    assert False, f'{jpg_file_name} does not exist'

    pass
