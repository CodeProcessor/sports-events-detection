#!/usr/bin/env python3
"""
@Filename:    event_finder.py
@Author:      dulanj
@Time:        24/01/2022 20:13
"""
import os
import time
from collections import deque

from tqdm import tqdm

from storage import Storage
from video_reader import VideoReader


class SportsEventsRecognition:
    def __init__(self, video_path, db_name, classes):
        self.model = None
        self.video = VideoReader(video_path)
        self.storage = Storage(db_name)
        self.classes = classes
        self.class_reverse = {v: k for k, v in self.classes.items()}
        print("Video path: {}\n"
              "DB path: {}\n"
              "Total frames: {}".format(video_path, db_name, self.video.get_total_frame_count()))
        time.sleep(2)

    def is_correct_event(self, event, event_name):
        ret = False

        if event_name in ["scrum", "lineout"]:
            _is_same_event = int(event[-1]) == self.class_reverse[event_name]
            if _is_same_event:
                # print(event)
                ret = True
        elif event_name in ["digital"]:
            _is_same_event = int(event[-1]) == self.class_reverse[event_name]
            _width = event[2] - event[0]
            _height = event[3] - event[1]
            _covered_area = _width * _height
            if _is_same_event and _covered_area > 0.4:
                ret = True
        elif event_name in ["noplay"]:
            ret = (event["class"] == event_name) and (float(event["prob"]) > 0.9)
        else:
            raise NotImplementedError

        return ret

    def get_moving_average(self, queue, model_name, event_name):
        """
        Get the moving average of the queue
        :param queue:
        :return:
        """
        _classes_count = 0
        for data in queue:
            if data is not None and "data" in data:
                try:
                    if isinstance(data["data"][model_name], list):
                        for event in data["data"][model_name]:
                            if self.is_correct_event(event, event_name):
                                _classes_count += 1
                    else:
                        if self.is_correct_event(data["data"][model_name], event_name):
                            _classes_count += 1
                except KeyError as ke:
                    print(ke)
                    print("KeyError: frame id - {} data - {}".format(data["frame_id"], data))
        return _classes_count / len(queue)

    def frame_to_time(self, frame_id):
        seconds = frame_id / self.video.get_fps()
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    def find_event(self, mod_eve_list):
        _max_len = int(1 * self.video.get_fps())
        queue = deque(maxlen=_max_len)
        event_frame_ids = []
        _event_name = "_".join([event_name for _, event_name in mod_eve_list])
        for frame_id in tqdm(range(0, self.video.get_total_frame_count())):
            # time.sleep(1)
            data = self.storage.get_data(frame_id)
            queue.append(data)
            # print(data)
            # print(queue)

            ret = max(
                [self.get_moving_average(queue, model_name, event_name) for model_name, event_name in mod_eve_list])
            if ret > 0.8:
                event_frame_ids.append(frame_id)
                # print("{}-{:.2f}-{}".format(frame_id, ret, self.frame_to_time(frame_id)))
                [queue.append(None) for _ in range(_max_len)]
            if data is None:
                print(len(queue))
                break

        event_gap = [None, None]
        for f_id in event_frame_ids:
            if event_gap[0] is None:
                event_gap = [f_id, f_id]
            if f_id - event_gap[1] < _max_len:
                event_gap[1] = f_id
            else:
                if event_gap[1] - event_gap[0] > _max_len:
                    print("Event {} : {}-{} Duration {}".format(
                        _event_name,
                        self.frame_to_time(event_gap[0]),
                        self.frame_to_time(event_gap[1])
                        , self.frame_to_time(event_gap[1] - event_gap[0])
                    ))
                event_gap = [None, None]


if __name__ == '__main__':
    video_path = '/home/dulanj/MSc/DialogRugby/out-s-20_30-e-40_00-match-16.mp4'
    db_name = os.path.basename(video_path).split('.')[0] + '.db'
    classes = {
        0: 'scrum',
        1: 'line_out'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes)
    ef.find_event('scrum')
