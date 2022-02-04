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

from sports_event_detection.storage import Storage
from sports_event_detection.video_reader import VideoReader
from sports_event_detection.video_writer import SEDVideoWriter


class SportsEventsRecognition:
    def __init__(self, video_path, db_name, classes, save_clip=False):
        self.model = None
        self.video = VideoReader(video_path)
        self.storage = Storage(db_name)
        self.classes = classes
        self.class_reverse = {v: k for k, v in self.classes.items()}
        self.window_size = int(1 * self.video.get_fps())
        self.event_name = None
        print("Video path: {}\n"
              "DB path: {}\n"
              "Total frames: {}".format(video_path, db_name, self.video.get_total_frame_count()))
        self.save_clip = save_clip
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
        queue = deque(maxlen=self.window_size)
        event_frame_ids = []
        self.event_name = "_".join([event_name for _, event_name in mod_eve_list])
        for frame_id in tqdm(range(0, self.video.get_total_frame_count())):
            # time.sleep(1)
            data = self.storage.get_data(frame_id)
            queue.append(data)
            # print(data)
            # print(queue)

            ret = max(
                [self.get_moving_average(queue, model_name, event_name) for model_name, event_name in mod_eve_list])
            if ret >= 0.6:
                event_frame_ids.append(frame_id)
                # print("{}-{:.2f}-{}".format(frame_id, ret, self.frame_to_time(frame_id)))
                [queue.append(None) for _ in range(self.window_size)]
            if data is None:
                print(len(queue))
                break
        self.event_summary(event_frame_ids)

    def event_summary(self, event_frame_ids):
        event_gap = [None, None]
        _no_of_events = 0
        for f_id in event_frame_ids:
            if event_gap[0] is None:
                event_gap = [f_id, f_id]
            if f_id - event_gap[1] < self.window_size:
                event_gap[1] = f_id
            else:
                if event_gap[1] - event_gap[0] > self.window_size * 3:
                    _no_of_events += 1
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

    def clip_event(self, dir_name, clip_name, from_frame_id, to_frame_id):
        video_dir_path = os.path.join("event_clips", self.video.get_video_name(), dir_name)
        video_writer = SEDVideoWriter(clip_name, self.video.get_fps(), video_dir_path)
        self.video.seek(from_frame_id)
        for _ in range(from_frame_id, to_frame_id):
            frame = self.video.read_frame()
            if frame is not None:
                video_writer.write(frame)
        video_writer.clean()
        print("Clip {} created from {} to {} and saved to {}".format(
            clip_name,
            self.frame_to_time(from_frame_id),
            self.frame_to_time(to_frame_id),
            os.path.join(video_dir_path, clip_name))
        )


if __name__ == '__main__':
    video_path = '/home/dulanj/MSc/DialogRugby/out-s-20_30-e-40_00-match-16.mp4'
    db_name = os.path.basename(video_path).split('.')[0] + '.db'
    classes = {
        0: 'scrum',
        1: 'line_out'
    }
    ef = SportsEventsRecognition(video_path, db_name, classes)
    ef.find_event('scrum')
