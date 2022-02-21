#!/usr/bin/env python3
"""
@Filename:    tracking.py
@Author:      dulanj
@Time:        19/02/2022 14:31
"""
from collections import OrderedDict

import numpy as np
from scipy.spatial import distance as dist

from sports_event_detection.recognition.event_objects import Event


class Tracking:
    def __init__(self, event_type, max_disappeared=5, min_update_count=10):
        self.event_type = event_type
        self.min_update_count = min_update_count

        self.disappeared_max_frames = max_disappeared
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.update_count = 0
        self.event_count = 0

    def register(self, event):
        self.objects[self.next_object_id] = Event(self.next_object_id, event, self.event_type, self.update_count)
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        _obj: Event = self.objects[object_id]
        if _obj.update_count > self.min_update_count:
            self.event_count += 1
        del self.objects[object_id]
        del self.disappeared[object_id]

    def get_event_counts(self):
        return self.event_count

    def get_event_object_list(self):
        return [obj for obj in self.objects.values()]

    def update(self, events):
        self.update_count += 1
        if len(events) == 0:
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.disappeared_max_frames:
                    self.deregister(objectID)
            return self.get_event_object_list()
        else:
            # loop over the bounding box rectangles
            inputCentroids = np.zeros((len(events), 2), dtype="float")
            # loop over the bounding box rectangles
            for (i, (x, y, w, h, _, _)) in enumerate(events):
                # use the bounding box coordinates to derive the centroid
                inputCentroids[i] = (x, y)

            if len(self.objects) == 0:
                for i in range(0, len(events)):
                    self.register(events[i])
            else:
                objectIDs = list(self.objects.keys())
                objectCentroids = list([obj.get_centroid() for obj in self.objects.values()]) if len(
                    self.objects.values()) > 0 else [[]]
                D = dist.cdist(np.array(objectCentroids), inputCentroids)
                # list
                rows = D.min(axis=1).argsort()
                cols = D.argmin(axis=1)[rows]

                usedRows = set()
                usedCols = set()
                # loop over the combination of the (row, column) index
                # tuples
                for (row, col) in zip(rows, cols):
                    # if we have already examined either the row or
                    # column value before, ignore it
                    # val
                    if row in usedRows or col in usedCols:
                        continue
                    # otherwise, grab the object ID for the current row,
                    # set its new centroid, and reset the disappeared
                    # counter
                    objectID = objectIDs[row]
                    self.objects[objectID].update(events[col])
                    self.disappeared[objectID] = 0
                    # indicate that we have examined each of the row and
                    # column indexes, respectively
                    usedRows.add(row)
                    usedCols.add(col)

                unusedRows = set(range(0, D.shape[0])).difference(usedRows)
                unusedCols = set(range(0, D.shape[1])).difference(usedCols)

                if D.shape[0] >= D.shape[1]:
                    # loop over the unused row indexes
                    for row in unusedRows:
                        # grab the object ID for the corresponding row
                        # index and increment the disappeared counter
                        objectID = objectIDs[row]
                        self.disappeared[objectID] += 1
                        # check to see if the number of consecutive
                        # frames the object has been marked "disappeared"
                        # for warrants deregistering the object
                        if self.disappeared[objectID] > self.disappeared_max_frames:
                            self.deregister(objectID)
                else:
                    for col in unusedCols:
                        self.register(events[col])

        return self.get_event_object_list()
