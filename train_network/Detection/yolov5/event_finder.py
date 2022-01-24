#!/usr/bin/env python3
"""
@Filename:    event_finder.py
@Author:      dulanj
@Time:        24/01/2022 20:13
"""
import os
from collections import deque

from storage import Storage


class EventFinder:
    def __init__(self):
        video_path = '/home/dulanj/MSc/DialogRugby/out-s-20_30-e-40_00-match-16.mp4'
        db_name = os.path.basename(video_path).split('.')[0] + '.db'
        self.storage = Storage(db_name)
        self.classes = {
            0: 'scrum',
            1: 'line_out'
        }
        self.class_reverse = {v: k for k, v in self.classes.items()}

    def get_moving_average(self, queue, event_name):
        """
        Get the moving average of the queue
        :param queue:
        :return:
        """
        _classes_count = 0
        # events = [data for data in queue if data is not None and "scrum_lineout_pred" in data]
        for data in queue:
            if data is not None and "scrum_lineout_pred" in data:
                # print(data)
                for event in data["scrum_lineout_pred"]:
                    if int(event[-1]) == self.class_reverse[event_name]:
                        _classes_count += 1
        return _classes_count / len(queue)

    def frame_to_time(self, frame_id):
        seconds = frame_id / 30
        minutes = seconds // 60
        seconds = seconds % 60
        return "{:02d}:{:02d}".format(int(minutes), int(seconds))

    def find_event(self, event_name):
        _max_len = 100
        queue = deque(maxlen=_max_len)
        for frame_id in range(1, 50000, 5):
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
    ef = EventFinder()
    ef.find_event('scrum')
