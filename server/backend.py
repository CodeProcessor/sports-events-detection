#!/usr/bin/env python3
"""
@Filename:    backend.py
@Author:      dulanj
@Time:        04/02/2022 13:53
"""
import os
import sys

sys.path.append("/home/dulanj/MSc/sports-events-detection")

from sports_event_detection.video_operations import VideoOperations
from sports_event_detection.youtube_downloader import YouTubeDownloader


class SportEventDetectionBackend:
    def __init__(self):
        pass

    def download_video_and_convert(self, video_url, output_path=None):
        _fps = 5
        yt_downloader = YouTubeDownloader(video_url)
        yt_downloader.get_info()
        _full_path = yt_downloader.download_video("youtube_downloads")
        print("Downloaded video: " + _full_path)

        video_op = VideoOperations(_full_path)
        video_op.get_video_info()
        video_op.change_fps(_fps)
        # video_op.split_video("00:01:00", "00:02:00")

        if output_path is None:
            output_path = os.path.join(f"video_outputs_{_fps}fps", os.path.basename(_full_path))
        video_op.save(output_path)

    def detect_sport_event(self, image_path):
        pass


if __name__ == '__main__':
    backend = SportEventDetectionBackend()
    backend.download_video_and_convert("https://www.youtube.com/watch?v=2Vv-BfVoq4g")
