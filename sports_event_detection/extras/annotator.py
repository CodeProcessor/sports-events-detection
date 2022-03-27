'''
Created on 6/6/21

@author: dulanj
'''
import os

import cv2

from sports_event_detection.extras.data_file import DataFile
from sports_event_detection.utils.video_reader import VideoReader
from sports_event_detection.utils.video_writer import SEDVideoWriter


class Annotate:
    def __init__(self, video_file_path, data_file_path, sheet_name=None, save_dir="clips", clip_list=None):
        self.match_id = int((os.path.basename(video_file_path).split('#')[1].split('_')[0]))
        self.clip_save_dir = save_dir
        self.video = VideoReader(video_file_path)
        if sheet_name is None:
            sheet_name = f"Match{self.match_id}"
        self.data = DataFile(filename=data_file_path, sheetname=sheet_name, fps=self.video.get_fps())
        self.clip_list = clip_list

    def test(self):
        frame = self.video.seek_n_read(10000)
        cv2.imshow('display', frame)
        _key = cv2.waitKey(5)

    def extract_all_clips(self):
        for i in range(0, self.data.get_shape()[0]):
            try:
                data_obj = self.data.get_info(i)
                self.save_clip(data_obj)
            except NotImplementedError as e:
                print(e)
                print("Skipping clip")
                continue

    def save_clip(self, data_obj):
        start_point = int(data_obj.frame_time_sec * self.video.get_fps())
        end_point = start_point + int(data_obj.duration_sec * self.video.get_fps() + 1)
        activity_name = data_obj.activity.name
        print(f"Next clip from {start_point} to {end_point}")
        if start_point == 0:
            print("Skipping invalid clip")
            return 0
        if not (self.clip_list is None or data_obj.activity in self.clip_list):
            print("Skip clip with activity type: " + activity_name)
            return 0
        clip_name = f"clip_{self.match_id}_{start_point}_{end_point}_{activity_name}.mp4"
        video_writer = SEDVideoWriter(clip_name, fps=self.video.get_fps(), save_loc=self.clip_save_dir)
        self.video.seek(start_point)
        for _ in range(end_point - start_point):
            frame = self.video.read_frame()
            if frame is not None:
                cv2.imshow('display', frame)
                video_writer.write(frame)
            else:
                print("Frame is None, skipping clip: ", clip_name)
                break
        video_writer.clean()
        # print(f"{clip_name} saved!")
