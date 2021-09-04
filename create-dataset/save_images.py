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


class ExtractTypes(enum.Enum):
    manual = 0


class Clips:
    _supported_extensions = ['avi']

    def __init__(self, path, _type, dest=""):
        self._path = path
        self._extract_type = _type
        if not os.path.exists(dest):
            os.makedirs(dest)
        self._destination = dest
        self.type_dict = dict()

    def extract_clip(self, clip_path, _clip_type):
        video_clip = cv2.VideoCapture(clip_path)
        ret, frame = video_clip.read()
        while ret:
            cv2.imshow('clip_window', frame)
            print("Type q - exit | s - save")
            c = cv2.waitKey(0)
            print(c)
            ret, frame = video_clip.read()
            if c == 27 or c == 113:
                sys.exit(0)
            if self._extract_type == ExtractTypes.manual:
                if c == 115:
                    self.type_dict[_clip_type] += 1
                    _file_name = os.path.join(self._destination, _clip_type, f"{_clip_type}_{self.type_dict[_clip_type]}.jpg")
                    _dir_name = os.path.dirname(_file_name)
                    if not os.path.exists(_dir_name):
                        os.makedirs(_dir_name)
                    cv2.imwrite(_file_name, frame)
                    print(f"Image saved! - {_file_name}")

    def clip_info(self, clip_name):
        _basename = os.path.basename(clip_name)
        _name, _ = _basename.split('.')
        _type = _name.split('_')[-1]
        if not (_type in self.type_dict.keys()):
            self.type_dict[_type] = 0
        return _type

    def extract(self):
        for clip in glob.glob(self._path + "/*.*"):
            print(clip)
            ext = clip.split('.')[-1]
            if ext in Clips._supported_extensions:
                _type = self.clip_info(clip)
                self.extract_clip(clip, _type)


if __name__ == '__main__':
    path_to_clips = "../clip-extract-tool/clips"
    destination = "extracted_images"
    _type = ExtractTypes.manual
    clip_obj = Clips(path_to_clips, _type, dest=destination)
    clip_obj.extract()
