#!/usr/bin/env python
"""
@Filename:    train.py.py
@Author:      dulanj
@Time:        2021-08-23 14.42
"""
import numpy as np
from torch import optim
from torch.utils.data import DataLoader
from torchvision.transforms import transforms
import torch
import torch.nn as nn
from tqdm import tqdm

from dataset import CatDogDataset
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


class Compose(object):
    def __init__(self, _transforms):
        self.transforms = _transforms

    def __call__(self, img, boxes):
        for t in self.transforms:
            img, boxes = t(img), boxes

        return img, boxes


transform = Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[1, 1, 1])
])
loss_func = nn.BCELoss()


def train_fn(train_loader, model, optimizer, loss_fn):
    loop = tqdm(train_loader, leave=True)
    _loss = []

    for batch_idx, (x, y) in enumerate(loop):
        x, y = x.to(DEVICE), y.to(DEVICE)
        out = model(x)
        loss = loss_fn(out, y)
        _loss.append(loss.item())
        optimizer.zero_grad()
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

    train_dataset = CatDogDataset(
        transform=transform,
        image_dir=IMG_DIR
    )

    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=BATCH_SIZE,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY,
        shuffle=True,
        drop_last=False
    )

    for epoch in range(start_epoch, EPOCHS):
        print(f"\nEpoch: {epoch + 1}/{EPOCHS}")

        _loss = train_fn(
            train_loader=train_loader,
            model=model,
            optimizer=optimizer,
            loss_fn=loss_func
        )

        if _loss < current_loss:
            print(f"\nsaving best model MAP > {_loss}")
            current_loss = _loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': _loss
            }, MODEL_SAVE_PATH)


if __name__ == '__main__':
    main()
