"""
@Filename:    test.py.py
@Author:      dulanj
@Time:        2021-08-23 16.12
"""
import torch
from torch.utils.data import DataLoader

from dataset import CatDogDataset
from model import ClassificationModel
from params import BATCH_SIZE, NUM_WORKERS, PIN_MEMORY, IMG_TEST_DIR, LOAD_MODEL_FILE, NO_OF_CLASSES, DEVICE
from train import transform


def test():
    model = ClassificationModel(num_classes=NO_OF_CLASSES).to(DEVICE)
    checkpoint = torch.load(LOAD_MODEL_FILE)
    model.load_state_dict(checkpoint['model_state_dict'])

    test_dataset = CatDogDataset(
        transform=transform,
        image_dir=IMG_TEST_DIR,
        test=True
    )

    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=1,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY,
        shuffle=True,
        drop_last=False
    )
    import matplotlib.pyplot as plt
    for x, y in test_loader:

        x = x.to(DEVICE)
        outputs = model(x)

        _, predicted = torch.max(outputs.data, 1)
        print(predicted)
        print(y)
        tensor_image = torch.squeeze(x).to('cpu')
        print(tensor_image.shape)
        plt.imshow(tensor_image.permute(1, 2, 0))
        plt.show()

        import sys
        sys.exit()


if __name__ == '__main__':
    test()