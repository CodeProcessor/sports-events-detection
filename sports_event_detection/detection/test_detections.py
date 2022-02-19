#!/usr/bin/env python3
"""
@Filename:    detections.py
@Author:      dulanj
@Time:        26/01/2022 14:02
"""
import os

from sports_event_detection.detection.event_detection import SportsEventsDetection
from sports_event_detection.detection.play_detection import PlayDetection
from sports_event_detection.extras.common import ModelNames


def get_digital(video_path, skip_time="00:00:00", break_on_time=None):
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/digital/v3/best.pt'
    classes = {
        0: 'digital'
    }
    model_name = ModelNames.digital_object_detection_model.name
    sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
    sed.video_loop(skip_time, break_on_time)


def get_scrum_linout(video_path, skip_time="00:00:00", break_on_time=None):
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/scrum-lineout/best.pt'
    classes = {
        0: 'scrum',
        1: 'line_out'
    }
    model_name = ModelNames.scrum_lineout_object_detection_model.name
    sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
    sed.video_loop(skip_time, break_on_time)


def play_detection(video_path, skip_time="00:00:00", break_on_time=None):
    model_path = "/home/dulanj/MSc/sports-events-detection/data/trained_models/play_noplay/best-model-parameters3.pt"
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    pd_obj = PlayDetection(video_path, db_name, model_path)
    pd_obj.video_loop(skip_time, break_on_time)


if __name__ == '__main__':
    # video_path = "/home/dulanj/MSc/DialogRugby/Match#16_CR_&_FC_v_Army_SC_DRL_2019_20.mp4"
    video_path = "/home/dulanj/MSc/DialogRugby/Match#1_Navy_SC_vs_Havelock_SC_DRL_2019_20.mp4"

    video_list = [
        # video_path,
        # "/home/dulanj/MSc/DialogRugby/10fps/match2.mp4",
        "/home/dulanj/MSc/DialogRugby/10fps/match30.mp4"
    ]
    skip_time = "00:10:00"
    break_on_time = None
    for video_path in video_list:
        print(video_path, skip_time, break_on_time)
        # play_detection(video_path, skip_time, break_on_time)
        # get_digital(video_path, "00:10:00", "00:20:00")
        get_scrum_linout(video_path, "00:18:00", "00:30:00")
