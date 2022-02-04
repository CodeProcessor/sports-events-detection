#!/usr/bin/env python3
"""
@Filename:    video.py
@Author:      dulanj
@Time:        12/01/2022 00:17
"""
import logging
import time

import cv2

from sports_event_detection.storage import Storage
from sports_event_detection.video_reader import VideoReader
from sports_event_detection.yolo_model import YoloModel


class SportsEventsDetection:
    def __init__(self, video_path, db_name, weights_path, classes, model_name):
        self.model = None
        self.video = VideoReader(video_path)
        self.storage = Storage(db_name)
        self.weights_path = weights_path
        self.classes = classes
        self.model_name = model_name

    def load_model(self):
        """
        :return:
        """
        print('Loading model... - {} from {}'.format(self.model_name, self.weights_path))
        model = YoloModel(self.weights_path)
        return model

    def get_data(self, frame_count, frame):
        data_json = self.storage.get_data(frame_count)
        is_model_inference = data_json is None or self.model_name not in data_json["data"]
        if is_model_inference:
            if self.model is None:
                self.model = self.load_model()
            if data_json is None:
                logging.debug('No data found for frame {}, predicting'.format(frame_count))
                data_json = {
                    'frame_id': frame_count,
                    'data': {
                        f"{self.model_name}": self.model.predict(frame).tolist()
                    }
                }
            else:
                logging.debug('Data found for frame {}, but not specific model predicting'.format(frame_count))
                data_json['data'][f"{self.model_name}"] = self.model.predict(frame).tolist()
        else:
            logging.debug('Data found for frame {}, skipping'.format(frame_count))

        return is_model_inference, data_json

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

    def video_loop(self, skip_frames=0, break_on_frame=None):
        frame_count = skip_frames
        self.video.seek(skip_frames)
        frame = self.video.read_frame()
        bulk_data = []
        bulk_delete_ids = []
        viz_count = 100
        start_time = None

        try:
            while frame is not None:

                if break_on_frame is not None and break_on_frame < frame_count:
                    break
                if frame_count % viz_count == 0:
                    _fps = "{:.2f}".format(viz_count / (time.time() - start_time)) if start_time is not None else 'N/A'
                    print('Processing frame {} @ {} fps'.format(frame_count, _fps))
                    start_time = time.time()

                is_store, data_json = self.get_data(frame_count, frame)
                if is_store:
                    bulk_data.append(data_json)
                    bulk_delete_ids.append(frame_count)

                if len(bulk_data) > 100:
                    self.storage.delete_bulk_data(bulk_delete_ids)
                    self.storage.insert_bulk_data(bulk_data)
                    bulk_data = []
                    bulk_delete_ids = []

                frame = self.draw_info(frame, data_json)

                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                frame_count += 1
                frame = self.video.read_frame()
        except KeyError as ke:
            print(ke)
        self.storage.delete_bulk_data(bulk_delete_ids)
        self.storage.insert_bulk_data(bulk_data)

        self.video.cleanup()
        cv2.destroyAllWindows()
