#!/usr/bin/env python3
"""
@Filename:    streamlit_server.py
@Author:      dulanj
@Time:        12/02/2022 16:38
"""

import streamlit as st
from PIL import Image

from backend import SportEventDetectionBackend

sports_event_detection_backend = SportEventDetectionBackend(return_json=False)

st.title('Sports Video Event Analysis System')

image = Image.open('banner.jpg')
# st.image(image, caption='Sports Event Detection')
url = st.text_input('Paste rugby match youtube video URL')


@st.cache
def get_info(url):
    return sports_event_detection_backend.get_yt_video_info(url)


def get_video_time(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    seconds = seconds % 60
    minutes = minutes % 60
    return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))


try:
    info = get_info(url)

    enable = True
except Exception as e:
    info = {
        'title': '',
        'length': 100,
        'views': 0,
    }
    enable = False
    url = "Not a valid url"

if enable:
    st.video(url, start_time=100)

st.write('URL : {}'.format(url))
_length = int(info['length'])
st.write('{:10} : {}'.format("Title", info['title']))
st.write('{} : {}'.format("Length", info['length']))
st.write('{} : {}'.format("Views", info['views']))

values = st.slider('Select video range seconds scale', 0, _length, (0, _length), disabled=not enable)
_start_sec, _end_sec = values
_skip_time = get_video_time(_start_sec)
_break_on_time = get_video_time(_end_sec)
st.write(f'Video selected from **{_skip_time}** to **{_break_on_time}**')

if st.button('Process Video', disabled=not enable):
    st.write(f'Video Processing video from {_skip_time} to {_break_on_time} ...')

    # my_bar = st.progress(0)
    # for percent_complete in range(100):
    #     time.sleep(0.1)
    #     my_bar.progress(percent_complete + 1)

    dataframe = sports_event_detection_backend.process_video(url, skip_time=_skip_time, break_on_time=_break_on_time)
    dataframe.drop(columns=['start_frame_id', 'end_frame_id'], inplace=True)
    st.write('Completed!')
    st.balloons()
    st.write(dataframe)
