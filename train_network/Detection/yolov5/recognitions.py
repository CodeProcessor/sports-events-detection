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


def play_recognition():
    video_path = '/home/dulanj/MSc/DialogRugby/Match#16_CR_&_FC_v_Army_SC_DRL_2019_20.mp4'
    db_name = os.path.basename(video_path).split('.')[0] + '_play.db'
    classes = {
        0: 'digital'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes, logic="banner")
    ef.find_event('digital')


if __name__ == '__main__':
    play_recognition()
