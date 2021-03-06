#!/usr/bin/env python3
"""
@Filename:    detections.py
@Author:      dulanj
@Time:        19/02/2022 09:33
"""
import logging
import os
import time

import cv2

from sports_event_detection.extras.params import database_update_frequency, save_video
from sports_event_detection.utils.storage import Storage
from sports_event_detection.utils.video_reader import VideoReader
from sports_event_detection.utils.video_writer import SEDVideoWriter


class Detection:
    def __init__(self, video_path, db_name, weights_path, model_name):
        self.model = None
        self.model_name = model_name
        self.weights_path = weights_path
        self.storage = Storage(db_name)
        self.video = VideoReader(video_path, verbose=True)
        _video_basename = os.path.basename(video_path)
        _video_name, _video_ext = os.path.splitext(_video_basename)
        _output_video_name = f"{_video_name}_{self.model_name}_output{_video_ext}"
        self.video_writer = SEDVideoWriter(_output_video_name, 25, "video_outputs") if \
            save_video else None

    def load_model(self):
        raise NotImplementedError

    def get_model_output(self, model, frame):
        raise NotImplementedError

    def draw_info(self, frame, data_json):
        raise NotImplementedError

    def get_data(self, frame_count, frame, overwrite=False):
        data_json = self.storage.get_data(frame_count)
        is_model_inference = overwrite or data_json is None or self.model_name not in data_json["data"]
        if is_model_inference:
            if self.model is None:
                self.model = self.load_model()
            if data_json is None:
                logging.debug('No data found for frame {}, predicting'.format(frame_count))
                data_json = {
                    'frame_id': frame_count,
                    'data': {
                        f"{self.model_name}": self.get_model_output(self.model, frame)
                    }
                }
            else:
                if overwrite:
                    logging.debug('Overwriting data for frame {}'.format(frame_count))
                else:
                    logging.debug('Data found for frame {}, but not specific model predicting'.format(frame_count))
                data_json['data'][f"{self.model_name}"] = self.get_model_output(self.model, frame)
        else:
            logging.debug('Data found for frame {}, skipping'.format(frame_count))

        return is_model_inference, data_json

    def video_loop(self, skip_time="00:00:00", break_on_time=None, visualize=False, overwrite=False):
        skip_frames = self.video.get_frame_no(skip_time)
        break_on_frame = self.video.get_total_frame_count() if break_on_time is None else \
            self.video.get_frame_no(break_on_time)
        duration = break_on_frame - skip_frames
        self.video.set_progress_bar_limit(duration)
        frame_count = skip_frames
        self.video.seek(skip_frames)
        frame = self.video.read_frame()
        bulk_data = []
        bulk_delete_ids = []

        try:
            while frame is not None:
                if break_on_frame < frame_count:
                    break

                is_store, data_json = self.get_data(frame_count, frame, overwrite=overwrite)
                if is_store:
                    bulk_data.append(data_json)
                    bulk_delete_ids.append(frame_count)

                if len(bulk_data) > database_update_frequency:
                    self.storage.delete_bulk_data(bulk_delete_ids)
                    self.storage.insert_bulk_data(bulk_data)
                    bulk_data = []
                    bulk_delete_ids = []
                if visualize or self.video_writer is not None:
                    out_frame = self.draw_info(frame, data_json)
                    if self.video_writer is not None:
                        self.video_writer.write(out_frame)
                    if visualize:
                        cv2.imshow('frame', out_frame)
                        time.sleep(0.02)
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
