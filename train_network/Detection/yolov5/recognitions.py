#!/usr/bin/env python3
"""
@Filename:    recognitions.py
@Author:      dulanj
@Time:        26/01/2022 15:41
"""
import os

from sports_event_recognition import SportsEventsRecognition


def scrum_lineout_recognition():
    video_path = '/home/dulanj/MSc/DialogRugby/out-s-20_30-e-40_00-match-16.mp4'
    db_name = os.path.basename(video_path).split('.')[0] + '.db'
    classes = {
        0: 'scrum',
        1: 'line_out'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes)
    ef.find_event('scrum')


if __name__ == '__main__':
    scrum_lineout_recognition()
