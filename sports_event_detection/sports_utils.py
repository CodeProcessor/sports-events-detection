#!/usr/bin/env python3
"""
@Filename:    utils.py
@Author:      dulanj
@Time:        02/02/2022 01:10
"""
from datetime import datetime


def get_current_timestamp():
    """
    Get current datetime as formatted string
    @return:
    """
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")
