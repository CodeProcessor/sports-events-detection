#!/usr/bin/env python3
"""
@Filename:    annotate.py
@Author:      dulanj
@Time:        29/01/2022 10:51
"""
import glob
import os

from sports_event_detection.annotator import Annotate


def annotate_events():
    videos = [
        "Match#18_Police_SC_v_CH_&_FC_DRL_2019_20.mp4",
        "Match#21_Air_Force_SC_v_Police_SC_DRL_2019_20.mp4",
        "Match#23_CH_&_FC_v_Kandy_SC_DRL_2019_20.mp4",
        "Match#30_Air_Force_SC_v_Kandy_SC_DRL_201920.mp4",
        "Match#35_Kandy_SC_v_CH_&_FC_DRL_2019_20.mp4",
        "Match#47_CH_&_FC_v_Air_Force_SC_DRL_2019_20.mp4",
        "Match#56_Kandy_SC_v_Police_SC_DRL_2019_20.mp4"
    ]
    data_file = "/home/dulanj/MSc/sports-events-detection/data/LSK Annotations Clean.xlsx"
    sheet_names = [18, 21, 23, 30, 35, 47, 56]
    skip_list = [18, 21, 23, 30, 35]
    for video, sheet in zip(videos, sheet_names):
        if sheet in skip_list:
            continue
        sheet_name = f"Match{sheet}"
        video_path = os.path.join("/home/dulanj/MSc/DialogRugby", video)
        annotate = Annotate(
            video_file_path=video_path,
            data_file_path=data_file,
            sheet_name=sheet_name,
            save_dir="data/clips_2c_7m"
        )
        annotate.extract_all_clips()


def annotate_events_v2():
    videos = glob.glob("/home/dulanj/MSc/DialogRugby/Match*")
    data_file = "/home/dulanj/MSc/sports-events-detection/data/LSK Annotations Clean_v3.xlsx"
    sheet_ids = [9]
    skip_list = []

    for sheet_id in sheet_ids:
        if sheet_id in skip_list:
            continue
        _video_prefix = "Match#{}_".format(sheet_id)
        video_path = [video for video in videos if _video_prefix in video]
        if len(video_path) == 1:
            video_path = video_path[0]
            sheet_name = f"Match{sheet_id}"
            print("Annotating {} with sheet name {}".format(video_path, sheet_name))
            annotate = Annotate(
                video_file_path=video_path,
                data_file_path=data_file,
                sheet_name=sheet_name,
                save_dir="data/clips_2c_3m_v3"
            )
            annotate.extract_all_clips()
        else:
            print("No video found for sheet id {}".format(sheet_id))


def digital_overlay_detection():
    videos = [
        "Match#1_Navy_SC_vs_Havelock_SC_DRL_2019_20.mp4",
        "Match#16_CR_&_FC_v_Army_SC_DRL_2019_20.mp4",
        "Match#19_CR_&_FC_v_Kandy_SC_DRL_2019_20.mp4",
        "Match#23_CH_&_FC_v_Kandy_SC_DRL_2019_20.mp4"
    ]
    data_file = "/home/dulanj/MSc/sports-events-detection/data/Play and NoPlay Annotations.xlsx"
    sheet_names = [1, 16, 19, 23]
    skip_list = []
    for video, sheet in zip(videos, sheet_names):
        if sheet in skip_list:
            continue
        sheet_name = f"Match{sheet}"
        video_path = os.path.join("/home/dulanj/MSc/DialogRugby", video)
        annotate = Annotate(
            video_file_path=video_path,
            data_file_path=data_file,
            sheet_name=sheet_name,
            save_dir="data/clips_digital"
        )
        annotate.extract_all_clips()


if __name__ == '__main__':
    annotate_events_v2()
    # digital_overlay_detection()
    print("Done")
