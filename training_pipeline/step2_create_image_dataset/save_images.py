#!/usr/bin/env python3
"""
@Filename:    save_images.py
@Author:      dulanj
@Time:        2021-09-04 11.53
"""
import enum
import glob
import os
import sys

import cv2

from sports_event_detection.extras.common import EventTypes


class ExtractTypes(enum.Enum):
    manual = 0
    auto = 1


clip_type_to_freq = {
    EventTypes.lineout.name: 5,
    EventTypes.scrum.name: 10,
    EventTypes.kick.name: 3,
    EventTypes.ruck.name: 25,
    EventTypes.play.name: 15,
    EventTypes.noplay.name: 15,
    EventTypes.other.name: 15,
}




class Clips:
    _supported_extensions = ['avi', 'mp4']

    def __init__(self, path, _type, dest="", event_list=None):
        self._path = path
        self._extract_type = _type
        if not os.path.exists(dest):
            os.makedirs(dest)
        self._destination = dest
        self.type_dict = dict()
        self.event_list = [eve.name for eve in event_list] if event_list is not None else None

    def extract_clip(self, clip_path):
        _clip_info = self.clip_info(clip_path)
        _clip_type = _clip_info['type']
        _match_id = _clip_info['match_id']
        _start_pos = _clip_info['start_pos']

        video_clip = cv2.VideoCapture(clip_path)
        ret, frame = video_clip.read()
        frame_position = 1
        c = ""
        while ret:

            if c == 27 or c == 113:
                sys.exit(0)
            if c == 100:
                return 0

            def save_image():
                self.type_dict[_clip_type] += 1
                _file_name = os.path.join(self._destination, _clip_type,
                                          f"{_clip_type}_{_match_id:02d}_{_start_pos + frame_position}.jpg")
                _dir_name = os.path.dirname(_file_name)
                if not os.path.exists(_dir_name):
                    os.makedirs(_dir_name)
                cv2.imwrite(_file_name, frame)
                print(f"Image saved! - {_file_name}")

            if self.event_list is None or _clip_type in self.event_list:
                if self._extract_type == ExtractTypes.manual:
                    cv2.imshow('clip_window', frame)
                    print("Type q - exit | s - save")
                    c = cv2.waitKey(0)
                    print(c)
                    if c == 115:
                        save_image()
                elif self._extract_type == ExtractTypes.auto:
                    if frame_position % clip_type_to_freq[_clip_type] == 0:
                        save_image()
                else:
                    raise Exception("Invalid extract type")
            else:
                print(f"Skipping {_clip_type}")
            frame_position += 1
            ret, frame = video_clip.read()

    def clip_info(self, clip_name):
        _basename = os.path.basename(clip_name)
        _name, _ = _basename.split('.')
        _type = _name.split('_')[-1]
        if not (_type in self.type_dict.keys()):
            self.type_dict[_type] = 0
        _start_pos = _name.split('_')[-3]
        _end_pos = _name.split('_')[-2]
        _match_id = _name.split('_')[-4]
        return {
            'type': _type,
            'start_pos': int(_start_pos),
            'end_pos': int(_end_pos),
            'match_id': int(_match_id)
        }

    def extract(self):
        for clip in glob.glob(self._path + "/*.*"):
            print(clip)
            ext = clip.split('.')[-1]
            if ext in Clips._supported_extensions:
                self.extract_clip(clip)


if __name__ == '__main__':
    path_to_clips = "../step1_video_clip_extraction/data/clips_20m_ruck"
    destination = "data/rucks_v2_20m"
    _type = ExtractTypes.auto
    event_list = [
        # EventTypes.lineout,
        # EventTypes.scrum,
        # EventTypes.kick,
        EventTypes.ruck,
        # EventTypes.play,
        # EventTypes.noplay,
        # EventTypes.other,
    ]
    clip_obj = Clips(path_to_clips, _type, dest=destination, event_list=event_list)
    clip_obj.extract()
