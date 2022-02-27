#!/usr/bin/env python3
"""
@Filename:    backend.py
@Author:      dulanj
@Time:        04/02/2022 13:53
"""
import hashlib
import json
import os
from datetime import datetime

from sports_event_detection.detection.event_detection import SportsEventsDetection
from sports_event_detection.detection.play_detection import PlayDetection
from sports_event_detection.extras.common import ModelNames
from sports_event_detection.recognition.event_recognition import SportsEventsRecognition
from sports_event_detection.utils.video_operations import VideoOperations
from sports_event_detection.utils.youtube_downloader import YouTubeDownloader


class SportEventDetectionBackend:
    def __init__(self, return_json=True, save_clips=False):
        self.return_json = return_json
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
        weight_path = 'models/digital_v3.pt'
        classes = {
            0: 'digital'
        }
        model_name = ModelNames.digital_object_detection_model.name
        sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
        sed.video_loop(skip_time, break_on_time, overwrite=self.prediction_override['digital'])

    def get_scrum_linout(self, video_path, skip_time, break_on_time):
        db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
        weight_path = 'models/events_v3.pt'
        classes = {
            0: 'scrum',
            1: 'line_out',
            2: 'ruck'
        }
        model_name = ModelNames.sport_events_object_detection_model.name
        sed = SportsEventsDetection(video_path, db_name, weight_path, classes, model_name)
        sed.video_loop(skip_time, break_on_time, overwrite=self.prediction_override['events'])

    def play_detection(self, video_path, skip_time, break_on_time):
        model_path = "models/activity_v3.pt"
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
            break_on_time,
            self.return_json
        )
        return [_noplay_event_summary_dict] if isinstance(_noplay_event_summary_dict, dict) else \
            _noplay_event_summary_dict

    def scrum_lineout_recognition(self, video_path, skip_time, break_on_time):
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
            break_on_time,
            self.return_json
        )
        _line_out_event_summary_dict = ef.find_event(
            [(ModelNames.sport_events_object_detection_model.name, 'line_out')],
            skip_time,
            break_on_time,
            self.return_json
        )
        _ruck_event_summary_dict = ef.find_event(
            [(ModelNames.sport_events_object_detection_model.name, 'ruck')],
            skip_time,
            break_on_time,
            self.return_json
        )
        return [_scrum_event_summary_dict, _line_out_event_summary_dict, _ruck_event_summary_dict] if \
            isinstance(_scrum_event_summary_dict, dict) \
            else _scrum_event_summary_dict.append(_line_out_event_summary_dict).append(_ruck_event_summary_dict)

    def detect_sport_events(self, video_path, skip_time, break_on_time):
        self.get_digital(video_path, skip_time, break_on_time)
        self.get_scrum_linout(video_path, skip_time, break_on_time)
        self.play_detection(video_path, skip_time, break_on_time)

    def recognize_sport_event(self, video_path, skip_time, break_on_time):
        _event_list_1 = self.scrum_lineout_recognition(video_path, skip_time, break_on_time)
        _event_list_2 = self.play_recognition(video_path, skip_time, break_on_time)
        return _event_list_1 + _event_list_2 if isinstance(_event_list_1, list) else _event_list_1.append(_event_list_2)

    def process_video(self, video_url, skip_time, break_on_time):
        event_lists = []
        _converted_path = ""
        _full_path = self.download_video(video_url)
        if _full_path is not None:
            _converted_path = self.convert_video(_full_path)
            # self.detect_sport_events(_converted_path, skip_time, break_on_time)
            event_lists = self.recognize_sport_event(_converted_path, skip_time, break_on_time)
        return {
            'video_url': video_url,
            'video_download_path': _full_path,
            'converted_path': _converted_path,
            'event_lists': event_lists
        } if isinstance(event_lists, list) else event_lists


if __name__ == '__main__':
    output_type_json = False
    backend = SportEventDetectionBackend(return_json=output_type_json)
    video_url_list = [
        "https://www.youtube.com/watch?v=hwn3NpEwBfk"
        # "https://www.youtube.com/watch?v=HGPhsSsZE7E",
        # "https://www.youtube.com/watch?v=hwn3NpEwBfk",
        # "https://www.youtube.com/watch?v=DhdYasfUcds",
        # "https://www.youtube.com/watch?v=2w1dwDE57jw",
        # "https://www.youtube.com/watch?v=WnrOpvy0U_w",
        # "https://www.youtube.com/watch?v=KMcrbMoJ2Mk"
        # "https://www.youtube.com/watch?v=ab--JFZNxMM",
        # "https://www.youtube.com/watch?v=ObFxcZtUkCg",
        # "https://www.youtube.com/watch?v=ol_0V671OQ8",
        # "https://www.youtube.com/watch?v=3qcArzTl5sk",
        # "https://www.youtube.com/watch?v=yx1ORXAIhNA",
        # "https://www.youtube.com/watch?v=hMjiUFExsRs",
        # "https://www.youtube.com/watch?v=Q51uDv1YzuU",
        # "https://www.youtube.com/watch?v=OLtz28d0OCI",
        # "https://www.youtube.com/watch?v=3iVlBS-vZuY",
        # "https://www.youtube.com/watch?v=VzGdHEcqcNM",
        # "https://www.youtube.com/watch?v=a-rhpeAcNpY",
        # "https://www.youtube.com/watch?v=2vGH7TzYw6k",
        # "https://www.youtube.com/watch?v=x4rvFbkcox4",
        # "https://www.youtube.com/watch?v=rCc9CxdLTrA",
        # "https://www.youtube.com/watch?v=PeixkhanS_M"
    ]
    for _video_url in video_url_list:
        ret = backend.process_video(_video_url, skip_time="00:00:00", break_on_time=None)
        print("Processed video: {}".format(_video_url))
        print("Time now: {}".format(datetime.now()))
        if output_type_json:
            print(json.dumps(ret, indent=4))
        else:
            print(ret.head())
        # print(json.dumps(ret, indent=4, sort_keys=True))

    # backend.process("https://www.youtube.com/watch?v=HGPhsSsZE7E")
