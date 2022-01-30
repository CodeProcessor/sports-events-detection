#!/usr/bin/env python3
"""
@Filename:    data_loader.py
@Author:      dulanj
@Time:        04/12/2021 12:50
"""

from torch.utils.data import DataLoader
from torchvision.transforms import transforms, Compose

from dataset import ClassificationDataset
from params import *

transform = Compose([
    transforms.Resize((int(configs["model"]["input_width"]), int(configs["model"]["input_height"]))),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=configs["model"]["mean"], std=configs["model"]["std"])
])


def get_train_loader():
    train_dataset = ClassificationDataset(
        transform=transform,
        image_dir=os.path.join(configs["data"]["image_dir"], configs["data"]["image_train_dir"]),
    )

    return get_loader(train_dataset, batch_size=configs["model"]["batch_size"])


def get_val_loader():
    test_dataset = ClassificationDataset(
        transform=transform,
        image_dir=os.path.join(configs["data"]["image_dir"], configs["data"]["image_val_dir"]),
        test=True
    )
    return get_loader(test_dataset, batch_size=1)


def get_test_loader():
    test_dataset = ClassificationDataset(
        transform=transform,
        image_dir=os.path.join(configs["data"]["image_dir"], configs["data"]["image_test_dir"]),
        test=True
    )
    return get_loader(test_dataset, batch_size=1)


def get_loader(dataset, batch_size):
    return DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        num_workers=configs["model"]["no_of_workers"],
        pin_memory=configs["model"]["pin_memory"],
        shuffle=True,
        drop_last=False
    )


if __name__ == '__main__':
    train_loader = get_train_loader()
    for i, (images, labels) in enumerate(train_loader):
        print(images.shape)
        print(labels.shape)
        break
