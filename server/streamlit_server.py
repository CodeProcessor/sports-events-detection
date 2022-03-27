#!/usr/bin/env python3
"""
@Filename:    streamlit_server.py
@Author:      dulanj
@Time:        12/02/2022 16:38
"""
import streamlit as st

from backend import SportEventDetectionBackend

if 'process_button' not in st.session_state:
    st.session_state['process_button'] = False
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = None
if 'time_frame' not in st.session_state:
    st.session_state['time_frame'] = (0, 60)
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = 0

sports_event_detection_backend = SportEventDetectionBackend(return_json=False)

st.title('Sports Video Event Analysis System')

# image = Image.open('banner.jpg')
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
        'length': st.session_state['time_frame'][1],
        'views': 0,
    }
    enable = False
    url = "Not a valid url"

st.write('URL : {}'.format(url))
_length = int(info['length'])
st.write('{:10} : {}'.format("Title", info['title']))
st.write('{} : {} | {} : {} | {} : {} seconds'.format(
    "Length", get_video_time(info['length']),
    "Views", info['views'],
    "Duration", info['length'])
)

values = st.slider('Select video range seconds scale', 0, _length, (0, _length), disabled=not enable)
_start_sec, _end_sec = values
st.session_state['start_time'] = _start_sec
_skip_time = get_video_time(_start_sec)
_break_on_time = get_video_time(_end_sec)
st.write(f'Video selected from **{_skip_time}** to **{_break_on_time}**')

if enable:
    st.video(url, start_time=st.session_state['start_time'])


@st.cache
def process_video(url, skip_time, break_on_time):
    dataframe = sports_event_detection_backend.process_video(url, skip_time=skip_time, break_on_time=break_on_time)
    if len(dataframe.index) > 0:
        dataframe.drop(columns=['start_frame_id', 'end_frame_id'], inplace=True)
        dataframe.sort_values(by=['start_time'], inplace=True)
        dataframe.reset_index(drop=True, inplace=True)
    return dataframe


if st.button('Process Video', disabled=not enable):
    st.session_state['process_button'] = True
    dataframe = process_video(url, skip_time=_skip_time, break_on_time=_break_on_time)
    st.session_state['dataframe'] = dataframe
    st.session_state['time_frame'] = (_skip_time, _break_on_time)
    st.write('Completed!')
    st.balloons()

if st.session_state['process_button']:
    dataframe = st.session_state['dataframe']
    if dataframe is not None:
        if len(dataframe.index) > 0:
            _options = list(dataframe['event_name'].unique())
            options = st.multiselect('Show Events', _options, _options)
            st.write(f'Results are showing from **{st.session_state["time_frame"][0]}** to '
                     f'**{st.session_state["time_frame"][1]}**')
            st.write(dataframe[dataframe['event_name'].isin(options)])
        else:
            st.write('No events found')
    else:
        st.write('Video is not processed')

_ = [st.write('') for _ in range(10)]
st.write('https://github.com/CodeProcessor/sports-events-detection')
st.write('Copyright © 2022 Dulan Jayasuriya. All rights reserved.')
