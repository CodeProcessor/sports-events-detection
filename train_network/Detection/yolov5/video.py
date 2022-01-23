#!/usr/bin/env python3
"""
@Filename:    video.py
@Author:      dulanj
@Time:        12/01/2022 00:17
"""
import logging
import os

import cv2

from storage import Storage
from yolo_model import YoloModel


class SportsEventsDetection:
    def __init__(self):
        self.model = None
        self.video_path = '/home/dulanj/MSc/DialogRugby/out-s-20_30-e-23_30-match-16.mp4'
        db_name = os.path.basename(self.video_path).split('.')[0] + '.db'
        self.storage = Storage(db_name)

    def load_model(self):
        """

        :return:
        """
        weight_path = '/home/dulanj/MSc/yolov5/runs/train/exp5/weights/best.pt'
        model = YoloModel(weight_path)
        return model

    def get_data(self, frame_count, frame):
        data_json = self.storage.get_data(frame_count)
        is_model_inference = data_json is None
        if is_model_inference:
            if self.model is None:
                self.model = self.load_model()
            logging.info('No data found for frame {}, predicting'.format(frame_count))
            data_json = {
                'frame_id': frame_count,
                'scrum_lineout_pred': self.model.predict(frame).tolist()
            }
        else:
            logging.debug('Data found for frame {}, skipping'.format(frame_count))

        return is_model_inference, data_json

    def main(self):
        cap = cv2.VideoCapture(self.video_path)
        frame_count = 0
        ret, frame = cap.read()
        bulk_data = []

        while ret:
            frame_count += 1
            if frame_count % 100 == 0:
                print('Processing frame {}'.format(frame_count))

            is_store, data_json = self.get_data(frame_count, frame)
            if is_store:
                bulk_data.append(data_json)

            if len(bulk_data) > 100:
                self.storage.insert_bulk_data(bulk_data)
                bulk_data = []

            # Visualize
            for det in data_json['scrum_lineout_pred']:
                cv2.rectangle(frame, (int(det[0]), int(det[1])), (int(det[2]), int(det[3])), (0, 0, 255), 2)

            cv2.imshow('frame', frame)
            cv2.waitKey(1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            ret, frame = cap.read()
        self.storage.insert_bulk_data(bulk_data)

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    sed = SportsEventsDetection()
    sed.main()
