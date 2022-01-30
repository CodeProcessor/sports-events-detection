#!/usr/bin/env python3
"""
@Filename:    play_noplay_classification.py
@Author:      dulanj
@Time:        30/01/2022 13:40
"""
from PIL import Image

from draw import put_text
from sports_event_detection.classify import Classify
from sports_event_detection.video_reader import VideoReader
from sports_event_detection.video_writer import SEDVideoWriter


def main():
    model_name = "/home/dulanj/MSc/sports-events-detection/data/trained_models/play_noplay/best-model-parameters3.pt"
    classify_play_noplay = Classify(model_name)

    video = VideoReader("/home/dulanj/MSc/DialogRugby/Match#56_Kandy_SC_v_Police_SC_DRL_2019_20.mp4", verbose=True)
    video_writer = SEDVideoWriter("output_play_noplay.mp4", 25, "output")

    frame = video.read_frame()
    frame_number = 1
    _pred_class = ""
    _pred_conf = ""
    while frame is not None:
        if frame_number % 25 == 1:
            # convert to PIL image
            pil_image = Image.fromarray(frame)
            _pred = classify_play_noplay.predict(pil_image)
            _pred_class = _pred.get_class()
            _pred_conf = _pred.get_prob()

        out_frame = put_text(frame, f"{_pred_class} - {_pred_conf}", (25, 25), color=(0, 0, 255))

        video_writer.write(out_frame)
        if frame_number % 100 == 0:
            print("Frame: {} - {}".format(frame_number, video.get_video_time()))
        frame_number += 1
        # frame_number += 25
        # video.seek(frame_number)
        frame = video.read_frame()


if __name__ == '__main__':
    main()
