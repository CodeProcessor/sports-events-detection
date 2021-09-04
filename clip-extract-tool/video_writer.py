#!/usr/bin/env python
"""
# -*- coding:utf-8 -*-
# @Filename:    video_writer.py
# @Author:      dulanj
# @Time:        2021-07-25 13.08
"""
import cv2
import os


class SEDVideoWriter:
    def __init__(self, file_name, fps, save_loc):
        self.__clip_save_loc = save_loc
        self.__filename = os.path.join(self.__clip_save_loc, file_name)
        self.__fps = fps
        self.__fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.__video_writer = None

    def write(self, frame):
        if self.__video_writer is not None:
            self.__video_writer.write(frame)
        else:
            self.__video_writer = cv2.VideoWriter(self.__filename, self.__fourcc, self.__fps,
                                                  (frame.shape[1], frame.shape[0]))
            self.__video_writer.write(frame)

    def clean(self):
        # self.__video_writer.release()
        self.__video_writer = None


if __name__ == '__main__':
    video_writer = SEDVideoWriter("clip_name", fps=5, save_loc='.')

    for _ in range(10):
        video_writer.write(frame)
    video_writer.clean()