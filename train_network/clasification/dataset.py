#!/usr/bin/env python
"""
@Filename:    dataset.py
@Author:      dulanj
@Time:        2021-08-23 14.35
"""
import glob
import os

import torch
from PIL import Image

from params import configs


class ClassificationDataset(torch.utils.data.Dataset):
    def __init__(self, image_dir, transform=None, test=False):
        self.location = image_dir
        self.file_list = []
        self.no_of_classes = len(configs["data"]["class_names"])
        for _class in configs["data"]["class_names"]:
            _full_cls_path = os.path.join(self.location, _class)
            _class_index = configs["data"]["class_names"].index(_class)
            self.file_list += [(_class_index, file_name) for file_name in glob.glob(_full_cls_path + '/*.*')]
        self.transform = transform
        self.is_test = test

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, index):
        _class_index, _file_name = self.file_list[index]
        image = Image.open(_file_name)

        label_matrix = torch.zeros(self.no_of_classes)
        label_matrix[_class_index] = 1

        if self.transform:
            image = self.transform(image)

        # if self.is_test:
        #     return image, _class_index

        return image, label_matrix
