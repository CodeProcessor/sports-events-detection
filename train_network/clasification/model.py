#!/usr/bin/env python
"""
@Filename:    model.py
@Author:      dulanj
@Time:        2021-08-23 13.53
"""
import torch
import torch.nn as nn
from torchsummary import summary

from params import DEVICE

architecture_config = [
    # kernal size, no of filters, Stride, padding
    (3, 16, 1, 1),
    (3, 16, 1, 1),
    "Maxpool",
    (3, 32, 1, 1),
    (3, 32, 1, 1),
    "Maxpool",
    (3, 48, 1, 1),
    (3, 48, 1, 1),
    (3, 48, 1, 1),
    "Maxpool",
    (3, 64, 1, 1),
    (3, 64, 1, 1),
    (3, 64, 1, 1)
]


class CNNBlock(nn.Module):
    def __init__(self, input_channels, output_channels, **kwargs):
        super(CNNBlock, self).__init__()
        self.conv_2d = nn.Conv2d(in_channels=input_channels, out_channels=output_channels, bias=False, **kwargs)
        self.batch_normalize = nn.BatchNorm2d(output_channels)
        self.leaky_relu = nn.LeakyReLU(0.1)

    def forward(self, x):
        return self.leaky_relu(self.batch_normalize(self.conv_2d(x)))


class ClassificationModel(nn.Module):
    def __init__(self, input_channels=3, **kwargs):
        super(ClassificationModel, self).__init__()
        self.nn_architecture = architecture_config
        self.input_channels = input_channels
        self.custom_architecture = self._create_convolution_layers()
        self.fully_connected_layers = self._create_fully_connected_layers(**kwargs)

    def forward(self, x):
        x = self.custom_architecture(x)
        return self.fully_connected_layers(torch.flatten(x, start_dim=1))

    def _create_convolution_layers(self):
        layers = []
        input_channels = self.input_channels
        for ele in self.nn_architecture:
            if isinstance(ele, tuple):
                layers += [
                    CNNBlock(
                        input_channels=input_channels,
                        output_channels=ele[1],
                        kernel_size=ele[0],
                        stride=ele[2],
                        padding=ele[3]
                    )
                ]
                input_channels = ele[1]
            elif isinstance(ele, str):
                layers += [
                    nn.MaxPool2d(
                        kernel_size=2,
                        stride=2
                    )
                ]
        return nn.Sequential(*layers)

    def _create_fully_connected_layers(self, num_classes):
        return nn.Sequential(
            nn.Flatten(),
            nn.Linear(8*8*64, 256),
            nn.Dropout(0.2),
            nn.LeakyReLU(0.1),
            nn.Linear(256,  num_classes),
            nn.Softmax()
        )


def test():
    model = ClassificationModel(num_classes=2).to(DEVICE)
    summary(model, input_size=(3, 64, 64), device=DEVICE)
    x = torch.randn(2, 3, 64, 64, device=DEVICE)
    print(model(x).shape)


if __name__ == '__main__':
    test()
