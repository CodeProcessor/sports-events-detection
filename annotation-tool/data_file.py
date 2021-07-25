#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    data_file.py
# @Author:      dulanj
# @Time:        2021-07-25 11.36
import pandas as pd

from common import EventTypes


class RowData:

    def __init__(self, frame_no, team_name, activity=EventTypes.other):
        self.frame_no = frame_no
        self.team_name = team_name
        self.activity = activity


class DataFile:
    def __init__(self):
        filename = "/home/dulanj/MSc/Research/datafile/Data results.xlsx"
        self.data = pd.read_excel(filename)
        self.row_pointer = 0
        print(self.data.head(100))

    def get_info(self):
        row_data = self.data.loc[self.row_pointer]
        self.row_pointer += 1
        # print(row_data)
        min, sec = row_data.Time.split('.')
        _time_in_seconds = min * 60 + sec
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
