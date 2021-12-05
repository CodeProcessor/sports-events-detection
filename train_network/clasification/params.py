#!/usr/bin/env python
"""
@Filename:    params.py.py
@Author:      dulanj
@Time:        2021-08-23 14.22
"""
import os

import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

CHANNELS = 3

MODEL_SAVE_PATH = '../../data/trained_models/play_noplay/best-model-parameters2.pt'

LR = 2e-5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 16
WEIGHT_DECAY = 0
EPOCHS = 50
NUM_WORKERS = 2
PIN_MEMORY = True
LOAD_MODEL = False
LOAD_MODEL_FILE = '../../data/trained_models/play_noplay/best-model-parameters-val.pt'

IMG_DIR_BASE = '../../data/dataset2/'
IMG_DIR_TRAIN = os.path.join(IMG_DIR_BASE, 'train')
IMG_TEST_DIR = os.path.join(IMG_DIR_BASE, 'test')
IMG_VAL_DIR = os.path.join(IMG_DIR_BASE, 'val')

# CLASSES = ['kick', 'out', 'scrum']
CLASSES = ['play', 'noplay']

NO_OF_CLASSES = len(CLASSES)
