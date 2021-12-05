"""
@Filename:    test.py.py
@Author:      dulanj
@Time:        2021-08-23 16.12
"""
import torch

from model import ClassificationModel
from params import configs, DEVICE
from train_network.clasification.data_loader import get_test_loader


def test():
    model = ClassificationModel(num_classes=configs["data"]["no_of_classes"]).to(DEVICE)
    checkpoint = torch.load(configs["data"]["no_of_classes"])
    model.load_state_dict(checkpoint['model']['model_load_path'])

    test_loader = get_test_loader()

    # get accuracy
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            _, labels = torch.max(labels.data, 1)
            print("Actual: ", labels.data.cpu().numpy())
            print("Predicted: ", predicted.cpu().numpy())

            total += labels.size(0)
            correct += sum(predicted == labels)
            print("Accuracy: ", 100 * correct / total)

    print('Accuracy of the network on the 10000 test images: %d %%' % (100 * correct / total))

    # for x, y in test_loader:
    #
    #     x = x.to(DEVICE)
    #     outputs = model(x)
    #
    #     _, predicted = torch.max(outputs.data, 1)
    #     print(predicted)
    #     print(y)
    #     print("Image {} predicted as {}".format(y, predicted[0]))
    #     # tensor_image = torch.squeeze(x).to('cpu')
    #     # print(tensor_image.shape)
    #     # plt.imshow(tensor_image.permute(1, 2, 0))
    #     # plt.show()
    #     #
    #     # import sys
    #     # sys.exit()


if __name__ == '__main__':
    test()