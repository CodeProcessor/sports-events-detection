#!/usr/bin/env python3
"""
@Filename:    recognition_with_tracking.py
@Author:      dulanj
@Time:        19/02/2022 14:42
"""

import cv2
import pandas as pd

from sports_event_detection.extras.common import ModelNames
from sports_event_detection.recognition.event_objects import Event
from sports_event_detection.recognition.recognition import Recognition
from sports_event_detection.recognition.tracking import Tracking


class TrackRecognition(Recognition):
    def __init__(self, video_path, db_name):
        super().__init__(video_path, db_name)
        self.track_scrum = Tracking("scrum", min_lifespan=30)
        self.track_lineout = Tracking("lineout", min_lifespan=30)
        self.track_ruck = Tracking("ruck", min_lifespan=15)
        self.frame_count = 0
        self.class_labels = {
            0: 'scrum',
            1: 'line_out',
            2: 'ruck'
        }

    def draw_object_list(self, object_list, frame):
        h, w = frame.shape[:2]
        obj: Event
        for obj in object_list:
            # if obj.get_lifespan(self.frame_count) < 10:
            #     continue
            if obj.update_count < 10:
                continue
            x1, y1, x2, y2 = obj.get_bounding_box(h, w)
            x1, y1, x2, y2 = x1 - 1, y1 - 1, x2 + 1, y2 + 1
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, obj.event_name, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, str(obj.event_id), (x1, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, str(obj.confidence), (x1, y1 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def draw_event_list(self, event_list, frame):
        height, width = frame.shape[:2]
        for event in event_list:
            x1 = event[0]
            y1 = event[1]
            x2 = event[2]
            y2 = event[3]
            confidence = event[4]
            class_id = event[5]

            x1, y1, x2, y2 = [
                int(x1 * width),
                int(y1 * height),
                int(x2 * width),
                int(y2 * height)
            ]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, self.class_labels[class_id], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    def create_structured_df(self, dataframe):
        start_time = [self.frame_to_time(st) for st in dataframe["start_frame_id"].to_list()]
        end_time = [self.frame_to_time(et) for et in dataframe["end_frame_id"].to_list()]
        duration = [self.frame_to_time(et - st) for st, et in
                    zip(dataframe["start_frame_id"].to_list(), dataframe["end_frame_id"].to_list())]
        dataframe["start_time"] = start_time
        dataframe["end_time"] = end_time
        dataframe["duration"] = duration
        return dataframe

    def recognize(self, visualize=False):
        self.video.seek(self.frame_count)
        frame = self.video.read_frame()
        total_frame_count = self.video.get_total_frame_count()
        [tr.set_frame_count(self.frame_count) for tr in [self.track_scrum, self.track_lineout, self.track_ruck]]
        while frame is not None:
            self.frame_count += 1
            if self.frame_count > total_frame_count:
                break
            data = self.storage.get_data(self.frame_count)
            if data is None:
                continue
            events = data["data"][ModelNames.sport_events_object_detection_model.name]

            scrum_events = [event for event in events if event[-1] == 0.0]
            line_out_events = [event for event in events if event[-1] == 1.0]
            ruck_events = [event for event in events if event[-1] == 2.0]

            _object_list_1 = _object_list_2 = _object_list_3 = []
            _object_list_1 = self.track_scrum.update(scrum_events)
            _object_list_2 = self.track_lineout.update(line_out_events)
            _object_list_3 = self.track_ruck.update(ruck_events)

            _object_list = _object_list_1 + _object_list_2 + _object_list_3

            if visualize:
                self.draw_object_list(_object_list, frame)
                self.draw_event_list(data["data"][ModelNames.sport_events_object_detection_model.name], frame)
                cv2.imshow("frame", frame)
                c = cv2.waitKey(1)
                if c == 27:
                    break
                import time
                time.sleep(0.05)
                print(f"Registered events Scrum: {self.track_scrum.get_event_counts()}"
                      f" Line-out: {self.track_lineout.get_event_counts()}"
                      f" Ruck: {self.track_ruck.get_event_counts()}")
            frame = self.video.read_frame()
            # if self.frame_count > 10000:
            #     break

        cv2.destroyAllWindows()
        scrum_df = self.track_scrum.events_dataframe
        lineout_df = self.track_lineout.events_dataframe
        ruck_df = self.track_ruck.events_dataframe
        concat_df = pd.concat([ruck_df, scrum_df, lineout_df], ignore_index=True)
        print(concat_df.head())
        concat_df = self.create_structured_df(concat_df)
        print(concat_df)
        return concat_df


if __name__ == '__main__':
    _video_path = '/home/dulanj/MSc/sports-events-detection/server/video_outputs_5fps/CH___FC_v_CR___FC_–_DRL_2019_20_#7.mp4'
    _db_name = '/home/dulanj/MSc/sports-events-detection/server/data_storage/CH___FC_v_CR___FC_–_DRL_2019_20_#7.db'
    tr = TrackRecognition(_video_path, _db_name)
    dataframe = tr.recognize()
    dataframe.to_excel("CH___FC_v_CR___FC_–_DRL_2019_20_#7.xlsx")
