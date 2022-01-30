#!/usr/bin/env python3
"""
@Filename:    detections.py
@Author:      dulanj
@Time:        26/01/2022 14:02
"""
import os

from sports_event_detection.common import ModelNames
from sports_event_detection.event_detection import SportsEventsDetection


def get_digital(video_path):
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/digital/v3/best.pt'
    classes = {
        0: 'digital'
    }
    model_name = ModelNames.digital_object_detection_model.name
    sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
    sed.video_loop(skip_frames=0)


def get_scrum_linout(video_path):
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/scrum-lineout/best.pt'
    classes = {
        0: 'scrum',
        1: 'line_out'
    }
    model_name = ModelNames.scrum_lineout_detection_model.name
    sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
    sed.video_loop(skip_frames=0)


if __name__ == '__main__':
    video_path = "/home/dulanj/MSc/DialogRugby/Match#16_CR_&_FC_v_Army_SC_DRL_2019_20.mp4"
    get_digital(video_path)
    get_scrum_linout(video_path)
