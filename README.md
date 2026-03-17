# Sports Events Detection

![](server/banner.jpg)

A computer vision system for automatic detection and temporal localization of sports events in video footage. Originally developed as an MSc research project, the system processes rugby match videos to identify key events — **scrums**, **lineouts**, and **rucks** — along with play/no-play activity and digital banner detection.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Models](#models)
- [Installation](#installation)
- [Usage](#usage)
- [Output Format](#output-format)
- [Training Pipeline](#training-pipeline)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

---

## Overview

The system takes a YouTube URL or local video file as input, processes it at 5 FPS through a multi-model detection pipeline, and outputs a structured table of detected events with their timestamps and durations.

The pipeline combines:
- **Object detection** (YOLOv3/YOLOv5) for spatial event localization
- **Image classification** (ResNet50) for play/no-play activity
- **Moving average** and **centroid-based tracking** algorithms for temporal event grouping

---

## Features

- Detect rugby events (scrum, lineout, ruck) with temporal boundaries
- Classify play vs. no-play activity per frame
- Detect digital banners/scoreboards and suppress events during coverage
- Accept YouTube URLs or local video files as input
- Incrementally store frame predictions in SQLite (memory-efficient for long videos)
- Two recognition strategies: moving average and object tracking
- REST API (FastAPI) and interactive web UI (Streamlit)
- Docker support

---

## Architecture

```
Input: YouTube URL / Local Video
           │
           ▼
   Video Download & FPS Conversion (→ 5 FPS)
           │
    ┌──────┼──────────────┐
    ▼      ▼              ▼
Digital  Events        Play/NoPlay
Banner   Detection     Classification
(YOLOv5) (YOLOv3)      (ResNet50)
    └──────┴──────────────┘
                │
                ▼
      SQLite Database (frame-level predictions)
                │
         ┌──────┴──────┐
         ▼             ▼
   Moving Average   Tracking-based
   Recognition      Recognition
         └──────┬──────┘
                ▼
     Pandas DataFrame (event list with timestamps)
                │
         ┌──────┴──────┐
         ▼             ▼
     FastAPI        Streamlit
     REST API       Web UI
```

---

## Models

| Model | Architecture | Purpose | Classes |
|-------|-------------|---------|---------|
| `events_v3.pt` | YOLOv3 tiny | Sports event detection | Scrum, Line-out, Ruck |
| `digital_v3.pt` | YOLOv5 | Digital banner detection | Digital banner |
| `activity_v3.pt` | ResNet50 | Activity classification | Play, No-play |

**Trained model weights** are hosted separately. Download from Google Drive and place in `server/trained_models/`:

```
server/trained_models/
├── events_v3.pt
├── digital_v3.pt
└── activity_v3.pt
```

> See `server/trained_models/README.md` for the download link.

### Detection Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Confidence threshold | 0.25 | Minimum detection confidence |
| NMS IoU threshold | 0.45 | Non-maximum suppression overlap |
| Moving average threshold | 0.6 | Fraction of window required to confirm event |
| Processing FPS | 5 | Frames per second processed |

---

## Installation

### Prerequisites

- Python 3.8+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/CodeProcessor/sports-events-detection.git
cd sports-events-detection

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install PyTorch (CPU build)
pip install torch==1.8.2+cpu torchvision==0.9.2+cpu torchaudio==0.8.2 \
  -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html

# 4. Download trained models and place them in server/trained_models/
```

### Docker

```bash
docker-compose up
```

This builds and starts the FastAPI server on port 5000.

---

## Usage

### Option 1: FastAPI Server

```bash
cd server
uvicorn main:app --port 5000 --reload
```

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Returns the banner image |
| `GET` | `/status` | Health check |
| `POST` | `/process` | Process a video |

**POST `/process` request body:**

```json
{
  "video_link": "https://www.youtube.com/watch?v=...",
  "start_time": "00:01:00",
  "end_time": "00:05:00"
}
```

### Option 2: Streamlit Web UI

```bash
cd server
streamlit run streamlit_server.py
```

Opens an interactive browser interface where you can paste a YouTube URL, set a time range, and view results.

### Option 3: Shell Scripts

```bash
./start_server.sh   # Start FastAPI server
./run_stream.sh     # Start Streamlit server
```

---

## Output Format

The system returns a list of detected events as a structured table:

| Column | Type | Description |
|--------|------|-------------|
| `event_name` | string | `scrum`, `lineout`, `ruck`, or `digital_noplay` |
| `start_frame_id` | int | Frame index where the event begins |
| `end_frame_id` | int | Frame index where the event ends |
| `start_time` | string | Event start timestamp (`HH:MM:SS`) |
| `end_time` | string | Event end timestamp (`HH:MM:SS`) |
| `duration` | string | Event duration (`HH:MM:SS`) |

**Example:**

```
event_name  start_frame_id  end_frame_id  start_time  end_time  duration
scrum       150             175           00:00:30    00:00:35  00:00:05
lineout     310             340           00:01:02    00:01:08  00:00:06
ruck        520             560           00:01:44    00:01:52  00:00:08
```

---

## Training Pipeline

A complete training pipeline is provided in `training_pipeline/` with four steps:

| Step | Directory | Description |
|------|-----------|-------------|
| 1 | `step1_video_clip_extraction/` | Extract clips from raw videos and annotate events |
| 2 | `step2_create_image_dataset/` | Extract labeled frames for model training |
| 3 | `step3_model_training/` | Train YOLO (object detection) and ResNet (classification) models |
| 4 | `step4_evaluation/` | Evaluate model accuracy on test sets |

---

## Configuration

**`sports_event_detection/extras/params.py`** — runtime parameters:

```python
database_update_frequency = 5000  # Commit to SQLite every N frames
save_video = True                 # Save annotated output video
```

**Tracking parameters** (in `server/backend.py` and recognition modules):

```python
max_disappeared = 5        # Frames before an unmatched object is removed
min_update_count = 10–20   # Minimum frames an object must be tracked to count as valid
min_lifespan = 10–40       # Minimum frame lifespan for a recognized event
```

---

## Project Structure

```
sports-events-detection/
├── server/
│   ├── main.py                  # FastAPI app
│   ├── backend.py               # Main pipeline orchestration
│   ├── streamlit_server.py      # Streamlit UI
│   └── trained_models/          # Pre-trained model weights (.pt files)
│
├── sports_event_detection/
│   ├── detection/
│   │   ├── detections.py        # Base detection class
│   │   ├── event_detection.py   # YOLO-based event detection
│   │   └── play_detection.py    # ResNet50 play/no-play classification
│   │
│   ├── recognition/
│   │   ├── event_recognition.py         # Moving average recognition
│   │   ├── recognition_with_tracking.py # Tracking-based recognition
│   │   ├── tracking.py                  # Centroid + IoU object tracker
│   │   └── event_objects.py             # Event lifecycle management
│   │
│   ├── models/
│   │   ├── yolo_model.py        # YOLO inference wrapper
│   │   ├── classify.py          # ResNet50 inference wrapper
│   │   └── pretrained_models.py # Model architecture initialization
│   │
│   ├── utils/
│   │   ├── video_reader.py      # Frame-by-frame video reading
│   │   ├── video_operations.py  # FPS conversion utilities
│   │   ├── video_writer.py      # Annotated video output
│   │   ├── storage.py           # SQLite frame storage
│   │   └── youtube_downloader.py# YouTube video download
│   │
│   └── extras/
│       ├── params.py            # Global configuration constants
│       ├── common.py            # Enums (EventTypes, ModelNames)
│       └── sports_utils.py      # IoU, time conversion utilities
│
├── training_pipeline/           # End-to-end model training scripts
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Research Context

This system was developed as part of an MSc research project focused on automated sports video analysis. The goal was to build a scalable, modular pipeline capable of detecting structured events in broadcast rugby footage, using a combination of object detection, image classification, and temporal reasoning algorithms.
