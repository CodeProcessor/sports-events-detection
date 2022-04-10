#!/usr/bin/env python3
"""
@Filename:    backend.py
@Author:      dulanj
@Time:        04/02/2022 13:53
"""
import hashlib
import os

import pandas as pd
from pandas import DataFrame

from sports_event_detection.detection.event_detection import SportsEventsDetection
from sports_event_detection.detection.play_detection import PlayDetection
from sports_event_detection.extras.common import ModelNames
from sports_event_detection.recognition.event_recognition import SportsEventsRecognition
from sports_event_detection.recognition.recognition_with_tracking import TrackRecognition
from sports_event_detection.utils.video_operations import VideoOperations
from sports_event_detection.utils.youtube_downloader import YouTubeDownloader


class SportEventDetectionBackend:
    def __init__(self, save_clips=False):
        self.save_clips = save_clips
        self._fps = 5
        self.prediction_override = {
            "events": False,
            "play": False,
            "digital": False,
        }

    def get_yt_video_info(self, video_url):
        yt_downloader = YouTubeDownloader(video_url)
        return yt_downloader.get_info()

    def download_video(self, video_url, video_path="youtube_downloads"):
        yt_downloader = YouTubeDownloader(video_url)
        yt_downloader.get_info()
        _full_path = yt_downloader.download_video(video_path)
        print("Downloaded video: " + _full_path)
        return _full_path

    def convert_video(self, video_path, output_video_name=None):
        if output_video_name is None:
            output_path = os.path.join(f"video_outputs_{self._fps}fps", os.path.basename(video_path))
        else:
            output_path = os.path.join(f"video_outputs_{self._fps}fps", output_video_name)

        if not os.path.exists(output_path):
            video_op = VideoOperations(video_path)
            video_op.get_video_info()
            video_op.change_fps(self._fps)
            # video_op.split_video("00:01:00", "00:02:00")

            video_op.save(output_path)
            print("Converted video saved: " + output_path)
        else:
            print("Video already exists: " + output_path)
        return output_path

    def get_unique_name(self, url):
        return hashlib.md5(url.encode()).hexdigest()

    def get_digital(self, video_path, skip_time, break_on_time):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        weight_path = 'trained_models/digital_v3.pt'
        classes = {
            0: 'digital'
        }
        model_name = ModelNames.digital_object_detection_model.name
        sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
        sed.video_loop(skip_time, break_on_time, overwrite=self.prediction_override['digital'])

    def get_scrum_linout(self, video_path, skip_time, break_on_time):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        weight_path = 'trained_models/events_v3.pt'
        classes = {
            0: 'scrum',
            1: 'line_out',
            2: 'ruck'
        }
        model_name = ModelNames.sport_events_object_detection_model.name
        sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
        sed.video_loop(skip_time, break_on_time, overwrite=self.prediction_override['events'])

    def play_detection(self, video_path, skip_time, break_on_time):
        model_path = "trained_models/activity_v3.pt"
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        pd_obj = PlayDetection(video_path, db_name, model_path)
        pd_obj.video_loop(skip_time, break_on_time)

    def play_recognition(self, video_path, skip_time, break_on_time):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        classes = {
            0: 'digital'
        }
        ef = SportsEventsRecognition(video_path, db_name, classes, save_clip=self.save_clips)
        mod_eve_list = [
            (ModelNames.digital_object_detection_model.name, 'digital'),
            (ModelNames.activity_classification_model.name, 'noplay')
        ]
        _noplay_event_summary_dict = ef.find_event(
            mod_eve_list,
            skip_time,
            break_on_time
        )
        return [_noplay_event_summary_dict] if isinstance(_noplay_event_summary_dict, dict) else \
            _noplay_event_summary_dict

    def event_recognition(self, video_path, skip_time, break_on_time):
        """
        Event tracking with moving average
        :param video_path: Path to the video
        :param skip_time: Start time of the video to be skipped hh:mm:ss
        :param break_on_time: End time of the video to be skipped hh:mm:ss
        :return: Dataframe
        """
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        classes = {
            0: 'scrum',
            1: 'line_out',
            2: 'ruck'
        }
        ef = SportsEventsRecognition(video_path, db_name, classes, save_clip=self.save_clips)
        _scrum_event_summary_dict = ef.find_event(
            [(ModelNames.sport_events_object_detection_model.name, 'scrum')],
            skip_time,
            break_on_time
        )
        _line_out_event_summary_dict = ef.find_event(
            [(ModelNames.sport_events_object_detection_model.name, 'line_out')],
            skip_time,
            break_on_time
        )
        _ruck_event_summary_dict = ef.find_event(
            [(ModelNames.sport_events_object_detection_model.name, 'ruck')],
            skip_time,
            break_on_time
        )
        return [_scrum_event_summary_dict, _line_out_event_summary_dict, _ruck_event_summary_dict] if \
            isinstance(_scrum_event_summary_dict, dict) \
            else _scrum_event_summary_dict.append(_line_out_event_summary_dict).append(_ruck_event_summary_dict)

    def event_recognition_with_tracking(self, video_path, skip_time, break_on_time):
        """
        Event tracking with bounding box tracking algorithm
        :param video_path: Path to the video
        :param skip_time: Start time of the video to be skipped hh:mm:ss
        :param break_on_time: End time of the video to be skipped hh:mm:ss
        :return: Dataframe
        """
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        tr = TrackRecognition(video_path, db_name)
        dataframe = tr.recognize(skip_time=skip_time, break_on_time=break_on_time, visualize=False)
        return dataframe

    def detect_sport_events(self, video_path, skip_time, break_on_time):
        """
        Predict on all the sports events
        :param video_path:
        :param skip_time:
        :param break_on_time:
        :return:
        """
        self.get_digital(video_path, skip_time, break_on_time)
        self.get_scrum_linout(video_path, skip_time, break_on_time)
        self.play_detection(video_path, skip_time, break_on_time)

    def recognize_sport_event(self, video_path, skip_time, break_on_time):
        # _event_list_1 = self.event_recognition(video_path, skip_time, break_on_time)
        _event_df_1 = self.event_recognition_with_tracking(video_path, skip_time, break_on_time)
        _event_df_2 = self.play_recognition(video_path, skip_time, break_on_time)
        return _event_df_1.append(_event_df_2)

    def process_video(self, video_url, skip_time, break_on_time):
        data: DataFrame = pd.DataFrame()
        _converted_path = ""
        _full_path = self.download_video(video_url)
        if _full_path is not None:
            _converted_path = self.convert_video(_full_path)
            self.detect_sport_events(_converted_path, skip_time, break_on_time)
            data = self.recognize_sport_event(_converted_path, skip_time, break_on_time)
            data.replace("line_out", "lineout", inplace=True)
            data.sort_values(by=['start_frame_id'], inplace=True)
        return data
