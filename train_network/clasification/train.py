#!/usr/bin/env python
"""
@Filename:    train.py.py
@Author:      dulanj
@Time:        2021-08-23 14.42
"""
import numpy as np
from torch import optim

import torch
import torch.nn as nn
from tqdm import tqdm
import wandb


from dataset import ClassificationDataset
from model import ClassificationModel
from params import (
    DEVICE,
    IMG_DIR,
    WEIGHT_DECAY,
    LR,
    NO_OF_CLASSES,
    BATCH_SIZE,
    NUM_WORKERS,
    PIN_MEMORY,
    EPOCHS,
    MODEL_SAVE_PATH, LOAD_MODEL, LOAD_MODEL_FILE
)
from train_network.clasification.data_loader import get_train_loader


class Compose(object):
    def __init__(self, _transforms):
        self.transforms = _transforms

    def __call__(self, img, boxes):
        for t in self.transforms:
            img, boxes = t(img), boxes

        return img, boxes



loss_func = nn.CrossEntropyLoss()


def train_fn(train_loader, model, optimizer, loss_fn):
    loop = tqdm(train_loader, leave=True)
    _loss = []

    for batch_idx, (x, y) in enumerate(loop):
        # get the inputs; data is a list of [inputs, labels]
        x, y = x.to(DEVICE), y.to(DEVICE)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        out = model(x)
        loss = loss_fn(out, y)
        _loss.append(loss.item())
        loss.backward()
        optimizer.step()

        loop.set_postfix(loss=loss.item())

    mean_loss = np.mean(_loss)
    print(f"\nMean loss was {mean_loss}")
    return mean_loss


def main():
    model = ClassificationModel(num_classes=NO_OF_CLASSES).to(DEVICE)
    optimizer = optim.Adam(
        model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY
    )
    current_loss = 10000
    start_epoch = 0

    if LOAD_MODEL:
        checkpoint = torch.load(LOAD_MODEL_FILE)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        start_epoch = checkpoint['epoch']
        current_loss = checkpoint['loss']

    train_loader = get_train_loader()

    for epoch in range(start_epoch, EPOCHS):
        print(f"\nEpoch: {epoch + 1}/{EPOCHS}")

        _loss = train_fn(
            train_loader=train_loader,
            model=model,
            optimizer=optimizer,
            loss_fn=loss_func
        )
        wandb.log({"loss": _loss})
        wandb.watch(model)
        if _loss < current_loss:
            print(f"\nSaving Model, loss > {_loss}")
            current_loss = _loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': _loss
            }, MODEL_SAVE_PATH)


if __name__ == '__main__':
    wandb.init(project="play_no-play_classification", entity="dulan20")
    wandb.config = {
        "learning_rate": LR,
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE
    }
    main()
