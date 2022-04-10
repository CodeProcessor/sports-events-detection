"""
@Filename:    test.py.py
@Author:      dulanj
@Time:        2021-08-23 16.12
"""
import time

import torch

from data_loader import get_test_loader
from params import configs, DEVICE
from pretrained_models import initialize_model


def main():
    model_name = configs["model"]["model_name"]
    num_classes = configs["data"]["no_of_classes"]

    print("Test for the model {} with {} classes".format(model_name, num_classes))

    feature_extract = False
    model, input_size = initialize_model(model_name, num_classes, feature_extract, use_pretrained=False)
    model_file_name = configs["model"]["model_load_path"]
    checkpoint = torch.load(model_file_name)
    model.load_state_dict(checkpoint['model_state_dict'])

    test_loader = get_test_loader()

    # get accuracy
    model.eval()
    correct = 0
    total = 0
    pred_time_list = []
    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)
            start_time = time.time()
            outputs = model(images)
            end_time = time.time()
            pred_time_list.append(end_time - start_time)
            _, predicted = torch.max(outputs.data, 1)
            _, labels = torch.max(labels.data, 1)
            # print("Actual: ", labels.data.cpu().numpy())
            # print("Predicted: ", predicted.cpu().numpy())

            total += labels.size(0)
            correct += sum(predicted == labels)
            # print("Accuracy: ", 100 * correct / total)

    print("Average prediction time: ", round(sum(pred_time_list) * 1000 / len(pred_time_list), 2), "ms")
    print('Accuracy of the network on the {} test images: {}%'.format(total, 100 * correct / total))
    print(pred_time_list)


if __name__ == '__main__':
    main()
