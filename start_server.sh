#!/usr/bin/env bash

export PYTHONPATH="/home/dulanj/MSc/yolov5":$(pwd):$PYTHONPATH
cd server
uvicorn main:app --port 5000 --reload
