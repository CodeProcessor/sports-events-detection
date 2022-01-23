#!/usr/bin/env python
"""
# -*- coding:utf-8 -*-
# @Filename:    video_writer.py
# @Author:      dulanj
# @Time:        2021-07-25 13.08
"""

import os

import cv2


class SEDVideoWriter:
    def __init__(self, file_name, fps, save_loc):
        if os.path.isfile(save_loc):
            os.remove(save_loc)
        if not os.path.exists(save_loc):
            os.makedirs(save_loc)
        self.__clip_save_loc = save_loc
        self.__filename = os.path.join(self.__clip_save_loc, file_name)
        self.__fps = fps
        self.__fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.__video_writer = None

    def write(self, frame):
        if self.__video_writer is None:
            self.__video_writer = cv2.VideoWriter(self.__filename, self.__fourcc, self.__fps,
                                                  (frame.shape[1], frame.shape[0]))
        self.__video_writer.write(frame)

    def clean(self):
        if self.__video_writer is not None:
            self.__video_writer.release()
            self.__video_writer = None
            print(f"{self.__filename} saved!")
        else:
            print(f"{self.__filename} not saved!")


if __name__ == '__main__':
    video_writer = SEDVideoWriter("clip_name.mp4", fps=5, save_loc='.')
    frame = cv2.imread('/home/dulanj/Pictures/frame.jpg')
    print(frame.shape)
    for _ in range(10):
        video_writer.write(frame)
    video_writer.clean()
