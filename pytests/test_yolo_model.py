#!/usr/bin/env python3
"""
@Filename:    test_yolo_model.py
@Author:      dulanj
@Time:        19/02/2022 11:21
"""
import cv2
import pytest

from sports_event_detection.models.yolo_model import YoloModel


class TestYoloModel:
    @pytest.fixture
    def yolo_model(self):
        model_file_path = "../server/models/events_v2.pt"
        model = YoloModel(model_file_path)
        return model

    def test_predict(self, yolo_model):
        image = cv2.imread("assets/lineout_05_42115_jpg.rf.a6535f43de3675c1698cb5df711a61bd.jpg")
        ret = yolo_model.predict(image)
        print(ret)
        h, w = image.shape[:2]
        for det in ret:
            x1, y1, x2, y2 = det[:4]
            x1, y1, x2, y2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow("image", image)
        cv2.waitKey(0)
