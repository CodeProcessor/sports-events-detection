#!/usr/bin/env python3
"""
@Filename:    video.py
@Author:      dulanj
@Time:        12/01/2022 00:17
"""

import cv2


# from yolo_model import YoloModelq

def main():
    # model = load_model()
    video_path = '/home/dulanj/MSc/DialogRugby/match-16.mp4'
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    ret, frame = cap.read()
    while ret:
        ret, frame = cap.read()
        print(frame.shape)
        print(type(frame))
        # print(model.predict(frame))
        cv2.imshow('frame', frame)
        cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_count += 1
        if frame_count % 100 == 0:
            print(frame_count)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
