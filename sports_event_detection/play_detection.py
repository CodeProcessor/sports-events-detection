#!/usr/bin/env python3
"""
@Filename:    play_noplay_classification.py
@Author:      dulanj
@Time:        30/01/2022 13:40
"""
import logging
import os

from PIL import Image

from sports_event_detection.classify import Classify
from sports_event_detection.common import ModelNames
from sports_event_detection.draw import put_text
from sports_event_detection.params import database_update_frequency
from sports_event_detection.storage import Storage
from sports_event_detection.video_reader import VideoReader

logging.basicConfig(level=logging.INFO)


class PlayDetection:
    def __init__(self, video_path, db_name, model_path):
        self.model = None
        self.model_path = model_path
        self.storage = Storage(db_name)
        self.video = VideoReader(video_path, verbose=True)
        self.video_writer = None  # SEDVideoWriter("output_play_noplay.mp4", 25, "output")
        self.model_name = ModelNames.play_noplay_classification_model.name

    def load_model(self):
        logging.info('Loading model {}'.format(self.model_path))
        return Classify(self.model_path)

    def get_data(self, frame_count, frame):
        data_json = self.storage.get_data(frame_count)
        is_model_inference = data_json is None or self.model_name not in data_json["data"]
        if is_model_inference:
            if self.model is None:
                self.model = self.load_model()
            _pred = self.model.predict(frame)
            _pred_json = {
                'class': _pred.get_class(),
                'prob': _pred.get_prob()
            }
            if data_json is None:
                logging.debug('No data found for frame {}, predicting'.format(frame_count))
                data_json = {
                    'frame_id': frame_count,
                    'data': {
                        f"{self.model_name}": _pred_json
                    }
                }
            else:
                logging.debug('Data found for frame {}, but not specific model predicting'.format(frame_count))
                data_json['data'][f"{self.model_name}"] = _pred_json
        else:
            logging.debug('Data found for frame {}, skipping'.format(frame_count))

        return is_model_inference, data_json

    def video_loop(self, skip_frames=0, break_on_frame=None):
        frame_number = skip_frames
        self.video.seek(skip_frames)
        frame = self.video.read_frame()
        data_json = {
            'frame_id': 1,
            'data':
                {
                    f'{self.model_name}': {
                        'class': "",
                        'prob': ""
                    }
                }
        }
        bulk_data = []
        bulk_delete_ids = []
        try:
            while frame is not None:
                if break_on_frame is not None and break_on_frame < frame_number:
                    break

                pil_image = Image.fromarray(frame)
                is_store, data_json = self.get_data(frame_number, pil_image)
                if is_store:
                    bulk_data.append(data_json)
                    bulk_delete_ids.append(frame_number)

                if len(bulk_data) > database_update_frequency:
                    self.storage.delete_bulk_data(bulk_delete_ids)
                    self.storage.insert_bulk_data(bulk_data)
                    bulk_data = []
                    bulk_delete_ids = []

                if self.video_writer is not None:
                    out_frame = put_text(frame,
                                         f"{data_json['data'][f'{self.model_name}']['class']} - "
                                         f"{data_json['data'][f'{self.model_name}']['prob']}",
                                         (25, 25), color=(0, 0, 255))
                    #     cv2.imshow('frame', out_frame)
                    #     if cv2.waitKey(1) & 0xFF == ord('q'):
                    #         break
                    # else:
                    self.video_writer.write(out_frame)
                # if frame_number % 100 == 0:
                #     print("Frame: {} - {}".format(frame_number, self.video.get_video_time()))
                frame_number += 1
                frame = self.video.read_frame()
        except KeyError as ke:
            print(ke)
        self.storage.delete_bulk_data(bulk_delete_ids)
        self.storage.insert_bulk_data(bulk_data)


if __name__ == '__main__':
    model_name = "/home/dulanj/MSc/sports-events-detection/data/trained_models/play_noplay/best-model-parameters3.pt"
    video_path = "/home/dulanj/MSc/DialogRugby/Match#56_Kandy_SC_v_Police_SC_DRL_2019_20.mp4"
    db_name = os.path.join("data_storage", os.path.basename(video_path).split('.')[0] + '.db')
    pd_obj = PlayDetection(video_path, db_name, model_name)
    pd_obj.video_loop()
