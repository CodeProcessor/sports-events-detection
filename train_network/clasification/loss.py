#!/usr/bin/env python
"""
@Filename:    loss.py.py
@Author:      dulanj
@Time:        2021-08-23 14.23
"""
import torch
import torch.nn as nn


class ModelLoss(nn.Module):
    def __init__(self):
        super(ModelLoss, self).__init__()

    def forward(self, predictions, target):
        loss = "123"
        return loss