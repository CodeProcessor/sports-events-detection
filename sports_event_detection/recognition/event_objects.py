#!/usr/bin/env python3
"""
@Filename:    event_objects.py
@Author:      dulanj
@Time:        19/02/2022 14:35
"""


class Event:
    def __init__(self, event_id, event, event_type, start_frame):
        self.event_id = event_id
        self.event_name = f"Event-{event_id}"
        self.event_type = event_type
        self.event_start_frame = start_frame
        self.event_end_frame = None

        self.x1 = event[0]
        self.y1 = event[1]
        self.x2 = event[2]
        self.y2 = event[3]
        self.confidence = event[4]

        self.update_count = 0

    def get_lifespan(self, current_frame=None):
        if current_frame is None:
            return self.event_end_frame - self.event_start_frame
        else:
            return current_frame - self.event_start_frame

    def update(self, event, end_frame=None):
        self.x1 = event[0]
        self.y1 = event[1]
        self.x2 = event[2]
        self.y2 = event[3]
        self.confidence = event[4]
        self.event_end_frame = end_frame
        self.update_count += 1

    def get_bounding_box(self, height, width):
        return [int(element) for element in
                [
                    self.x1 * width,
                    self.y1 * height,
                    self.x2 * width,
                    self.y2 * height
                ]
                ]

    def get_centroid(self):
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2
