#!/usr/bin/env python3
"""
@Filename:    event_finder.py
@Author:      dulanj
@Time:        24/01/2022 20:13
"""
import os
from collections import deque

from storage import Storage
from video_reader import VideoReader


class SportsEventsRecognition:
    def __init__(self, video_path, db_name, classes, model_name, logic="default"):
        self.model = None
        self.video = VideoReader(video_path)
        self.storage = Storage(db_name)
        self.classes = classes
        self.model_name = model_name
        self.logic = logic
        self.class_reverse = {v: k for k, v in self.classes.items()}

    def is_correct_event(self, event, event_name):
        ret = False
        _is_same_event = int(event[-1]) == self.class_reverse[event_name]
        if self.logic == "default":
            if _is_same_event:
                print(event)
                ret = True
        elif self.logic == "banner":
            _width = event[2] - event[0]
            _height = event[3] - event[1]
            _covered_area = _width * _height
            if _is_same_event and _covered_area > 0.4:
                # print(event)
                ret = True
        else:
            raise NotImplementedError

        return ret

    def get_moving_average(self, queue, event_name):
        """
        Get the moving average of the queue
        :param queue:
        :return:
        """
        _classes_count = 0
        for data in queue:
            if data is not None and "data" in data:
                for event in data["data"][self.model_name]:
                    if self.is_correct_event(event, event_name):
                        _classes_count += 1
        return _classes_count / len(queue)

    def frame_to_time(self, frame_id):
        seconds = frame_id / self.video.get_fps()
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    def find_event(self, event_name):
        _max_len = int(5 * self.video.get_fps())
        queue = deque(maxlen=_max_len)
        for frame_id in range(1, 250000):
            data = self.storage.get_data(frame_id)
            queue.append(data)
            # print(data)
            # print(queue)
            ret = self.get_moving_average(queue, event_name)
            if ret > 0.8:
                print(frame_id, ret, self.frame_to_time(frame_id))
                [queue.append(None) for _ in range(_max_len)]
            if data is None:
                print(len(queue))
                break


if __name__ == '__main__':
    video_path = '/home/dulanj/MSc/DialogRugby/out-s-20_30-e-40_00-match-16.mp4'
    db_name = os.path.basename(video_path).split('.')[0] + '.db'
    classes = {
        0: 'scrum',
        1: 'line_out'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes)
    ef.find_event('scrum')
