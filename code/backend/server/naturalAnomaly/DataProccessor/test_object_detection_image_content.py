import gdown
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')
import pytest
import os
import params_links


@pytest.mark.order(7)
@pytest.mark.parametrize("input_video_name, input_video_link, jpg_file_name, jpg_gt_file_name, jpg_gt_file_link, size",
                         [('test1.mp4',
                           params_links.test1_link(),
                           '1.0_*.jpg',
                           '1.0_2024-06-12__17_17_46_476904.jpg',
                           params_links.image_link(),
                           100)
                          ])
def test_check_created_jpg_file(input_video_name, input_video_link, jpg_file_name, jpg_gt_file_name, jpg_gt_file_link, size):
    current_directory = os.getcwd()
    input_video_name = os.path.join(current_directory, input_video_name)
    gdown.download(input_video_link, input_video_name)
    # run_main_anomaly_loop(input_video_name) # no need to run this! only if necessary
    gdown.download(jpg_gt_file_link, jpg_gt_file_name)
    # assert True if one of the 1.0_*.jpg files in /bbox_images is absolute difference from jpg_gt_file_name is smaller than size
    assert False, f'file not found'
    pass