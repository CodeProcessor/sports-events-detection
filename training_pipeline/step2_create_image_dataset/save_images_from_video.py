#!/usr/bin/env python3
"""
@Filename:    save_images_from_video.py
@Author:      dulanj
@Time:        01/02/2022 23:07
"""
import glob
import os

import cv2

from sports_event_detection.utils.video_reader import VideoReader


def extract_images(video_path, output_dir, every_n_second=1.0):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    video = VideoReader(video_path)
    _fps = video.get_fps()
    every_n_frame = int(_fps * every_n_second)
    video_name = os.path.basename(video_path).split('.')[0]

    for i in range(0, video.get_total_frame_count(), every_n_frame):
        video.seek(i)
        image = video.read_frame(pil_image=True)
        image_name = os.path.join(output_dir, '{}_image_{}.jpg'.format(video_name, i))
        if image is not None:
            image.save(image_name)
        else:
            print('image is None')
            break


def resize_images(inpout_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for image_path in glob.glob(os.path.join(inpout_dir, '*.jpg')):
        print(image_path)
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        new_image = image[:height, :height]
        cv2.imwrite(os.path.join(output_dir, os.path.basename(image_path)), new_image)


if __name__ == '__main__':
    # videos = glob.glob('/home/dulanj/SimplyfAI/BoxAnnotations/*.avi')
    # print(videos)
    # for vid in videos:
    #     print(vid)
    #     extract_images(vid, '/home/dulanj/SimplyfAI/BoxAnnotations/images', every_n_second=0.5)

    resize_images('/home/dulanj/SimplyfAI/BoxAnnotations/images',
                  '/home/dulanj/SimplyfAI/BoxAnnotations/images_resized')
