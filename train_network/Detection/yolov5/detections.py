#!/usr/bin/env python3
"""
@Filename:    detections.py
@Author:      dulanj
@Time:        26/01/2022 14:02
"""
import os

from sports_event_detection import SportsEventsDetection


def get_digital():
    video_path = "/home/dulanj/MSc/DialogRugby/Match#16_CR_&_FC_v_Army_SC_DRL_2019_20.mp4"
    db_name = os.path.basename(video_path).split('.')[0] + '_play.db'
    weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/digital/v2/best.pt'
    classes = {
        0: 'digital'
    }
    sed = SportsEventsDetection(video_path, db_name, weight_path, classes)
    sed.video_loop()


def get_scrum_linout():
    video_path = "/home/dulanj/MSc/DialogRugby/Match#16_CR_&_FC_v_Army_SC_DRL_2019_20.mp4"
    db_name = os.path.basename(video_path).split('.')[0] + '_event.db'
    weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/scrum-lineout/best.pt'
    classes = {
        0: 'scrum',
        1: 'line_out'
    }
    sed = SportsEventsDetection(video_path, db_name, weight_path, classes)
    sed.video_loop()


if __name__ == '__main__':
    get_digital()
    # get_scrum_linout()
