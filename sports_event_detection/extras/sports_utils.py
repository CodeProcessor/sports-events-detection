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
