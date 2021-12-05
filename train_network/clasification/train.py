#!/usr/bin/env python
"""
@Filename:    train.py.py
@Author:      dulanj
@Time:        2021-08-23 14.42
"""
import numpy as np
import torch.nn as nn
from torch import optim
from tqdm import tqdm

import wandb
from model import ClassificationModel
from params import *
from train_network.clasification.data_loader import get_train_loader, get_val_loader


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
    correct = 0
    for batch_idx, (x, y) in enumerate(loop):
        # get the inputs; data is a list of [inputs, labels]
        x, y = x.to(DEVICE), y.to(DEVICE)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        output = model(x)
        loss = loss_fn(output, y)
        _loss.append(loss.item())
        loss.backward()
        optimizer.step()

        loop.set_postfix(loss=loss.item())
    #     correct += (output == y).items().sum()
    #
    # accuracy = 100 * correct / len(train_loader.dataset)
    mean_loss = np.mean(_loss)
    print(f"Training Mean loss was {mean_loss}")
    return mean_loss#, accuracy


def val_fn(val_loader, model, loss_fn):
    valid_loss = 0.0
    model.eval()  # Optional when not using Model Specific layer
    for data, labels in val_loader:
        if torch.cuda.is_available():
            data, labels = data.cuda(), labels.cuda()

        target = model(data)
        loss = loss_fn(target, labels)
        valid_loss = loss.item() * data.size(0)
    return valid_loss


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
    val_loader = get_val_loader()

    """
    Go through the training data set and train the model for a number of epochs
    """
    for epoch in range(start_epoch, EPOCHS):
        print(f"\nEpoch: {epoch + 1}/{EPOCHS}")

        _loss = train_fn(
            train_loader=train_loader,
            model=model,
            optimizer=optimizer,
            loss_fn=loss_func
        )

        _val_loss = val_fn(
            val_loader=val_loader,
            model=model,
            loss_fn=loss_func
        )
        """
        Update weights and biases graphs
        """
        wandb.log({"train_loss": _loss})
        wandb.log({"val_loss": _val_loss})

        """
        Save model if the validation loss is less than the current loss
        """
        if _val_loss < current_loss:
            print(f"Saving Model, val loss > {_val_loss}")
            current_loss = _val_loss
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
