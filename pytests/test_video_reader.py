#!/usr/bin/env python3
"""
@Filename:    test_video_reader.py
@Author:      dulanj
@Time:        05/02/2022 12:50
"""
import pytest

from sports_event_detection.video_reader import VideoReader


class TestVideoReader:

    @pytest.fixture
    def video_reader(self):
        reader = VideoReader("assets/test_video.mp4", verbose=True)
        return reader

    def test_get_video_time(self, video_reader):
        video_reader.seek(92)
        assert video_reader.get_video_time() == "00:00:04"
        assert video_reader.get_video_time(115) == "00:00:05"

    def test_get_frame_no(self, video_reader):
        video_reader.seek(92)
        assert video_reader.get_frame_no() == 92
        assert video_reader.get_frame_no() == video_reader.get_frame_no(":00:00:04")
