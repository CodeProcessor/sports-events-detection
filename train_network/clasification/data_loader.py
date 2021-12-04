#!/usr/bin/env python3
"""
@Filename:    data_loader.py
@Author:      dulanj
@Time:        04/12/2021 12:50
"""
from torch.utils.data import DataLoader
from torchvision.transforms import transforms, Compose

from train_network.clasification.dataset import ClassificationDataset
from train_network.clasification.params import IMG_DIR, BATCH_SIZE, NUM_WORKERS, PIN_MEMORY, IMG_TEST_DIR

transform = Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[1, 1, 1])
])


def get_train_loader():
    train_dataset = ClassificationDataset(
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

    return train_loader


def get_test_loader():
    test_dataset = ClassificationDataset(
        transform=transform,
        image_dir=IMG_TEST_DIR,
        test=True
    )

    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=3,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY,
        shuffle=True,
        drop_last=False
    )
    return test_loader


if __name__ == '__main__':
    train_loader = get_train_loader()
    for i, (images, labels) in enumerate(train_loader):
        print(images.shape)
        print(labels.shape)
        break
