#!/usr/bin/env python3
"""
@Filename:    overall_accuracy.py
@Author:      dulanj
@Time:        09/04/2022 12:50
"""
import pandas as pd

from sports_event_detection.extras.sports_utils import check_overlap, remove_noplay_overlapped_events

prediction_file = "/home/dulanj/MSc/sports-events-detection/server/x4rvFbkcox4.csv"
# prediction_file = "/home/dulanj/MSc/sports-events-detection/sports_event_detection/recognition/Army_SC_v_Kandy_SC_–_DRL_2019_20_#38.csv"
ground_truth_file = "/home/dulanj/Learn/rugby-events-dataset/video-annotations/match_csv_files/match#38.csv"


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

    get_gt = get_next_row(ground_truth_df)
    get_pd = get_next_row(prediction_df)
    row_gt = get_gt.__next__()
    row_pd = get_pd.__next__()
    try:
        while row_gt is not None and row_pd is not None:
            overlap, value = check_overlap(row_gt, row_pd)
            if overlap:
                conf_matrix['TP'] += 1
                assert value > 0
                iou.append(value)
                row_gt = get_gt.__next__()
                row_pd = get_pd.__next__()
            else:
                if value > 0:
                    conf_matrix['FN'] += 1
                    row_gt = get_gt.__next__()
                else:
                    conf_matrix['FP'] += 1
                    row_pd = get_pd.__next__()
    except StopIteration:
        pass

    print(conf_matrix)
    print(iou)
    print("IOU: {}".format(sum(iou) / len(iou)))
    print("Accuracy: {}".format(conf_matrix['TP'] / (conf_matrix['TP'] + conf_matrix['FP'] + conf_matrix['FN'])))
    print("Precision: {}".format(conf_matrix['TP'] / (conf_matrix['TP'] + conf_matrix['FP'])))
    print("Recall: {}".format(conf_matrix['TP'] / (conf_matrix['TP'] + conf_matrix['FN'])))
    print("F1: {}".format(2 * conf_matrix['TP'] / (2 * conf_matrix['TP'] + conf_matrix['FP'] + conf_matrix['FN'])))
    return conf_matrix


if __name__ == '__main__':
    df_pd, df_gt = load_df(ground_truth_file, prediction_file)
    df_pd = remove_noplay_overlapped_events(df_pd)
    # print(df_pd.head())
    # print(df_gt.head())
    for _event in ['scrum', 'lineout', 'ruck']:
        print("=" * 20)
        print("Event: {}".format(_event))
        get_overall_accuracy(df_pd, df_gt, _event)
    # print(convert_to_seconds('1.10.5'))
