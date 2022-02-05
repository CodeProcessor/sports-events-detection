#!/usr/bin/env python3
"""
@Filename:    recognitions.py
@Author:      dulanj
@Time:        26/01/2022 15:41
"""
import os

from sports_event_detection.common import ModelNames
from sports_event_detection.event_recognition import SportsEventsRecognition


def scrum_lineout_recognition(video_path):
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    classes = {
        0: 'scrum',
        1: 'lineout'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes)
    ef.find_event([(ModelNames.scrum_lineout_object_detection_model.name, 'scrum')])
    ef.find_event([(ModelNames.scrum_lineout_object_detection_model.name, 'lineout')])


def play_recognition(video_path):
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    classes = {
        0: 'digital'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes)
    mod_eve_list = [
        (ModelNames.digital_object_detection_model.name, 'digital'),
        (ModelNames.play_noplay_classification_model.name, 'noplay')
    ]
    ef.find_event(mod_eve_list)


if __name__ == '__main__':
    video_path = '/home/dulanj/MSc/DialogRugby/Match#1_Navy_SC_vs_Havelock_SC_DRL_2019_20.mp4'
    video_path = "/home/dulanj/MSc/DialogRugby/10fps/match30.mp4"
    scrum_lineout_recognition(video_path)
    play_recognition(video_path)
