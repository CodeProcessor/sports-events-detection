#!/usr/bin/env python3
"""
@Filename:    video_operations.py
@Author:      dulanj
@Time:        01/02/2022 21:13
"""
import logging
import os
import random
import string
import subprocess
from pathlib import Path

from sports_event_detection.video_reader import VideoReader

logging.getLogger("ffmpeg").setLevel(logging.ERROR)


class VideoOperations:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_name = Path(video_path).stem
        self.video_dir = Path(video_path).parent
        self.video_ext = Path(video_path).suffix

        self.video_full_path_str = str(self.video_path)

        self.video_cv = VideoReader(self.video_full_path_str)

        self.video_in = video_path
        self.video_out = self.get_random_name()

        self.video_info: VideoReader = None

    def get_random_name(self):
        length = 10
        result = ''.join(
            (random.choice(string.ascii_lowercase) for x in range(length)))  # run loop until the define length
        return result + self.video_ext

    def set_random_in_out_name(self):
        logging.info("Set random in out name, in: %s, out: %s", self.video_in, self.video_out)
        if self.video_path != self.video_in:
            os.remove(self.video_in)
        self.video_in = self.video_out
        self.video_out = self.get_random_name()
        return True

    def get_video_info(self):
        video_cv = VideoReader(self.video_in)
        print("FPS:", video_cv.get_fps())
        print("Frame count:", video_cv.get_total_frame_count())
        print("Frame size:", video_cv.get_shape())
        self.video_info = video_cv

    def split_video(self, start_second: str, end_second: str):
        command = "ffmpeg -i " + self.video_in + " -ss " + start_second + " -to " + end_second + \
                  " -c:v libx264 -crf 30 " + self.video_out

        logging.info("Execute command: %s", command)
        subprocess.call(command, shell=True)
        logging.info("Video Split Successfully from %s to %s", start_second, end_second)

        self.set_random_in_out_name()
        self.get_video_info()
        return 0

    def split_video_frames(self, start_frame, end_frame):
        return self.split_video(self.video_info.get_video_time(start_frame), self.video_info.get_video_time(end_frame))

    def change_fps(self, fps):
        if fps < self.video_info.get_fps():
            command = "ffmpeg -i " + self.video_in + " -filter:v fps=" + str(fps) + " " + self.video_out
            logging.info("Execute command: %s", command)

            subprocess.call(command, shell=True)
            logging.info("Video Change FPS Successfully from %s to %s", self.video_info.get_fps(), fps)
        else:
            logging.info("Video FPS is not higher than %s", fps)
            raise Exception("Video FPS is not higher than %s", fps)

        self.set_random_in_out_name()
        self.get_video_info()
        return 0

    def save(self, output_path):
        _out_dirname = os.path.dirname(output_path)
        if not os.path.exists(_out_dirname):
            os.makedirs(_out_dirname)
        os.rename(self.video_in, output_path)
        logging.info("Video Save Successfully to %s", output_path)
        return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    video_path = '/home/dulanj/MSc/DialogRugby/Match#1_Navy_SC_vs_Havelock_SC_DRL_2019_20_20fps.mp4'
    video_operations = VideoOperations(video_path)
    video_operations.get_video_info()
    video_operations.split_video("00:40:00", "00:50:00")
    # video_operations.split_video_frames(100, 500)
    video_operations.change_fps(5)
    video_operations.save("/home/dulanj/MSc/DialogRugby/short_clips/match_1_short_clip.mp4")

    # video_info = VideoReader("/home/dulanj/MSc/DialogRugby/10fps/match2.mp4")
    # print(video_info.get_fps())
