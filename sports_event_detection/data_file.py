#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    data_file.py
# @Author:      dulanj
# @Time:        2021-07-25 11.36
import enum

import pandas as pd

from sports_event_detection.common import EventTypes


class RowData:
    FPS = 5

    @staticmethod
    def set_fps(fps):
        RowData.FPS = fps

    def __init__(self, frame_no, duration, team_name, activity=EventTypes.other):
        self.frame_no = int(int(frame_no) * RowData.FPS)
        self.duration = int(int(duration + 1) * RowData.FPS)
        self.team_name = team_name
        self.activity = activity


class RowNames(enum.Enum):
    start_time = 3
    end_time = 4
    activity = 2
    team = 1


class DataFile:
    def __init__(self, filename, sheetname, fps):
        self.data = pd.read_excel(filename, sheet_name=sheetname)
        self.row_pointer = 0
        print(self.data.head(100))
        RowData.set_fps(fps)

    def get_shape(self):
        return self.data.shape

    def __get_time_in_secs(self, time_str: str) -> int:
        _time_split = time_str.split('.')
        _time_in_seconds = 0

        def second_correction(_second):
            if len(_second) == 1:
                _second = _second + '0'
            return _second

        if len(_time_split) == 2:
            _min, _sec = _time_split
            _time_in_seconds = int(_min) * 60 + int(second_correction(_sec))
        elif len(_time_split) == 3:
            _hour, _min, _sec = _time_split
            _time_in_seconds = int(_hour) * 3600 + int(_min) * 60 + int(second_correction(_sec))
        return _time_in_seconds

    def get_info(self, pointer=None) -> RowData:
        row_data = self.data.loc[self.row_pointer]
        if pointer is None:
            self.row_pointer += 1
        else:
            self.row_pointer = pointer
        _start_time_string = str(row_data[RowNames.start_time.value])
        _end_time_string = str(row_data[RowNames.end_time.value])
        print(f"Getting info: start-{_start_time_string} end-{_end_time_string}")
        _start_time_in_seconds = self.__get_time_in_secs(_start_time_string)
        _stop_time_in_seconds = self.__get_time_in_secs(_end_time_string)
        _duration = _stop_time_in_seconds - _start_time_in_seconds
        _duration = _duration if _duration > 0 else 1
        _team = row_data[RowNames.team.value]
        _activity = row_data[RowNames.activity.value]
        _activity_type = EventTypes.other
        if "Kick" in _activity:
            _activity_type = EventTypes.kick
        elif "Line" in _activity:
            _activity_type = EventTypes.lineout
        elif "Scrum" in _activity:
            _activity_type = EventTypes.scrum
        elif "noplay" in _activity:
            _activity_type = EventTypes.noplay
        elif "play" in _activity:
            _activity_type = EventTypes.play
        else:
            raise NotImplementedError(f"Unknown activity: {_activity}")
        return RowData(_start_time_in_seconds, _duration, _team, _activity_type)


if __name__ == '__main__':
    data = DataFile()
    for i in range(5):
        dt = data.get_info()
        print(dt.activity)
