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
    def __init__(self, video_file_path=None, data_file_path=None, sheet_name=None, save_dir="clips"):
        if video_file_path is None:
            video_file_path = "/home/dulanj/MSc/Research/CH & FC v Kandy SC - DRL 2019_20 Match #23.mp4"
        if data_file_path is None:
            data_file_path = "data/datafile/Data results edited.xlsx"
        if sheet_name is None:
            sheet_name = 'Match1a'
        self.match_id = int((os.path.basename(video_file_path).split('#')[1].split('_')[0]))
        self.clip_save_dir = save_dir
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


if __name__ == "__main__":
    videos = [
        "Match#18_Police_SC_v_CH_&_FC_DRL_2019_20.mp4",
        "Match#21_Air_Force_SC_v_Police_SC_DRL_2019_20.mp4",
        "Match#23_CH_&_FC_v_Kandy_SC_DRL_2019_20.mp4",
        "Match#30_Air_Force_SC_v_Kandy_SC_DRL_201920.mp4",
        "Match#35_Kandy_SC_v_CH_&_FC_DRL_2019_20.mp4",
        "Match#47_CH_&_FC_v_Air_Force_SC_DRL_2019_20.mp4",
        "Match#56_Kandy_SC_v_Police_SC_DRL_2019_20.mp4"
    ]
    data_file = "/home/dulanj/MSc/sports-events-detection/data/LSK Annotations Clean.xlsx"
    sheet_names = [18, 21, 23, 30, 35, 47, 56]
    skip_list = [18, 21, 23, 30, 35]
    for video, sheet in zip(videos, sheet_names):
        if sheet in skip_list:
            continue
        sheet_name = f"Match{sheet}"
        video_path = os.path.join("/home/dulanj/MSc/DialogRugby", video)
        annotate = Annotate(
            video_file_path=video_path,
            data_file_path=data_file,
            sheet_name=sheet_name,
            save_dir="data/clips_2c_7m"
        )
        annotate.main()
