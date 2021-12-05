#!/usr/bin/env python
"""
@Filename:    params.py.py
@Author:      dulanj
@Time:        2021-08-23 14.22
"""

import torch
import yaml

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
configs = None
with open('configs.yaml', 'r') as file:
    configs = yaml.load(file, Loader=yaml.FullLoader)
