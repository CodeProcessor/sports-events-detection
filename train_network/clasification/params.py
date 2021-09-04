#!/usr/bin/env python
"""
@Filename:    params.py.py
@Author:      dulanj
@Time:        2021-08-23 14.22
"""
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

CHANNELS=3

MODEL_SAVE_PATH='../../data/trained_models/best-model-parameters.pt'

LR = 2e-5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 256
WEIGHT_DECAY = 0
EPOCHS = 50
NUM_WORKERS = 2
PIN_MEMORY = True
LOAD_MODEL = False
LOAD_MODEL_FILE = '../../data/trained_models/best-model-parameters.pt'
IMG_DIR = '../../data/dataset/train'
IMG_TEST_DIR = '../../data/dataset/test'
CLASSES = ['kick', 'out', 'scrum']
NO_OF_CLASSES = len(CLASSES)