#!/usr/bin/env python3
"""
@Filename:    main.py
@Author:      dulanj
@Time:        02/02/2022 00:38
"""

import io
from typing import Optional

import cv2
from fastapi import FastAPI
from starlette.responses import StreamingResponse

import sports_event_detection
from backend import SportEventDetectionBackend
from sports_event_detection.extras.sports_utils import get_current_timestamp

tags_metadata = [
    {
        "name": "Show Banner",
        "description": "Show the banner of the sports event detection system",
    },
    {
        "name": "API Status",
        "description": "Check the status of the API.",
    },
    {
        "name": "Video Process",
        "description": "Process a given YouTube Link.",
    }
]
description = """
## Event Recognition Backend API
"""

app = FastAPI(
    title="Sports-Event-Detection-System",
    description=description,
    version=sports_event_detection.__api_version__,
    terms_of_service="https://github.com/CodeProcessor/sports-events-detection/blob/main/LICENSE",
    openapi_tags=tags_metadata
)

event_detection_backend = SportEventDetectionBackend()


@app.get("/", tags=["Show Banner"])
def read_root():
    cv2img = cv2.imread("banner.jpg")
    res, im_png = cv2.imencode(".png", cv2img)
    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")


@app.get("/status", tags=["API Status"])
def show_status():
    ret = {
        "Sports Event Detection Version": sports_event_detection.__version__,
        "API version": sports_event_detection.__api_version__,
        "Commit ID": sports_event_detection.__commit_id__,
        "Build Datetime": sports_event_detection.__build_time__,
        "Server Status": "Up",
        "Datetime": get_current_timestamp()
    }

    return ret


@app.post("/process", tags=["Video Process"])
def call_video_process_engine_function(
        video_link: str,
        start_time: Optional[str] = "00:00:00",
        end_time: Optional[str] = "99:99:99"
):
    if end_time == "99:99:99":
        end_time = None
    _result = event_detection_backend.process_video(video_link, start_time, end_time)

    return _result
