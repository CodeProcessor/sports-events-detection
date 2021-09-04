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


class CatDogDataset(torch.utils.data.Dataset):
    def __init__(self, image_dir, transform=None, test=False):
        self.location = image_dir
        self.file_list = glob.glob(self.location + '/*.*')
        self.transform = transform
        self.is_test = test

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, index):
        file_name = self.file_list[index]
        image = Image.open(file_name)
        base_name = os.path.basename(file_name)
        label_matrix = torch.zeros((2))
        if 'cat' in base_name:
            label_matrix[0] = 1
        else:
            label_matrix[1] = 1

        if self.transform:
            image, label_matrix = self.transform(image, label_matrix)

        if self.is_test:
            return image, file_name
        return image, label_matrix
