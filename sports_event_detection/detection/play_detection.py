#!/usr/bin/env python3
"""
@Filename:    play_noplay_classification.py
@Author:      dulanj
@Time:        30/01/2022 13:40
"""
import logging

from PIL import Image

from sports_event_detection.detection.detections import Detection
from sports_event_detection.extras.common import ModelNames
from sports_event_detection.extras.draw import put_text
from sports_event_detection.models.classify import Classify


class PlayDetection(Detection):
    def __init__(self, video_path, db_name, model_path):
        model_name = ModelNames.activity_classification_model.name
        super().__init__(video_path, db_name, model_path, model_name)

    def load_model(self):
        logging.info('Loading model {}'.format(self.weights_path))
        return Classify(self.weights_path)

    def get_model_output(self, model, frame):
        pil_image = Image.fromarray(frame)
        _pred = model.predict(pil_image)
        _pred_json = {
            'class': _pred.get_class(),
            'prob': _pred.get_prob()
        }
        return _pred_json

    def draw_info(self, frame, data_json):
        out_frame = put_text(frame,
                             f"{data_json['data'][f'{self.model_name}']['class']} - "
                             f"{data_json['data'][f'{self.model_name}']['prob']}",
                             (25, 25), color=(0, 0, 255))
        return out_frame
