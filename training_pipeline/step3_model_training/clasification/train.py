#!/usr/bin/env python
"""
@Filename:    train.py.py
@Author:      dulanj
@Time:        2021-08-23 14.42
"""
import ssl

import numpy as np
import torch.nn as nn
from torch import optim
from torch.optim.lr_scheduler import StepLR
from tqdm import tqdm

import wandb
from data_loader import get_train_loader, get_val_loader
from params import *
from pretrained_models import initialize_model

ssl._create_default_https_context = ssl._create_unverified_context


class Compose(object):
    def __init__(self, _transforms):
        self.transforms = _transforms

    def __call__(self, img, boxes):
        for t in self.transforms:
            img, boxes = t(img), boxes

        return img, boxes


loss_func = nn.CrossEntropyLoss().cuda()


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
        predicted = model(x)
        loss = loss_fn(predicted, y)
        _loss.append(loss.item())
        loss.backward()
        optimizer.step()

        loop.set_postfix(loss=loss.item())

        _, target = torch.max(predicted.data, 1)
        _, labels = torch.max(y.data, 1)

        correct += torch.sum(target == labels)

    accuracy = 100 * correct / len(train_loader.dataset)
    mean_loss = np.mean(_loss)
    print(f"Training Mean loss was {mean_loss}")
    print(f"Training Accuracy {accuracy}")
    return mean_loss, accuracy


def val_fn(val_loader, model, loss_fn):
    valid_loss = 0.0
    correct = 0
    model.eval()  # Optional when not using Model Specific layer
    for data, labels in val_loader:
        if torch.cuda.is_available():
            data, labels = data.cuda(), labels.cuda()

        predicted = model(data)
        loss = loss_fn(predicted, labels)
        valid_loss = loss.item() * data.size(0)

        _, target = torch.max(predicted.data, 1)
        correct += torch.sum(target == labels)
    accuracy = 100 * correct / len(val_loader.dataset)
    print(f"Validation Loss: {valid_loss}")
    print(f"Validation Accuracy: {accuracy}")
    return valid_loss, accuracy


def main():
    # model = ClassificationModel(num_classes=configs["data"]["no_of_classes"]).to(DEVICE)
    # model = torch.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=True).to(DEVICE)
    model_name = "efficientnet"
    num_classes = 2
    feature_extract = False
    model, input_size = initialize_model(model_name, num_classes, feature_extract, use_pretrained=True)
    print(input_size)

    optimizer = optim.Adam(
        model.parameters(), lr=configs["model"]["lr"], weight_decay=configs["model"]["weight_decay"])
    current_loss = 10000
    start_epoch = 0

    if configs["model"]["load_model"]:
        checkpoint = torch.load(configs["model"]["load_model_path"])
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        start_epoch = checkpoint['epoch']
        current_loss = checkpoint['loss']

    train_loader = get_train_loader()
    val_loader = get_val_loader()

    # Loading weights and biases
    wandb.init(project="play_no-play_classification", entity="dulan20", config=flatten_dict(configs))

    """
    Go through the training data set and train the model for a number of epochs
    """
    _lr_scheduler = StepLR(optimizer, step_size=10, gamma=0.2)
    for epoch in range(start_epoch, configs["model"]["epochs"]):
        print(f"\nEpoch: {epoch + 1}/{configs['model']['epochs']}")

        _loss, _train_acc = train_fn(
            train_loader=train_loader,
            model=model,
            optimizer=optimizer,
            loss_fn=loss_func
        )
        _lr_scheduler.step()
        _val_loss, _val_acc = val_fn(
            val_loader=val_loader,
            model=model,
            loss_fn=loss_func
        )
        """
        Update weights and biases graphs
        """
        wandb.log({"train_loss": _loss})
        wandb.log({"train_acc": _train_acc})
        wandb.log({"val_loss": _val_loss})
        wandb.log({"val_acc": _val_acc})
        wandb.log({"lr": float(_lr_scheduler.get_last_lr()[0])})
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
            }, configs["model"]["model_save_path"])


def flatten_dict(dd, separator='_', prefix=''):
    return {prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(dd, dict) else {prefix: dd}


if __name__ == '__main__':
    main()
