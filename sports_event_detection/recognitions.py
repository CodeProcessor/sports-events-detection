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
        1: 'line_out'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes)
    ef.find_event('scrum')


def play_recognition(video_path):
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    classes = {
        0: 'digital'
    }
    model_name = ModelNames.digital_object_detection_model.name
    ef = SportsEventsRecognition(video_path, db_name, classes, model_name, logic="banner")
    ef.find_event('digital')


if __name__ == '__main__':
    video_path = '/home/dulanj/MSc/DialogRugby/Match#1_Navy_SC_vs_Havelock_SC_DRL_2019_20.mp4'
    # scrum_lineout_recognition(video_path)
    play_recognition(video_path)
