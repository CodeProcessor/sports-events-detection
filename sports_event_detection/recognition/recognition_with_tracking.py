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
from sports_event_detection.utils.video_writer import SEDVideoWriter


class TrackRecognition(Recognition):
    def __init__(self, video_path, db_name, output_path=None):
        print("[INFO] Initializing TrackRecognition...")
        super().__init__(video_path, db_name)
        self.track_scrum = Tracking("scrum", max_disappeared=5, min_update_count=15, min_lifespan=40)
        self.track_lineout = Tracking("lineout", max_disappeared=5, min_update_count=20, min_lifespan=40)
        self.track_ruck = Tracking("ruck", max_disappeared=5, min_update_count=20, min_lifespan=20)
        self.frame_count = 0
        self.class_labels = {
            0: 'scrum',
            1: 'line_out',
            2: 'ruck'
        }
        if output_path is not None:
            self.video_writer = SEDVideoWriter(output_path, 5, 'output')
        else:
            self.video_writer = None

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
            cv2.putText(frame, str(round(obj.confidence, 2)), (x1, y1 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                        2)

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
            _txt = f"{self.class_labels[class_id]}-{round(confidence, 2)}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, _txt, (x2 - 50, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    def create_structured_df(self, dataframe):
        start_time = [self.frame_to_time(st) for st in dataframe["start_frame_id"].to_list()]
        end_time = [self.frame_to_time(et) for et in dataframe["end_frame_id"].to_list()]
        duration = [self.frame_to_time(et - st) for st, et in
                    zip(dataframe["start_frame_id"].to_list(), dataframe["end_frame_id"].to_list())]
        dataframe["start_time"] = start_time
        dataframe["end_time"] = end_time
        dataframe["duration"] = duration
        return dataframe

    def recognize(self, skip_time="00:00:00", break_on_time=None, visualize=False):
        start_frame = self.video.get_frame_no(skip_time)
        end_frame = self.video.get_total_frame_count() if break_on_time is None else \
            self.video.get_frame_no(break_on_time)
        duration = end_frame - start_frame
        self.video.set_progress_bar_limit(duration)
        self.video.seek(start_frame)

        [tr.set_frame_count(start_frame) for tr in [self.track_scrum, self.track_lineout, self.track_ruck]]
        for frame_id in range(start_frame, end_frame):
            frame = self.video.read_frame()
            data = self.storage.get_data(frame_id)
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

            if visualize or self.video_writer is not None:
                self.draw_object_list(_object_list, frame)
                self.draw_event_list(data["data"][ModelNames.sport_events_object_detection_model.name], frame)
                txt = f"Frame {self.frame_count}" \
                      f" Scrum: {self.track_scrum.get_event_counts()}" \
                      f" Line-out: {self.track_lineout.get_event_counts()}" \
                      f" Ruck: {self.track_ruck.get_event_counts()}"
                cv2.putText(frame, txt, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                if visualize:
                    cv2.imshow("frame", frame)
                    c = cv2.waitKey(1)
                    if c == 27:
                        break
                    # time.sleep(0.05)
                    print(txt)

                if self.video_writer is not None:
                    self.video_writer.write(frame)

        cv2.destroyAllWindows()
        if self.video_writer is not None:
            self.video_writer.clean()
        scrum_df = self.track_scrum.events_dataframe
        lineout_df = self.track_lineout.events_dataframe
        ruck_df = self.track_ruck.events_dataframe
        concat_df = pd.concat([ruck_df, scrum_df, lineout_df], ignore_index=True)
        concat_df = self.create_structured_df(concat_df)

        return concat_df
