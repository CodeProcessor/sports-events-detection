#!/usr/bin/env python
"""
@Filename:    params.py.py
@Author:      dulanj
@Time:        2021-08-23 14.22
"""
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

CHANNELS=3
NO_OF_CLASSES = 2
MODEL_SAVE_PATH='trained_models/best-model-parameters.pt'

LR = 2e-5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 256
WEIGHT_DECAY = 0
EPOCHS = 250
NUM_WORKERS = 2
PIN_MEMORY = True
LOAD_MODEL = True
LOAD_MODEL_FILE = 'trained_models/best-model-parameters.pt'
IMG_DIR = '/home/dulanj/Datasets/dogs-vs-cats/train'
IMG_TEST_DIR = '/home/dulanj/Datasets/dogs-vs-cats/test1'
