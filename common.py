#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    common.py
# @Author:      dulanj
# @Time:        2021-07-25 11.55
import enum


class EventTypes(enum.Enum):
    line_out = 0
    kick = 1
    scrum = 2
    other = 3
