'''
Created on 6/6/21

@author: dulanj
'''
import cv2

from data_file import DataFile
from video_reader import VideoReader
from video_writer import SEDVideoWriter


class Annotate():
    def __init__(self):
        video_file_path = "/home/dulanj/MSc/Research/CH & FC v Kandy SC - DRL 2019_20 Match #23.mp4"
        data_file_path = "/home/dulanj/MSc/Research/datafile/Data results.xlsx"
        self.video = VideoReader(video_file_path)
        self.data = DataFile(filename=data_file_path, fps=self.video.get_fps())

    def test(self):
        frame = self.video.seek_n_read(10000)
        cv2.imshow('display', frame)
        _key = cv2.waitKey(5)

    def main(self):
        duration = 10 * self.video.get_fps()
        for i in range(10):
            data_obj = self.data.get_info()
            start_point = data_obj.frame_no
            end_point = start_point + duration
            print(f"Next clip from {start_point} to {end_point}")
            self.save_clip(start_point, end_point)

    def save_clip(self, ts_from, ts_to):
        clip_name = f"clip_{ts_from}_{ts_to}.avi"
        clip_save_dir = "/home/dulanj/MSc/sports-events-detection/annotation-tool/clips"
        video_writer = SEDVideoWriter(clip_name, fps=self.video.get_fps(), save_loc=clip_save_dir)
        self.video.seek(ts_from)
        for _ in range(ts_to-ts_from):
            frame = self.video.read_frame()
            video_writer.write(frame)
        video_writer.clean()
        print(f"{clip_name} saved!")


if __name__ == "__main__":
    obj = Annotate()
    obj.main()
