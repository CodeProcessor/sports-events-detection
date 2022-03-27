#!/usr/bin/env python3
"""
@Filename:    classify.py
@Author:      dulanj
@Time:        30/01/2022 13:19
"""
import torch
from PIL import Image
from torch.nn.functional import softmax
from torchvision import transforms
from torchvision.transforms import Compose

from sports_event_detection.models.pretrained_models import initialize_model


class Pred:
    def __init__(self, class_id, prob):
        self.class_id = class_id
        self.prob = prob
        self.classes = ['play', 'noplay']

    def __str__(self):
        return f'{self.class_id} {self.prob}'

    def get_class(self):
        return self.classes[self.class_id]

    def get_prob(self):
        return f"{round(self.prob * 100, 2):.2f}"


class Classify:
    def __init__(self, model_path, device='cuda'):
        model_name = "resnet"
        num_classes = 2
        feature_extract = False
        model, input_size = initialize_model(model_name, num_classes, feature_extract, use_pretrained=False,
                                             device=device)
        checkpoint = torch.load(model_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        self.model = model
        self.device = device
        self.transform = Compose([
            transforms.Resize((224, 224)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _preprocess(self, image: Image):
        return torch.unsqueeze(self.transform(image), 0).to(self.device)

    def _inference(self, image):
        return self.model(image)

    def _postprocess(self, prediction):
        _cls_id = prediction.argmax(dim=1).item()
        _conf = softmax(prediction, dim=1)[0][_cls_id].cpu().detach().numpy()
        return Pred(_cls_id, _conf)

    def predict(self, image):
        if isinstance(image, str):
            image = Image.open(image)
        elif issubclass(type(image), Image.Image):
            pass
        else:
            raise TypeError("image should be a string or PIL.Image")

        image = self._preprocess(image)
        prediction = self._inference(image)
        pred_obj = self._postprocess(prediction)
        return pred_obj


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default=os.path.join(os.getcwd(), "model.pth"))
    parser.add_argument("--image", type=str, default=os.path.join(os.getcwd(), "images", "test.jpg"))
    args = parser.parse_args()

    classify = Classify(args.model_path, device='cpu')
    image = Image.open(args.image)
    pred_class = classify.predict(image)
    print(f"Predicted class: {pred_class}")
