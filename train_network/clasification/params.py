#!/usr/bin/env python
"""
@Filename:    params.py.py
@Author:      dulanj
@Time:        2021-08-23 14.22
"""
import os

import torch
import yaml

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
configs = None
with open(os.path.join(os.path.dirname(__file__), 'configs.yaml'), 'r') as file:
    configs = yaml.load(file, Loader=yaml.FullLoader)
