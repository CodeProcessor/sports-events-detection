#!/usr/bin/env python3
"""
@Filename:    overall_accuracy.py
@Author:      dulanj
@Time:        09/04/2022 12:50
"""
import pandas as pd

from sports_event_detection.extras.sports_utils import check_overlap


def load_df(gt_file, pred_file):
    df_pd = pd.read_csv(pred_file)
    df_pd.drop(columns=['start_frame_id', 'end_frame_id', 'duration'], inplace=True)

    df_gt = pd.read_csv(gt_file, names=["event_name", "start_time", "end_time"])
    return df_pd, df_gt


def get_next_row(dataframe):
    for index1, row in dataframe.iterrows():
        yield row


def get_overall_accuracy(df_pd, df_gt, event_name):
    conf_matrix = {
        'TP': 0,
        'FP': 0,
        'FN': 0,
        'TN': 0
    }
    iou = []

    ground_truth_df = df_gt[df_gt['event_name'] == event_name]
    prediction_df = df_pd[df_pd['event_name'] == event_name]
    ground_truth_df.reset_index(drop=True, inplace=True)
    prediction_df.reset_index(drop=True, inplace=True)
    #
    # print(ground_truth_df.head())
    # print(prediction_df.head())

    # Generator comprehension
    get_gt = (row for _, row in ground_truth_df.iterrows())
    get_pd = (row for _, row in prediction_df.iterrows())

    row_gt = next(get_gt)
    row_pd = next(get_pd)

    while row_gt is not None and row_pd is not None:
        try:
            overlap, value = check_overlap(row_gt, row_pd)
            if overlap:
                conf_matrix['TP'] += 1
                assert value >= 0, print(row_gt)
                iou.append(value)
                row_gt = next(get_gt)
                row_pd = next(get_pd)
            else:
                if value > 0:
                    conf_matrix['FN'] += 1
                    row_gt = next(get_gt)
                else:
                    conf_matrix['FP'] += 1
                    row_pd = next(get_pd)
        except StopIteration:
            break

    print(conf_matrix)
    # print(iou)
    _iou_avg = sum(iou) / len(iou)
    _acc = conf_matrix['TP'] / (conf_matrix['TP'] + conf_matrix['FP'] + conf_matrix['FN'])
    _precision = conf_matrix['TP'] / (conf_matrix['TP'] + conf_matrix['FP'])
    _recall = conf_matrix['TP'] / (conf_matrix['TP'] + conf_matrix['FN'])
    _f1 = 2 * _precision * _recall / (_precision + _recall)
    print(
        f"IOU: {_iou_avg:.2f} \tAccuracy: {_acc:.2f} \tPrecision: {_precision:.2f} \tRecall: {_recall:.2f} \tF1: {_f1:.2f}")
    return conf_matrix
