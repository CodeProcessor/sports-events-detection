#!/usr/bin/env python3
"""
@Filename:    video_writer.py
@Author:      dulanj
@Time:        05/12/2021 11:59
"""
import cv2


class VideoWriter:
    def __init__(self, filename, fps):
        self.cap = None
        self.filename = filename
        self.fps = fps
        self.frame_no = 0

    def write(self, image, frame_no=None):
        if self.cap is None:
            self.cap = cv2.VideoWriter(self.filename, cv2.VideoWriter_fourcc(*'MP4V'), self.fps,
                                       (image.shape[1], image.shape[0]))
        self.frame_no += 1
        self.cap.write(image)

    def __del__(self):
        self.cap.release()
