FROM ubuntu:20.04

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Remove user input for package installtion
ENV DEBIAN_FRONTEND=noninteractive

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git vim

RUN apt-get install -y python3-pip

# install Torch
RUN pip3 install torch==1.8.2+cpu torchvision==0.9.2+cpu torchaudio==0.8.2 -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install  --upgrade pip  \
    && python3 -m pip install -r requirements.txt  \
    && python3 -m pip cache purge

