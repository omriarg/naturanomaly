import pickle
import gdown
# import matplotlib.pyplot as plt
import numpy as np
import pytest
import os
import params_links

@pytest.mark.order(6)
@pytest.mark.parametrize("input_video_name, input_video_link, heatmap_gt_file_name, heatmap_gt_file_link, max_error",
                         [('routine_frame.mp4',
                           params_links.routine_frame_link(),
                           'routine_map_left_road_gt.pkl',
                           params_links.routine_map_left_road_gt_link(),
                           1280 * 720 / 2)])
def test_left_side_routine_map_as_pkl_when_input_moving_left_side(input_video_name,  input_video_link,
                                                                  heatmap_gt_file_name, heatmap_gt_file_link,
                                                          max_error):
    current_directory = os.getcwd()
    video_file = os.path.join(current_directory, input_video_name)
    if not os.path.exists(input_video_name):
        gdown.download(input_video_link, input_video_name)
    # run_main_routine_loop(video_file)
    pkl_file_path = os.path.join(os.getcwd(), 'routine_map.pkl')
    if os.path.exists(pkl_file_path):
        with open('routine_map.pkl', 'rb') as f:
            heatmap = pickle.load(f)
        if not os.path.exists(heatmap_gt_file_name):
            gdown.download(heatmap_gt_file_link, heatmap_gt_file_name)

        with open(heatmap_gt_file_name, 'rb') as f:
            # with open('routine_map_left_right_roads_gt.pkl', 'rb') as f:
            heatmap_gt = pickle.load(f)
        height, width = heatmap_gt.shape
        left_half_heatmap = heatmap[:, :width // 2 + 20]
        left_half_heatmap_gt = heatmap_gt[:, :width // 2 + 20]
        assert np.sum(np.abs(left_half_heatmap - left_half_heatmap_gt)) <= max_error
    else:
        assert False