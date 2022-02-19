#!/usr/bin/env python3
"""
@Filename:    video.py
@Author:      dulanj
@Time:        12/01/2022 00:17
"""

import cv2

from sports_event_detection.detection.detections import Detection
from sports_event_detection.yolo_model import YoloModel


class SportsEventsDetection(Detection):
    def __init__(self, video_path, db_name, weights_path, classes, model_name):
        super().__init__(video_path, db_name, weights_path)
        self.classes = classes
        self.model_name = model_name

    def load_model(self):
        """
        :return:
        """
        print('Loading model... - {} from {}'.format(self.model_name, self.weights_path))
        model = YoloModel(self.weights_path)
        return model

    def get_model_output(self, model, frame):
        raise model.predict(frame).tolist()

    def draw_info(self, frame, data_json):
        # Visualize
        h, w = frame.shape[:2]
        for det in data_json['data'][f"{self.model_name}"]:
            _class_id = int(det[-1])
            _confidence = round(float(det[-2]), 2)
            cv2.rectangle(frame, (int(det[0] * w), int(det[1] * h)), (int(det[2] * w), int(det[3] * h)), (0, 0, 255), 2)
            cv2.putText(frame, f"{self.classes[_class_id]}-{_confidence}", (int(det[0] * w), int(det[1] * h)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(frame, 'Frame: {}'.format(data_json['frame_id']), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        return frame
