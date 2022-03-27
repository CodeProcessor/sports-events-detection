#!/usr/bin/env python3
"""
@Filename:    tracking.py
@Author:      dulanj
@Time:        19/02/2022 14:31
"""
from collections import OrderedDict

import numpy as np
import pandas as pd
from scipy.spatial import distance as dist

from sports_event_detection.extras.sports_utils import iou
from sports_event_detection.recognition.event_objects import Event


class Tracking:
    def __init__(self, event_type, max_disappeared=5, min_update_count=10, min_lifespan=10):
        self.event_type = event_type
        self.min_update_count = min_update_count
        self.min_lifespan = min_lifespan

        self.disappeared_max_frames = max_disappeared
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.frame_count = 0
        self.event_count = 0
        self.events_dataframe = pd.DataFrame(columns=["event_name", "start_frame_id", "end_frame_id"])

    def get_df(self):
        return self.events_dataframe

    def set_frame_count(self, frame_count):
        self.frame_count = frame_count

    def register(self, event):
        self.objects[self.next_object_id] = Event(self.next_object_id, event, self.event_type, self.frame_count)
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def is_valid_event(self, event):
        return event.update_count > self.min_update_count and event.get_lifespan() > self.min_lifespan

    def deregister(self, object_id):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        _obj: Event = self.objects[object_id]
        if self.is_valid_event(_obj):
            self.event_count += 1
            self.events_dataframe = self.events_dataframe.append(
                {
                    "event_name": self.event_type,
                    "start_frame_id": int(_obj.event_start_frame),
                    "end_frame_id": int(_obj.event_end_frame)
                }, ignore_index=True
            )
        del self.objects[object_id]
        del self.disappeared[object_id]

    def get_event_counts(self):
        return self.event_count

    def get_event_object_list(self):
        return [obj for obj in self.objects.values()]

    def update(self, events):
        self.frame_count += 1
        if len(events) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[object_id] > self.disappeared_max_frames:
                    self.deregister(object_id)
            return self.get_event_object_list()
        else:
            # loop over the bounding box rectangles
            input_bounding_boxes = np.zeros((len(events), 4), dtype="float")
            # loop over the bounding box rectangles
            for (i, (x1, y1, x2, y2, _, _)) in enumerate(events):
                # use the bounding box coordinates to derive the centroid
                input_bounding_boxes[i] = (x1, y1, x2, y2)

            if len(self.objects) == 0:
                for i in range(0, len(events)):
                    self.register(events[i])
            else:
                object_i_ds = list(self.objects.keys())
                object_centroids = list([obj.get_bounding_box() for obj in self.objects.values()]) if len(
                    self.objects.values()) > 0 else [[]]
                D = dist.cdist(np.array(object_centroids), input_bounding_boxes, lambda a, b: iou(a, b))
                # list
                rows = D.max(axis=1).argsort()[::-1]
                cols = D.argmax(axis=1)[rows]

                used_rows = set()
                used_cols = set()
                # loop over the combination of the (row, column) index
                # tuples
                for (row, col) in zip(rows, cols):
                    # if we have already examined either the row or
                    # column value before, ignore it
                    # val
                    if D[row, col] == 0:
                        # print("D[row, col] == 0")
                        continue
                    if row in used_rows or col in used_cols:
                        continue
                    # otherwise, grab the object ID for the current row,
                    # set its new centroid, and reset the disappeared
                    # counter
                    object_id = object_i_ds[row]
                    self.objects[object_id].update(events[col], end_frame=self.frame_count)
                    self.disappeared[object_id] = 0
                    # indicate that we have examined each of the row and
                    # column indexes, respectively
                    used_rows.add(row)
                    used_cols.add(col)

                unused_rows = set(range(0, D.shape[0])).difference(used_rows)
                unused_cols = set(range(0, D.shape[1])).difference(used_cols)

                if D.shape[0] >= D.shape[1]:
                    # loop over the unused row indexes
                    for row in unused_rows:
                        # grab the object ID for the corresponding row
                        # index and increment the disappeared counter
                        object_id = object_i_ds[row]
                        self.disappeared[object_id] += 1
                        # check to see if the number of consecutive
                        # frames the object has been marked "disappeared"
                        # for warrants deregistering the object
                        if self.disappeared[object_id] > self.disappeared_max_frames:
                            self.deregister(object_id)
                else:
                    for col in unused_cols:
                        self.register(events[col])

        return self.get_event_object_list()
