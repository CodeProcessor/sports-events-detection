#!/usr/bin/env python3
"""
@Filename:    utils.py
@Author:      dulanj
@Time:        02/02/2022 01:10
"""
from datetime import datetime


def get_current_timestamp():
    """
    Get current datetime as formatted string
    @return:
    """
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")


def iou(box1, box2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.
    """
    # determine the coordinates of the intersection rectangle
    x_a = max(box1[0], box2[0])
    y_a = max(box1[1], box2[1])
    x_b = min(box1[2], box2[2])

    y_b = min(box1[3], box2[3])
    if x_b - x_a > 0 and y_b - y_a > 0:
        inter_area = (x_b - x_a) * (y_b - y_a)
        # print("interArea:", inter_area)
        # print("unionArea:", union_area)
        union_area = (box1[2] - box1[0]) * (box1[3] - box1[1]) + (box2[2] - box2[0]) * (box2[3] - box2[1])
        _iou = inter_area / (union_area - inter_area)
    else:
        _iou = 0
    return _iou


def convert_string_time_to_seconds(time_str: str) -> int:
    _time_split = time_str.split(':')
    _time_in_seconds = 0

    def second_correction(_second):
        if len(_second) == 1:
            _second = _second + '0'
        return _second

    if len(_time_split) == 2:
        _min, _sec = _time_split
        _time_in_seconds = int(_min) * 60 + int(second_correction(_sec))
    elif len(_time_split) == 3:
        _hour, _min, _sec = _time_split
        _time_in_seconds = int(_hour) * 3600 + int(_min) * 60 + int(second_correction(_sec))
    return _time_in_seconds


def check_overlap(series_a, series_b, verbose=False):
    a_start_second = convert_string_time_to_seconds(series_a['start_time'])
    a_end_second = convert_string_time_to_seconds(series_a['end_time'])

    b_start_second = convert_string_time_to_seconds(series_b['start_time'])
    b_end_second = convert_string_time_to_seconds(series_b['end_time'])

    _overlap = False
    _value = 0
    if max(a_start_second, b_start_second) - min(a_end_second, b_end_second) <= 0:
        _value = (min(a_end_second, b_end_second) - max(a_start_second, b_start_second)) * 1.0 \
                 / (max(a_end_second, b_end_second) - min(a_start_second, b_start_second))
        _overlap = True
    else:
        _value = b_start_second - a_start_second if a_start_second < b_start_second else b_end_second - a_start_second

    print("{} - {} | {} - {} | {} {} ".format(
        series_a['start_time'],
        series_a['end_time'],
        series_b['start_time'],
        series_b['end_time'],
        _overlap,
        _value)
    ) if verbose else ""
    return _overlap, _value


def remove_noplay_overlapped_events(prediction_df):
    no_play_df = prediction_df[prediction_df['event_name'] == 'digital_noplay']
    play_df = prediction_df[prediction_df['event_name'] != 'digital_noplay']
    for index1, row in no_play_df.iterrows():
        for index2, row_event in play_df.iterrows():
            _overlap, _value = check_overlap(row, row_event, verbose=False)
            if _overlap:
                try:
                    prediction_df.drop(index2, inplace=True, axis=0)
                    print("Dropped index {}".format(index2))
                    # print("No play \n{}".format(row))
                    # print("Dropped \n{}".format(row_event))
                    # print("=" * 50)
                except KeyError as e:
                    print(index2)
    return prediction_df
