#!/usr/bin/env python3
"""
@Filename:    event_finder.py
@Author:      dulanj
@Time:        24/01/2022 20:13
"""
import os
from collections import deque

import pandas as pd
from tqdm import tqdm

from sports_event_detection.recognition.recognition import Recognition


class SportsEventsRecognition(Recognition):
    def __init__(self, video_path, db_name, classes, save_clip=False):
        super().__init__(video_path, db_name, classes, save_clip)

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

    def find_event(self, mod_eve_list, skip_time="00:00:00", break_on_time=None, return_json=True):
        queue = deque(maxlen=self.window_size)
        self.event_name = "_".join([event_name for _, event_name in mod_eve_list])
        start_frame = self.video.get_frame_no(skip_time)
        end_frame = self.video.get_total_frame_count() if break_on_time is None else \
            self.video.get_frame_no(break_on_time)
        duration = end_frame - start_frame
        self.video.set_progress_bar_limit(duration)
        event_frame_data = {
            "event_frame_ids": [],
            "start_time": skip_time,
            "end_time": break_on_time,
            "event_name": self.event_name,
            "duration": duration
        }
        for frame_id in tqdm(range(start_frame, end_frame)):
            data = self.storage.get_data(frame_id)
            queue.append(data)

            ret = max(
                [self.get_moving_average(queue, model_name, event_name) for model_name, event_name in mod_eve_list])
            if ret >= 0.6:
                event_frame_data["event_frame_ids"].append(frame_id)
                # print("{}-{:.2f}-{}".format(frame_id, ret, self.frame_to_time(frame_id)))
                [queue.append(None) for _ in range(self.window_size)]
            if data is None:
                print(len(queue))
                break
        return self.event_summary(event_frame_data) if return_json else self.event_summary_df(event_frame_data)

    def event_summary(self, event_frame_data):
        _events = []
        event_gap = [None, None]
        _no_of_events = 0
        for f_id in event_frame_data["event_frame_ids"]:
            if event_gap[0] is None:
                event_gap = [f_id, f_id]
            if f_id - event_gap[1] < self.window_size:
                event_gap[1] = f_id
            else:
                if event_gap[1] - event_gap[0] > self.window_size * 3:
                    _no_of_events += 1
                    _events.append(
                        {
                            "event_name": self.event_name,
                            "start_frame_id": event_gap[0],
                            "end_frame_id": event_gap[1],
                            "start_time": self.frame_to_time(event_gap[0]),
                            "end_time": self.frame_to_time(event_gap[1]),
                            "duration": self.frame_to_time(event_gap[1] - event_gap[0])
                        }
                    )
                    print("Event {} : {}-{} Duration {}".format(
                        self.event_name,
                        self.frame_to_time(event_gap[0]),
                        self.frame_to_time(event_gap[1]),
                        self.frame_to_time(event_gap[1] - event_gap[0])
                    ))
                    self.clip_event(
                        f"{self.event_name}",
                        f"{self.event_name}_{_no_of_events}.mp4",
                        event_gap[0],
                        event_gap[1]
                    ) if self.save_clip else ""

                event_gap = [None, None]
        print("Total {} Events: {}".format(self.event_name, _no_of_events))
        _event_dictionary = {
            "event_name": self.event_name,
            "events": _events,
            "start_time": event_frame_data["start_time"],
            "end_time": event_frame_data["end_time"],
            "duration": event_frame_data["duration"],
            "total_event_frames": len(event_frame_data["event_frame_ids"]),
            "total_events": _no_of_events
        }
        return _event_dictionary

    def event_summary_df(self, event_frame_data):
        _event_dataframe = pd.DataFrame()
        _events = []
        event_gap = [None, None]
        _no_of_events = 0
        for f_id in event_frame_data["event_frame_ids"]:
            if event_gap[0] is None:
                event_gap = [f_id, f_id]
            if f_id - event_gap[1] < self.window_size:
                event_gap[1] = f_id
            else:
                if event_gap[1] - event_gap[0] > self.window_size * 3:
                    _no_of_events += 1
                    _event_dataframe = _event_dataframe.append(
                        {
                            "event_name": self.event_name,
                            "start_frame_id": int(event_gap[0]),
                            "end_frame_id": int(event_gap[1]),
                            "start_time": self.frame_to_time(event_gap[0]),
                            "end_time": self.frame_to_time(event_gap[1]),
                            "duration": self.frame_to_time(event_gap[1] - event_gap[0])
                        }, ignore_index=True
                    )
                    print("Event {} : {}-{} Duration {}".format(
                        self.event_name,
                        self.frame_to_time(event_gap[0]),
                        self.frame_to_time(event_gap[1]),
                        self.frame_to_time(event_gap[1] - event_gap[0])
                    ))
                    self.clip_event(
                        f"{self.event_name}",
                        f"{self.event_name}_{_no_of_events}.mp4",
                        event_gap[0],
                        event_gap[1]
                    ) if self.save_clip else ""

                event_gap = [None, None]
        print("Total {} Events: {}".format(self.event_name, _no_of_events))
        return _event_dataframe


if __name__ == '__main__':
    _video_path = '/home/dulanj/MSc/DialogRugby/out-s-20_30-e-40_00-match-16.mp4'
    _db_name = os.path.basename(_video_path).split('.')[0] + '.db'
    _classes = {
        0: 'scrum',
        1: 'line_out'
    }
    ef = SportsEventsRecognition(_video_path, _db_name, _classes)
    ef.find_event('scrum')
