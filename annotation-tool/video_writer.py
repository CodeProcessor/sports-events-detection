#!/usr/bin/env python
"""
# -*- coding:utf-8 -*-
# @Filename:    video_writer.py
# @Author:      dulanj
# @Time:        2021-07-25 13.08
"""
import cv2


class SEDVideoWriter:
    def __init__(self, file_name):
        self.filename = file_name
        self.__fourcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
        self.video_writer = None

    def write(self, frame):
        if self.video_writer is not None:
            self.video_writer.write(frame)
        else:
            self.video_writer = cv2.VideoWriter(self.filename, self.__fourcc, 30, (frame.shape[1], frame.shape[0]))
            self.video_writer.write(frame)
        
    
    def clean(self):
        self.video_writer.release()
        self.video_writer = None
    