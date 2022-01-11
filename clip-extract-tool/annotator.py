'''
Created on 6/6/21

@author: dulanj
'''
import os

import cv2

from data_file import DataFile
from video_reader import VideoReader
from video_writer import SEDVideoWriter


class Annotate:
    def __init__(self, video_file_path=None, data_file_path=None, sheet_name=None):
        if video_file_path is None:
            video_file_path = "/home/dulanj/MSc/Research/CH & FC v Kandy SC - DRL 2019_20 Match #23.mp4"
        if data_file_path is None:
            data_file_path = "data/datafile/Data results edited.xlsx"
        if sheet_name is None:
            sheet_name = 'Match1a'
        self.match_id = int((os.path.basename(video_file_path).split('.')[0].split('#')[-1]))
        self.clip_save_dir = "clips_3c"
        self.video = VideoReader(video_file_path)
        self.data = DataFile(filename=data_file_path, sheetname=sheet_name, fps=self.video.get_fps())

    def test(self):
        frame = self.video.seek_n_read(10000)
        cv2.imshow('display', frame)
        _key = cv2.waitKey(5)

    def main(self):
        for i in range(0, self.data.get_shape()[0]):
            data_obj = self.data.get_info(i)
            self.save_clip(data_obj)

    def save_clip(self, data_obj):
        start_point = data_obj.frame_no
        end_point = start_point + data_obj.duration
        activity_name = data_obj.activity.name
        print(f"Next clip from {start_point} to {end_point}")
        if start_point == 0:
            print("Skipping invalid clip")
            return 0
        clip_name = f"clip_m-{self.match_id}_s-{start_point}_e-{end_point}_{activity_name}.mp4"
        video_writer = SEDVideoWriter(clip_name, fps=self.video.get_fps(), save_loc=self.clip_save_dir)
        self.video.seek(start_point)
        for _ in range(end_point - start_point):
            frame = self.video.read_frame()
            cv2.imshow('display', frame)
            video_writer.write(frame)
        video_writer.clean()
        # print(f"{clip_name} saved!")


if __name__ == "__main__":
    videos = [
        "/home/dulanj/MSc/DialogRugby/CH & FC v Kandy SC - DRL 2019-20 Match #23.mp4",
        "/home/dulanj/MSc/DialogRugby/Kandy SC v Police SC – DRL 2019-20 #56.mp4",
        "/home/dulanj/MSc/DialogRugby/Kandy SC v CH & FC – DRL 2019-20 #35.mp4"
    ]
    data_file = "/home/dulanj/MSc/sports-events-detection/data/Data results edited.xlsx"
    sheet_names = [
        "Match1",
        "Match2",
        "Match3",
    ]

    for video, sheet in zip(videos, sheet_names):
        annotate = Annotate(video_file_path=video, data_file_path=data_file, sheet_name=sheet)
        annotate.main()
