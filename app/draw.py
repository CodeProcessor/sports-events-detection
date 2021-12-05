#!/usr/bin/env python3
"""
@Filename:    draw.py
@Author:      dulanj
@Time:        04/12/2021 13:57
"""
import cv2


def put_text(img, text, pos, font_size=0.5, color=(255, 255, 255), thickness=1):
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_size, color, thickness)
    return img


def rectangle(img, pos, size, color=(255, 255, 255), thickness=-1):
    cv2.rectangle(img, pos, (pos[0] + size[0], pos[1] + size[1]), color, thickness)
    return img
