#!/usr/bin/env python3
"""
@Filename:    main.py
@Author:      dulanj
@Time:        04/12/2021 13:49
"""
import torch
from PIL import Image
from torchvision.transforms import Compose, transforms

from draw import put_text, rectangle
from params import CLASSES
from train_network.clasification.model import ClassificationModel

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

"""
loop in a video frame by frame
"""
import cv2

transform = Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[1, 1, 1])
])


def load_model(model_file_name):
    model = ClassificationModel(num_classes=2).to(DEVICE)
    checkpoint = torch.load(model_file_name)
    model.load_state_dict(checkpoint['model_state_dict'])
    return model


def main(file_name):
    frame_no = 0
    vc = cv2.VideoCapture(file_name)
    model = load_model(
        '/home/dulanj/MSc/sports-events-detection/data/trained_models/play_noplay/best-model-parameters2.pt')
    while vc.isOpened():
        rval, frame = vc.read()
        if rval:
            # exit with esc key
            if cv2.waitKey(1) & 0xFF == 27:
                break
            frame_no += 1
            if not frame_no % 10 == 9:
                continue

            image = Image.fromarray(frame)
            image = transform(image)
            image = image.unsqueeze(0)
            image = image.to(DEVICE)
            print(image.shape)
            outputs = model(image)
            _, predicted = torch.max(outputs.data, 1)
            frame = rectangle(frame, (5, 5), (320, 120))
            frame = put_text(frame, text=f"Frame No: {frame_no}", pos=(20, 40), font_size=1, color=(255, 0, 0),
                             thickness=3)
            frame = put_text(frame, text=f"Prediction: {CLASSES[predicted]}", pos=(20, 90), font_size=1,
                             color=(255, 0, 0), thickness=3)
            cv2.imshow("frame", frame)
            cv2.waitKey(1)


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print("Usage: python main.py video_file_name")
    #     exit(1)
    main("/home/dulanj/MSc/Research/CH & FC v Kandy SC - DRL 2019_20 Match #23.mp4")
    cv2.destroyAllWindows()
