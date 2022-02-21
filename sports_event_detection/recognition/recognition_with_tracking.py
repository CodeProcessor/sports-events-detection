#!/usr/bin/env python3
"""
@Filename:    recognition_with_tracking.py
@Author:      dulanj
@Time:        19/02/2022 14:42
"""
import time

import cv2

from sports_event_detection.extras.common import ModelNames
from sports_event_detection.recognition.event_objects import Event
from sports_event_detection.recognition.recognition import Recognition
from sports_event_detection.recognition.tracking import Tracking


class TrackRecognition(Recognition):
    def __init__(self, video_path, db_name):
        super().__init__(video_path, db_name)
        self.track_scrum = Tracking("scrum")
        self.track_lineout = Tracking("lineout")
        self.track_ruck = Tracking("ruck")
        self.frame_count = 7090
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

    def recognize(self):
        self.video.seek(self.frame_count)
        frame = self.video.read_frame()
        while frame is not None:
            self.frame_count += 1
            data = self.storage.get_data(self.frame_count)
            events = data["data"][ModelNames.sport_events_object_detection_model.name]

            scrum_events = [event for event in events if event[-1] == 0.0]
            lineout_events = [event for event in events if event[-1] == 1.0]
            ruck_events = [event for event in events if event[-1] == 2.0]

            _object_list_1 = self.track_scrum.update(scrum_events)
            _object_list_2 = self.track_lineout.update(lineout_events)
            _object_list_3 = self.track_ruck.update(ruck_events)

            _object_list = _object_list_1 + _object_list_2 + _object_list_3

            self.draw_object_list(_object_list, frame)
            self.draw_event_list(data["data"][ModelNames.sport_events_object_detection_model.name], frame)
            print(data)
            # print("Processing frame {}".format(frame_count))
            cv2.imshow("frame", frame)
            c = cv2.waitKey(1)
            if c == 27:
                break
            time.sleep(0.05)
            frame = self.video.read_frame()
            print(f"Registered events Scrum: {self.track_scrum.get_event_counts()}"
                  f" Lineout: {self.track_lineout.get_event_counts()}"
                  f" Ruck: {self.track_ruck.get_event_counts()}")
        cv2.destroyAllWindows()


if __name__ == '__main__':
    _video_path = '/home/dulanj/MSc/sports-events-detection/server/video_outputs_5fps/CH___FC_v_CR___FC_–_DRL_2019_20_#7.mp4'
    _db_name = '/home/dulanj/MSc/sports-events-detection/server/data_storage/CH___FC_v_CR___FC_–_DRL_2019_20_#7.db'
    tr = TrackRecognition(_video_path, _db_name)
    tr.recognize()
