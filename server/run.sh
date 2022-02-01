#!/usr/bin/env bash

export PYTHONPATH=/home/dulanj/MSc/sports-events-detection:$PYTHONPATH

uvicorn main:app --reload
