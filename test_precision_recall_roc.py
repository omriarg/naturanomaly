import pickle
import cv2
import gdown
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')
import numpy as np
from precision_recall_roc import generate_precision_recall_auc_graphs
import pytest
import os
import params_links
import glob
import pandas as pd


@pytest.mark.order(9)
@pytest.mark.parametrize("roc_curve_gt_file_name, roc_curve_gt_file_link, roc_curve_file_name, "
                         "precision_recall_gt_file_name, precision_recall_gt_file_link, precision_recall_file_name, "
                         "min_error, tagging_csv_file_name",
                         [('roc_curve_gt.png',
                           params_links.roc_link(),
                           'roc_curve.png',
                           'precision_recall_gt.png',
                           params_links.precision_recall_link(),
                           'precision_recall.png',
                           60000,
                           'tagged.csv')
                          ])
def test_check_created_roc_precision_curve_file(roc_curve_gt_file_name, roc_curve_gt_file_link, roc_curve_file_name,
                                                precision_recall_gt_file_name, precision_recall_gt_file_link,
                                                precision_recall_file_name, min_error, tagging_csv_file_name):
    gdown.download(roc_curve_gt_file_link, roc_curve_gt_file_name)
    gdown.download(precision_recall_gt_file_link, precision_recall_gt_file_name)

    y_true = [1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0]

    y_predict = ((100 * np.arange(1, -1 / (len(y_true) - 1), -1 / (len(y_true) - 1))).astype(np.int32)).astype(
        np.float32) / 100

    generate_precision_recall_auc_graphs(y_true, y_predict, version='v1', show_threshold=False)
    y_true[3] = 1
    generate_precision_recall_auc_graphs(y_true, y_predict, version='v2', show_threshold=False)

    data_base = pd.read_csv(tagging_csv_file_name)

    y_true = data_base.tag.values
    y_predict = data_base.score.values.tolist()
    y_predict = (y_predict / np.max(y_predict)).tolist()
    generate_precision_recall_auc_graphs(y_true, y_predict, version='v1', show_threshold=False)
    plt.legend()
    # plt.pause(0.1)
    # plt.show()
    plt.figure('precision recall')
    plt.savefig('precision_recall.png')  # Change the extension to save in different formats, e.g., .pdf, .svg
    plt.figure('ROC curve')
    plt.savefig('roc_curve.png')

    # check if absolute difference between roc_curve_graph and roc_curve_graph_gt is smaller than min_error
    assert False

    # check if absolute difference between precision_recall_graph and precision_recall_graph_gt is smaller than
    # min_error
    assert False

    pass
