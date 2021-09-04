'''
Created on 6/6/21

@author: dulanj
'''
import cv2

from data_file import DataFile
from video_reader import VideoReader
from video_writer import SEDVideoWriter


class Annotate:
    def __init__(self):
        video_file_path = "/home/dulanj/MSc/Research/CH & FC v Kandy SC - DRL 2019_20 Match #23.mp4"
        data_file_path = "data/datafile/Data results edited.xlsx"
        sheet_name = 'Match1'
        self.video = VideoReader(video_file_path)
        self.data = DataFile(filename=data_file_path, sheetname=sheet_name, fps=self.video.get_fps())

    def test(self):
        frame = self.video.seek_n_read(10000)
        cv2.imshow('display', frame)
        _key = cv2.waitKey(5)

    def main(self):
        for i in range(66):
            data_obj = self.data.get_info()
            self.save_clip(data_obj)

    def save_clip(self, data_obj):
        start_point = data_obj.frame_no
        end_point = start_point + data_obj.duration
        activity_name = data_obj.activity.name
        print(f"Next clip from {start_point} to {end_point}")
        if start_point == 0:
            print("Skipping invalid clip")
            return 0
        clip_name = f"clip_{start_point}_{end_point}_{activity_name}.avi"
        clip_save_dir = "//clips"
        video_writer = SEDVideoWriter(clip_name, fps=self.video.get_fps(), save_loc=clip_save_dir)
        self.video.seek(start_point)
        for _ in range(end_point - start_point):
            frame = self.video.read_frame()
            video_writer.write(frame)
        video_writer.clean()
        print(f"{clip_name} saved!")


if __name__ == "__main__":
    obj = Annotate()
    obj.main()
