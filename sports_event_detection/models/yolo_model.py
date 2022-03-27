#!/usr/bin/env python3
"""
@Filename:    model.py
@Author:      dulanj
@Time:        23/01/2022 12:12
"""
import numpy as np
import torch
from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import non_max_suppression, check_img_size, scale_coords
from utils.torch_utils import select_device


class YoloModel:
    def __init__(self, model_path, loader='yolo'):
        if loader == 'yolo':
            device = "cuda:0"
            imgsz = [640, 640]
            self.stride = 32
            self.img_size = check_img_size(imgsz, s=self.stride)
            self.auto = True
            self.device = select_device(device)
            self.model = self.load_yolo(model_path)

            self.ori_image_shape = None
            self.resized_image_shape = None

    def load_yolo(self, model_path):
        """

        :param model_path:
        :return:
        """

        dnn = False
        data = "/home/dulanj/MSc/yolov5/sed-scrum-lineout.yaml"

        model = DetectMultiBackend([model_path], device=self.device, dnn=dnn, data=data)
        return model

    def pre_process(self, image):
        """

        :param image:
        :return:
        """
        half = False
        self.ori_image_shape = image.shape[:2]
        # Padded resize
        img = letterbox(image, self.img_size, stride=self.stride, auto=self.auto)[0]
        self.resized_image_shape = img.shape
        # Convert
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)

        im = torch.from_numpy(img).to(self.device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim

        return im

    def _inference(self, image):
        """

        :param image:
        :return:
        """
        augment = False
        visualize = False
        pred = self.model(image, augment=augment, visualize=visualize)
        return pred

    def _post_process(self, pred):
        """

        :param image:
        :param boxes:
        :param scores:
        :param classes:
        :return:
        """
        conf_thres = 0.25  # confidence threshold
        iou_thres = 0.45  # NMS IOU threshold
        agnostic_nms = False
        max_det = 1000
        classes = None
        pred_out = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        det = pred_out[0]
        det[:, :4] = scale_coords(self.resized_image_shape, det[:, :4], self.ori_image_shape)
        det[:, 0] = det[:, 0] / self.ori_image_shape[1]
        det[:, 1] = det[:, 1] / self.ori_image_shape[0]
        det[:, 2] = det[:, 2] / self.ori_image_shape[1]
        det[:, 3] = det[:, 3] / self.ori_image_shape[0]
        return det.cpu().numpy()

    def predict(self, image):
        """

        :param image:
        :return: xyxy, conf, class
        """
        return self._post_process(self._inference(self.pre_process(image)))
