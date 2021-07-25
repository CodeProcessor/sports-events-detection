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
        file_path = "/home/dulanj/MSc/Research/CH & FC v Kandy SC - DRL 2019_20 Match #23.mp4"
        self.video = VideoReader(file_path)
        self.data = DataFile()

    def test(self):
        frame = self.video.seek_n_read(10000)
        cv2.imshow('display', frame)
        _key = cv2.waitKey(5)

    def main(self):
        duration = 100
        for i in range(5):
            start_point = 1000 + i*100
            self.save_clip(start_point, start_point + duration)

    def save_clip(self, ts_from, ts_to):
        clip_name = f"clip_{ts_from}_{ts_to}.mp4"
        video_writer = SEDVideoWriter(clip_name)
        self.video.seek(ts_from)
        for _ in range(ts_to-ts_from):
            frame = self.video.read_frame()
            video_writer.write(frame)
        video_writer.clean()


if __name__ == "__main__":
    obj = Annotate()
    obj.main()
