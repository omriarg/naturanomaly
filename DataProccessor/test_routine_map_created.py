import gdown
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')
from main import run_main_routine_loop
import pytest
import os
import params_links

@pytest.mark.order(1)
@pytest.mark.parametrize("input_video_name, input_video_link, max_size",
                         [('routine_frame.mp4',
                           params_links.routine_frame_link(),
                           1000)])
def test_save_heat_map_as_pkl(input_video_name, input_video_link, max_size):
    current_directory = os.getcwd()
    gdown.download(input_video_link, input_video_name)
    video_file = os.path.join(current_directory, input_video_name)
    run_main_routine_loop(video_file)
    pkl_file_path = os.path.join(os.getcwd(), 'routine_map.pkl')
    # check if pkl_file_path file exists
    assert False
    # check if pkl_file_path file is larger than max_size
    assert False
