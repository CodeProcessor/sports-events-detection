#!/usr/bin/env python3
"""
@Filename:    backend.py
@Author:      dulanj
@Time:        04/02/2022 13:53
"""
import os
import sys

from sports_event_detection.common import ModelNames
from sports_event_detection.event_detection import SportsEventsDetection
from sports_event_detection.event_recognition import SportsEventsRecognition
from sports_event_detection.play_detection import PlayDetection

sys.path.append("/home/dulanj/MSc/sports-events-detection")

from sports_event_detection.video_operations import VideoOperations
from sports_event_detection.youtube_downloader import YouTubeDownloader


class SportEventDetectionBackend:
    def __init__(self):
        pass

    def download_video(self, video_url, video_path="youtube_downloads"):
        yt_downloader = YouTubeDownloader(video_url)
        yt_downloader.get_info()
        _full_path = yt_downloader.download_video(video_path)
        print("Downloaded video: " + _full_path)
        return _full_path

    def convert_video(self, video_path, output_path=None):
        _fps = 5
        if output_path is None:
            output_path = os.path.join(f"video_outputs_{_fps}fps", os.path.basename(video_path))

        if not os.path.exists(output_path):
            video_op = VideoOperations(video_path)
            video_op.get_video_info()
            video_op.change_fps(_fps)
            # video_op.split_video("00:01:00", "00:02:00")

            video_op.save(output_path)
            print("Converted video saved: " + output_path)
        else:
            print("Video already exists: " + output_path)
        return output_path

    def process(self, video_url, output_path=None):
        _full_path = self.download_video(video_url)
        _converted_path = self.convert_video(_full_path, output_path)
        # self.detect_sport_event(_converted_path)
        self.recognize_sport_event(_converted_path)
        return True

    def get_digital(self, video_path):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/digital/v3/best.pt'
        classes = {
            0: 'digital'
        }
        model_name = ModelNames.digital_object_detection_model.name
        sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
        sed.video_loop(skip_frames=0, break_on_frame=None)

    def get_scrum_linout(self, video_path):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        weight_path = '/home/dulanj/MSc/sports-events-detection/data/trained_models/scrum-lineout/best.pt'
        classes = {
            0: 'scrum',
            1: 'line_out'
        }
        model_name = ModelNames.scrum_lineout_object_detection_model.name
        sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
        sed.video_loop(skip_frames=0, break_on_frame=None)

    def play_detection(self, video_path):
        model_path = "/home/dulanj/MSc/sports-events-detection/data/trained_models/play_noplay/best-model-parameters3.pt"
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        pd_obj = PlayDetection(video_path, db_name, model_path)
        pd_obj.video_loop(skip_frames=0, break_on_frame=None)

    def play_recognition(self, video_path):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        classes = {
            0: 'digital'
        }
        ef = SportsEventsRecognition(video_path, db_name, classes, save_clip=True)
        mod_eve_list = [
            (ModelNames.digital_object_detection_model.name, 'digital'),
            (ModelNames.play_noplay_classification_model.name, 'noplay')
        ]
        ef.find_event(mod_eve_list)

    def scrum_lineout_recognition(self, video_path):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        classes = {
            0: 'scrum',
            1: 'lineout'
        }
        ef = SportsEventsRecognition(video_path, db_name, classes, save_clip=True)
        ef.find_event([(ModelNames.scrum_lineout_object_detection_model.name, 'scrum')])
        ef.find_event([(ModelNames.scrum_lineout_object_detection_model.name, 'lineout')])

    def detect_sport_event(self, video_path):
        self.get_digital(video_path)
        self.get_scrum_linout(video_path)
        self.play_detection(video_path)

    def recognize_sport_event(self, video_path):
        self.scrum_lineout_recognition(video_path)
        self.play_recognition(video_path)


if __name__ == '__main__':
    backend = SportEventDetectionBackend()
    backend.process("https://www.youtube.com/watch?v=OsMiN6QdiNw")
