#!/usr/bin/env python3
"""
@Filename:    streamlit_server.py
@Author:      dulanj
@Time:        12/02/2022 16:38
"""
import streamlit as st

from backend import SportEventDetectionBackend

sports_event_detection_backend = SportEventDetectionBackend()

st.title('Sports Video Event Analysis System')

url = st.text_input('Video URL')


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
except Exception as e:
    info = {
        'title': '',
        'length': 100,
        'views': 0,
    }
    url = "Not a valid url"
st.write('URL : {}'.format(url))
_length = int(info['length'])
st.write('{:10} : {}'.format("Title", info['title']))
st.write('{} : {}'.format("Length", info['length']))
st.write('{} : {}'.format("Views", info['views']))

values = st.slider('Select video range seconds scale', 0, _length, (0, _length))
_start_sec, _end_sec = values
st.write(f'Process video from {get_video_time(_start_sec)} to {get_video_time(_end_sec)}')

if st.button('Process Video'):
    st.write('Video Processing...')
