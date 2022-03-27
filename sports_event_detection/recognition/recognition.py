#!/usr/bin/env python3
"""
@Filename:    recognition.py
@Author:      dulanj
@Time:        19/02/2022 12:38
"""
import os

from sports_event_detection.utils.storage import Storage
from sports_event_detection.utils.video_reader import VideoReader
from sports_event_detection.utils.video_writer import SEDVideoWriter


class Recognition:
    def __init__(self, video_path, db_name, save_clip=False):
        self.model = None
        self.video = VideoReader(video_path, verbose=True)
        self.storage = Storage(db_name)
        self.window_size = int(1 * self.video.get_fps())
        self.event_name = None
        print("Video path: {}\n"
              "DB path: {}\n"
              "Total frames: {}".format(video_path, db_name, self.video.get_total_frame_count()))
        self.save_clip = save_clip

    def frame_to_time(self, frame_id):
        seconds = frame_id / self.video.get_fps()
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    def clip_event(self, dir_name, clip_name, from_frame_id, to_frame_id):
        video_dir_path = os.path.join("../event_clips", self.video.get_video_name(), dir_name)
        video_writer = SEDVideoWriter(clip_name, self.video.get_fps(), video_dir_path)
        self.video.seek(from_frame_id)
        for _ in range(from_frame_id, to_frame_id):
            frame = self.video.read_frame()
            if frame is not None:
                video_writer.write(frame)
        video_writer.clean()
        print("Clip {} created from {} to {} and saved to {}".format(
            clip_name,
            self.frame_to_time(from_frame_id),
            self.frame_to_time(to_frame_id),
            os.path.join(video_dir_path, clip_name))
        )
