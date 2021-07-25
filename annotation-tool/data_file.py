#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    data_file.py
# @Author:      dulanj
# @Time:        2021-07-25 11.36
import pandas as pd

from common import EventTypes


class RowData:
    FPS = 5

    @staticmethod
    def set_fps(fps):
        RowData.FPS = fps

    def __init__(self, frame_no, team_name, activity=EventTypes.other):
        self.frame_no = int(int(frame_no) * RowData.FPS)
        self.team_name = team_name
        self.activity = activity


class DataFile:
    def __init__(self,filename,  fps):
        self.data = pd.read_excel(filename)
        self.row_pointer = 0
        print(self.data.head(100))
        RowData.set_fps(fps)

    def __get_time_in_secs(self, time_str: str) -> int:
        _time_split = time_str.split('.')
        _time_in_seconds = 0
        if len(_time_split) == 2:
            _min, _sec = _time_split
            _time_in_seconds = int(_min) * 60 + int(_sec)
        elif len(_time_split) == 3:
            _hour, _min, _sec = _time_split
            _time_in_seconds = int(_hour) * 3600 + int(_min) * 60 + int(_sec)
        return _time_in_seconds



    def get_info(self) -> RowData:
        row_data = self.data.loc[self.row_pointer]
        self.row_pointer += 1

        _time_in_seconds = self.__get_time_in_secs(row_data.Time)
        _team = row_data.Team
        _activity = row_data.Activity
        _activity_type = EventTypes.other
        if "Kick" in _activity:
            _activity_type = EventTypes.kick
        elif "Line" in _activity:
            _activity_type = EventTypes.line_out
        elif "Scrum" in _activity:
            _activity_type = EventTypes.scrum
        return RowData(_time_in_seconds, _team, _activity_type)


if __name__ == '__main__':
    data = DataFile()
    for i in range(5):
        dt = data.get_info()
        print(dt.activity)
